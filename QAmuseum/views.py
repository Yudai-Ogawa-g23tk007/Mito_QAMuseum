from typing import Any, Dict
from django.forms.models import BaseModelForm
from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth.models import User
from .models import UserPath,Museum,MuseumEvaluation
from .pathcalculate import calculatepath,recalculate,data,TSPCalculate,GoalTime
from .museumdata import time_stay
from QAmuseum.views_modules import module
from django.views.generic import CreateView
from .forms import parameterform,EvaluationForm,parameterEnform,LoginForm,EvaluationEnForm,TSPParameterEnForm,TSPParameterForm
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from PIL import Image
import time
from celery import shared_task
from celery.result import AsyncResult
from django_celery_results.models import TaskResult
from django import forms
from django.urls import reverse
from django.conf import settings
import os

#美術館選択画面
class Name(CreateView):
    template_name="QAmuseum/Name.html"
    #form_class=NameForm
    model=UserPath
    fields=['name','password']
    def get_form(self,form_class=None):
        form = super().get_form(form_class)
        form.fields['name'].widget.attrs['placeholder'] = '名前を入力'
        form.fields['name'].widget.attrs['class']='large-textbox'
        form.fields['name'].label =''
        form.fields['password'].widget= forms.PasswordInput()
        form.fields['password'].widget.attrs['placeholder'] = 'パスワード(数字4桁)'
        form.fields['password'].widget.attrs['class']='large-textbox'
        form.fields['password'].label=''
        return form
    def get_success_url(self):
        username=self.request.POST.get('name')
        password = self.request.POST.get('password')
        pk=self.object.pk
        #print(type(username) is str)
        print(pk)
        return reverse("ParameterSelect",kwargs={'pk':pk})
class Name_En(CreateView):
    template_name="QAmuseum/Name_En.html"
    #form_class=NameForm
    model=UserPath
    fields=['name','password']
    def get_form(self,form_class=None):
        form = super().get_form(form_class)
        form.fields['name'].widget.attrs['placeholder'] = 'Name'
        form.fields['name'].widget.attrs['class']='large-textbox'
        form.fields['name'].label =''
        form.fields['password'].widget= forms.PasswordInput()
        form.fields['password'].widget.attrs['placeholder'] = 'Enter a 4-digit number.'
        form.fields['password'].widget.attrs['class']='large-textbox'
        form.fields['password'].label=''
        return form
    def get_success_url(self):
        username=self.request.POST.get('name')
        password = self.request.POST.get('password')
        pk=self.object.pk
        #print(type(username) is str)
        print(pk)
        return reverse("ParameterSelectEn",kwargs={'pk':pk})

def Agree(request):

    return render(request,"QAmuseum/Agree.html")

def AgreeEn(request):
    return render(request,"QAmuseum/Agree_En.html")

def Login(request):
    form = LoginForm()
    ctx = {"form"}
    if request.POST:
        form = LoginForm(request.POST)
        if form.is_valid():
            login_name=form.cleaned_data["name"]
            login_password=form.cleaned_data["password"]
            user = UserPath.objects.get(name=login_name,password=login_password)
            pk=user.pk
            url=user.last_page
            return HttpResponseRedirect(url)
    return render(request,"QAmuseum/login.html",{'form':form})

def Login_En(request):
    form = LoginForm()
    if request.POST:
        form = LoginForm(request.POST)
        if form.is_valid():
            login_name=form.cleaned_data["name"]
            login_password=form.cleaned_data["password"]
            user = UserPath.objects.get(name=login_name,password=login_password)
            pk=user.pk
            url=user.last_page
            return HttpResponseRedirect(url)
    return render(request,"QAmuseum/login_en.html",{'form':form})

def ParameterSelect(request,pk):
    obj=UserPath.objects.get(pk=pk)
    obj.last_page=request.build_absolute_uri()
    obj.calculate_count=0
    obj.save()
    if request.method == 'POST':
        select_option=request.POST.get('radio_option')
        if select_option == 'option1':
            return HttpResponseRedirect(reverse('TSPParameter',args=[pk]))
        if select_option == 'option2':
            return HttpResponseRedirect(reverse('Parameter',args=[pk]))
    return render(request,"QAmuseum/ParamSelect.html",{'pk':pk})

def ParameterSelectEn(request,pk):
    obj=UserPath.objects.get(pk=pk)
    obj.last_page=request.build_absolute_uri()
    obj.calculate_count=0
    obj.save()
    if request.method == 'POST':
        select_option = request.POST.get('radio_option')
        if select_option == 'option1':
            return HttpResponseRedirect(reverse('TSPParameterEn',args=[pk]))
        if select_option == 'option2':
            return HttpResponseRedirect(reverse('Parameter_En',args=[pk]))
    return render(request,"QAmuseum/ParamSelect_En.html",{'pk':pk})

def CalcPathWait(request,pk):
    
    obj  = UserPath.objects.get(pk=pk)
    mustvisit=obj.must_spot.split(',')
    print(mustvisit)
    task = CalcPath.delay(obj.time,obj.speed,obj.browse,mustvisit)
    obj.caluculate_back = task
    obj.save()
    return redirect('AllMuseumPath',pk)

def CalcPathWaitEn(request,pk):
    
    obj  = UserPath.objects.get(pk=pk)
    mustvisit=obj.must_spot.split(',')
    task = CalcPath.delay(obj.time,obj.speed,obj.browse,mustvisit)
    obj.caluculate_back = task
    obj.save()
    return redirect('AllMuseumPathEn',pk)

def TSPParameter(request,pk):
    obj=UserPath.objects.get(pk=pk)
    obj.last_page=request.build_absolute_uri()
    obj.save()
    initial_values={"speed":obj.speed,"browse":obj.browse}
    form = TSPParameterForm(initial_values)
    ctx={"form":form,'pk':pk}
    if request.method == 'POST':
        form = TSPParameterForm(request.POST)
        if form.is_valid():
            speed = form.cleaned_data["speed"]
            browse=form.cleaned_data["browse"]
            obj.speed=speed
            obj.browse=browse
            obj.count_time=0
            obj.calc_bool=False
            obj.save()
            return redirect('TSPCalc',pk)
    return render(request,"QAmuseum/TSPParameter.html",ctx)


def TSPParameterEn(request,pk):
    obj=UserPath.objects.get(pk=pk)
    obj.last_page=request.build_absolute_uri()
    obj.save()
    initial_values={"speed":obj.speed,"browse":obj.browse}
    form = TSPParameterEnForm(initial_values)
    ctx={"form":form,'pk':pk}
    if request.method == 'POST':
        form = TSPParameterForm(request.POST)
        if form.is_valid():
            speed = form.cleaned_data["speed"]
            browse=form.cleaned_data["browse"]
            obj.speed=speed
            obj.browse=browse
            obj.count_time=0
            obj.calc_bool=False
            obj.save()
            return redirect('TSPCalcEn',pk)
    return render(request,"QAmuseum/TSPParameterEn.html",ctx)



def TSPCalc(request,pk):
    task = test_calc.delay()
    obj  = UserPath.objects.get(pk=pk)
    obj.caluculate_back = task
    obj.save()
    return redirect('TSPPathShow',pk)

def TSPCalcEn(request,pk):
    task = test_calc.delay()
    obj  = UserPath.objects.get(pk=pk)
    obj.caluculate_back = task
    obj.save()
    return redirect('TSPPathShowEn',pk)

def Reload(request):
    task = reload.delay()
    return redirect('ReloadResult')

def ReloadResult(request):
    return render(request,"QAmuseum/Reload.html")

def TSPPathShow(request,pk):
    obj=UserPath.objects.get(pk=pk)
    obj.last_page=request.build_absolute_uri()
    obj.save()
    task = AsyncResult(obj.caluculate_back)
    if task.ready():
        path = task.get()
        obj.path=path
        pt = path.split(',')
        obj.now_spot=int(pt[0])
        obj.next_spot=int(pt[1])
        obj.calculate_count+=1
        goaltime=GoalTime(pt,obj.speed,obj.browse)
        obj.goal_time=int(goaltime)
        obj.count=0
        obj.start_time=time.time()
        obj.save()
        graph = All_Plot_graph(pt)#経路描画
        ctx={'pk':pk,'path':path,"graph":graph,"goaltime":obj.goal_time}
        return render(request,"QAmuseum/TSPPathShow.html",ctx)
    return render(request,"QAmuseum/TSPCalc.html",{'pk':pk})

def TSPPathShowEn(request,pk):
    obj=UserPath.objects.get(pk=pk)
    obj.last_page=request.build_absolute_uri()
    obj.save()
    task = AsyncResult(obj.caluculate_back)
    if task.ready():
        path = task.get()
        obj.path=path
        pt = path.split(',')
        obj.now_spot=int(pt[0])
        obj.next_spot=int(pt[1])
        obj.calculate_count+=1
        goaltime=GoalTime(pt,obj.speed,obj.browse)
        obj.goal_time=int(goaltime)
        obj.count=0
        obj.start_time=time.time()
        obj.save()
        graph = All_Plot_graph(pt)#経路描画
        ctx={'pk':pk,'path':path,"graph":graph,"goaltime":obj.goal_time}
        return render(request,"QAmuseum/TSPPathShow_En.html",ctx)
    return render(request,"QAmuseum/TSPCalc_En.html",{'pk':pk})

def TSPNextPath(request,pk):
    obj=UserPath.objects.get(pk=pk)
    obj.last_page=request.build_absolute_uri()
    obj.save()
    object = {
        "path":obj.path,
        "nowspot":obj.now_spot,
        "nextspot":obj.next_spot,
        "pk":obj.pk
    }
    nows=Museum.objects.get(id=obj.now_spot)
    nexts=Museum.objects.get(id=obj.next_spot)
    nextmap=Museum.objects.get(id=obj.next_spot)
    spot={"nowspot_name":nows.name,
          "nextspot_name":nexts.name,
          "mapimg":nextmap.map_image,
          "nextimg":nexts.image,
          }
    object.update(spot)
    pt=obj.path.split(',')
    graph = Plot_graph(obj.now_spot-1,obj.next_spot-1,pt)
    object['graph']=graph
    return render(request,"QAmuseum/TSPNextPath.html",object)

def TSPNextPathEn(request,pk):
    obj=UserPath.objects.get(pk=pk)
    obj.last_page=request.build_absolute_uri()
    obj.save()
    object = {
        "path":obj.path,
        "nowspot":obj.now_spot,
        "nextspot":obj.next_spot,
        "pk":obj.pk
    }
    nows=Museum.objects.get(id=obj.now_spot)
    nexts=Museum.objects.get(id=obj.next_spot)
    nextmap=Museum.objects.get(id=obj.next_spot)
    spot={"nowspot_name":nows.en_name,
          "nextspot_name":nexts.en_name,
          "nextimg":nexts.image,
          "mapimg":nextmap.map_image,
          }
    object.update(spot)
    pt=obj.path.split(',')
    graph = Plot_graph(obj.now_spot-1,obj.next_spot-1,pt)
    object['graph']=graph
    return render(request,"QAmuseum/TSPNextPath_En.html",object)

def TSPSpot(request,pk):
    obj=UserPath.objects.get(pk=pk)
    obj.last_page=request.build_absolute_uri()
    obj.save()
    nsp = obj.now_spot
    spot = Museum.objects.get(id=nsp+1)
    object_spot={'name':spot.name,'explain':spot.exp,
                "img":spot.image,
                "pk":obj.pk}
    value={"display_evaluation":0}
    form={"form":EvaluationForm(value)}
    object_spot.update(form)
    return render(request,"QAmuseum/TSPSpot.html",object_spot)

def TSPSpotEn(request,pk):
    obj=UserPath.objects.get(pk=pk)
    obj.last_page=request.build_absolute_uri()
    obj.save()
    nsp = obj.now_spot
    spot = Museum.objects.get(id=nsp+1)
    object_spot={'name':spot.en_name,'explain':spot.en_exp,
                "img":spot.image,
                "pk":obj.pk}
    value={"display_evaluation":0}
    form={"form":EvaluationForm(value)}
    object_spot.update(form)
    return render(request,"QAmuseum/TSPSpot_En.html",object_spot)



#パラメータ設定画面
def Parameter(request,pk):
    print(type(pk) is str)
    obj=UserPath.objects.get(pk=pk)
    obj.last_page=request.build_absolute_uri()
    obj.save()
    initial_values={"time":obj.time,"speed":obj.speed,"browse":obj.browse,"demand":0}
    form = parameterform(initial_values)
    ctx={"form":form,'pk':pk}
    if request.method=='POST':
        form=parameterform(request.POST)
        dynamic_demand_fields = [field for field in request.POST if field.startswith('demand_')]
        for field_name in dynamic_demand_fields:
            form.fields[field_name] = forms.ChoiceField(
                widget=forms.Select(attrs={'label_type': 'f'}),
                label="Place to see",
                choices=form.fields['demand'].choices,
                required=False
            )
        if form.is_valid():
            time = form.cleaned_data["time"]
            speed = form.cleaned_data["speed"]
            browse=form.cleaned_data["browse"]
            demand=[0]
            demand.append(int(form.cleaned_data["demand"]))
            for form.field_name in dynamic_demand_fields:
                demand.append(int(form.cleaned_data[field_name]))
            print(form.cleaned_data)
            obj.time=time
            obj.speed=speed
            obj.browse=browse
            obj.count_time=0
            obj.calc_bool=False
            
            print(demand)
            de=str(demand)
            dem=de.replace(']','')
            obj.must_spot=dem.replace('[','')
            obj.save()
            return redirect('CalcPathWait',pk)
        
    return render(request, "QAmuseum/Parameter.html",ctx)

def Parameter_En(request,pk):
    print(type(pk) is str)
    obj=UserPath.objects.get(pk=pk)
    obj.last_page=request.build_absolute_uri()
    obj.save()
    initial_values={"time":obj.time,"speed":obj.speed,"browse":obj.browse,"demand":'0'}
    form = parameterEnform(initial_values)
    ctx={"form":form,'pk':pk}
    if request.POST:
        form=parameterform(request.POST)
        dynamic_demand_fields = [field for field in request.POST if field.startswith('demand_')]
        for field_name in dynamic_demand_fields:
            form.fields[field_name] = forms.ChoiceField(
                widget=forms.Select(attrs={'label_type': 'f'}),
                label="Place to see",
                choices=form.fields['demand'].choices,
                required=False
            )
        if form.is_valid():
            time = form.cleaned_data["time"]
            speed = form.cleaned_data["speed"]
            browse=form.cleaned_data["browse"]
            demand=[]
            demand.append(int(form.cleaned_data["demand"]))
            for form.field_name in dynamic_demand_fields:
                demand.append(int(form.cleaned_data[field_name]))
            obj.time=time
            obj.speed=speed
            obj.browse=browse
            obj.count_time=0
            obj.calc_bool=False
            de=str(demand)
            dem=de.replace(']','')
            obj.must_spot=dem.replace('[','')
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
            return HttpResponseRedirect(reverse('CalcPathWaitEn',args=[pk]))
    return render(request, "QAmuseum/Parameter_En.html",ctx)

def CalculatePath(request,pk):
    object=UserPath.objects.get(pk=pk)
    object.last_page=request.build_absolute_uri()
    object.save()
    return render(request,"QAmuseum/CalculatePath.html",{'object':object,'pk':pk})

#計算実行
def caluculate(request,pk):
    if request.method =='GET':
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
    obj=UserPath.objects.get(pk=pk)
    obj.last_page=request.build_absolute_uri()
    obj.save()
    task = AsyncResult(obj.caluculate_back)
    if task.ready():
        path = task.get()
        pd = str(path)
        pa= pd.replace(']','')
        path= pa.replace('[','')
        obj.path=path
        print(path)
        pt = path.split(',')
        goaltime=GoalTime(pt,obj.speed,obj.browse)
        obj.now_spot=0
        obj.next_spot=int(pt[1])
        visit_path=[0]
        pd=str(visit_path)
        pa = pd.replace(']','')
        visit_path = pa.replace('[','')
        obj.visit_path=visit_path
        obj.count=0
        obj.goal_time=goaltime
        obj.calc_bool=False
        obj.calculate_count=1
        obj.save()
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
    return render(request,"QAmuseum/CalcPathWait.html",{'pk':pk})

def AllMuseumEn(request,pk):
    obj=UserPath.objects.get(pk=pk)
    obj.last_page=request.build_absolute_uri()
    obj.save()
    task = AsyncResult(obj.caluculate_back)
    if task.ready():
        path = task.get()
        
        pd = str(path)
        pa= pd.replace(']','')
        path= pa.replace('[','')

        obj.path=path
        print(path)
        pt = path.split(',')
        goaltime=GoalTime(pt,obj.speed,obj.browse)
        obj.now_spot=0
        obj.next_spot=int(pt[1])
        visit_path=[0]
        pd=str(visit_path)
        pa = pd.replace(']','')
        visit_path = pa.replace('[','')
        obj.visit_path=visit_path
        obj.count=0
        obj.goal_time=goaltime
        obj.calc_bool=False
        obj.calculate_count=1
        obj.save()
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
        return render(request,"QAmuseum/AllMuseumPath_En.html",object)
    return render(request,"QAmuseum/CalcPathWait_En.html",{'pk':pk})


#経路表示画面
def MuseumPath(request,pk):
    obj=UserPath.objects.get(pk=pk)
    obj.last_page=request.build_absolute_uri()
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
                    userpath.calculate_count = userpath.calculate_count+1
                    userpath.count_time=userpath.count_time+time.time()-userpath.start_time
                    userpath.start_time=time.time()
                    userpath.calculate_count =userpath.calculate_count+1
                    userpath.calc_bool=False
                    userpath.save()
        if userpath.now_spot==0:
            start_time=time.time()
            userpath.start_time=start_time
            userpath.save()
        nex = Museum.objects.get(pk=userpath.next_spot+1)
        object = {
            "path":userpath.path,
            "nowspot":userpath.now_spot+1,
            "nextspot":userpath.next_spot+1,
            "pk":userpath.pk,
            "map_img":nex.map_image,
            "img":nex.image,
            }
    nowsp=userpath.now_spot+1
    nextsp=userpath.next_spot+1
    now_spot=Museum.objects.get(id=nowsp)
    next_spot=Museum.objects.get(id=nextsp)
    spot={"nowspot_name":now_spot.name,
          "nextspot_name":next_spot.name}
    object.update(spot)
    pt=userpath.path.split(',')
    graph = Plot_graph(userpath.now_spot,userpath.next_spot,pt)
    object['graph']=graph
    return render(request, "QAmuseum/MuseumPath.html",object)

def MuseumPathEn(request,pk):
    obj=UserPath.objects.get(pk=pk)
    obj.last_page=request.build_absolute_uri()
    obj.save()
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
                    userpath.calculate_count = userpath.calculate_count+1
                    userpath.count_time=userpath.count_time+time.time()-userpath.start_time
                    userpath.start_time=time.time()
                    userpath.calculate_count =userpath.calculate_count+1
                    userpath.calc_bool=False
                    userpath.save()
        if userpath.now_spot==0:
            start_time=time.time()
            userpath.start_time=start_time
            userpath.save()
        nex = Museum.objects.get(pk=userpath.next_spot+1)
        object = {
            "path":userpath.path,
            "nowspot":userpath.now_spot+1,
            "nextspot":userpath.next_spot+1,
            "pk":userpath.pk,
            "img":nex.image,
            "map_img":nex.map_image
            }
    nowsp=userpath.now_spot+1
    nextsp=userpath.next_spot+1
    now_spot=Museum.objects.get(id=nowsp)
    next_spot=Museum.objects.get(id=nextsp)
    spot={"nowspot_name":now_spot.en_name,
          "nextspot_name":next_spot.en_name}
    object.update(spot)
    pt=userpath.path.split(',')
    graph = Plot_graph(userpath.now_spot,userpath.next_spot,pt)
    object['graph']=graph
    
    return render(request, "QAmuseum/MuseumPath_En.html",object)

def Evaluation(request,pk):
    if request.method=="POST":
        form = EvaluationForm(request.POST)
        if form.is_valid():
            ev=form.cleaned_data["display_evaluation"]
            if int(ev)==0:
                print(ev)
                #return redirect("Arrive",pk)
            else:
                userpath=UserPath.objects.get(pk=pk)
                spot=Museum.objects.get(id=userpath.now_spot+1)
                evaluation=MuseumEvaluation.objects.create(display_id=userpath.now_spot,display_name=spot.name,display_evaluation=ev,user_name=userpath.name,display_time=time.time()-userpath.now_time)
    else:
        form=EvaluationForm()
    return redirect("MuseumPath",pk)

def EvaluationEn(request,pk):
    if request.method=="POST":
        form = EvaluationForm(request.POST)
        if form.is_valid():
            ev=form.cleaned_data["display_evaluation"]
            if int(ev)==0:
                print(ev)
                #return redirect("ArriveEn",pk)
            else:
                userpath=UserPath.objects.get(pk=pk)
                spot=Museum.objects.get(id=userpath.now_spot+1)
                evaluation=MuseumEvaluation.objects.create(display_id=userpath.now_spot,display_name=spot.name,display_evaluation=ev,user_name=userpath.name,display_time=time.time()-userpath.now_time)
    else:
        form=EvaluationForm()
    return redirect("MuseumPathEn",pk)

def EvaluationTSP(request,pk):
    if request.method=="POST":
        form = EvaluationForm(request.POST)
        if form.is_valid():
            ev=form.cleaned_data["display_evaluation"]
            if int(ev)==0:
                print(ev)
                
            else:
                userpath=UserPath.objects.get(pk=pk)
                spot=Museum.objects.get(id=userpath.now_spot+1)
                evaluation=MuseumEvaluation.objects.create(display_id=userpath.now_spot,display_name=spot.name,display_evaluation=ev,user_name=userpath.name,display_time=time.time()-userpath.now_time)
    else:
        form=EvaluationForm()
    UpdateUserPath(pk)
    obj=UserPath.objects.get(pk=pk)
    if obj.next_spot == 0:
        obj.count_time=time.time()-obj.start_time
        obj.save()
        return redirect("End",pk)
    return redirect("TSPNextPath",pk)

def EvaluationTSPEn(request,pk):
    if request.method=="POST":
        form = EvaluationForm(request.POST)
        if form.is_valid():
            ev=form.cleaned_data["display_evaluation"]
            if int(ev)==0:
                print(ev)
                
            else:
                userpath=UserPath.objects.get(pk=pk)
                spot=Museum.objects.get(id=userpath.now_spot+1)
                evaluation=MuseumEvaluation.objects.create(display_id=userpath.now_spot,display_name=spot.name,display_evaluation=ev,user_name=userpath.name,display_time=time.time()-userpath.now_time)
    else:
        form=EvaluationForm()
    UpdateUserPath(pk)
    obj=UserPath.objects.get(pk=pk)
    if obj.next_spot == 0:
        obj.count_time=time.time()-obj.start_time
        obj.save()
        return redirect("EndEn",pk)
    return redirect("TSPNextPathEn",pk)

def UpdateUserPath(pk):
    obj=UserPath.objects.get(pk=pk)
    path=obj.path.split(',')
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
        obj.count = count+1
        obj.now_spot=path[obj.count]
        obj.next_spot=path[obj.count+1]
        obj.save()


def Arrive(request,pk):
    obj=UserPath.objects.get(pk=pk)
    obj.last_page=request.build_absolute_uri()
    obj.save()
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
                    
            else:
                obj.count_time=time.time()-obj.start_time
                obj.save()
                return redirect("End",pk)
        
    userpath=UserPath.objects.get(pk=pk)
    path = userpath.path.split(',')


    nsp = userpath.now_spot
    spot = Museum.objects.filter(id=nsp+1)
    for spot in spot:
        object_spot={"name":spot.name,
                     "explain":spot.exp,
                    "img":spot.image,
                     "pk":userpath.pk}
    value={"display_evaluation":0}
    form={"form":EvaluationForm(value)}
    object_spot.update(form) 
    return render(request,"QAmuseum/Arrive.html",object_spot)


def ArriveEn(request,pk):
    obj=UserPath.objects.get(pk=pk)
    obj.last_page=request.build_absolute_uri()
    obj.save()
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
            else:
                obj.count_time=time.time()-obj.start_time
                obj.save()
                return redirect("EndEn",pk)
        
    userpath=UserPath.objects.get(pk=pk)
    path = userpath.path.split(',')


    nsp = userpath.now_spot
    spot = Museum.objects.filter(id=nsp+1)
    for spot in spot:
        object_spot={"name":spot.en_name,
                     "explain":spot.en_exp,
                    "img":spot.image,
                     "pk":userpath.pk}
    value={"display_evaluation":0}
    form={"form":EvaluationEnForm(value)}
    object_spot.update(form) 
    return render(request,"QAmuseum/Arrive_En.html",object_spot)

def Enter(request,pk):
    enter = Museum.objects.get(id=1)
    object={'pk':pk,
            "name":enter.name,
            "explain":enter.exp,
            "img":enter.image}
    return render(request,"QAmuseum/Enter.html",object)

def EnterEn(request,pk):
    enter = Museum.objects.get(id=1)
    object={'pk':pk,
            "name":enter.en_name,
            "explain":enter.en_exp,
            "img":enter.image}
    return render(request,"QAmuseum/EnterEn.html",object)

def BackSave(pk):
    obj= UserPath.objects.get(pk=pk)
    next=obj.now_spot
    visit=obj.visit_path.split(',')
    if len(visit)==0:
        now=0
    else:
        now=int(visit[obj.count-1])
        obj.now_spot=now
        obj.next_spot=next
        temp=[]
        for i in range(obj.count):
            temp.append(int(visit[i]))
            print(temp)
        pd=str(temp)
        pa = pd.replace(']','')
        visit = pa.replace('[','')
        obj.visit_path=visit
        obj.count -=1
        obj.save()

def BackPath(pk):
    obj= UserPath.objects.get(pk=pk)
    visit=obj.visit_path.split(',')
    if len(visit)<=1:
        er=True
        temp=[0]
        pd=str(temp)
        pa = pd.replace(']','')
        visit = pa.replace('[','')
        obj.visit_path=visit
        obj.count =0
        obj.save()
    else:
        temp=[]
        for i in range(obj.count-1):
            temp.append(int(visit[i]))
            print(temp)
        obj.next_spot=obj.now_spot
        obj.now_spot=int(visit[obj.count-2])
        
        pd=str(temp)
        pa = pd.replace(']','')
        visit = pa.replace('[','')
        obj.visit_path=visit
        obj.count -=1
        
        obj.save()
        er=False
    return er

def BacktoArrive(request,pk):
    obj= UserPath.objects.get(pk=pk)
    if obj.now_spot!=0:
        er=BackPath(pk)
        if er==False:
            return redirect("Arrive",pk)
        else:
            return redirect("AllMuseumPath",pk)
    else:
        return redirect("AllMuseumPath",pk)

def BacktoPath(request,pk):
    obj= UserPath.objects.get(pk=pk)
    if obj.now_spot!=0:
        er=BackPath(pk)
        if er==False:
            return redirect("MuseumPath",pk)
        else:
            return redirect("AllMuseumPath",pk)
    else:
        return redirect("AllMuseumPath",pk)
    
def BacktoArriveEn(request,pk):
    obj= UserPath.objects.get(pk=pk)
    if obj.now_spot!=0:
        er=BackPath(pk)
        if er==False:
            return redirect("ArriveEn",pk)
        else:
            return redirect("AllMuseumPathEn",pk)
    else:
        return redirect("AllMuseumPathEn",pk)
    
def BacktoPathEn(request,pk):
    obj= UserPath.objects.get(pk=pk)
    if obj.now_spot!=0:
        er=BackPath(pk)
        if er==False:
            return redirect("MuseumPathEn",pk)
        else:
            return redirect("AllMuseumPathEn",pk)
    else:
        return redirect("AllMuseumPathEn",pk)

def BacktoTSPSpot(request,pk):
    obj= UserPath.objects.get(pk=pk)
    if obj.now_spot!=0:
        er=BackPath(pk)
        if er==False:
            return redirect("TSPSpot",pk)
        else:
            return redirect("TSPPathShow",pk)
    else:
        return redirect("TSPPathShow",pk)
    
def BacktoTSPPath(request,pk):
    obj= UserPath.objects.get(pk=pk)
    if obj.now_spot!=0:
        er=BackPath(pk)
        if er==False:
            return redirect("TSPNextPath",pk)
        else:
            return redirect("TSPPathShow",pk)
    else:
        return redirect("TSPPathShow",pk)


def BacktoTSPSpotEn(request,pk):
    obj= UserPath.objects.get(pk=pk)
    if obj.now_spot!=0:
        er=BackPath(pk)
        if er==False:
            return redirect("TSPSpotEn",pk)
        else:
            return redirect("TSPPathShowEn",pk)
    else:
        return redirect("TSPPathShowEn",pk)

def BacktoTSPPathEn(request,pk):
    obj= UserPath.objects.get(pk=pk)
    if obj.now_spot!=0:
        er=BackPath(pk)
        if er==False:
            return redirect("TSPNextPathEn",pk)
        else:
            return redirect("TSPPathShowEn",pk)
    else:
        return redirect("TSPPathShowEn",pk)
#終了画面
def End(request,pk):
    obj=UserPath.objects.get(pk=pk)
    obj.last_page=request.build_absolute_uri()
    obj.save()
    obj = UserPath.objects.get(pk=pk)
    ctx={
        'pk':pk,
        'name':obj.name,
        'count':obj.calculate_count
    }
    return render(request,"QAmuseum/End.html",ctx)

def EndEn(request,pk):
    obj=UserPath.objects.get(pk=pk)
    obj.last_page=request.build_absolute_uri()
    obj.save()
    obj = UserPath.objects.get(pk=pk)
    ctx={
        'pk':pk,
        'name':obj.name,
        'count':obj.calculate_count
    }
    return render(request,"QAmuseum/End_En.html",ctx)

def Quantum(request,pk):
    obj=UserPath.objects.get(pk=pk)
    obj.last_page=request.build_absolute_uri()
    obj.save()
    ctx={'pk':pk}
    return render(request,"QAmuseum/Quantum.html",ctx)

def QuantumEn(request,pk):
    obj=UserPath.objects.get(pk=pk)
    obj.last_page=request.build_absolute_uri()
    obj.save()
    ctx={'pk':pk}
    return render(request,"QAmuseum/Quantum_En.html",ctx)


def ReCalculate(request,pk):
    return render(request,"QAmuseum/ReCalculate.html",{"pk":pk})

def recalc(request,pk):
    if request.method =='GET':
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
    """290,#21
       290,#22
       430,#23
       520,#24
       430,#25
       520,#26
       670,#27
       670,#28
       290,#29
       560,#30
       370,#31"""
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
    """-580,#21
       -300,#22
       -420,#23
       -420,#24
       -300,#25
       -300,#26
       -340,#27
       -580,#28
       -510,#29
       -340,#30
       -580,#31"""
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

@shared_task
def allview_calc():
    time.sleep(1)
    path=TSPCalculate()
    pd=str(path)
    pa = pd.replace(']','')
    path = pa.replace('[','')
    return path

@shared_task
def test_calc():
    time.sleep(1)
    t= int(time.time())
    if t%2==0:
        path=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,0]
    else:
        path=[0,19,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0]
    pd=str(path)
    pa = pd.replace(']','')
    path = pa.replace('[','')
    return path

@shared_task
def CalcPath(T,speed,browse,must_visit=None):
    path=[]
    print(must_visit)
    must_spot=[]
    for i in range(len(must_visit)):
        must_spot.append(int(must_visit[i]))
    while path==[]:
        path = calculatepath(T,speed,browse,must_spot)
        pd = str(path)
        pa= pd.replace(']','')
        path= pa.replace('[','')

    return path

@shared_task
def reload():
    time.sleep(1)
    og=2*3
    return og
