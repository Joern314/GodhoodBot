#  Help the GM list the players and their act counts

import csv


class PlayerCharacter:
    def __init__(self, name: str, player: str, act_history, gain_history, inactive: bool):
        self.name = name
        self.player = player
        self.act_history = act_history
        self.gain_history = gain_history
        self.inactive = inactive

    def current_acts(self):
        return sum(self.act_history)

    def current_gain(self):
        return sum(self.gain_history)


def load_csv():
    with open("data/wiki/players.csv") as file:
        csv_r = csv.reader(file)
        chars = {}

        turn_count = None

        for row in csv_r:
            if turn_count is None:
                turn_count = (len(row) - 2) / 2

            char = PlayerCharacter(
                name=row[0].strip(),
                player=row[1].strip(),
                act_history=row[2::2],
                gain_history=row[3::2],
                inactive=len(row) < turn_count * 2 + 2
            )
            chars[char.name] = char

        return chars


def format_csv():
    chars = load_csv()
    max_name = max(len(c.name) for c in chars.values())
    max_player = max(len(c.player) for c in chars.values())

    with open("data/wiki/players.csv") as file:
        csv_w = csv.writer(file)
        for c in chars.values()