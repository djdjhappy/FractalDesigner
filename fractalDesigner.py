import pygame as pg
import core
import numpy as np
from copy import deepcopy
import random
from geometry import *
from canvas import *
from archive import archive
pg.init()
__builtins__.SCALE = 800
__builtins__.SIZE = np.array([1, 1]) * SCALE
__builtins__.screen = pg.display.set_mode(SIZE)

__builtins__.editCanvas = EditCanvas(*archive.load())#EditCanvas()
__builtins__.effectCanvas = EffectCanvas()
editCanvas.update()
def loop():
    cvs = [editCanvas, effectCanvas]
    ci = 0
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_1:
                    archive.save(editCanvas)
                elif event.key == pg.K_2:
                    archive.report() 
                elif event.key == pg.K_TAB:
                    ci = (ci + 1) % 2
                else:
                    cvs[ci].keyDown(event.key)
            elif event.type == pg.MOUSEBUTTONDOWN:
                cvs[ci].mouseButtonDown(event.pos, event.button)
            elif event.type == pg.MOUSEMOTION:
                cvs[ci].mouseMotion(event.pos)
            elif event.type == pg.MOUSEBUTTONUP:
                cvs[ci].mouseButtonUp(event.pos)
        cvs[ci].draw()
        screen.blit(cvs[ci].surface, (0, 0))
        note(screen) #
        pg.display.update()
    pg.quit()
loop()
