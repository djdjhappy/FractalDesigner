import pygame as pg
import core
import numpy as np
from copy import deepcopy
import random
from geometry import *

class Canvas:
    def draw(self, surface):
        pass
    def mouseButtonDown(self, pos, button):
        pass
    def mouseMotion(self, pos):
        pass
    def mouseButtonUp(self, pos):
        pass
    def keyDown(self, key):
        pass
class EditCanvas(Canvas):
    M = 0.5 # 相对于屏幕长度（x方向）的放缩因子
    N_MAX = 10 # 最大允许子向量数
    GRID_N = 20
    def __init__(self, gvectors = (), gpoints = (), ref = None):
        self.surface = pg.Surface(SIZE)
        self.gvectors = set(gvectors)
        self.gpoints = set(gpoints)
        self.ref = ref
        self.clicked = None
        self.news = True
        self.law = core.Law([])
        self.initRef()
##        self.testInit()
    def update(self):
        # 更新law
        self.news = True
        self.law = core.Law([gvector.vector() for gvector in self.gvectors], self.ref.vector())
    def updator(f):
        def g(self, *args, **kwargs):
            res = f(self, *args, **kwargs)
            self.update()
            return res
        return g
    @updator
    def addGVector(self, gvector):
        self.gvectors.add(gvector)
        self.gpoints.update(gvector.gpoints)
    @updator
    def addGPoint(self, gpoint):
        self.gpoints.add(gpoint)
        return gpoint
    @updator
    def removeGPoint(self, gpoint):
        self.gpoints.remove(gpoint)
        return gpoint
    @updator
    def removeGVector(self, gvector):
        self.gvectors.remove(gvector)
        for gpoint in gvector.gpoints:
            gpoint.gvectors.remove(gvector)
            if not gpoint.gvectors:
                self.removeGPoint(gpoint)
    @updator
    def newGVector(self):
        w, h = SIZE
        dh = h * 0.5 / self.N_MAX
        dw = w / 4
        l = len(self.gvectors)
        if l < self.N_MAX:
            vh = dh * (l + 1)
            gvector = GVector([GPoint(dw + vh * 1j), GPoint(dw + w / 4 + vh * 1j)])
            self.addGVector(gvector)
    @updator
    def updatePos(self, pos):
        # 更新被拖动的点的坐标
        if not isinstance(pos, complex):
            pos = cplx(pos)
        self.clicked.pos = pos
    def initRef(self):
        if self.ref is None:
            w, h = SIZE
            M = self.M
            ct = cplx(SIZE) * M
            self.ref = GVector([GPoint(ct - w * 0.5 * M), GPoint(ct + w * 0.5 * M)])
            self.addGPoint(self.ref.gpoints[0])
            self.addGPoint(self.ref.gpoints[1])
        # 此处不能直接添加ref为Canvas的gvector，因为这会导致作为通常的规则参与渲染
##    def testInit(self):
##        w, h = SIZE
##        M = self.M
##        l = w * M
##        c = self.ref.devide(0.4)
##        d = GPoint(c.pos - l * 0.4j)
##        e = GPoint(c.pos + l * 0.3j)
##        gppairs = [(self.ref[0], c), (c, self.ref[1]), (c, d), (c, e)]
##        for gppair in gppairs:
##            self.addGVector(GVector(gppair))
    def gridAdhere(self):
        #（如果足够近，则）将self.clicked的坐标附着到最近的网格点上
        N = self.GRID_N
        if self.clicked:
            p = self.clicked.pos
            dw, dh = SIZE[0] / N, SIZE[1] / N
            p2 = dw * round(p.real / dw) + 1j * dh * round(p.imag / dh)
            if core.norm([p, p2]) < 5:
                self.updatePos(p2)
    def drawGrid(self, surface):
        # 绘制辅助线网格背景
        N = self.GRID_N # 等分数
        color = GREY
        for i in range(N):
            h = i * SIZE[1] / N
            pg.draw.line(surface, color, (0, h), (SIZE[0], h), 1)
        for i in range(N):
            w = i * SIZE[0] / N
            pg.draw.line(surface, color, (w, 0), (w, SIZE[1]), 1)
    def draw(self):
        self.surface.fill(BLACK)
        self.drawGrid(self.surface)
        self.ref.draw(self.surface, RED, 4)
        for gvector in self.gvectors:
            gvector.draw(self.surface)
        
    def getClicked(self, pos):
        for gpoint in self.gpoints:
            if gpoint.contain(pos):
                return gpoint
    def getClickedGVector(self, pos):
        for gvector in self.gvectors: # 不包含self.ref
            if gvector.contain(pos):
                return gvector
            
    def mouseButtonDown(self, pos, button):
        if button == 1: # 左键
            self.clicked = self.getClicked(pos)
        elif button == 3: # 右键
            # 先讨论点的右击
            clicked = self.getClicked(pos)
            if clicked:
                for gvector in list(clicked.gvectors):
                    #还有问题
                    cp = clicked.copy()
                    self.addGPoint(cp)
                    gvector.replace(clicked, cp)
                self.removeGPoint(clicked)
            # 考虑线的右击及删除（仅当未点击点时进行）
            else:
                clicked = self.getClickedGVector(pos)
                if clicked:
                    self.removeGVector(clicked)
    def mouseMotion(self, pos):
        if self.clicked:
            self.updatePos(pos)
    def mouseButtonUp(self, pos):
        if self.clicked:
            self.gridAdhere()
            for gpoint in self.gpoints:
                if gpoint is not self.clicked and gpoint.contain(self.clicked.pos):
                    if not self.clicked.gvectors.intersection(gpoint.gvectors):
                        for gvector in list(gpoint.gvectors):
                            gvector.replace(gpoint, self.clicked)
                        self.removeGPoint(gpoint)
                        break # 注意这里的break是不可以去除的，否则会出现多点同时合并的情形，可能导致位置相近的同向量端点被合并
        self.clicked = None
    def keyDown(self, key):
        if key == pg.K_RETURN:
            self.newGVector()
class EffectCanvas(Canvas):
    N = 7 # 动画帧数
    def __init__(self):
        self.vectors = []
        
        
##        self.ratio = 0.75
##        self.ref = np.array([w * 0.125 + h * 0.5j, w * 0.875 + h * 0.5j])
        self.law = None
        self.surfaces = [pg.Surface(SIZE) for i in range(self.N)] # 动画的单个循环中的帧
        self.resetRatio(0.75)
        self.cnt = 0 # 当前动画的帧
        self.clock = 0 # 每帧循环时钟
        self.animating = False
        self.refresh()
    def resetRatio(self, ratio):
        self.ratio = ratio
        w, h = SIZE
        self.ref = np.array([w * 0.5 * (1 - ratio) + h * 0.5j, w * 0.5 * (1 + ratio) + h * 0.5j])
        self.refresh() ##
    @property
    def surface(self):
        return self.surfaces[self.cnt]
    def wander(self):
        if editCanvas.law.ops:
##        if self.law.ops:
            i = random.randint(0, self.N - 1)
            # test
            t = float(i) / self.N
            ref = (t * self.aop + (1 - t) * np.eye(2))  @ self.ref
            # 暂时没有好方法来填充，就先不改，怕影响正常功能
##            v = self.law.randomIterate(ref)
            v = editCanvas.law.randomIterate(ref)
            prim(self.surfaces[i], WHITE, v)
##    def updateLaw(self):
##        self.law = core.Law([gvector.vector() for gvector in editCanvas.gvectors], editCanvas.ref.vector())
##        if self.law.ops:
##            self.aop = np.linalg.inv(self.law.ops[0])
##        editCanvas.news = False
##        for surface in self.surfaces:
##            surface.fill(BLACK)
    def refresh(self):
        editCanvas.news = False
        for surface in self.surfaces:
            surface.fill(BLACK)
    def draw(self):
##        # 及时更新规则
        if editCanvas.news:
            self.refresh()
        if editCanvas.law.ops:
            self.aop = np.linalg.inv(editCanvas.law.ops[0])
##            self.updateLaw()
        # 均匀随机更新
        for i in range(100):
            self.wander()
        if self.animating:
            self.clock += 1
            if self.clock == 20:
                self.clock = 0
                self.cnt = (self.cnt + 1) % self.N
    def keyDown(self, key):
        if key == pg.K_RETURN:
            self.animating = not self.animating
        elif key == pg.K_RIGHTBRACKET:
            self.resetRatio(self.ratio * 1.25)
        elif key == pg.K_LEFTBRACKET:
            self.resetRatio(self.ratio * 0.8)
def note(surface):
    #  加标注
    font = pg.font.SysFont('Times', 30)
    dim = editCanvas.law.dim() + 1e-14
    text = font.render("dH = %.3f" % dim, True, (255, 0, 0))
    surface.blit(text, (0, 0))
