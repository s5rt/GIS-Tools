import zipfile
import os
import geopandas as gpd
def dd_to_dms(decimal_deg, is_lat):
    """Convert decimal degrees to DMS string format."""
    direction = ""
    if is_lat:
        direction = "N" if decimal_deg >= 0 else "S"
    else:
        direction = "E" if decimal_deg >= 0 else "W"
    decimal_deg = abs(decimal_deg)
    degrees = int(decimal_deg)
    minutes_full = (decimal_deg - degrees) * 60
    minutes = int(minutes_full)
    seconds = (minutes_full - minutes) * 60
    return f"{degrees}°{minutes}'{seconds:.2f}\"{direction}"
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
    # Step 4: Convert geometry to lat/lon in DMS format (for points)
    if gdf.geometry.iloc[0].geom_type == 'Point':
        gdf["latitude"]  = gdf.geometry.y.apply(lambda y: dd_to_dms(y, is_lat=True))
        gdf["longitude"] = gdf.geometry.x.apply(lambda x: dd_to_dms(x, is_lat=False))
    else:
        # For lines/polygons: store WKT
        gdf["geometry_wkt"] = gdf.geometry.to_wkt()
    # Step 5: Drop geometry column
    gdf = gdf.drop(columns="geometry")
    # Step 6: Export to CSV
    gdf.to_csv(output_csv, index=False)
    print(f"CSV exported to: {output_csv}")
# Example usage
kmz_to_csv("input.kmz", "output.csv")