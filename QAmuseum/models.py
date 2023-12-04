from django.db import models
from django.contrib.auth.models import User
# Create your models here.

#大村記念館の各地点データ
class OmuraMuseum(models.Model):
    id=models.IntegerField(primary_key=True)
    name=models.CharField(max_length=100)
    satisfaction=models.FloatField()
    x=models.IntegerField()
    y=models.IntegerField()
    stay_time = models.FloatField()
    wait_time = models.IntegerField(default=0)
    exp = models.TextField()
    image=models.ImageField(upload_to='media/',blank=True)
    en_name=models.CharField(max_length=100,default="title")
    en_exp = models.TextField(default="text")
    #sum_score=models.IntegerField(default=0)


    def __str__(self):
        return self.name
    
class MuseumImage(models.Model):
    image=models.ImageField(upload_to='media/')
    id=models.IntegerField(primary_key=True)
    name=models.CharField(max_length=100,default="入口")

    def __str__(self):
        return self.name

#各ユーザーの設定や計算した経路
class UserPath(models.Model):
    name = models.CharField(max_length=20)#ユーザーネーム
    museumname = models.CharField(max_length=100,default="大村智記念学術館")#美術館名
    time = models.IntegerField(default=40)#設定巡回時間
    choice_speed=(
        (70,"速い"),
        (60,"普通"),
        (50,"遅い"),
        )
    speed = models.IntegerField(default=60,choices=choice_speed)#歩く速度
    choice_browse=(
        (2.0,"速い"),
        (1.5,"やや速い"),
        (1.0,"普通"),
        (0.75,"やや遅い"),
        (0.5,"遅い")
    )
    browse = models.FloatField(default=1.0,choices=choice_browse)#閲覧時間
    path = models.CharField(max_length=1000,default="0, 7, 16, 14, 2, 1, 3, 4, 5, 10, 8, 6, 0")#計算した経路
    visit_path=models.CharField(max_length=1000,default="0")
    now_spot = models.IntegerField(default=0)#現在地点
    next_spot = models.IntegerField(default=7)#次の地点
    predict_time = models.FloatField(default=0)#予想巡回時間
    start_time=models.FloatField(default=0)
    now_time = models.FloatField(default=0)#現在の巡回時間
    calculate_count = models.IntegerField(default=0)#計算回数
    count = models.IntegerField(default=0)
    #user = models.OneToOneField(User,on_delete=models.CASCADE,null=True,blank=True)
    goal_time=models.IntegerField(default=0)
    caluculate_back=models.CharField(default=0,max_length=100)
    calc_bool=models.BooleanField(default=False)
    count_time=models.FloatField(default=0)
    last_page=models.URLField(blank=True,default="")
    password = models.CharField(default="",max_length=10)
    def __str__(self):
        return self.name

class MuseumEvaluation(models.Model):
    display_id=models.IntegerField(default=0)
    display_name=models.CharField(max_length=100)
    choice_evaluation=(
        (5,"☆☆☆☆☆"),
        (4,"☆☆☆☆"),
        (3,"☆☆☆"),
        (2,"☆☆"),
        (1,"☆"),
        (0,"評価なし"),
    )
    display_evaluation=models.ImageField(default=0,choices=choice_evaluation)
    user_name=models.CharField(max_length=20)
    display_time=models.FloatField(default=0.0)
    def __str__(self):
        return self.user_name+":"+ self.display_name
