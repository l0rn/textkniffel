# coding=utf-8
from messages import prompt, print_message, print_help, print_dice, print_points
from dice import Dice
from points import Points, FieldAlreadyAssignedException


class Player(object):

    def __init__(self, game, point_config='STD_CONFIG', uid=1, max_turns=3):
        self.game = game
        self.id = uid
        self.turn = 0
        self.points = Points(config=point_config)
        self.dice = Dice()
        self.max_turns = max_turns

    def save_dice(self, values):
        self.dice.save(values)

    def entry_points(self, field, column, values, preview=False):
        score = self.points.entry(field, column, values, self.game, preview=preview)
        if not preview:
            if all([all([i[1] for i in column.points.values()]) for column in self.points.columns]):
                raise PlayerFinishedException()
            self.game.next_player()
            self.turn = 0
        return score

    def roll_dice(self):
        if self.turn >= self.max_turns:
            raise NoTurnsLeftException()
        self.dice.roll()
        self.turn += 1

    def delete(self):
        if self.game.active_player == self:
            self.game.next_player()
        del self.game.players[self.game.players.index(self)]

    @classmethod
    def generate_players(cls, game, count, point_config):
        return [cls(game, point_config=point_config, uid=i) for i in range(1, count+1)]


class CommandlinePlayer(Player):

    def __init__(self, game, uid=1, max_turns=3, point_config='STD_CONFIG'):
        super(CommandlinePlayer, self).__init__(game, uid=uid, point_config=point_config, max_turns=max_turns)
        self.commands = {
            'd': self.roll_dice,
            's': self.save_dice,
            'save': self.save_dice,
            'help': print_help,
            'p': self.show_points,
            'p_all': self.show_all_points
        }

        self.point_commands = [
            'one', 'two', 'three', 'four', 'five', 'six', 'threesome', 'foursome', 'onepair', 'twopair',
            'smallstreet', 'bigstreet', 'kniffel', 'fullhouse', 'chance'
        ]

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

    def roll_dice(self):
        super(CommandlinePlayer, self).roll_dice()
        print_dice(self.dice)

    def show_points(self):
        print_points(self)

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
            elif value.split(' ')[0] in self.point_commands:
                try:
                    try:
                        column = value.split(' ')[1]
                        self.entry_points(value, column, self.dice.valuelist())
                        raise TurnEndException()
                    except IndexError:
                        print_message('specify_column')
                except FieldAlreadyAssignedException:
                    print_message('fieldblocked')
            else:
                raise WrongCommandException()
        except IndexError:
            print_dice(self.dice)

    def show_all_points(self):
        print_points(self.game.players)


class WebPlayer(Player):

    def __init__(self, game, point_config='STD_CONFIG', uid=1, max_turns=3):
        super(WebPlayer, self).__init__(game, point_config=point_config, uid=uid, max_turns=max_turns)
        self.token = None
        self.socket = None
        self.nickname = ''


class TurnEndException(Exception):
    pass


class WrongCommandException(Exception):
    pass


class PlayerFinishedException(Exception):
    pass


class NoTurnsLeftException(Exception):
    pass