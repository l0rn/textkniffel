# coding=utf-8
from game import CommandlineGame
import argparse
import messages
import wsserver


def commandline_game():
    messages.print_message('welcome')
    game = CommandlineGame.new_game_by_prompt()
    game.start()


def todesknobel_server():
    wsserver.start_server()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--cmd", help="start with commandline gui(default)", action='store_true')
    parser.add_argument("--server", help="start todesknobel server", action='store_true')
    args = parser.parse_args()
    if args.cmd:
        commandline_game()
    elif args.server:
        todesknobel_server()