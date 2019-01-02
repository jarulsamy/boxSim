import sys
import random
import time
import cv2
import operator
import numpy as np
from sim import *
import tflearn
from termcolor import colored
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.estimator import regression
from statistics import mean, median
from collections import Counter


s = Simulator(512, 512)

LR = 1e-3

score_requirement = 100
initial_games = 200

def initial_population():
    
    training_data = []
    scores = []
    accepted_scores = []

    s.reset()

    for i in range(initial_games):

        view = False
        score = 0
        game_memory = []

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
        sys.stdout.write("{} {}".format(colored(" Training Game #{}".format(i), "green"), colored("Score: {}".format(score), "cyan")))
        print_progress(i, initial_games, prefix = 'Progress:', suffix = 'Complete')
        scores.append(score)

    training_data_save = np.array(training_data)
    np.save("training.npy", training_data_save)

    # print("Average Accepted Score:", mean(accepted_scores))
    # print("Median Score fro Accpeted Scores:", median(accepted_scores))
    print("Counter: ", Counter(accepted_scores))
    print("Largest: ", max(scores))
    # print("Training_Data: ", training_data)
    return training_data

# initial_population()

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
    network = regression(network, optimizer="adam", learning_rate = LR, loss="categorical_crossentropy", name="targets")
    model = tflearn.DNN(network, tensorboard_dir="j_log")

    return model

def train_model(training_data, model=False):
    X = np.array([i[0] for i in training_data]).reshape(-1,len(training_data[0][0]),1)
    # X = np.array(i[0] for i in training_/data]).reshape(-1,len(training_data[0][0], 1))
    y = [i[1] for i in training_data]

    if not model:
        model = neural_network_model(input_size = len(X[0]))
    model.fit({'input': X}, {'targets': y}, n_epoch=5, snapshot_step=500, show_metric=True, run_id='openai_learning')

    return model

training_data = initial_population()
try:
    model = train_model(training_data)
except:
    training_data = initial_population()
    model = train_model(training_data)

model.save("jm.model")

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

