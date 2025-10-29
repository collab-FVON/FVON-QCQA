"""Flag Temperature/Salinity Spike Test"""
import pandas as pd

def flag_temp_spike(df, temp_col='temperature', pres_col='pressure'):
    """Neighbor-based spike test with depth-dependent thresholds."""
    df['flag_temp_spike'] = 1
    df['prev'] = df[temp_col].shift(1)
    df['post'] = df[temp_col].shift(-1)
    df['val'] = abs(df[temp_col] - (df['post'] + df['prev'])/2) - abs((df['post'] - df['prev'])/2)
    
    # Depth-dependent thresholds
    df.loc[(df[pres_col] < 500) & (df['val'] > 6.0), 'flag_temp_spike'] = 4
    df.loc[(df[pres_col] >= 500) & (df['val'] > 2.0), 'flag_temp_spike'] = 4
    
    df = df.drop(columns=['prev', 'post', 'val'])
    return df
