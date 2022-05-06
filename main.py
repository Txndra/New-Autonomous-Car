from asyncio import constants
import os
import pygame
import pickle
import neat
from point import Point, GetDistance
from spline import Spline
from math import sin, radians, degrees, copysign, sqrt
from pygame.math import Vector2
from car import Car
from CT import CT
from constants import *
from UI.setup import *
import sys
import tkinter as tk
from tkinter import messagebox
import tkinter.font as tkFont
from tkinter.filedialog import askopenfilename
from typing import Type
import simulation as sim

class Application(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.master = master
        self.pack()
        self.MapDict = None
        self.fontStyle = tkFont.Font(family = "Lucida Grande", size = 20)
        self.debug=False
        self.editorMode = False
        self.edit=False
        self.wireframe=False
        self.wireframeLine=False
        self.updateLines = False
        self.Lines = None
        self.changed = False
        self.saveChange = False
        self.ThemeIndex = 3
        self.generation = 0
        self.showPanel = False
        self.displayMenu()

    def displayMenu(self):
        menuTitle = tk.Label(self, text = "Welcome to Sean's Autonomous Car Simulation",
        foreground = "black",
        background = "white",
        font = self.fontStyle
        ).pack(side = 'top')
        self.designMap = tk.Button(self, text = 'DESIGN A MAP', font = self.fontStyle, bg = 'black', fg = 'white',
             command = self.getMapinfo).pack(side = 'top')
        self.runSimulation = tk.Button(self, text = 'RUN SIMULATION', font = self.fontStyle, bg = 'black', fg = 'white',
             command = self.runSim).pack(side = 'top')
        self.obstacles = tk.Button(self, text = 'ADD/REMOVE OBSTACLES', font = self.fontStyle, bg = 'black', fg = 'white',
             command = self.getObstacles).pack(side = 'top')
        self.quit = tk.Button(self, text = 'QUIT', font = self.fontStyle, bg = 'black', fg = 'white',
             command = self.master.destroy).pack(side = 'bottom')

    def getMapinfo(self):
        self.changed = True
        pygame.init()
        screen = pygame.display.set_mode((Width, Height), vsync = True)
        clock = pygame.time.Clock()
        fps = 60

        track = Spline()
        trackTopBound = Spline()
        trackBottomBound = Spline()
        trackTopBound.pointRadius = 1
        trackBottomBound.pointRadius = 1

        track.CreatePoints(N_POINTS, False)
        trackBottomBound.CreatePoints(N_POINTS, False)
        trackTopBound.CreatePoints(N_POINTS, False)

        track.resolution = SPLINE_RESOLUTION
        trackBottomBound.resolution = SPLINE_RESOLUTION
        trackTopBound.resolution = SPLINE_RESOLUTION
        TrackLines = []

        counter = 1

        run = True
        MouseClicked = False

        while run:
            screen.fill(Themes[self.ThemeIndex]["background"])

            dt = clock.get_time()/1000
            clock.tick(fps)
            framerate = clock.get_fps()
            pygame.display.set_caption("Self Driving Car AI - FrameRate(fps) : {}".format(int(framerate)))

            if self.edit == True:
                self.changed = True
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        run = False
                        pygame.quit()
                    if event.key == pygame.K_q:
                        self.ThemeIndex = (self.ThemeIndex + 1 ) % len(Themes)
                    if event.key == pygame.K_RETURN or event.key == pygame.K_p:
                        self.showPanel = not self.showPanel
                    if event.key == pygame.K_r:
                        debug = not debug
                        wireframeLine= not wireframeLine
                    if event.key == pygame.K_f:
                        wireframe = not wireframe
                if event.type == pygame.MOUSEBUTTONDOWN:
                    MouseClicked = True
            if self.changed == True:
                global TRACK_WIDTH
                for i in range(N_POINTS ):
                    p1 = track.GetSplinePoints(i * SPLINE_RESOLUTION, True)
                    g1 = track.GetSplineGradient(i * SPLINE_RESOLUTION, True)
                    glength = sqrt(g1[0] * g1[0] + g1[1] * g1[1])

                    trackTopBound.points[i].x = p1[0] - TRACK_WIDTH * (-g1[1]/glength)
                    trackTopBound.points[i].y = p1[1] - TRACK_WIDTH * (g1[0]/glength)

                    trackBottomBound.points[i].x = p1[0] + TRACK_WIDTH * (-g1[1]/glength)
                    trackBottomBound.points[i].y = p1[1] + TRACK_WIDTH * (g1[0]/glength)
            if self.changed == True:
                for i in range(N_POINTS ):
                    p1 = track.GetSplinePoints(i * SPLINE_RESOLUTION, True)
                    g1 = track.GetSplineGradient(i * SPLINE_RESOLUTION, True)
                    glength = sqrt(g1[0] * g1[0] + g1[1] * g1[1])

                    trackTopBound.points[i].x = p1[0] - TRACK_WIDTH * (-g1[1]/glength)
                    trackTopBound.points[i].y = p1[1] - TRACK_WIDTH * (g1[0]/glength)

                    trackBottomBound.points[i].x = p1[0] + TRACK_WIDTH * (-g1[1]/glength)
                    trackBottomBound.points[i].y = p1[1] + TRACK_WIDTH * (g1[0]/glength)

        # draw track triangles and extract the lines out of the track
        Lines = CT.TrackTriangles(
            screen ,
            Top=trackTopBound,
            Bottom=trackBottomBound,
            themeIndex=self.ThemeIndex,
            updateLines=True,
            Lines=TrackLines,
            wireframe=wireframe,
            wireframeLine=wireframeLine
            )

        if debug:
            trackBottomBound.Draw(screen, False)
            trackTopBound.Draw(screen, False)
            track.Draw(screen, MouseClicked, edit)

        if self.showPanel == True:
            # might need to change the way i render ui for optimisation
            panel.Render(screen)
            quitSave.Render(screen)
            editorModeText.Render(screen)
            editText.Render(screen)
            wireframeModeText.Render(screen)
            showLineText.Render(screen)


            editorMode = editorModeToggle.Render(screen, MouseClicked)

            edit = editToggle.Render(screen, MouseClicked)
            wireframe = wireframeToggle.Render(screen, MouseClicked)
            debug = ShowlineToggle .Render(screen, MouseClicked)
            wireframeLine = debug

            if edit == True:
                TrackWidthText.Render(screen)
                TRACK_WIDTH = WidthSlider.Render(screen)

        if quitSave.state == True:
            saveChange = True
            run = False

        MouseClicked = False
        if editorMode:
            changed = True
        else:
            changed = False

        pygame.display.flip()

        if self.saveChange == True:
            self.saveMap(track, trackTopBound, trackBottomBound, TrackLines, track_filename = 'map1')
            
            
    def saveMap(self, track, trackTopBound, trackBottomBound, TrackLines, track_filename):
        data = {
                "TRACK":track,
                "TOP_TRACK": trackTopBound,
                "BOTTOM_TRACK": trackBottomBound,
                "LINES": TrackLines,
                "VARIABLES": {
                    "N_POINTS": N_POINTS,
                    "RESOLUTION": SPLINE_RESOLUTION,
                    "TRACK_WIDTH": TRACK_WIDTH
                }
            }
        pickle.dump(data, open(track_filename, 'wb'))

    def runSim(self):
        pass

    def getObstacles(self):
        pass


root = tk.Tk()
app = Application(master = root)
app.mainloop()


            
