from fastapi import APIRouter, Depends
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from bson import ObjectId

from config.database import conn_str
from schemas.user import serializeDict, serializeList, userDict, userList
from models.user import Approval

user = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@user.get('/')
async def find_all_approved_users():
    return serializeList(conn_str.test_db.user.find({"is_approved": True}))


@user.get('/all')
async def find_all_approved_users():
    return serializeList(conn_str.test_db.user.find({}))


# @user.get('/waiting_approval', dependencies=[Depends(oauth2.RoleChecker(['checker']))])
@user.get('/waiting_approval')
async def find_all_users_waiting_approval():
    print(f"conn.fastapi")
    return userList(conn_str.fastapi.user.find({"is_approved": False}))


@user.post('/approve')
async def approve_users(data: Approval):
    print(f"data ::: {data.user_id}")
    # print(f"current_user ::: {current_user}")
    waiting_approval_user = conn_str.fastapi.user.find_one_and_update({"_id": ObjectId(data.user_id)}, {
        "$set": {
            "is_approved": data.approved,
            # "approved_by": current_user["name"]
        }
    })
    print(f"waiting_approval_user ::: {waiting_approval_user}")
    return "this is approved"
