# -*- coding: utf-8 -*-
# 多体引力模型

"""
Created on Sat Aug 24 12:09:32 2019

@author: _Mumu, Squirtle
Environment: base(py37 with pygame)
"""

import random, math, pygame, sys
from pygame.locals import *
import numpy as np

window_size = width, height = 960, 540  # 设置窗口大小
middle = np.array([width//2,
                   height//2])          # 中心点坐标
white = (255, 255, 255)                 # 白色
black = (0, 0, 0)                       # 黑色
num_font = None                         # 星体编号字体全局变量
text_font = None                        # 文本字体全局变量
pause_font = None                       # 暂停字体全局变量
screen = None                           # screen全局变量
#fps = 30                               # 帧率
time_step = 5                           # 计算的时间步长，单位为毫秒
tracking = False                        # 默认不跟踪质量最大的星体

body_list = []      # 星体列表
max_count = 200     # 初始星体数量
body_count = 0      # 实时形体数量
max_body = None     # 最大星体
max_path = 200      # 轨迹长度
G = 0.02            # 引力常数
den = 1             # 密度



class body:
    
    """
    Class:      星体
    CreateObj:  body(num, mass, x, y, vx, vy)
    
    模型假设:
        所有星体密度相同
        星体间的相互作用只有万有引力
        星体碰撞为完全非弹性碰撞
        碰撞时大星体吞噬小星体，没有质量损失
        碰撞后形成的新星体位置位于两星体的质心
    """
    
    def __init__(self, num, mass, x, y, vx, vy):
        
        """
        Method:     __init__                    构造方法
        Input:      num, mass, x, y, vx, vy     星体参数
        Return:     body                        星体类
        """
        self.num = num                          # 编号
        self.mass = mass                        # 质量
        self.r = self.calr()                    # 半径
        self.pos = np.array([x, y])             # 位置
        self.vel = np.array([vx, vy])           # 速度
        self.col = (random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255))     # 颜色
        self.path = []                          # 轨迹
        body_list.append(self)
    
    def calr(self):
        
        """
        Method:     calr        计算半径，为max_body赋值
        Input:      None
        Return:     self.r      星体半径
        """
        global max_body
        if max_body == None:
            max_body = self
        elif max_body.mass < self.mass:                 # 确定质量最大星体
            max_body = self
        
        return(np.cbrt(self.mass/den/math.pi*0.75))     # 计算半径
    
    def __draw(self):
        
        """
        Method:     __draw      显示星体，外接__show_path显示轨迹
        Input:      None
        Return:     None
        
        Variables:
        position    tuple       用于绘图的星体坐标，坐标值为整数
        radius      int         用于绘图的星体半径，为整数
        num_sf      Surface     标记星体编号的文字对象
        num_rect    Surface     承载星体编号文字的矩形框
        """
        num_sf = num_font.render("%d"%(self.num), True, white)
        num_rect = num_sf.get_rect()
        pos_move = self.r / 1.414
        
        if tracking == True:                                # 跟踪
            position = (int(self.pos[0] + 0.5
                            - max_body.pos[0] + middle[0]),
                        int(self.pos[1] + 0.5
                            - max_body.pos[1] + middle[1])) # 坐标取整
            
            num_rect.left = (self.pos[0] + pos_move
                             - max_body.pos[0] + middle[0])
            num_rect.top = (self.pos[1] - pos_move - num_rect.height
                            - max_body.pos[1] + middle[1])
        else:                                               # 不跟踪
            position = (int(self.pos[0] + 0.5),
                        int(self.pos[1] + 0.5))             # 坐标取整
            
            num_rect.left = self.pos[0] + pos_move
            num_rect.top = self.pos[1] - pos_move - num_rect.height
        
        radius = int(self.r + 0.5)                          # 半径取整
        pygame.draw.circle(screen, self.col,
                           position, radius, 0)             # 绘制实心圆
        screen.blit(num_sf, num_rect)                       # 显示星体编号
    
    def move(self):
        
        """
        Method:     move        移动星体
        Input:      None
        Return:     None
        """
        if len(self.path) == max_path / 4 and body_count > 15:
            self.path.pop(0)                        # 控制轨迹长度
        elif len(self.path) == max_path:
            self.path.pop(0)                        # 控制轨迹长度
        self.path.append(self.pos)
        self.__showpath()
        self.__draw()
        
        self.pos = self.pos + self.vel              # 更新位置
        self.vel = self.vel + self.__gforce()       # 更新速度
    
    def __gforce(self):
        
        """
        Method:     __gforce    计算引力
        Input:      None
        Return:     gf          星体受到的引力
        
        Variables:
        other       body        不同于self的其他星体
        vec_so      array       从self指向other的矢量
                                [# 原使用一半时间步长后的位置计算]
        dis_so      float       从self到other的距离
        gf_so       float       self受到other的引力加速度大小
        """
        gf = np.array([0, 0])
        for other in body_list:
            if other == self:
                continue
            else:
                #vec_so = (other.pos + other.vel / 2
                #          - self.pos - self.vel / 2)        # 引力方向

                vec_so = other.pos - self.pos               # 引力方向
                dis_so = np.linalg.norm(vec_so)             # 计算距离
                
                #if self.__collision(other, dis_so):         # 检测碰撞
                #    continue
                
                gf_so = (G * other.mass
                         / (dis_so ** 2))                   # 计算引力加速度大小
                gf = gf + gf_so * vec_so / dis_so           # 计算合加速度矢量
        
        return gf
    
    def __showpath(self):
        
        """
        Method:     __showpath  显示轨迹
        Input:      None
        Return:     None
        
        Variables:
        len_path    int         轨迹长度-1
        pos_a       array       轨迹起点坐标
        pos_b       array       轨迹终点坐标
        """
        len_path = len(self.path) - 1
        for i in range(1, len_path):
            
            if tracking == True:                    # 获取一段轨迹的起止点
                pos_a = self.path[i-1] - max_body.pos + middle
                pos_b = self.path[i] - max_body.pos + middle
            else:
                pos_a = self.path[i-1]
                pos_b = self.path[i]
            
            pygame.draw.line(screen, self.col,
                             pos_a, pos_b, 1)       # 画出一段轨迹


def init_window():
    
    """
    Function:   init_windows    窗口初始化
    Input:      None
    Return:     screen          背景Surface对象
    """
    global num_font, text_font, pause_font
    pygame.init()                                               # 初始化pygame
    dis_sf = pygame.display.set_mode(window_size)               # 显示窗口
    pygame.display.set_caption("Multibody Gravitation Model")   # 窗口标题
    num_font = pygame.font.SysFont("times", 10)                 # 设置字体
    text_font = pygame.font.SysFont("times", 12)                # 设置字体
    pause_font = pygame.font.SysFont("times", 20, True)         # 设置字体
    
    #clock = pygame.time.Clock()                                 # 初始化clock
    #clock.tick(fps)                                             # 设置最大帧率
    
    return dis_sf

def counting_stars(body_count):
    
    """
    Function:   counting_stars  显示剩余星体数
    Input:      body_count      实时星体数量
    Return:     None
    """
    count_sf = text_font.render("BODY LEFT: %d"%(body_count), True, white)
    count_rect = count_sf.get_rect()
    count_rect.left = 0
    count_rect.top = 0
    screen.blit(count_sf, count_rect)

def paused():
    
    """
    Function:   paused          显示暂停文字
    Input:      None
    Return:     None
    """
    pause_sf = pause_font.render("-PAUSE-", True, white)
    pause_rect = pause_sf.get_rect()
    pause_rect.left = middle[0] - pause_rect.width / 2
    pause_rect.top = 0
    screen.blit(pause_sf, pause_rect)

def check_collision():
        
    """
    Function:   check_collision     检测星体碰撞
    Input:		None
    Output:     max_body_list		存储每一组碰撞事件中的最大星体
    			collide_event_list  存储每一组碰撞事件的列表，表中包含参与碰撞的星体
    """
    global body_count, body_list

    collide_event_list = []
    max_body_list = []

    stars = list(range(body_count))						# 用于循环的临时列表，处理后的死星将会设为-1，跳过当前循环

    for i in stars:
    	if i == -1:
    		continue

    	collide_body_list = []                                  # 开始统计单次事件中的碰撞星体
    	max_body = body_list[i]                                 # 将max_body初始化为i星球

    	for j in stars:
    		if j <= i:                                          # 确保j一定比i大，减少for循环体积（该判断包含j == -1的情况）
    			continue

    		dis_so = np.linalg.norm(body_list[j].pos - body_list[i].pos)

    		if dis_so <= body_list[j].r + body_list[i].r:       # 如果发生碰撞
    			collide_body_list.append(body_list[j])          # 将j星球加入collide_body_list豪华套餐
    			stars[j] = -1                                   # 将j星球设为-1，再起不能
    			if body_list[j].mass > max_body.mass:           # 如果j星球是当前豪华套餐中最大滴...
    				max_body = body_list[j]                     # 把j星球设为最大星球！

    	if collide_body_list:                                   # 如果套餐中有星星，说明i星球本尊也被撞了
    		collide_body_list.append(body_list[i])              # 将i星球加入collide_body_list豪华套餐
    		stars[i] = -1                                       # 将i星球设为-1，再起不能

    		collide_event_list.append(collide_body_list)        # 将豪华套餐加入菜单
    		max_body_list.append(max_body)                      # 将最大星球加入菜单目录

    return max_body_list, collide_event_list                    # 返回菜单目录和菜单

def merge(max_body, collide_body_list):

    """
    Function:   merge			    处理星体碰撞
    Input:		max_body 			碰撞中最大星球
    			collide_body_list	参与碰撞的星球列表
    Output:     None
    """
    global body_count, body_list

    for other in collide_body_list:
        if max_body == other:
            continue

        max_body.mass = max_body.mass + other.mass              # 计算过程抄的你的
        max_body.r = max_body.calr()
        max_body.pos = ((max_body.mass - other.mass) * max_body.pos
                        + other.mass * other.pos) / max_body.mass
        max_body.vel = ((max_body.mass - other.mass) * max_body.vel
                        + other.mass * other.vel) / max_body.mass

        body_list.remove(other)
        body_count = body_count - 1

def collision():

    """
    Function:   collision			合并上面两个函数，没啥NB之处
    Input:		None
    Output:     None
    """
    max_body_list, collide_event_list = check_collision()
    for i in range(len(max_body_list)):
    	merge(max_body_list[i], collide_event_list[i])

def track_text():
    
    """
    Function:   paused          显示追踪状态
    Input:      None
    Return:     None
    """
    track_sf = text_font.render("TRACKING", True, white)
    track_rect = track_sf.get_rect()
    track_rect.left = width - track_rect.width
    track_rect.top = 0
    screen.blit(track_sf, track_rect)

def body_info(star):
    
    """
    Function:   body_info       显示星体信息
    Input:      star            星体对象
    Return:     None
    """
    star_sf = text_font.render("BODY NO.%d:"%
                               (star.num),              # 星体编号
                                True,
                                star.col)
    star_rect = star_sf.get_rect()
    index = body_list.index(star) + 1
    star_rect.left = 0
    star_rect.top = -20 + 3 * index * star_rect.height
    screen.blit(star_sf, star_rect)
    
    mass_sf = text_font.render("MASS: %d"%
                               (star.mass),             # 星体质量
                                True,
                                star.col)
    mass_rect = mass_sf.get_rect()
    mass_rect.left = 0
    mass_rect.top = -20 + (3 * index + 1) * mass_rect.height
    screen.blit(mass_sf, mass_rect)
    
    if tracking:
        pos_sf = text_font.render("POSITION: (%d, %d)"%
                                  (star.pos[0]-max_body.pos[0]+0.5, # 相对坐标
                                   star.pos[1]-max_body.pos[1]+0.5),# 相对坐标
                                   True,
                                   star.col)
    else:
        pos_sf = text_font.render("POSITION: (%d, %d)"%
                                  (star.pos[0]+0.5,         # 横坐标
                                   star.pos[1]+0.5),        # 纵坐标
                                   True,
                                   star.col)
    pos_rect = pos_sf.get_rect()
    pos_rect.left = 0
    pos_rect.top = -20 + (3 * index + 2) * star_rect.height
    screen.blit(pos_sf, pos_rect)


if __name__ == "__main__":
    
    screen = init_window()                  # 窗口初始化
    x, y = width // 2, height // 2          # 中心点坐标
    
    running = True                          # 程序运行状态
    
    for i in range(1, max_count + 1):
        body(i,
             random.randint(100, 300),          # 初始质量
             random.randint(0, width),
             random.randint(0, height),         # 初始坐标
             random.randint(-120, 120)/100,
             random.randint(-120, 120)/100)     # 初始速度
    body_count = len(body_list)
    
    while True:                                     # 死循环确保窗口一直显示
        for event in pygame.event.get():            # 遍历所有事件
            if event.type == QUIT:                  # 如果单击关闭窗口，则退出
                sys.exit(0)
            if event.type == KEYDOWN:               # 检测按键
                if event.key == K_SPACE:            # 空格，Pause或Resume
                    running = not running;
                if event.key == K_BACKSPACE:        # 空格，修改追踪状态
                    tracking = not tracking
        
        collision()                                 # 触发碰撞融合
        
        if running:
            screen.fill(black)                      # 背景重新填充为黑色

            for star in body_list:
                star.move()
            for star in body_list:
                body_info(star)
            
            counting_stars(body_count)

        else:
            paused()
        
        if tracking:
            track_text()
        
        pygame.display.flip()                       # 更新全部显示
        pygame.time.wait(time_step)                 # 延迟

    pygame.quit()                           # 退出pygame