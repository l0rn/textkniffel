# coding=utf-8
from collections import OrderedDict
import sys
import collections
import messages


POINTS = collections.OrderedDict([
            ('one', [0, False]),
            ('two', [0, False]),
            ('three', [0, False]),
            ('four', [0, False]),
            ('five', [0, False]),
            ('six', [0, False]),
            ('bonus', [0, False]),
            ('onepair', [0, False]),
            ('twopair', [0, False]),
            ('threesome', [0, False]),
            ('foursome', [0, False]),
            ('fullhouse', [0, False]),
            ('smallstreet', [0, False]),
            ('bigstreet', [0, False]),
            ('kniffel', [0, False]),
            ('chance', [0, False]),
        ])


class PointColumn(object):
    def __init__(self, restriction=lambda x, y: True):
        self.restriction = restriction
        self.points = POINTS.copy()
        self.lastentry = -1

    def everything(self, game, field):
        return True

    def all_dice(self, game, field):
        if game.active_player.states.get('rolled', 0) == len(game.active_player.dice.valuelist()):
            return True
        else:
            return False

    def up_to_down(self, game, field):
        # skip bonus
        if self.lastentry == list(self.points.keys()).index(field) - 1:
            return True
        elif field == 'onepair' and self.lastentry == list(self.points.keys()).index(field) - 2:
            return True
        raise TurnDoesntMatchRestrictionException()

    def down_to_up(self, game, field):
        if self.lastentry == -1 and field == 'chance':
            return True
        elif self.lastentry == list(self.points.keys()).index(field) + 1:
            return True
        elif field == 'six' and self.lastentry == list(self.points.keys()).index(field) + 2:
            return True
        raise TurnDoesntMatchRestrictionException()


class Points(object):
    def __init__(self, config='STD_CONFIG'):
        self.config = get_pointconfig(config)
        self.columns = get_pointtable(self.config)

    def bonus(self, column):
        if sum([self.columns[column - 1].points[k][0] for k in ('one', 'two', 'three', 'four', 'five', 'six')]) >= 63:
            return 35
        else:
            return 0

    def entry(self, field, column, values, game, preview=False):
        if self.columns[column - 1].points[field][1]:
            raise FieldAlreadyAssignedException()
        elif self.config.values()[column - 1](self.columns[column - 1], game, field):
            score = getattr(sys.modules[__name__], field)(values)
        else:
            score = 0
        if preview:
            return score
        self.columns[column - 1].points[field] = [score, True]
        self.columns[column - 1].points['bonus'] = self.bonus(column), True
        self.columns[column - 1].lastentry = list(POINTS.keys()).index(field)
        return score

    def subtotal(self, column):
        return sum([self.columns[column - 1].points[k][0] for k in ('one', 'two', 'three', 'four', 'five', 'six', 'bonus')])

    def total(self, column):
        return sum([i[0] for i in self.columns[column - 1].points.values()])

    def all_total(self):
        total = 0
        for i, val in enumerate(self.columns):
            total += self.total(i)
        return total

    def __str__(self):
        return self.__unicode__().encode('utf-8')

    def __unicode__(self):
        ret = ''
        for k, v in POINTS.iteritems():
            for column in self.columns:
                ret += u'{:15s}: {:8d} {}\n'.format(messages.strings[k], column.points[k][0],
                                                    (u'X' if column.points[k][1] else ' '))
        return ret

    def get_field_value(self, field, column):
        if field == 'subtotal':
            return self.subtotal(column), True
        elif field == 'total':
            return self.total(column), True
        elif field == 'bonus':
            return self.bonus(column), True
        else:
            return self.columns[column - 1].points[field]

    def get_field(self, field, column):
        try:
            return self.columns[column - 1].points[field]
        except KeyError:
            raise ColumnNotExistentException()


class ColumnNotExistentException(Exception):
    pass


class TurnDoesntMatchRestrictionException(Exception):
    pass


class FieldAlreadyAssignedException(Exception):
    pass


class FieldNotAllowedException(Exception):
    pass


def one(values):
    return numbers(values, 1)


def two(values):
    return numbers(values, 2)


def three(values):
    return numbers(values, 3)


def four(values):
    return numbers(values, 4)


def five(values):
    return numbers(values, 5)


def six(values):
    return numbers(values, 6)


def onepair(values):
    if len([x for x, y in collections.Counter(values).items() if y > 1]) >= 1:
        return sum(values)
    else:
        return 0


def twopair(values):
    if len([x for x, y in collections.Counter(values).items() if y > 1]) >= 2:
        return sum(values)
    else:
        return 0


def threesome(values):
    if multiple(values, 3):
        return sum(values)
    else:
        return 0


def foursome(values):
    if multiple(values, 4):
        return sum(values)
    else:
        return 0


def smallstreet(values):
    if street(values, 4):
        return 30
    else:
        return 0


def bigstreet(values):
    if street(values, 5):
        return 40
    else:
        return 0


def fullhouse(values):
    if multiple(values, 3, exact=True) and multiple(values, 2, exact=True):
        return 25
    else:
        return 0


def kniffel(values):
    if multiple(values, 5):
        return 50
    else:
        return 0


def numbers(values, number):
    return sum([i for i in values if i == number])


def chance(values):
    return sum(values)


def multiple(values, count, exact=False):
    for i in range(1, 7):
        check = 0
        for val in values:
            if val == i:
                check += val
        if ((not exact) and check > i * count) or check == i * count:
            return True
    return False


def street(values, length):
    values = list(set(values))
    last = values[0]
    count = 1
    for i in range(1, len(values)):
        if last == values[i]-1:
            count += 1
        last = values[i]
    if count >= length:
        return True
    else:
        return False


STD_CONFIG = OrderedDict([
    ('Beliebig', PointColumn.everything),
])


TODES_CONFIG = OrderedDict([
    ('Beliebig', PointColumn.everything),
    ('Oben nach Unten', PointColumn.up_to_down),
    ('Unten nach Oben', PointColumn.down_to_up),
    ('Von Hand', PointColumn.all_dice)
])


def get_pointconfig(config_str):
    thismodule = sys.modules[__name__]
    config = getattr(thismodule, config_str, STD_CONFIG)
    return config


def get_pointtable(config):
    pointtable = []
    for k, v in config.iteritems():
        pointtable.append(PointColumn(v) if v else PointColumn())
    return pointtable

