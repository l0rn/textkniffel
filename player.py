#coding=utf-8
from messages import prompt, print_message, print_help, print_dice, print_points
from dice import Dice
from points import Points, FieldAlreadyAssignedException


class Player(object):

    def __init__(self, game, id=1, max_turns=3):
        self.game = game
        self.id = id
        self.turn = 0
        self.points = Points()
        self.dice = Dice()
        self.max_turns = max_turns
        self.commands = {
            'd': self.roll_dice,
            's': self.save_dice,
            'save': self.save_dice,
            'help': print_help,
            'p': self.show_points,
            'p_all': self.show_all_points
        }

        self.point_commands = [
            'one', 'two', 'three', 'four', 'five', 'six', 'triple', 'quadruple',
            'small_street', 'big_street', 'kniffel', 'fullhouse', 'chance'
        ]

    def save_dice(self, values):
        self.dice.save(values)

    def play(self):
        self.dice = Dice()
        while True:
            try:
                self.command_prompt()
            except WrongCommandException:
                print_message('wrongcommand')
            except TurnEndException:
                break

        self.turn = 0

    def entry_points(self, field, values):
        self.points.entry(field, values)
        if all([i[1] for i in self.points.points.values()]):
            raise PlayerFinishedException()
        self.game.next_player()
        self.turn = 0

    def print_points(self):
        print_points(self.points)

    def command_prompt(self):
        value = prompt('playerprompt', self.id)
        try:
            if value.split(' ')[0] is 's':
                for pos in value.split(' ')[1].split(','):
                    try:
                        self.save_dice([int(pos)])
                    except ValueError:
                        print_message('unknown_param', pos)
                print_dice(self.dice)
            elif value in self.commands:
                try:
                    self.commands[value]()
                except NoTurnsLeftException:
                    print_message('noturnsleft')
            elif value in self.point_commands:
                try:
                    self.entry_points(value, self.dice.valuelist())
                    raise TurnEndException()
                except FieldAlreadyAssignedException:
                    print_message('fieldblocked')
            else:
                raise WrongCommandException()
        except IndexError:
            print_dice(self.dice)

    def roll_dice(self):
        if self.turn >= self.max_turns:
            raise NoTurnsLeftException()
        self.dice.roll()
        # TODO: printing shouln't be done here
        # print_dice(self.dice)
        self.turn += 1

    def show_points(self):
        print_points(self)

    def show_all_points(self):
        print_points(self.game.players)

    @classmethod
    def generate_players(cls, game, count):
        return [cls(game, i) for i in range(1, count+1)]


class WebPlayer(Player):
    def __init__(self, game, id=1, max_turns=3):
        self.token = None
        self.socket = None
        self.nickname = ''
        super(WebPlayer, self).__init__(game)

class TurnEndException(Exception):
    pass


class WrongCommandException(Exception):
    pass


class PlayerFinishedException(Exception):
    pass


class NoTurnsLeftException(Exception):
    pass