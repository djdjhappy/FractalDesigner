import pygame as pg
import core
import numpy as np
from copy import deepcopy
import random
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (130, 130, 130)
RED = (255, 0, 0)
def arr(c, type = float):
    return np.array([c.real, c.imag], dtype = type)
def cplx(a):
    return a[0] + a[1] * 1j
def prim(surface, color, vector):
    surface.set_at(arr(vector[0], int), color)
pid = 0
class GPoint:
    R = 5
    def __init__(self, pos):
        self.pos = pos
        self.gvectors = set()
        global pid
        self.id = pid
        pid += 1
    def __repr__(self):
        return '#%d'%self.id
    def arr(self):
        return arr(self.pos)
    def rect(self):
        center = self.arr()
        rect = [*(center - GPoint.R), 2 * GPoint.R, 2 * GPoint.R]
        return rect
    def contain(self, pos):
        if not isinstance(pos, complex):
            pos = pos[0] + pos[1] * 1j
        return core.norm([self.pos, pos]) <= self.R # 换一种，统一
    def draw(self, surface, color = WHITE, mark = '#'):
        if mark == '#':
            pg.draw.rect(surface, color, self.rect(), 2)
        elif mark == '^':
            rect = self.rect()
            p1 = (rect[0] + rect[2] / 2, rect[1] - rect[3] / 4)
            p2 = (rect[0] - rect[2] / 4, rect[1] + rect[3] / 2)
            p3 = (rect[0] + rect[2] / 2, rect[1] + rect[3] * 5 / 4)
            p4 = (rect[0] + rect[2] * 5 / 4, rect[1] + rect[3] / 2)
            pg.draw.polygon(surface, color, [p1, p2, p3, p4])
    def copy(self):
        # 复制一个仅含有相同坐标的副本
        return GPoint(self.pos)
class GVector:
    WIDTH = 0.5 # contain判定意义下的线宽
    def __init__(self, gpoints):
        self.gpoints = list(gpoints)
        gpoints[0].gvectors.add(self)
        gpoints[1].gvectors.add(self)
    def replace(self, old, new):
        # 替换掉端点
        old.gvectors.remove(self)
        new.gvectors.add(self)
        if self.gpoints[0] is old:
            self.gpoints[0] = new
        elif self.gpoints[1] is old:
            self.gpoints[1] = new
    def draw(self, surface, color = WHITE, width = 2):
        self.gpoints[0].draw(surface, color, '#')
        self.gpoints[1].draw(surface, color, '^')
        pg.draw.line(surface, color, self.gpoints[0].arr(), self.gpoints[1].arr(), width)
    def vector(self):
        return np.array([self.gpoints[0].pos, self.gpoints[1].pos])
    def devide(self, r):
        return GPoint(core.devide(self.vector(), r))
    def contain(self, pos):
        # 检测点是否在包围向量的一个椭圆范围内
        if not isinstance(pos, complex):
            pos = pos[0] + pos[1] * 1j
        u = core.norm([self.gpoints[0].pos, pos])
        v = core.norm([self.gpoints[1].pos, pos])
        w = core.norm([self.gpoints[0].pos, self.gpoints[1].pos])
        return u + v - w <= self.WIDTH
    def __getitem__(self, i):
        return self.gpoints[i]
