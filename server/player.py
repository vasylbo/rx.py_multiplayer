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
        self.id = id
        self.ws_subject = ws_subject
        self.name = name
        self.size = BehaviorSubject(size)
        self.pos = BehaviorSubject(pos)
        self.dir = BehaviorSubject(None)

        ws_subject \
            .to_observable() \
            .map(lambda d: json.loads(d.data)) \
            .filter(lambda m: m["t"] == "d") \
            .subscribe(self.dir)

        self.dir.subscribe(lambda d: print(d))

    def partial_data(self):
        return {
            "id": self.id,
            "size": self.size.value,
            "pos": self.pos.value
        }

    def full_data(self):
        data = self.partial_data()
        data["name"] = self.name
        return data
