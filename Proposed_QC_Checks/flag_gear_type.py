"""Flag Gear Type Test - Validates motion vs gear type (FIXED vs MOBILE)"""
import pandas as pd
from geopy.distance import geodesic

def flag_gear_type(df, gear_type, lat_col='raw_lat', lon_col='raw_lon'):
    """Flag data when gear type doesn't match observed motion patterns."""
    df['flag_gear_type'] = 1
    gear = gear_type.upper()
    if gear == 'OTHER':
        return df
    
    # Calculate distance traveled
    coords_1 = (df[lat_col].iloc[0], df[lon_col].iloc[0])
    coords_2 = (df[lat_col].iloc[-1], df[lon_col].iloc[-1])
    
    if pd.isna(coords_1[0]) or pd.isna(coords_2[0]):
        df['flag_gear_type'] = 4
        return df
    
    d = geodesic(coords_1, coords_2).m
    
    # Threshold: 200 meters
    if (d > 200 and gear == 'FIXED') or (d <= 200 and gear == 'MOBILE'):
        df['flag_gear_type'] = 3
    
    return df

if __name__ == "__main__":
    print("See QC.py for full implementation")
