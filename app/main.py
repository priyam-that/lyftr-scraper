from fastapi import FastAPI
from app.api.health import router as health_router
from app.api.scrape import router as scrape_router
from app.frontend.routes import router as frontend_router

app = FastAPI()

app.include_router(health_router)
app.include_router(scrape_router)
app.include_router(frontend_router)
