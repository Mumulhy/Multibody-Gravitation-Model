# -*- coding: utf-8 -*-
# 多体引力模型向量化模型

"""
Created on Sun Sept 1 21:45:16 2019

@author: _Mumu, Squirtle
Environment: py37 with pygame
"""

import random, math, time
import numpy as np
import cv2 as cv

random.seed(100)

NUM, MASS, R, X, Y, VX, VY, COLOR = [], [], [], [], [], [], [], []
AX, AY = np.array([]), np.array([])

body_list = []
body_count = 0

width, height = 960, 540

middle = np.array([width//2,
                   height//2])                     # 中心点坐标

body_list = []      # 星体列表
max_count = 20     # 初始星体数量
max_body = None     # 最大星体
max_path = 150      # 轨迹长度
G = 0.02            # 引力常数
den = 1             # 密度

screen = np.zeros((height, width, 3), dtype = np.uint8)

class body(object):
    
    """
    Class:      星体
    CreateObj:  body(num, mass, x, y, vx, vy) 	用于创建对象，只存储对象id(self.num)以及颜色(self.col)
    """
    
    def __init__(self, num, mass, x, y, vx, vy):
        
        """
        Method:     __init__                    构造方法
        Input:      num, mass, x, y, vx, vy     星体参数
        Return:     body                        星体类
        """
        self.num = num                          # 编号
        NUM.append(num)
        MASS.append(mass)                       # 质量
        r = np.cbrt(mass/den/math.pi*0.75)      # 计算半径
        R.append(r)
        X.append(x) 				            # 横坐标
        Y.append(y) 				            # 纵坐标
        VX.append(vx) 				            # 速度X分量
        VY.append(vy) 				            # 速度Y分量
        self.col = (random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255))     # 颜色
        COLOR.append(self.col)
        body_list.append(self)

def move_pos():
    global X, Y, VX, VY
    X = X + VX
    Y = Y + VY

def move_vel():
    global VX, VY, AX, AY
    VX = VX + AX
    VY = VY + AY

def accel():
    global AX, AY

    ones = np.ones((body_count,body_count))
    eyes = np.eye(body_count)

    DIS = np.sqrt( (X*ones-(X*ones).T)**2 + (Y*ones-(Y*ones).T)**2 )

    AX2d = G*(MASS*ones)*(MASS*ones).T*(X*ones - (X*ones).T) / (DIS**3 + eyes)
    AX = np.sum(AX2d, axis = 1)
    AY2d = G*(MASS*ones)*(MASS*ones).T*(Y*ones - (Y*ones).T) / (DIS**3 + eyes)
    AY = np.sum(AY2d, axis = 1)

def drawStars(X, Y, R, COLOR):

    global screen
    for x, y, r, color in zip(X, Y, R, COLOR):
        screen = cv.circle(screen, (int(x), int(y)), int(r), color, -1)    # 绘制实心圆
    

if __name__ == '__main__':

    #middlex, middley = width // 2, height // 2          # 中心点坐标
    
    running = True                          # 程序运行状态

    for i in range(1, max_count + 1):
        body(i,
             random.randint(150, 300),           # 初始质量
             random.randint(0, width),
             random.randint(0, height),         # 初始坐标
             random.randint(-120, 120)/500,
             random.randint(-120, 120)/500)     # 初始速度
    body_count = len(body_list)

    while True:

        tic = time.time()

        if running:
            screen = np.zeros((height, width, 3), dtype = np.uint8)

            drawStars(X, Y, R, COLOR)

            accel()
            move_vel()
            move_pos()

        cv.imshow("Universe", screen)

        toc = time.time()
        print(toc - tic)

        key = cv.waitKey(50)

        if key == 27:                                      # 按esc退出
            break
            
        if key == 9:                                       # Tab，Pause或Resume
            running = not running;

    for i in range(5):                                     # 关闭cv窗口
        cv.waitKey(1)
        cv.destroyAllWindows()

    




