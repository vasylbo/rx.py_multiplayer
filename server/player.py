import json
import logging
from json import JSONEncoder

from rx.subjects import BehaviorSubject

log = logging.getLogger("game")


class PlayerEncoder(JSONEncoder):
    def __init__(self, ignore_keys):
        super(PlayerEncoder, self).__init__()
        self._ignore_keys = ignore_keys

    def default(self, o):
        if isinstance(o, BehaviorSubject):
            return o.value
        elif isinstance(o, Player):
            return {key: value for
                    key, value in o.__dict__.items()
                    if key not in self._ignore_keys}


class Player:
    def __init__(self, id, name, ws_subject, size, pos):
        log.info("New player %s" % name)
        self.id = id
        self.ws_subject = ws_subject
        self.name = name
        self.size = BehaviorSubject(size)
        self.pos = BehaviorSubject(pos)
        self.dir = ws_subject \
            .to_observable() \
            .map(lambda d: json.loads(d.data))

        def scan_direction(pos, dir):
            if dir:
                pos["x"] += dir["x"] * 10
                pos["y"] += dir["y"] * 10
            return pos

        self.dir \
            .scan(scan_direction, seed=pos) \
            .subscribe(self.pos)
        self.dir.subscribe(lambda d: print(id, d))

    def partial_to_json(self):
        return PlayerEncoder(["ws_subject", "name", "dir"]).encode(self)

    def full_to_json(self):
        return PlayerEncoder(["ws_subject", "dir"]).encode(self)
