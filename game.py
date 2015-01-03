# coding=utf-8
import messages
import curses_gui
from player import Player, PlayerFinishedException
import messages


class Game(object):
    def __init__(self, playercount, player_cls=Player):
        self.players = player_cls.generate_players(self, playercount)
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
        messages.print_message('winner', winner.id, winner.points.sumpoints())

    def get_winner(self):
        last = self.players[0]
        for player in self.players:
            if player.points.sumpoints() > last.points.sumpoints():
                last = player
        return last

    @classmethod
    def new_game_by_prompt(cls):
        messages.print_message('newgame')
        playercount = messages.prompt('chooseplayer', needed=int)
        return cls(playercount)


class CursesGame(Game):
    def start(self):
        curses_gui.game(self)

    @classmethod
    def new_game_by_curses(cls):
        return cls(curses_gui.player_select())