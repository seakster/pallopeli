import pygame as pg
import numpy as np
import json
from math import sqrt


class ball:

    tnum = 10

    def __init__(self, position, velocity, radius, color):

        self.color = color
        self.pos = position
        self.radius = radius
        self.vel = velocity
        self.screenpos = position
        self.past = [[int(position[0]), int(position[1])]]

    def move(self):

        dt = 0.01
        accel = 20 - 0.3 * self.vel[1]
        airrx = -0.3 * self.vel[0]
        self.vel[1] += accel * dt
        self.vel[0] += airrx * dt
        if self.vel[0] > 5:
            self.vel[0] = 5
        if self.vel[0] < -5:
            self.vel[0] = -5
        self.pos = np.add(self.pos, self.vel)

    def update(self, campos, deltapos, size):

        self.screenpos[0] = self.pos[0] - (campos[0] - size[0]/2)
        self.screenpos[1] = self.pos[1]

        self.past.insert(0, [int(self.screenpos[0]), int(self.screenpos[1])])
        if len(self.past) == self.tnum:
            self.past.pop()

        if deltapos != (0 or 0.):
            for pos in self.past:
                pos[0] += int(deltapos[0])

    def check(self, obstacles):

        def clamp(val, minval, maxval):
            return max(minval, min(val, maxval))

        # for ob in obstacles:
            # # löytää lähimmän pisteen ympyrään esteestä
            # closex = clamp(self.pos[0], ob.pos[0], ob.pos[0] + ob.width)
            # closey = clamp(self.pos[1], ob.pos[1], ob.pos[1] + ob.height)
            # # ympyrän keskipisteen ja tämän pisteen etäisyyden neliö
            # distx = self.pos[0] - closex
            # disty = self.pos[1] - closey
            # distsquare = (distx * distx) + (disty * disty)
            # # onko etäisyyden neliö pienempi kuin ympyrän säteen neliö
            # if distsquare < self.radius * self.radius:
            #     offset = [distx, disty]
            #     offsetmagnitude = sqrt(offset[0]**2 + offset[1]**2)
            #     norm = np.divide(offset, offsetmagnitude)
            #     if norm[0] != 0. and norm[1] != 0.:
            #         self.vel = np.multiply(norm, sqrt(self.vel[0]**2 + self.vel[1]**2))
            #     else:
            #         if self.vel[1] >= 0 and self.pos[1] < ob.pos[1]:
            #             self.vel[1] *= -1
            #         elif self.vel[1] < 0 and self.pos[1] > ob.pos[1] + ob.height:
            #             self.vel[1] *= -1
            #         elif self.vel[0] > 0 and self.pos[0] < ob.pos[0]:
            #             self.vel[0] *= -1
            #         else:
            #             self.vel[0] *= -1
            #     self.pos = np.add(self.pos, offset)

        for obstacle in obstacles:
            if ((self.pos[0] + self.radius > obstacle.pos[0] and
                self.pos[0] - self.radius < obstacle.pos[0] + obstacle.width) and
                (self.pos[1] + self.radius > obstacle.pos[1] and
                 self.pos[1] - self.radius < obstacle.pos[1] + obstacle.height)):
                if self.vel[1] >= 0 and self.pos[1] < obstacle.pos[1]:
                    self.pos[1] = obstacle.pos[1] - self.radius
                    self.vel[1] = -self.vel[1]
                elif self.vel[1] < 0 and self.pos[1] > obstacle.pos[1] + obstacle.height:
                    self.pos[1] = (obstacle.pos[1] + obstacle.height) + self.radius
                    self.vel[1] = -self.vel[1]
                elif self.vel[0] > 0 and self.pos[0] < obstacle.pos[0]:
                    self.pos[0] = obstacle.pos[0] - self.radius
                    self.vel[0] = -self.vel[0]
                else:
                    self.pos[0] = obstacle.pos[0] + obstacle.width + self.radius
                    self.vel[0] = -self.vel[0]

    def draw(self, surface):

        for pos in self.past:
            pg.draw.circle(surface, self.color, pos, int(self.radius - 2*self.past.index(pos)))


class obstacle:

    near = False

    def __init__(self, position, width, height, color):
        self.pos = position
        self.screenpos = position
        self.width = width
        self.height = height
        self.color = color

    def update(self, camdeltapos):
        self.screenpos = [self.screenpos[0] + camdeltapos[0], self.screenpos[1] + camdeltapos[1]]

    def draw(self, surface):
        pos = [int(self.screenpos[0]), int(self.screenpos[1])]
        pg.draw.rect(surface, self.color, (pos[0], pos[1], self.width, self.height))


class camera:

    vel = [0, 0]
    deltapos = [0, 0]
    nearobstacles = []

    def __init__(self, size):
        self.size = size
        self.pos = [size[0]/2, size[1]/2]

    def move(self, ballposition):

        if ballposition[0] > self.pos[0] + self.size[0]/4:
            self.vel[0] += ballposition[0] - (self.pos[0] + self.size[0]/4)
        if ballposition[0] < self.pos[0] - self.size[0]/4:
            self.vel[0] += ballposition[0] - (self.pos[0] - self.size[0]/4)

        beforex = self.pos[0]
        accel = 0.9 * self.vel[0]
        if round(self.vel[0]) != 0:
            if self.vel[0] > 0:
                self.vel[0] -= accel
                self.pos[0] += self.vel[0]
            else:
                self.vel[0] -= accel
                self.pos[0] += self.vel[0]
        self.deltapos[0] = beforex - self.pos[0]

    def checkobstacles(self, obstacles):
        for ob in obstacles:
            if (ob.pos[0] > self.pos[0] + self.size[0]/2 or
               ob.pos[0] + ob.width < self.pos[0] - self.size[0]/2):
                ob.near = False
            else:
                ob.near = True
            if ob.near and ob not in self.nearobstacles:
                self.nearobstacles.append(ob)
            if not ob.near and ob in self.nearobstacles:
                self.nearobstacles.remove(ob)

    def openlevel(self, filename):

        obstaclelist = []
        lvldata = open(filename).read()
        lvl = json.loads(lvldata)

        for object in lvl:
            ob = obstacle(object["pos"], object["width"], object["height"], object["color"])
            obstaclelist.append(ob)

        return obstaclelist
