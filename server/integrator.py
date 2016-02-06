from rx.subjects import Subject


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

    def add_player(self, player):
        self._new_players.append(player)

    def remove_player(self, player):
        self._removed_players.append(player)

    def update(self, dt):
        if len(self._new_players):
            self._players.extend(self._new_players)
            self.new_players_broadcast.on_next(
                    (self._players, self._new_players.copy()))
            self._new_players.clear()

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

        if len(self._removed_players):
            for p in self._removed_players:
                self._players.remove(p)
            self.removed_players_broadcast.on_next(
                    (self._players, self._removed_players.copy()))
            self._removed_players.clear()
