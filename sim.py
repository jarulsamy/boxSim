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
        self.rect1 = [(self.width / 2) - 10, (self.height / 2) - 10]
        self.rect2 = [(self.width / 2) + 10, (self.height / 2) + 10]

        self.rect1 = [int(x) for x in self.rect1]
        self.rect2 = [int(x) for x in self.rect2]

        # Generate Blank Image based off of Passed Size     
        self.image = np.ones((self.height, self.width, 3), np.uint8) * 255

        # Predefine mouse click pt as none for draw logic later
        self.pt = None

        # Global distance map
        self.distanceList = []

        # Number of actions
        self.steps = 0

        # Generate and draw box
        self.rectangle()
        self.update()

    def rectangle(self):
        """ Draw box with centerpoint """
        self.rect1 = [int(x) for x in self.rect1]
        self.rect2 = [int(x) for x in self.rect2]

        cv2.rectangle(self.image, tuple(self.rect1), tuple(self.rect2), (255,0,0), -1)
        self.rectCenter = [(self.rect1[0] + self.rect2[0]) / 2, (self.rect1[1] + self.rect2[1]) / 2]
        self.rectCenter = [int(x) for x in self.rectCenter]
        cv2.circle(self.image, tuple(self.rectCenter), 4, (0, 0, 255), -1)

    def drawGoal(self):
        cv2.circle(self.image, tuple(self.pt), 10, (0, 255, 0), -1)
        self.update()

    def update(self, view=False):
        """ Show image if wanted, otherwise only update rectangle coords """
        self.rectangle()
        if view == True:
            cv2.imshow("image", self.image)
            cv2.namedWindow("image")
            cv2.setMouseCallback("image", self.handleMousePress)
        else:
            pass
        cv2.waitKey(1)

    def removeOldRect(self):
        """ Draw whitespace where old box was """
        cv2.rectangle(self.image, tuple(self.rect1), tuple(self.rect2), (255, 255, 255), -1)

    def removeOldGoal(self):
        """ Draw whitespace where old drawGoal point was """
        cv2.circle(self.image, tuple(self.pt), 10, (255, 255, 255), -1)

    def keepOnScreen(self):
        """ Keep box from moving off of screen """

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
        """ Create goal circle based on mouse click """
        if event == cv2.EVENT_LBUTTONDOWN:
            self.pt = [x, y]
            self.drawGoal()            

    def handleKeyPress(self, key):
        """ Take key press and move box """
        self.key = key
        
        # W Move box up
        if self.key == 119:
            self.removeOldRect()
            self.rect1[1] -= 10
            self.rect2[1] -= 10
        
        # A Move box left
        if self.key == 97:
            self.removeOldRect()
            self.rect1[0] -= 10
            self.rect2[0] -= 10
        
        # S Move box down
        if self.key == 115:
            self.removeOldRect()
            self.rect1[1] += 10
            self.rect2[1] += 10
       
        # D Move box right
        if self.key == 100:
            self.removeOldRect()
            self.rect1[0] += 10
            self.rect2[0] += 10
       
        # ESC Close the sim
        if self.key == 27:
            print("Completions: {}".format(self.completions))
            exit(0)

        # Spacebar Reset the sim
        if self.key == 32:
            self.removeOldRect()
            self.reset()

        if self.pt != None:
            self.drawGoal()

        self.keepOnScreen()
        self.steps += 1

    def calcDistance(self, p1, p2):
        """ Calculate distance between two points """
        self.distance = math.sqrt(((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2))
        return self.distance
        
    def getScore(self):
        """ Return positve score if distance to goal decreases,
        return negative score if distance to goal increases """
        if self.pt != None:
            ret = self.calcDistance(self.rectCenter, self.pt)
            self.distanceList.append(ret)
            if len(self.distanceList) > 2:
                if self.distanceList[-1] > self.distanceList[-2]:
                    return -1
                elif self.distanceList[-1] < self.distanceList[-2]:
                    return 1
                elif self.distanceList[-1] == self.distanceList[-2]:
                    return 0
            else:
                return 0
        
        return 0

    def getDoneStatus(self):
        ret = self.calcDistance(self.rectCenter, self.pt)
        if ret < 15:
            return True
        else:
            return False

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

    def runWASD(self, view=True, verbose=False):
        """ Run mode for humans """ 
        self.reset()
        self.completions = 0
        s = 0
        while True:
            
            self.rectangle()
            self.update(view)
            self.handleKeyPress(cv2.waitKey(0))
            
            if verbose == True:
                s += self.getScore()
                print(s, "SCORE")
                # print(self.getDoneStatus(), "DONE STATUS")
            
            if self.getDoneStatus():
                self.reset()
                self.completions += 1
                s = 0
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
        """ Reset simulator and pick random goal """
        # Try block if for some reason rect is not defined
        try:
            self.removeOldRect()
        except:
            pass

        self.rect1 = [(self.width / 2) - 10, (self.height / 2) - 10]
        self.rect2 = [(self.width / 2) + 10, (self.height / 2) + 10]

        if self.pt != None:
            self.removeOldGoal()
            self.randomGoal()
        else:
            self.randomGoal()
        
        self.steps = 0
        self.update(view)

    def randomActionSampler(self):
        """ Pick a random direction to move """
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
        """ Generate random goal for box to attempt to reach """
        x = random.randint(0, self.width)
        y = random.randint(0, self.height)  
        self.pt = [x ,y]
        self.drawGoal()

        return [x, y]

    # Get "observation" for RL training
    def getObservation(self):
        temp = self.calcDistance(self.rectCenter, self.pt)
        # temp = [temp, self.rectCenter, self.pt]
        temp = np.array([temp])
<<<<<<< HEAD
=======
        # temp = [[temp], [self.rectCenter], [self.pt]]
        # temp = np.array(temp)
>>>>>>> 727a3e6442132e61d4b01cacfdec1deb9847fdb9
        return temp

    # Redundant, remove me later
    def exit(self):
        exit(0)

    def getSteps(self):
        return self.steps


if __name__ == "__main__":
    pass
