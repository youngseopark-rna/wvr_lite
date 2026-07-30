from pathlib import Path
import os
import dotenv

env_file_path = dotenv.find_dotenv()
dotenv.load_dotenv(env_file_path)

# find the path of root directory
ENV_DIR = Path(env_file_path).resolve().parent
WVR_DIR_PATH = os.environ.get("WVR_DIR_PATH")
ALM_WVR_PATH = os.environ.get("ALM_WVR_PATH")
SII_WVR_PATH = os.environ.get("SII_WVR_PATH")
DB_PATH = ENV_DIR / "db"
R3S_DRIVER = "DRIVER={R³S Results Driver (*.wvr)};"
DIVIDED_UNIT_1 = 1_000_000
MAX_THREAD_WORKERS = 60
MAX_PROCESS_WORKERS = 12
