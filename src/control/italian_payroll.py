from decimal import Decimal
from src.grasp.models import ItalianPayrollRecord


class ItalianPayrollCalculator:
    @staticmethod
    def calculate_irpef(gross_pay: Decimal, tax_brackets: dict[Decimal, Decimal]) -> Decimal:
        tax = Decimal(0)
        remaining = gross_pay
        for bracket_min, rate in sorted(tax_brackets.items()):
            if remaining <= 0:
                break
            taxable = min(remaining, bracket_min)
            tax += taxable * rate
            remaining -= taxable
        return tax.quantize(Decimal("0.01"))

    @staticmethod
    def calculate_tfr(base_salary: Decimal, years_of_service: int) -> Decimal:
        annual_tfr = base_salary * Decimal("0.0691") * years_of_service
        inflation_adjustment = annual_tfr * Decimal("0.015") * years_of_service
        return (annual_tfr + inflation_adjustment).quantize(Decimal("0.01"))

    @staticmethod
    def prorate_quattordicesima(base_salary: Decimal, days_worked: int, total_days: int = 30) -> Decimal:
        monthly_13th = base_salary / Decimal(12)
        return (monthly_13th * Decimal(days_worked) / Decimal(total_days)).quantize(Decimal("0.01"))