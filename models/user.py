from enum import Enum
from pydantic import BaseModel, EmailStr


class ROLES_M(Enum):
    ADMIN = 'admin'
    MAKER = 'maker'
    CHECKER = 'checker'

class AdminUserCreation(BaseModel):
    name: str
    contact_number: str = None
    # picture: str = None
    email: EmailStr
    password: str
    role: ROLES_M = ROLES_M.MAKER
    is_approved: bool = True
    approved_by: str = None

class User(BaseModel):
    name: str
    contact_number: str = None
    # picture: str = None
    email: EmailStr
    password: str
    role: ROLES_M = ROLES_M.MAKER
    is_approved: bool = False
    approved_by: str = None

    class Config:
        use_enum_values = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class Approval(BaseModel):
    user_id: str
    approved: bool
