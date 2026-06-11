import uuid
import uvicorn
import logging
from fastapi import FastAPI, status, Request
from datetime import datetime
from apps.database.database import engine
# from apps.wallets.models import Base # опционально для создания таблиц
from apps.wallets.api_router import api_router
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from time import time
from contextlib import asynccontextmanager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%d.%m.%Y %H:%M:%S',
)

logger = logging.getLogger(__name__)

EXCLUDED_LOGGED_URL = ['health', 'liveness', 'readiness']

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if str(request.url).split('/')[-1] in EXCLUDED_LOGGED_URL:
            return await call_next(request)
        start_time = time()
        response = await call_next(request)
        process_time = time() - start_time
        logger.info(
            f"{request.client.host}:{request.client.port} - "
            f"\"{request.method} {str(request.url)} HTTP/1.1\" "
            f"{response.status_code} - "
            f"{process_time:.3f}s"
        )
        return response

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("✅ Startup completed, ready to accept requests")
    yield
    logger.info("🛑 Shutdown initiated")

# Создаю таблицы при старте (для простоты, предусмотрены Alembic миграции)
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    lifespan=lifespan,
    title='Wallet API',
    docs_url=None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.add_middleware(
    LoggingMiddleware,
)

app.include_router(api_router)

@app.get("/health", status_code=status.HTTP_200_OK, tags=['Monitoring'])
async def health():
    return {
        'status': 'healthy',
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health/liveness", status_code=status.HTTP_200_OK, tags=["Monitoring"])
async def liveness():
    return {
        "status": "alive",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health/readiness", status_code=status.HTTP_200_OK, tags=["Monitoring"])
async def readiness():
    return {
        "status": "ready",
        "timestamp": datetime.now().isoformat(),
    }


if __name__ == "__main__":
    try:
        uvicorn.run(app, host='0.0.0.0', port=8000)
    finally:
        print("Exit app")