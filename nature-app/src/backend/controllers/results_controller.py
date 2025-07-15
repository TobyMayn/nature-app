from exceptions import InvalidAlgorithmException, NoAnalysisTypeException
from fastapi import HTTPException, status
from models import AnalysisBody
from services.algorithm_service import AlgorithmService
from sqlmodel import Session

algorithm_service = AlgorithmService()

class ResultsController():
    async def analyse_area(self, session: Session, body: AnalysisBody):
        try:
            return await algorithm_service.create_analysis(session, body)
        
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
        except Exception:
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not process request",
                )