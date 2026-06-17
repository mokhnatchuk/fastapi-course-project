import os
from datetime import datetime, timezone
from fpdf import FPDF
from collections.abc import Sequence

FONTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fonts")
MAX_TITLE_CHARS = 40


def truncate_at_word(text: str, max_chars: int = MAX_TITLE_CHARS) -> str:
    if len(text) <= max_chars:
        return text
    truncated = text[:max_chars].rsplit(" ", 1)[0]
    return truncated + "…"


def generate_promotions_report(
    promotions: Sequence,
    filename: str = "promotions_report.pdf",
) -> str:
    pdf = FPDF()
    pdf.add_font("DejaVu", "", os.path.join(FONTS_DIR, "DejaVuSans.ttf"))
    pdf.add_font("DejaVu", "B", os.path.join(FONTS_DIR, "DejaVuSans-Bold.ttf"))
    pdf.add_page()

    pdf.set_font("DejaVu", "B", 14)
    pdf.cell(0, 10, "Звіт по акціях", ln=True, align="C")  # pyright: ignore[reportArgumentType]

    pdf.ln(5)
    pdf.set_font("DejaVu", "", 10)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    pdf.cell(0, 10, f"Згенеровано: {generated_at}", ln=True)  # pyright: ignore[reportArgumentType]
    pdf.cell(0, 10, f"Всього акцій: {len(promotions)}", ln=True)  # pyright: ignore[reportArgumentType]

    pdf.ln(5)

    pdf.set_font("DejaVu", "B", 8)
    pdf.cell(12, 10, "ID", border=1)
    pdf.cell(80, 10, "Назва", border=1)
    pdf.cell(25, 10, "Стара ціна", border=1)
    pdf.cell(25, 10, "Нова ціна", border=1)
    pdf.cell(18, 10, "Знижка", border=1)
    pdf.cell(30, 10, "Активна", border=1, ln=True)  # pyright: ignore[reportArgumentType]

    pdf.set_font("DejaVu", "", 7)
    now = datetime.now(timezone.utc)
    for promotion in promotions:
        is_active = "Так" if promotion.starts_at <= now <= promotion.ends_at else "Ні"

        pdf.cell(12, 8, str(promotion.id), border=1)
        pdf.cell(80, 8, truncate_at_word(promotion.title), border=1)
        pdf.cell(25, 8, f"{promotion.original_price:.2f}", border=1)
        pdf.cell(25, 8, f"{promotion.discounted_price:.2f}", border=1)
        pdf.cell(18, 8, f"{promotion.discount_percent}%", border=1)
        pdf.cell(30, 8, is_active, border=1, ln=True)  # pyright: ignore[reportArgumentType]

    filepath = f"./uploads/{filename}"
    os.makedirs("./uploads", exist_ok=True)
    pdf.output(filepath)

    return filepath
