"""Flag Rollover Test - Bottom temperature changes"""
import pandas as pd

def flag_rollover(df, temp_col='temperature', segment_col='segment_type'):
    """Flag if bottom temperature differs > 1.0°C from previous."""
    df['flag_rollover'] = 1
    df['prev_temp'] = df[temp_col].shift(1)
    
    mask = (abs(df[temp_col] - df['prev_temp']) > 1.0) & (df[segment_col] == 'Fishing')
    df.loc[mask, 'flag_rollover'] = 3
    
    df = df.drop(columns=['prev_temp'])
    return df
