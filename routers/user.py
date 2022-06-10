from fastapi import APIRouter, Depends
from bson import ObjectId

from config.database import conn_str
from schemas.user import serializeDict, serializeList, userDict, userList
from models.user import Approval
from utils import auth_utils

user = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@user.get('/')
async def find_all_approved_users():
    return serializeList(conn_str.test_db.user.find({"is_approved": True}))


@user.get('/all')
async def find_all_users(current_user: dict = Depends(auth_utils.get_current_user)):
    return serializeList(conn_str.test_db.user.find({}))


@user.get('/myprofile')
async def current_logged_in_user(current_user: dict = Depends(auth_utils.get_current_user)):
    return current_user


@user.get('/waiting_approval', dependencies=[Depends(auth_utils.RoleChecker(['admin', 'checker']))])
async def find_all_users_waiting_approval(current_user: dict = Depends(auth_utils.get_current_user)):
    return userList(conn_str.test_db.user.find({"is_approved": False}))


@user.post('/approve_user', dependencies=[Depends(auth_utils.RoleChecker(['admin', 'checker']))])
async def approve_user(data: Approval, current_user: dict = Depends(auth_utils.get_current_user)):
    waiting_approval_user = conn_str.test_db.user.find_one_and_update({"_id": ObjectId(data.user_id)}, {
        "$set": {
            "is_approved": data.approved,
            "approved_by": current_user["name"]
        }
    })

    return userList(conn_str.test_db.user.find({"_id": ObjectId(waiting_approval_user["_id"])}))
