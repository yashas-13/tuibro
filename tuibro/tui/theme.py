"""Color pairs and visual theme for Tuibro TUI."""
import curses


# Color pair IDs
PAIR_DEFAULT = 0
PAIR_USER_MSG = 1
PAIR_AGENT_MSG = 2
PAIR_ACTION_LOG = 3
PAIR_ERROR = 4
PAIR_SYSTEM = 5
PAIR_BORDER = 6
PAIR_URL = 7
PAIR_ELEMENT = 8
PAIR_INTERACTIVE = 9
PAIR_FOCUSED = 10
PAIR_INPUT = 11
PAIR_STATUS = 12
PAIR_STATUS_KEY = 13
PAIR_HEADER = 14
PAIR_DIM = 15
PAIR_TITLE = 16
PAIR_TREE = 17
PAIR_HIGHLIGHT = 18


def setup_colors():
    """Initialize terminal color pairs."""
    if not curses.has_colors():
        return

    curses.start_color()
    curses.use_default_colors()

    curses.init_pair(PAIR_USER_MSG, curses.COLOR_BLUE, -1)
    curses.init_pair(PAIR_AGENT_MSG, curses.COLOR_GREEN, -1)
    curses.init_pair(PAIR_ACTION_LOG, curses.COLOR_YELLOW, -1)
    curses.init_pair(PAIR_ERROR, curses.COLOR_RED, -1)
    curses.init_pair(PAIR_SYSTEM, curses.COLOR_MAGENTA, -1)
    curses.init_pair(PAIR_BORDER, curses.COLOR_CYAN, -1)
    curses.init_pair(PAIR_URL, curses.COLOR_WHITE, -1)
    curses.init_pair(PAIR_ELEMENT, curses.COLOR_CYAN, -1)
    curses.init_pair(PAIR_INTERACTIVE, curses.COLOR_YELLOW, -1)
    curses.init_pair(PAIR_FOCUSED, curses.COLOR_GREEN, -1)
    curses.init_pair(PAIR_INPUT, curses.COLOR_WHITE, -1)
    curses.init_pair(PAIR_STATUS, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(PAIR_STATUS_KEY, curses.COLOR_WHITE, -1)
    curses.init_pair(PAIR_HEADER, curses.COLOR_WHITE, -1)
    curses.init_pair(PAIR_DIM, curses.COLOR_WHITE, -1)
    curses.init_pair(PAIR_TITLE, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(PAIR_TREE, curses.COLOR_WHITE, -1)
    curses.init_pair(PAIR_HIGHLIGHT, curses.COLOR_BLACK, curses.COLOR_YELLOW)


# Unicode drawing characters
BORDER_H = "─"
BORDER_V = "│"
BORDER_TL = "┌"
BORDER_TR = "┐"
BORDER_BL = "└"
BORDER_BR = "┘"
BORDER_T = "┬"
BORDER_B = "┴"
BORDER_L = "├"
BORDER_R = "┤"

TREE_BRANCH = "├──"
TREE_LAST = "└──"
TREE_PIPE = "│  "
TREE_SPACE = "   "
ARROW_ACTION = "→"
ARROW_FOCUSED = "►"
BULLET_USER = "🔵"
BULLET_AGENT = "🤖"
SPINNER = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
