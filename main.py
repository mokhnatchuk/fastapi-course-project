from fastapi import FastAPI, HTTPException, status
from routers import categories, promotions, stores
from settings.db import ping

app = FastAPI()

app.include_router(stores.router)
app.include_router(categories.router)
app.include_router(promotions.router)


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
