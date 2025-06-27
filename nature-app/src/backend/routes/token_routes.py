from fastapi import APIRouter

router = APIRouter()

@router.get("/token", tags=["token"])
async def get_token():
    return [{"text": "This is the token path"}]