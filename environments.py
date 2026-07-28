from pathlib import Path
import os
import dotenv

env_file_path = dotenv.find_dotenv()
dotenv.load_dotenv(env_file_path)

ENV_DIR = Path(env_file_path).resolve().parent

ALM_WVR_PATH = os.environ.get("ALM_WVR_PATH")
SII_WVR_PATH = os.environ.get("SII_WVR_PATH")
DB_PATH = ENV_DIR / "db"
DIVIDED_UNIT_1 = 1_000_000
MAX_THREAD_WORKERS = 60
MAX_PROCESS_WORKERS = 12
