#coding=utf-8
import sys
import collections
import messages

class Points():
    def __init__(self):
        self.points = collections.OrderedDict([
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
            ('kniffel', [0, False]),
            ('smallstreet', [0, False]),
            ('bigstreet', [0, False]),
            ('chance', [0, False]),
            ('fullhouse', [0, False])
        ])

    def bonus(self):
        if sum([self.points[k][0] for k in ('one', 'two', 'three', 'four', 'five', 'six')]) >= 63:
            return 35
        else:
            return 0

    def entry(self, field, values):
        if self.points[field][1]:
            raise FieldAlreadyAssignedException()
        self.points[field] = [getattr(sys.modules[__name__], field)(values), True]
        self.points['bonus'] = self.bonus(), True

    def subtotal(self):
        return sum([self.points[k][0] for k in ('one', 'two', 'three', 'four', 'five', 'six', 'bonus')])

    def sumpoints(self):
        return sum([i[0] for i in self.points.values()])

    def __str__(self):
        return self.__unicode__().encode('utf-8')

    def __unicode__(self):
        ret = ''
        for k, v in self.points.iteritems():
            ret += u'{:15s}: {:8d} {}\n'.format(messages.strings[k], v[0], (u'X' if v[1] else ' '))
        return ret


class FieldAlreadyAssignedException(Exception):
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
    if [x for x, y in collections.Counter(values).items() if y > 1] >= 1:
        return sum(values)
    else:
        return 0

def twopair(values):
    if [x for x, y in collections.Counter(values).items() if y > 1] >= 2:
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
    if street(values, 4):
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
        else:
            count = 1
        last = values[i]
    if count >= length:
        return True
    else:
        return False
