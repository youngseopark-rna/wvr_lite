from config.environments import DB_PATH

from pathlib import Path
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
import logging

logger = logging.getLogger(__name__)
_engines = {}


def get_engine(db_name: str):
    if db_name not in _engines:
        db_file_path = Path(DB_PATH) / f"{db_name}.db"
        db_url = f"sqlite+aiosqlite:///{db_file_path.as_posix()}"
        logger.info(f"DB URL: {db_url}")

        _engines[db_name] = create_async_engine(
            url=db_url, connect_args={"check_same_thread": False}, echo=True
        )
    return _engines[db_name]


async def get_db_session_by_name(db_name: str) -> AsyncGenerator[AsyncSession, None]:
    engine = get_engine(db_name)
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
