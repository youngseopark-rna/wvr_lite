from scripts.convertor import convert_wvr_to_orm

import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
logger = logging.getLogger(__name__)

async def daily_batch_job():
    logger.info("[Batch] Start Daily Batch Job")

    await asyncio.to_thread(convert_wvr_to_orm)
    logger.info("[Batch] Batch Job finished!")

def set_batch_job_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()

    scheduler.add_job(
        daily_batch_job,
        trigger=CronTrigger(hour=3, minute=0), # 매일 새벽 3시에 실행
        id="daily_batch",
        replace_existing=True,
        next_run_time=datetime.now(),
    )

    return scheduler