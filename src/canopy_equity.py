import os
import sys

# Ensure PROJ and GDAL know where their database files live inside conda
conda_env_path = os.path.dirname(os.path.dirname(sys.executable))
os.environ["PROJ_LIB"] = os.path.join(conda_env_path, "share", "proj")
os.environ["GDAL_DATA"] = os.path.join(conda_env_path, "share", "gdal")

import geopandas as gpd

def analyze_canopy_equity():
    extracted_vector = "outputs/vectors/extracted_roofs.gpkg"
    output_equity_geojson = "outputs/vectors/canopy_equity_assessment.geojson"
    
    print("Loading extracted vector layers...")
    gdf = gpd.read_file(extracted_vector)
    
    # Project to metric CRS for Austin, TX (UTM Zone 14N)
    gdf = gdf.to_crs(epsg=32614)
    gdf["area_m2"] = gdf.geometry.area
    gdf["perimeter_m"] = gdf.geometry.length
    gdf["compactness"] = (4 * 3.14159 * gdf["area_m2"]) / (gdf["perimeter_m"] ** 2)
    
    # Separate canopy features (lower compactness or small irregular polygons) from roofs
    canopy = gdf[(gdf["area_m2"] < 50) | (gdf["compactness"] < 0.35)].copy()
    roofs = gdf[(gdf["area_m2"] >= 50) & (gdf["compactness"] >= 0.35)].copy()
    
    print(f"Identified {len(roofs)} structures and {len(canopy)} canopy/vegetation clusters.")
    
    # Total tile bounding area
    total_area_m2 = gdf.unary_union.convex_hull.area
    total_canopy_m2 = canopy["area_m2"].sum()
    total_roof_m2 = roofs["area_m2"].sum()
    
    canopy_coverage_pct = round((total_canopy_m2 / total_area_m2) * 100, 2)
    
    # Measure distance from each roof to the nearest green canopy cluster (Heat Exposure Index)
    roofs["dist_to_canopy_m"] = roofs.geometry.apply(
        lambda g: canopy.distance(g).min() if not canopy.empty else 0
    ).round(2)
    
    # Classify Heat Vulnerability Score (Higher distance = higher heat exposure)
    roofs["heat_vulnerability_score"] = (
        (roofs["dist_to_canopy_m"] / roofs["dist_to_canopy_m"].max()) * 100
    ).round(1)
    
    # Export assessment layer
    roofs = roofs.to_crs(epsg=4326)
    roofs.to_file(output_equity_geojson, driver="GeoJSON")
    
    print("\nCanopy & Heat Vulnerability Summary:")
    print(f" - Total Study Area: {total_area_m2:.1f} m²")
    print(f" - Total Tree Canopy: {total_canopy_m2:.1f} m² ({canopy_coverage_pct}% coverage)")
    print(f" - Exported Equity Metrics to: {output_equity_geojson}")
    print("\nSample Output Metrics:")
    print(roofs[["area_m2", "dist_to_canopy_m", "heat_vulnerability_score"]].head())

if __name__ == "__main__":
    analyze_canopy_equity()

    