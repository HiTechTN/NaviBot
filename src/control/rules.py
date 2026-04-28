import yaml
from pathlib import Path
from decimal import Decimal
from src.grasp.models import ItalianPayrollRecord
from src.utils.logger import get_logger

logger = get_logger(__name__)


class RuleEngine:
    def __init__(self, rules_path: Path = Path("config/thresholds.yaml")):
        self.rules = yaml.safe_load(rules_path.read_text()) if rules_path.exists() else {}

    def check_anomalies(self, record: ItalianPayrollRecord, calculated: dict) -> list[str]:
        anomalies = []
        tolerance = Decimal(str(self.rules.get("tolerance_threshold", 0.05)))
        
        if "irpef_tax" in calculated:
            diff = abs(record.irpef_tax - calculated["irpef_tax"])
            if diff > tolerance:
                anomalies.append(f"IRPEF deviation: {diff} > {tolerance}")
        
        if "net_pay" in calculated:
            diff = abs(record.net_pay - calculated["net_pay"])
            if diff > tolerance:
                anomalies.append(f"Net pay deviation: {diff} > {tolerance}")
        
        return anomalies