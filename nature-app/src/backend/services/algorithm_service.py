

import re
from datetime import datetime

from algorithms.algo_factory import (  # noqa: F401
    ConcreteAlgorithmFactory,
    InvalidAlgorithmException,
)
from database.location import LocationAccess
from database.results import ResultsAccess
from exceptions import NoAnalysisTypeException  # noqa: F401
from models import AnalysisBody, AnalysisPayload  # noqa: F401
from services.image_service import ImageDownloadService
from sqlmodel import Session

concrete_algorithm_factory = ConcreteAlgorithmFactory()
db_location = LocationAccess()
db_results = ResultsAccess()
image_service = ImageDownloadService()

layers = {
    "ortho": ['geodanmark_2024_12_5cm', 
              'geodanmark_2023_12_5cm', 
              'geodanmark_2022_12_5cm', 
              'geodanmark_2021_12_5cm', 
              'geodanmark_2020_12_5cm', 
              'geodanmark_2019_12_5cm', 
              'geodanmark_2018_12_5cm', 
              'geodanmark_2017_12_5cm', 
              'geodanmark_2016_12_5cm', 
              'geodanmark_2015_12_5cm'],
    "satellite": ["Add layers when algorithm is implemented"]
}

class AlgorithmService:
    async def create_analysis(self, user_id: int, session: Session, body: AnalysisBody):
        analysis_type = body.analysis_type
        polygon = body.polygon
        try:
            location_id = await db_location.create_location(session, polygon)

            result_id = await db_results.create_results(session, body, user_id, location_id)

        except Exception as e:
            raise e
        
        if not analysis_type:
            raise NoAnalysisTypeException
        
        start_date = body.start_date
        end_date = body.end_date
        # Download photos for analysis
        image_service.download_images_for_analysis(analysis_type=analysis_type, polygon=polygon, date_range=(start_date, end_date), layers=self._filter_layers(layers[analysis_type]))
        
        
        try:
            # Get algorithm based on analysis type
            algorithm = concrete_algorithm_factory.create_algorithm(analysis_type)
        except InvalidAlgorithmException as e:
            raise e
        
        try:
            # Run analysis
            result = algorithm.predict_change()
        except Exception as e:
            raise e

        result_id = db_results.update_results(session, result_id, result)

        return AnalysisPayload(result_id=result_id)
    
    def _filter_layers(self, start_date: datetime, end_date: datetime) -> list:
        filtered_layers = []
        year_regex = r'geodanmark_(\d{4})_12_5cm'
        for layer in layers:
            match = re.search(year_regex, layer)
            if match:
                year = int(match.group(1))
                if start_date.year <= year <= end_date.year:
                    filtered_layers.append(layer)

        return filtered_layers

        

    