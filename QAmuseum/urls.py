from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns=[
    path("Start",views.Start,name="Start"),
    path("Name",views.Name.as_view(),name="Name"),
    path("Name_En",views.Name_En.as_view(),name="Name_En"),
    path("Parameter/<int:pk>/",views.Parameter,name="Parameter"),
    path("Parameter_En/<int:pk>/",views.Parameter_En,name="Parameter_En"),
    path("CalculatePath/<int:pk>/",views.CalculatePath,name="CalculatePath"),
    path("ajax/<int:pk>",views.caluculate,name="calculate"),
    path("ReCalculate/<int:pk>",views.ReCalculate,name="ReCalculate"),
    path("CalcPathWait/<int:pk>",views.CalcPathWait,name="CalcPathWait"),
    path("CalcPathWait_En/<int:pk>",views.CalcPathWaitEn,name="CalcPathWaitEn"),
    #path("ajax/recalc/<int:pk>",views.recalc,name="recalc"),
    path("AllMuseumPath/<int:pk>",views.AllMuseum,name="AllMuseumPath"),
    path("AllMuseumPath_En/<int:pk>",views.AllMuseumEn,name="AllMuseumPathEn"),
    path("MuseumPath/<int:pk>",views.MuseumPath,name="MuseumPath"),
    path("MuseumPath_En/<int:pk>",views.MuseumPathEn,name="MuseumPathEn"),
    path("Arrive/<int:pk>",views.Arrive,name="Arrive"),
    path("Arrive_En/<int:pk>",views.ArriveEn,name="ArriveEn"),
    path("Evaluation/<int:pk>",views.Evaluation,name="Evaluation"),
    path("Evaluation_En/<int:pk>",views.EvaluationEn,name="EvaluationEn"),
    path("NextPath/<int:pk>",views.NextPath,name="NextPath"),
    path("End/<int:pk>",views.End,name="End"),
    path("End_En/<int:pk>",views.EndEn,name="EndEn"),
    path("login",views.Login,name="login"),
    path("login_en",views.Login_En,name="loginEn"),
    path("Agree",views.Agree,name="Agree"),
    path("Terms",views.AgreeEn,name="AgreeEn"),
    path("ParameterSelect/<int:pk>/",views.ParameterSelect,name="ParameterSelect"),
    path("ParameterSelectEn/<int:pk>/",views.ParameterSelectEn,name="ParameterSelectEn"),
    path("TSPCalc/<int:pk>",views.TSPCalc,name="TSPCalc"),
    path("TSPCalcEn/<int:pk>",views.TSPCalcEn,name="TSPCalcEn"),
    path("TSPPathShow/<int:pk>",views.TSPPathShow,name="TSPPathShow"),
    path("TSPPathShowEn/<int:pk>",views.TSPPathShowEn,name="TSPPathShowEn"),
    path("TSPSpot/<int:pk>",views.TSPSpot,name="TSPSpot"),
    path("TSPSpotEn/<int:pk>",views.TSPSpotEn,name="TSPSpotEn"),
    path("EvaluationTSP/<int:pk>",views.EvaluationTSP,name="EvaluationTSP"),
    path("EvaluationTSPEn/<int:pk>",views.EvaluationTSPEn,name="EvaluationTSPEn"),
    path("TSPNextPath/<int:pk>",views.TSPNextPath,name="TSPNextPath"),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)