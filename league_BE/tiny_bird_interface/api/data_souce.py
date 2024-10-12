import requests
import json
import os
from dotenv import load_dotenv
from datetime import datetime
from pandas_to_pydantic import dataframe_to_pydantic

from tiny_bird_interface.models.frame_request import FrameRequest
import consts

class DataSource:

    def __init__(self):
        load_dotenv()

    def post_data(self,data_source_name,processed_frame):

        frame_request_object = dataframe_to_pydantic(processed_frame, FrameRequest).model_dump()

        r = requests.post(consts.BaseConstants.BASE_TB_POST_URL,
                          params={
                              'name': data_source_name,
                              'token': os.environ.get('TB_TOKEN'),
                          },
                          data=json.dumps(frame_request_object)
                          )
        print(r.status_code)
        print(r.text)