# coding=utf-8

strings = {
    'welcome': u'Willkommen zu TextKniffel, das Spiel startet sofort!',
    'newgame': u'Ein neues Spiel beginnt...',
    'chooseplayer': u'Wie viele Spieler sollen spielen? ',
    'nameplayer': u'Wie lautet der Name für Spieler {}',
    'prompt': u'Kommando:',
    'playerprompt': u'Kommando({}):',
    'player': u'Spieler({})',
    'wrongtype': u'Der eingegebene Wert muss vom Typ {} sein',
    'wrongcommand': u'Kein gültiges Kommando',
    'noturnsleft': u'Alle Würfe aufgebraucht, bitte Punkte eintragen',
    'int': u'Zahl',
    'finished': u'Das Spiel ist beendet!',
    'winner': u'Spieler {} hat mit {} Punkten gewonnen!',
    'help': u'Test',
    'points': u'Punktestand',
    'point_header': u'Feld',
    'one': u'Einsen',
    'two': u'Zweien',
    'three': u'Dreien',
    'four': u'Vieren',
    'five': u'Fünfen',
    'six': u'Sechsen',
    'bonus': u'Bonus',
    'onepair': u'Ein Paar',
    'twopair': u'Zwei Paar',
    'threesome': u'Dreierpasch',
    'foursome': u'Viererpasch',
    'kniffel': u'Kniffel',
    'smallstreet': u'Kleine Straße',
    'bigstreet': u'Große Straße',
    'chance': u'Chance',
    'fullhouse': u'Full House',
    'sum': u'Summe',
    'fieldblocked': u'Dieses Feld ist schon belegt',
    'unknown_param': u'Ungültiger Parameter {}'
}


def print_message(message, *args):
    print strings[message].format(*args)


def print_dice(dice):
    print dice


def print_points(players):
    if type(players) != list:
        players = [players]
    header = u'{:<18s}'.format(strings['points'])
    for player in players:
        header += u'{:>14s}'.format(strings['player'].format(player.id))
    points = u''
    for field in player.points.points:
        points += u'{:<18s}'.format(strings[field])
        for player in players:
            points += u'   {}{:>10d}'.format('X' if player.points.points[field][1] else ' ',
                                             player.points.points[field][0])
        points += u'\n'
    points += u'{:<18s}'.format(strings['sum'])
    for player in players:
        points += u'{:14d}'.format(player.points.sumpoints())
    print header
    print points


def print_help():
    print_message('help')


def prompt(message, values=[], needed=None):
    while True:
        input_value = raw_input(strings[message].format(values))
        if needed:
            try:
                return needed(input_value)
            except ValueError:
                print_message('wrongtype', strings[needed.__name__])
        else:
            return input_value