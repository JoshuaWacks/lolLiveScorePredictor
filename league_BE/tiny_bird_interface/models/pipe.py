from pydantic import BaseModel

class Pipe(BaseModel):

    pipe_name: str
    sql_transformation: str