import json
import logging
from copy import copy

from rx.concurrency import AsyncIOScheduler
from rx.subjects import Subject

import messages as mess_factory
from connection import WSHandlerSubject, WSSubject
from manager import manage
from names import generate_name
from player import Player

global_id = 0
START_SIZE = 40
START_POS = {"x": 500, "y": 500}


def register(ws_subject: WSSubject, i):
    name = generate_name()
    return Player(i, name,
                  ws_subject,
                  START_SIZE, copy(START_POS))


def send_init(player: Player):
    ws_subject = player.ws_subject
    data = mess_factory.init(player)
    # needs refactoring
    player \
        .ws_subject \
        .to_observable() \
        .map(lambda d: json.loads(d.data)) \
        .filter(lambda d: d["t"] == "ping") \
        .subscribe(lambda data: send_pong(player, data))
    ws_subject.on_next(json.dumps(data))


def send_pong(player, data):
    m = mess_factory.pong(data["ts"])
    player.ws_subject.on_next(json.dumps(m))


def create_game_handler(loop):
    logging.basicConfig(level=logging.INFO)

    scheduler = AsyncIOScheduler(loop)
    handler = WSHandlerSubject()

    # todo: find a place where it can gracefully shutdown
    players = Subject()

    handler \
        .map(register) \
        .subscribe(players)

    players \
        .subscribe(send_init)

    # refactor
    manage(players, scheduler)

    return handler
