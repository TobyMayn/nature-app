from controllers.results_controller import ResultsController
from deps import SessionDep, get_current_user
from fastapi import APIRouter, Depends
from models import AnalysisBody, Users

router = APIRouter()
results_controller = ResultsController()


@router.get("/results", tags=["results"])
async def get_results():
    return [{"text": "This is the results path"}] #TODO: 

@router.post("/results/analyse", tags=["results"])
async def analyse_area( session: SessionDep, body: AnalysisBody, user: Users = Depends(get_current_user)):
    return await results_controller.analyse_area(user.user_id, session, body)


@router.get("/results/{result_id}", tags=["results"])
async def get_result(result_id: str):
    return [{"text": f"This is the result {result_id} path"}] #TODO: implement

