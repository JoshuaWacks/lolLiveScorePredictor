import pandas as pd

class ChampIndexHandler:

    def __init__(self, file_version):

        self.file_version = file_version

        self.file_path =  F"static_game_data/raw_data/gameData{self.file_version}/champs.csv"

        self.champ_df = pd.read_csv(self.file_path)

        # Assign index as a column, and only get name and index
        self.champ_df['champ_index'] = self.champ_df.index
        self.champ_df = self.champ_df[['name','champ_index']]

    def get_champ_index(self,champ_name):

        return self.champ_df[self.champ_df['name'] == champ_name].champ_index.index[0]