from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
import logging

from dependencies import get_alm_service
from service.alm_service import AlmService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/alm", tags=["ALM Dashboard"])


class TableDataResponse(BaseModel):
    db_name: str
    table_name: str
    columns: list[str]
    data: Any


@router.get(path="", response_model=list[TableDataResponse])
async def get_alm_wvr_data(
    table_name: str = Query(..., description="Table name for ALM_*.wvr"),
    columns: list[str] = Query(..., description="Column lists for the table"),
    service: AlmService = Depends(get_alm_service),
):
    try:
        result = await service.get_datas_from_all_db(
            table_name=table_name,
            columns=columns,
        )

        response = list()
        for db_name, query in result.items():
            response.append(
                TableDataResponse(
                    db_name=db_name, table_name=table_name, columns=columns, data=query
                )
            )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
