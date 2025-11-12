"""Flag Rate of Change Test - Segment-specific thresholds"""
import pandas as pd

def flag_rate_of_change(df, temp_col='temperature', segment_col='segment_type', n_dev=3):
    """Flag steps > N standard deviations within each segment."""
    df['flag_rate_of_change'] = 1
    
    for segment in ['Profiling Down', 'Fishing', 'Profiling Up']:
        seg_data = df[df[segment_col] == segment]
        if len(seg_data) > 0:
            sd = seg_data[temp_col].std()
            df['prev'] = df[temp_col].shift(1)
            mask = (abs(df[temp_col] - df['prev']) > (n_dev * sd)) & (df[segment_col] == segment)
            df.loc[mask, 'flag_rate_of_change'] = 3
    
    if 'prev' in df.columns:
        df = df.drop(columns=['prev'])
    return df
