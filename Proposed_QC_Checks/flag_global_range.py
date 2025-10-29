"""Flag Global Range Test - Validates sensor operating ranges"""
import pandas as pd

def flag_global_range(df, sensor_type, temp_col='temperature', pres_col='pressure', sal_col='salinity'):
    """Flag values outside sensor operating ranges."""
    df['flag_global_range'] = 1
    
    # Define sensor-specific ranges
    ranges = {
        'NKE': {'temp': (-2, 35), 'pres_max': 1100},
        'ZEBRATECH': {'temp': (-2, 35), 'pres_max': 1100},
        'MOANA': {'temp': (-2, 35), 'pres_max': 1100},
        'LOWELL': {'temp': (-5, 50), 'pres_max': 1500},
    }
    
    if sensor_type not in ranges:
        return df
    
    r = ranges[sensor_type]
    
    # Pressure checks
    df.loc[(df[pres_col] >= -5) & (df[pres_col] < 0), 'flag_global_range'] = 3
    df.loc[df[pres_col] > r['pres_max'], 'flag_global_range'] = 3
    df.loc[df[pres_col] < -5, 'flag_global_range'] = 4
    
    # Temperature check
    df.loc[(df[temp_col] < r['temp'][0]) | (df[temp_col] > r['temp'][1]), 'flag_global_range'] = 4
    
    return df

if __name__ == "__main__":
    print("See QC.py for full implementation")
