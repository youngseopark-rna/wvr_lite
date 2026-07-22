import os
import sqlite3
import tempfile
from contextlib import closing
import pandas as pd
import pytest

from tests import __handle_exception
from app import save_wvr_table_to_db_file
from models import ReadOnlyModel, ReadOnlyError
from repositories import BaseRepository


@__handle_exception(is_success=True)
def test_save_wvr_table_to_db_file():
    df = pd.DataFrame({"id": [1, 2], "name": ["Alpha", "Beta"], "score": [95.5, 88.0]})
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = os.path.join(temp_dir, "test_model.db")
        save_wvr_table_to_db_file(df, db_path, "TestTable")

        assert os.path.exists(db_path)
        with closing(sqlite3.connect(db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM TestTable")
            count = cursor.fetchone()[0]
            assert count == 2


@__handle_exception(is_success=True)
def test_read_only_orm_model():
    row_data = {"id": 1, "col_a": "value_a", "col_b": 100}
    model = ReadOnlyModel(**row_data)

    # 속성 및 인덱스 접근 검증
    assert model.id == 1
    assert model.col_a == "value_a"
    assert model["col_b"] == 100

    # 읽기 전용(수정 시 예외 발생) 검증
    with pytest.raises(ReadOnlyError):
        model.id = 999

    with pytest.raises(ReadOnlyError):
        model["col_a"] = "new_val"


@__handle_exception(is_success=True)
def test_base_repository_operations():
    df = pd.DataFrame({"category": ["A", "B", "A", "C"], "val": [10, 20, 30, 40]})
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = os.path.join(temp_dir, "repo_test.db")
        save_wvr_table_to_db_file(df, db_path, "SampleData")

        repo = BaseRepository(db_path=db_path, table_name="SampleData")

        # 레코드 수 확인
        assert repo.count() == 4

        # find_all 검증
        all_records = repo.find_all()
        assert len(all_records) == 4
        assert isinstance(all_records[0], ReadOnlyModel)

        # 인덱스 생성 검증
        repo.create_index(["category"])

        # find_by 필터링 검증
        category_a_records = repo.find_by({"category": "A"})
        assert len(category_a_records) == 2
        assert category_a_records[0].category == "A"
        assert category_a_records[1].category == "A"
