#!/usr/bin/env python3
"""
Simple simulator for the shortest-path-to-target problem.

+------------------------------------------------------------------------------+
|                                                                              |
|          □ -------------------------------------                             |
|          ^(player)                             |                             |
|                                                |                             |
|                                                ■                             |
|                                                ^(target)                     |
|                                                                              |
+------------------------------------------------------------------------------+
"""

import random
import time
from collections import defaultdict
from typing import Callable, Optional, Union

import cv2
import numpy as np


def empty_path() -> dict[str, int]:
    """Get an empty path."""
    return {"UP": 0, "DOWN": 0, "LEFT": 0, "RIGHT": 0}


class Pt:
    """Represent a point in 2D space."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __iter__(self):
        """Get the point as an iterable."""
        pt = (self.x, self.y)
        for i in pt:
            yield i

    def __eq__(self, rhs):
        """Check if two points 'point' to the same point."""
        return self.x == rhs.x and self.y == rhs.y

    def __add__(self, rhs: Union[float]):
        """Add two points together."""
        if isinstance(rhs, Pt):
            return Pt(self.x + rhs.x, self.y + rhs.y)
        else:
            return Pt(self.x + rhs, self.y + rhs)

    def __sub__(self, rhs):
        """Subtract two points."""
        if isinstance(rhs, Pt):
            return Pt(self.x - rhs.x, self.y - rhs.y)
        else:
            return Pt(self.x - rhs, self.y - rhs)

    def __repr__(self):
        """Debug output."""
        return f"Pt(x={self.x}, y={self.y})"

    @property
    def np(self):
        """Get Pt as numpy array."""
        return np.array([self.x, self.y])


class Simulator:
    """2D Simulator for shortest-path-to-target problem."""

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
        height: int,
        width: int,
        win_name: Optional[str] = "Simulator",
        display: Optional[bool] = True,
        player_start_pos: Optional[Pt] = None,
        action_callback: Optional[Callable] = None,
        *callback_args,
    ):
        self._height = height
        self._width = width
        self._display = display
        self._player_start_pos = None
        self._win_name = win_name

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
        """Reset all actions taken by the player."""
        self._steps = 0
        self._empty_canvas()

        if self._player_start_pos is None:
            x = random.randint(0, (self._width // self.PLAYER_DIM) - 1)
            y = random.randint(0, (self._height // self.PLAYER_DIM) - 1)

            x *= self.PLAYER_DIM
            y *= self.PLAYER_DIM

            self._player = Pt(x, y)
        else:
            self._player = self._player_start_pos

        self._goal_generate()
        self._current_route_key = (tuple(self._player), tuple(self._goal))
        while self._current_route_key in self._routes.keys():
            self._goal_generate()
            self._current_route_key = (tuple(self._player), tuple(self._goal))

        self._routes[self._current_route_key]

        self._update()

    def _empty_canvas(self):
        self.frame = np.ones((self._height, self._width, 3), np.uint8)
        self.frame[self.frame.all(axis=2)] = self.BACKGROUND_COLOR

    def _goal_generate(self):
        self._goal_erase()
        self._goal = self._player

        max_x = (self._width // self.PLAYER_DIM) - 1
        max_y = (self._height // self.PLAYER_DIM) - 1
        while self._goal == self._player:
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
        if self._display:
            self._player_draw()
            cv2.imshow(self._win_name, self.frame)
            cv2.namedWindow(self._win_name)

    @property
    def player_pos(self) -> Pt:
        """Get the current position of the player."""
        return self._player

    @property
    def goal_pos(self) -> Pt:
        """Get the current position of the goal."""
        return self._goal

    @property
    def player_goal_distance(self) -> float:
        """Get the distance between the player and the goal."""
        route = self.best_route
        return sum(route.values())

    def best_route(self, player: Optional[Pt] = None, goal: Optional[Pt] = None):
        """Get the best route from the player to the goal."""
        best = empty_path()

        if player is None and goal is None:
            diff = self._goal - self._player
        else:
            diff = goal - player

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
    def routes(self) -> dict:
        """Get all the routes."""
        return dict(self._routes)

    @property
    def best_routes_matrix(self) -> np.array:
        """Get the best route as a numpy array."""
        x = np.empty((0, 4))
        y = np.empty((0, 4))
        for k, v in self.routes.items():
            x_row = np.zeros((1, 4))
            y_row = np.zeros((1, 4))

            # Player start position
            player = Pt(k[0][0], k[0][1])
            x_row[0, 0] = player.x
            x_row[0, 1] = player.y

            # Goal start position
            goal = Pt(k[1][0], k[1][1])
            x_row[0, 2] = goal.x
            x_row[0, 3] = goal.y
            x = np.vstack((x, x_row))

            # Outputs
            best_route = self.best_route(player, goal)
            y_row[0, 0] = best_route["UP"]
            y_row[0, 1] = best_route["DOWN"]
            y_row[0, 2] = best_route["LEFT"]
            y_row[0, 3] = best_route["RIGHT"]

            y = np.vstack((y, y_row))

        return x, y

    def player_up(self) -> None:
        """Move the player up one cell."""
        self._routes[self._current_route_key]["UP"] += 1
        new_pos = self._player.y - self.MOVE_INC
        if new_pos + self.PLAYER_DIM <= self._height and new_pos - self.PLAYER_DIM >= 0:
            self._player.y = new_pos

    def player_down(self) -> None:
        """Move the player down one cell."""
        self._routes[self._current_route_key]["DOWN"] += 1
        new_pos = self._player.y + self.MOVE_INC
        if new_pos + self.PLAYER_DIM <= self._height and new_pos - self.PLAYER_DIM >= 0:
            self._player.y = new_pos

    def player_left(self) -> None:
        """Move the player left one cell."""
        self._routes[self._current_route_key]["LEFT"] += 1
        new_pos = self._player.x - self.MOVE_INC
        if new_pos + self.PLAYER_DIM <= self._width and new_pos - self.PLAYER_DIM >= 0:
            self._player.x = new_pos

    def player_right(self) -> None:
        """Move the player right one cell."""
        self._routes[self._current_route_key]["RIGHT"] += 1
        new_pos = self._player.x + self.MOVE_INC
        if new_pos + self.PLAYER_DIM <= self._height and new_pos - self.PLAYER_DIM >= 0:
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

    def callback_game_loop(self) -> None:
        """Initiate a game loop by using the action callback to get player movements."""
        self._goal_generate()
        self._update()
        self.reset()

        while self._player != self._goal:
            self._update()
            action = self._action_callback(
                self._player.np,
                self._goal.np,
                *self._action_callback_args,
            )
            if action == "QUIT":
                break
            self._player_erase()
            self.FUNCMAP[action]()
            self._update()

            if self._display:
                time.sleep(0.1)
                try:
                    if chr(cv2.waitKey(5)) in self.KEYMAP["QUIT"]:
                        break
                except ValueError:
                    pass

        if self._display:
            print(f"Steps taken: {self._routes[self._current_route_key]}")

        if self._display:
            cv2.waitKey(0)


if __name__ == "__main__":
    s = Simulator(512, 512)
