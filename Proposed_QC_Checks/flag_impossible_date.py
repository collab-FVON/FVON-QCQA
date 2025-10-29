"""
Flag Impossible Date Test

Flags data with dates before 01/01/2010 or after current UTC date.

Author: FVON-QCQA Team
Date: 2025-10-29
Issue: #6
"""

import pandas as pd
from datetime import datetime, timezone


def flag_impossible_date(df, datetime_col='datetime', min_date='2010-01-01'):
    """
    Flag data with impossible dates (before min_date or after current UTC date).

    The date of the profile can be no earlier than 01/01/2010 and no later
    than current date in UTC.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing oceanographic observation data
    datetime_col : str, optional
        Name of the datetime column (default: 'datetime')
    min_date : str, optional
        Minimum acceptable date in 'YYYY-MM-DD' format (default: '2010-01-01')

    Returns
    -------
    pd.DataFrame
        Input DataFrame with added 'flag_impossible_date' column

    Flag Values
    -----------
    1 : Pass - Valid date
    4 : Fail - Impossible date (before min_date or after current UTC date)

    Examples
    --------
    >>> import pandas as pd
    >>> from datetime import datetime
    >>>
    >>> # Create sample data
    >>> df = pd.DataFrame({
    ...     'datetime': pd.to_datetime(['2009-12-31', '2020-06-15', '2099-01-01']),
    ...     'temperature': [15.2, 18.3, 20.1]
    ... })
    >>>
    >>> # Apply QC test
    >>> df = flag_impossible_date(df)
    >>> print(df[['datetime', 'flag_impossible_date']])
    #      datetime  flag_impossible_date
    # 0  2009-12-31                     4  (too early)
    # 1  2020-06-15                     1  (valid)
    # 2  2099-01-01                     4  (in future)

    Notes
    -----
    - Uses current UTC time for maximum date check
    - Default minimum date is 2010-01-01 (can be program-specific)
    - Updates the main 'flag' column to 4 if date test fails

    References
    ----------
    - IOOS QARTOD Manual for Real-Time Quality Control
    - FVON-QCQA README.md
    """
    # Initialize flag column
    df['flag_impossible_date'] = 1
    if 'flag' not in df.columns:
        df['flag'] = 1

    # Ensure datetime column is datetime type
    df[datetime_col] = pd.to_datetime(df[datetime_col])

    # Get current UTC date and minimum date
    currdate = datetime.now(timezone.utc).replace(tzinfo=None)
    mindate = pd.to_datetime(min_date)

    # Flag dates outside valid range
    mask = (df[datetime_col] > currdate) | (df[datetime_col] < mindate)
    df.loc[mask, 'flag_impossible_date'] = 4
    df.loc[mask, 'flag'] = 4

    return df


if __name__ == "__main__":
    # Example usage
    import pandas as pd
    from datetime import datetime, timedelta

    # Create test data
    df = pd.DataFrame({
        'datetime': pd.to_datetime([
            '2009-12-31',  # Too early
            '2015-06-15',  # Valid
            '2023-01-01',  # Valid
            datetime.now() + timedelta(days=1)  # Future date
        ]),
        'latitude': [45.0, 45.1, 45.2, 45.3],
        'longitude': [-65.0, -65.1, -65.2, -65.3],
        'temperature': [15.2, 18.3, 20.1, 19.5]
    })

    print("Original Data:")
    print(df)
    print("\nApplying impossible date test...")

    df = flag_impossible_date(df)

    print("\nResults:")
    print(df[['datetime', 'flag_impossible_date']])

    print(f"\nPassed: {len(df[df['flag_impossible_date'] == 1])}")
    print(f"Failed: {len(df[df['flag_impossible_date'] == 4])}")
