"""
Flag Position on Land Test

Flags points that intersect land polygons using spatial analysis.

Author: FVON-QCQA Team
Date: 2025-10-29
Issue: #11
"""

import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import pyproj
import os


def flag_position_on_land(df, lat_col='latitude', lon_col='longitude',
                          shapefile_path=None):
    """
    Flag data with positions on land using spatial intersection.

    Requires latitude and longitude from a profile to be located in an ocean.
    Uses World Bank countries shapefile (Natural Earth 10m resolution).

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing oceanographic observation data
    lat_col : str, optional
        Name of the latitude column (default: 'latitude')
    lon_col : str, optional
        Name of the longitude column (default: 'longitude')
    shapefile_path : str, optional
        Path to land shapefile. If None, looks for 'QC_land/WB_countries_Admin0_10m.shp'
        relative to this script

    Returns
    -------
    pd.DataFrame
        Input DataFrame with added 'flag_position_on_land' column

    Flag Values
    -----------
    1 : Pass - Position in ocean
    4 : Fail - Position on land

    Examples
    --------
    >>> import pandas as pd
    >>>
    >>> # Create sample data
    >>> df = pd.DataFrame({
    ...     'latitude': [45.0, 40.7128, -33.8688],  # Ocean, NYC, Sydney
    ...     'longitude': [-60.0, -74.0060, 151.2093],
    ...     'temperature': [15.2, 18.3, 20.1]
    ... })
    >>>
    >>> # Apply QC test
    >>> df = flag_position_on_land(df)
    >>> print(df[['latitude', 'longitude', 'flag_position_on_land']])
    #    latitude  longitude  flag_position_on_land
    # 0     45.0     -60.0                        1  (ocean)
    # 1   40.7128   -74.0060                      4  (land - NYC)
    # 2  -33.8688   151.2093                      4  (land - Sydney)

    Notes
    -----
    - Uses Natural Earth 10m resolution land polygons
    - Optional coastline buffer could be added to reduce nearshore false positives
    - Currently no buffer implemented (0 km)
    - Global applicability: Yes

    Dependencies
    ------------
    - geopandas
    - shapely
    - pyproj

    Required Data Files
    -------------------
    - QC_land/WB_countries_Admin0_10m.shp (and associated .shx, .dbf files)
    - Download from: https://www.naturalearthdata.com/

    References
    ----------
    - IOOS QARTOD Manual for Real-Time Quality Control
    - FVON-QCQA README.md
    """
    # Initialize flag column
    df['flag_position_on_land'] = 1
    if 'flag' not in df.columns:
        df['flag'] = 1

    # Determine shapefile path
    if shapefile_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        shapefile_path = os.path.join(script_dir, '..', 'QC_land',
                                     'WB_countries_Admin0_10m.shp')

    # Check if shapefile exists
    if not os.path.exists(shapefile_path):
        print(f"Warning: Shapefile not found at {shapefile_path}")
        print("Skipping position on land test.")
        return df

    # Create GeoDataFrame from points
    points = gpd.GeoDataFrame(
        df,
        geometry=[Point(xy) for xy in zip(df[lon_col], df[lat_col])],
        crs="EPSG:4326"
    )

    # Load land shapefile
    land = gpd.read_file(shapefile_path)
    land.crs = pyproj.CRS("EPSG:4326")

    # Spatial join to find points on land
    results = points.sjoin(land, how="left", predicate="intersects")
    on_land = ~results['index_right'].isna()

    # Update flags
    df['flag_position_on_land'] = np.where(on_land, 4, 1)
    df.loc[df['flag_position_on_land'] == 4, 'flag'] = 4

    return df


if __name__ == "__main__":
    # Example usage
    import pandas as pd

    # Create test data with known land/ocean positions
    df = pd.DataFrame({
        'latitude': [
            45.0,      # North Atlantic (ocean)
            40.7128,   # New York City (land)
            -33.8688,  # Sydney (land)
            35.6762,   # Tokyo (land)
            -15.0,     # South Atlantic (ocean)
        ],
        'longitude': [
            -60.0,     # North Atlantic
            -74.0060,  # New York City
            151.2093,  # Sydney
            139.6503,  # Tokyo
            -25.0,     # South Atlantic
        ],
        'temperature': [15.2, 18.3, 20.1, 19.5, 24.8],
        'pressure': [10.0, 5.0, 8.0, 3.0, 12.0]
    })

    print("Original Data:")
    print(df[['latitude', 'longitude', 'temperature']])
    print("\nApplying position on land test...")

    try:
        df = flag_position_on_land(df)

        print("\nResults:")
        print(df[['latitude', 'longitude', 'flag_position_on_land']])

        print(f"\nIn Ocean: {len(df[df['flag_position_on_land'] == 1])}")
        print(f"On Land: {len(df[df['flag_position_on_land'] == 4])}")

        # Show which records are on land
        on_land = df[df['flag_position_on_land'] == 4]
        if len(on_land) > 0:
            print("\nPositions flagged as on land:")
            for idx, row in on_land.iterrows():
                print(f"  Row {idx}: ({row['latitude']:.4f}, {row['longitude']:.4f})")
    except Exception as e:
        print(f"Error: {e}")
        print("Note: This test requires the WB_countries shapefile.")
