# -*- coding: utf-8 -*-
# 多体引力模型向量化模型

"""
Created on Sun Sept 1 21:45:16 2019

@author: _Mumu, Squirtle
Environment: py37 with pygame
"""

NUM, MASS, X, Y, VX, VY = [], [], [], [], [], []
body_list = []
body_count = 0

class body:
    
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
        X.append(x) 				            # 横坐标
        Y.append(y) 				            # 横坐标
        VX.append(vx) 				            # 速度X分量
        VY.append(vy) 				            # 速度Y分量
        self.col = (random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255))     # 颜色
        body_list.append(self)



class universe:
    
    """
    Class:      宇宙，即向量化的所有星体
    CreateObj:  universe(NUM, MASS, X, Y, VX, VY) 	所有参数为body的向量化版本
    
    模型假设:
        所有星体密度相同
        星体间的相互作用只有万有引力
        星体碰撞为完全非弹性碰撞
        碰撞时大星体吞噬小星体，没有质量损失
        碰撞后形成的新星体位置位于两星体的质心
    """
    
    def __init__(self, NUM, MASS, X, Y, VX, VY):
        
        """
        Method:     __init__                    构造方法
        Input:      NUM, MASS, X, Y, VX, VY     宇宙参数
        Return:     universe                    宇宙类
        """
        self.NUM = NUM                          # 编号
        self.MASS = MASS                        # 质量
        self.R = self.calr()                    # 半径
        self.X = X 				                # 横坐标
        self.Y = Y 				                # 纵坐标
        self.VX = VX 				            # 速度X分量
        self.VY = VY 				            # 速度Y分量
        self.PATH = []                          # 轨迹列表

    def move_pos():
        X = X + VX
        Y = Y + VY
    
    def move_vel():
        VX = VX + AX
        VY = VY + AY
    
    def accel(id):
        ones = np.ones((body_count,body_count))
        eyes = np.eye(body_count)
    
        AX2d = G*m*(X*ones - (X*ones).T) / (DIS**3 + eyes)
        AX = np.sum(AX2d, axis = 1)
        AY2d = G*m*(Y*ones - (Y*ones).T) / (DIS**3 + eyes)
        AY = np.sum(AY2d, axis = 1)
    
        return AX, AY


def main():

	"""
    Function:   main 		主函数
    Input:      None
    Output:     Unknown 	模拟画面
    """
	for i in range(1, max_count + 1):
        body(i,
             random.randint(50, 150),           # 初始质量
             random.randint(0, width),
             random.randint(0, height),         # 初始坐标
             random.randint(-120, 120)/100,
             random.randint(-120, 120)/100)     # 初始速度
    body_count = len(body_list)
    stars = universe(NUM, MASS, X, Y, VX, VY)



if __name__ == '__main__':
	main()
