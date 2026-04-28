import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright
from src.config.settings import settings
from src.utils.logger import get_logger, take_screenshot

logger = get_logger(__name__)
STORAGE_STATE_PATH = Path("storage_state.json")
INSPECTION_OUTPUT = Path("logs/adp_inspection.json")


async def inspect_adp_interface():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            storage_state=STORAGE_STATE_PATH if STORAGE_STATE_PATH.exists() else None
        )
        page = await context.new_page()

        if not STORAGE_STATE_PATH.exists():
            logger.info("No session found, logging in")
            await page.goto(settings.ADP_LOGIN_URL)
            await page.get_by_role("textbox", name="Username").fill(settings.ADP_USERNAME)
            await page.get_by_role("textbox", name="Password").fill(settings.ADP_PASSWORD)
            await page.get_by_role("button", name="Login").click()
            await page.wait_for_url("**/dashboard", timeout=30000)
            await context.storage_state(path=STORAGE_STATE_PATH)

        await page.get_by_role("link", name="Payroll").click()
        await page.wait_for_load_state("networkidle")

        frames_info = [
            {
                "name": frame.name,
                "url": frame.url,
                "is_detached": frame.is_detached(),
                "parent": frame.parent_frame.name if frame.parent_frame else None
            }
            for frame in page.frames if frame != page.main_frame
        ]

        payroll_frame = next(
            (f for f in page.frames if f != page.main_frame and "payroll" in f.url.lower()),
            page.frames[1] if len(page.frames) > 1 else None
        )

        elements_info = []
        if payroll_frame:
            inputs = await payroll_frame.query_selector_all("input, select, textarea")
            for inp in inputs:
                elements_info.append({
                    "tag": await inp.evaluate("el => el.tagName.toLowerCase()"),
                    "aria-label": await inp.get_attribute("aria-label"),
                    "name": await inp.get_attribute("name"),
                    "role": await inp.get_attribute("role"),
                    "value": await inp.input_value() if await inp.get_attribute("type") not in ["password", "hidden"] else "***"
                })

            text_elems = await payroll_frame.query_selector_all("label, div, span")
            for elem in text_elems:
                text = await elem.inner_text()
                if any(k in text.lower() for k in ["salary", "irpef", "net", "gross", "inps", "tfr"]):
                    elements_info.append({
                        "text": text.strip(),
                        "aria-label": await elem.get_attribute("aria-label"),
                        "role": await elem.get_attribute("role")
                    })

        result = {
            "frames": frames_info,
            "payroll_elements": elements_info[:50],
            "current_url": page.url
        }

        INSPECTION_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        INSPECTION_OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False))
        logger.info(f"Inspection results saved to {INSPECTION_OUTPUT}")
        await take_screenshot(page, "adp_inspection")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(inspect_adp_interface())