from fastapi import Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT
from bson import ObjectId
from typing import List

from models.user import User
from config.database import conn_str
from schemas.user import serializeDict


def get_current_user(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"The Access Token could not be validated.")

    current_user = Authorize.get_jwt_subject()

    user = conn_str.test_db.user.find_one({"email": current_user})

    return serializeDict(user)


class RoleChecker:
    def __init__(self, allowed_roles: List):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)):
        # user = serializeDict(user)
        # print(user)
        if user['role'] not in self.allowed_roles:
            raise HTTPException(
                status_code=403, detail="Operation not permitted")
