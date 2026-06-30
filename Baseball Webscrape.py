# %%
import requests
from bs4 import BeautifulSoup
from pybaseball import pitching_stats_range
import pandas as pd
import time
import random

# %%
# Get request for all the pitchers that played on a sepecifc date
url = "https://baseballsavant.mlb.com/statcast_search"

lookup_date = "2025-03-27"

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

# %%

## Fetching a request of each player on the player_names list
pitching_df = pd.DataFrame()

# Making new parameters for each player on the daily list
for player in player_names:
    params_per_player = {
        "hfGT": "R|",
        "hfSea": "2025|",
        "player_type": "pitcher",
        "game_date_gt": lookup_date,
        "game_date_lt": lookup_date,
        "pitchers_lookup[]": player['player_id'],
        "group_by": "name",
        "min_pitches": 0,
        "min_results": 0,
        "min_pas": 0,
        "sort_col": "pitches",
        "sort_order": "desc",
        "type": "details",
        "player_id": player['player_id']
    }

    response = requests.get(url, params=params_per_player, headers=headers, timeout=10)
    time.sleep(random.uniform(1.46, 2.13)) 
    response.raise_for_status()

    table = pd.read_html(response.text)
    df = table[0]
    df = df[['Date', 'Pitcher', 'Pitch', 'MPH', 'Zone', 'Pitch Result', 'PA Result', 'Count', 'Inning', 'Spin Rate']]
    # Creating additional columns
    df['Player ID'] = player["player_id"] # Adding player ID to each row for the player
    df['Pitch Count'] = range(len(df), 0, -1) #Adding the pitch count for the appearence
    

    pitching_df = pd.concat([pitching_df, df], ignore_index=True)

# %%
## Cleaning and formatting the data
# Formating all columns
pitching_df.columns = pitching_df.columns.str.lower().str.replace(' ','_')
# Miscellaneous
pitching_df['inning'] = pitching_df['inning'].str.extract(r'(\d+)') #Extracting only the inning number from the inning column
pitching_df['pitcher_hand'] = pitching_df['pitcher'].str.extract(r'\((R|L)\)') #Extracing the pitchers handedness
pitching_df['pitcher'] = pitching_df["pitcher"].str.replace(r"\((R|L)\)", "", regex=True).str.strip() 
# Pitch Results
p_result_map = {'Blocked Ball':'Ball', 'Foul Bunt':'Foul', 'Foul Tip':'Foul', 'Hit By Pitch':'HBP', 
                'Missed Bunt':'Swinging Strike', 'Swinging Strike Blocked':'Swinging Strike'} # Mapping pitch results to more unified categories
pitching_df['pitch_result'] = pitching_df['pitch_result'].replace(p_result_map) # Applying the map
pitching_df['pitch_result'] = pitching_df['pitch_result'].str.lower().str.replace(' ','_') # Formating values to be lowercase and underscore the spaces
# pitching_df['pitch_result'] = pitching_df[pitching_df['pitch_result'] != 'Automatic Ball']
#Plate Apperance Results into categories
pitching_df['pa_result'] = pitching_df['pa_result'].str.lower()
# Single string lists
strikout_str = ['strikes out', 'called out']
walked_str = ['walks']
inplayout_str = ['flied out', 'grounds out', 'lines out', 'pops out', 
                 'sacrifice fly', 'sacrifice bunt', 'error']
firstbase_str = ['singles']
secondbase_str = ['doubles', 'ground-rule double']
thirdbase_str = ['triples']
homerun_str = ['homers']



# %%
print(pitching_df[pitching_df['pa_result'].str.contains("error", na=False)]["pa_result"].tolist())






# %%
