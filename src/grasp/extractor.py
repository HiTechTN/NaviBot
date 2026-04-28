from decimal import Decimal
from playwright.async_api import Page
from src.grasp.models import ItalianPayrollRecord
from src.utils.logger import get_logger, take_screenshot

logger = get_logger(__name__)


class PayrollExtractor:
    def __init__(self, page: Page):
        self.page = page

    async def extract_payroll_record(self, employee_id: str) -> ItalianPayrollRecord:
        await self.page.get_by_role("link", name="Payroll").click()
        await self.page.wait_for_load_state("networkidle")
        frame = self.page.frame_locator("iframe[name='payroll-frame']")
        
        base_salary = await frame.get_by_text("Base Salary").locator("..").get_by_role("textbox").input_value()
        irpef_tax = await frame.get_by_text("IRPEF Tax").locator("..").get_by_role("textbox").input_value()
        net_pay = await frame.get_by_text("Net Pay").locator("..").get_by_role("textbox").input_value()
        
        await take_screenshot(self.page, f"extraction_{employee_id}")
        return ItalianPayrollRecord(
            employee_id=employee_id,
            base_salary=Decimal(base_salary),
            irpef_tax=Decimal(irpef_tax),
            net_pay=Decimal(net_pay)
        )