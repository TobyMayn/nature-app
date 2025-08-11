from controllers.results_controller import ResultsController
from deps import SessionDep, get_current_user
from fastapi import APIRouter, Depends, Query
from models import AnalysisBody, Users

router = APIRouter()
results_controller = ResultsController()


@router.get("/results", tags=["results"])
async def get_results(
    session: SessionDep, 
    user: Users = Depends(get_current_user),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return")
):
    return await results_controller.get_results(session=session, user_id=user.user_id, offset=offset, limit=limit)

@router.post("/results/analyse", tags=["results"])
async def analyse_area( session: SessionDep, body: AnalysisBody, user: Users = Depends(get_current_user)):
    return await results_controller.analyse_area(user.user_id, session, body)


@router.get("/results/{result_id}", tags=["results"])
async def get_result_by_id(
    result_id: int,
    session: SessionDep, 
    user: Users = Depends(get_current_user)
):
    return await results_controller.get_result_by_id(session, result_id, user.user_id)

