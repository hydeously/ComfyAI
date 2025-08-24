import sys
import time
import random
import os

# ANSI color codes for phosphor green
PHOSPHOR_GREEN = "\033[38;2;100;255;100m"
DIM_GREEN = "\033[38;2;50;128;50m"
BRIGHT_GREEN = "\033[38;2;150;255;150m"
COLOR_RESET = "\033[0m"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"

# Blinking cursor character
CURSOR_CHAR = "❚"

def typewriter(text, base_delay=0.02, flicker_chance=0.05):
    """Prints text one character at a time with random flicker brightness."""
    for char in text:
        # Randomly pick brightness to simulate CRT flicker
        rand = random.random()
        if rand < flicker_chance / 2:
            color = DIM_GREEN
        elif rand < flicker_chance:
            color = BRIGHT_GREEN
        else:
            color = PHOSPHOR_GREEN
        sys.stdout.write(color + char + COLOR_RESET)
        sys.stdout.flush()
        time.sleep(base_delay)
    print()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def scanline_effect(lines=24):
    """Simulate faint scanlines for CRT effect."""
    for i in range(lines):
        if i % 2 == 0:
            sys.stdout.write(DIM_GREEN + " " * 80 + COLOR_RESET + "\n")
        else:
            sys.stdout.write("\n")
    sys.stdout.flush()
    sys.stdout.write("\033[H")  # move cursor to top-left

def display_logo():
    logo = r"""
   ____ ___ __  __ _____ ___   ___ 
  / ___|_ _|  \/  | ____|_ _| |_ _|
 | |    | || |\/| |  _|  | |   | | 
 | |___ | || |  | | |___ | |   | | 
  \____|___|_|  |_|_____|___| |___|
    """
    typewriter(logo, base_delay=0.002, flicker_chance=0.1)

def simulate_crt_flicker(lines):
    """Randomly brighten/dim each line to mimic CRT persistence."""
    flickered = []
    for line in lines:
        flicked_line = ""
        for char in line:
            if char.strip():  # only flick visible chars
                rand = random.random()
                if rand < 0.05:
                    color = DIM_GREEN
                elif rand > 0.95:
                    color = BRIGHT_GREEN
                else:
                    color = PHOSPHOR_GREEN
                flicked_line += color + char + COLOR_RESET
            else:
                flicked_line += char
        flickered.append(flicked_line)
    return flickered

def blinking_cursor():
    """Blink a cursor at the bottom without moving text."""
    try:
        while True:
            sys.stdout.write(PHOSPHOR_GREEN + CURSOR_CHAR + COLOR_RESET)
            sys.stdout.flush()
            time.sleep(0.5)
            sys.stdout.write("\b ")
            sys.stdout.flush()
            time.sleep(0.5)
    except KeyboardInterrupt:
        sys.stdout.write("\n")
        sys.stdout.flush()
        sys.stdout.write(SHOW_CURSOR)

def main_demo():
    clear_screen()
    print(HIDE_CURSOR, end="")  # hide the real cursor
    scanline_effect()
    display_logo()

    # Demo messages
    messages = [
        "[System] ComfyAI terminal demo loaded.",
        "User: Hello, ComfyAI!",
        "ComfyAI: Greetings, human. I am your vintage-style AI companion.",
        "User: How are you today?",
        "ComfyAI: I am processing your query...",
        "ComfyAI: Response generated successfully."
    ]

    displayed_lines = []
    for msg in messages:
        typewriter(msg + "\n", base_delay=0.01, flicker_chance=0.08)
        displayed_lines.append(msg)
        # Refresh flicker on all previous lines
        flickered = simulate_crt_flicker(displayed_lines)
        sys.stdout.write("\033[F" * len(flickered))  # move cursor up
        for line in flickered:
            print(line)
        time.sleep(0.3)

    typewriter("\nPress Ctrl+C to exit. Cursor will blink below.\n", flicker_chance=0.05)
    blinking_cursor()

if __name__ == "__main__":
    main_demo()
