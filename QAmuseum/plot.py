import matplotlib.pyplot as plt
from io import BytesIO
import base64
from PIL import Image

def Output_graph():
    buffer = BytesIO()
    plt.savefig(buffer,format="png",transparent=True)
    buffer.seek(0)
    img = buffer.getvalue()
    graph = base64.b64encode(img)
    graph = graph.decode("utf-8")
    buffer.close()
    return graph

def All_Plot_graph(path):
    spot_x,spot_y=graph_data()
    plt.switch_backend("AGG")
    plt.figure(figsize=(9,7),dpi=100)
    plt.ylim(-720,0)
    plt.xlim(0,940)
    plt.scatter(spot_x,spot_y,marker="")
    for i in range(len(path)-1):
        plt.annotate("",xy=[spot_x[int(path[i+1])],spot_y[int(path[i+1])]],xytext=[spot_x[int(path[i])],spot_y[int(path[i])]],arrowprops=dict(shrink=0, width=4, headwidth=10, 
                                headlength=10, connectionstyle='arc3',
                                facecolor='red', edgecolor='red'))
    plot_x=[]
    plot_y=[]
    for i in path:
        plot_x.append(spot_x[int(i)])
        plot_y.append(spot_y[int(i)])
    
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)
    plt.gca().spines['left'].set_visible(False)
    plt.tick_params(labelbottom=False, labelleft=False, labelright=False, labeltop=False, bottom=False, left=False, right=False, top=False)
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    graph= Output_graph()
    return graph

def Plot_graph(now_spot,next_spot,path):
    spot_x,spot_y=graph_data()
    waypoint=Waypoint(now_spot,next_spot)
    plt.switch_backend("AGG")
    plt.figure(figsize=(9,7),dpi=100)
    plt.ylim(-720,0)
    plt.xlim(0,940)
    plt.scatter(spot_x,spot_y,marker="")
    
    
    for i in range(len(waypoint)-1):
        plt.annotate("",xy=[spot_x[waypoint[i+1]],spot_y[waypoint[i+1]]],xytext=[spot_x[waypoint[i]],spot_y[waypoint[i]]],arrowprops=dict(shrink=0, width=4, headwidth=10, 
                                headlength=10, connectionstyle='arc3',
                                facecolor='red', edgecolor='red'))
        
    plot_x=[]
    plot_y=[]
    for i in path:
        plot_x.append(spot_x[int(i)])
        plot_y.append(spot_y[int(i)])
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)
    plt.gca().spines['left'].set_visible(False)
    plt.tick_params(labelbottom=False, labelleft=False, labelright=False, labeltop=False, bottom=False, left=False, right=False, top=False)
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    graph= Output_graph()
    return graph
#展示館の中継地点の追加（必要に応じて編集）
def Waypoint(now_spot,next_spot):
    waypoint =[]
    waypoint.append(now_spot)
    if now_spot <=4:
        if next_spot>=8 and next_spot<=15:
            waypoint.append(20)
            if next_spot >= 13 and next_spot<=15:
                waypoint.append(21)
                if next_spot==14 or next_spot==15:
                    waypoint.append(24)
                    waypoint.append(25)
        if next_spot==6:
            waypoint.append(20)
        if next_spot==16 or next_spot==17:
            waypoint.append(27)

    if now_spot==7 or now_spot==8:
        if next_spot >=9 and next_spot<=17:
            waypoint.append(28)
            if next_spot>=13 and next_spot<=17:
                waypoint.append(21)
                if next_spot>=14:
                    waypoint.append(24)
                    waypoint.append(25)
        if next_spot>=18:
            waypoint.append(30)
        if next_spot<=1:
            waypoint.append(30)

    if now_spot==5 or now_spot==6:
        if next_spot<=1:
            waypoint.append(20)
        if next_spot>=13 and next_spot<=17:
            waypoint.append(21)
            if next_spot >=14:
                waypoint.append(24)
                waypoint.append(25)
        if next_spot>=18:
            waypoint.append(20)

    if now_spot >= 9 and now_spot<=10:
        if next_spot<=2:
            waypoint.append(20)
        if next_spot==7 or next_spot==8:
            waypoint.append(28)
        if next_spot>=13:
            waypoint.append(21)
            if next_spot>=14 :
                waypoint.append(24)
                waypoint.append(25)
                if next_spot>=18:
                    waypoint.append(26)

    if now_spot>=11 and now_spot<=12:
        if next_spot <= 4:
            waypoint.append(20)
        if next_spot==7 or next_spot==8:
            waypoint.append(28)
        if next_spot ==14 or next_spot==15:
            waypoint.append(25)
        if next_spot>=18:
            waypoint.append(25)
            waypoint.append(26)
    if now_spot==13:
        if next_spot==14:
            waypoint.append(22)
            waypoint.append(23)
        if next_spot<=10:
            waypoint.append(21)
            if next_spot==7 or next_spot==8:
                waypoint.append(28)
            if next_spot<=4:
                waypoint.append(20)
        if next_spot==15:
            waypoint.append(22)
        if next_spot>=16:
            waypoint.append(24)
            if next_spot>=18:
                waypoint.append(26)
    if now_spot == 14:
        if next_spot == 13:
            waypoint.append(23)
            waypoint.append(22)
        if next_spot<=12:
            waypoint.append(25)
            if next_spot<=10:
                waypoint.append(24)
                waypoint.append(21)
                if next_spot==7 or next_spot==8:
                    waypoint.append(28)
                if next_spot<=4:
                    waypoint.append(20)
        if next_spot>=18:
            waypoint.append(26)

    if now_spot==15:
        if next_spot<=12:
            waypoint.append(25)
            if next_spot<=9:
                waypoint.append(21)
                if next_spot<=4:
                    waypoint.append(20)
                if next_spot==7 or next_spot==8:
                    waypoint.append(28)
        if next_spot >=16:
            if next_spot>=18:
                waypoint.append(26)
        if next_spot==13:
            waypoint.append(22)

    if now_spot>=16 and now_spot<=17:
        if next_spot<=5:
            waypoint.append(27)
        if next_spot>=6 and next_spot<=10:
            waypoint.append(21)
        if next_spot==13:
            waypoint.append(24)
        

    if now_spot==18:
        if next_spot<=10:
            waypoint.append(27)
        if next_spot>=11 and next_spot<=15:
            waypoint.append(26)
            if next_spot==13:
                waypoint.append(25)
                waypoint.append(24)
            
    if now_spot==19:
        if next_spot==6:
            waypoint(20)
        if next_spot>=8 and next_spot<=12:
            waypoint.append(20)
        if next_spot==13:
            waypoint.append(26)
            waypoint.append(25)
            waypoint.append(24)
        if next_spot==14:
            waypoint.append(26)
        if next_spot==15:
            waypoint.append(26)
    waypoint.append(next_spot)
    return waypoint

def graph_data():
    x=[570,#1
       480,#2
       440,#3
       320,#4
       215,#5
       200,#6
       200,#7
       370,#8
       340,#9
       290,#10
       210,#11
       310,#12
       320,#13
       450,#14
       560,#15
       490,#16
       580,#17
       720,#18
       720,#19
       730,#20
       
       270,#21
       270,#22
       450,#23
       560,#24
       450,#25
       560,#26
       630,#27
       670,#28
       270,#29
       580,#30
       370,#31
       
       ]
    y=[-585,#1
       -585,#2
       -665,#3
       -665,#4
       -650,#5
       -580,#6
       -480,#7
       -550,#8
       -520,#9
       -410,#10
       -350,#11
       -290,#12
       -160,#13
       -370,#14
       -370,#15
       -500,#16
       -530,#17
       -180,#18
       -430,#19
       -650,#20

       -630,#21
       -330,#22
       -420,#23
       -420,#24
       -300,#25
       -300,#26
       -340,#27
       -610,#28
       -510,#29
       -340,#30
       -640,#31
    ]
    return x,y
