import logging
import os
import sys
logger = logging.getLogger(__name__)

def set_root_logger():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers = []

    log_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(log_formatter)
    root_logger.addHandler(stdout_handler)

    log_dir = "/app/logs"
    os.makedirs(log_dir, exist_ok=True)  # 로그 폴더 자동 생성
    log_file_path = os.path.join(log_dir, "app.log")

    file_handler = logging.handlers.RotatingFileHandler(
        log_file_path, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(log_formatter)
    root_logger.addHandler(file_handler)

    for logger_name in logging.root.manager.loggerDict:
        current_logger = logging.getLogger(logger_name)
        current_logger.disabled = False
        current_logger.propagate = True

    logger.info("====================================================")
    logger.info("📢 All custom loggers successfully activated & centralized!")
    logger.info("====================================================")