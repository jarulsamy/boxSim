from pickle import UnpicklingError
import numpy as np
import tensorflow as tf
import cv2
import random
from sim import Simulator
from tensorflow import keras
from tensorflow.keras.layers import Dense
from tqdm import tqdm
from pathlib import Path


def generate_model(in_dim, out_dim):
    # Input
    inputs = keras.Input(shape=(in_dim,), name="Inputs")
    # Normalization
    x = tf.keras.layers.LayerNormalization()(inputs)
    x = Dense(64, activation="relu")(x)
    x = Dense(64, activation="relu")(x)
    outputs = Dense(out_dim, activation="sigmoid", name="predictions")(x)

    model = keras.Model(inputs=inputs, outputs=outputs)

    model.summary()

    return model


# Designing an input for the neural network ------------------------------------
#
#    (x)            (x)         (y)
# Player Pos  |  Goal Pos  | Best Route  |
#   (x, y)    |    (x, y)  |   (UDLR)    |


def generate_training_data(num_samples=1000):
    def gen_callback(*args):
        return "QUIT"

    x_path = Path("x.npy")
    y_path = Path("y.npy")

    try:
        x = np.load(x_path)
        y = np.load(y_path)
        x_rows, _ = x.shape
        y_rows, _ = y.shape
        if x_rows == y_rows == num_samples + 1:
            return x, y
    except (OSError, ValueError, UnpicklingError):
        pass

    s = Simulator(
        512,
        512,
        "sim",
        display=False,
        action_callback=gen_callback,
    )

    for _ in tqdm(range(num_samples)):
        s.callback_game_loop()

    x, y = s.best_routes_matrix
    np.save("x.npy", x)
    np.save("y.npy", y)

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
    LR = 0.00001
    BATCH_SIZE = 256
    EPOCHS = 64

    # Get the data
    x_train, y_train = generate_training_data(50_000)

    # Prep the model
    model = generate_model(x_train.shape[1], y_train.shape[1])
    model.compile(
        optimizer=keras.optimizers.RMSprop(learning_rate=LR),
        loss=keras.losses.MeanSquaredError(),
        metrics=[keras.metrics.MeanSquaredError()],
    )

    # Train
    model.fit(x_train, y_train, batch_size=BATCH_SIZE, epochs=EPOCHS)
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
