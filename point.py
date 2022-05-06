import pygame
from constants import Width, Height, Green, Black, White
from math import sqrt

class Point:
    #class for points of the spline
    def __init__(self, x=Width//2, y=Height//2, radius=5, color=(40,240,235)):
        self.x = x
        self.y = y
        self.color = color #Sets colour of movable points
        self.temp = color
        self.selectColor = (255,0,0) #If colour is selected it changes colour.
        self.radius = radius #Radius set for click
        self.selected = False #Variable to check whether the point has been selected
        self.label = None
        self.labelColor = Green
        self.fontSize = 25
        self.length = 0

    def parseToInt(self):
        return (int(self.x), int(self.y)) #returns integer values for the x and y coordinates


    def update(self, clicked):
        mouseX, mouseY = pygame.mouse.get_pos() #uses pygame library to get the cooridnates of the mouse in x and y

        if clicked == True and self.selected == False:
            dist = GetDistance(mouseX, mouseY, self.x, self.y) #Calculates distance between the point and mouse click to determine whether 
            #the user has clicked it
            if dist <= self.radius: #Allows space for user error
                self.selected = True 
                self.color = self.selectColor #Changes colour when he point is clicked
        elif clicked == True and self.selected == True: #If the point is clicked again it gets deselected and returns to the original colour
            self.selected = False
            self.color = self.temp

        if self.selected == True:
            #Changes coordinates of the point to follow the mouse
            self.x = mouseX 
            self.y = mouseY


    def Draw(self, screen):
        pygame.draw.circle(screen, self.color, self.parseToInt(), self.radius)
        if self.label:
            font = pygame.font.Font('freesansbold.ttf', self.fontSize)
            text = font.render(self.label, True, self.labelColor)
            textRect = text.get_rect()
            setattr(textRect, "center", (self.x, self.y+30)) #sets the named arrtibute on the given object to the value
            screen.blit(text, textRect)
    
def GetDistance(x1, y1, x2, y2):
        return sqrt( (x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1)) #Mathematical formula to calculate distance (square root of the sum of distances)