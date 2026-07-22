import os
import dotenv

dotenv.load_dotenv()
ALM_WVR_PATH = os.environ.get("ALM_WVR_PATH")
SII_WVR_PATH = os.environ.get("SII_WVR_PATH")
DB_PATH = os.environ.get("DB_PATH")
DIVIDED_UNIT_1 = 1_000_000
MAX_THREAD_WORKERS = 60
MAX_PROCESS_WORKERS = 12
