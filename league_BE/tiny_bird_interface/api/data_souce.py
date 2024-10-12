import requests
import json
import os
from dotenv import load_dotenv
from datetime import datetime
from pandas_to_pydantic import dataframe_to_pydantic

from tiny_bird_interface.models.frame_request import FrameRequest
import consts

def poll_delete_job(url):

    request_result = requests.get(url,
                                   params={
                                       'token': os.environ.get('TB_TOKEN'),
                                   }
                                   )

    return request_result.json()['status']

class DataSource:

    def __init__(self):
        load_dotenv()

    def post_data(self,data_source_name,processed_frame):

        frame_request_object = dataframe_to_pydantic(processed_frame, FrameRequest).model_dump()[0]

        request_result = requests.post(consts.BaseConstants.BASE_TB_POST_URL,
                          params={
                              'name': data_source_name,
                              'token': os.environ.get('TB_TOKEN'),
                              'mode':'create'
                          },
                          data=json.dumps(frame_request_object)
                          )
        print(request_result.status_code)
        print(request_result.text)

    def delete_existing_data_source(self,data_source_name):

        full_delete_url = F"{consts.BaseConstants.BASE_TB_DELETE_URL}/{data_source_name}/delete"

        request_result = requests.post(full_delete_url,
                                       params={
                                           'delete_condition': 'True',
                                           'token': os.environ.get('TB_TOKEN'),
                                       },
                                       )

        if request_result.status_code == 201 and request_result.json()['job']['status'] == 'waiting':
            delete_job_url = request_result.json()['job_url']
            while poll_delete_job(delete_job_url) != 'done':
                print("Waiting for old datasource to be delete")

        print(F"Old datasource {data_source_name} cleared")