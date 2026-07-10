from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.chat import router as chat_router
from api.conversations import router as conversations_router
from api.products import router as products_router
from auth.router import router as auth_router
from config.settings import settings
from config.logging import setup_logging, logger
from middleware import (
    RequestIDMiddleware,
    SecurityHeadersMiddleware,
    add_error_handlers,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Application starting", app_name=settings.app_name)
    yield
    logger.info("Application shutting down")


app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

add_error_handlers(app)

app.include_router(auth_router)
app.include_router(conversations_router)
app.include_router(chat_router)
app.include_router(products_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
