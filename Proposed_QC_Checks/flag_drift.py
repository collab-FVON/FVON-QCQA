"""Flag Drift Test - Bottom T/S drift detection"""
import pandas as pd

def flag_drift(df, temp_col='temperature', segment_col='segment_type', time_col='datetime'):
    """Detects substantial drift in T/S during Fishing for deployments < 24h."""
    df['flag_drift'] = 1
    
    bottom = df[df[segment_col] == 'Fishing']
    if len(bottom) == 0:
        return df
    
    duration_hrs = (bottom[time_col].max() - bottom[time_col].min()).total_seconds() / 3600
    
    if duration_hrs < 24:
        temp_change = abs(bottom[temp_col].iloc[0] - bottom[temp_col].iloc[-1])
        if temp_change > 3.0:
            df['flag_drift'] = 3
    
    return df
