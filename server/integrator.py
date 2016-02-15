import math
from itertools import combinations

from rx.subjects import Subject, BehaviorSubject


class Integrator:
    def __init__(self, new_players, exiting_players):
        self._new_players = []
        self._players = []
        self._removed_players = []

        new_players.subscribe(self.add_player)
        exiting_players.subscribe(self.remove_player)

        # streams api
        self.new_players_broadcast = Subject()
        self.removed_players_broadcast = Subject()
        self.collisions = Subject()
        self.players = BehaviorSubject([])
        self.players_count = self.players \
            .map(lambda ps: len(ps))

    def add_player(self, player):
        self._new_players.append(player)

    def remove_player(self, player):
        self._removed_players.append(player)

    def broadcast(self, message):
        for p in self._players:
            p.ws_subject.on_next(message)

    def update(self, dt):
        if len(self._new_players):
            self._do_add_players()

        self._integrate_speed(dt)
        self._collide()

        if len(self._removed_players):
            self._do_remove_players()

    def _collide(self):
        for a, b in combinations(self._players, 2):
            posa = a.pos.value
            posb = b.pos.value
            sizea = a.size.value
            sizeb = b.size.value

            distance = math.sqrt((posa["x"] - posb["x"]) ** 2 + (posa["y"] - posb["y"]) ** 2)
            if distance < sizea + sizeb:
                self.collisions.on_next((a, b))

    def _integrate_speed(self, dt):
        for player in self._players:
            direction = player.dir.value
            if direction is not None \
                    and direction["x"] != 0 \
                    and direction["y"] != 0:
                position = player.pos.value
                speed = 300 * dt
                result = {
                    "x": position["x"] + direction["x"] * speed,
                    "y": position["y"] + direction["y"] * speed
                }
                player.pos.on_next(result)

    def _do_add_players(self):
        self._players.extend(self._new_players)
        self.new_players_broadcast.on_next(
                (self._players, self._new_players.copy()))
        self._new_players.clear()
        self.players.on_next(self._players)

    def _do_remove_players(self):
        for p in self._removed_players:
            self._players.remove(p)
        self.removed_players_broadcast.on_next(
                (self._players, self._removed_players.copy()))
        self._removed_players.clear()
        self.players.on_next(self._players)
