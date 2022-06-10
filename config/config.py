from pydantic import BaseSettings
from datetime import timedelta


class JWTSettings(BaseSettings):
    authjwt_secret_key: str = "secret"
    authjwt_denylist_enabled: bool = True
    authjwt_denylist_token_checks: set = {"access", "refresh"}
    access_expires: int = timedelta(minutes=15)
    refresh_expires: int = timedelta(days=30)

    class Config:
        env_file = '.env'


auth_jwt_settings = JWTSettings()
