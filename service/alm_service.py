from pathlib import Path
import logging

from config.environments import DB_PATH
from config.database import get_db_session_by_name
from repositories.table_repository import GenericReadOnlyTableRepository


class AlmService:
    logger = logging.getLogger(__name__)

    def __init__(self, repo_dict: dict):
        self.repo_dict = repo_dict

    @classmethod
    async def create(cls):
        db_dir = Path(DB_PATH)
        prefix = "ALM_"
        target_db_files = [file.stem for file in db_dir.glob(f"{prefix}*.db")]

        repo_dict = dict()
        for db in target_db_files:
            cls.logger.info(f"DB Name: {db}")
            async_session_gen = get_db_session_by_name(db)
            session = await anext(async_session_gen)
            repo_dict[db] = GenericReadOnlyTableRepository(session)

        return cls(repo_dict)

    async def get_datas_from_all_db(
        self,
        table_name: str,
        columns: list[str],
        where_clause: str = None,
        group_by: str = None,
        having: str = None,
        order_by: str = None,
        limit: int = 100,
        offset: int = 0,
    ):
        result_dict = dict()
        for repo_name, repo in self.repo_dict.items():
            result_dict[repo_name] = await repo.find(
                table_name=table_name,
                columns=columns,
                where_clause=where_clause,
                group_by=group_by,
                having=having,
                order_by=order_by,
                limit=limit,
                offset=offset,
            )
            self.logger.info(f"Query result: {result_dict[repo_name]}")
        return result_dict
