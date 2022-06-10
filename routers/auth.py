import json
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT
from pymongo.errors import WriteError
from bson import json_util

from models.user import UserLogin, User
from schemas.user import serializeDict, serializeList
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
    print(f"inside signup:{user}")
    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    try:
        user = conn_str.test_db.user.insert_one(dict(user))
        # print(f"user:{user['_id']}")
    except WriteError as e:
        raise HTTPException(status_code=400, detail=json.loads(
            json_util.dumps(e.details)))
    return serializeList(conn_str.test_db.user.find({}))


@auth.post('/refresh_token')
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
