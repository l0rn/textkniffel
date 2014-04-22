# coding=utf-8
import messages
import curses_gui
from player import Player, PlayerFinishedException
import messages


class CommandlineGame():
    def __init__(self, playercount):
        self.players = Player.generate_players(self, playercount)

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


class CursesGame():
    def __init__(self, playercount):
        self.players = Player.generate_players(playercount)

    def start(self):
        curses_gui.game(self)

    @classmethod
    def new_game_by_curses(cls):
        return cls(curses_gui.player_select())