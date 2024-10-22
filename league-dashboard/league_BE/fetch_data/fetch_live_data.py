import league_BE.consts as consts
from league_BE.static_game_data.handle_static_data.champ_index_handler import ChampIndexHandler
from league_BE.fetch_data.live_data_handler import LiveDataHandler

import requests
import pandas as pd

def extract_fixed_info(json_data):

    # Extracting the fixed data in the match from the raw json
    ret_data = dict()
    try:
        game_start_time = get_unix_time(json_data['frames'][0]['rfc460Timestamp'])
    except:
        raise Exception("Invalid game ID or start time")


    for i,pos in enumerate(['top','jungle','mid','bot','supp']):
        ret_data[F'blue_{pos}_champ'] = json_data['gameMetadata']['blueTeamMetadata']['participantMetadata'][i]['championId']
        ret_data[F'red_{pos}_champ'] = json_data['gameMetadata']['redTeamMetadata']['participantMetadata'][i]['championId']

    return ret_data,game_start_time

def encode_dragons(team, info):

    # Take the raw info on the drakes taken and sum the type of each taken for that team
    drake_types = ['ocean_drakes', 'cloud_drakes', 'mountain_drakes', 'chemtech_drakes', 'infernal_drakes',
                  'hextech_drakes', 'elder_drakes']

    ret_data = dict()
    for drake in drake_types:
        ret_data[F"{team}_{drake}"] = 0
    for drake_taken in info:
        k = F"{team}_{drake_taken}_drakes"
        ret_data[k] = ret_data[k] + 1

    return ret_data

def extract_changing_info(json_data):

    # Extract the info that is changing on a time step basis from raw data

    ret_data = dict()

    for clr in ['blue','red']:
        ret_data[F'{clr}_team_total_gold'] = json_data[F'{clr}Team']['totalGold']
        ret_data[F'{clr}_team_inhibitors'] = json_data[F'{clr}Team']['inhibitors']
        ret_data[F'{clr}_team_towers'] = json_data[F'{clr}Team']['towers']
        ret_data[F'{clr}_team_barons'] = json_data[F'{clr}Team']['barons']
        ret_data[F'{clr}_team_total_kills'] = json_data[F'{clr}Team']['totalKills']
        ret_data.update(encode_dragons(F'{clr}_team',json_data[F'{clr}Team']['dragons']))

        for i,pos in enumerate(['top','jungle','mid','bot','supp']):
            ret_data[F'{clr}_{pos}_total_gold'] = json_data[F'{clr}Team']['participants'][i]['totalGold']
            ret_data[F'{clr}_{pos}_level'] = json_data[F'{clr}Team']['participants'][i]['level']
            ret_data[F'{clr}_{pos}_kills'] = json_data[F'{clr}Team']['participants'][i]['kills']
            ret_data[F'{clr}_{pos}_deaths'] = json_data[F'{clr}Team']['participants'][i]['deaths']
            ret_data[F'{clr}_{pos}_assists'] = json_data[F'{clr}Team']['participants'][i]['assists']
            ret_data[F'{clr}_{pos}_creep_score'] = json_data[F'{clr}Team']['participants'][i]['creepScore']
            ret_data[F'{clr}_{pos}_current_health'] = json_data[F'{clr}Team']['participants'][i]['currentHealth']
            ret_data[F'{clr}_{pos}_max_health'] = json_data[F'{clr}Team']['participants'][i]['maxHealth']


    return ret_data

def increment_time(start_time,time_delta):

    conv_time = pd.to_datetime(start_time) + pd.to_timedelta(time_delta, unit='s')
    conv_time = conv_time.round('10s')
    return "{}T{}.000Z".format(str(conv_time.date()),str(conv_time.time()))

def get_unix_time(value):
    try:
        return (pd.to_datetime(value, format='%Y-%m-%dT%H:%M:%S.%fZ') - pd.Timestamp("1970-01-01")) // pd.Timedelta(
            '1s')
    except ValueError:
        return (pd.to_datetime(value, format='%Y-%m-%dT%H:%M:%SZ') - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')



class FetchLiveData:

    def __init__(self, live_data_handler:LiveDataHandler):

        self.live_data_handler = live_data_handler

        # The fixed static data we need to compare it to
        self.champ_index_handler = ChampIndexHandler(file_version=consts.BaseConstants.CURRENT_STATIC_DATA_VERSION)


    def assign_champ_index(self,df):
        for clr in ['blue', 'red']:
            for i, pos in enumerate(['top', 'jungle', 'mid', 'bot', 'supp']):
                col = F"{clr}_{pos}_champ"

                df[col] = df[col].apply(lambda x: self.champ_index_handler.get_champ_index(x))

    def get_dynamic_frame_data(self,frame,delta_info_prev):

        delta_info_curr = extract_changing_info(frame)

        # If nothing has happened between frames we can skip
        if delta_info_prev is not None and delta_info_curr == delta_info_prev:
            return None
        delta_info_curr.update(self.live_data_handler.fixed_info)

        delta_info_curr['time_in_game'] = get_unix_time(frame['rfc460Timestamp']) - self.live_data_handler.game_start_time

        df = pd.DataFrame(delta_info_curr, index=[0])
        self.assign_champ_index(df)

        return df

    def get_data_at_timestamp(self,time_stamp):

        # An array of data at each frame
        temp_df = pd.DataFrame()
        timestamped_url = consts.BaseConstants.BASE_LIVE_URL_FEED.format(self.live_data_handler.match_id,time_stamp)
        raw_data = requests.get(timestamped_url)

        if raw_data.status_code == 204:  # No content returned
            return temp_df,"in_game"

        data = raw_data.json()
        if self.live_data_handler.game_start_time is None:
            self.live_data_handler.fixed_info,self.live_data_handler.game_start_time = extract_fixed_info(data)
        delta_info_prev = None

        for frame in data['frames']:

            processed_frame = self.get_dynamic_frame_data(frame,delta_info_prev)

            # Posting data to tb here
            # if processed_frame is not None:

            temp_df = pd.concat([ temp_df, processed_frame], ignore_index=True, sort=False)
            delta_info_prev = extract_changing_info(frame)

        temp_df.drop_duplicates(inplace=True)
        return temp_df,data['frames'][-1]['gameState']

    def start_capture(self):

        game_state = "in_game"
        time_elapsed = 0
        time_stamp = increment_time(self.live_data_handler.match_min_start_time,time_elapsed)
        while game_state == "in_game" or game_state == "paused":

            timestamp_data,game_state = self.get_data_at_timestamp(time_stamp)
            self.live_data_handler.add_match_data(timestamp_data)
            time_elapsed = time_elapsed + consts.BaseConstants.TIME_DELTA_S
            time_stamp = increment_time(self.live_data_handler.match_min_start_time,time_elapsed)
            print(time_stamp)

# if __name__ == '__main__':
#
#     min_start_time = pd.Timestamp(consts.BaseConstants.TEST_MIN_START_TIME)
#
#     fld = FetchLiveData(consts.BaseConstants.TEST_MATCH_ID,min_start_time)
#     fld.start_capture()