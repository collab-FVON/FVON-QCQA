"""
Flag Vessel Region Test

Validates that observed bounding box matches declared operating region.

Author: FVON-QCQA Team
Date: 2025-10-29
Issue: #13
"""

import pandas as pd


def flag_vessel_region(df, declared_region, lat_col='latitude', lon_col='longitude'):
    """
    Flag data when observed bounding box conflicts with declared operating region.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing oceanographic observation data
    declared_region : str
        Declared operating region. Options: 'Greenland', 'North Sea', 'Atlantic',
        'New Zealand', 'Red Sea', 'Mediterranean Sea', 'Alaska', 'Canada', 'Pacific',
        'Gulf of Mexico', 'All' (bypasses check)
    lat_col : str, optional
        Name of the latitude column (default: 'latitude')
    lon_col : str, optional
        Name of the longitude column (default: 'longitude')

    Returns
    -------
    pd.DataFrame
        Input DataFrame with added 'flag_vessel_region' column

    Flag Values
    -----------
    1 : Pass - Matches declared region or region='All'
    3 : Suspect - Outside declared region

    Regional Bounding Boxes
    -----------------------
    - Greenland: lon[-60,-15], lat[55,90]
    - North Sea: lon[-15,30], lat[45,60]
    - Atlantic: lon[-75,30], lat[0,90]
    - New Zealand: lon[160,180] or [0,5], lat[-50,-30]
    - Red Sea: lon[30,45], lat[10,45]
    - Mediterranean Sea: lon[-5,40], lat[25,45]
    - Alaska/Canada: lon[-180,-125], lat[45,90]
    - Pacific: lon[-180,-70], lat[0,60]
    - Gulf of Mexico: lon[-100,-70], lat[15,35]
    - All: Bypass check

    Examples
    --------
    >>> import pandas as pd
    >>>
    >>> df = pd.DataFrame({
    ...     'latitude': [45.0, 35.0, 60.0],
    ...     'longitude': [-50.0, -65.0, -20.0],  # Atlantic region
    ...     'temperature': [15.2, 18.3, 12.1]
    ... })
    >>>
    >>> # Check against Atlantic region
    >>> df = flag_vessel_region(df, declared_region='Atlantic')
    >>> print(df['flag_vessel_region'])  # All should pass (1)
    >>>
    >>> # Check against Mediterranean (wrong region)
    >>> df = flag_vessel_region(df, declared_region='Mediterranean Sea')
    >>> print(df['flag_vessel_region'])  # All should fail (3)

    Notes
    -----
    - Uses bounding box approach (may include overlapping regions)
    - 'All' region bypasses the check entirely
    - Region definitions from FVON-QCQA README

    References
    ----------
    - FVON-QCQA README.md
    """
    # Regional definitions [lon_min, lon_max, lat_min, lat_max]
    regions = {
        'Greenland': {'lon': [-60, -15], 'lat': [55, 90]},
        'North Sea': {'lon': [-15, 30], 'lat': [45, 60]},
        'Atlantic': {'lon': [-75, 30], 'lat': [0, 90]},
        'New Zealand': {'lon': [[160, 180], [0, 5]], 'lat': [-50, -30]},  # Two lon ranges
        'Red Sea': {'lon': [30, 45], 'lat': [10, 45]},
        'Mediterranean Sea': {'lon': [-5, 40], 'lat': [25, 45]},
        'Alaska': {'lon': [-180, -125], 'lat': [45, 90]},
        'Canada': {'lon': [-180, -125], 'lat': [45, 90]},
        'Pacific': {'lon': [-180, -70], 'lat': [0, 60]},
        'Gulf of Mexico': {'lon': [-100, -70], 'lat': [15, 35]},
    }

    # Initialize flag
    df['flag_vessel_region'] = 1

    # Bypass check if region is 'All'
    if declared_region == 'All':
        return df

    # Calculate bounding box from data
    max_lat = df[lat_col].max()
    min_lat = df[lat_col].min()
    max_lon = df[lon_col].max()
    min_lon = df[lon_col].min()

    # Determine which regions the data falls within
    data_regions = ['Unknown']

    for region_name, bounds in regions.items():
        lat_min, lat_max = bounds['lat']

        # Handle special case of New Zealand (two longitude ranges)
        if region_name == 'New Zealand':
            in_region = False
            for lon_range in bounds['lon']:
                lon_min, lon_max = lon_range
                if (lon_min <= max_lon <= lon_max and lon_min <= min_lon <= lon_max and
                    lat_min <= max_lat <= lat_max and lat_min <= min_lat <= lat_max):
                    in_region = True
                    break
            if in_region:
                data_regions.append(region_name)
        else:
            lon_min, lon_max = bounds['lon']
            if (lon_min <= max_lon <= lon_max and lon_min <= min_lon <= lon_max and
                lat_min <= max_lat <= lat_max and lat_min <= min_lat <= lat_max):
                data_regions.append(region_name)

    # Flag if declared region doesn't match any determined regions
    if declared_region not in data_regions:
        df['flag_vessel_region'] = 3
        if 'flag' not in df.columns:
            df['flag'] = 1
        df['flag'] = 3

    return df


if __name__ == "__main__":
    # Example usage
    import pandas as pd

    # Create test data in Atlantic Ocean
    df = pd.DataFrame({
        'latitude': [45.0, 46.0, 44.5, 45.5],
        'longitude': [-50.0, -51.0, -49.5, -50.5],
        'temperature': [15.2, 15.0, 15.5, 15.3],
        'pressure': [10.0, 12.0, 11.0, 10.5]
    })

    print("Test Data (Atlantic Ocean region):")
    print(f"Lat range: [{df['latitude'].min()}, {df['latitude'].max()}]")
    print(f"Lon range: [{df['longitude'].min()}, {df['longitude'].max()}]")

    # Test correct region
    print("\n1. Testing with correct region (Atlantic):")
    df_test1 = flag_vessel_region(df.copy(), declared_region='Atlantic')
    print(f"   Result: {df_test1['flag_vessel_region'].iloc[0]} (should be 1)")

    # Test incorrect region
    print("\n2. Testing with incorrect region (Mediterranean Sea):")
    df_test2 = flag_vessel_region(df.copy(), declared_region='Mediterranean Sea')
    print(f"   Result: {df_test2['flag_vessel_region'].iloc[0]} (should be 3)")

    # Test 'All' bypass
    print("\n3. Testing with 'All' (bypass):")
    df_test3 = flag_vessel_region(df.copy(), declared_region='All')
    print(f"   Result: {df_test3['flag_vessel_region'].iloc[0]} (should be 1)")
