from datetime import datetime
from typing import Annotated

from fastapi import Query
from models import AnalysisBody, Results
from sqlmodel import Session, select


class ResultsAccess:
    async def create_results(self, session: Session, body: AnalysisBody, user_id:int, location_id: int) -> int:
        
        # Create and extract fields from body object
        analysis_date = datetime.now()
        requested_at = body.requested_at
        analysis_type = body.analysis_type

        result = Results(user_id=user_id, location_id=location_id, analysis_date=analysis_date, 
                         analysis_type=analysis_type, request_params=body, requested_at=requested_at)
        
        # Create entry of result in DB
        session.add(result)
        await session.commit()
        await session.refresh(result)

        return result.results_id


    async def update_results(self, session: Session, result_id: int, result: dict) -> int:
        # Retrieve correct resulta entry to update with analysis results
        statement = select(Results).where(Results.results_id == result_id)
        results = session.exec(statement).first()
        if not results:
            raise Exception #TODO: raise correct exception

        results.status = "Complete"
        results.result = result
        results.completed_at = datetime.now()
        error_message = result.get("error_message")
        if error_message:
            results.status = "Error"
            results.error_message = error_message

        session.add(results)
        await session.commit()
        await session.refresh(results)

        return results.results_id
    
    async def get_results(self, session: Session,
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100,
    ) -> list[Results]:
        statement = select(Results).offset(offset).limit(limit)
        results = session.exec(statement).all()
        return results
