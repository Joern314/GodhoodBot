import json

from wiki import Entry


class Player:
    def __init__(self, obj):
        self.name = obj['name']
        self.spheres = obj['spheres']
        self.player = obj['player']

        self.acts = obj.get('acts', 0)
        self.gain = obj.get('gain', 0)
        self.draw = obj.get('draw', 0)

    def to_string(self):
        sp = " & ".join(self.spheres)
        return (
            f"**{self.name}** ({sp}) {self.player} \n"
            f"> Acts: {self.acts} Gain: +{self.gain} Draw: -{-self.draw}\n"
        )

    def to_obj(self):
        return {
            "name": self.name,
            "spheres": self.spheres,
            "player": self.player,
            "acts": self.acts,
            "gain": self.gain,
            "draw": self.draw
        }


class PlayerList:
    def __init__(self, file):
        objs = json.loads(file)
        self.players = [Player(obj) for obj in objs]
        self.players.sort(key=lambda p: Entry.normalize(p.name))

    def get_player(self, name: str):
        for player in self.players:
            if Entry.normalize(player.name) == Entry.normalize(name):
                return player
        return None

    def to_string(self):
        return "\n".join([p.to_string() for p in self.players])

    def to_obj(self):
        return [p.to_obj() for p in self.players]

    def to_json_string(self):
        obj = self.to_obj()
        return json.dumps(obj, indent=2, sort_keys=True)