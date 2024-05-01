import requests
from bs4 import BeautifulSoup 

import pandas as pd

class ChampSelect:

    GAME_INFO_BASE_URL = 'https://gol.gg/game/stats/'
    GAME_INFO_HEADERS = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0"
    }
    
    SEASON_OVERVIEW_BASE_URL = 'https://gol.gg/tournament/tournament-stats/'
    SEASON_MATCH_LIST_BASE_URL = 'https://gol.gg/tournament/tournament-matchlist/'

    def __init__(self, league, season,season_format,year,gol_year_format):

        self.league = league
        self.season = season
        self.season_format = season_format
        self.year = year
        self.gol_year_format = gol_year_format

    def _get_game_links_in_season(self,soup):

        links = soup.find_all('td',class_ = 'text-left')
        all_season_games = []
        for l in links:
            base_game_num = int(l.find('a').get("href").split('/')[-3].strip())

            game_info_url = F'{self.GAME_INFO_BASE_URL}{base_game_num}/page-summary/'
            page = requests.get(game_info_url, headers=self.GAME_INFO_HEADERS)
            new_soup = BeautifulSoup(page.content, 'html.parser')

            num_games = len(new_soup.find_all('div',class_='row pb-1'))
            all_season_games = all_season_games+ list(range(base_game_num,base_game_num+num_games))

        return all_season_games
    
    def _setup(self):
    
        SEASON_MATCH_LIST_URL = F'{self.SEASON_MATCH_LIST_BASE_URL}{self.league}%20{self.season}%20{self.season_format}%{self.gol_year_format}/'

        page = requests.get(SEASON_MATCH_LIST_URL, headers=self.GAME_INFO_HEADERS)
        soup = BeautifulSoup(page.content, 'html.parser') 

        self.all_season_games = self._get_game_links_in_season(soup)

        SEASON_OVERVIEW_URL = F'{self.SEASON_OVERVIEW_BASE_URL}{self.league}%20{self.season}%20{self.season_format}%{self.gol_year_format}/'

        page = requests.get(SEASON_OVERVIEW_URL, headers=self.GAME_INFO_HEADERS)
        soup = BeautifulSoup(page.content, 'html.parser') 
        number_of_games_in_season = int(soup.find("td", class_="text-center").text)

        assert len(self.all_season_games) == number_of_games_in_season

        self.champ_select_df = pd.DataFrame(columns=['gol_game_num',
                                                          'blue_ban_0','blue_ban_1','blue_ban_2','blue_ban_3','blue_ban_4',
                                                          'blue_top','blue_jungle','blue_mid','blue_bot','blue_supp',
                                                          'red_ban_0','red_ban_1','red_ban_2','red_ban_3','red_ban_4',
                                                          'red_top','red_jungle','red_mid','red_bot','red_supp'
                                                          ])
        
    def _get_champs(self,soup):
        game_champs = dict()
        
        i = 1
        for row in soup.find_all('div',class_ = 'col-10'):
            for champ in row.find_all('a'):
                game_champs[self.champ_select_df.columns[i]] = champ.img.get("alt")
                i = i+1

        return game_champs
    
    def get_champ_select(self):
        self._setup()

        for game_num in self.all_season_games:
    
            game_info_url = F'{self.GAME_INFO_BASE_URL}{game_num}/page-game/'
            page = requests.get(game_info_url, headers=self.GAME_INFO_HEADERS)
            soup = BeautifulSoup(page.content, 'html.parser')

            game_champs = self._get_champs(game_num,soup)
            game_champs['gol_game_num'] = game_num

            self.champ_select_df = pd.concat([self.champ_select_df,pd.DataFrame([game_champs])],ignore_index=True)
        # self.overall_game_info_df['index'] = self.overall_game_info_df.index
        return self.champ_select_df
