import os
import sys
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

try:
    import keyring
    HAS_KEYRING = True
except ImportError:
    HAS_KEYRING = False

KEYRING_SERVICE = "WebPayAutomator"
ENV_MAP = {
    "ADP_USERNAME": "ADP_USERNAME",
    "ADP_PASSWORD": "ADP_PASSWORD",
    "ADP_LOGIN_URL": "ADP_LOGIN_URL",
}


class CredentialManager:
    @staticmethod
    def discover() -> dict[str, str | None]:
        creds = {}

        # 1. Try environment variables first
        for key, env_key in ENV_MAP.items():
            val = os.getenv(env_key)
            if val:
                creds[key] = val
                logger.info(f"Found {key} from environment variable")
            else:
                creds[key] = None

        # 2. Fall back to OS keyring
        if HAS_KEYRING:
            try:
                for key, env_key in ENV_MAP.items():
                    if not creds[key]:
                        val = keyring.get_password(KEYRING_SERVICE, key)
                        if val:
                            creds[key] = val
                            logger.info(f"Found {key} from OS keyring ({KEYRING_SERVICE})")
            except Exception as e:
                logger.warning(f"Keyring access failed: {e}")

        return creds

    @staticmethod
    def save_to_keyring(username: str, password: str, url: str):
        if not HAS_KEYRING:
            logger.warning("keyring not available, cannot save credentials")
            return
        try:
            keyring.set_password(KEYRING_SERVICE, "ADP_USERNAME", username)
            keyring.set_password(KEYRING_SERVICE, "ADP_PASSWORD", password)
            keyring.set_password(KEYRING_SERVICE, "ADP_LOGIN_URL", url)
            logger.info(f"Credentials saved to OS keyring '{KEYRING_SERVICE}'")
        except Exception as e:
            logger.error(f"Failed to save credentials to keyring: {e}")

    @staticmethod
    def has_credentials(creds: dict[str, str | None]) -> bool:
        return all(creds.get(k) for k in ["ADP_USERNAME", "ADP_PASSWORD", "ADP_LOGIN_URL"])


def mask_pii(value: str, visible_chars: int = 4) -> str:
    if len(value) <= visible_chars:
        return "*" * len(value)
    return value[:visible_chars] + "*" * (len(value) - visible_chars)