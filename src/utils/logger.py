import logging
import os
from pathlib import Path


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))
    
    audit_handler = logging.FileHandler(Path("logs/audit.log"))
    audit_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
    
    logger.addHandler(audit_handler)
    logger.addHandler(console_handler)
    return logger


async def take_screenshot(page, name: str):
    path = Path(f"logs/screenshots/{name}.png")
    path.parent.mkdir(parents=True, exist_ok=True)
    await page.screenshot(path=path)
    logger = get_logger(__name__)
    logger.info(f"Screenshot saved to {path}")