from typing import Any, Dict
from django.forms.models import BaseModelForm
from django.shortcuts import render, reverse,redirect
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth.models import User
from .models import UserPath,OmuraMuseum,MuseumEvaluation
from .omuracalculate import calculatepath,time_for_move_calc,time_stay,recalculate,data
from QAmuseum.views_modules import module
from django.views.generic import ListView,CreateView
from .forms import parameterform,NameForm,EvaluationForm,parameterEnform
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from PIL import Image
import time
#from .recalculate import recalculate
from celery import shared_task
from celery.result import AsyncResult
from django_celery_results.models import TaskResult
# Create your views here.

#スタート画面
def Start(request):
    return render(request,"QAmuseum/Start.html")

#美術館選択画面
class Name(CreateView):
    template_name="QAmuseum/Name.html"
    #form_class=NameForm
    model=UserPath
    fields=['name']
    def get_form(self,form_class=None):
        form = super().get_form(form_class)
        form.fields['name'].widget.attrs['placeholder'] = '名前を入力'
        form.fields['name'].widget.attrs['class']='large-textbox'
        form.fields['name'].label =''
        return form
    def get_success_url(self):
        username=self.request.POST.get('name')
        pk=self.object.pk
        #print(type(username) is str)
        print(pk)
        return reverse("Parameter",kwargs={'pk':pk})
class Name_En(CreateView):
    template_name="QAmuseum/Name_En.html"
    #form_class=NameForm
    model=UserPath
    fields=['name']
    def get_form(self,form_class=None):
        form = super().get_form(form_class)
        form.fields['name'].widget.attrs['placeholder'] = 'Name'
        form.fields['name'].widget.attrs['class']='large-textbox'
        form.fields['name'].label =''
        return form
    def get_success_url(self):
        username=self.request.POST.get('name')
        pk=self.object.pk
        #print(type(username) is str)
        print(pk)
        return reverse("Parameter",kwargs={'pk':pk})

#パラメータ設定画面
def Parameter(request,pk):
    print(type(pk) is str)
    obj=UserPath.objects.get(pk=pk)
    
    initial_values={"time":obj.time,"speed":obj.speed,"browse":obj.browse,"demand":'0'}
    form = parameterform(initial_values)
    ctx={"form":form,'pk':pk}
    if request.POST:
        form=parameterform(request.POST)
        if form.is_valid():
            time = form.cleaned_data["time"]
            speed = form.cleaned_data["speed"]
            browse=form.cleaned_data["browse"]
            obj.time=time
            obj.speed=speed
            obj.browse=browse
            obj.count_time=0
            obj.calc_bool=False
            obj.save()
            user_path=UserPath.objects.filter(pk=pk)
            for user_path in user_path:
                object={
                    "path":user_path.path,
                    "nowspot":user_path.now_spot+1,
                    "nextspot":user_path.next_spot+1,
                    "pk":user_path.pk
                }
            object=UserPath.objects.get(pk=pk)
            #return render(request,"QAmuseum/CalculatePath.html/",{"pk":pk,"user_path":object})
            #return reverse("MuseumPath",kwargs={"pk":pk,"user_path":object})
            return render(request,"QAmuseum/CalculatePath.html/",{'object':object,'pk':pk})
    return render(request, "QAmuseum/Parameter.html",ctx)

def Parameter_En(request,pk):
    print(type(pk) is str)
    obj=UserPath.objects.get(pk=pk)
    
    initial_values={"time":obj.time,"speed":obj.speed,"browse":obj.browse,"demand":'0'}
    form = parameterEnform(initial_values)
    ctx={"form":form,'pk':pk}
    if request.POST:
        form=parameterform(request.POST)
        if form.is_valid():
            time = form.cleaned_data["time"]
            speed = form.cleaned_data["speed"]
            browse=form.cleaned_data["browse"]
            obj.time=time
            obj.speed=speed
            obj.browse=browse
            obj.count_time=0
            obj.calc_bool=False
            obj.save()
            user_path=UserPath.objects.filter(pk=pk)
            for user_path in user_path:
                object={
                    "path":user_path.path,
                    "nowspot":user_path.now_spot+1,
                    "nextspot":user_path.next_spot+1,
                    "pk":user_path.pk
                }
            object=UserPath.objects.get(pk=pk)
            #return render(request,"QAmuseum/CalculatePath.html/",{"pk":pk,"user_path":object})
            #return reverse("MuseumPath",kwargs={"pk":pk,"user_path":object})
            return render(request,"QAmuseum/CalculatePath.html/",{'object':object,'pk':pk})
    return render(request, "QAmuseum/Parameter_En.html",ctx)


#計算画面
""""
class CalculatePath(ListView):
    template_name="QAmuseum/CalculatePath.html"
    context_object_name="user_path"
    
    model=UserPath
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset=UserPath.objects.filter(pk=self.kwargs['pk'])
"""
def CalculatePath(request,pk):
    """"
    user_path=UserPath.objects.filter(pk=pk)
    for user_path in user_path:
        object={
            "path":user_path.path,
            "nowspot":user_path.now_spot+1,
            "nextspot":user_path.next_spot+1,
            "pk":user_path.pk
        }
        """
    object=UserPath.objects.get(pk=pk)
    #return render(request,"QAmuseum/CalculatePath.html",dict(user_path=obj))
    return render(request,"QAmuseum/CalculatePath.html",{'object':object,'pk':pk})
#計算実行
def caluculate(request,pk):
    if request.method =='GET':
        #data=calctest()
        userpath=UserPath.objects.get(pk=pk)
        
        path_data ,goal_time= calculatepath(userpath.time,userpath.speed,userpath.browse)
        print(goal_time)
        data=[]
        data.append(path_data)
        pd=str(path_data)
        pa = pd.replace(']','')
        path = pa.replace('[','')
        userpath.path = path
        userpath.now_spot=path_data[0]
        userpath.next_spot=path_data[1]
        visit_path=[0]
        pd=str(visit_path)
        pa = pd.replace(']','')
        visit_path = pa.replace('[','')
        userpath.visit_path=visit_path
        userpath.count=0
        userpath.goal_time=goal_time
        userpath.calc_bool=False
        userpath.save()
        return HttpResponse(data)


def AllMuseum(request,pk):
    userpath = UserPath.objects.filter(pk=pk)
    for userpath in userpath:
        object = {
            "path":userpath.path,
            "nowspot":userpath.now_spot+1,
            "nextspot":userpath.next_spot+1,
            "goaltime":userpath.goal_time,
            "pk":userpath.pk
            }
    pt=userpath.path.split(',')
    graph = All_Plot_graph(pt)
    object['graph']=graph
    return render(request,"QAmuseum/AllMuseumPath.html",object)

#経路表示画面
def MuseumPath(request,pk):
    if "reset" in request.GET:
            obj =UserPath.objects.get(pk=pk)
            path = obj.path.split(',')
            if obj.count > 0:
                obj.count = obj.count-1
                obj.now_spot=path[obj.count]
                obj.next_spot=path[obj.count+1]
                obj.save()
    
    userpath = UserPath.objects.filter(pk=pk)
    for userpath in userpath:
        if userpath.calc_bool==True:
            back_task=AsyncResult(userpath.caluculate_back)
            print(back_task.status)
            if back_task.status=="STARTED":
                back_task.revoke(terminate=True)
            if back_task.status=="SUCCESS":
                print(back_task.result)
                if len(back_task.result) != 0:
                    path=back_task.result
                    print(type(path))
                    userpath.path=path
                    pt=userpath.path.split(',')
                    userpath.next_spot = int(pt[1])
                    userpath.count=0
                    userpath.count_time=userpath.count_time+time.time()-userpath.start_time
                    userpath.start_time=time.time()
                    userpath.calculate_count =userpath.calculate_count+1
                    userpath.calc_bool=False
                    userpath.save()
        if userpath.now_spot==0:
            start_time=time.time()
            userpath.start_time=start_time
            userpath.save()
        object = {
            "path":userpath.path,
            "nowspot":userpath.now_spot+1,
            "nextspot":userpath.next_spot+1,
            "pk":userpath.pk
            }
    nowsp=userpath.now_spot+1
    nextsp=userpath.next_spot+1
    now_spot=OmuraMuseum.objects.get(id=nowsp)
    next_spot=OmuraMuseum.objects.get(id=nextsp)
    spot={"nowspot_name":now_spot.name,
          "nextspot_name":next_spot.name}
    object.update(spot)
    pt=userpath.path.split(',')
    graph = Plot_graph(userpath.now_spot,userpath.next_spot,pt)
    object['graph']=graph
    return render(request, "QAmuseum/MuseumPath.html",object)
    #return reverse("MuseumPath",kwargs={'pk':pk})

def Evaluation(request,pk):
    if request.method=="POST":
        form = EvaluationForm(request.POST)
        if form.is_valid():
            ev=form.cleaned_data["display_evaluation"]
            if int(ev)==0:
                print(ev)
                return redirect("Arrive",pk)
            else:
                userpath=UserPath.objects.get(pk=pk)
                spot=OmuraMuseum.objects.get(id=userpath.now_spot+1)
                evaluation=MuseumEvaluation.objects.create(display_id=userpath.now_spot,display_name=spot.name,display_evaluation=ev,user_name=userpath.name,display_time=time.time()-userpath.now_time)
    else:
        form=EvaluationForm()
    return redirect("MuseumPath",pk)


def Arrive(request,pk):
    if request.method == 'GET':
        if "arrive" in request.GET:
            obj = UserPath.objects.get(pk=pk)
            path=obj.path.split(',')
            print(path)
            count=obj.count
            if not obj.next_spot==0:
                temp_path=obj.visit_path.split(',')
                visit_path=[]
                for i in temp_path:
                    visit_path.append(int(i))
                visit_path.append(int(path[count+1]))
                pd=str(visit_path)
                pa = pd.replace(']','')
                visit_path = pa.replace('[','')
                obj.visit_path=visit_path
                obj.count=count+1
                obj.now_spot=path[obj.count]
                obj.next_spot=path[obj.count+1]
                obj.save()

                userpath=UserPath.objects.get(pk=pk)
                path = userpath.path.split(',')
                mid_time=time.time()
                userpath.now_time=mid_time
                predict_time=predict(path,userpath.now_spot,userpath.speed,userpath.browse)
                userpath.predict_time=predict_time
                userpath.save()
                if int(predict_time) != int(userpath.now_time-userpath.start_time)/60:
    #if predict_time>0:
                    print(predict_time*60)
                    print(userpath.now_time-userpath.start_time)
                    print("time over")
                    T=userpath.time-(userpath.now_time-userpath.start_time)/60-userpath.count_time/60
                    speed_move=userpath.speed
                    speed_watch=userpath.browse
                    temp_path=userpath.visit_path.split(',')
                    visit_spot=[]
                    for i in temp_path:
                        visit_spot.append(int(i))
                    now_spot=userpath.now_spot
                    now_path=userpath.path
                    pt=back_calc.delay(T,speed_move,speed_watch,visit_spot,now_spot)
                    userpath.caluculate_back=pt.id
                    userpath.calc_bool=True
                    userpath.save()
                    """
                    path=recalculate(T,speed_move,speed_watch,visit_spot,now_spot)
                    if len(path) >2:
                        userpath.next_spot=path[1]
                        #print(path)
                        pd=str(path)
                        pa = pd.replace(']','')
                        path = pa.replace('[','')
                        userpath.path=path
                        userpath.count=0
                        userpath.start_time=time.time()
                        userpath.calculate_count =userpath.calculate_count+1
                        userpath.save()
                    else:
                        userpath.next_spot=0
                        now_spot=userpath.now_spot
                        path=[]
                        path.append(now_spot)
                        path.append(0)
                        pd=str(path)
                        pa = pd.replace(']','')
                        path = pa.replace('[','')
                        userpath.path=path
                        userpath.count=0"""
            #userpath.save()
            else:
                return render(request,"QAmuseum/End.html")
        if "reset" in request.GET:
            obj =UserPath.objects.get(pk=pk)
            path = obj.path.split(',')
            if obj.count > 0:
                obj.count = obj.count-1
            else:
                obj.count=0
            obj.now_spot=path[obj.count]
            obj.next_spot=path[obj.count+1]
            obj.save()
            userpath = UserPath.objects.filter(pk=pk)
            for userpath in userpath:
                object = {
                    "path":userpath.path,
                    "nowspot":userpath.now_spot+1,
                    "nextspot":userpath.next_spot+1,
                    "pk":userpath.pk
                    }
            nowsp=userpath.now_spot+1
            nextsp=userpath.next_spot+1
            now_spot=OmuraMuseum.objects.get(id=nowsp)
            next_spot=OmuraMuseum.objects.get(id=nextsp)
            spot={"nowspot_name":now_spot.name,
                "nextspot_name":next_spot.name,
                }
            object.update(spot)
            pt=userpath.path.split(',')
            graph = Plot_graph(userpath.now_spot,userpath.next_spot,pt)
            object['graph']=graph
            return render(request, "QAmuseum/MuseumPath.html",{'object':object,'pk':pk})
    
    userpath=UserPath.objects.get(pk=pk)
    path = userpath.path.split(',')


    nsp = userpath.now_spot
    spot = OmuraMuseum.objects.filter(id=nsp+1)
    for spot in spot:
        object_spot={"name":spot.name,
                     "explain":spot.exp,
                    "img":spot.image,
                     "pk":userpath.pk}
    value={"display_evaluation":0}
    form={"form":EvaluationForm(value)}
    object_spot.update(form) 
    return render(request,"QAmuseum/Arrive.html",object_spot)
            

#次の経路表示画面
def NextPath(request):
    return render(request,"QAmuseum/NextPath.html")

#終了画面
def End(request):
    return render(request,"QAmuseum/End.html")

def ReCalculate(request,pk):
    return render(request,"QAmuseum/ReCalculate.html",{"pk":pk})

def recalc(request,pk):
    if request.method =='GET':
        #data=calctest()
        userpath=UserPath.objects.get(pk=pk)
        re_time=userpath.time-(userpath.now_time-userpath.start_time)/60
        path_data = calculatepath(userpath.time,userpath.speed,userpath.browse)
        data=[]
        data.append(path_data)
        pd=str(path_data)
        pa = pd.replace(']','')
        path = pa.replace('[','')
        userpath.path = path
        userpath.now_spot=path_data[0]
        userpath.next_spot=path_data[1]
        userpath.count=0
        userpath.save()
        return HttpResponse(data)

def predict(path,now_spot,tm,ts):
    predict_time=0
    #move_time=time_for_move_calc(tm)
    stay_time=time_stay(ts)
    N,mt,ts,sat = data()
    
    for i in range(len(path)-1):
            predict_time=predict_time+tm*mt[int(path[i])][int(path[i+1])]/60
            predict_time=predict_time+stay_time[int(path[i])]
            if int(now_spot)==int(path[i+1]):
                return predict_time
            
            
            
    return predict_time


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
    plt.scatter(spot_x,spot_y,marker=".")
    for i in range(len(path)-1):
        plt.annotate("",xy=[spot_x[int(path[i+1])],spot_y[int(path[i+1])]],xytext=[spot_x[int(path[i])],spot_y[int(path[i])]],arrowprops=dict(shrink=0, width=1, headwidth=8, 
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
    graph = Output_graph()
    return graph

def Plot_graph(now_spot,next_spot,path):
    spot_x,spot_y=graph_data()
    waypoint=Waypoint(now_spot,next_spot)
    plt.switch_backend("AGG")
    plt.figure(figsize=(9,7),dpi=100)
    plt.ylim(-720,0)
    plt.xlim(0,940)
    plt.scatter(spot_x,spot_y,marker=".")
    
    """plt.annotate("",xy=[spot_x[next_spot],spot_y[next_spot]],xytext=[spot_x[now_spot],spot_y[now_spot]],arrowprops=dict(shrink=0, width=1, headwidth=8, 
                                headlength=10, connectionstyle='arc3',
                                facecolor='red', edgecolor='red'))"""
   
    for i in range(len(waypoint)-1):
        plt.annotate("",xy=[spot_x[waypoint[i+1]],spot_y[waypoint[i+1]]],xytext=[spot_x[waypoint[i]],spot_y[waypoint[i]]],arrowprops=dict(shrink=0, width=1, headwidth=8, 
                                headlength=10, connectionstyle='arc3',
                                facecolor='red', edgecolor='red'))
        
    plot_x=[]
    plot_y=[]
    for i in path:
        plot_x.append(spot_x[int(i)])
        plot_y.append(spot_y[int(i)])
    #plt.plot(plot_x,plot_y,color="k")
    """labels=[num for num in range(len(spot_x))]
    for i in labels:
        plt.text(spot_x[i],spot_y[i],i)"""
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)
    plt.gca().spines['left'].set_visible(False)
    plt.tick_params(labelbottom=False, labelleft=False, labelright=False, labeltop=False, bottom=False, left=False, right=False, top=False)
    graph = Output_graph()
    return graph

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
            waypoint.append(29)
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
        if next_spot==15:
            waypoint.append(29)

    if now_spot==18:
        if next_spot<=10:
            waypoint.append(27)
        if next_spot>=11 and next_spot<=15:
            waypoint.append(26)
            if next_spot==13:
                waypoint.append(25)
                waypoint.append(24)
            if next_spot==15:
                waypoint.append(29)

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
            waypoint.append(29)

    waypoint.append(next_spot)
    return waypoint

def graph_data():
    x=[570,#1
       480,#2
       440,#3
       320,#4
       230,#5
       230,#6
       210,#7
       370,#8
       330,#9
       290,#10
       240,#11
       300,#12
       320,#13
       430,#14
       520,#15
       560,#16
       650,#17
       720,#18
       720,#19
       670,#20

       290,#21
       290,#22
       430,#23
       520,#24
       430,#25
       520,#26
       670,#27
       670,#28
       290,#29
       560,#30
       370,#31
       ]
    y=[-560,#1
       -560,#2
       -620,#3
       -620,#4
       -620,#5
       -550,#6
       -440,#7
       -530,#8
       -490,#9
       -390,#10
       -330,#11
       -240,#12
       -160,#13
       -340,#14
       -340,#15
       -500,#16
       -160,#17
       -280,#18
       -520,#19
       -590,#20

       -560,#21
       -280,#22
       -400,#23
       -400,#24
       -280,#25
       -280,#26
       -320,#27
       -560,#28
       -490,#29
       -320,#30
       -560,#31
    ]
    return x,y

@shared_task
def back_calc(T,speed_move,speed_watch,visit_spot,now_spot):
    time.sleep(5)
    print("非同期処理")
    path=recalculate(T,speed_move,speed_watch,visit_spot,now_spot)
    print(path)
    if len(path) < 2:
        path=[]
    pd=str(path)
    pa = pd.replace(']','')
    path = pa.replace('[','')
    return path



"""mid_time=time.time()
    userpath.now_time=mid_time
    predict_time=predict(path,userpath.now_spot,userpath.speed,userpath.browse)
    userpath.predict_time=predict_time
    userpath.save()
    if int(predict_time) != int(userpath.now_time-userpath.start_time)/60:
    #if predict_time>0:
        print(predict_time*60)
        print(userpath.now_time-userpath.start_time)
        print("time over")
        T=userpath.time-(userpath.now_time-userpath.start_time)/60
        speed_move=userpath.speed
        speed_watch=userpath.browse
        temp_path=userpath.visit_path.split(',')
        visit_spot=[]
        for i in temp_path:
            visit_spot.append(int(i))
        now_spot=userpath.now_spot
        path=recalculate(T,speed_move,speed_watch,visit_spot,now_spot)
        if len(path) >2:
            userpath.next_spot=path[1]
            print(path)
            pd=str(path)
            pa = pd.replace(']','')
            path = pa.replace('[','')
            userpath.path=path
            userpath.count=0
            userpath.start_time=time.time()
            userpath.save()
        else:
            userpath.next_spot=0
            now_spot=userpath.now_spot
            path=[]
            path.append(now_spot)
            path.append(0)
            pd=str(path)
            pa = pd.replace(']','')
            path = pa.replace('[','')
            userpath.path=path
            userpath.count=0
            #userpath.save()"""