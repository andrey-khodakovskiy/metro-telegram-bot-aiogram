from string import capwords
import re
from rejson import Client, Path
from typing import List, Dict, Tuple, Any
from decouple import config


REDIS_HOST = config("REDIS_HOST")
REDIS_PORT = config("REDIS_PORT")
rj = Client(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


def set_cost_add_to_dict(name: str, cost: int) -> Dict[str, Any]:
    """Gets name of the station and cost. Loads data for this station from Redis. Adds cost to its data. Returns dict with data."""
    data = rj.jsonget(name, Path.rootPath(), no_escape=True)
    data.update({"cost": cost})
    return {name: data}


def input_check(station: str) -> List[str]:
    """
    Checks if the station with input name exists. Returns [] if the station doesn't exist.
    If there are multiple stations, starting with input name, returns a list of this stations.
    If there is one station returns a list with one item.
    """
    all_stations = rj.jsonget("all_stations", Path.rootPath(), no_escape=True)
    result = []

    for name in all_stations:
        match = re.match(station, name)
        if match:
            result.append(name)

    return result


def dijkstra(start: str, finish: str) -> Tuple[int, List[str]]:
    """
    Calculate the shortest path in the graph using Dijkstra algorithm.
    This function creates a dict of visited stations with it's calculated costs.
    This dict is used in function find_way() to form a list of stations which form a shortest path.
    """
    visited, unvisited = {}, {}
    unvisited.update(set_cost_add_to_dict(start, 0))
    unvisited.update(set_cost_add_to_dict(finish, 9999))

    current = start

    while unvisited[current]["cost"] < unvisited[finish]["cost"]:
        current_links = unvisited[current]["links"]

        for link in current_links:
            if not link in unvisited and not link in visited and not link == finish:
                unvisited.update(set_cost_add_to_dict(link, 9999))

            if link in unvisited:
                current_cost = unvisited[current]["cost"]
                current_link_cost = unvisited[current]["links"][link]

                if (current_cost + current_link_cost) < unvisited[link]["cost"]:
                    unvisited[link]["cost"] = current_cost + current_link_cost

        visited.update({current: unvisited[current]})
        del unvisited[current]

        min_cost_station, _ = sorted(unvisited.items(), key=lambda x: x[1]["cost"])[0]
        current = min_cost_station

    visited.update({finish: unvisited[finish]})
    del unvisited[finish]

    return visited[finish]["cost"], find_path(visited, start, finish)


def find_path(graph: Dict[str, Any], start: str, finish: str) -> List[str]:
    """Gets graph with calculated costs for stations, start and finish stations. Returns a list of stations which form a shortest path from start to finish."""
    path = []
    current = finish

    while current != start:
        path.append(current)
        for link in graph[current]["links"]:
            if link in graph:
                if graph[link]["cost"] == (
                    graph[current]["cost"] - graph[current]["links"][link]
                ):
                    Next = link

        current = Next

    path.append(start)

    return path[::-1]


def path_output(time: int, stations: List[str]) -> str:
    """Gets shortest path time and stations list. Returns this path in human-readable format for printing."""
    result = f"Время в пути: <b>{time} мин</b>.\n"
    result += f"\nНаиболее короткий маршрут:\n\n<u><b>{capwords(stations[0])}</b></u>"
    current_line = rj.jsonget(stations[0], Path(".line"), no_escape=True)

    for i, station in enumerate(stations):
        station_line = rj.jsonget(station, Path(".line"), no_escape=True)

        if station_line != current_line:
            result += "\n|\nV\n{}\n  *\n    *\n    V\n<i>    ПЕРЕХОД ({} -> {})</i>\n    *\n  *\n V\n{}".format(
                capwords(stations[i - 1]),
                current_line,
                station_line,
                capwords(station),
            )
            current_line = station_line

    result += f"\n|\nV\n<u><b>{capwords(stations[-1])}</b></u>\n"

    return result
