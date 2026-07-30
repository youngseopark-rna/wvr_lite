from config.environments import MAX_PROCESS_WORKERS

from concurrent.futures import ProcessPoolExecutor, as_completed
import subprocess
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def _run_script(db_path: list, models_dir: str):
    db_path = Path(db_path)
    file_name = db_path.stem
    model_file_path = models_dir / f"{file_name}_models.py"
    if model_file_path.is_file():
        logger.info(f"Skip the logic as the file exists: {model_file_path.name}")
        return True
    logger.info(f"File Path: {model_file_path}")

    db_uri = f"sqlite:///{db_path.resolve().as_posix()}"
    model_path_str = str(model_file_path.resolve())
    command = ["sqlacodegen", db_uri, "--outfile", model_path_str]
    logger.info(f"Proceed sqlacodegen {db_uri} --outfile models/{file_name}_models.py")

    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
    if result.returncode == 0:
        logger.info(f"Success -> {file_name}_models.py generated")
    else:
        logger.error(f"Failed -> Error: {result.stderr.strip()}")
        raise RuntimeError

    return True


def convert_db_to_orm() -> bool:
    logger.info("\nInitiate Directories")
    base_dir = Path(__file__).parent
    db_dir = base_dir / "db"
    models_dir = base_dir / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"base: {base_dir}, db: {db_dir}, models: {models_dir}")

    db_files = list(db_dir.glob("*.db"))
    if not db_files:
        logger.error("There is no db files")
        return
    logger.info(f"Found {len(db_files)} db files. Start converting...")

    with ProcessPoolExecutor(max_workers=MAX_PROCESS_WORKERS) as executor:
        futures = [
            executor.submit(_run_script, db_path, models_dir) for db_path in db_files
        ]

        for future in as_completed(futures):
            if not future.result():
                logger.error(
                    f"Error Occured during executing Multi Process: {future.exception()}"
                )
                return False

    return True
