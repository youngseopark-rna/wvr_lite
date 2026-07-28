from environments import ALM_WVR_PATH
import queries
from tests import __handle_exception, logger
from wvr_convertor import get_pivot, get_all_tables_in_wvr
from repositories.table_repository import GenericReadOnlyTableRepository
from service.alm_service import AlmService
from database import get_db_session_by_name

import pytest

IS_SUCCESS = True
ALM_DB = "ALM_DashBoard_20260424"


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


@pytest.mark.skip(reason="Success")
@pytest.mark.asyncio
async def test_table_repository():
    async_session_gen = get_db_session_by_name(ALM_DB)
    session = await anext(async_session_gen)

    try:
        repo = GenericReadOnlyTableRepository(session)
        result = await repo.find(
            table_name="A_Company",
            columns=["Step Date"],
        )
        logger.info(f"Result: {result}")
    finally:
        await async_session_gen.aclose()


@pytest.mark.asyncio
async def test_alm_service():
    async def test_alm_service_create():
        service = await AlmService.create()

        for repo in service.repo_list:
            logger.info(f"{repo}")

    async def test_alm_service_get_datas_from_table():
        service = await AlmService.create()

        result = await service.get_datas_from_all_db(
            table_name="A_Company", columns=["Assets_Total", "Step Date"]
        )

        for db, query in result.items():
            logger.info(f"{db} Result: {query}")

    await test_alm_service_get_datas_from_table()
