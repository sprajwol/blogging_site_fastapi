from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException

from models.user import UserLogin
from schemas.user import serializeDict
from config.database import conn_str
from utils import utils

auth = APIRouter(
    tags=["Auth"]
)


@auth.post('/login')
def login(user_credentials: UserLogin, Authorize: AuthJWT = Depends()):

    user = serializeDict(conn_str.test_db.user.find_one(
        {"email": user_credentials.email}))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    if not utils.verify(user_credentials.password,  user['password']):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    if not user["is_approved"] == True:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Account has not been approved. Please contact your admin.")

    # Use create_access_token() and create_refresh_token() to create our
    # access and refresh tokens
    access_token = Authorize.create_access_token(subject=user['email'])
    refresh_token = Authorize.create_refresh_token(subject=user['email'])

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer"
    }
