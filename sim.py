import cv2
import numpy as np

# Create simulator with height and width of window
class Simulator:
    """ Simulator built by Joshua Arulsamy """

    def __init__(self, height, width):
        self.height = height
        self.width = width

        self.rect1 = [(self.width / 2) - 10, (self.height / 2) - 10]
        self.rect2 = [(self.width / 2) + 10, (self.height / 2) + 10]

        self.key = int

        self.image = np.ones((self.height, self.width, 3), np.uint8) * 255

    def rectangle(self):
        """ Draw box """
        cv2.rectangle(self.image, tuple(self.rect1), tuple(self.rect2), (255,0,0), -1)

    def update(self):
        """ Show image """
        cv2.imshow("image", self.image)

    def removeOld(self):
        """ Draw whitespace where old box was"""
        cv2.rectangle(self.image, tuple(self.rect1), tuple(self.rect2), (255, 255, 255), -1)

    def keepOnScreen(self):
        """ Keep box from moving off of screen"""

        if self.rect1[0] < 0:
            self.rect1[0] += 10
            self.rect2[0] += 10

        if self.rect1[1] < 0:
            self.rect1[1] += 10
            self.rect2[1] += 10

        if self.rect2[0] > self.width:
            self.rect1[0] -= 10
            self.rect2[0] -= 10

        if self.rect2[1] > self.height:
            self.rect1[1] -= 10
            self.rect2[1] -= 10

        self.removeOld()

    def handleKeyPress(self, key):
        """ Take key press and move box"""
        self.key = key
        # W
        if self.key == 119:
            self.removeOld()
            self.rect1[1] -= 10
            self.rect2[1] -= 10
        # A
        if self.key == 97:
            self.removeOld()
            self.rect1[0] -= 10
            self.rect2[0] -= 10
        # S
        if self.key == 115:
            self.removeOld()
            self.rect1[1] += 10
            self.rect2[1] += 10
        # D
        if self.key == 100:
            self.removeOld()
            self.rect1[0] += 10
            self.rect2[0] += 10
        # ESC
        if self.key == 27:
            exit(0)

        self.keepOnScreen()

    def run(self):
        while True:
            self.rectangle()
            self.update()
            self.handleKeyPress(cv2.waitKey(0))

s = Simulator(512, 512)
s.run()

