import os
import pygame
import pickle
import neat
from point import Point, GetDistance
from mapsetup import Spline
from math import sin, radians, degrees, copysign, sqrt
from pygame.math import Vector2
from car import Car
from CT import CT
from constants import *
from UI.setup import *
import tkinter as tk

class MapDesign:
    def __init__(self):
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
        self.createMap()

    def renderTexts(self, screen): #Displays text
        panel.Render(screen)
        quitSave.Render(screen)
        editorModeText.Render(screen)
        editText.Render(screen)
        wireframeModeText.Render(screen)
        showLineText.Render(screen)

    def getPygameEvents(self):
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
                        self.debug = not self.debug
                        self.wireframeLine= not self.wireframeLine
                    if event.key == pygame.K_f:
                        self.wireframe = not self.wireframe
                if event.type == pygame.MOUSEBUTTONDOWN:
                    MouseClicked = True


    def createMap(self):
        self.edit = True
        self.editorMode = True
        pygame.init()
        # pygame.display.set_caption(" Self Driving Car")
        screen = pygame.display.set_mode((Width, Height), vsync=True)
        clock = pygame.time.Clock()
        fps = 60
        #instantiates spline class for track and two bounds
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

        self.renderTexts(screen)


        run = True
        MouseClicked = False

        while run:
            screen.fill(Themes[self.ThemeIndex]["background"])
            clock.tick(fps)
            framerate = clock.get_fps()
            pygame.display.set_caption("Self Driving Car AI - FrameRate(fps) : {}".format(int(framerate)))

            if self.edit == True:
                self.changed == True
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
                        self.debug = not self.debug
                        self.wireframeLine= not self.wireframeLine
                    if event.key == pygame.K_f:
                        self.wireframe = not self.wireframe
                if event.type == pygame.MOUSEBUTTONDOWN:
                    MouseClicked = True
            if self.changed == True:
                for i in range(N_POINTS ):
                    p1 = track.GetSplinePoints(i * SPLINE_RESOLUTION, True)
                    g1 = track.GetSplineGradient(i * SPLINE_RESOLUTION, True)
                    glength = sqrt(g1[0] * g1[0] + g1[1] * g1[1])

                    trackTopBound.points[i].x = p1[0] - self.trackWidth * (-g1[1]/glength)
                    trackTopBound.points[i].y = p1[1] - self.trackWidth * (g1[0]/glength)

                    trackBottomBound.points[i].x = p1[0] + self.trackWidth * (-g1[1]/glength)
                    trackBottomBound.points[i].y = p1[1] + self.trackWidth * (g1[0]/glength)
            
            Lines = CT.TrackTriangles(
            screen ,
            Top=trackTopBound,
            Bottom=trackBottomBound,
            themeIndex=self.ThemeIndex,
            updateLines=True,
            Lines=TrackLines,
            wireframe=self.wireframe,
            wireframeLine=self.wireframeLine
            ) #Draws track from CT.py

            if self.debug:
                trackBottomBound.Draw(screen, False) #Draws bounds separately
                trackTopBound.Draw(screen, False)

            if self.editorMode:
                track.Draw(screen, MouseClicked, self.edit) #Allows user to click and edit points for spline

            if self.showPanel == True:
            # might need to change the way i render ui for optimisation
                self.renderTexts(screen)


                self.editorMode = editorModeToggle.Render(screen, MouseClicked)

                self.edit = editToggle.Render(screen, MouseClicked)
                self.wireframe = wireframeToggle.Render(screen, MouseClicked)
                self.debug = ShowlineToggle .Render(screen, MouseClicked)
                self.wireframeLine = self.debug
                if self.edit == True:
                    TrackWidthText.Render(screen)
                    self.trackWidth = WidthSlider.Render(screen)
            if quitSave.state == True:
                self.saveChange = True
                run = False

            MouseClicked = False
            if self.editorMode:
                self.changed = True
            else:
                self.changed = False

            pygame.display.flip()
        if self.saveChange == True:
            track_filename = "./map/new_track" 
            current_directory = os.path.dirname(os.path.abspath(__file__))
            self.saveMap(track, trackTopBound, trackBottomBound, TrackLines, track_filename)

    def carryOn(self):
        pass


    def saveMap(self, track, trackTopBound, trackBottomBound, TrackLines, trackName):
        #Uses pickle module to save track
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
        pickle.dump(data, open(trackName, 'wb'))
        pygame.quit()


        