import requests
import json
import os
from dotenv import load_dotenv

import consts
from tiny_bird_interface.models.pipe import Pipe



class DataPipe:

    all_pipes = []

    def __init__(self,data_source):

        load_dotenv()
        self.data_source = data_source
        self.create_pipe_templates()

        self.existing_pipes = self.get_all_pipes()

    def get_all_pipes(self):

        full_url = consts.BaseConstants.BASE_TB_URL + 'pipes'
        request_result = requests.get(full_url,
                                       params={
                                           'token': os.environ.get('TB_TOKEN')
                                       }
                                       )
        return request_result.json()['pipes']


    def create_pipe(self,pipe_name,sql_transformation):

        for pipe in self.existing_pipes:
            if pipe_name == pipe['name']:
                print("Pipe already exists skipping")
                return pipe['nodes'][0]['name']

        full_url = consts.BaseConstants.BASE_TB_URL + 'pipes'
        request_result = requests.post(full_url,
                                       params={
                                           'token': os.environ.get('TB_TOKEN'),
                                           'name':pipe_name,
                                           'sql':sql_transformation
                                       },
                                       )
        print(request_result.status_code)
        print(request_result.text)

        return request_result.json()[0]['name']

    # No need to run this as the data source is cleared and then the pipe will only return new data
    def delete_pipe(self,pipe_name):

        full_url = consts.BaseConstants.BASE_TB_URL + 'pipes'

        request_result = requests.delete(full_url,
                                       params={
                                           'token': os.environ.get('TB_TOKEN'),
                                           'name': pipe_name
                                       }
                                       )
        print(request_result.status_code)
        print(request_result.text)

    def enable_pipe_as_endpoint(self,pipe_name,node_name):

        full_url = F"{consts.BaseConstants.BASE_TB_URL}pipes/{pipe_name}/nodes/{node_name}/endpoint"
        request_result = requests.post(full_url,
                                       params={
                                           'token': os.environ.get('TB_TOKEN')
                                       }
                                       )
        print(request_result.status_code)
        print(request_result.text)

    def create_pipe_templates(self):

        select_all_pipe = Pipe(pipe_name=F'SELECT_ALL_PIPE_{self.data_source}',
                               sql_transformation=F"SELECT * FROM {self.data_source}")

        self.all_pipes.append(select_all_pipe)
