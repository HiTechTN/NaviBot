from pydantic import BaseModel
from src.utils.security import CredentialManager


class Settings(BaseModel):
    ADP_USERNAME: str | None = None
    ADP_PASSWORD: str | None = None
    ADP_LOGIN_URL: str | None = None
    TOLERANCE_THRESHOLD: float = 0.05
    LOG_LEVEL: str = "INFO"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Auto-discover credentials if not already provided
        if not self.ADP_LOGIN_URL:
            creds = CredentialManager.discover()
            self.ADP_USERNAME = creds.get("ADP_USERNAME") or self.ADP_USERNAME
            self.ADP_PASSWORD = creds.get("ADP_PASSWORD") or self.ADP_PASSWORD
            self.ADP_LOGIN_URL = creds.get("ADP_LOGIN_URL") or self.ADP_LOGIN_URL


settings = Settings()