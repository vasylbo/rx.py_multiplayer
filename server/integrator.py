import json
import logging
from functools import partial

import time
from rx import Observable
from rx.subjects import BehaviorSubject

from player import Player

log = logging.getLogger("game")


def integrate(new_players, scheduler):
    players = BehaviorSubject([])

    exiting_players = new_players \
        .flat_map(players_to_exits)

    exiting_players \
        .map(lambda player: (player, "remove")) \
        .merge(
            new_players
                .map(lambda player: (player, "add"))) \
        .scan(players_changed, []) \
        .subscribe(players)

    players \
        .zip(new_players,
             lambda p, ps: (ps, p)) \
        .subscribe(new_player_updates)

    Observable \
        .interval(16, scheduler) \
        .map(players_interval(players)) \
        .subscribe(update)

    # frame ticks
    stream_changes(player_to_change, 33, players, scheduler) \
        .subscribe(broadcast_changes)

    # direction update ticks
    stream_changes(player_to_direction, 16, players, scheduler) \
        .subscribe(broadcast_changes)


def players_interval(players):
    def get_time():
        return int(round(time.time() * 1000))

    start = get_time()

    def on_interval(*args):
        nonlocal start
        current = get_time()
        dt = current - start
        start = current
        return players.value, dt * 0.001

    return on_interval


# todo: maybe make reactive
def update(d):
    players, dt = d
    for player in players:
        direction = player.dir.value
        if direction is not None:
            position = player.pos.value
            speed = 300 * dt
            result = {
                "x": position["x"] + direction["x"] * speed,
                "y": position["y"] + direction["y"] * speed
            }
            player.pos.on_next(result)


def stream_changes(transformer, dt, players, scheduler):
    def to_changes(ps):
        return Observable \
            .from_iterable(ps, scheduler) \
            .flat_map(partial(
                transformer, scheduler))

    return players \
        .flat_map_latest(to_changes) \
        .buffer_with_time(dt, scheduler=scheduler) \
        .filter(lambda cs: len(cs) > 0) \
        .combine_latest(
            players,
            lambda c, p: (c, p))


def players_to_exits(player):
    return player \
        .ws_subject \
        .to_observable() \
        .last_or_default(None, True) \
        .map(lambda _: player)


def prepare_data(player: Player, t):
    return lambda data: {
        "id": player.id,
        "t": t,
        "data": data
    }


def player_to_change(scheduler, player: Player):
    return player.pos.map(
            prepare_data(player, "pos")) \
        .merge(scheduler, player.size.map(
            prepare_data(player, "size")))


def player_to_direction(scheduler, player: Player):
    return player.dir \
        .map(prepare_data(player, "d"))


def players_changed(players: list, operation):
    player, op = operation
    log.info("Player with id %s %s" % (player.name, op))
    if op == "add":
        players.append(player)
    else:
        players.remove(player)
    return players


def new_player_updates(data):
    new_player, players = data
    new_player_message = create_full_player_info(new_player)
    for player in players:
        player.ws_subject.on_next(new_player_message)
        if player is not new_player:
            new_player.ws_subject.on_next(
                    create_full_player_info(player))


def create_full_player_info(player):
    message = \
        """{
            "t": "new_player",
            "data": %s
        }""" % player.full_to_json()
    return message


def broadcast_changes(data):
    updates, players = data
    raw = {"t": "up", "data": updates}
    message = json.dumps(raw)
    for player in players:
        player.ws_subject.on_next(message)
