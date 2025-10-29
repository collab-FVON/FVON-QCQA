"""Flag Cold Surface Test - Ice clogging detection"""
import pandas as pd

def flag_cold_surface(df, temp_col='temperature', pres_col='pressure', segment_col='segment_type'):
    """Detects anomalous warming on descent near surface (ice/thermistor clogging)."""
    df['flag_cold_surface'] = 1
    
    df['diff_temp'] = df[temp_col] - df[temp_col].shift(1)
    df['diff_temp'] = df['diff_temp'].shift(-1)  # Look ahead
    
    # Flag warming during descent near surface
    mask = (df[segment_col] == 'Profiling Down') & (df['diff_temp'] > 0.5) & (df[pres_col] < 10)
    df.loc[mask, 'flag_cold_surface'] = 3
    
    # Extend flag to all surface points
    if mask.any():
        last_flag_idx = df[mask].index.max()
        df.loc[df.index <= last_flag_idx + 1, 'flag_cold_surface'] = 3
    
    df = df.drop(columns=['diff_temp'])
    return df
