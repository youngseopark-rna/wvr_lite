from importlib import import_module
from pkgutil import walk_packages
from typing import Any, Dict, List, Optional, Sequence, Union
from sqlalchemy import Column, Table, select
from sqlalchemy.sql import ColumnElement, ClauseElement
from sqlalchemy.ext.asyncio import AsyncSession
import logging

import models


class GenericReadOnlyTableRepository:
    logger = logging.getLogger(__name__)

    def __init__(self, session: AsyncSession):
        # 생성자에서는 오직 세션만 받습니다.
        self.session = session
        self._table_map: Dict[str, Table] = self._scan_models_and_collect_tables()

    def _scan_models_and_collect_tables(self) -> Dict[str, Table]:
        """
        models 패키지 내의 모든 모듈을 순회하면서
        sqlacodegen으로 생성된 Table 객체들을 모아서 {테이블이름: Table객체}로 반환합니다.
        """
        tables: Dict[str, Table] = {}

        # 1. models 폴더 하위의 모든 sub-module을 순회
        for _, module_name, _ in walk_packages(
            path=models.__path__, prefix=f"{models.__name__}."
        ):
            # 모듈 동적 import
            mod = import_module(module_name)

            # 2. 모듈 내부에 선언된 모든 객체 검사
            for attr_name in dir(mod):
                attr = getattr(mod, attr_name)

                # 3. 객체가 SQLAlchemy Table 인스턴스인 경우 맵에 등록
                if isinstance(attr, Table):
                    # attr.name은 Table('A_BSCR', ...)에서 첫 번째 인자로 전달된 DB 테이블명입니다.
                    tables[attr.name] = attr

        return tables

    def _resolve_columns(
        self,
        target_table: Table,
        columns: Optional[Sequence[Union[str, Column, ClauseElement]]] = None,
    ) -> List[Any]:
        """
        넘겨받은 target_table을 기준으로 문자열 컬럼/표현식을 해소합니다.
        """
        if not columns:
            return list(target_table.columns)

        resolved = []
        for col in columns:
            if isinstance(col, str):
                resolved.append(target_table.c[col])
            elif isinstance(col, ClauseElement):
                resolved.append(col)
            else:
                raise ValueError(f"유효하지 않은 컬럼/표현식 타입입니다: {type(col)}")
        return resolved

    def get_table(self, table_name: str) -> Table:
        """테이블 이름으로 저장된 Table 객체 반환"""
        table = self._table_map.get(table_name)
        if table is None:
            available_tables = list(self._table_map.keys())
            raise ValueError(
                f"'{table_name}' 테이블을 models에서 찾을 수 없습니다.\n"
                f"가능한 테이블 목록({len(available_tables)}개): {available_tables[:5]}..."
            )
        return table

    async def find(
        self,
        table_name: str,  # find 함수에서만 테이블 이름을 받습니다.
        columns: Optional[Sequence[Union[str, Column, ClauseElement]]] = None,
        where_clause: Optional[Sequence[ColumnElement]] = None,
        group_by: Optional[Sequence[Union[str, Column, ClauseElement]]] = None,
        having: Optional[Sequence[ColumnElement]] = None,
        order_by: Optional[Sequence[Union[str, Column, ClauseElement]]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        find 함수 호출 시 전달받은 table_name 기반 동적 조회
        """
        # 1. 전달받은 테이블 이름 문자열로 임시 MetaData 내에 Table 객체 생성
        target_table = self.get_table(table_name)
        self.logger.info(f"Target Table: {target_table}")

        # 2. SELECT 컬럼 및 FROM 절 설정 (stmt 미완성 부분 수정)
        selected_cols = self._resolve_columns(target_table, columns)
        stmt = select(*selected_cols).select_from(target_table)

        # 3. WHERE 절 (개별 행 필터링)
        if where_clause:
            for condition in where_clause:
                stmt = stmt.where(condition)

        # 4. GROUP BY 절
        if group_by:
            group_cols = self._resolve_columns(target_table, group_by)
            stmt = stmt.group_by(*group_cols)

        # 5. HAVING 절 (그룹 집계 필터링)
        if having:
            for condition in having:
                stmt = stmt.having(condition)

        # 6. ORDER BY 절
        if order_by:
            order_cols = self._resolve_columns(target_table, order_by)
            stmt = stmt.order_by(*order_cols)

        # 7. LIMIT / OFFSET
        stmt = stmt.limit(limit).offset(offset)

        self.logger.info(f"Query: {stmt}")
        # 8. 쿼리 실행 및 결과 반환
        result = await self.session.execute(stmt)
        return [dict(row) for row in result.mappings().all()]
