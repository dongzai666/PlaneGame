import random
import pygame

# 屏幕大小的常量
SCREEN_RECT = pygame.Rect(0, 0, 480, 700)
# 创建敌机的事件
CREATE_ENEMY_EVENT = pygame.USEREVENT
# 英雄飞机发射子弹的事件
HERO_FIRE_EVENT = pygame.USEREVENT + 1
#几发子弹击毁敌机设置
DESTORY_ENEMY = 1
#分数记录
SCORE = 0
#用户登陆名
LOGIN_NAME = 'NULL'

class GameSprite(pygame.sprite.Sprite):
    """游戏主类"""

    def __init__(self, image_name, speed=1):
        # 调用父类的初始化方法
        super().__init__()
        # 定义属性
        self.image = pygame.image.load(image_name)
        self.rect = self.image.get_rect()
        self.speed = speed

    def update(self):
        # 在屏幕的垂直方向向下移动
        self.rect.y += self.speed

class Player_plane(GameSprite):
    """玩家飞机类"""
    def __init__(self,speed_y=0):
        # 设置速度为0
        super().__init__("./image/player1.png", speed=0)
        # 玩家飞机出场位置位于游戏主窗口的中央
        self.rect.centerx = SCREEN_RECT.centerx
        self.rect.bottom = SCREEN_RECT.height - 10
        # 创建子弹精灵组
        self.bullet_group = pygame.sprite.Group()
        self.speed_y = speed_y
    def update(self):
        # 英雄飞机在水平方向移动且不能移出边界
        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.right > SCREEN_RECT.width:
            self.rect.right = SCREEN_RECT.width
        else:
            self.rect.x += self.speed

         #控制上下移动
        if self.rect.y <0:
            self.rect.y =0
        elif self.rect.bottom > SCREEN_RECT.height:
            self.rect.bottom = SCREEN_RECT.height
        else:
            self.rect.y += self.speed_y       
        

    def fire(self):
        """玩家飞机发射子弹"""
            # 创建子弹精灵
        bullet = Bullet()
            # 设定子弹精灵的位置，应该与英雄飞机的正上方中央发射
        bullet.rect.y = self.rect.y 
        bullet.rect.centerx = self.rect.centerx
            # 子弹精灵加入精灵组
        self.bullet_group.add(bullet)

class Enemy(GameSprite):
    """敌机精灵类"""

    def __init__(self):
        super().__init__("./image/enemy1.png")
        # 随机抽出现在屏幕上的位置
        self.rect.x = random.randrange(0, (SCREEN_RECT.width - self.rect.width), 1)
        # 随机生成敌机出现速度
        self.speed = random.randint(1, 3)
        # 初始位置应该在游戏主窗口的上方
        self.rect.bottom = 0

    def update(self):
        # 向下移动
        super().update()
        # 判断敌机是否飞出屏幕，飞出则kill()
        if self.rect.y >= SCREEN_RECT.height:
            self.kill()


class Bullet(GameSprite):
    """子弹类"""
    def __init__(self):
        super().__init__("./image/bullet.png", speed=-3)

    def update(self):
        # 向下移动
        super().update()
        # 判断子弹是否飞出屏幕，飞出则kill()掉
        if self.rect.bottom <= 0:
            self.kill()

#GameOVer界面按键操作类

class Button(object):
    def __init__(self,text,x,y):
        self.text = text
        self.WIDTH = 120
        self.HEIGHT =30

        self.x = x
        self.y = y 
    
    def check_click(self,position):

        x_match = position[0] > self.x and position[0] < self.x + self.WIDTH
        y_match = position[1] > self.y and position[1] < self.y + self.HEIGHT

        if x_match and y_match:
            return True
        else:
            return False