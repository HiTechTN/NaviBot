# WebPay Automator (Expert Edition)
Automation tool for Italian payroll control on ADP One Service.

## Setup
1. Copy `.env.example` to `.env` and fill in your credentials
2. Install dependencies: `pip install -r requirements.txt`
3. Install Playwright browsers: `playwright install`
4. Run: `python main.py`

## Features
- Secure ADP authentication with session persistence
- Semantic selectors to avoid UI fragility
- Italian payroll calculations (IRPEF, INPS, TFR)
- Anomaly detection with configurable thresholds
- Full audit logging + screenshots