from fastapi import FastAPI

from src.api.routes.companies import router as companies_router
from src.api.routes.ranking import router as ranking_router
from src.api.routes.screener import router as screener_router


app = FastAPI(
    title="Nifty 100 Financial Intelligence API",
    description="API for company data, financial screening, and quality rankings.",
    version="1.0.0",
)


app.include_router(companies_router)
app.include_router(ranking_router)
app.include_router(screener_router)


@app.get("/")
def root():
    return {
        "message": "Nifty 100 Financial Intelligence API is running",
        "version": "1.0.0",
    }