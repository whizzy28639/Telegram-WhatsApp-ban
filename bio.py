#!/usr/bin/env python3
"""
bio_matrix.py

Terminal animation:
 - Matrix rain background
 - Typed bio (word-by-word) with cycling colors
 - Works in typical UNIX terminals (including Termux)
 - Quit with 'q' or Ctrl-C

Dependencies: only Python standard library (uses curses).
If curses isn't available on your platform, try running in a Linux-like shell.

Customize the BIO_LINES list below.

Author: generated for Tizzy Whizzy
"""

import curses
import time
import random
import argparse
import textwrap
import sys
from itertools import cycle

# -----------------------
# Customizable Bio Lines
# -----------------------
BIO_LINES = [
    "Tizzy Whizzy",
    "Cybersecurity Instructor & Developer",
    "I teach practical cybersecurity with hands-on tooling, Termux workflows, and playful demos.",
    "Skills: Python · Bash/Termux · Git · Automation · Teaching",
    "Contact: http://t.me/Mr_Whizzy01  ·  Channel: https://t.me/t_tech_X"
]

# Characters used in matrix rain
MATRIX_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&*+-/\\|()[]{}<>"

# Colors we'll cycle through for the bio text (curses color constants)
COLOR_CYCLE = [
    curses.COLOR_GREEN,
    curses.COLOR_CYAN,
    curses.COLOR_YELLOW,
    curses.COLOR_MAGENTA,
    curses.COLOR_RED,
    curses.COLOR_BLUE,
    curses.COLOR_WHITE,
]

# -----------------------
# Core functions
# -----------------------
def init_colors():
    """
    Initialize color pairs for text cycling and for the matrix drops.
    Pair 1..n for text; pair 50 used for bright green matrix head,
    pair 51 for dim green tail (if terminal supports).
    """
    curses.start_color()
    curses.use_default_colors()
    # create pairs for cycling bio text
    for i, color in enumerate(COLOR_CYCLE, start=1):
        try:
            curses.init_pair(i, color, -1)
        except Exception:
            # terminal might not support many colors; ignore
            pass

    # matrix colors
    try:
        curses.init_pair(50, curses.COLOR_GREEN, -1)   # bright-ish head
        curses.init_pair(51, curses.COLOR_BLACK, -1)   # darker tail (fallback)
    except Exception:
        pass


class MatrixColumn:
    """Represents one column of falling characters."""
    def __init__(self, x, height):
        self.x = x
        self.height = height
        self.reset()

    def reset(self):
        self.y = random.randint(-self.height // 2, 0)
        self.speed = random.uniform(0.05, 0.4)  # seconds per step
        self.length = random.randint(4, max(6, self.height // 6))
        self.last_step = time.time()
        # pre-generate characters for the column
        self.chars = [random.choice(MATRIX_CHARS) for _ in range(self.height + self.length + 10)]

    def step(self):
        now = time.time()
        if now - self.last_step >= self.speed:
            self.y += 1
            self.last_step = now
            # sometimes reset when a column has gone off screen
            if self.y - self.length > self.height + random.randint(0, self.height):
                self.reset()

    def get_positions(self):
        """Return list of (y_pos, char, is_head) for currently visible chars."""
        res = []
        for i in range(self.length):
            pos = self.y - i
            if 0 <= pos < self.height:
                char = self.chars[(self.y + i) % len(self.chars)]
                is_head = (i == 0)
                res.append((pos, char, is_head))
        return res


def center_x_for_text(screen_width, text):
    return max(0, (screen_width - len(text)) // 2)


def draw_matrix(stdscr, columns):
    """Draw the matrix rain given current column states."""
    height, width = stdscr.getmaxyx()
    for col in columns:
        for y, ch, is_head in col.get_positions():
            try:
                if is_head:
                    # bright head
                    stdscr.addch(y, col.x, ch, curses.color_pair(50) | curses.A_BOLD)
                else:
                    # tail: dim or normal
                    # Use white or default tail falloff by intensity
                    stdscr.addch(y, col.x, ch, curses.color_pair(51))
            except curses.error:
                # off-screen writes can raise; ignore
                pass


def type_bio_overlay(stdscr, bio_lines, color_cycle_iter, word_delay=0.28, char_delay=0.02):
    """
    Types the bio word-by-word centered on the screen. Each word cycles color.
    We overlay this on top of the matrix.
    """
    height, width = stdscr.getmaxyx()
    # compute where to start vertically (center block)
    block_height = len(bio_lines)
    start_y = max(2, (height - block_height) // 2)

    # split lines into words but maintain punctuation spacing
    for row_idx, line in enumerate(bio_lines):
        words = line.split(" ")
        x = center_x_for_text(width, line)
        y = start_y + row_idx
        # walk across words, printing them with space
        for w_idx, word in enumerate(words):
            # cycle color for each word
            color_idx = next(color_cycle_iter)
            # ensure valid color pair index (1..n where n=len(COLOR_CYCLE))
            pair_num = (color_idx % len(COLOR_CYCLE)) + 1
            # print word character-by-character for a type effect
            for ch in word:
                try:
                    stdscr.addch(y, x, ch, curses.color_pair(pair_num) | curses.A_BOLD)
                except curses.error:
                    pass
                x += 1
                stdscr.refresh()
                time.sleep(char_delay)
            # print following space
            try:
                stdscr.addch(y, x, " ")
            except curses.error:
                pass
            x += 1
            stdscr.refresh()
            time.sleep(word_delay)
        # small pause after finishing a line
        time.sleep(0.25)


def main(stdscr, args):
    # configuration tweaks
    curses.curs_set(0)  # hide cursor
    stdscr.nodelay(True)  # make getch non-blocking
    stdscr.timeout(0)

    init_colors()

    height, width = stdscr.getmaxyx()
    # create columns across the full width with some spacing
    columns = []
    for x in range(0, width):
        if random.random() < 0.12:  # about 12% of columns active -> density control
            columns.append(MatrixColumn(x, height))

    # ensure we have enough columns
    if not columns:
        for x in range(0, width, max(1, width // 40)):
            columns.append(MatrixColumn(x, height))

    # a cycling iterator that returns indices for color pairs
    color_idx_cycle = cycle(range(len(COLOR_CYCLE)))
    # We'll type the bio once, then keep it visible while matrix keeps raining.
    typed = False
    last_draw = 0.0

    # allow the bio to be typed repeatedly (set to False to type only once)
    repeat_bio = args.repeat

    # If user passed speed adjustments
    word_delay = args.word_delay
    char_delay = args.char_delay

    # Keep timeline - we will render matrix continuously and trigger typing when space bar pressed or immediately if configured
    if args.autoplay:
        do_type = True
    else:
        do_type = False

    try:
        while True:
            # handle input
            ch = stdscr.getch()
            if ch != -1:
                if ch in (ord('q'), ord('Q')):
                    break
                if ch == ord(' '):  # space toggles typing
                    do_type = True

            # update columns
            for col in columns:
                col.step()

            # draw background (clear then draw)
            stdscr.erase()
            draw_matrix(stdscr, columns)

            # decide to type / overlay
            if do_type and (not typed or repeat_bio):
                type_bio_overlay(stdscr, args.lines, color_idx_cycle, word_delay=word_delay, char_delay=char_delay)
                typed = True
                do_type = False if not repeat_bio else True

            # keep a faint static copy of bio (so it doesn't disappear if typed only once)
            # We'll rewrite full lines centered, but without typing animation, using a subtle color cycle
            height, width = stdscr.getmaxyx()
            block_height = len(args.lines)
            start_y = max(2, (height - block_height) // 2)
            # display static overlay (slight dim)
            for row_idx, line in enumerate(args.lines):
                x = center_x_for_text(width, line)
                y = start_y + row_idx
                # use cycling colors but not heavy bold
                for i, ch in enumerate(line):
                    try:
                        pair_num = (next(color_idx_cycle) % len(COLOR_CYCLE)) + 1
                        stdscr.addch(y, x + i, ch, curses.color_pair(pair_num))
                    except curses.error:
                        pass

            stdscr.refresh()
            time.sleep(0.03)  # main loop frame rate

    except KeyboardInterrupt:
        # exit gracefully
        pass


# -----------------------
# Helper to parse args
# -----------------------
def parse_args():
    p = argparse.ArgumentParser(description="Terminal bio with matrix rain and colored typing.")
    p.add_argument("--repeat", action="store_true", help="Keep typing the bio repeatedly (default: type once).")
    p.add_argument("--autoplay", action="store_true", help="Start typing automatically on launch (default: press space to start).")
    p.add_argument("--word-delay", type=float, default=0.28, help="Delay (s) between words while typing.")
    p.add_argument("--char-delay", type=float, default=0.02, help="Delay (s) between characters while typing.")
    p.add_argument("--lines", nargs="*", help="Override bio lines (quoted), e.g. --lines \"Line 1\" \"Line 2\"")
    return p.parse_args()


# -----------------------
# Entrypoint
# -----------------------
if __name__ == "__main__":
    args = parse_args()
    # if lines provided on CLI, use them; otherwise use our BIO_LINES
    if args.lines and len(args.lines) > 0:
        args.lines = args.lines
    else:
        args.lines = BIO_LINES

    # Ensure terminal is large enough for good effect; else run anyway
    try:
        curses.wrapper(main, args)
    except curses.error as e:
        print("Terminal does not support curses or is too small. Run in a normal terminal.")
        print("Error:", e)
        sys.exit(1)
