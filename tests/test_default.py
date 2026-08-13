from config.environments import ALM_WVR_PATH, ALM_MODEL_SCEN
from tables.mv_distribution_tables import A_Company
from tables import BE_LIABILITY, ALM_SCENARIO, A_COMPANY, STEP_DATE, VALUE_MARKET
import util.queries as queries
from tests import __handle_exception, logger
from util.wvr_convertor import get_pivot, get_all_tables_in_wvr
from util.wvr_connector import find_out_wvr_paths
from repositories.table_repository import GenericReadOnlyTableRepository
from repositories.auto_repository import AutoDetectedReadOnlyRepository
from service.alm_service import AlmService
import pandas as pd
import pyodbc
from config.database import (
    get_db_session_by_name,
    get_db_engine_by_alchemy,
    _init_wvr_connection,
)

import pytest

IS_SUCCESS = True
ALM_DB = "ALM_DashBoard_20260424"


@pytest.mark.skip(reason="Success")
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


@pytest.mark.skip(reason="Success")
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


@pytest.mark.skip(reason="Success")
@__handle_exception(is_success=IS_SUCCESS)
def test_finding_wvr_paths():
    wvr_paths = find_out_wvr_paths()
    logger.info(f"wvr paths: \n{wvr_paths}")


@pytest.mark.skip(reason="Success")
@__handle_exception(is_success=IS_SUCCESS)
def test_autodection_of_tables():
    engine = get_db_engine_by_alchemy(ALM_WVR_PATH, ALM_MODEL_SCEN)
    repo = AutoDetectedReadOnlyRepository.create(engine=engine)
    session = repo.session

    table = None
    try:
        table = (
            session.query(A_Company)
            .filter(
                A_Company.step_date >= "2024-12-31", A_Company.step_date <= "2025-10-31"
            )
            .all()
        )

        for row in table:
            logger.info(
                f"Step Date: {row.step_date}, BE Liability: {row.be_liability}, Value Market: {row.value_market}, ALM Scenario: {row.alm_scenario}"
            )
    except Exception as e:
        logger.exception("Error occurred while quering A_Company table")
        raise RuntimeError from e
    finally:
        session.close()

    assert table is not None


@__handle_exception(is_success=IS_SUCCESS)
def test_pyodbc_connection():
    try:
        conn = _init_wvr_connection(ALM_WVR_PATH, ALM_MODEL_SCEN)
        conn.add_output_converter(
            pyodbc.SQL_DECIMAL, lambda val: float(val) if val is not None else None
        )
        conn.add_output_converter(
            pyodbc.SQL_NUMERIC, lambda val: float(val) if val is not None else None
        )

        data_frame = pd.read_sql(
            f"SELECT [{VALUE_MARKET}], [{BE_LIABILITY}], [{STEP_DATE}], [{ALM_SCENARIO}] FROM [{A_COMPANY}] WHERE [{STEP_DATE}] BETWEEN '2024-12-31' AND '2025-10-31'",
            conn,
        )

        logger.info(f"Data frame: \n{data_frame}")
    except Exception as e:
        logger.exception("Error occurred while quering A_Company table")
        raise RuntimeError from e

    assert data_frame is not None
