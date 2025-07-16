import math
import os
from io import BytesIO
from typing import List, Literal, Optional, Tuple

import numpy as np
import rasterio  # For satellite data handling (if needed)
from fastapi import HTTPException
from owslib.wms import WebMapService
from PIL import Image

# Import shapely for geometry processing
from shapely.geometry import Polygon
from sqlmodel import DateTime

# Re-incorporate the ImageDownloader from Crop_images_SG.py
# It's better to put it directly into this file or a utils file
# if it's tightly coupled to this service. For now, let's include it.

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
        self.url = 'https://services.hxgncontent.com/streaming/wms?username=DMP_DAI&password=2B276B54'
        self.wms = WebMapService(self.url)

    def _download_tile(self, bbox: Tuple[float, float, float, float], file_path: str):
        """Helper to download a single tile."""
        response = self.wms.getmap(
            layers=self.layers,
            styles=[],
            srs='EPSG:28532', # WGS84 for lat/lon
            bbox=bbox,
            size=(self.image_size_x, self.image_size_y),
            format='image/png',
            transparent=True
        )
        img = Image.open(BytesIO(response.read()))
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        out = open(file_path, 'wb')
        out.write(img.read())
        out.close()
        print(f"Downloaded tile to: {file_path}")

    def download_images(self) -> List[str]:
        """
        Downloads images within the bounding box, potentially tiling if length/width are provided.
        Returns a list of paths to the downloaded images.
        """
        downloaded_paths = []
        for layer in self.layers:
            image_num = 0
                
            delta_lat = self.length / 111111  # ~111.1 km per degree lat
            delta_lon = self.width / (111111 * math.cos(math.radians(self.min_lat)))

            cur_lat = self.min_lat
            cur_lon = self.min_lon

            while cur_lat < self.max_lat:
                while cur_lon < self.max_lon:
                    max_lat = cur_lat + delta_lat
                    max_lon = cur_lon + delta_lon
            
                    file_name = f"{layer}_{cur_lat}_{cur_lon}_{max_lat}_{max_lon}_{image_num}.png"
                    file_path = os.path.join(self.save_directory, file_name)
                    self._download_tile((cur_lon, cur_lon, max_lon, max_lat), file_path)
                    downloaded_paths.append(file_path)
            image_num += 1

        return downloaded_paths

class ImageDownloadService:
    def __init__(self):
        self.base_download_dir = "src/backend/data" # Base directory for all downloads

    def _get_bounding_box_from_polygon(self, polygon: Polygon) -> Tuple[float, float, float, float]:
        """
        Extracts the bounding box (min_lon, min_lat, max_lon, max_lat)
        from a GeoJSON Polygon dictionary.
        """
        try:
            min_lon, min_lat, max_lon, max_lat = polygon.bounds
            return min_lon, min_lat, max_lon, max_lat
        except Exception as e:
            raise ValueError(f"Invalid  Polygon or error processing: {e}")

    async def download_images_for_analysis(
        self,
        analysis_type: Literal["ortho", "satellite"],
        polygon: Polygon,
        image_size: str = "1024x1024",
        date_range: Optional[Tuple[DateTime, DateTime]] = None, # For satellite data: (start_date, end_date) 'YYYY-MM-DD'
        layers: list = [] # Specific layer for orthophotos
    ) -> dict:
        """
        Downloads images based on analysis type and polygon.
        Returns paths to downloaded images.
        """
        try:
            min_lon, min_lat, max_lon, max_lat = self._get_bounding_box_from_polygon(polygon)
            print(f"Calculated Bounding Box: {min_lon}, {min_lat}, {max_lon}, {max_lat}")

            # Create a unique directory for this request
            # (You might want a more robust naming/cleanup strategy)
            download_session_dir = os.path.join(self.base_download_dir, f"{analysis_type}")

            downloaded_files = []

            if analysis_type == "ortho":
                print("Initiating orthophoto download...")
                downloader = ImageDownloader(
                    save_directory=download_session_dir,
                    min_lat=min_lat,
                    min_lon=min_lon,
                    max_lat=max_lat,
                    max_lon=max_lon,
                    image_size=image_size,
                    layer=layers
                    # length and width are optional, if not provided, it gets the whole bbox
                )
                downloaded_files = downloader.download_images()
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
                    'transform': rasterio.transform.from_bounds(min_lon, min_lat, max_lon, max_lat, width, height)
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
    