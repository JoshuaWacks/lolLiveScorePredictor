import requests
from bs4 import BeautifulSoup 

import pandas as pd

# TODO get stats from an individual to a team level. Total deaths, assists,damage, vision etc
# Add team names to dataframes will be easier for analysis not just red vs blue
# This may be easier once everything is downloaded and in dataframes

# TODO features I want to create: deaths/min

class PlayerScraper:

    def __init__(self):
        self.payer_stats_df = pd.DataFrame()

    def get_all_player_stats(self, overall_soup,gol_game_num):
        self.overall_soup = overall_soup
        self.gol_game_num = gol_game_num

        stats_table = self.overall_soup.find('table')

        for i,champ in enumerate(stats_table.find_all('th')[1:]):
            player_stats = dict()
            player_stats['gol_game_num'] = self.gol_game_num
            player_stats['champ'] = champ.find('img').get('alt').strip()

            player_stats['team'] = 'blue' if i < 5 else 'red'
            self.payer_stats_df = pd.concat([self.payer_stats_df, pd.DataFrame([player_stats])], ignore_index=True)

        
        for stat in stats_table.find_all('tr')[1:]:
            key = stat.find('td').text.strip().lower()
            for index,info in enumerate(stat.find_all('td')[1:]):

                if key == 'player' or key == 'role':
                    self.payer_stats_df.loc[index,key] = info.text.strip()
                    continue

                if key == 'kda':
                    self.payer_stats_df.iloc[index][key] = (self.payer_stats_df.iloc[index]['kills'] + self.payer_stats_df.iloc[index]['assists'])/ float(self.payer_stats_df.iloc[index]['deaths'])
                    continue

                if '%' in key:
                    self.payer_stats_df.iloc[index][key] = float(info.text.strip()[:-1])
                    continue

                if info.text.strip() == '':
                    self.payer_stats_df.iloc[index][key] = 0
                    continue

                self.payer_stats_df.iloc[index][key] = float(info.text.strip())   
    
        return self.payer_stats_df