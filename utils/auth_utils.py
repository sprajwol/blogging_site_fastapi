from fastapi import Depends
from fastapi_jwt_auth import AuthJWT
from bson import ObjectId

from config.database import conn_str
from schemas.user import serializeDict


def get_current_user(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    current_user = Authorize.get_jwt_subject()

    user = conn_str.test_db.user.find_one({"email": current_user})

    return serializeDict(user)
