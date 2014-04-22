#coding=utf-8
from game import CommandlineGame, CursesGame
import argparse
import messages
import curses_gui

def commandline_game():
    messages.print_message('welcome')
    game = CommandlineGame.new_game_by_prompt()
    game.start()


def curses_game():
    curses_gui.welcome_screen()
    game = CursesGame.new_game_by_curses()
    game.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--curses", help="start with curses gui", action='store_true')
    parser.add_argument("--cmd", help="start with commandline gui(default)", action='store_true')
    args = parser.parse_args()
    if args.cmd:
        commandline_game()
    elif args.curses:
        curses_game()