"""
Flag Impossible Location Test

Flags data with impossible geographic coordinates (outside valid lat/lon ranges).

Author: FVON-QCQA Team
Date: 2025-10-29
Issue: #7
"""

import pandas as pd


def flag_impossible_location(df, lat_col='latitude', lon_col='longitude'):
    """
    Flag data with impossible geographic coordinates.

    Checks that latitude is within [-90, 90] and longitude within [-180, 180].

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing oceanographic observation data
    lat_col : str, optional
        Name of the latitude column (default: 'latitude')
    lon_col : str, optional
        Name of the longitude column (default: 'longitude')

    Returns
    -------
    pd.DataFrame
        Input DataFrame with added 'flag_impossible_location' column

    Flag Values
    -----------
    1 : Pass - Valid coordinates
    4 : Fail - Impossible location (latitude outside [-90, 90] or
        longitude outside [-180, 180])

    Examples
    --------
    >>> import pandas as pd
    >>>
    >>> # Create sample data
    >>> df = pd.DataFrame({
    ...     'latitude': [45.0, -91.0, 89.5, 0.0],
    ...     'longitude': [-65.0, -170.0, 200.0, 0.0],
    ...     'temperature': [15.2, 18.3, 20.1, 19.5]
    ... })
    >>>
    >>> # Apply QC test
    >>> df = flag_impossible_location(df)
    >>> print(df[['latitude', 'longitude', 'flag_impossible_location']])
    #    latitude  longitude  flag_impossible_location
    # 0     45.0      -65.0                         1  (valid)
    # 1    -91.0     -170.0                         4  (lat < -90)
    # 2     89.5      200.0                         4  (lon > 180)
    # 3      0.0        0.0                         1  (valid, "Null Island")

    Notes
    -----
    - Uses 180° limit for longitude (not 360°)
    - Point (0, 0) "Null Island" is considered valid but may need special handling
    - NaN/missing values should be handled separately
    - Updates the main 'flag' column to 4 if location test fails

    References
    ----------
    - IOOS QARTOD Manual for Real-Time Quality Control
    - FVON-QCQA README.md
    """
    # Initialize flag column
    df['flag_impossible_location'] = 1
    if 'flag' not in df.columns:
        df['flag'] = 1

    # Define valid ranges
    latrange = [-90, 90]
    lonrange = [-180, 180]

    # Flag coordinates outside valid ranges
    mask = (
        (df[lat_col] < latrange[0]) | (df[lat_col] > latrange[1]) |
        (df[lon_col] < lonrange[0]) | (df[lon_col] > lonrange[1])
    )
    df.loc[mask, 'flag_impossible_location'] = 4
    df.loc[mask, 'flag'] = 4

    return df


if __name__ == "__main__":
    # Example usage
    import pandas as pd

    # Create test data with various coordinate issues
    df = pd.DataFrame({
        'latitude': [45.0, -91.0, 89.5, 0.0, 45.2],
        'longitude': [-65.0, -170.0, 200.0, 0.0, -181.0],
        'temperature': [15.2, 18.3, 20.1, 19.5, 16.8],
        'pressure': [10.0, 15.0, 20.0, 5.0, 12.0]
    })

    print("Original Data:")
    print(df[['latitude', 'longitude', 'temperature']])
    print("\nApplying impossible location test...")

    df = flag_impossible_location(df)

    print("\nResults:")
    print(df[['latitude', 'longitude', 'flag_impossible_location']])

    print(f"\nPassed: {len(df[df['flag_impossible_location'] == 1])}")
    print(f"Failed: {len(df[df['flag_impossible_location'] == 4])}")

    # Show which records failed
    failed = df[df['flag_impossible_location'] == 4]
    if len(failed) > 0:
        print("\nFailed records:")
        for idx, row in failed.iterrows():
            reasons = []
            if row['latitude'] < -90 or row['latitude'] > 90:
                reasons.append(f"lat={row['latitude']}")
            if row['longitude'] < -180 or row['longitude'] > 180:
                reasons.append(f"lon={row['longitude']}")
            print(f"  Row {idx}: {', '.join(reasons)}")
