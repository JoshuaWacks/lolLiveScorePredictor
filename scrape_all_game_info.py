import requests
from bs4 import BeautifulSoup 

import pandas as pd

class GameScraper:

    GAME_INFO_BASE_URL = 'https://gol.gg/game/stats/'
    GAME_INFO_HEADERS = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0"
    }

    SEASON_OVERVIEW_BASE_URL = 'https://gol.gg/tournament/tournament-stats/'
    SEASON_MATCH_LIST_BASE_URL = 'https://gol.gg/tournament/tournament-matchlist/'

    def __init__(self, league, season,season_format,year,gol_year_format,
                 scrape_game_info = False,
                 scrape_champ_select = False,
                 scrape_team_stats = False):

        self.league = league
        self.season = season
        self.season_format = season_format
        self.year = year
        self.gol_year_format = gol_year_format
        
        self.scrape_game_info = scrape_game_info
        self.scrape_champ_select = scrape_champ_select
        self.scrape_team_stats = scrape_team_stats

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
            break
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
        print(number_of_games_in_season)
        # assert len(self.all_season_games) == number_of_games_in_season

        if self.scrape_game_info:
            self.overall_game_info_df = pd.DataFrame(columns=['gol_game_num','league','season','year','date','week','patch','format','game_in_format','game_length(min)','game_length(s)','red_team','blue_team','red_team_outcome','blue_team_outcome','winner','mvp'])

        if self.scrape_champ_select:
            self.champ_select_df = pd.DataFrame(columns=['gol_game_num',
                                                    'blue_ban_0','blue_ban_1','blue_ban_2','blue_ban_3','blue_ban_4',
                                                    'blue_top','blue_jungle','blue_mid','blue_bot','blue_supp',
                                                    'red_ban_0','red_ban_1','red_ban_2','red_ban_3','red_ban_4',
                                                    'red_top','red_jungle','red_mid','red_bot','red_supp'
                                                    ])
            
        if self.scrape_team_stats:
            self.overall_team_info_df = pd.DataFrame(columns=['gol_game_num',
                                                    'blue_gold','blue_kills','blue_towers','blue_first_tower','blue_first_blood',
                                                    'blue_hextech_drake','blue_mountain_drake','blue_infernal_drake','blue_ocean_drake','blue_cloud_drake','blue_chemtech_drake',
                                                    'blue_void_grubs',
                                                    'blue_rift_herald', #TODO
                                                    'blue_plates','blue_plates_top','blue_plates_mid','blue_plates_bot',
                                                    'blue_wards_destroyed','blue_wards_placed',
                                                    'red_gold','red_kills','red_towers','red_first_tower','red_first_blood',
                                                    'red_hextech_drake','red_mountain_drake','red_infernal_drake','red_ocean_drake','red_cloud_drake','red_chemtech_drake',
                                                    'red_void_grubs',
                                                    'red_rift_herald', #TODO
                                                    'red_plates','red_plates_top','red_plates_mid','red_plates_bot',
                                                    'red_wards_destroyed','red_wards_placed'
                                                    
                                                    ])
            # TODO get stats from an individual to a team level. Total deaths, assists, vision etc
            
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
    
    def _get_game_info(self,game_num,soup):

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
    
    def _get_champs(self,soup):
        game_champs = dict()
        
        i = 1
        for row in soup.find_all('div',class_ = 'col-10'):
            for champ in row.find_all('a'):
                game_champs[self.champ_select_df.columns[i]] = champ.img.get("alt")
                i = i+1

        return game_champs
    
    def _get_drake_name(self,team,drake):
        return team+'_'+drake.strip().lower().split(' ')[0]+'_drake'
    
    def _convert_gold(self,gold):
        formatted_gold = int(gold[0:2] + gold[3] + '00')
        return formatted_gold
    
    def _get_ward_info(self,ward_info):
        blue_team_wards_destroyed = int(ward_info[ward_info.rindex('data :')+8:ward_info.rindex('data :')+10])
        blue_team_wards_placed = int(ward_info[ward_info.rindex('data :')+11:ward_info.rindex('data :')+14])

        red_team_wards_destroyed = int(ward_info[ward_info.index('data :')+8:ward_info.index('data :')+10])
        red_team_wards_placed = int(ward_info[ward_info.index('data :')+11:ward_info.index('data :')+14])

        return blue_team_wards_destroyed,blue_team_wards_placed,red_team_wards_destroyed,red_team_wards_placed
    
    def _get_overall_team_stats(self,soup):
        team_stats = dict()

        for col in self.overall_team_info_df.columns:
            team_stats[col] = 0

        team_stats['blue_kills'] = soup.find_all('div',class_='col-12 col-sm-6')[0].find_all('div',class_ = 'col-2')[0].text.strip()
        team_stats['blue_towers'] = soup.find_all('div',class_='col-12 col-sm-6')[0].find_all('div',class_ = 'col-2')[1].text.strip()

        drake_info = soup.find_all('div',class_='col-12 col-sm-6')[0].find_all('div',class_ = 'col-2')[2].find_all('img')[1:]
        for d in drake_info:
            drake_name = self._get_drake_name('blue',d.get('alt'))
            team_stats[drake_name] = team_stats[drake_name] + 1

        team_stats['blue_barons'] = soup.find_all('div',class_='col-12 col-sm-6')[0].find_all('div',class_ = 'col-2')[3].text.strip()

        gold_info = soup.find_all('div',class_='col-12 col-sm-6')[0].find_all('div',class_ = 'col-2')[4].text.strip()

        team_stats['blue_gold'] = self._convert_gold(gold_info)

        team_stats['blue_void_grubs']  = int(soup.find_all('div',class_='row pb-3')[1].find_all('div')[1].text.strip())
        team_stats['blue_plates']  = int(soup.find_all('div',class_='row pb-3')[2].find_all('div')[1].text.strip())
        team_stats['blue_plates_top']  = int(soup.find_all('div',class_='row pb-3')[3].find_all('div')[1].text.strip())
        team_stats['blue_plates_mid']  = int(soup.find_all('div',class_='row pb-3')[4].find_all('div')[1].text.strip())
        team_stats['blue_plates_bot']  = int(soup.find_all('div',class_='row pb-3')[5].find_all('div')[1].text.strip())

        ward_info = soup.find_all('script')[-4].text

        blue_team_wards_destroyed,blue_team_wards_placed,red_team_wards_destroyed,red_team_wards_placed = self._get_ward_info(ward_info)
        team_stats['blue_wards_destroyed'] = blue_team_wards_destroyed
        team_stats['blue_wards_placed'] = blue_team_wards_placed
        team_stats['red_wards_destroyed'] = red_team_wards_destroyed
        team_stats['red_wards_placed'] = red_team_wards_placed

        team_stats['red_kills'] = soup.find_all('div',class_='col-12 col-sm-6')[1].find_all('div',class_ = 'col-2')[0].text.strip()
        team_stats['red_towers'] = soup.find_all('div',class_='col-12 col-sm-6')[1].find_all('div',class_ = 'col-2')[1].text.strip()

        drake_info = soup.find_all('div',class_='col-12 col-sm-6')[1].find_all('div',class_ = 'col-2')[2].find_all('img')[1:]
        for d in drake_info:
            drake_name = self._get_drake_name('red',d.get('alt'))
            team_stats[drake_name] = team_stats[drake_name] + 1

        team_stats['red_barons'] = soup.find_all('div',class_='col-12 col-sm-6')[1].find_all('div',class_ = 'col-2')[3].text.strip()

        gold_info = soup.find_all('div',class_='col-12 col-sm-6')[1].find_all('div',class_ = 'col-2')[4].text.strip()

        team_stats['red_gold'] = self._convert_gold(gold_info)

        team_stats['red_void_grubs']  = int(soup.find_all('div',class_='row pb-3')[1].find_all('div')[2].text.strip())
        team_stats['red_plates']  = int(soup.find_all('div',class_='row pb-3')[2].find_all('div')[2].text.strip())
        team_stats['red_plates_top']  = int(soup.find_all('div',class_='row pb-3')[3].find_all('div')[2].text.strip())
        team_stats['red_plates_mid']  = int(soup.find_all('div',class_='row pb-3')[4].find_all('div')[2].text.strip())
        team_stats['red_plates_bot']  = int(soup.find_all('div',class_='row pb-3')[5].find_all('div')[2].text.strip())

        return team_stats

    def scrape_info(self):
        self._setup()

        for game_num in self.all_season_games:
            print(game_num)
            game_info_url = F'{self.GAME_INFO_BASE_URL}{game_num}/page-game/'
            page = requests.get(game_info_url, headers=self.GAME_INFO_HEADERS)
            soup = BeautifulSoup(page.content, 'html.parser')

            if self.scrape_game_info:
                new_record = self._get_game_info(game_num,soup)
                self.overall_game_info_df = pd.concat([self.overall_game_info_df,pd.DataFrame([new_record])],ignore_index=True)
            
            if self.scrape_champ_select:
                game_champs = self._get_champs(game_num,soup)
                game_champs['gol_game_num'] = game_num
                self.champ_select_df = pd.concat([self.champ_select_df,pd.DataFrame([game_champs])],ignore_index=True)

            if self.scrape_team_stats:
                team_stats = self._get_overall_team_stats(soup)
                team_stats['gol_game_num'] = game_num
                self.overall_team_info_df = pd.concat([self.overall_team_info_df,pd.DataFrame([team_stats])],ignore_index=True)
            break


# TODO first blood and first tower