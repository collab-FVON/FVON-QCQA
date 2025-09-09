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
    import json
    from datetime import date, datetime, timedelta
    from zoneinfo import ZoneInfo
    
    # Read in available program metadata
    with open("Proposed_QC_Checks/supporting_data.json","r") as file:
      p_meta=json.load(file)
      
    # Define a start_date and end_date based on the program
    i = -1
  
    for index,item in enumerate(p_meta):
      if item['Abbreviation'] == fvon_program:
        i = index
        start_date = item['Start_Date']
        end_date = item['End_Date']
        break
    
    if i == -1:
      raise ValueError("FVON program abbreviation not found")

    # Reformat start_date from character into a timestamp with timezone
    start_date = datetime.strptime(start_date,"%Y-%m-%d")
    start_date = pd.to_datetime(start_date)
    start_date = start_date.replace(tzinfo=ZoneInfo("UTC"))
    
    # Define the end date
    # If the program is ongoing, use tomorrow's date as the end_date, otherwise
    # use the existing end_date from the .json file
    if end_date is None:
      end_date = pd.to_datetime(date.today()+timedelta(days=1))
    else:
      end_date = datetime.strptime(end_date, "%Y-%m-%d")
      
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
    
