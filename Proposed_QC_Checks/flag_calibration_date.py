"""
Flag Calibration Date Test

Flags sensors where last calibration date exceeds sensor-specific thresholds.

Author: FVON-QCQA Team
Date: 2025-10-29
Issue: #12
"""

import pandas as pd


def flag_calibration_date(df, datetime_col='datetime', calibration_col='calibration_date',
                         sensor_col='sensor_type', thresholds=None):
    """
    Flag data based on sensor calibration date.

    Checks if the gap between observation date and last calibration exceeds
    sensor-specific thresholds.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing oceanographic observation data
    datetime_col : str, optional
        Name of the datetime column (default: 'datetime')
    calibration_col : str, optional
        Name of the calibration date column (default: 'calibration_date')
    sensor_col : str, optional
        Name of the sensor type column (default: 'sensor_type')
    thresholds : dict, optional
        Dictionary mapping sensor types to calibration intervals in years.
        Default: {'ZEBRATECH': 2, 'NKE': 0.5, 'MOANA': 2, 'LOWELL': 1}

    Returns
    -------
    pd.DataFrame
        Input DataFrame with added 'flag_calibration_date' column

    Flag Values
    -----------
    1 : Pass - Within calibration window
    2 : Not evaluated - Missing calibration date
    3 : Suspect - Outside calibration window

    Examples
    --------
    >>> import pandas as pd
    >>> from datetime import datetime, timedelta
    >>>
    >>> # Create sample data
    >>> df = pd.DataFrame({
    ...     'datetime': pd.to_datetime(['2023-01-15', '2023-06-15', '2023-12-15']),
    ...     'calibration_date': pd.to_datetime(['2021-01-01', '2023-01-01', '2020-01-01']),
    ...     'sensor_type': ['ZEBRATECH', 'ZEBRATECH', 'ZEBRATECH'],
    ...     'temperature': [15.2, 18.3, 20.1]
    ... })
    >>>
    >>> # Apply QC test
    >>> df = flag_calibration_date(df)
    >>> print(df[['datetime', 'calibration_date', 'flag_calibration_date']])
    #     datetime calibration_date  flag_calibration_date
    # 0 2023-01-15       2021-01-01                      1  (2.0 years, pass)
    # 1 2023-06-15       2023-01-01                      1  (0.5 years, pass)
    # 2 2023-12-15       2020-01-01                      3  (3.9 years, suspect)

    Notes
    -----
    - ZEBRATECH: 2-year calibration interval
    - NKE: 6-month (0.5 year) calibration interval
    - Missing calibration dates are flagged as 2 (not evaluated)

    References
    ----------
    - Sensor manufacturer specifications
    - FVON-QCQA README.md
    """
    # Default thresholds (in years)
    if thresholds is None:
        thresholds = {
            'ZEBRATECH': 2.0,
            'NKE': 0.5,
            'MOANA': 2.0,
            'LOWELL': 1.0
        }

    # Initialize flag column
    df['flag_calibration_date'] = 1

    # Ensure datetime columns are datetime type
    df[datetime_col] = pd.to_datetime(df[datetime_col])
    df[calibration_col] = pd.to_datetime(df[calibration_col], errors='coerce')

    try:
        # Calculate gap in years
        df['gap_cal'] = (df[datetime_col].dt.date - df[calibration_col].dt.date)
        df['gap_cal'] = pd.to_timedelta(df['gap_cal'])
        df['gap_cal'] = df['gap_cal'].dt.total_seconds() / 3600 / 24 / 365

        # Check each sensor type
        for sensor_type, threshold in thresholds.items():
            mask = (df['gap_cal'] > threshold) & (df[sensor_col] == sensor_type)
            df.loc[mask, 'flag_calibration_date'] = 3

        # Flag missing calibration dates
        df.loc[df['gap_cal'].isna(), 'flag_calibration_date'] = 2

        # Clean up temporary column
        df = df.drop(columns=['gap_cal'])

    except Exception as e:
        print(f"Warning: Error processing calibration dates: {e}")
        # If error, flag as not evaluated
        df['flag_calibration_date'] = 2
        if 'gap_cal' in df.columns:
            df = df.drop(columns=['gap_cal'])

    return df


if __name__ == "__main__":
    # Example usage
    import pandas as pd
    from datetime import datetime, timedelta

    # Create test data
    now = datetime(2023, 12, 15)
    df = pd.DataFrame({
        'datetime': [now, now, now, now],
        'calibration_date': pd.to_datetime([
            now - timedelta(days=365*2.5),  # 2.5 years ago (expired for ZEBRATECH)
            now - timedelta(days=365*1.5),  # 1.5 years ago (ok for ZEBRATECH)
            now - timedelta(days=180),      # 6 months ago (ok for NKE)
            pd.NaT                          # Missing
        ]),
        'sensor_type': ['ZEBRATECH', 'ZEBRATECH', 'NKE', 'ZEBRATECH'],
        'temperature': [15.2, 18.3, 20.1, 19.5],
        'pressure': [10.0, 15.0, 20.0, 5.0]
    })

    print("Original Data:")
    print(df[['datetime', 'calibration_date', 'sensor_type']])
    print("\nApplying calibration date test...")

    df = flag_calibration_date(df)

    print("\nResults:")
    print(df[['sensor_type', 'calibration_date', 'flag_calibration_date']])

    print(f"\nPass: {len(df[df['flag_calibration_date'] == 1])}")
    print(f"Not Evaluated: {len(df[df['flag_calibration_date'] == 2])}")
    print(f"Suspect: {len(df[df['flag_calibration_date'] == 3])}")
