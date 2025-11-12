"""Flag Impossible Speed Test - Detects unrealistic vessel speeds"""
import pandas as pd
from geopy.distance import geodesic

def flag_impossible_speed(df, gear_type, speed_threshold=4.12):
    """Flag speeds exceeding 4.12 m/s (8 knots) for mobile gear."""
    df['flag_impossible_speed'] = 1
    
    if gear_type.upper() == 'FIXED':
        return df
    
    # Calculate speeds between consecutive points
    speeds = []
    for i in range(1, len(df)):
        if pd.notna(df['latitude'].iloc[i]) and pd.notna(df['latitude'].iloc[i-1]):
            dist = geodesic(
                (df['latitude'].iloc[i-1], df['longitude'].iloc[i-1]),
                (df['latitude'].iloc[i], df['longitude'].iloc[i])
            ).meters
            time_diff = (df['datetime'].iloc[i] - df['datetime'].iloc[i-1]).total_seconds()
            if time_diff > 0:
                speeds.append(dist / time_diff)
            else:
                speeds.append(0)
        else:
            speeds.append(0)
    
    speeds = [0] + speeds
    df['speed'] = speeds
    df.loc[df['speed'] > speed_threshold, 'flag_impossible_speed'] = 4
    df = df.drop(columns=['speed'])
    
    return df

if __name__ == "__main__":
    print("See QC.py for full implementation")
