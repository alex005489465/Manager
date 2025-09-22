import logging
from pathlib import Path
from .config import config


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """設定日誌記錄系統

    配置同時輸出到文件和控制台的日誌記錄器。
    日誌文件將保存所有收集過程的詳細記錄。

    Args:
        level (int, optional): 日誌級別，預設為 INFO

    Returns:
        logging.Logger: 配置好的日誌記錄器

    Note:
        這個函數會配置全局的日誌系統，影響所有後續的日誌輸出。
        確保在程式開始時只調用一次。
    """
    # 確保日誌目錄存在
    config.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    # 配置日誌系統
    logging.basicConfig(
        level=level,
        format=config.LOG_FORMAT,
        handlers=[
            # 文件輸出（支持 UTF-8 編碼）
            logging.FileHandler(config.LOG_FILE, encoding='utf-8'),
            # 控制台輸出
            logging.StreamHandler()
        ],
        # 強制重新配置，避免重複的 handler
        force=True
    )

    logger = logging.getLogger(__name__)
    logger.info(f"日誌系統已初始化 - 日誌檔案: {config.LOG_FILE}")

    return logger


def get_logger(name: str) -> logging.Logger:
    """獲取指定名稱的日誌記錄器

    Args:
        name (str): 日誌記錄器名稱，通常使用 __name__

    Returns:
        logging.Logger: 日誌記錄器實例

    Note:
        確保在調用此函數之前已經調用過 setup_logging()
    """
    return logging.getLogger(name)


def configure_module_logger(module_name: str, level: int = None) -> logging.Logger:
    """配置特定模組的日誌記錄器

    Args:
        module_name (str): 模組名稱
        level (int, optional): 特定的日誌級別，如果不提供則使用預設級別

    Returns:
        logging.Logger: 配置好的模組日誌記錄器
    """
    logger = logging.getLogger(module_name)

    if level is not None:
        logger.setLevel(level)

    return logger