from pydantic import BaseModel
from src.utils.security import get_env_var


class Settings(BaseModel):
    ADP_USERNAME: str = get_env_var("ADP_USERNAME")
    ADP_PASSWORD: str = get_env_var("ADP_PASSWORD")
    ADP_LOGIN_URL: str = get_env_var("ADP_LOGIN_URL")
    TOLERANCE_THRESHOLD: float = float(get_env_var("TOLERANCE_THRESHOLD", "0.05"))
    LOG_LEVEL: str = get_env_var("LOG_LEVEL", "INFO")


settings = Settings()