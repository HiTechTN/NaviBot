import asyncio
from pathlib import Path
from playwright.async_api import async_playwright, Browser, Page
from src.config.settings import settings
from src.utils.logger import get_logger, take_screenshot

logger = get_logger(__name__)
STORAGE_STATE_PATH = Path("storage_state.json")


class ADPBrowser:
    def __init__(self):
        self.browser: Browser | None = None
        self.page: Page | None = None
        self.playwright = None

    async def initialize(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)
        if STORAGE_STATE_PATH.exists():
            logger.info("Loading existing session state")
            self.page = await self.browser.new_page(storage_state=STORAGE_STATE_PATH)
        else:
            self.page = await self.browser.new_page()
        return self.page

    async def login(self):
        if STORAGE_STATE_PATH.exists():
            logger.info("Session exists, skipping login")
            return
        logger.info("No session found, performing login")
        await self.page.goto(settings.ADP_LOGIN_URL)
        await self.page.get_by_role("textbox", name="Username").fill(settings.ADP_USERNAME)
        await self.page.get_by_role("textbox", name="Password").fill(settings.ADP_PASSWORD)
        await self.page.get_by_role("button", name="Login").click()
        await self.page.wait_for_url("**/dashboard", timeout=30000)
        await self.page.context.storage_state(path=STORAGE_STATE_PATH)
        logger.info("Session state saved")
        await take_screenshot(self.page, "login_success")

    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Browser closed")