def flag_impossible_date(fvon_program, filename):
    """
    This program checks to see if the date of an observation is
    considered impossible based on the program that collected
    the observation. For example, eMOLT began in 2001, 
    therefore, no observations should include dates earlier 
    than 2001-01-01. The end date for the check is defined as
    ...
    
    Args:
      fvon_program: The name of the FVON Program the data were collected by. 
        Currently supported values are
        - eMOLT
      filename: The name of the file the dataframe will be loaded from (may be 
        necessary to know the offload date)
      
    Returns:
      flagged_dataframe: The dataframe with an additional column called 
        "flag_impossible_date" which can have the values as follows
        - 1: Pass
        - 4: Fail -- date is impossible based on the program provided
    """
    
    import pandas as pd
    from datetime import date, datetime, timedelta
    from zoneinfo import ZoneInfo
    
    # Read in available program metadata
    p_meta = pd.read_csv("Proposed_QC_Checks/supporting_data.csv")
    
    # Check to see if the program exists
    try:
      p_meta['Abbreviation'].isin([fvon_program])
    except KeyError:
      print("Error: fvon_program not defined.")
      
    # Define a start_date based on the program
    condition = p_meta['Abbreviation']==fvon_program
    start_date = p_meta['Start_Date'][p_meta[condition].index.to_list()]
    # Reformat start_date from character into a timestamp with timezone
    start_date = datetime.strptime(start_date[0],"%Y-%m-%d")
    start_date = pd.to_datetime(start_date)
    start_date = start_date.replace(tzinfo=ZoneInfo("UTC"))
    
    # Define the end date
    end_date = pd.to_datetime(date.today()+timedelta(days=1))
    # Add a timezone
    end_date = end_date.replace(tzinfo=ZoneInfo("UTC"))
    
    # Read in the dataframe to be evaluated
    observations = pd.read_csv(filename)
    # Reformat date times
    timestamps = pd.to_datetime(observations['ISO 8601 Time'])
    observations['ISO 8601 Time']=timestamps

    
    # Check to see if the observation dates are between the start_date and 
    # end_date
    condition = (observations['ISO 8601 Time'] > start_date) & (observations['ISO 8601 Time'] < end_date)   
    
    # Replace condition values with flags
    custom_mapping = {True: 1, False: 4}
    condition = condition.map(custom_mapping)
    
    # Add the new vector to the existing dataframe
    new_observations = observations
    new_observations['flag_impossible_date'] = condition
    
    return new_observations
    
