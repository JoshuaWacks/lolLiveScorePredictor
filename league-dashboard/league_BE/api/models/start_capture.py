from pydantic import BaseModel

class StartCapture(BaseModel):
    match_id:int
    match_min_start_time:str