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
    #path("ajax/recalc/<int:pk>",views.recalc,name="recalc"),
    path("AllMuseumPath/<int:pk>",views.AllMuseum,name="AllMuseumPath"),
    path("MuseumPath/<int:pk>",views.MuseumPath,name="MuseumPath"),
    path("Arrive/<int:pk>",views.Arrive,name="Arrive"),
    path("Evaluation/<int:pk>",views.Evaluation,name="Evaluation"),
    path("NextPath/<int:pk>",views.NextPath,name="NextPath"),
    path("End",views.End,name="End"),
    path("login",views.Login,name="login"),
    path("login_en",views.Login_En,name="login_en"),
    path("Agree",views.Agree,name="Agree"),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)