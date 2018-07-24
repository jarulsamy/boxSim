import random
import math
import cv2
import numpy as np

# Create simulator with height and width of window
class Simulator:
    """ Simulator built by Joshua Arulsamy 
    
    Args: Height and Width of window"""
    def __init__(self, height, width):
        self.height = height
        self.width = width

        # Center Rectangle in Simulator
        # Save a copy to use to reset simulator

        self.rect1Original = [(self.width / 2) - 10, (self.height / 2) - 10]
        self.rect2Original = [(self.width / 2) + 10, (self.height / 2) + 10]
        
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

    def update(self, view=False):
        """ Show image """
        self.rectangle()
        if view == True:
            cv2.imshow("image", self.image)
            cv2.namedWindow("image")
            cv2.setMouseCallback("image", self.handleMousePress)
        else:
            pass
        cv2.waitKey(1)

    def removeOldRect(self):
        """ Draw whitespace where old box was"""
        cv2.rectangle(self.image, tuple(self.rect1), tuple(self.rect2), (255, 255, 255), -1)

    def removeOldGoal(self):
        """ Draw whitespace where old drawGoal point was"""
        cv2.circle(self.image, tuple(self.pt), 10, (255, 255, 255), -1)

    def goalStatus(self):
        if self.pt != None:
            return True
        else:
            return False
    
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
            ret = self.calcDistance(self.rectCenter, self.pt) ** 2
            return -ret

    def convertKeyToID(self, key):
        """ Convert key character to ID """

        if key == "w":
            self.key = 119
            return self.key

        elif key == "a":
            self.key = 97
            return self.key

        elif key == "s":
            self.key = 115
            return self.key

        elif key == "d":
            self.key = 100
            return self.key


    def runWASD(self):
        while True:
            self.rectangle()
            self.update()
            self.handleKeyPress(cv2.waitKey(0))
            print(self.getScore())


    # Function for box movement from code instead of keypresses
    def emulateKeyPress(self, key, view=False): 
        """ Function for box movement from code instead of keypresses""" 
        self.rectangle()
        self.update(view)
        tempKey = self.convertKeyToID(key)
        self.handleKeyPress(tempKey)

    def setGoal(self, pt):
        """ Function for goal point from code instead of mouse down """
        self.pt = pt
        self.drawGoal()

    def reset(self, view=False):
        self.rect1 = self.rect1Original
        self.rect2 = self.rect2Original

        if self.pt != None:
            self.removeOldGoal()
            self.randomGoal()
        else:
            self.randomGoal
        self.update(view)

    def randomActionSampler(self):
        i = random.randint(0,3)
        # if i == 0:
        #     return "w"
        # elif i == 1:
        #     return "a"
        # elif i == 2:
        #     return "s"
        # elif i == 3:
        #     return "d"
        return i

    def randomGoal(self):
        x = random.randint(0, self.width)
        y = random.randint(0, self.height)  
        self.pt = [x ,y]
        self.drawGoal()

        return [x, y]

    def getObservation(self):
        temp = self.calcDistance(self.rectCenter, self.pt)
        return [temp]

    def exit(self):
        exit(0)
if __name__ == "__main__":
    pass
