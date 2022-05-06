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
from neural import Neural
from MapDesign import MapDesign

class Simulation:
    def __init__(self):
        pygame.init()
        # pygame.display.set_caption(" Self Driving Car")
        self.screen = pygame.display.set_mode((Width, Height), vsync=True)
        self.clock = pygame.time.Clock()
        self.fps = 60

        # load Assets
        self.track_filename = "./map/new_track"
        self.current_directory = os.path.dirname(os.path.abspath(__file__))
        self.carImage_path = os.path.join(self.current_directory, "./Assets/car2.png")
        self.car_sprite = pygame.image.load(self.carImage_path)
        self.sprite = pygame.transform.scale(self.car_sprite, CAR_SIZE)

        self.filename = self.track_filename
        (self.track, self.trackTopBound, self.trackBottomBound, self.TrackLines) = self.loadData()
        self.startPoint = self.track.points[0]
        self.debug=True
        self.editorMode = False
        self.edit=False
        self.wireframe=False
        self.wireframeLine=False
        self.updateLines = False
        self.Lines = None
        # set changed=True if you want to edit a track or create a new one
        self.changed = False

        self.saveChange = False
        self.ThemeIndex = 3
        self.generation = 0
        self.showPanel = False
        self.brain = Neural()
        self.__local_dir = os.path.dirname(__file__) # current directory
        config_path = os.path.join(self.__local_dir, "config-feedforward.txt")
        self.run(config_path)

    def loadData(self):
        #Loads pickle file
        mapData = pickle.load(open(self.filename, 'rb'))
        track = mapData['TRACK']
        trackTopBound = mapData['TOP_TRACK']
        trackBottomBound = mapData['BOTTOM_TRACK']
        TrackLines = mapData['LINES']

        return track, trackTopBound, trackBottomBound, TrackLines

    def Fitness(self,genomes, config):  
        nets = []
        genes = []
        cars = []

        for index, genome in genomes:
            genome.fitness = 0
            nn = neat.nn.FeedForwardNetwork.create(genome, config) #Initiates neural network from neat module.
            nets.append(nn)

            car = Car(12, 20)
            car.sprite = self.sprite
            car.angle = 90
            cars.append(car)
            genome.fitness = 0
            genes.append(genome)

        counter = 1

        run = True
        MouseClicked = False
        self.generation += 1
        GenerationText.text = "Generation : " + str(self.generation)
        PopulationText.text = "Population size: " + str(len(cars))
        survivors = len(cars)
        while run:
            self.screen.fill(Themes[self.ThemeIndex]["background"]) #Changes pygame screen to fit background selected.

            dt = self.clock.get_time()/1000
            self.clock.tick(self.fps)
            framerate = self.clock.get_fps()
            pygame.display.set_caption("Self Driving Car AI - FrameRate(fps) : {}".format(int(framerate)))

            # HANDLE EVENT
            # q -> Switch themes , Esc -> to close window
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
                if event.type == pygame.MOUSEBUTTONDOWN:
                    MouseClicked = True

            for index, car in enumerate(cars):

                car.Forward(dt)
                #Traverses through network
                genes[index].fitness += 0.1
                output = nets[index].activate(
                    (
                    abs(car.intersections[0]["distance"]),
                    abs(car.intersections[1]["distance"]),
                    abs(car.intersections[2]["distance"]),
                    abs(car.intersections[3]["distance"]),
                    abs(car.intersections[4]["distance"]),
                    )
                )
                #Uses activation function to calculate an output from car radars (distance)

                i = output.index(max(output))
                #Car goes left or right depending on output
                if i == 0:
                    car.Left(dt) 
                else:
                    car.Right(dt)

                # if output[0] > 0.6:
                #     car.Right(dt)
                # elif output[1] > 0.6:
                #     car.Left(dt)


                car.constrainSteering()


            # draw track triangles and extract the lines out of the track
            Lines = CT.TrackTriangles(
                self.screen ,
                Top=self.trackTopBound,
                Bottom=self.trackBottomBound,
                themeIndex=self.ThemeIndex,
                updateLines=True,
                Lines=self.TrackLines,
                wireframe=self.wireframe,
                wireframeLine=self.wireframeLine
                )
            

            if self.debug:
                self.trackBottomBound.Draw(self.screen, False)
                self.trackTopBound.Draw(self.screen, False)


            if len(cars) > 0:
                for index, car in enumerate(cars):

                    car.update(self.screen, dt, self.TrackLines, self.debug) #updates car
                    car.Draw(self.screen, self.debug) #draws car

                    if car.crashed == True:
                        pygame.draw.circle(self.screen, Red, car.center, 8) #When a car crashes, a red circle is displayed to indicate
                        genes[index].fitness -= 1
                        cars.pop(index) #Car gets removed
                        nets.pop(index) 
                        genes.pop(index)
                        survivors -= 1 #Count decreases when car dies
            else:
                run = False

            for gene in genes:
                gene.fitness += 2

            counter += 1
            #Displays stats
            GenerationText.Render(self.screen)
            PopulationText.Render(self.screen)
            AgentAliveText.text = "Alive : " + str(survivors)
            AgentAliveText.Render(self.screen)

            MouseClicked = False
            changed = False

            pygame.display.flip()

    def run(self, config_path):
        config = neat.config.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            config_path
            )
        popul = neat.Population(config)
        popul.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        popul.add_reporter(stats)
        winner = popul.run(self.Fitness,1000)


    



