"""Flag Stuck Value Test - Detects sensor failures"""
import pandas as pd

def flag_temp_stuck(df, temp_col='temperature', segment_col='segment_type'):
    """Flag identical repeated values (3=suspect, 5=fail)."""
    df['flag_temp_stuck'] = 1
    
    # Check for 3 consecutive identical values
    df['p1'] = df[temp_col].shift(1)
    df['n1'] = df[temp_col].shift(-1)
    mask3 = (df['p1'] == df[temp_col]) & (df['n1'] == df[temp_col]) & (df[segment_col] != 'Fishing')
    df.loc[mask3, 'flag_temp_stuck'] = 3
    
    # Check for 5 consecutive identical values
    df['p2'] = df[temp_col].shift(2)
    df['n2'] = df[temp_col].shift(-2)
    mask5 = mask3 & (df['p2'] == df[temp_col]) & (df['n2'] == df[temp_col])
    df.loc[mask5, 'flag_temp_stuck'] = 4
    
    df = df.drop(columns=['p1', 'n1', 'p2', 'n2'])
    return df
