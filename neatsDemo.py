import time
import cv2
import numpy as np
from sim import *


s = Simulator(512, 512)

s.emulateMousePress([20, 20])

print(s.getScore())
cv2.waitKey(0)


