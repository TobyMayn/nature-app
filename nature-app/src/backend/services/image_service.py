import os
from io import BytesIO
from typing import List, Literal, Optional, Tuple

import numpy as np
import rasterio  # For satellite data handling (if needed)
from fastapi import HTTPException
from owslib.wms import WebMapService
from PIL import Image

# Import shapely for geometry processing
from sqlmodel import DateTime


# Re-incorporate the ImageDownloader from Crop_images_SG.py
# It's better to put it directly into this file or a utils file
# if it's tightly coupled to this service. For now, let's include it.
# https://services.hxgncontent.com/streaming/wms?username=DMP_DAI&password=2B276B54
class ImageDownloader:
    """
    Adapted from Crop_images_SG.py for direct use within the service.
    Downloads images from a WMS service given a bounding box.
    """
    def __init__(self, save_directory: str, min_lat: float, min_lon: float,
                 max_lat: float, max_lon: float, image_size: str,
                 length: int = 512, width: int = 512,
                 layers: list = []):
        self.save_directory = save_directory
        self.min_lon = min_lon
        self.min_lat = min_lat
        self.max_lon = max_lon
        self.max_lat = max_lat
        self.image_size_x, self.image_size_y = map(int, image_size.split('x'))
        self.length = length  # Tile length in meters
        self.width = width    # Tile width in meters
        self.layers = layers
        self.url = 'https://services.datafordeler.dk/GeoDanmarkOrto/orto_foraar/1.0.0/WMS?username=UFZLDDPIJS&password=DAIdatafordel123'
        self.wms = WebMapService(self.url, version='1.3.0')

    def _download_tile(self, min_lon: float, min_lat: float, max_lon: float, max_lat: float, file_path: str, layer: str):
        """Helper to download a single tile."""        
        # Use the same parameters as the working example
        response = self.wms.getmap(
            layers=[layer],
            styles=['default'],  # Use default style like working example
            srs='EPSG:25832',
            bbox=[self.min_lat, self.min_lon, self.max_lat, self.max_lon],  # [minx, miny, maxx, maxy] format
            size=(self.image_size_x, self.image_size_y),
            format='image/jpeg',  # Use JPEG like working example
            transparent=True
        )
        img = Image.open(BytesIO(response.read()))
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        img.save(file_path)
        print(f"Downloaded tile to: {file_path}")

    def download_images(self) -> List[str]:
        """
        Downloads images within the bounding box, potentially tiling if length/width are provided.
        Once a valid bbox is found, uses the same bbox for all layers.
        Returns a list of paths to the downloaded images.
        """
        downloaded_paths = []
        
        # Get calling files path to create relative path to /data/ folder
        script_dir = os.path.dirname(os.path.abspath(__file__))
        target_directory = os.path.normpath(os.path.join(script_dir, self.save_directory))
        self.save_directory = target_directory
        
        # Ensure directory exists
        os.makedirs(self.save_directory, exist_ok=True)
        
        # First, find a valid bbox by trying to download from the first layer
        for layer in self.layers:
            # First attempt: try the original full bbox as provided
            print("Trying original full bbox...")
            file_name = f"{layer}_{self.min_lon}_{self.min_lat}_{self.max_lon}_{self.max_lat}.jpg"
            file_path = os.path.join(self.save_directory, file_name)
            
            try:
                self._download_tile(self.min_lon, self.min_lat, self.max_lon, self.max_lat, file_path, layer)
                downloaded_paths.append(file_path)
                valid_bbox = (self.min_lon, self.min_lat, self.max_lon, self.max_lat)
                print(f"Success with bbox: {valid_bbox}")
            except Exception as e:
                print(f"Failed downloading image for layer {layer}: {e}")
            
        return downloaded_paths

class ImageDownloadService:
    def __init__(self):
        self.base_download_dir = "../data" # Base directory for all downloads

    # def _get_bounding_box_from_polygon(self, polygon: Polygon) -> Tuple[float, float, float, float]:
    #     """
    #     Extracts the bounding box (min_lon, min_lat, max_lon, max_lat)
    #     from a GeoJSON Polygon dictionary.
    #     """
    #     try:
    #         min_lon, min_lat, max_lon, max_lat = polygon.bounds
    #         return min_lon, min_lat, max_lon, max_lat
    #     except Exception as e:
    #         raise ValueError(f"Invalid  Polygon or error processing: {e}")

    async def download_images_for_analysis(
        self,
        analysis_type: Literal["ortho", "satellite"],
        bbox: list,
        image_size: str = "1024x1024",
        date_range: Optional[Tuple[DateTime, DateTime]] = None, # For satellite data: (start_date, end_date) 'YYYY-MM-DD'
        layers: list = [] # Specific layer for orthophotos
    ) -> dict:
        """
        Downloads images based on analysis type and polygon.
        Returns paths to downloaded images.
        """
        try:
            # min_lon, min_lat, max_lon, max_lat = self._get_bounding_box_from_polygon(polygon)
            # print(f"Calculated Bounding Box: {min_lon}, {min_lat}, {max_lon}, {max_lat}")
            # split_bbox = BBoxSplitter([polygon], CRS.WGS84, 2)
            # Create a unique directory for this request
            # (You might want a more robust naming/cleanup strategy)
            download_session_dir = os.path.join(self.base_download_dir, f"{analysis_type}")

            downloaded_files = []

            if analysis_type == "ortho":
                print("Initiating orthophoto download...")
                # for split in split_bbox.bbox_list:
                #     min_lon, min_lat, max_lon, max_lat = split
                downloader = ImageDownloader(
                    save_directory=download_session_dir,
                    min_lat=bbox[0],
                    min_lon=bbox[1],
                    max_lat=bbox[2],
                    max_lon=bbox[3],
                    image_size=image_size,
                    layers=layers
                    # length and width are optional, if not provided, it gets the whole bbox
                )
                downloaded_files.append(downloader.download_images())
                print(f"Orthophoto download complete. Files: {downloaded_files}")

            elif analysis_type == "satellite":
                ##TODO: Insert actual implementation here.
                print("Initiating satellite data download (NDVI bands)...")
                # --- Satellite Data Logic Placeholder ---
                # This is where you would integrate with a satellite imagery API
                # (e.g., Google Earth Engine, Sentinel Hub, Planet, or custom WCS/WFS).
                # This will be significantly different from the WMS orthophoto download.
                # You'd likely fetch specific bands (e.g., Red, NIR for NDVI) for the date range.

                if not date_range or len(date_range) != 2:
                    raise ValueError("date_range must be provided for satellite analysis (e.g., ['2023-01-01', '2023-01-31'])")

                # Dummy satellite image generation for demonstration
                # In a real scenario, you'd use a library like `earthengine-api` or `sentinelhub`
                # to fetch actual satellite data for the bbox and date range.
                print(f"Simulating satellite data download for {date_range} in {download_session_dir}")
                dummy_red_path = os.path.join(download_session_dir, "red_band.tif")
                dummy_nir_path = os.path.join(download_session_dir, "nir_band.tif")

                # Create dummy GeoTIFFs (replace with actual API calls)
                height, width = map(int, image_size.split('x'))
                profile = {
                    'driver': 'GTiff',
                    'height': height,
                    'width': width,
                    'count': 1,
                    'dtype': rasterio.uint8,
                    'crs': 'EPSG:28532',
                    'transform': rasterio.transform.from_bounds(bbox[0], bbox[1], bbox[2], bbox[3], width, height)
                }

                with rasterio.open(dummy_red_path, 'w', **profile) as dst:
                    dst.write(np.random.randint(0, 255, size=(height, width), dtype=np.uint8), 1)
                with rasterio.open(dummy_nir_path, 'w', **profile) as dst:
                    dst.write(np.random.randint(0, 255, size=(height, width), dtype=np.uint8), 1)

                downloaded_files.extend([dummy_red_path, dummy_nir_path])
                print(f"Satellite data simulation complete. Files: {downloaded_files}")

            else:
                raise ValueError(f"Unsupported analysis_type: {analysis_type}")

            return {"message": "Images downloaded successfully", "files": downloaded_files, "download_path": download_session_dir}

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            print(f"Error in ImageDownloadService: {e}")
            raise HTTPException(status_code=500, detail=f"Image download failed: {e}")
    