import requests
from bs4 import BeautifulSoup 

import pandas as pd

class OverallGameInfo:

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

        self.overall_game_info_df = pd.DataFrame(columns=['gol_game_num','league','season','year','date','week','patch','format','game_in_format','game_length(min)','game_length(s)','red_team','blue_team','red_team_outcome','blue_team_outcome','winner','mvp'])


    def _get_game_date(self,soup):
        # Getting the date and week game was played
        obj = soup.find("div", class_="col-12 col-sm-5 text-right")
        date = obj.text.split(" ")[0].strip()
        week = obj.text.split(" ")[1][1:-1].strip()

        return date,week
    
    def _get_game_length(self,soup):
        # Getting the length of the game
        obj = soup.find("div", class_="col-6 text-center")
        game_length_minutes = obj.find("h1").text.strip()
        game_length_split = game_length_minutes.split(":")

        if len(game_length_split) == 2: #Only minutes and seconds
            game_length_seconds = int(game_length_split[0])*60 + int(game_length_split[1])
        else: #Hours, minutes and seconds
            game_length_seconds = int(game_length_split[0])*3600+int(game_length_split[1])*60 + int(game_length_split[2])

        return game_length_minutes,game_length_seconds
    
    def _get_game_patch(self,soup):
    
        # Getting the game patch
        obj = soup.find("div", class_="col-3 text-right")
        game_patch = obj.text[2:].strip()

        return game_patch
    
    def _get_game_format(self,game_num,soup):

        game_info_url = F'{self.GAME_INFO_BASE_URL}{game_num}/page-summary/'
        page = requests.get(game_info_url, headers=self.GAME_INFO_HEADERS)
        new_soup = BeautifulSoup(page.content, 'html.parser')

        game_format = new_soup.find('div',class_ = 'col-4 col-sm-2 text-center').find('h1').text
        game_in_series = soup.find(id = 'gameMenuToggler').find('li',class_ = 'nav-item game-menu-button-active').find('a').text[-1]

        return game_format,game_in_series
    
    def _get_teams_and_outcomes(self,soup):
        obj = soup.find("div", class_="col-12 blue-line-header")
        blue_team = obj.text.split('-')[0].strip()
        blue_team_outcome = obj.text.split('-')[1].strip()

        obj = soup.find("div", class_="col-12 red-line-header")
        red_team = obj.text.split('-')[0].strip()
        red_team_outcome = obj.text.split('-')[1].strip()

        return red_team,red_team_outcome,blue_team,blue_team_outcome
    
    def _get_required_info(self,game_num,soup):

        date,week = self._get_game_date(soup)

        game_patch = self._get_game_patch(soup)

        game_format,game_in_series = self._get_game_format(game_num,soup)

        game_length_minutes,game_length_seconds = self._get_game_length(soup)

        red_team,red_team_outcome,blue_team,blue_team_outcome = self._get_teams_and_outcomes(soup)

        if red_team_outcome == 'WIN':
            winner = red_team
            loser = blue_team
        else:
            loser = red_team
            winner = blue_team

        new_record = {
            'gol_game_num':game_num,
            'league':self.league,
            'season':self.season,
            'season_format':self.season_format,
            'year':self.year,
            'date':pd.Timestamp(date),
            'week': week,
            'patch':game_patch,
            'format': game_format,
            'game_in_format': game_in_series, #Start counting from 1 here for the standard they use
            'game_length(min)': game_length_minutes,
            'game_length(s)':game_length_seconds,
            'red_team':red_team,
            'blue_team':blue_team,
            'red_team_outcome':red_team_outcome,
            'blue_team_outcome':blue_team_outcome,
            'winner': winner,
            'loser':loser,
            'mvp':'',#TODO
        }

        return new_record
    
    def get_overall_game_info(self):
        self._setup()

        for game_num in self.all_season_games:
    
            game_info_url = F'{self.GAME_INFO_BASE_URL}{game_num}/page-game/'
            page = requests.get(game_info_url, headers=self.GAME_INFO_HEADERS)
            soup = BeautifulSoup(page.content, 'html.parser')

            new_record = self._get_required_info(game_num,soup)
            self.overall_game_info_df = pd.concat([self.overall_game_info_df,pd.DataFrame([new_record])],ignore_index=True)
        # self.overall_game_info_df['index'] = self.overall_game_info_df.index


        return self.overall_game_info_df