import os
import torch
import geopandas as gpd
from samgeo.text_sam import LangSAM

def run_prompted_solar_segmentation():
    input_tif = "data/raw/urban_solar_sample.tif"
    output_vector = "outputs/vectors/solar_rooftop_potential.geojson"
    
    print("Initializing LangSAM (Grounding DINO + SAM)...")
    # LangSAM uses text prompts to detect ONLY target classes
    sam = LangSAM(model_type="vit_b")
    
    print("Detecting roof structures using text prompt: 'building roof'...")
    sam.predict(
        image_path=input_tif,
        text_prompt="building roof",
        box_threshold=0.24,
        text_threshold=0.24,
        output="outputs/vectors/raw_roofs.gpkg"
    )
    
    # Process extracted vectors
    gdf = gpd.read_file("outputs/vectors/raw_roofs.gpkg")
    gdf = gdf.to_crs(epsg=32614)  # Austin UTM 14N
    
    gdf["area_m2"] = gdf.geometry.area
    roofs = gdf[gdf["area_m2"] >= 40].copy()
    roofs["roof_id"] = range(1, len(roofs) + 1)
    
    # Calculate solar potential metrics
    roofs["est_usable_solar_m2"] = (roofs["area_m2"] * 0.65).round(1)
    roofs["est_kwh_per_year"] = (roofs["est_usable_solar_m2"] * 5.5 * 365 * 0.18 * 0.75).round(1)
    
    roofs.to_crs(epsg=4326).to_file(output_vector, driver="GeoJSON")
    print(f"Cleaned solar layer saved: {len(roofs)} verified rooftops extracted.")

if __name__ == "__main__":
    run_prompted_solar_segmentation()