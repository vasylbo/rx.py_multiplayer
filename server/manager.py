import json
import logging
from functools import partial
import messages as mess_factory

import time
from rx import Observable
from rx.subjects import BehaviorSubject

from food import create_food
from integrator import Integrator
from player import Player

log = logging.getLogger("game")


def manage(new_players, scheduler):
    exiting_players = new_players \
        .flat_map(players_to_exits)

    integrator = Integrator(new_players, exiting_players)

    integrator.new_players_broadcast.subscribe(broadcast_new_player)
    integrator.removed_players_broadcast.subscribe(broadcast_removed_player)
    # integrator.collisions \
    #     .subscribe(lambda data: print("collision", data))

    short_frame = Observable \
        .interval(16, scheduler) \
        .map(compute_delta())
    short_frame.subscribe(integrator.update)

    # frame ticks
    stream_changes(player_to_change, 33, new_players, scheduler) \
        .subscribe(lambda data: broadcast_changes(data, integrator))

    # direction update ticks
    stream_changes(player_to_direction, 16, new_players, scheduler) \
        .subscribe(lambda data: broadcast_changes(data, integrator))


def compute_delta():
    def get_time():
        return int(round(time.time() * 1000))

    start = get_time()

    def on_interval(*args):
        nonlocal start
        current = get_time()
        dt = current - start
        start = current
        return dt * 0.001

    return on_interval


def stream_changes(transformer, dt, new_players, scheduler):
    return new_players \
        .flat_map(partial(transformer, scheduler)) \
        .buffer_with_time(dt, scheduler=scheduler) \
        .filter(lambda cs: len(cs) > 0)


def players_to_exits(player):
    return player \
        .ws_subject \
        .to_observable() \
        .last_or_default(None, True) \
        .map(lambda _: player)


def prepare_data(player: Player, t):
    return lambda data: mess_factory \
        .update(player, t, data)


def player_to_change(scheduler, player: Player):
    return player.pos.map(
            prepare_data(player, "pos")) \
        .merge(scheduler, player.size.map(
            prepare_data(player, "size")))


def player_to_direction(scheduler, player: Player):
    return player.dir \
        .map(prepare_data(player, "d"))


def broadcast_new_player(value):
    players, new_players = value

    # send new players to old players
    new_players_message = mess_factory.new_players(new_players)
    for player in players:
        if player not in new_players:
            player.ws_subject.on_next(new_players_message)

    # send all players to new players
    players_message = mess_factory.new_players(players)
    for player in new_players:
        player.ws_subject.on_next(players_message)


def broadcast_removed_player(value):
    players, removed_players = value
    removed_players_msg = mess_factory \
        .removed_players(removed_players)
    for player in players:
        player.ws_subject.on_next(removed_players_msg)


def broadcast_changes(data, integrator):
    updates = data
    raw = mess_factory.broadcast_update(updates)
    message = json.dumps(raw)
    integrator.broadcast(message)
