import random
import time
import cv2
import operator
import numpy as np

from sim import  *

from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.estimator import regression

from statistics import mean, median
from collections import Counter

s = Simulator(512, 512)

LR = 1e-3
score_requirement = -5
inital_games = 1000
goal_steps = 115

def initial_population():

    training_data = []
    scores = []
    accepted_scores = []

    for j in range(goal_steps):

        view = False
        
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

                    score = s.getScore()

                    if s.getDoneStatus(): 
                        break

                if score >= score_requirement:
                    accepted_scores.append(score)
                    for data in game_memory:
                        if data[1] == 0:
                            output = [0, 0]
                        elif data[1] == 1:
                            output = [1, 0]
                        elif data[1] == 2:
                            output = [0, 1]
                        elif data[1] == 3:
                            output = [1, 1]
                        
                        training_data.append([data[0], output])

                s.reset()
                print("Training Game #{}".format(i))
                scores.append(score)
            