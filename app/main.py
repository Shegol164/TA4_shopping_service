from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api import auth, products, cart
from app.core.database import create_db_and_tables

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Shopping Service API",
    description="API для сервиса покупки товаров",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(products.router, prefix="/products", tags=["products"])
app.include_router(cart.router, prefix="/cart", tags=["cart"])

@app.on_event("startup")
async def startup_event():
    logger.info("Starting application...")
    try:
        await create_db_and_tables()
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Error starting application: {e}")
        # Не останавливаем приложение, пусть пользователь сам решает

@app.get("/")
async def root():
    return {"message": "Welcome to Shopping Service API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}