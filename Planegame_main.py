import tkinter
from Planegame_Module import *
import time
import threading
import pymssql #数据库模块
from PIL import Image,ImageTk #加载图片处理模块
"""
写在前面，数据库链接需要本地配置好环境，然后需要手动在sqlserver新建一个数据库
，最好是同时新建一个表， 设置两个参数 name nvarchar(20) not null 和  score int not null 即可
->更改程序中sqlserver登陆的用户名，密码等信息即可
"""
#数据库参数
host="."  #服务器名
user="sa"  #账户名
password="888"  #密码
database="PlaneGame"  #数据库名
charset="utf8" #编码格式，不建议更改

#数据库操作   
class SqlServer(object):

    def __init__(self):

        self.connect = pymssql.connect(host,user,password,database,charset)
        self.__open_Sql()
        self.cursor = self.connect.cursor()  #创建游标对象
        #在PlaneGame数据库下创建名为Score的表，参数有name 和 score
        #不存在则创建
        if self.table_exists(self.cursor,'Score'):
            self.cursor.execute("CREATE TABLE  Score(name varchar(20) not null,score int not null)")
            self.connect.commit()

        self.ns_dict={}

    
    def __open_Sql(self):

        if self.connect:
            print("数据库连接成功！")
        else:
            print("数据库连接失败！")
            
    #添加数据
    def insert(self,player_name,player_score):
        print("开始添加数据库")
        sql_insert = "select name,score from Score"
        self.cursor.execute(sql_insert)

        row = self.cursor.fetchall()
        print(row)
        #对于重复数据进行删除操作 
        if len(row) != 0:
            for i in range(len(row)):
                #用户名相同
                if player_name == row[i][0]:
                    #进一步判断分数
                    if player_score > row[i][1]:
                        self.delete(player_name)
                    else:
                        player_name = row[i][0]
                        player_score = row[i][1]
                        self.delete(row[i][0])

        sql = "insert into Score (name,score)values(%s,%s)"
        print("++++++++++++++")
        print(player_name)
        self.cursor.execute(sql,(player_name,player_score))
        self.connect.commit()
        print("添加数据库成功")

    #查询数据
    def select(self):
        print("开始查询数据库")
        sql = "select name,score from Score"
        self.cursor.execute(sql)
        row = self.cursor.fetchone() #读取查询结果
        while row:
            self.ns_dict[row[1]]=row[0]
            row = self.cursor.fetchone()
        
        #查询完毕，关闭数据库
        self.cursor.close()
        self.connect.close()
        print("查询完毕并关闭")

    def delete(self,name):
        sql = "Delete From Score Where name=%s"
        self.cursor.execute(sql,(name))
        self.connect.commit()
        print("存在相同数据并更新完毕")


    #判断数据库中表是否存在
    def table_exists(self,con,table_name):       
        sql = "SELECT NAME FROM SYSOBJECTS WHERE TYPE='U'" 
        con.execute(sql)
        
        list_table = con.fetchall()[0]
        
        if table_name in list_table:
            print("数据库中表已经存在！")
            return 0        #存在返回0
        else:
            print("数据库中表不存在！")
            return 1  


#获取用户名
def Get_Logname(name):
    global LOGIN_NAME
    LOGIN_NAME = name
    print("用户名\n")
    print(LOGIN_NAME)


class PlaneGame(object):
    """主游戏类"""
    background = pygame.image.load("./image/background.png")
    gameover_background = pygame.image.load("./image/gameover.png")
    def __init__(self):
        print("游戏正在初始化...")
        # 创建游戏主窗口
        self.screen = pygame.display.set_mode(SCREEN_RECT.size)
        # 创建游戏时钟
        self.clock = pygame.time.Clock()
        # 调用私有方法，创建精灵和精灵组
        self.__create_sprites()
        pygame.time.set_timer(CREATE_ENEMY_EVENT, 1000)
        pygame.time.set_timer(HERO_FIRE_EVENT, 300)

    def __create_sprites(self):
        self.player_plane = Player_plane()
        self.player_plane2 = Player_plane()
        # 创建游戏飞机精灵组
        self.player_group = pygame.sprite.Group(self.player_plane,self.player_plane2)
        # 创建敌机精灵组
        self.enemy_group = pygame.sprite.Group()

    def start_game(self):
        """启动游戏"""
        # 游戏主循环
        while True:
            # 设置刷新帧率
            self.clock.tick(110)
            # 事件监听
            self.__event_handler()
            # 碰撞检测
            self.__check_collide()
            # 位置更新
            self.__update_sprites()
            # 游戏主窗口刷新显示
            pygame.display.update()

    def __check_collide(self):
        """碰撞检测"""
        # 子弹与敌机之间的碰撞检测
        temp_dict = pygame.sprite.groupcollide(self.enemy_group, self.player_plane.bullet_group, False, True)
        temp_dict2 = pygame.sprite.groupcollide(self.enemy_group, self.player_plane2.bullet_group, False, True)
        
        #遍历查找符合要求的被击毁敌机
        global SCORE
        for key,value in temp_dict.items():
            
            if(len(value) >= DESTORY_ENEMY):
                self.__enemy_destory(key.rect.x,key.rect.y)
                key.kill()
                SCORE += 1000

        for key,value in temp_dict2.items():
            if(len(value) >= DESTORY_ENEMY):
                self.__enemy_destory(key.rect.x,key.rect.y)
                key.kill()
                SCORE += 1000

        # 英雄飞机与敌机之间的碰撞检测
        enemy_list = pygame.sprite.spritecollide(self.player_plane, self.enemy_group, True)
        enemy_list2 = pygame.sprite.spritecollide(self.player_plane2, self.enemy_group, True)
        # 如果有一个飞机发生了碰撞，游戏结束
        if len(enemy_list) > 0 or len(enemy_list2) > 0:
            self.__player_destory(self.player_plane.rect.x,self.player_plane.rect.y)
            #此时应当将所有精灵组都kill掉
            # self.player_plane.kill()
            # self.player_plane2.kill()

            time.sleep(1)
            self.screen.blit(PlaneGame.gameover_background,(0,0))
            
            ''' 数据库操作 '''
            Pysq = SqlServer()

            Pysq.insert(LOGIN_NAME,SCORE)
            Pysq.select()

            DaoXU_List = {}
            keys = sorted(Pysq.ns_dict.keys(),reverse= True)
            for key in keys:
                DaoXU_List[Pysq.ns_dict[key]] = key

            #更新数据库信息
            SQL = SqlServer()
            for key in DaoXU_List.items():
                SQL.delete(key)
            
            for key,value in DaoXU_List.items():
                SQL.insert(key,value)
            SQL.cursor.close()
            SQL.connect.close()
            
            #绘制game_over界面
            score_font = pygame.font.SysFont("华文宋体",30)

            score_now = score_font.render("%s"% SCORE,True,(0,255,0))
            self.screen.blit(score_now,(230,300))

            #定义重新开始游戏按钮和查看排行榜按钮
            start_again = Button('重新开始',200, 350)
            Rank_list = Button('排行榜',200, 400)

            start_again_text = score_font.render('重新开始',True,(0,255,0))
            Rank_list_text = score_font.render('排行榜',True,(0,255,0))
    
            self.screen.blit(start_again_text,(start_again.x,start_again.y))
            self.screen.blit(Rank_list_text,(Rank_list.x,Rank_list.y))

            pygame.display.update()

            while True:
                if start_again.check_click(pygame.mouse.get_pos()):
                    start_again_text = score_font.render(start_again.text,True,(255,0,0))
                    self.screen.blit(start_again_text,(start_again.x,start_again.y))
                else:
                    start_again_text = score_font.render(start_again.text,True,(0,255,0))
                    self.screen.blit(start_again_text,(start_again.x,start_again.y))

                if Rank_list.check_click(pygame.mouse.get_pos()):
                    Rank_list_text = score_font.render(Rank_list.text,True,(255,0,0))
                    self.screen.blit(Rank_list_text,(Rank_list.x,Rank_list.y))
                else:
                    Rank_list_text = score_font.render(Rank_list.text,True,(0,255,0))
                    self.screen.blit(Rank_list_text,(Rank_list.x,Rank_list.y))
                    
                pygame.display.update()

                for event in  pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()

                if pygame.mouse.get_pressed()[0]:
                    if start_again.check_click(pygame.mouse.get_pos()):
                        SCORE = 0
                        self.start_game()
                    if Rank_list.check_click(pygame.mouse.get_pos()):
                        break
                

            #绘制得分情况
            print("排行榜！！！")
            self.screen.blit(PlaneGame.gameover_background,(0,0))
            pygame.display.update()
            i = 0
            j = 1
            score_Rant = score_font.render("Rant",True,(0,0,255))
            score_Name = score_font.render("Name",True,(0,0,255))
            score_nu = score_font.render("Score",True,(0,0,255))

            #退出按钮
            logout_button = Button('退出游戏',200,600)
            logout_button_text = score_font.render(logout_button.text,True,(0,255,0))

            self.screen.blit(score_Rant,(120,50))
            self.screen.blit(score_Name,(200,50))
            self.screen.blit(score_nu,(300,50))
            for key,value in DaoXU_List.items():
                score_text2 = score_font.render("%s"% j,True,(255,0,0))
                score_text = score_font.render("%s" % key, True,(255,0,0))
                score_text1 = score_font.render("%s"% value,True,(255,0,0))
                self.screen.blit(score_text2,(120,100+i))
                self.screen.blit(score_text,(200,100+i))
                self.screen.blit(score_text1,(300,100+i))
                i+= 50
                j+=1
            pygame.display.update()
            while True:
                if logout_button.check_click(pygame.mouse.get_pos()):
                    logout_button_text = score_font.render(logout_button.text,True,(255,0,0))
                    self.screen.blit(logout_button_text,(logout_button.x,logout_button.y))
                else:
                    logout_button_text= score_font.render(logout_button.text,True,(0,255,0))
                    self.screen.blit(logout_button_text,(logout_button.x,logout_button.y))

                pygame.display.update()
                for event in  pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                if pygame.mouse.get_pressed()[0]:
                    if logout_button.check_click(pygame.mouse.get_pos()):
                       pygame.quit()
                       exit() 

    #敌机爆炸效果
    def __enemy_destory(self,x,y):

        #加载爆炸图片列表
        enemy_destory_list = []
        for i in range(1,4):
            enemy_destory_list.append(pygame.image.load("./image/enemy_destory"+str(i)+".png"))
        #播放爆炸图
        for i in range(0,3):
            self.screen.blit(enemy_destory_list[i],(x,y))
            pygame.display.update()
            time.sleep(0.005)

    def __player_destory(self,x,y):

        player_destory_list = []
        for i in range(1,4):
            player_destory_list.append(pygame.image.load("./image/player_destory"+str(i)+".png"))
        for i in range(0,3):
            self.screen.blit(player_destory_list[i],(x,y))
            pygame.display.update()
            time.sleep(0.1)
            

    def __event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                PlaneGame.__game_over()
            elif event.type == CREATE_ENEMY_EVENT:
                # 创建敌机精灵同时加入精灵组
                self.enemy_group.add(Enemy())
            elif event.type == HERO_FIRE_EVENT:
                self.player_plane.fire()
                self.player_plane2.fire()

        # 按键判断
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_d]:
            self.player_plane.speed = 2
        elif keys_pressed[pygame.K_a]:
            self.player_plane.speed = -2
        else:
            # 当没有按下左右方向键
            self.player_plane.speed = 0

        if keys_pressed[pygame.K_w]:
            self.player_plane.speed_y = -2
        elif keys_pressed[pygame.K_s]:
            self.player_plane.speed_y = 2
        else:
            self.player_plane.speed_y = 0

        """第二个玩家的操作"""
        if keys_pressed[pygame.K_RIGHT]:
            self.player_plane2.speed = 2
        elif keys_pressed[pygame.K_LEFT]:
            self.player_plane2.speed = -2
        else:
            # 当没有按下左右方向键
            self.player_plane2.speed = 0

        if keys_pressed[pygame.K_UP]:
            self.player_plane2.speed_y = -2
        elif keys_pressed[pygame.K_DOWN]:
            self.player_plane2.speed_y = 2
        else:
            self.player_plane2.speed_y = 0

    def __update_sprites(self):
        """位置更新"""

        self.screen.blit(PlaneGame.background,(0,0))

        self.enemy_group.update()
        self.enemy_group.draw(self.screen)
        self.player_group.update()
        self.player_group.draw(self.screen)
        self.player_plane.bullet_group.update()
        self.player_plane.bullet_group.draw(self.screen)
        self.player_plane2.bullet_group.update()
        self.player_plane2.bullet_group.draw(self.screen)

    @staticmethod
    def __game_over():
        # 结束游戏
        pygame.quit()


#防止按钮卡死，守护进程              
class MyThread(threading.Thread):
    def __init__(self, func, *args):
        super().__init__()
        
        self.func = func
        self.args = args
        
        self.setDaemon(True)
        self.start()    # 在这里开始
        
    def run(self):
        self.func(*self.args)


if __name__ == '__main__':
    """GUI部分"""

    #开始登陆界面
    window = tkinter.Tk()
    window.title("飞机大战--登陆界面")
    window.geometry("400x400")

    #加载背景图片
    img = Image.open("./image/LgBackground.jpg").resize((800,800))

    #创建登陆界面画布
    canvas_window = tkinter.Canvas(window,width=800,height=800)
    im_window = ImageTk.PhotoImage(img)
    canvas_window.create_image(0,0,image=im_window)
    canvas_window.pack()

    #各具体按钮功能框
    label_title = tkinter.Label(window,text = "飞机大战",
    font=('隶书',35,'italic'),
    anchor='center')
    label_title.place(x=80,y=100,height=35,width=210)

    label_name = tkinter.Label(window,text="请输入用户名",
    font=('宋体',12,'italic'),
    anchor='center')
    label_name.place(x=135,y=200,height=15,width=100)

    login_name = tkinter.StringVar()

    entry = tkinter.Entry(window,textvariable=login_name)
    entry.place(x=130,y=230,height=20,width=110)

    #定义为StringVar()类型后该参数时实时更新的然后通过 entry.get()来实时获取
    # button1 = tkinter.Button(window,text="test",command= lambda:MyThread(print("用户名：{}".format(entry.get()))))
    #获取用户名
    button_yes = tkinter.Button(window,text="开始游戏",command= lambda:[pygame.init(),Get_Logname(entry.get()),window.withdraw(),PlaneGame().start_game()])
    button_no = tkinter.Button(window,text="退出游戏",command= lambda: window.destroy())

    button_yes.place(x=80,y=300,height=30,width=60)
    button_no.place(x=230,y=300,height=30,width=60)
    # button1.place(x=260,y=350,height=30,width=60)
    
    window.mainloop()
