from league_BE.api.models.start_capture import StartCapture
from league_BE.fetch_data.live_data_handler import LiveDataHandler
from league_BE.fetch_data.fetch_live_data import FetchLiveData

from league_BE import consts
from fastapi import FastAPI
import uvicorn
from fastapi import BackgroundTasks
from typing import Any
from fastapi.responses import Response

app = FastAPI()

app.live_data_handler =  LiveDataHandler()

# TODO: look at streaming this
@app.post("/start_capture")
async def start_capture(start_capture_obj: StartCapture,background_tasks: BackgroundTasks):
    message = F"Received request to start capturing data for match_id: {start_capture_obj.match_id} starting at {start_capture_obj.match_min_start_time}"
    print(message)

    app.live_data_handler.set_match_details(start_capture_obj.match_id, start_capture_obj.match_min_start_time)
    fetch_live_data = FetchLiveData(app.live_data_handler)
    background_tasks.add_task(fetch_live_data.start_capture)

    return {"message": "Started capturing data in the background"}

@app.get("/team/gold")
async def get_team_gold():
    message = F"Received request to get_team_gold"
    print(message)

    if not app.live_data_handler.match_ongoing():
        return {"message": "Match not ongoing"}

    return DataFrameJSONResponse(app.live_data_handler.get_all_team_gold())

class DataFrameJSONResponse(Response):
    media_type = "application/json"

    def render(self, content: Any) -> bytes:
        return content.to_json(orient="records", date_format='iso').encode("utf-8")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)