from util.wvr_convertor import export_all_wvr_to_db
from util.wvr_connector import find_out_wvr_paths
from config.environments import DB_PATH
from util.orm_convertor import convert_db_to_orm

import logging
logger = logging.getLogger(__name__)

def convert_wvr_to_orm():
    # 1. find out all the wvr file paths
    logger.info("Find out all the wvr file paths from the wvr directory")
    wvr_paths = find_out_wvr_paths()
    logger.info(f"{len(wvr_paths)} files are detected")
    if len(wvr_paths) == 0:
        logger.warn("There is no wvr files changed, so the process will be deprecated")
        return
    

    # 2. convert .wvr -> .db for SQLite
    logger.info("Convert all .wvr files -> .db for SQLite")
    for wvr_path in wvr_paths:
        if export_all_wvr_to_db(wvr_path, DB_PATH):
            logger.info(f"#{wvr_paths.index(wvr_path)} Migration Done! Check out the directory")
        else:
            logger.error("Something goes wrong")
            raise RuntimeError("Something goes wrong while export the wvr to db")

    # 3. convert .db files to sqlalchem.Table
    if convert_db_to_orm():
        logger.info("Converting db into ORM completed")

if __name__ == "__main__":
    logger.info("Convert wvr -> orm. Scripts Started")
    convert_wvr_to_orm()