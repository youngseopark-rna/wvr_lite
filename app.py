from wvr_lite import (DIVIDED_UNIT_1)
from wvr_lite.wvr_connector import (wvr_connection_manager, list_models, list_tables)

import sqlite3

import pandas as pd
import logging

logger = logging.getLogger(__name__)


def get_pivot(wvr_path: str, model_name: str, query: str) -> pd.DataFrame:
    with wvr_connection_manager(wvr_path, model_name) as conn:
        data_frame = pd.read_sql(query, conn)
        pivot = data_frame.copy()
    
    logger.info(f"{model_name} Pivot: \n {pivot}")
    return pivot

def get_all_tables_in_wvr(wvr_path: str) -> dict:
    model_list = list_models(wvr_path)
    table_dict = dict()

    for model in model_list:
        table_list = list_tables(wvr_path, model)
        table_list = [table for sublist in table_list.values for table in sublist]
        table_dict[model] = table_list
        logger.info(f"{model}, \n{table_list}")
    
    return table_dict


# 이거를 완성시켜야함
def save_wvr_table_to_db_file(pivot: pd.DataFrame):
    raise NotImplementedError()