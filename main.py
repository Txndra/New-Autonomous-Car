import os
import pygame
import pickle
import tkinter as tk
import tkinter.font as tkFont
from tkinter import *
from MapDesign import MapDesign
from constants import *
from simulation import Simulation

EMPTY_STRING = ''

class Application(tk.Frame): #Class to display main menu.
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.master = master
        self.pack()
        self.MapDict = None
        self.loadedWeights = None
        self.fontStyle = tkFont.Font(family="Lucida Grande", size=20)
        self.debug=False
        self.editorMode = False
        self.edit=False
        self.wireframe=False
        self.wireframeLine=False
        self.updateLines = False
        self.Lines = None
        self.trackWidth = TRACK_WIDTH
        # set changed=True if you want to edit a track or create a new one
        self.changed = True

        self.saveChange = False
        self.ThemeIndex = 3
        self.generation = 0
        self.showPanel = False
        self.displayMenu()
        global EMPTY_STRING
        



    def displayMenu(self):
        menuTitle = tk.Label(self, text = "Welcome to Sean's Autonomous Car Simulation",
            foreground = "black",
            background = "white",
            font = self.fontStyle
        ).pack(side = 'top')
        self.designMap = tk.Button(self, text = 'DESIGN A MAP', font = self.fontStyle, bg = 'black', fg = 'white', command = self.runMap).pack(side = 'top')
        self.designMap = tk.Button(self, text = 'QUIT', font = self.fontStyle, bg = 'black', fg = 'white', command = self.master.destroy).pack(side = 'bottom')
        self.designMap = tk.Button(self, text = 'RUN SIMULATION', font = self.fontStyle, bg = 'black', fg = 'white', command = self.runSim).pack(side = 'top')

    def runMap(self):
        map = MapDesign()
        
    def runSim(self):
        newsim = Simulation()



root = tk.Tk()
app = Application(master = root)
app.mainloop() 


