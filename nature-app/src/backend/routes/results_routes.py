from fastapi import APIRouter

router = APIRouter()

@router.get("/results", tags=["results"])
async def get_results():
    return [{"text": "This is the results path"}]

@router.get("/results/{result_id}", tags=["results"])
async def get_result(result_id: str):
    return [{"text": f"This is the result {result_id} path"}]