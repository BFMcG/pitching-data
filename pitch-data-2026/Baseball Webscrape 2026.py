import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import numpy as np
from io import StringIO
import os
import contextlib

lookup_date = "2026-07-26"

while lookup_date <= "2026-07-29":
    print('Fetching data for:', lookup_date)
    # Get request for all the pitchers that played on a sepecifc date
    url = "https://baseballsavant.mlb.com/statcast_search"

    # url parameters for all pitchers that pitched on lookup_date
    params_all_players = {
        "hfGT": "R|",
        "hfSea": "2026|",
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

    print('Players recorded')
    print("Starting pitch fetch")

    ### Fetching Daily data

    # List of all attack zones
    attack_zone = [nums for nums in range(1,40) if nums not in [10,15,20,25,30,35]]

    pitch_df = pd.DataFrame()

    url_csv = "https://baseballsavant.mlb.com/statcast_search/csv"

    for zone in attack_zone:
        params_az = {
            "hfGT": "R|",
            "hfNewZones": zone,
            "hfSea": "2026|",
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
        time.sleep(random.uniform(9.84, 15.67)) 

        df = pd.read_csv(StringIO(response.text))

        # Creating attack zone column
        df["attack_zone"] = zone
        
        pitch_df = pd.concat([pitch_df, df], ignore_index=True)

    print('Fetch completed')

    # Checking and removing auto balls, auto strikes, and intentional walks
    pitch_df = pitch_df[~pitch_df['pitch_type'].isin(['AB', 'AS', 'IBB'])].copy()

    print("Total pitches for", lookup_date, ": ", len(pitch_df))

    spark_pitch_df = spark.createDataFrame(pitch_df)

    print("Appending to Bronze Layer")

    spark_pitch_df.write.mode("append").saveAsTable("pitch_data_2026.bronze.pitch_data")

    lookup_date = (pd.Timestamp(lookup_date) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")












