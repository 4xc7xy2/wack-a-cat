# dep
import tkinter as tk
import math
import random
import threading
import time
from decimal import Decimal

# This version of Whack-a-Cat uses Tkinter for a simple UI
# Tkinter is Python's built-in GUI toolkit. using it to:
#   - Draw clickable buttons instead of ASCII boxes
#   - Replace "ENTER" inputs with button clicks
#   - Use threading so that the cat appears/disappears on a timer


# global

class Config:
    SLEEP_SECS = (0.5, 10)
    SLEEP_POW  = 3

    SHOW_SECS = (0.6, 1)
    SHOW_POW  = 1

    # how big the grid is (2 rows tall, 3 boxes across)
    GRID_ROWS = 2
    GRID_COLS = 3


class GameData:
    is_whackable = False

    shown_count = 0
    hit_count   = 0
    miss_count  = 0

    whack_score = 0
    whackuracy  = 0

    # where the cat is on the grid (row, column)
    cat_position = (0, 0)

    @staticmethod
    def hit():
        GameData.hit_count += 1
        GameData.calc()

    @staticmethod
    def miss(apply=True):
        if apply:
            GameData.miss_count += 1
        GameData.calc()

    @staticmethod
    def reset():
        GameData.is_whackable = False
        GameData.cat_position = (0, 0)
        GameData.shown_count = 0
        GameData.hit_count = 0
        GameData.miss_count = 0
        GameData.calc()

    @staticmethod
    def calc():
        GameData.whack_score = GameData.hit_count - GameData.miss_count

        ratio_div = GameData.shown_count + GameData.miss_count
        ratio = Decimal(GameData.hit_count / ratio_div if ratio_div > 0 else 0)
        GameData.whackuracy = round(ratio, 2)


# util

def randrange_pow(range_vals, pow_val):
    r = math.pow(random.random(), pow_val)
    return (r * (range_vals[1] - range_vals[0])) + range_vals[0]

class WhackACatUI:
    def __init__(self, root):

        self.root = root
        self.root.title("Whack-a-Cat 🐱")
        self.root.resizable(False, False)

        self.score_label = tk.Label(root, text="Score: 0", font=("Arial", 16))
        self.score_label.pack()

        self.acc_label = tk.Label(root, text="Whackuracy: 0.0", font=("Arial", 14))
        self.acc_label.pack()

        # Create a frame to hold the grid of buttons
        self.grid_frame = tk.Frame(root)
        self.grid_frame.pack(pady=10)

        # Create the clickable boxes as buttons in a grid layout
        self.buttons = []
        for r in range(Config.GRID_ROWS):
            row = []
            for c in range(Config.GRID_COLS):
                btn = tk.Button(
                    self.grid_frame,
                    text="📦",
                    font=("Arial", 24),
                    width=6,
                    height=2,
                    command=lambda r=r, c=c: self.whack(r, c)
                )
                btn.grid(row=r, column=c, padx=5, pady=5)
                row.append(btn)
            self.buttons.append(row)

        self.start_button = tk.Button(
            root,
            text="Start Game",
            font=("Arial", 14),
            command=self.start_game
        )
        self.start_button.pack(pady=10)

        self.running = False

    def update_labels(self):
        self.score_label.config(text=f"Score: {GameData.whack_score}")
        self.acc_label.config(text=f"Whackuracy: {GameData.whackuracy}")

    def clear_grid(self):
        for row in self.buttons:
            for btn in row:
                btn.config(text="📦", bg="SystemButtonFace")

    def show_cat(self):
        # Choose random position for cat
        GameData.cat_position = (
            random.randint(0, Config.GRID_ROWS - 1),
            random.randint(0, Config.GRID_COLS - 1)
        )

        r, c = GameData.cat_position
        self.buttons[r][c].config(text="🐱", bg="pink")

    def whack(self, r, c):
        if not GameData.is_whackable:
            GameData.miss()
        else:
            if (r, c) == GameData.cat_position:
                GameData.hit()
                GameData.is_whackable = False
                self.clear_grid()  # remove the cat
            else:
                GameData.miss()
        self.update_labels()

    # Game loop (running in a separate thread so UI doesn't freeze)

    def cat_loop(self):
        GameData.reset()
        self.running = True

        while self.running:
            # Clear grid between appearances
            self.clear_grid()
            self.update_labels()

            sleep_secs = randrange_pow(Config.SLEEP_SECS, Config.SLEEP_POW)
            time.sleep(sleep_secs)

            hits_before = GameData.hit_count

            GameData.shown_count += 1
            GameData.is_whackable = True
            self.root.after(0, self.show_cat)  # schedule UI updates safely

            show_secs = randrange_pow(Config.SHOW_SECS, Config.SHOW_POW)
            time.sleep(show_secs)

            if hits_before == GameData.hit_count:
                GameData.miss(False)
            GameData.is_whackable = False

        print("Game loop ended")

    def start_game(self):
        if not self.running:
            GameData.reset()
            self.running = True
            self.start_button.config(state="disabled", text="Game Running...")
            threading.Thread(target=self.cat_loop, daemon=True).start()

# main

def main():
    root = tk.Tk()
    app = WhackACatUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()