from contextlib import asynccontextmanager
from service.alm_service import AlmService
from fastapi import FastAPI
import logging

logger = logging.getLogger(__name__)

alm_service_instance: AlmService | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global alm_service_instance
    # 서버 시작 시 1회만 인스턴스 생성
    alm_service_instance = await AlmService.create()
    logger.info("ALM Service initialized")
    yield
    logging.info("Server Deprecated...")


def get_alm_service() -> AlmService:
    if alm_service_instance is None:
        raise RuntimeError("Service is not initialized")
    return alm_service_instance
