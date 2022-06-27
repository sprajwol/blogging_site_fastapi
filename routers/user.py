import json
from fastapi import APIRouter, Depends, Response, status, HTTPException
from bson import ObjectId
from typing import List
from pymongo.errors import WriteError
from bson import json_util

from config.database import conn_str
from schemas.user import serializeDict, serializeList, userDict, userList
from models.user import Approval, User, AdminUserCreation
from utils import auth_utils, utils

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


@user.get('/waiting_approval', dependencies=[Depends(auth_utils.RoleChecker(['admin']))])
async def find_all_users_waiting_approval(current_user: dict = Depends(auth_utils.get_current_user)):
    return userList(conn_str.test_db.user.find({"is_approved": False}))


@user.post('/approve_user', dependencies=[Depends(auth_utils.RoleChecker(['admin']))])
async def approve_user(data: Approval, current_user: dict = Depends(auth_utils.get_current_user)):
    waiting_approval_user = conn_str.test_db.user.find_one_and_update({"_id": ObjectId(data.user_id)}, {
        "$set": {
            "is_approved": data.approved,
            "approved_by": current_user["name"]
        }
    })

    return userList(conn_str.test_db.user.find({"_id": ObjectId(waiting_approval_user["_id"])}))

@user.get('/waiting_approval', dependencies=[Depends(auth_utils.RoleChecker(['admin']))], status_code=201)
async def create_multiple_users(user: List[User], current_user: dict = Depends(auth_utils.get_current_user)):
    return "created"


@user.delete('/delete_single_user', dependencies=[Depends(auth_utils.RoleChecker(['admin']))])
async def delete_user(user_id: str, response:Response, current_user: dict = Depends(auth_utils.get_current_user)):
    user = conn_str.test_db.user.find_one_and_delete({"_id": ObjectId(user_id)})

    if user:
        return {
            "detail" "The user has been deleted."
        }
    else:
        response.status_code=404
        return {
            "detail": f"User with user_id '{user_id} is not found."
        }

@user.post('/create_multiple_users', dependencies=[Depends(auth_utils.RoleChecker(['admin']))], status_code=status.HTTP_201_CREATED)
async def create_multiple_users(users: List[AdminUserCreation], response:Response, current_user: dict = Depends(auth_utils.get_current_user)):
    for each_user in users:
        raw_password = each_user.password
        hashed_password = utils.hash(raw_password)
        each_user.password = hashed_password
        each_user.approved_by = str(current_user['_id'])

        try:
            user = conn_str.test_db.user.insert_one(dict(each_user))
        except WriteError as e:
            response.status = status.HTTP_400_BAD_REQUEST
            return {
                "detail": json.loads(json_util.dumps(e.details)),
                "input_data": users
            }
    
    return {
        "detail":"All the users have been successfully created."
    }