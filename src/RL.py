# Reinforment Learning SIM Solver #

import cv2
import numpy as np

from sim import *


inital_games = 1000
steps = 100000

s = Simulator(512, 512)


def random_games():
    scores = []
    steps = 200
    view = True
    s.reset()
    for episode in range(5):
        for t in range(steps):
            action = s.randomActionSampler()

            if action == 0:
                s.emulateKeyPress("w", view)
            elif action == 1:
                s.emulateKeyPress("a", view)
            elif action == 2:
                s.emulateKeyPress("s", view)
            elif action == 3:
                s.emulateKeyPress("d", view)

            score = s.getScore()
            scores.append(score)

            print("Score:", score)
            print(s.getDoneStatus())

        if s.getDoneStatus():
            break


def dataGathering():

    training_data = []
    scores = []
    accepted_scores = []

    s.reset()

    for i in range(inital_games):
        view = False
        score = 0
        game_memory = []
        prev_observation = []

        for j in range(steps):

            action = s.randomActionSampler()

            if action == 0:
                s.emulateKeyPress("w", view)
            elif action == 1:
                s.emulateKeyPress("a", view)
            elif action == 2:
                s.emulateKeyPress("s", view)
            elif action == 3:
                s.emulateKeyPress("d", view)

            observation = s.getObservation()

            if len(prev_observation) > 0:
                game_memory.append([prev_observation, action])

            prev_observation = observation
