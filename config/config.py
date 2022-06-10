from pydantic import BaseSettings


class JWTSettings(BaseSettings):
    authjwt_secret_key: str = "secret"

    class Config:
        env_file = '.env'


auth_jwt_settings = JWTSettings()
