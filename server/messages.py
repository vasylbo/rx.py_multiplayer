import time
import json


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


def new_player(player):
    return """{
        "t": "new_player",
        "data": %s
    }""" % player.full_to_json()


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
