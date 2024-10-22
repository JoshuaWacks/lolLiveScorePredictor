import requests

import consts
from tiny_bird_interface.api.data_pipe import DataPipe
from tiny_bird_interface.api.data_souce import DataSource

class CleanUpTb:

    def __init__(self, data_pipe_in:DataPipe, data_source_in:DataSource):

        self.data_pipe = data_pipe_in
        self.data_source = data_source_in

    def clean_up(self):

        self.data_pipe.delete_all_pipes()
        self.data_source.delete_all_datasources()

if __name__ == '__main__':

    data_source = DataSource()
    data_pipe = DataPipe(data_source=data_source)

    clean_up_obj = CleanUpTb(data_pipe_in=data_pipe,data_source_in=data_source)
    clean_up_obj.clean_up()