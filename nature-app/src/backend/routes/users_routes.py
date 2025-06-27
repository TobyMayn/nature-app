from fastapi import APIRouter

router = APIRouter()

@router.get("/users", tags=["users"])
async def read_users():
    return [{"text": "This is the users path"}]

@router.get("/users/{user_id}", tags=["users"])
async def read_user(user_id: str):
    return [{"text": f"This is the user {user_id} path"}]