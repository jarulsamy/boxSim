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

        self.image = np.ones((self.height, self.width, 3), np.uint8) * 255

        self.pt = None

        self.rectangle()
        self.update()

    def rectangle(self):
        """ Draw box """
        cv2.rectangle(self.image, tuple(self.rect1), tuple(self.rect2), (255,0,0), -1)

    def drawGoal(self):
        cv2.circle(self.image, tuple(self.pt), 10, (0, 255, 0), -1)
        self.update()
        # self.removeOldGoal()

    def update(self):
        """ Show image """
        self.rectangle()
        cv2.imshow("image", self.image)
        cv2.namedWindow("image")
        cv2.setMouseCallback("image", self.handleMousePress)

    def removeOldRect(self):
        """ Draw whitespace where old box was"""
        cv2.rectangle(self.image, tuple(self.rect1), tuple(self.rect2), (255, 255, 255), -1)

    def removeOldGoal(self):
        """ Draw whitespace where old drawGoal point was"""
        cv2.circle(self.image, tuple(self.pt), 10, (255, 255, 255), -1)

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

        self.removeOldRect()
    
    def handleMousePress(self, event, x, y, flags, param):
        """ Create goal circle based on mouse click"""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.pt = [x, y]
            self.drawGoal()
            

    def handleKeyPress(self, key):
        """ Take key press and move box"""
        self.key = key
        # W
        if self.key == 119:
            self.removeOldRect()
            self.rect1[1] -= 10
            self.rect2[1] -= 10
        # A
        if self.key == 97:
            self.removeOldRect()
            self.rect1[0] -= 10
            self.rect2[0] -= 10
        # S
        if self.key == 115:
            self.removeOldRect()
            self.rect1[1] += 10
            self.rect2[1] += 10
        # D
        if self.key == 100:
            self.removeOldRect()
            self.rect1[0] += 10
            self.rect2[0] += 10
        # ESC
        if self.key == 27:
            exit(0)

        if self.pt != None:
            self.drawGoal()

        self.keepOnScreen()
        
    def convertKeyToID(self, key):
        """ Convert key character to ID """

        if key == "w":
            self.key = 119
            
        elif key == "a":
            self.key = 97
        
        elif key == "s":
            self.key == 115
        
        elif key == "d":
            self.key == 100

        return self.key

    def runWASD(self):
        while True:
            self.rectangle()
            self.update()
            self.handleKeyPress(cv2.waitKey(0))


    # Function for box movement from code instead of keypresses
    def runEmulate(self, key): 
        """ Function for box movement from code instead of keypresses""" 
        self.rectangle()
        self.update()
        tempKey = self.convertKeyToID(key)
        self.handleKeyPress(tempKey)


if __name__ == "__main__":
    pass
