"""Flag Mud Test - Near-constant temperature during profiling up"""
import pandas as pd

def flag_mud(df, temp_col='temperature', pres_col='pressure', segment_col='segment_type'):
    """Flags mud/obstruction by comparing Down vs Up profiles."""
    df['flag_mud'] = 1
    
    df['temp_diff'] = df[temp_col] - df[temp_col].shift(1)
    
    up = df[df[segment_col] == 'Profiling Up']
    down = df[df[segment_col] == 'Profiling Down']
    
    # Check deeper half only
    up_deep = up[up[pres_col] > up[pres_col].max() / 2]
    
    if len(up_deep) > 0:
        up_deep['rolled'] = up_deep['temp_diff'].rolling(10, center=True, min_periods=1).mean()
        flat_count = len(up_deep[abs(up_deep['rolled']) < 0.005])
        
        if flat_count > 10 and flat_count / len(up_deep) > 0.5:
            df.loc[df[segment_col] == 'Profiling Up', 'flag_mud'] = 3
    
    df = df.drop(columns=['temp_diff'])
    return df
