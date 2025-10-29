"""Flag Climatology Test - Regional/seasonal expectations"""
import pandas as pd

def flag_climatology(df, region, temp_col='temperature'):
    """Flag values outside seasonal/region expectations."""
    regions = {
        'Red Sea': (21.7, 40),
        'Mediterranean Sea': (10, 40),
        'Atlantic': (2, 40),
        'North Sea': (2, 40),
        'Pacific': (2, 40),
        'Gulf of Mexico': (2, 40),
        'Alaska': (-1.92, 25),
        'Canada': (-1.92, 25),
        'All': (-1.92, 35)
    }
    
    df['flag_climatology'] = 1
    if region in regions:
        tmin, tmax = regions[region]
        df.loc[(df[temp_col] < tmin) | (df[temp_col] > tmax), 'flag_climatology'] = 3
    
    return df
