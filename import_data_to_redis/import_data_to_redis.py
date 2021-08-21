from rejson import Client, Path
import yaml
from decouple import config


REDIS_HOST = config("REDIS_HOST")
REDIS_PORT = config("REDIS_PORT")


def data_import(filename: str):
    with open(filename) as f:
        return yaml.load(f)


graph = data_import("data/data.yaml")
all_stations = []

rj = Client(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

for station, data in graph.items():
    rj.jsonset(station, Path.rootPath(), data)
    all_stations.append(station)

rj.jsonset("all_stations", Path.rootPath(), all_stations)
