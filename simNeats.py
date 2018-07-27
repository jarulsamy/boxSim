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

LR = 1e-3
goal_steps = 1000
score_requirement = -5
initial_games = 300


def some_random_games_first():
    score = []
    s.randomGoal()
    for episode in range(5):
        for t in range(200):
            action = s.randomActionSampler()
            s.emulateKeyPress(action)
            sScore = s.getScore()
            # print(action)
            score.append(sScore)
            # print(max(score))
            # cv2.waitKey(0)
        # if done:
            # break

# some_random_games_first()

def initial_population():
    
    training_data = []
    scores = []
    accepted_scores = []

    # s.randomGoal() # Generate random goal for each game
    s.reset()

    for i in range(initial_games):
        view = False
        score = 0
        game_memory = []
        prev_observation = []

        for j in range(goal_steps):

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

    training_data_save = np.array(training_data)
    np.save("training.npy", training_data_save)

    print("Average Accepted Score:", mean(accepted_scores))
    print("Median Score fro Accpeted Scores:", median(accepted_scores))
    print(Counter(accepted_scores))

    return training_data


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
    y = [i[1] for i in training_data]

    if not model:
        model = neural_network_model(input_size = len(X[0]))
    model.fit({'input': X}, {'targets': y}, n_epoch=5, snapshot_step=500, show_metric=True, run_id='openai_learning')

    return model

training_data = initial_population()
print(training_data)
model = train_model(training_data)
model.save("jm.model")

scores = []
choices = []

for each_game in range(5):
    score = 0
    game_memory = []
    prev_obs = []
    s.reset(view=True)
    for i in range(goal_steps):
        
        if len(prev_obs) == 0: # prev_obs
            action = s.randomActionSampler()
        else:
            action = np.argmax(model.predict(prev_obs.reshape(-1,len(prev_obs),1))[0])
        
        choices.append(action)

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
        score = s.getScore()

        time.sleep(.1)
        if s.getDoneStatus():
            break
    
    scores.append(score)

print('Average Score:', sum(scores)/len(scores))
# print('choice 1:{}  choice 0:{}'.format(choices.count(1)/len(choices),choices.count(0)/len(choices)))
print("Score Requirement:", score_requirement)

