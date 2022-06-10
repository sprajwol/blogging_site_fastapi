import json
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT
from pymongo.errors import WriteError
from bson import json_util

from models.user import UserLogin, User
from schemas.user import serializeDict, serializeList
from config.database import conn_str
from config.redis import redis_conn
from config.config import auth_jwt_settings
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
    access_token = Authorize.create_access_token(
        subject=user['email'], fresh=True)
    refresh_token = Authorize.create_refresh_token(subject=user['email'])

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer"
    }


@auth.post('/signup', status_code=201)
def signup(user: User):
    # print(f"inside signup:{user}")
    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    try:
        user = conn_str.test_db.user.insert_one(dict(user))
        # print(f"user:{user['_id']}")
    except WriteError as e:
        raise HTTPException(status_code=400, detail=json.loads(
            json_util.dumps(e.details)))
    return serializeList(conn_str.test_db.user.find({}))


@auth.post('/token_refresh')
def refresh(Authorize: AuthJWT = Depends()):
    """
    Refresh token endpoint. This will generate a new access token from
    the refresh token, but will mark that access token as non-fresh,
    as we do not actually verify a password in this endpoint.
    """
    Authorize.jwt_refresh_token_required()

    current_user = Authorize.get_jwt_subject()
    new_access_token = Authorize.create_access_token(
        subject=current_user, fresh=False)
    return {"access_token": new_access_token}

# Endpoint for revoking the current users access token


@auth.delete('/access_revoke')
def access_revoke(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    # Store the tokens in redis with the value true for revoked.
    # We can also set an expires time on these tokens in redis,
    # so they will get automatically removed after they expired.
    jti = Authorize.get_raw_jwt()['jti']
    redis_conn.setex(jti, auth_jwt_settings.access_expires, 'true')
    return {"detail": "Access token has been revoked."}

# Endpoint for revoking the current users refresh token


@auth.delete('/refresh_revoke')
def refresh_revoke(Authorize: AuthJWT = Depends()):
    Authorize.jwt_refresh_token_required()

    jti_refresh = Authorize.get_raw_jwt()['jti']
    redis_conn.setex(jti_refresh, auth_jwt_settings.refresh_expires, 'true')
    return {"detail": "Refresh token has been revoked."}
