import time
import json


# todo: make decorator to json.dump all this

def get_timestamp():
    return int(round(time.time() * 1000))


def init(player):
    return {"name": player.name,
            "ts": get_timestamp(),
            "id": player.id}


def pong(client_ts):
    return {"t": "pong",
            "ts": get_timestamp(),
            "lts": client_ts}


def new_players(players):
    return json.dumps({
        "t": "new_player",
        "data": [player.full_data()
                 for player in players]
    })


def removed_player(player):
    return json.dumps({
        "t": "removed_player",
        "data": player.id
    })


def update(player, t, data):
    return {
        "id": player.id,
        "t": t,
        "data": data
    }


def broadcast_update(updates):
    return {
        "t": "up",
        "ts": get_timestamp(),
        "data": updates
    }
