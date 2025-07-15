from controllers.results_controller import ResultsController
from deps import SessionDep
from fastapi import APIRouter

router = APIRouter()
results_controller = ResultsController()


@router.get("/results", tags=["results"])
async def get_results():
    return [{"text": "This is the results path"}]

@router.post("/results/analyse", tags=["results"])
async def analyse_area(session: SessionDep):
    return await results_controller.analyse_area(session)


@router.get("/results/{result_id}", tags=["results"])
async def get_result(result_id: str):
    return [{"text": f"This is the result {result_id} path"}]

