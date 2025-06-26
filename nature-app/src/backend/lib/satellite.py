import os
import numpy as np
import matplotlib.pyplot as plt
import rasterio as rio
from shapely.geometry import Polygon, mapping
import earthpy as et
import earthpy.plot as ep

from matplotlib.colors import ListedColormap
import matplotlib.colors as colors



def compute_ndvi(b4_path, b8_path, output_path):
    # function to compute ndvi and save it in the output path
    #open raster bands B8 and B4
    b4_data = rio.open(b4_path)
    b8_data = rio.open(b8_path)
    b4 = rio.open(b4_path).read(1)
    b8 = rio.open(b8_path).read(1)
    red = b4.astype('float64')
    nir = b8.astype('float64')
    # calculating NDVI values
    ndvi = np.where((nir+red)==0.,0,(nir-red)/(nir+red))
    
    # writing ndvi with the original data format
    ndvi_tiff_file = rio.open(output_path, 'w', 
                              driver='Gtiff',
                              width = b4_data.width,
                              height = b4_data.height,
                              count = 1,
                              crs = b4_data.crs,
                              transform= b4_data.transform,
                              dtype='float64')
    ndvi_tiff_file.write(ndvi, 1)
    ndvi_tiff_file.close()