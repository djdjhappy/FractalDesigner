import numpy as np
import random
from scipy.optimize import fsolve

def op(m, m2):
    # 分形基本变换的复表示矩阵
    return np.array([
        [m[1] - m2[0], m2[0] - m[0]],
        [m[1] - m2[1], m2[1] - m[0]]
    ]) / (m[1] - m[0])

def norm(v):
    # 分形的尺寸
    return np.linalg.norm(v[1] - v[0])
def devide(v, r):
    # 将分形向量作分割，以r为比例得到分点
    return (1 - r) * v[0] + r * v[1]
def opScale(op):
    # 计算运算矩阵的伸缩倍数
    return norm(op @ np.array([0, 1]))
class Law:
    PL = 1
    PR = 1000
    def __init__(self, subs, sup = (0., 1.)):
        self.sup = np.array(sup)
        self.subs = list(map(np.array, subs))
        self.ops = [op(self.sup, sub) for sub in self.subs]

    def apply(self, vectors, pl = 3, pr = 1000):
        #pl, pr是上下精确度，超出此范围的长度的分形不会再进行迭代
        res = [op @ v if pl < norm(v) < pr else v for op in self.ops for v in vectors]
        return res
    # 绘图顺序的改进可以写入论文，充实其内容

    def randomIterate(self, v, m = 15):
        # 效率不够，还是要考虑如何利用矩阵乘法
        for i in range(m):
            v = random.choice(self.ops) @ v
            n = norm(v)
            if n <= self.PL or n >= self.PR:
                break
        return v
    def dim(self):
        if not self.ops:
            return float('nan')
        scales = np.array(list(map(opScale, self.ops)))
        if (scales <= 0).any() or (scales >= 1).any():
            return float('nan')
        def f(s):
            return np.sum(scales ** s) - 1
        s = fsolve(f, 0.5)
        return s[0]
