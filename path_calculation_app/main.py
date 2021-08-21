from fastapi import FastAPI

from functions_redis import input_check, dijkstra, path_output


app = FastAPI()


@app.get("/")
async def read_root():
    return "Hello! For path calculation use 127.0.0.1:8001/calculate_path?start=<>&finish=<>"


@app.get("/input_check")
async def read_item(station: str):
    stations = input_check(station)
    return stations


@app.get("/calculate_path")
async def read_item(start: str, finish: str):
    duration, stations = dijkstra(start, finish)
    text = path_output(duration, stations)
    return text
