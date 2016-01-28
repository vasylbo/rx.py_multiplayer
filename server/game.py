import json
import logging
from copy import copy

from rx.concurrency import AsyncIOScheduler
from rx.subjects import Subject

from connection import WSHandlerSubject, WSSubject
from integrator import integrate
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
    data = {"name": player.name,
            "id": player.id}
    ws_subject.on_next(json.dumps(data))


def create_game_handler(loop):
    logging.basicConfig(level=logging.INFO)

    scheduler = AsyncIOScheduler(loop)
    handler = WSHandlerSubject()

    players = Subject()

    handler \
        .map(register) \
        .subscribe(players)

    players \
        .subscribe(send_init)

    # refactor
    integrate(players, scheduler)

    return handler
