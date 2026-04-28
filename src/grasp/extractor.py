from decimal import Decimal
from pathlib import Path
from bs4 import BeautifulSoup
from playwright.async_api import Page, Frame
from src.grasp.models import ItalianPayrollRecord
from src.utils.logger import get_logger, take_screenshot
from src.utils.retry import retry_with_backoff

logger = get_logger(__name__)


class PayrollExtractor:
    def __init__(self, page: Page, payroll_frame_name: str = None):
        self.page = page
        self.payroll_frame_name = payroll_frame_name
        self.raw_html_dir = Path("logs/raw_html")
        self.raw_html_dir.mkdir(parents=True, exist_ok=True)

    def _get_payroll_frame(self) -> Frame:
        for frame in self.page.frames:
            if frame == self.page.main_frame:
                continue
            if self.payroll_frame_name and frame.name == self.payroll_frame_name:
                return frame
            if "payroll" in frame.url.lower():
                return frame
        raise ValueError("Payroll iframe not found")

    @retry_with_backoff(max_retries=3, base_delay=2.0)
    async def extract_payroll_record(self, employee_id: str) -> ItalianPayrollRecord:
        try:
            await self.page.get_by_role("link", name="Payroll", exact=False).click()
            await self.page.wait_for_load_state("networkidle", timeout=30000)

            frame = self._get_payroll_frame()
            await frame.wait_for_selector("[role='textbox'], input", timeout=15000)

            base_salary = await self._extract_field(frame, "Base Salary")
            irpef_tax = await self._extract_field(frame, "IRPEF Tax")
            net_pay = await self._extract_field(frame, "Net Pay")
            gross_pay = await self._extract_field(frame, "Gross Pay", required=False)
            inps = await self._extract_field(frame, "INPS", required=False)
            tfr = await self._extract_field(frame, "TFR", required=False)

            await take_screenshot(self.page, f"extraction_{employee_id}")

            record = ItalianPayrollRecord(
                employee_id=employee_id,
                base_salary=Decimal(base_salary),
                irpef_tax=Decimal(irpef_tax),
                net_pay=Decimal(net_pay),
                gross_pay=Decimal(gross_pay) if gross_pay else None,
                inps_contribution=Decimal(inps) if inps else None,
                tfr_accrual=Decimal(tfr) if tfr else None
            )

            html_path = self.raw_html_dir / f"{employee_id}.html"
            html_path.write_text(await frame.content())
            logger.info(f"Raw HTML saved to {html_path}")

            return record

        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            await take_screenshot(self.page, f"error_{employee_id}")
            raise

    async def _extract_field(self, frame: Frame, label: str, required: bool = True) -> str | None:
        for strategy in [
            lambda: frame.get_by_text(label, exact=False).first.locator("..").get_by_role("textbox").first.input_value(),
            lambda: frame.get_by_role("textbox", name=label, exact=False).first.input_value(),
            lambda: frame.locator(f"[aria-label*='{label}']").first.input_value()
        ]:
            try:
                val = await strategy()
                if val:
                    return val
            except Exception:
                continue
        if required:
            raise ValueError(f"Field '{label}' not found")
        return None

    def parse_offline_html(self, html_path: Path, employee_id: str) -> ItalianPayrollRecord:
        soup = BeautifulSoup(html_path.read_text(), "lxml")
        def extract(keyword: str) -> Decimal:
            elem = soup.find(text=lambda t: t and keyword.lower() in t.lower())
            if elem:
                import re
                match = re.search(r"[\d,]+\.\d{2}", elem.find_parent().get_text())
                if match:
                    return Decimal(match.group().replace(",", ""))
            raise ValueError(f"Offline parse failed for {keyword}")
        
        return ItalianPayrollRecord(
            employee_id=employee_id,
            base_salary=extract("Base Salary"),
            irpef_tax=extract("IRPEF"),
            net_pay=extract("Net Pay")
        )