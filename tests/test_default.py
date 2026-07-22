from environments import ALM_WVR_PATH, queries
from tests import __handle_exception, logger
from app import get_pivot, get_all_tables_in_wvr

import pytest

IS_SUCCESS = True


@pytest.mark.skip(reason="Test Finished")
@__handle_exception(is_success=IS_SUCCESS)
def test_get_all_tables():
    global IS_SUCCESS
    logger.info("Start get all tables test!")
    table_dict = get_all_tables_in_wvr(ALM_WVR_PATH)
    logger.info(f"Table Dict: \n{table_dict}")

    for model, table in table_dict.items():
        logger.info(f"Model: {model}, Table: {table}")
        for t in table:
            try:
                query = queries.select_all_datas(t)
                logger.info(f"Query: {query}")
                pivot = get_pivot(ALM_WVR_PATH, model, query)
            except Exception as e:
                IS_SUCCESS = False
                logger.error(
                    f"Error Occured during {test_get_all_tables.__name__}: {e}"
                )
                raise RuntimeError("Error Occured") from e
            logger.info(f"{table} Pivot : \n{pivot}")

    assert IS_SUCCESS
