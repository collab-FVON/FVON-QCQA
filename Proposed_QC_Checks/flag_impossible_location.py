def flag_impossible_location(filename):
    """
    This program checks to see if the location of an observation is
    considered impossible based on the provided coordinates.
    
    Args:
      filename: The name of the file the dataframe will be loaded from 
      
    Returns:
      flagged_dataframe: The dataframe with an additional column called 
        "flag_impossible_location" which can have the values as follows
        - 1: Pass
        - 4: Fail -- location is impossible
    """
    
    import pandas as pd

    # Read in the dataframe to be evaluated
    observations = pd.read_csv(filename)
    
    # Check to see if the latitude and longitude are within bounds
    condition = (-90 < observations['latitude']) & (observations['latitude'] < 90) & (-180 < observations['longitude']) & (observations['longitude'] < 180)
    
    # Replace condition values with flags
    custom_mapping = {True: 4, False: 1}
    condition = condition.map(custom_mapping)
    
    # Add the new vector to the existing dataframe
    new_observations = observations
    new_observations['flag_impossible_location'] = condition
    
    return new_observations
