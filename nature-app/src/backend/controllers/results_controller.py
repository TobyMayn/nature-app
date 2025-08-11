from database.results import ResultsAccess
from exceptions import InvalidAlgorithmException, NoAnalysisTypeException
from fastapi import HTTPException, status
from models import AnalysisBody
from services.algorithm_service import AlgorithmService
from sqlmodel import Session

algorithm_service = AlgorithmService()
db_results = ResultsAccess()

class ResultsController():
    async def analyse_area(self, user_id: int, session: Session, body: AnalysisBody):
        try:
            return await algorithm_service.create_analysis(user_id, session, body)
        
        except NoAnalysisTypeException:
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing analysis type in request body",
                )
        except InvalidAlgorithmException:
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Wrong analysis type provided",
                )
        except Exception as e:
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Could not process request: {e}",
                )
    
    async def get_results(self, user_id: int, session: Session, offset: int = 0, limit: int = 10):
        return await db_results.get_results(session, offset=offset, limit=limit, user_id=user_id)
    
    async def get_result_by_id(self, session: Session, result_id: int, user_id: int):
        try:
            result = await db_results.get_result_by_id(session, result_id, user_id)
            if result is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Result with ID {result_id} not found or access denied"
                )
            return result
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Could not retrieve result: {e}"
            )