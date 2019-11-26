# -*- coding: utf-8 -*-

import sys
import cv2
import numpy as np
from threading import Thread

from sim import *

from statistics import mean, median
from collections import Counter

from termcolor import colored

LR = 1e-3

# goal_steps = 150 # Irrelevant

score_requirement = 90
initial_games = 100


def print_progress(iteration, total, prefix='', suffix='', decimals=1, bar_length=50):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        bar_length  - Optional  : character length of bar (Int)
    """
    str_format = "{0:." + str(decimals) + "f}"
    percents = str_format.format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = '█' * filled_length + '-' * (bar_length - filled_length)

    sys.stdout.write('\r%s |%s| %s%s %s' %
                     (prefix, bar, percents, '%', suffix)),

    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()


def initial_population(s):

    # Inital empty variable decleration
    training_data = []
    scores = []
    accepted_scores = []

    s.reset()  # Start fresh sim
    print_progress(0, initial_games, prefix='Progress:', suffix='Complete')
    for i in range(initial_games):

        view = False  # Don't render games, much faster
        score = 0
        game_memory = []
        prev_observation = []

        # for j in range(goal_steps):
        while not s.getDoneStatus():
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

            val = s.getScore()
            score += int(val)

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

        # print("Training Game #{} Score: {} ".format(i, score))
        sys.stdout.write("{} {}".format(colored(" Training Game #{}".format(
            i), "green"), colored("Score: {}".format(score), "cyan")))
        print_progress(i, initial_games, prefix='Progress:', suffix='Complete')
        scores.append(score)

    training_data_save = np.array(training_data)
    np.save("training.npy", training_data_save)

    # print("Average Accepted Score:", mean(accepted_scores))
    # print("Median Score fro Accpeted Scores:", median(accepted_scores))
    print("Counter: ", Counter(accepted_scores))
    print("Largest: ", max(scores))
    # print("Training_Data: ", training_data)
    return training_data


class thread1(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.s = Simulator(512, 512)

    def run(self):
        ret = initial_population(self.s)
        return ret


class thread2(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.s = Simulator(512, 512)

    def run(self):
        ret = initial_population(self.s)
        return ret


class thread3(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.s = Simulator(512, 512)

    def run(self):
        ret = initial_population(self.s)
        return ret


class thread4(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.s = Simulator(512, 512)

    def run(self):
        ret = initial_population(self.s)
        return ret


threadObj1 = thread1()
threadObj2 = thread2()
threadObj3 = thread3()
threadObj4 = thread4()

threadObj1.start()
threadObj2.start()
threadObj3.start()
threadObj4.start()

threadObj1.join()
threadObj2.join()
threadObj3.join()
threadObj4.join()

print("Thread 1: ", threadObj1)
print("Thread 2: ", threadObj2)
print("Thread 3: ", threadObj3)
print("Thread 4: ", threadObj4)
