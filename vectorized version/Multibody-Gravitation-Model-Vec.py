# -*- coding: utf-8 -*-
# 多体引力模型向量化模型

"""
Created on Sun Sept 1 21:45:16 2019

@author: _Mumu, Squirtle
Environment: Python3.7 with OpenCV3.4.6
"""

import random, math, time
import numpy as np
import cv2 as cv

random.seed(1)

NUM = np.array([], dtype = int)
MASS, R = np.array([]), np.array([])
X, Y = np.array([]), np.array([])
VX, VY = np.array([]), np.array([])
COLOR = []
AX, AY = np.array([]), np.array([])
body_count = 0

width, height = 960, 540

middle = np.array([width//2, height//2])         # 中心点坐标

#body_list = []       # 星体列表
max_count = 100       # 初始星体数量
#max_body = None      # 最大星体
#max_path = 150       # 轨迹长度
G = 0.02              # 引力常数
den = 1               # 密度

'''
class body(object):
    
    """
    Class:      星体
    CreateObj:  body(num, mass, x, y, vx, vy)   用于创建对象，只存储对象id(self.num)以及颜色(self.col)
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
        X.append(x)                             # 横坐标
        Y.append(y)                             # 纵坐标
        VX.append(vx)                           # 速度X分量
        VY.append(vy)                           # 速度Y分量
        self.col = (random.randint(30, 255),
                    random.randint(30, 255),
                    random.randint(30, 255))    # 颜色
        COLOR.append(self.col)
        body_list.append(self)
'''
def create(num, mass, x, y, vx, vy):

    global NUM, MASS, R, X, Y, VX, VY, COLOR

    NUM = np.append(NUM, num)
    MASS = np.append(MASS, mass)                # 质量
    r = np.cbrt(mass/den/math.pi*0.75)
    R = np.append(R, r)                         # 半径
    X = np.append(X, x)                         # 横坐标
    Y = np.append(Y, y)                         # 纵坐标
    VX = np.append(VX, vx)                      # 速度X分量
    VY = np.append(VY, vy)                      # 速度Y分量
    col = (random.randint(30, 255),
                random.randint(30, 255),
                random.randint(30, 255))
    COLOR.append(col)                           # 颜色

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

    FX2d = G*(MASS*ones)*(MASS*ones).T*(X*ones - (X*ones).T) / (DIS**3 + eyes)
    FX = np.sum(FX2d, axis = 1)
    AX = FX/MASS
    FY2d = G*(MASS*ones)*(MASS*ones).T*(Y*ones - (Y*ones).T) / (DIS**3 + eyes)
    FY = np.sum(FY2d, axis = 1)
    AY = FY/MASS


def check_collision():
    
    """
    Function:   check_collision     检测星体碰撞
    Input:      None
    Output:     collide_event_list  存储碰撞事件列表的列表，每个碰撞事件列表包含撞在一起的一组星体
    """
    ones = np.ones((body_count,body_count))

    DIS = np.sqrt( (X*ones - (X*ones).T)**2 + (Y*ones - (Y*ones).T)**2 )    # 距离阵
    RR = R*ones + (R*ones).T                                                # 半径之和阵

    COLLIDE = DIS <= RR             # 用于检测两颗星系是否发生碰撞的二维布尔矩阵
    collide_event_list = []         # 用于存储每一组碰撞事件的列表

    for line in COLLIDE:
        if len(np.nonzero(line)[0]) == 1: continue               # 当矩阵中仅有对角元为True时，该星未发生碰撞

        line = list(np.nonzero(line)[0])                         # 获得与该星碰撞的所有星体的索引（包括该星）

        for index, old_line in enumerate(collide_event_list):    # 遍历已知碰撞事件，若与当前事件存在交集，则合并事件
            if set(old_line) & set(line):                        # （采用集合的交、并操作完成）
                line = list(set(old_line) | set(line))
                collide_event_list[index] = []                   # 由于collide_event_list还处在遍历当中，不能删除元素，只能先设为空集

        collide_event_list.append(line)

    collide_event_list = [i for i in collide_event_list if i]    # 统一删除collide_event_list中的空集

    return collide_event_list


def collision(collide_event_list):

    """
    Function:   merge                 处理星体碰撞
    Input:      collide_event_list    参与碰撞的星球列表
    Output:     None
    """
    global NUM, MASS, R, X, Y, VX, VY, COLOR, body_count

    body_to_delete = []

    for collide_body_list in collide_event_list:

        # 判断当前碰撞组合中最大星体
        max_body = collide_body_list[0]
        for index in collide_body_list:
            if MASS[index] > MASS[max_body]: max_body = index
    
        # 计算合并后星体的各项参数
        new_mass = np.sum(MASS[collide_body_list])
        new_x = np.sum(X[collide_body_list] * 
                       MASS[collide_body_list]) / new_mass
        new_y = np.sum(Y[collide_body_list] * 
                       MASS[collide_body_list]) / new_mass
        new_vx = np.sum(VX[collide_body_list] * 
                        MASS[collide_body_list]) / new_mass
        new_vy = np.sum(VY[collide_body_list] * 
                        MASS[collide_body_list]) / new_mass
        
        # 将新参数赋予各个list的max_body
        MASS[max_body] = new_mass
        X[max_body] = new_x
        Y[max_body] = new_y
        VX[max_body] = new_vx
        VY[max_body] = new_vy
        R[max_body] = np.cbrt(new_mass/den/math.pi*0.75)

        dead_body = collide_body_list.copy()
        dead_body.remove(max_body)

        body_to_delete.extend(dead_body)
        
        print("\rCollide happens! Body", 
        	  NUM[body_to_delete[0]] + 1, 
        	  "was eaten by", 
        	  NUM[max_body] + 1, 
        	  "!    ", end = "", flush = True)
    
    # Notice! 要降序排列body_to_delete列表，不然在删除最后一个球的时候会出现越界！
    body_to_delete.sort(reverse = True)

    for index in body_to_delete:
        NUM = np.delete(NUM, index)
        MASS = np.delete(MASS, index)
        R = np.delete(R, index)
        X = np.delete(X, index)
        Y = np.delete(Y, index)
        VX = np.delete(VX, index)
        VY = np.delete(VY, index)
        COLOR.pop(index)
    
    body_count = len(NUM)


def drawStars():

    global screen
    for x, y, r, color in zip(list(X), list(Y), list(R), COLOR):
        screen = cv.circle(screen, (int(x), int(y)), int(r), color, -1)    # 绘制实心圆
    

if __name__ == '__main__':

    #middlex, middley = width // 2, height // 2          # 中心点坐标
    
    running = True                          # 程序运行状态

    screen = np.zeros((height, width, 3), dtype = np.uint8)
    
    for i in range(max_count):
        create(i,
               random.randint(100, 500),                   # 初始质量
               random.randint(0, width),
               random.randint(0, height),                  # 初始坐标
               random.randint(-120, 120)/100,
               random.randint(-120, 120)/100)              # 初始速度
    
    #create(0, 10000, middle[0], middle[1], 0, 0)          # 太阳！
    #create(1, 10, middle[0]+100, middle[1], 0, -1.5)      # 水星！
    body_count = len(NUM)

    while True:

        tic = time.time()

        if running:
            screen = np.zeros((height, width, 3), dtype = np.uint8)

            drawStars()

            accel()
            move_vel()
            move_pos()
            collision(check_collision())

        cv.imshow("Universe", screen)

        toc = time.time()
        #print(toc - tic)

        key = cv.waitKey(30)

        if key == 27:                                      # 按esc退出
            break
            
        if key == 9:                                       # 按Tab暂停或恢复
            running = not running;

    for i in range(2):                                     # 关闭cv窗口
        cv.waitKey(1)
        cv.destroyAllWindows()

    




