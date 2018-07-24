import time
import cv2
import numpy as np

from sim import *

# s = Simulator(512, 512)
rect1 = [200, 200]
rect2 = [210, 210]

image = np.ones((512, 512, 3), np.uint8) * 255
cv2.imshow("image", image)

for i in range(10):
    cv2.rectangle(image, tuple(rect1), tuple(rect2), (255,0,0), -1)
    rect1[0] += 10
    rect1[1] += 10

    rect2[0] += 10
    rect2[0] += 10

    cv2.imshow("image", image)

    time.sleep(1)

    cv2.waitKey(1)