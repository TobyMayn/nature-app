import math
from collections import OrderedDict
from typing import Optional

import Levir_CD as Data  # Assuming Data.normalize_image
import matplotlib.pyplot as plt
import numpy as np
import torch

# Assuming these are available (or you provide dummy implementations for illustration)
from models.SAM_CD import SAM_CD as Net
from pyproj import Transformer
from rasterio.transform import Affine, from_bounds
from shapely import to_geojson
from shapely.geometry import Polygon
from skimage import io as ski_io
from skimage import measure
from torch.nn import functional as F
from torchvision.transforms import functional as transF


class OrthoAnalysis:
    def __init__(self, model_checkpoint_path: str, device: str = 'cuda', default_crop_size: tuple = (1024, 1024), default_tta: bool = True):
        """
        Initializes the Change Detection Service.
        Loads the model once.
        """
        self.device = torch.device(device, int(0))
        self.net = self._load_model(model_checkpoint_path)
        self.default_crop_size = default_crop_size
        self.default_tta = default_tta
        print(f"ChangeDetectionService initialized. Model loaded on {self.device}.")

    def _load_model(self, chkpt_path: str):
        """Loads the PyTorch model from the checkpoint path."""
        net = Net()
        state_dict = torch.load(chkpt_path, map_location="cpu", weights_only=False)
        new_state_dict = OrderedDict()
        for k, v in state_dict.items():
            if 'module.' in k: # Handle DataParallel saved models
                new_state_dict[k[7:]] = v
            else:
                new_state_dict = state_dict
        net.load_state_dict(new_state_dict, strict=False)
        net.to(self.device).eval() # Set to evaluation mode
        return net

    def _create_crops(self, img_np: np.ndarray, crop_size: tuple):
        """
        Creates overlapping crops from a large image.
        Returns a list of numpy arrays for crops.
        """
        img_crops = []
        h, w = img_np.shape[0], img_np.shape[1]
        c_h, c_w = crop_size

        if h < c_h or w < c_w:
            # Handle cases where image is smaller than crop_size (e.g., pad or resize)
            # For simplicity, returning original image as a single "crop" here, but real-world needs padding.
            print(f"Warning: Image ({h},{w}) smaller than crop_size {crop_size}. Returning as single crop.")
            return [img_np] # Or raise an error, or pad and then return
            
        rows = math.ceil(h / c_h)
        cols = math.ceil(w / c_w)
        
        # Calculate stride for overlapping crops
        stride_h = int((c_h * rows - h) / (rows - 1)) if rows > 1 else 0
        stride_w = int((c_w * cols - w) / (cols - 1)) if cols > 1 else 0

        for j in range(rows):
            for i in range(cols):
                s_h = int(j * c_h - j * stride_h)
                if j == (rows - 1) and s_h + c_h > h: s_h = h - c_h # Ensure last crop fits
                s_h = max(0, s_h) # Ensure start_h is not negative

                e_h = s_h + c_h

                s_w = int(i * c_w - i * stride_w)
                if i == (cols - 1) and s_w + c_w > w: s_w = w - c_w # Ensure last crop fits
                s_w = max(0, s_w) # Ensure start_w is not negative

                e_w = s_w + c_w
                
                img_crops.append(img_np[s_h:e_h, s_w:e_w, :])
        # print(f'Sliding crop finished. {len(img_crops)} images created.')
        return img_crops

    def _stitch_pred(self, patch_list: list, original_size: tuple) -> np.ndarray:
        """
        Stitches predicted patches back into a full-sized prediction map.
        Assumes patches are binary (0 or 1).
        """
        H, W = original_size
        if not patch_list:
            return np.zeros(original_size, dtype=np.uint8) # Return empty mask if no patches

        h_patch, w_patch = patch_list[0].shape
        
        # Calculate stitch rows/cols and overlap based on original image size and patch size
        stitch_rows = math.ceil(H / h_patch)
        stitch_cols = math.ceil(W / w_patch)
        
        # Recalculate stride based on actual stitch dimensions for precise overlap
        h_overlap = 0 if stitch_rows <= 1 else int((h_patch * stitch_rows - H) / (stitch_rows - 1))
        w_overlap = 0 if stitch_cols <= 1 else int((w_patch * stitch_cols - W) / (stitch_cols - 1))
        
        # Initialize an empty array for the stitched image (float to handle averages if needed)
        stitched_img = np.zeros(original_size, dtype=np.float32)
        overlap_counts = np.zeros(original_size, dtype=np.float32) # To handle averaging overlaps

        # Iterate through patches and place them, handling overlaps
        for r in range(stitch_rows):
            for c in range(stitch_cols):
                idx = r * stitch_cols + c
                if idx >= len(patch_list): # Safety check
                    continue

                patch = patch_list[idx]
                
                # Calculate start and end coordinates for placing the patch in the stitched image
                s_h = r * (h_patch - h_overlap)
                s_w = c * (w_patch - w_overlap)
                e_h = s_h + h_patch
                e_w = s_w + w_patch

                # Adjust for boundary conditions if the last row/col exceeds original size
                if e_h > H: s_h = H - h_patch
                if e_w > W: s_w = W - w_patch
                
                # Add patch data and increment overlap counts
                stitched_img[s_h:e_h, s_w:e_w] += patch
                overlap_counts[s_h:e_h, s_w:e_w] += 1

        # Average overlapping regions to finalize the stitched image
        # Avoid division by zero where overlap_counts is 0
        overlap_counts[overlap_counts == 0] = 1 # Set 0s to 1 to prevent /0 errors, their values will be 0 anyway
        stitched_img = (stitched_img / overlap_counts)
        
        # Convert to binary mask using a threshold (e.g., > 0.5 for averaged probabilities)
        # Assuming original patches were boolean, averaging multiple True's will give > 0.5
        stitched_img = (stitched_img > 0.5).astype(np.uint8) * 255 # Convert to 0 or 255
        
        # print(f'Pred Stitched ({stitched_img.shape[0]}, {stitched_img.shape[1]})')
        return stitched_img


    def predict_change(self, imgA_bytes: bytes, imgB_bytes: bytes, crop_size: tuple = None, use_tta: bool = None, 
                      return_polygons: bool = False, transform: Optional[Affine] = None, 
                      target_crs: str = "EPSG:25832") -> tuple:
        """
        Performs change detection prediction on two input images (as bytes).

        Args:
            imgA_bytes: Bytes data of the first image (e.g., from a web request).
            imgB_bytes: Bytes data of the second image.
            crop_size: Tuple (height, width) for model input cropping. Uses default if None.
            use_tta: Boolean for Test Time Augmentation. Uses default if None.
            return_polygons: Boolean to also return shapely polygons. Uses default if None.
            transform: Rasterio Affine transform to convert pixel coordinates to geographic coordinates.
            target_crs: Target coordinate reference system for polygons (default: EPSG:25832).

        Returns:
            If return_polygons is False: A numpy array representing the binary change mask (0 or 255).
            If return_polygons is True: A tuple (mask, polygons) where polygons is a list of shapely Polygon objects in the target CRS.
        """
        crop_size = crop_size if crop_size is not None else self.default_crop_size
        use_tta = use_tta if use_tta is not None else self.default_tta

        # --- Load images from bytes ---
        # Using PIL to load from bytes, then convert to numpy
        # imgA_pil = Image.open(BytesIO(imgA_bytes)).convert("RGB") # Ensure RGB
        # imgB_pil = Image.open(BytesIO(imgB_bytes)).convert("RGB")
        
        # imgA_np = np.array(imgA_pil)
        # imgB_np = np.array(imgB_pil)

        # Normalize images (assuming Data.normalize_image is robust to different ranges)
        # Original code uses `skimage.io.imread` which reads uint8/uint16, then converts.
        # Ensure `Data.normalize_image` handles numpy arrays correctly.
        imgA = Data.normalize_image(imgA_bytes)
        imgB = Data.normalize_image(imgB_bytes)
        
        original_h, original_w = imgA.shape[:2]

        with torch.no_grad():
            if imgA.shape[0]>crop_size[0] or imgA.shape[1]>crop_size[1]:
                # --- Process with Cropping and Stitching ---
                imgA_crops = self._create_crops(imgA, crop_size)
                imgB_crops = self._create_crops(imgB, crop_size) # Assuming same cropping for B

                if not imgA_crops or not imgB_crops:
                    raise ValueError("Image cropping failed or resulted in empty crops.")

                preds = []
                for idx in range(len(imgA_crops)): # Assume A and B have same num crops
                    cropA_np = imgA_crops[idx]
                    cropB_np = imgB_crops[idx]

                    # Convert numpy arrays to PyTorch tensors
                    tensorA = transF.to_tensor(cropA_np).unsqueeze(0).to(self.device).float()
                    tensorB = transF.to_tensor(cropB_np).unsqueeze(0).to(self.device).float()
                    output = self._run_inference_with_tta(self.net, tensorA, tensorB, use_tta)
                    
                    pred = output.cpu().detach().numpy().squeeze() > 0.5
                    preds.append(pred)
                
                final_pred_mask = self._stitch_pred(preds, (original_h, original_w))

            else:
                # --- Process Full Image (No Cropping) ---
                tensorA = transF.to_tensor(imgA).unsqueeze(0).to(self.device).float()
                tensorB = transF.to_tensor(imgB).unsqueeze(0).to(self.device).float()
                
                output = self._run_inference_with_tta(self.net, tensorA, tensorB, use_tta)
                
                # Convert to binary mask (0 or 255)
                final_pred_mask = ((output.cpu().detach().numpy().squeeze() > 0.5) * 255).astype(np.uint8)
        
        if return_polygons:
            polygons = self._mask_to_polygons(final_pred_mask, transform=transform, target_crs=target_crs)
            return final_pred_mask, polygons
        else:
            return final_pred_mask

    def _run_inference_with_tta(self, net, tensorA, tensorB, use_tta: bool) -> torch.Tensor:
        """
        Helper to run inference potentially with Test Time Augmentation.
        Returns raw output tensor (before final thresholding).
        """
        output, _, _ = net(tensorA, tensorB)
        output = F.sigmoid(output) # Initial sigmoid
        
        if use_tta:
            # Vertical flip
            output_v, _, _ = net(torch.flip(tensorA, [2]), torch.flip(tensorB, [2]))
            output += F.sigmoid(torch.flip(output_v, [2]))
            
            # Horizontal flip
            output_h, _, _ = net(torch.flip(tensorA, [3]), torch.flip(tensorB, [3]))
            output += F.sigmoid(torch.flip(output_h, [3]))
            
            # Both flips
            output_hv, _, _ = net(torch.flip(tensorA, [2,3]), torch.flip(tensorB, [2,3]))
            output += F.sigmoid(torch.flip(output_hv, [2,3]))
            
            output = output / 4.0 # Average the augmented results

        return output

    def _mask_to_polygons(self, mask: np.ndarray, min_area: int = 10, 
                         transform: Optional[Affine] = None, target_crs: str = "EPSG:25832") -> list:
        """
        Converts a binary mask to a list of shapely polygons in the specified CRS.
        
        Args:
            mask: Binary mask array (0s and 1s or 0s and 255s)
            min_area: Minimum area threshold for polygons (pixels if no transform, square meters if transformed)
            transform: Rasterio Affine transform to convert pixel coordinates to geographic coordinates
            target_crs: Target coordinate reference system (default: EPSG:25832)
            
        Returns:
            List of shapely Polygon objects in the target CRS
        """
        # Ensure mask is binary (0 and 1)
        binary_mask = (mask > 0).astype(np.uint8)
        
        # Find contours using skimage
        contours = measure.find_contours(binary_mask, 0.5)
        
        polygons = []
        for contour in contours:
            # Convert contour to polygon coordinates (swap x,y to match shapely convention)
            coords = [(point[1], point[0]) for point in contour]
            
            # Create polygon if it has enough points
            if len(coords) >= 3:
                try:
                    # Transform coordinates if transform is provided
                    if transform is not None:
                        # Convert pixel coordinates to geographic coordinates
                        transformed_coords = []
                        for x, y in coords:
                            geo_x, geo_y = transform * (x, y)
                            transformed_coords.append((geo_x, geo_y))
                        coords = transformed_coords
                    
                    polygon = Polygon(coords)
                    # Filter by minimum area
                    if polygon.area >= min_area and polygon.is_valid:
                        polygons.append(polygon)
                except Exception:
                    # Skip invalid polygons
                    continue
                    
        return polygons

# # --- How to use this service in your web app (Example) ---
# # This part would typically be in your FastAPI/Flask/Django view or controller

# # Assume configuration comes from environment variables or a settings file
# # These paths need to be valid on your deployment environment
MODEL_CHECKPOINT_PATH = '/home/tobymayn/school/project/nature-app/nature-app/src/backend/algorithms/SAM_CD_e9_OA98.98_F43.53_IoU32.88.pth'
DEFAULT_DEVICE = 'cuda' # or 'cpu' if no GPU available

# Initialize the service once, e.g., at app startup
change_detector = OrthoAnalysis(
    model_checkpoint_path=MODEL_CHECKPOINT_PATH,
    device=DEFAULT_DEVICE,
    default_crop_size=(1024, 1024),
    default_tta=True
)

# Example of how an API endpoint might call it:
# async def run_orthophoto_analysis(img_a_file: UploadFile, img_b_file: UploadFile, location_id: int):
#     # 1. Read image bytes from the uploaded files
img_a_bytes = ski_io.imread("/home/tobymayn/school/project/nature-app/nature-app/src/backend/data/ortho/orto2016.png")
img_b_bytes = ski_io.imread("/home/tobymayn/school/project/nature-app/nature-app/src/backend/data/ortho/orto2020.png")

#     # 2. Call the service
#     try:
# Example geospatial transform using actual coordinates
# Original WGS84 bounds: 55.685965784846324,12.266039998192857 55.69057378945433,12.274214155779534
# Converted to EPSG:25832 (UTM Zone 32N)

# Transform from WGS84 to EPSG:25832
transformer = Transformer.from_crs("EPSG:4326", "EPSG:25832", always_xy=True)
lon1, lat1 = 12.266039998192857, 55.685965784846324  # SW corner
lon2, lat2 = 12.274214155779534, 55.69057378945433   # NE corner

west, south = transformer.transform(lon1, lat1)
east, north = transformer.transform(lon2, lat2)

# Assuming your actual image dimensions (adjust as needed)
height, width = img_a_bytes.shape[:2]  # Get actual image dimensions
geo_transform = from_bounds(west, south, east, north, width, height)

change_mask_np, polygons = change_detector.predict_change(
    imgA_bytes=img_a_bytes,
    imgB_bytes=img_b_bytes,
    crop_size=(512, 512),     # Optional: override default for this request
    use_tta=False,            # Optional: override default
    return_polygons=True,     # Get both mask and polygons
    transform=geo_transform,  # Geospatial transform
    target_crs="EPSG:25832"   # Target coordinate system
)
print(f"Change mask shape: {change_mask_np.shape}")
print(f"Number of change polygons: {len(polygons)}")
for i, polygon in enumerate(polygons):
    print(f"Polygon {i}: area = {polygon.area:.2f} square meters")
    print(f"Polygon {i} bounds: {polygon.exterior.xy}")  # Now in EPSG:25832 coordinates
    print(to_geojson(polygon))
    plt.plot(polygon.exterior.xy)
    plt.show()
# #         # 3. Process the numpy mask (e.g., convert to GeoJSON polygons, store in DB)
# #         # This would involve converting the numpy mask to a geospatial vector format
# #         # (e.g., using `rasterio`, `shapely`, `fiona`) and associating it with a geographic context.
# #         # Example: Store 'change_mask_np' as a temporary TIFF, then vectorize.
        
# #         # For Untouched Areas, you'd convert the binary change_mask_np into polygons
# #         # and persist them in your `identified_areas` table, linking to the `location_id`.
# #         # You'd also need to retrieve the original geo-referencing info (transform, CRS)
# #         # for imgA_bytes / imgB_bytes to correctly geo-reference the output mask.
        
# #         # 4. Return results (e.g., GeoJSON, status message)
# #         return {"status": "success", "message": "Analysis complete", "change_mask_shape": change_mask_np.shape}
        
# #     except Exception as e:
# #         # Handle errors and return appropriate API response
# #         return {"status": "error", "message": str(e)}, 500

Polygon([(500503, 6000400.5), (500502.5, 6000401), (500502.5, 6000402), (500502.5, 6000403), (500502.5, 6000404), (500502.5, 6000405), (500502.5, 6000406), (500502.5, 6000407), (500502, 6000407.5), (500501.5, 6000408), (500501.5, 6000409), (500501.5, 6000410), (500501.5, 6000411), (500501.5, 6000412), (500502, 6000412.5), (500502.5, 6000413), (500502.5, 6000414), (500502.5, 6000415), (500503, 6000415.5), (500504, 6000415.5), (500504.5, 6000416), (500505, 6000416.5), (500506, 6000416.5), (500507, 6000416.5), (500508, 6000416.5), (500509, 6000416.5), (500510, 6000416.5), (500510.5, 6000417), (500511, 6000417.5), (500511.5, 6000417), (500511.5, 6000416), (500511.5, 6000415), (500511.5, 6000414), (500511.5, 6000413), (500511.5, 6000412), (500511.5, 6000411), (500511.5, 6000410), (500511.5, 60004090), (500511.5, 6000408), (500511.5, 6000407), (500511.5, 6000406), (500511.5, 6000405), (500511.5, 6000404), (500511.5, 6000403), (500511, 6000402.5), (500510, 6000402.5), (500509.5, 6000403), (500509, 6000403.5), (500508.5, 6000404), (500508, 6000404.5), (500507.5, 6000405), (500507, 6000405.5), (500506.5, 6000405), (500506, 6000404.5), (500505.5, 6000404), (500505, 6000403.5), (500504.5, 6000403), (500504.5, 6000402), (500504, 6000401.5), (500503.5, 6000401), (500503, 6000400.5)])