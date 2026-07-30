import util.queries as queries
from config.environments import WVR_DIR_PATH, R3S_DRIVER

import time
from pathlib import Path
import pandas as pd
import logging
import pathlib
from collections.abc import Generator
from contextlib import contextmanager
import pyodbc

pyodbc.pooling = True
logger = logging.getLogger(__name__)

def list_tables(wvr_file: str, model_name: str) -> pd.DataFrame:
    with wvr_connection_manager(wvr_file, model_name) as conn:
        table_frame = pd.read_sql(queries.select_table_name, conn)
        if table_frame.empty:
            logger.error("There is no table")

        return table_frame


def list_models(wvr_file: str) -> list[str]:
    with wvr_connection_manager(wvr_file, "Results info") as conn:
        cursor = conn.cursor()
        cursor.execute(queries.select_model_name)
        return [row[0] for row in cursor.fetchall()]


@contextmanager
def wvr_connection_manager(wvr_path: str, model: str) -> Generator[pyodbc.Connection]:
    """Context manager for WVR database connections. Ensures proper cleanup."""
    logger.info("Successfully connected to WVR file.")
    conn = pyodbc.connect(__wvr_connection_string(wvr_path, model))
    conn.add_output_converter(
        pyodbc.SQL_DECIMAL, lambda val: float(val) if val is not None else None
    )
    conn.add_output_converter(
        pyodbc.SQL_NUMERIC, lambda val: float(val) if val is not None else None
    )

    try:
        yield conn
    finally:
        conn.close()

def find_out_wvr_paths() -> list[str]:
    wvr_dir_path = Path(WVR_DIR_PATH)
    pattern = "*.wvr"

    wvr_paths = list()
    time_threshold = time.time() - (24 * 3600) # before one day
    for p in wvr_dir_path.glob(pattern):
        if p.is_file() and p.stat().st_mtime >= time_threshold:
            logger.info(f"Found recently modified wvr file: {p.name}")
            wvr_paths.append(str(p))

    return wvr_paths

def __wvr_connection_string(wvr_path: str, model: str) -> str:
    if not wvr_path or not model:
        raise ValueError("Both wvr_path and model must be provided.")

    clean_path = str(pathlib.Path(wvr_path).resolve())
    dbq = f"DBQ={clean_path};"
    model_param = f"MODEL={model}"
    return R3S_DRIVER + dbq + model_param
