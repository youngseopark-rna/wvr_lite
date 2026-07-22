from app import export_all_wvr_to_db
from environments import DB_PATH, SII_WVR_PATH, ALM_WVR_PATH
from orm_convertor import convert_db_to_orm

import logging
import sys

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

if not root_logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(asctime)s - %(message)s"))
    root_logger.addHandler(handler)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if __name__ == "__main__":
    logger.info("Convert SII wvr files to .db for SQLite")
    if export_all_wvr_to_db(SII_WVR_PATH, DB_PATH):
        logger.info("SII DB Migration to SQLite Done! Check out the directory")

    logger.info("Convert ALM wvr files to .db for SQLite")
    if export_all_wvr_to_db(ALM_WVR_PATH, DB_PATH):
        logger.info("ALM DB Migration to SQLite Done! Check out the directory")

    if convert_db_to_orm():
        logger.info("Converting db into ORM completed")
