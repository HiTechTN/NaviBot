from src.grasp.models import ItalianPayrollRecord
from src.control.italian_payroll import ItalianPayrollCalculator
from src.control.rules import RuleEngine


class Reconciler:
    def __init__(self):
        self.calculator = ItalianPayrollCalculator()
        self.rule_engine = RuleEngine()

    def reconcile(self, record: ItalianPayrollRecord, years_of_service: int = 1, days_worked: int = 30) -> dict:
        theoretical_irpef = self.calculator.calculate_irpef(record.base_salary, {})
        theoretical_net = record.base_salary - theoretical_irpef
        
        anomalies = self.rule_engine.check_anomalies(record, {
            "irpef_tax": theoretical_irpef,
            "net_pay": theoretical_net
        })
        
        return {
            "extracted": record.model_dump(),
            "theoretical": {
                "irpef_tax": str(theoretical_irpef),
                "net_pay": str(theoretical_net)
            },
            "anomalies": anomalies
        }