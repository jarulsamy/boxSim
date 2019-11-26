import numpy as np
import cv2
import tflearn
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.estimator import regression
from statistics import mean, median
from collections import Counter


def neural_network_model(input_size):
    LR = 0.001

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
    network = regression(network, optimizer="adam", learning_rate=LR,
                         loss="categorical_crossentropy", name="targets")
    model = tflearn.DNN(network, tensorboard_dir="j_log")

    return model


def train_model(training_data, model=False):
    X = np.array([i[0] for i in training_data]
                 ).reshape(-1, len(training_data[0][0]), 1)
    y = [i[1] for i in training_data]

    if not model:
        model = neural_network_model(input_size=len(X[0]))
    model.fit({'input': X}, {'targets': y}, n_epoch=5,
              snapshot_step=500, show_metric=True, run_id='openai_learning')

    return model
