import math
import cv2
import numpy as np

# Create simulator with height and width of window
class Simulator:
    """ Simulator built by Joshua Arulsamy """

    def __init__(self, height, width):
        self.height = height
        self.width = width

        # Center Rectangle in Simulator

        self.rect1 = [(self.width / 2) - 10, (self.height / 2) - 10]
        self.rect2 = [(self.width / 2) + 10, (self.height / 2) + 10]

        # Generate Blank Image based off of Passed Size     
        self.image = np.ones((self.height, self.width, 3), np.uint8) * 255

        # Predefine mouse click pt as none for draw logic later
        self.pt = None

        # Generate and draw box
        self.rectangle()
        self.update()

    def calcRectCenter(self):
        self.rectCenter = [(self.rect1[0] + self.rect2[0]) / 2, (self.rect1[1] + self.rect2[1]) / 2]

    def rectangle(self):
        """ Draw box with centerpoint """
        cv2.rectangle(self.image, tuple(self.rect1), tuple(self.rect2), (255,0,0), -1)
        self.calcRectCenter()
        cv2.circle(self.image, tuple(self.rectCenter), 4, (0, 0, 255), -1)

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

    def calcDistance(self, p1, p2):
        self.distance = math.sqrt(((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2))
        return self.distance
        
    def getScore(self):
        if self.pt != None:
            ret = self.calcDistance(self.rectCenter, self.pt)
            return ret

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
    def emulateKeyPress(self, key): 
        """ Function for box movement from code instead of keypresses""" 
        self.rectangle()
        self.update()
        tempKey = self.convertKeyToID(key)
        self.handleKeyPress(tempKey)

    def emulateMousePress(self, pt):
        self.pt = pt
        self.drawGoal()


if __name__ == "__main__":
    pass
