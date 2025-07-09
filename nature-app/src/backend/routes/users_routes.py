from controllers import users_controller
from database import db
from fastapi import APIRouter

user_controller = users_controller.UsersController()

router = APIRouter()

@router.get("/users", tags=["users"])
async def read_users():
    return await user_controller.read_users()

@router.get("/users/db_test", tags=["users"])
async def get_db():
    return await db.get_db()

@router.get("/users/{user_id}", tags=["users"])
async def read_user(user_id: str):
    return await user_controller.read_user(user_id)

