import asyncio
from src.grasp.browser import ADPBrowser
from src.grasp.extractor import PayrollExtractor
from src.control.reconciler import Reconciler
from src.utils.logger import get_logger

logger = get_logger(__name__)


async def main():
    browser = ADPBrowser()
    try:
        page = await browser.initialize()
        await browser.login()
        extractor = PayrollExtractor(page)
        record = await extractor.extract_payroll_record("12345")
        logger.info(f"Extracted record: {record}")
        
        reconciler = Reconciler()
        result = reconciler.reconcile(record)
        logger.info(f"Reconciliation result: {result}")
    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise
    finally:
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())