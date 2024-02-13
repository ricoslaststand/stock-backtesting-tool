from fastapi import FastAPI

from app.strategies import AvgComparedToXDayAvgStrategy

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": AvgComparedToXDayAvgStrategy.__name__}
