import util.queries as queries
from config.environments import MAX_THREAD_WORKERS
from util.wvr_connector import wvr_connection_manager, list_models, list_tables

from concurrent.futures import ProcessPoolExecutor, as_completed
import sqlite3
from pathlib import Path
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def get_pivot(wvr_path: str, model_name: str, query: str) -> pd.DataFrame:
    try:
        with wvr_connection_manager(wvr_path, model_name) as conn:
            data_frame = pd.read_sql(query, conn)
            pivot = data_frame.copy()
    except Exception as e:
        logger.error(f"Error occured: {e}")
        raise RuntimeError(f"Error occur from {get_pivot.__name__}") from e

    logger.info(f"{model_name} Pivot job is successed!")
    return pivot


def get_all_tables_in_wvr(wvr_path: str) -> dict:
    model_list = list_models(wvr_path)
    table_dict = dict()

    with ProcessPoolExecutor(max_workers=MAX_THREAD_WORKERS) as executor:
        futures = {
            executor.submit(list_tables, wvr_path, model): model for model in model_list
        }

        for future in as_completed(futures):
            model = futures[future]
            try:
                table_list = future.result()
                table_list = [
                    table for sublist in table_list.values for table in sublist
                ]
                table_dict[model] = table_list
                logger.info(f"Model: {model}, Table List: \n{table_list}")
            except Exception as e:
                logger.error(f"Failed to get tables for {model}: {e}")

    return table_dict


def export_all_wvr_to_db(wvr_path: str, output_dir: str = "db") -> bool:
    """Transfer all model and table data in the WVR file to the SQLite3.db file."""
    table_dict = get_all_tables_in_wvr(wvr_path)
    logger.info("Got all the table list from models")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    db_path = output_path / f"{Path(wvr_path).stem}.db"
    logger.info(f"DB Path: {db_path}")
    for model_name, tables in table_dict.items():
        with ProcessPoolExecutor(max_workers=MAX_THREAD_WORKERS) as executor:
            pivot_futures = {
                table: executor.submit(
                    get_pivot, wvr_path, model_name, queries.select_all_datas(table)
                )
                for table in tables
            }

            for table, future in pivot_futures.items():
                pivot = future.result()

                if pivot is None:
                    logger.error(f"Failed to get pivot from {model_name}")
                    return False

                with sqlite3.connect(db_path) as conn:
                    result = pivot.to_sql(
                        name=table, con=conn, if_exists="replace", index=False
                    )
                logger.info(f"Successfully written to {table}, {result}")

    return True
