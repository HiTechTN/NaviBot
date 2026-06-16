import sys
from pathlib import Path
from loguru import logger
from functools import partial

# Remove default handler
logger.remove()

# Add file handler with rotation
logger.add(
    "logs/automator.log",
    rotation="10 MB",
    retention="30 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    filter=lambda record: "sensitive" not in record["extra"]
)

# Add console handler
logger.add(
    sys.stdout,
    format="{level} | {message}",
    filter=lambda record: "sensitive" not in record["extra"]
)


def get_logger(name: str = __name__):
    return logger.bind(name=name)


async def take_screenshot(page, name: str):
    path = Path(f"logs/screenshots/{name}.png")
    path.parent.mkdir(parents=True, exist_ok=True)
    await page.screenshot(path=path)
    logger.info(f"Screenshot saved to {path}")