import curses


def welcome_screen():
    stdscr = curses.initscr()
    stdscr.border(0)
    stdscr.addstr(12, 25, 'TextKniffel Curses')
    stdscr.getch()
    curses.endwin()
    stdscr.clear()

def player_select():
    stdscr = curses.initscr()
    stdscr.border(0)
    stdscr.addstr(12, 25, 'Type in the Number of Players')
    while True:
        selected = stdscr.getch()
        try:
            return int(selected)
        except ValueError:
            pass
    stdscr.clear()

def game(game):
    #initiating curses
    stdscr = curses.initscr()
    stdscr.clear()
    stdscr.border(0)
    stdscr.addstr(2, 2, "Please enter a number...")
    stdscr.addstr(4, 4, "1 - 5 Save dice")
    stdscr.addstr(5, 4, "6 - Roll dice")
    stdscr.addstr(6, 4, "7 - Assign Points")
    stdscr.addstr(7, 4, "Q - Exit")
    stdscr.refresh()
    selected = stdscr.getch()

    if selected in [1, 2, 3, 4, 5]:
        curses.endwin()