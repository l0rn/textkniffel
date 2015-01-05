# coding=utf-8
from player import Player, PlayerFinishedException, CommandlinePlayer
from points import STD_CONFIG

import points
import messages


class Game(object):
    def __init__(self, playercount, player_cls=Player, point_config='STD_CONFIG'):
        self.point_config = []
        for i, column_name in enumerate(getattr(points, point_config, STD_CONFIG).keys()):
            self.point_config.append({
                'name': column_name,
                'id': i + 1
            })

        self.players = player_cls.generate_players(self, playercount, point_config=point_config)
        self.active_player_number = 0

    def next_player(self):
        self.active_player.dice.clear()
        self.active_player_number += 1
        if self.active_player_number >= len(self.players):
            self.active_player_number = 0

    @property
    def active_player(self):
        return self.players[self.active_player_number]


class CommandlineGame(Game):
    def start(self):
        finished = 0
        while finished < len(self.players):
            for player in self.players:
                try:
                    player.play()
                except PlayerFinishedException:
                    finished += 1

        winner = self.get_winner()
        messages.print_message('finished')
        messages.print_points(self.players)
        messages.print_message('winner', winner.id, winner.points.total())

    def get_winner(self):
        last = self.players[0]
        for player in self.players:
            if player.points.total() > last.points.total():
                last = player
        return last

    @classmethod
    def new_game_by_prompt(cls):
        messages.print_message('newgame')
        playercount = messages.prompt('chooseplayer', needed=int)
        return cls(playercount, player_cls=CommandlinePlayer)
