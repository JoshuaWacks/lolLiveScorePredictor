import pandas as pd

class LiveDataHandler:
    # Info that does not change about the game

    def __init__(self):

        self.match_min_start_time = None
        self.match_id = None
        self.fixed_info = None
        self.game_start_time = None

        self.game_state = "in_game"

        self.match_data = pd.DataFrame()

    def match_ongoing(self):

        return self.match_id is not None and self.match_min_start_time is not None

    def set_match_details(self, match_id,match_min_start_time):
        # The info on what match we are getting
        self.match_id =  match_id
        self.match_min_start_time =  match_min_start_time

    def add_match_data(self,timestamp_data):
        self.match_data = pd.concat([self.match_data, timestamp_data], ignore_index=True, sort=False)
        print(len(self.match_data))

    def get_all_team_gold(self):

        required_fields = ['blue_team_total_gold','red_team_total_gold','time_in_game']
        return self.match_data[required_fields]