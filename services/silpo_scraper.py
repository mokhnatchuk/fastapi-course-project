import asyncio
import logging
from decimal import Decimal
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.category import Category
from models.promotion import Promotion
from models.store import Store

logger = logging.getLogger(__name__)

SILPO_API_BASE_URL = "https://sf-ecom-api.silpo.ua"
DEFAULT_BRANCH_ID = "00000000-0000-0000-0000-000000000000"
IMAGE_BASE_URL = "https://content.silpo.ua/ecom/product"
PRODUCTS_PER_PAGE = 500
DELAY_SECONDS = 1
REQUEST_TIMEOUT_SECONDS = 30
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
HASH_SLUG_LENGTH = 32
CONCURRENCY_LIMIT = 3


class SilpoScraper:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.client = httpx.AsyncClient(
            timeout=REQUEST_TIMEOUT_SECONDS,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "application/json",
            },
        )
        self.semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)

    async def close(self):
        await self.client.aclose()

    async def fetch_with_retry(self, url: str, max_retries: int = 3):
        last_error: httpx.HTTPError | None = None
        for attempt in range(max_retries):
            try:
                response = await self.client.get(url)
                if response.status_code == 429:
                    base_delay = (2**attempt) * 1000
                    jitter = int(asyncio.get_event_loop().time() % 500)
                    total_delay = base_delay + jitter
                    logger.warning(
                        "Rate limit hit, waiting %dms (attempt %d)",
                        total_delay,
                        attempt + 1,
                    )
                    await asyncio.sleep(total_delay / 1000)
                    continue
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as error:
                last_error = error
                if "429" not in str(error):
                    raise
                base_delay = (2**attempt) * 1000
                jitter = int(asyncio.get_event_loop().time() % 500)
                total_delay = base_delay + jitter
                logger.warning(
                    "Rate limit, waiting %dms (attempt %d)",
                    total_delay,
                    attempt + 1,
                )
                await asyncio.sleep(total_delay / 1000)
        if last_error is not None:
            raise last_error
        raise httpx.HTTPError(f"Failed after {max_retries} retries: {url}")

    async def fetch_categories(self):
        url = (
            f"{SILPO_API_BASE_URL}/v1/branches/{DEFAULT_BRANCH_ID}"
            f"/categories/tree?deliveryType=DeliveryHome"
        )
        data = await self.fetch_with_retry(url)
        categories = []
        if not data or not data.get("items"):
            return categories
        for item in data["items"]:
            slug = item.get("slug", "")
            if len(slug) == HASH_SLUG_LENGTH:
                continue
            name = item.get("name") or item.get("title") or slug
            categories.append({"slug": slug, "title": name})
        return categories

    async def fetch_products_page(self, category_slug: str, offset: int):
        url = (
            f"{SILPO_API_BASE_URL}/v1/uk/branches/{DEFAULT_BRANCH_ID}/products"
            f"?limit={PRODUCTS_PER_PAGE}&offset={offset}"
            f"&deliveryType=DeliveryHome&category={category_slug}"
            f"&includeChildCategories=true&inStock=true"
        )
        return await self.fetch_with_retry(url)

    async def fetch_all_products_for_category(
        self, category_slug: str, category_title: str
    ):
        all_products = []
        current_offset = 0

        try:
            first_page = await self.fetch_products_page(category_slug, 0)
        except Exception as error:
            logger.warning("Category %s failed: %s", category_title, error)
            return []

        if not first_page:
            return []

        total_products = first_page.get("total", 0)
        items = first_page.get("items", [])
        all_products.extend(items)
        current_offset = PRODUCTS_PER_PAGE

        while current_offset < total_products:
            await asyncio.sleep(DELAY_SECONDS)
            try:
                page_data = await self.fetch_products_page(
                    category_slug, current_offset
                )
                if not page_data or not page_data.get("items"):
                    break
                all_products.extend(page_data["items"])
                current_offset += PRODUCTS_PER_PAGE
            except Exception as error:
                logger.warning(
                    "Offset %d for %s failed: %s",
                    current_offset,
                    category_title,
                    error,
                )
                break

        return all_products

    async def process_category(self, category: dict, all_products: list):
        async with self.semaphore:
            logger.info("Processing category: %s", category["title"])
            products = await self.fetch_all_products_for_category(
                category["slug"], category["title"]
            )
            for product in products:
                product["_categoryTitle"] = category["title"]
            all_products.extend(products)
            logger.info("%d products in %s", len(products), category["title"])
            await asyncio.sleep(DELAY_SECONDS)

    def parse_price(self, raw_value):
        if raw_value is None:
            return None
        try:
            return float(raw_value)
        except ValueError, TypeError:
            return None

    def calculate_discount(self, old_price, new_price):
        if not old_price or not new_price or old_price <= new_price:
            return None
        return round(((old_price - new_price) / old_price) * 100)

    def make_full_image_url(self, icon_filename):
        if not icon_filename:
            return None
        if icon_filename.startswith("http"):
            return icon_filename
        return f"{IMAGE_BASE_URL}/{icon_filename}"

    async def scrape(self):
        logger.info("Starting Silpo scraper")

        try:
            categories = await self.fetch_categories()
        except Exception as error:
            logger.error("Failed to fetch categories: %s", error)
            return {"error": f"Failed to fetch categories: {error}"}

        logger.info("Found %d top-level categories", len(categories))

        all_products = []
        tasks = [
            self.process_category(category, all_products) for category in categories
        ]
        await asyncio.gather(*tasks)

        logger.info("Collected %d products total", len(all_products))

        seen_titles = set()
        unique_products = []
        for product in all_products:
            title = product.get("title")
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_products.append(product)

        logger.info("Unique products: %d", len(unique_products))

        return await self.save_products(unique_products)

    async def save_products(self, products):
        result = await self.db.execute(select(Store).where(Store.slug == "silpo"))
        store = result.scalars().first()
        if not store:
            store = Store(name="Сільпо", slug="silpo")
            self.db.add(store)
            await self.db.flush()
            logger.info("Created Silpo store")

        stats = {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0}

        for product in products:
            try:
                new_price = self.parse_price(
                    product.get("displayPrice") or product.get("price")
                )
                old_price = self.parse_price(
                    product.get("displayOldPrice") or product.get("oldPrice")
                )

                if new_price is None:
                    stats["skipped"] += 1
                    continue

                discount_percent = self.calculate_discount(old_price, new_price)
                image_url = self.make_full_image_url(product.get("icon"))
                category_title = product.get("_categoryTitle", "Без категорії")

                result = await self.db.execute(
                    select(Category).where(Category.slug == product.get("slug", ""))
                )
                category = result.scalars().first()
                if not category:
                    category_slug = product.get(
                        "slug", category_title.lower().replace(" ", "-")
                    )
                    category = Category(name=category_title, slug=category_slug)
                    self.db.add(category)
                    await self.db.flush()

                from datetime import datetime, timezone

                now = datetime.now(timezone.utc)
                from datetime import timedelta

                promotion = Promotion(
                    store_id=store.id,
                    category_id=category.id,
                    title=product.get("title", ""),
                    original_price=Decimal(str(old_price))
                    if old_price
                    else Decimal(str(new_price)),
                    discounted_price=Decimal(str(new_price)),
                    discount_percent=discount_percent or 0,
                    image_path=image_url,
                    starts_at=now,
                    ends_at=now + timedelta(days=30),
                )
                self.db.add(promotion)
                stats["inserted"] += 1

            except Exception as error:
                logger.warning("Failed to save product: %s", error)
                stats["errors"] += 1
                continue

        await self.db.commit()
        logger.info("Saved products: %s", stats)
        return stats
