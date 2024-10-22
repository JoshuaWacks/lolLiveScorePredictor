from league_BE.fetch_data.fetch_live_data import FetchLiveData

class BaseTransformations:

    def __init__(self, match_id,match_min_start_time):

        self.live_data = FetchLiveData(match_id,match_min_start_time)
        self.live_data.start_capture()

    def get_all_team_gold(self):
        self.live_data.match_data