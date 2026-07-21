import os
import dotenv

dotenv.load_dotenv()
ALM_WVR_PATH = os.environ.get("ALM_WVR_PATH")
DIVIDED_UNIT_1 = 1_000_000