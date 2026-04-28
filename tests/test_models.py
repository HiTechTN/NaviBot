from decimal import Decimal
import pytest
from src.grasp.models import ItalianPayrollRecord


def test_italian_payroll_record_valid():
    record = ItalianPayrollRecord(
        employee_id="12345",
        base_salary=Decimal("50000.00"),
        irpef_tax=Decimal("10000.00"),
        net_pay=Decimal("40000.00")
    )
    assert record.employee_id == "12345"


def test_italian_payroll_record_invalid_net():
    with pytest.raises(ValueError):
        ItalianPayrollRecord(
            employee_id="12345",
            base_salary=Decimal("50000.00"),
            irpef_tax=Decimal("10000.00"),
            net_pay=Decimal("-100.00")
        )