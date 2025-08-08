import glob
import math
import os
from collections import OrderedDict
from typing import Optional

import numpy as np
import pyproj
import torch
from rasterio.transform import Affine
from shapely.geometry import Polygon
from shapely.ops import transform
from skimage import measure
from torch.nn import functional as F
from torchvision.transforms import functional as transF

from . import Levir_CD as Data  # Assuming Data.normalize_image

# Assuming these are available (or you provide dummy implementations for illustration)
from .models.SAM_CD import SAM_CD as Net


def find_sam_cd_checkpoint() -> str:
    """
    Automatically finds the SAM_CD checkpoint file in the algorithms folder.
    
    Returns:
        str: Path to the SAM_CD checkpoint file
        
    Raises:
        FileNotFoundError: If no SAM_CD checkpoint file is found
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Look for SAM_CD checkpoint files (common patterns)
    patterns = [
        "SAM_CD*.pth",
        "SAM_CD*.pt", 
        "*SAM_CD*.pth",
        "*SAM_CD*.pt"
    ]
    
    for pattern in patterns:
        checkpoint_files = glob.glob(os.path.join(current_dir, pattern))
        if checkpoint_files:
            # Return the first match, or you could add logic to pick the best one
            return checkpoint_files[0]
    
    raise FileNotFoundError(
        f"No SAM_CD checkpoint file found in {current_dir}. "
        f"Expected files matching patterns: {patterns}"
    )


class OrthoAnalysis:
    def __init__(self, model_checkpoint_path: Optional[str] = None, device: str = 'cuda', default_crop_size: tuple = (1024, 1024), default_tta: bool = True):
        """
        Initializes the Change Detection Service.
        Loads the model once.
        
        Args:
            model_checkpoint_path: Path to the model checkpoint. If None, automatically finds SAM_CD checkpoint.
            device: Device to run the model on ('cuda' or 'cpu')
            default_crop_size: Default crop size for processing large images
            default_tta: Whether to use test time augmentation by default
        """
        self.device = torch.device(device, int(0))
        
        # Auto-find checkpoint if not provided
        if model_checkpoint_path is None:
            model_checkpoint_path = find_sam_cd_checkpoint()
            print(f"Auto-found checkpoint: {model_checkpoint_path}")
        
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
                      return_polygons: bool = False, bbox: list = None) -> tuple:
        """
        Performs change detection prediction on two input images (as bytes).

        Args:
            imgA_bytes: Bytes data of the first image (e.g., from a web request).
            imgB_bytes: Bytes data of the second image.
            crop_size: Tuple (height, width) for model input cropping. Uses default if None.
            use_tta: Boolean for Test Time Augmentation. Uses default if None.
            return_polygons: Boolean to also return shapely polygons. Uses default if None.
            bbox: Bounding box as [min_lat, min_lon, max_lat, max_lon] in EPSG:25832. Required if return_polygons is True.

        Returns:
            If return_polygons is False: A numpy array representing the binary change mask (0 or 255).
            If return_polygons is True: A tuple (mask, polygons) where polygons is a list of shapely Polygon objects in EPSG:25832.
        """
        crop_size = crop_size if crop_size is not None else self.default_crop_size
        use_tta = use_tta if use_tta is not None else self.default_tta

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
            if bbox is None:
                raise ValueError("bbox parameter is required when return_polygons=True")
            polygons = self._mask_to_polygons(final_pred_mask, bbox)
            return {"np_array": final_pred_mask, "polygons": polygons}
        else:
            return {"np_array": final_pred_mask, "polygons": []}

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

    def _mask_to_polygons(self, mask: np.ndarray, bbox: list, source_crs: str = "EPSG:25832", min_area: int = 10) -> list:
        """
        Converts a binary mask to a list of shapely polygons in EPSG:25832.
        
        Args:
            mask: Binary mask array (0s and 1s or 0s and 255s)
            bbox: Bounding box as [min_lat, min_lon, max_lat, max_lon] in EPSG:25832
            source_crs: Source coordinate reference system (default: EPSG:25832)
            min_area: Minimum area threshold for polygons in square meters
            
        Returns:
            List of shapely Polygon objects in EPSG:25832
        """
        # Ensure mask is binary (0 and 1)
        binary_mask = (mask > 0).astype(np.uint8)
        
        # Find contours using skimage
        contours = measure.find_contours(binary_mask, 0.5)
        
        # Get mask dimensions
        height, width = mask.shape
        
        # Create transform from pixel coordinates to geographic coordinates
        # bbox format: [min_lat, min_lon, max_lat, max_lon] but we need [min_x, min_y, max_x, max_y]
        min_x, min_y, max_x, max_y = bbox[1], bbox[0], bbox[3], bbox[2]  # lon=x, lat=y
        transform_matrix = Affine.from_gdal(min_x, (max_x - min_x) / width, 0, max_y, 0, (min_y - max_y) / height)
        
        # Set up coordinate transformation (only if source_crs is different from EPSG:25832)
        transformer = None
        if source_crs != "EPSG:25832":
            source_proj = pyproj.CRS(source_crs)
            target_proj = pyproj.CRS("EPSG:25832")
            transformer = pyproj.Transformer.from_crs(source_proj, target_proj, always_xy=True)
        
        polygons = []
        for contour in contours:
            # Convert contour to polygon coordinates (swap x,y to match shapely convention)
            coords = [(point[1], point[0]) for point in contour]
            
            # Create polygon if it has enough points
            if len(coords) >= 3:
                try:
                    # Transform pixel coordinates to geographic coordinates using the affine transform
                    geo_coords = []
                    for x, y in coords:
                        geo_x, geo_y = transform_matrix * (x, y)
                        geo_coords.append((geo_x, geo_y))
                    
                    # Create polygon in source CRS
                    polygon = Polygon(geo_coords)
                    
                    # Transform to EPSG:25832 if needed
                    if transformer is not None:
                        polygon = transform(transformer.transform, polygon)
                    
                    # Filter by minimum area and validity
                    if polygon.area >= min_area and polygon.is_valid:
                        polygons.append(polygon)
                except Exception:
                    # Skip invalid polygons
                    continue
                    
        return polygons