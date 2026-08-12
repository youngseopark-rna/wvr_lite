from config.environments import DB_PATH, R3S_DRIVER
import pyodbc
from pathlib import Path
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import create_engine

import logging

logger = logging.getLogger(__name__)
_engines = {}

"""
Connection for WVR -> Lite convertor
"""
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

"""
DB Connection for using ORM with SQLAlchemy
"""
def get_db_engine_by_alchemy(wvr_path: str, model: str):
    logger.info(f"Start to connect {wvr_path}, model: {model}")

    # create db engine
    try: 
        engine = create_engine(
            "mssql+pyodbc://", 
            creator=lambda: _wvr_connection_string(wvr_path, model)
        )
        logger.info(f"Successfully created db engine {engine}")

        return engine
    except Exception as e:
        logger.exception(f"Failed to connect to the db engine: {e}")
        raise RuntimeError from e


def _wvr_connection_string(wvr_path: str, model: str) -> pyodbc.Connection:
    if not wvr_path or not model:
        raise ValueError("Both wvr_path and model must be provided.")

    clean_path = str(Path(wvr_path).resolve())
    dbq = f"DBQ={clean_path};"
    model_param = f"MODEL={model};"
    raw_odbc_str = R3S_DRIVER + dbq + model_param
    logger.info(f"Raw ODBC URL: {raw_odbc_str}")

    try:
        conn = pyodbc.connect(raw_odbc_str)
        conn.add_output_converter(pyodbc.SQL_DECIMAL, lambda val: float(val) if val is not None else None)
        conn.add_output_converter(pyodbc.SQL_NUMERIC, lambda val: float(val) if val is not None else None)
        logger.info(f"Successfully connected to the odbc driver: {conn}")

        return conn
    except Exception as e:
        logger.exception(f"Failed to access to odbc driver: {e}")
        raise RuntimeError from e
