from contextlib import asynccontextmanager
from service.alm_service import AlmService
from util.batch_scheduler import set_batch_job_scheduler
from util.log_handler import set_root_logger
from fastapi import FastAPI
import logging

logger = logging.getLogger(__name__)
alm_service_instance: AlmService | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("[Logger] Set up the root logger and volumes")
    set_root_logger()
    logger.info("[Server] Starting up FastAPI Application...")

    batch_job_scheduler = set_batch_job_scheduler()
    batch_job_scheduler.start()

    global alm_service_instance
    # 서버 시작 시 1회만 인스턴스 생성
    alm_service_instance = await AlmService.create()
    logger.info("[Context Manager] Server initialized finished!")
    yield
    batch_job_scheduler.shutdown()
    logger.info("[Batch] Background Batch Job Scheduler deprecated")
    logger.info("[Server] Shutting down the server...")


def get_alm_service() -> AlmService:
    if alm_service_instance is None:
        raise RuntimeError("Service is not initialized")
    return alm_service_instance
