#coding=utf-8
import random


class Dice():
    def __init__(self, count=5):
        self.values = {k: [0, False] for k in range(1, count+1)}

    def clear(self):
        self.__init__()

    def roll(self):
        for dice in self.values.itervalues():
            if not dice[1]:
                dice[0] = self.get_dice()

    def save(self, to_save):
        for i in to_save:
            self.values[i][1] = not self.values[i][1]

    def __str__(self):
        line1 = ''
        line2 = ''
        for v in self.values.itervalues():
            line1 += '[ %d ] ' % v[0]
            line2 += '[ %s ] ' % ('X' if v[1] else ' ')
        return line1 + '\n' + line2

    def valuelist(self):
        return [v[0] for v in self.values.itervalues()]

    def savelist(self):
        return [v[1] for v in self.values.itervalues()]

    @staticmethod
    def get_dice():
        return random.randint(1, 6)
