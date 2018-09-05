import time
import cv2
import numpy as np

from sim import *

s = Simulator(512, 512)

# s.runWASD(verbose=True)

view = True

s.reset(view)

while True:
    s.emulateKeyPress("a", view=True)
    time.sleep(1)
    s.emulateKeyPress("d", view=True)
    time.sleep(1)
