import json
import logging
from functools import partial

from rx import Observable
from rx.subjects import ReplaySubject

log = logging.getLogger("game")


def integrate(new_players, scheduler):
    players = ReplaySubject()

    players \
        .zip(new_players,
             lambda p, ps: (ps, p)) \
        .subscribe(new_player_updates)

    exiting_players = new_players \
        .flat_map(players_to_exits)

    exiting_players \
        .map(lambda player: (player, "remove")) \
        .merge(
            new_players
                .map(lambda player: (player, "add"))) \
        .scan(players_changed, []) \
        .subscribe(players)

    changed_players = players \
        .flat_map_latest(partial(players_to_changes, scheduler))

    # update ticks
    changed_players \
        .buffer_with_time(66, scheduler=scheduler) \
        .filter(lambda changes: len(changes) > 0) \
        .combine_latest(
            players,
            lambda c, p: (c, p)) \
        .subscribe(tick_updates)


def players_to_exits(player):
    return player \
        .ws_subject \
        .to_observable() \
        .last_or_default(None, True) \
        .map(lambda _: player)


def players_to_changes(scheduler, players: list):
    return Observable \
        .from_iterable(players, scheduler) \
        .flat_map(partial(flat_map_player, scheduler))


def prepare_data(player, data):
    info = {"id": player.id, "data": data}
    return player.ws_subject, info


def flat_map_player(scheduler, player):
    return player.pos \
        .merge(scheduler, player.size) \
        .map(partial(prepare_data, player))


def players_changed(players: list, operation):
    player, op = operation
    if op == "add":
        players.append(player)
    else:
        players.remove(player)
    return players


def new_player_updates(data):
    new_player, players = data
    log.info("Send new player %s" % new_player.name)
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


def tick_updates(data):
    updates, players = data
    changes = [data for _, data in updates]
    message = json.dumps({"t": "up", "data": changes})
    for player in players:
        player.ws_subject.on_next(message)
