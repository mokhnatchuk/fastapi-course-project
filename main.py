from fastapi import FastAPI, HTTPException, status
from routers import categories, promotions, stores, files, auth, scraper
from settings.db import ping

app = FastAPI()


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    from fastapi.openapi.utils import get_openapi

    openapi_schema = get_openapi(
        title="FastAPI",
        version="0.1.0",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        },
    }
    openapi_schema["security"] = [{"OAuth2PasswordBearer": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
app.include_router(auth.router)
app.include_router(stores.router)
app.include_router(categories.router)
app.include_router(promotions.router)
app.include_router(files.router)
app.include_router(scraper.router)


@app.get("/")
def read_root():
    return {"message": "Server is running"}


@app.get("/healthcheck", status_code=status.HTTP_200_OK)
async def db_healthcheck():
    is_alive = await ping()
    if not is_alive:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed",
        )
    return {"status": "healthy", "database": "connected"}
