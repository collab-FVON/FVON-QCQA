"""Flag Response Time Test - dP/dt thresholds"""
import pandas as pd

def flag_response_time(df, pres_col='pressure', time_col='datetime', segment_col='segment_type'):
    """Flags overly rapid dP/dt in Down/Up segments."""
    df['flag_response_time'] = 1
    
    # Calculate dP/dt
    df['dpdt'] = abs((df[pres_col] - df[pres_col].shift(1)) / 
                     (df[time_col] - df[time_col].shift(1)).dt.total_seconds())
    df['dpdt'] = df['dpdt'].fillna(0)
    
    # Apply thresholds to profiling segments
    prof_mask = df[segment_col].isin(['Profiling Down', 'Profiling Up'])
    df.loc[prof_mask & (df['dpdt'] > 2.0), 'flag_response_time'] = 4
    df.loc[prof_mask & (df['dpdt'] > 1.0) & (df['dpdt'] <= 2.0), 'flag_response_time'] = 3
    
    df = df.drop(columns=['dpdt'])
    return df
