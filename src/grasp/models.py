from decimal import Decimal
from pydantic import BaseModel, field_validator


class ItalianPayrollRecord(BaseModel):
    employee_id: str
    base_salary: Decimal
    irpef_tax: Decimal
    net_pay: Decimal
    gross_pay: Decimal | None = None
    inps_contribution: Decimal | None = None
    tfr_accrual: Decimal | None = None

    @field_validator(
        "net_pay",
        "base_salary",
        "irpef_tax",
        "gross_pay",
        "inps_contribution",
        "tfr_accrual",
        mode="before",
    )
    @classmethod
    def validate_decimal(cls, v):
        if v is None:
            return None
        if isinstance(v, Decimal):
            return v
        try:
            return Decimal(str(v))
        except Exception:
            raise ValueError(f"Invalid decimal value: {v}")

    @field_validator("net_pay")
    @classmethod
    def check_positive_net(cls, v):
        if v <= 0:
            raise ValueError("Le salaire net doit être positif")
        return v

    @field_validator("base_salary")
    @classmethod
    def check_positive_base(cls, v):
        if v <= 0:
            raise ValueError("Le salaire de base doit être positif")
        return v