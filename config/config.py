from pydantic import BaseSettings


class JWTSettings(BaseSettings):
    authjwt_secret_key: str = "secret"
