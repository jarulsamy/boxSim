import sys
import random
import time
import cv2
import operator
import numpy as np
from sim import *
import tflearn
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.estimator import regression
from statistics import mean, median
from collections import Counter

s = Simulator(512, 512)

def neural_network_model(input_size):

    network = input_data(shape=[None, input_size, 1], name="input")

    network = fully_connected(network, 128, activation="relu")
    network = dropout(network, 0.8)

    network = fully_connected(network, 256, activation="relu")
    network = dropout(network, 0.8)

    network = fully_connected(network, 512, activation="relu")
    network = dropout(network, 0.8)

    network = fully_connected(network, 256, activation="relu")
    network = dropout(network, 0.8)

    network = fully_connected(network, 128, activation="relu")
    network = dropout(network, 0.8)

    network = fully_connected(network, 2, activation="softmax")
    network = regression(network, optimizer="adam", learning_rate = 1e-3, loss="categorical_crossentropy", name="targets")
    model = tflearn.DNN(network, tensorboard_dir="j_log")

    model.load('jm.model')

    return model

# try:
#     for i in range(256):
#         model = neural_network_model(i)
#         print(i)
# except:
#     pass

for i in range(256):
    try:
        model = neural_network_model(i)
    except:
        continue


scores = []
choices = []

for each_game in range(5):
    score = 0
    game_memory = []
    prev_obs = []
    steps = 0
    s.reset(view=True)
    for i in range(1000):
        
        if len(prev_obs) == 0: # prev_obs
            action = s.randomActionSampler()
        else:
            action = np.argmax(model.predict(prev_obs.reshape(-1,len(prev_obs),1))[0])
        
        choices.append(action)
        steps += 1

        if action == 0:
            s.emulateKeyPress("w", view=True)
            print("w")
        elif action == 1:
            s.emulateKeyPress("a", view=True)
            print("a")
        elif action == 2:
            s.emulateKeyPress("s", view=True)
            print("s")
        elif action == 3:
            s.emulateKeyPress("d", view=True)
            print("d")

        new_observation = s.getObservation()
        prev_obs = new_observation
        game_memory.append([new_observation, action])
        score += s.getScore()
        # cv2.waitKey(0)
        # time.sleep(.1)
        if steps > 150:
            s.reset()
            break
            
        if s.getDoneStatus():
            break
    
    scores.append(score)

print('Average Score:',sum(scores)/len(scores))
# print('choice 1:{}  choice 0:{}'.format(choices.count(1)/len(choices),choices.count(0)/len(choices)))
print("choices: {}".format(choices))
print("choice 0 (W): {}".format(choices.count(0)))
print("choice 1 (A): {}".format(choices.count(1)))
print("choice 2 (S): {}".format(choices.count(2)))
print("choice 3 (D): {}".format(choices.count(3)))
print(score_requirement)
