import numpy as np
import tensorflow as tf
import cv2
import random
from sim import Simulator
from tensorflow import keras
from tensorflow.keras.layers import Dense
from tqdm import tqdm

LR = 0.0001


def generate_model(in_dim, out_dim):
    inputs = keras.Input(shape=(in_dim,), name="Inputs")
    x = Dense(64, activation="relu")(inputs)
    x = Dense(64, activation="relu")(x)
    outputs = Dense(out_dim, activation="sigmoid", name="predictions")(x)

    model = keras.Model(inputs=inputs, outputs=outputs)

    model.summary()

    return model


# Designing an input for the neural network ------------------------------------
#
# Array with the following components:
#    (x)            (x)               (x)                         (y)
# Player Pos  |  Goal Pos  | Route taken to goal |              Score             |
#   (x, y)    |    (x, y)  |         (UDLR)      |    Diff of best and this route |


def generate_training_data(num_samples=1000):
    s = Simulator(
        512,
        512,
        "sim",
        display=False,
        action_callback=lambda pp, gp: random.choice(("UP", "DOWN", "LEFT", "RIGHT")),
    )

    for _ in tqdm(range(num_samples)):
        s.callback_game_loop()

    return s.best_routes_matrix


def callback_func_factory(model):
    def func(player_pos, goal_pos):
        inputs = np.zeros((1, 4))
        inputs[0, 0] = player_pos[0]
        inputs[0, 1] = player_pos[1]
        inputs[0, 2] = goal_pos[0]
        inputs[0, 3] = goal_pos[1]

        outputs = model(inputs, training=False).numpy()

        actions = {}
        actions["UP"] = outputs[0, 0]
        actions["DOWN"] = outputs[0, 1]
        actions["LEFT"] = outputs[0, 2]
        actions["RIGHT"] = outputs[0, 3]

        action = max(actions, key=actions.get)
        print(actions, action)
        return action

    return func


if __name__ == "__main__":
    # Get the data
    x_train, y_train = generate_training_data(10_000)

    print(x_train.shape)
    print(y_train.shape)

    # Prep the model
    model = generate_model(x_train.shape[1], y_train.shape[1])
    model.compile(
        optimizer=keras.optimizers.RMSprop(),
        loss=keras.losses.MeanSquaredError(),
        metrics=[keras.metrics.MeanSquaredError()],
    )

    # Train
    model.fit(x_train, y_train, epochs=100)
    model.save("model")

    # Evaluate
    s = Simulator(
        512,
        512,
        "Sim",
        display=True,
        action_callback=callback_func_factory(model),
    )
    for _ in range(10):
        s.callback_game_loop()
