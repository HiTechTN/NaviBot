import asyncio
from pathlib import Path
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from loguru import logger
from src.config.settings import settings
from src.utils.security import CredentialManager
from src.utils.retry import retry_with_backoff

STORAGE_STATE_PATH = Path("storage_state.json")
USER_DATA_DIR = Path(".playwright_profile")


class ADPBrowser:
    def __init__(self):
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None
        self.page: Page | None = None
        self.playwright = None

    @retry_with_backoff(max_retries=3, base_delay=2.0)
    async def initialize(self):
        self.playwright = await async_playwright().start()
        USER_DATA_DIR.mkdir(parents=True, exist_ok=True)

        if STORAGE_STATE_PATH.exists():
            logger.info("Loading saved session state")
            self.browser = await self.playwright.chromium.launch(
                headless=False,
                args=["--auth-server-whitelist=*", "--auth-negotiate-delegate-whitelist=*"]
            )
            self.context = await self.browser.new_context(storage_state=STORAGE_STATE_PATH)
        else:
            logger.info("No session found — launching clean browser for SSO")
            self.context = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(USER_DATA_DIR),
                headless=False,
                args=["--auth-server-whitelist=*", "--auth-negotiate-delegate-whitelist=*"]
            )

        self.page = self.context.pages[0] if self.context.pages else await self.context.new_page()
        return self.page

    @retry_with_backoff(max_retries=3, base_delay=2.0)
    async def login(self):
        if STORAGE_STATE_PATH.exists():
            logger.info("Session already persisted, skipping login")
            return

        creds = {
            "ADP_USERNAME": settings.ADP_USERNAME,
            "ADP_PASSWORD": settings.ADP_PASSWORD,
            "ADP_LOGIN_URL": settings.ADP_LOGIN_URL,
        }

        if CredentialManager.has_credentials(creds):
            logger.info("Using stored credentials for login")
            await self.page.goto(f"{creds['ADP_LOGIN_URL']}/login")
            await self.page.wait_for_load_state("networkidle")

            await self.page.get_by_role("textbox", name="Username").fill(creds["ADP_USERNAME"])
            await self.page.get_by_role("textbox", name="Password").fill(creds["ADP_PASSWORD"])
            await self.page.get_by_role("button", name="Login").click()
            await self.page.wait_for_url("**/dashboard", timeout=60000)

            want_save = input("Enregistrer les identifiants dans le keyring OS ? (o/N): ").strip().lower()
            if want_save == "o":
                CredentialManager.save_to_keyring(
                    creds["ADP_USERNAME"], creds["ADP_PASSWORD"], creds["ADP_LOGIN_URL"]
                )
        else:
            logger.info("No credentials found — launching SSO login")
            await self.page.goto(settings.ADP_LOGIN_URL or "https://login.adp.com")
            logger.info("Veuillez vous connecter manuellement dans le navigateur...")
            input("Appuyez sur Entrée après la connexion réussie...")

        await self.context.storage_state(path=STORAGE_STATE_PATH)
        logger.success(f"Session state saved to {STORAGE_STATE_PATH}")

    async def close(self):
        try:
            if self.context:
                await self.context.close()
        except Exception:
            pass
        try:
            if self.browser:
                await self.browser.close()
        except Exception:
            pass
        if self.playwright:
            await self.playwright.stop()
        logger.info("Browser closed")