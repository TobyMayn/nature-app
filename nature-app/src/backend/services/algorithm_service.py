
import os
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
from skimage import io as ski_io
from sqlmodel import Session

concrete_algorithm_factory = ConcreteAlgorithmFactory()
db_location = LocationAccess()
db_results = ResultsAccess()
image_service = ImageDownloadService()

layers_dict = {
    "orthophoto": ['geodanmark_2024_12_5cm', 
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
        polygon = body.bbox
        try:
            location_id = await db_location.create_location(session, polygon)

            result_id = await db_results.create_results(session, body, user_id, location_id)

        except Exception as e:
            raise e
        
        if not analysis_type:
            raise NoAnalysisTypeException
        
        start_date = datetime.strptime(body.start_date, "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(body.end_date, "%Y-%m-%d %H:%M:%S")
        # Download photos for analysis
        download_paths = await image_service.download_images_for_analysis(analysis_type=analysis_type, bbox=polygon, date_range=(start_date, end_date), layers=self._filter_layers(layers=layers_dict[analysis_type], start_date=start_date, end_date=end_date))
        # Retrieve earliest image by date
        img_a = ski_io.imread(download_paths["files"][0][-1])

        # Retrieve latest image by date
        img_b = ski_io.imread(download_paths["files"][0][0])
        
        
        try:
            # Get algorithm based on analysis type
            algorithm = concrete_algorithm_factory.create_algorithm(analysis_type)
        except InvalidAlgorithmException as e:
            raise e
        
        try:
            # Run analysis
            result = algorithm.predict_change(imgA_bytes=img_a, imgB_bytes=img_b, crop_size=(512, 512))
        except Exception as e:
            raise e
        finally:
            # Clean up downloaded images after analysis
            self._cleanup_downloaded_images()

        result_id = db_results.update_results(session, result_id, result)

        return AnalysisPayload(result_id=result_id)
        
    
    def _filter_layers(self, layers: list, start_date: datetime, end_date: datetime) -> list:
        filtered_layers = []
        year_regex = r'geodanmark_(\d{4})_12_5cm'
        for layer in layers:
            match = re.search(year_regex, layer)
            if match:
                year = int(match.group(1))
                if start_date.year <= year <= end_date.year:
                    filtered_layers.append(layer)

        return filtered_layers

    def _cleanup_downloaded_images(self):
        """Delete all downloaded images from the data folder after analysis."""
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        
        if not os.path.exists(data_dir):
            return
            
        for subfolder in ['orthophoto', 'satellite']:
            subfolder_path = os.path.join(data_dir, subfolder)
            if os.path.exists(subfolder_path):
                # Delete all files in the subfolder
                for file in os.listdir(subfolder_path):
                    file_path = os.path.join(subfolder_path, file)
                    if os.path.isfile(file_path):
                        try:
                            os.remove(file_path)
                            print(f"Deleted: {file_path}")
                        except Exception as e:
                            print(f"Error deleting {file_path}: {e}")

        

    