import zipfile
import os
import geopandas as gpd
def kmz_to_csv(kmz_path, output_csv):
    # Step 1: Extract KMZ
    extract_dir = "kmz_extracted"
    os.makedirs(extract_dir, exist_ok=True)
    with zipfile.ZipFile(kmz_path, 'r') as kmz:
        kmz.extractall(extract_dir)
    # Step 2: Find KML file
    kml_file = None
    for root, dirs, files in os.walk(extract_dir):
        for file in files:
            if file.endswith(".kml"):
                kml_file = os.path.join(root, file)
                break
    if not kml_file:
        raise FileNotFoundError("No KML file found inside KMZ.")
    print(f"KML found: {kml_file}")
    # Step 3: Read KML using geopandas
    gdf = gpd.read_file(kml_file, driver='KML')
    # Step 4: Convert geometry to lat/lon (for points)
    if gdf.geometry.iloc[0].geom_type == 'Point':
        gdf["longitude"] = gdf.geometry.x
        gdf["latitude"] = gdf.geometry.y
    else:
        # For lines/polygons: store WKT
        gdf["geometry_wkt"] = gdf.geometry.to_wkt()
    # Step 5: Drop geometry column (optional)
    gdf = gdf.drop(columns="geometry")
    # Step 6: Export to CSV
    gdf.to_csv(output_csv, index=False)
    print(f"CSV exported to: {output_csv}")
# Example usage
kmz_to_csv("input.kmz", "output.csv")