from imp import reload
import uvicorn
from fastapi import FastAPI, Request
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel
from fastapi.responses import JSONResponse

from routers.user import user
from routers.auth import auth
from config import config

app = FastAPI()


@AuthJWT.load_config
def get_config():
    return config.settings


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


app.include_router(auth)
app.include_router(user)


@app.get('/')
def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
