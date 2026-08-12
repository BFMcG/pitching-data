import requests
from bs4 import BeautifulSoup
from pybaseball import pitching_stats_range
import pandas as pd
import time
import random
from pybaseball import playerid_lookup
from pybaseball import statcast_pitcher
import numpy as np
from io import StringIO
import os
import contextlib

# pybaseball==2.2.7

lookup_date = "2025-03-27"

while lookup_date <= "2025-09-28":

    print("Starting fetch for ", lookup_date)

    assert_passed = False

    # Get request for all the pitchers that played on a sepecifc date
    url = "https://baseballsavant.mlb.com/statcast_search"

    # url parameters for all pitchers that pitched on lookup_date
    params_all_players = {
        "hfGT": "R|",
        "hfSea": "2025|",
        "player_type": "pitcher",
        "game_date_gt": lookup_date,
        "game_date_lt": lookup_date,
        "group_by": "name",
        "min_pitches": 0,
        "min_results": 0,
        "min_pas": 0,
        "sort_col": "pitches",
        "sort_order": "desc"
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "XMLHttpRequest"
    }

    response = requests.get(url, params=params_all_players, headers=headers)
    player_soup = BeautifulSoup(response.text, "html.parser")

 
    player_names = [
        {"player_name": name, "player_id": pid}
        for row in player_soup.find_all("tr", class_="search_row")
        if (pid := row.get("data-player-id")) and (name := row.get("data-player-name"))
    ]

    print("Starting total pitch fetch")

    ## Fetching a request of each player on the player_names list
    temp_total_pitching_df = pd.DataFrame()

    # Making new parameters for each player on the daily list
    for player in player_names:
        params_per_player = {
            "hfGT": "R|",
            "hfSea": "2025|",
            "player_type": "pitcher",
            "game_date_gt": lookup_date,
            "game_date_lt": lookup_date,
            "group_by": "name",
            "min_pitches": 0,
            "min_results": 0,
            "min_pas": 0,
            "sort_col": "pitches",
            "sort_order": "desc",
            "type": "details",
            "player_id": player['player_id']
        }

        response = requests.get(url, params=params_per_player, headers=headers, timeout=25)
        time.sleep(random.uniform(1.73, 1.99))

        table = pd.read_html(StringIO(response.text))
        df = table[0]
        
        # Checking and removing auto balls, auto strikes, and intentional walks
        df = df[~df['Pitch'].isin(['AB', 'AS', 'IBB'])].copy()

        # Creating additional columns
        df['Player ID'] = player["player_id"] # Adding player ID to each row for the player
        df['Total Pitch Count'] = range(len(df), 0, -1) # Adding the pitch count for the appearence

        temp_total_pitching_df = pd.concat([temp_total_pitching_df, df], ignore_index=True)



    # Checking if data was recorded or not
    temp_total_pitching_df = temp_total_pitching_df[~temp_total_pitching_df['Zone'].isna()].copy()
    
    # Parsing out ° from launch angle values
    temp_total_pitching_df['LA (°)'] = pd.to_numeric(
        temp_total_pitching_df['LA (°)']
        .astype(str).str
        .replace("°", "", regex=False),errors="coerce")

    # Converting numeric columns to numeric types for spark transfer
    num_columns = ['MPH', 'Spin Rate', 'EV (MPH)', 'LA (°)', 'Dist (ft)']

    temp_total_pitching_df[num_columns] = temp_total_pitching_df[num_columns].apply(pd.to_numeric, errors="coerce")

    # Getting rid of the spaces and () for all column names so it will work when importing in dataframe
    temp_total_pitching_df.columns = temp_total_pitching_df.columns.str.replace(" ", "_").str.replace("(", "").str.replace(")", "")

    print("Total Pitch Complete")
    print("Starting attack zone fetch")

    ### Finding Attack Zones

    # List of all attack zones
    attack_zone = [nums for nums in range(1,40) if nums not in [10,15,20,25,30,35]]

    temp_attack_zone_df = pd.DataFrame()

    url_csv = "https://baseballsavant.mlb.com/statcast_search/csv"

    for zone in attack_zone:
        params_az = {
            "hfGT": "R|",
            "hfNewZones": zone,
            "hfSea": "2025|",
            "player_type": "pitcher",
            "game_date_gt": lookup_date,
            "game_date_lt": lookup_date,
            "group_by": "name",
            "min_pitches": 0,
            "min_results": 0,
            "min_pas": 0,
            "sort_col": "pitches",
            "sort_order": "desc",
            "type": "details",
            "all": "true",
            "minors": "false",
            "wbc": "false"
        }

        response = requests.get(url_csv, params=params_az, headers=headers, timeout=25)
        time.sleep(random.uniform(1.73, 1.99)) 

        df = pd.read_csv(StringIO(response.text))

        # Creating attack zone column
        df["attack_zone"] = zone
        
        temp_attack_zone_df = pd.concat([temp_attack_zone_df, df], ignore_index=True)

    # Checking and removing auto balls, auto strikes, and intentional walks
    temp_attack_zone_df = temp_attack_zone_df[~temp_attack_zone_df['pitch_type'].isin(['AB', 'AS', 'IBB'])].copy()

    print("Attack Zone Fetch Complete")
    print("Starting pybaseball fetch")


    ### Pybaseball
    temp_pybaseball_df = pd.DataFrame()

    for player in player_names:
        with open(os.devnull, "w") as f:
            with contextlib.redirect_stdout(f):
                df = statcast_pitcher(lookup_date, lookup_date, player_id=player['player_id'])
                time.sleep(random.uniform(1.57, 2.09))
        temp_pybaseball_df = pd.concat([temp_pybaseball_df, df], ignore_index=True)
        
    
    # Checking and removing auto balls, auto strikes, and intentional walks
    temp_pybaseball_df = temp_pybaseball_df[~temp_pybaseball_df['description'].isin(['automatic_ball', 'automatic_strike'])].copy()

    # Checking if data was recorded or not
    temp_pybaseball_df = temp_pybaseball_df[~temp_pybaseball_df['zone'].isna()].copy()
      
    print("Pybaseball Fetch Complete")

    if not (len(temp_attack_zone_df) == len(temp_total_pitching_df) ==  len(temp_pybaseball_df)):
        raise ValueError("Error: length of data frames are not equal :", len(temp_attack_zone_df), len(temp_total_pitching_df), len(temp_pybaseball_df))

    else:
        print("data lengths for", lookup_date, ": ", len(temp_attack_zone_df), len(temp_total_pitching_df), len(temp_pybaseball_df))
        assert_passed = True

    if assert_passed:
        # Converting to pyspark dataframe
        pys_total_pitch_df = spark.createDataFrame(temp_total_pitching_df)
        pys_attack_zone_df = spark.createDataFrame(temp_attack_zone_df)
        pys_pybaseball_df = spark.createDataFrame(temp_pybaseball_df)

        # Writing to bronze table
        pys_total_pitch_df.write.mode("append").saveAsTable("pitch_data_2025.bronze.total_pitch_data")
        pys_attack_zone_df.write.mode("append").saveAsTable("pitch_data_2025.bronze.attack_zone_data")
        pys_pybaseball_df.write.mode("append").saveAsTable("pitch_data_2025.bronze.pybaseball_data")

        print("Data written to bronze complete")

    lookup_date = (pd.Timestamp(lookup_date) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")

print("Data Collection Complete!!!")
