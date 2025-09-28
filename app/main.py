from fastapi import FastAPI
from pathlib import Path
import logging.config

from app.routers import (
    auth_routes,
    ninja_routes,
)


BASE_DIR = Path(__file__).resolve().parent.parent
logging_conf_path = BASE_DIR / "logging.conf"


logging.config.fileConfig(logging_conf_path, disable_existing_loggers=False)

app = FastAPI()
app.include_router(auth_routes.router, prefix="/auth", tags=["auth"])
app.include_router(ninja_routes.router, prefix="/ninja", tags=["ninja"])
