from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api import auth, products, cart
from app.core.database import create_db_and_tables, test_connection

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
        # Проверим подключение к базе данных
        connection_ok = await test_connection()
        if connection_ok:
            logger.info("Database connection successful")
            await create_db_and_tables()
            logger.info("Application started successfully")
        else:
            logger.warning("Database connection failed, starting without database")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        logger.info("Application will start without database connectivity")

@app.get("/")
async def root():
    return {"message": "Welcome to Shopping Service API"}

@app.get("/health")
async def health_check():
    connection_ok = await test_connection()
    return {
        "status": "healthy" if connection_ok else "database_unavailable",
        "database": "connected" if connection_ok else "disconnected"
    }

@app.get("/test-db")
async def test_db():
    """Тестовый эндпоинт для проверки подключения к БД"""
    try:
        connection_ok = await test_connection()
        return {
            "database_connection": connection_ok,
            "message": "Connected to database" if connection_ok else "Failed to connect to database"
        }
    except Exception as e:
        return {"database_connection": False, "error": str(e)}