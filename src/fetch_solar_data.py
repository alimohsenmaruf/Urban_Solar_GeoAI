import os
import sys

# Ensure GDAL/PROJ environment paths are set
conda_env_path = os.path.dirname(os.path.dirname(sys.executable))
os.environ["PROJ_LIB"] = os.path.join(conda_env_path, "share", "proj")
os.environ["GDAL_DATA"] = os.path.join(conda_env_path, "share", "gdal")

import leafmap

def fetch_solar_tiles():
    os.makedirs("data/raw", exist_ok=True)
    output_tif = "data/raw/urban_solar_sample.tif"
    
    # Bounding box covering an urban residential/commercial district
    # [min_lon, min_lat, max_lon, max_lat] (Austin, TX area)
    bbox = [-97.7450, 30.2620, -97.7380, 30.2680]
    
    print("Downloading urban aerial imagery tile for solar potential modeling...")
    leafmap.map_tiles_to_geotiff(
        output=output_tif,
        bbox=bbox,
        zoom=18,
        source="Satellite",
        overwrite=True
    )
    print(f"Urban imagery saved to {output_tif}")

if __name__ == "__main__":
    fetch_solar_tiles()