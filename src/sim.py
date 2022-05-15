#!/usr/bin/env python3

import random
from collections import defaultdict

import cv2
import numpy as np
import random


def empty_path():
    return {"UP": 0, "DOWN": 0, "LEFT": 0, "RIGHT": 0}


class Pt:
    def __init__(self, x, y):
        """Helper class to represent a point."""
        self.x = x
        self.y = y

    def __iter__(self):
        """Get the point as a tuple."""
        pt = (self.x, self.y)
        for i in pt:
            yield i

    def __eq__(self, rhs):
        """Check if two points 'point' to the same point."""
        return self.x == rhs.x and self.y == rhs.y

    def __add__(self, rhs):
        if isinstance(rhs, Pt):
            return Pt(self.x + rhs.x, self.y + rhs.y)
        else:
            return Pt(self.x + rhs, self.y + rhs)

    def __sub__(self, rhs):
        if isinstance(rhs, Pt):
            return Pt(self.x - rhs.x, self.y - rhs.y)
        else:
            return Pt(self.x - rhs, self.y - rhs)

    def __repr__(self):
        return f"Pt(x={self.x}, y={self.y})"


class Simulator:
    PLAYER_DIM = 16
    MOVE_INC = PLAYER_DIM
    BACKGROUND_COLOR = (255, 255, 255)
    PLAYER_COLOR = (255, 0, 0)
    GOAL_COLOR = (0, 0, 255)

    KEYMAP = {
        "UP": ("w", "k"),
        "DOWN": ("s", "j"),
        "LEFT": ("a", "h"),
        "RIGHT": ("d", "l"),
        "QUIT": (chr(27), "q"),
    }

    _goal = None

    def __init__(
        self,
        height,
        width,
        win_name="Simulator",
        display=True,
        action_callback=None,
        *callback_args,
    ):
        self.height = height
        self.width = width
        self.display = display
        self.win_name = win_name

        self.FUNCMAP = {
            "UP": self.player_up,
            "DOWN": self.player_down,
            "LEFT": self.player_left,
            "RIGHT": self.player_right,
        }
        self._routes = defaultdict(empty_path)

        self.reset()

        if action_callback is None:
            self._user_game_loop()
        else:
            self._action_callback = action_callback
            self._action_callback_args = callback_args

    def reset(self):
        self.steps = 0

        self._empty_canvas()

        self._player = Pt(self.width // 2, self.height // 2)
        self._goal_generate()
        self._current_route_key = (tuple(self._player), tuple(self._goal))

        self._update()

    def _empty_canvas(self):
        self.frame = np.ones((self.height, self.width, 3), np.uint8)
        self.frame[self.frame.all(axis=2)] = self.BACKGROUND_COLOR

    def _goal_generate(self):
        self._goal_erase()
        self._goal = self._player

        while self._goal == self._player:
            max_x = (self.width // self.PLAYER_DIM) - 1
            max_y = (self.height // self.PLAYER_DIM) - 1

            self._goal = Pt(
                random.randint(1, max_x) * self.PLAYER_DIM,
                random.randint(1, max_y) * self.PLAYER_DIM,
            )
        self._goal_draw()

    def _goal_draw(self, color=GOAL_COLOR):
        offset = self.PLAYER_DIM // 2
        top_left = self._goal - offset
        bottom_right = self._goal + offset
        cv2.rectangle(
            self.frame,
            tuple(top_left),
            tuple(bottom_right),
            color,
            -1,
        )

    def _goal_erase(self):
        if self._goal is not None:
            self._goal_draw(color=self.BACKGROUND_COLOR)

    def _player_draw(self, color=PLAYER_COLOR):
        offset = self.PLAYER_DIM // 2
        top_left = Pt(self._player.x - offset, self._player.y - offset)
        bottom_right = Pt(self._player.x + offset, self._player.y + offset)
        cv2.rectangle(
            self.frame,
            tuple(top_left),
            tuple(bottom_right),
            color,
            -1,
        )

    def _player_erase(self):
        self._player_draw(color=self.BACKGROUND_COLOR)

    def _update(self):
        if self.display:
            self._player_draw()
            cv2.imshow(self.win_name, self.frame)
            cv2.namedWindow(self.win_name)

    @property
    def player_pos(self):
        return self._player

    @property
    def goal_pos(self):
        return self._player

    @property
    def best_route(self):
        best = empty_path()
        diff = self._goal - self._player

        horz = diff.x // self.PLAYER_DIM
        vert = diff.y // self.PLAYER_DIM

        if vert < 0:
            best["UP"] = abs(vert)
        elif vert > 0:
            best["DOWN"] = vert
        if horz > 0:
            best["RIGHT"] = horz
        elif horz < 0:
            best["LEFT"] = abs(horz)

        return best

    @property
    def routes(self):
        return dict(self._routes)

    def player_up(self):
        self._routes[self._current_route_key]["UP"] += 1
        new_pos = self._player.y - self.MOVE_INC
        if new_pos + self.PLAYER_DIM <= self.height and new_pos - self.PLAYER_DIM >= 0:
            self._player.y = new_pos

    def player_down(self):
        self._routes[self._current_route_key]["DOWN"] += 1
        new_pos = self._player.y + self.MOVE_INC
        if new_pos + self.PLAYER_DIM <= self.height and new_pos - self.PLAYER_DIM >= 0:
            self._player.y = new_pos

    def player_left(self):
        self._routes[self._current_route_key]["LEFT"] += 1
        new_pos = self._player.x - self.MOVE_INC
        if new_pos + self.PLAYER_DIM <= self.width and new_pos - self.PLAYER_DIM >= 0:
            self._player.x = new_pos

    def player_right(self):
        self._routes[self._current_route_key]["RIGHT"] += 1
        new_pos = self._player.x + self.MOVE_INC
        if new_pos + self.PLAYER_DIM <= self.height and new_pos - self.PLAYER_DIM >= 0:
            self._player.x = new_pos

    def _handle_key_press(self, key):
        self._player_erase()
        key = chr(key)
        if key in self.KEYMAP["QUIT"]:
            return False
        elif key in self.KEYMAP["UP"]:
            self.FUNCMAP["UP"]()
        elif key in self.KEYMAP["DOWN"]:
            self.FUNCMAP["DOWN"]()
        elif key in self.KEYMAP["LEFT"]:
            self.FUNCMAP["LEFT"]()
        elif key in self.KEYMAP["RIGHT"]:
            self.FUNCMAP["RIGHT"]()

        self._update()
        return True

    def _user_game_loop(self):
        self._update()
        run = True
        while run:
            # print(f"Best path: {self.best_route}")
            self.reset()

            while self._player != self._goal:
                self._update()
                if not self._handle_key_press(cv2.waitKey(0)):
                    run = False
                    break

            print(f"Steps taken: {self._routes[self._current_route_key]}")
            self._goal_generate()
            self._update()

    def callback_game_loop(self):

        self._goal_generate()
        self._update()
        self.reset()

        while self._player != self._goal:
            self._update()
            action = self._action_callback(*self._action_callback_args)
            if action == "QUIT":
                break
            self._player_erase()
            self.FUNCMAP[action]()
            self._update()

            if self.display:
                try:
                    if chr(cv2.waitKey(5)) in self.KEYMAP["QUIT"]:
                        break
                except ValueError:
                    pass

        print(f"Steps taken: {self._routes[self._current_route_key]}")

        if self.display:
            cv2.waitKey(0)


state = 500


if __name__ == "__main__":
    collection = Simulator(
        512,
        512,
        "sim",
        display=False,
        action_callback=lambda: random.choice(("UP", "DOWN", "LEFT", "RIGHT")),
    )

    for i in range(100):
        collection.callback_game_loop()

    print(collection.routes)
