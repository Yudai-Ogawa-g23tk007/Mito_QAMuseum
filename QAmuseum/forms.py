from django import forms
from django.core.validators import MinValueValidator
from .models import UserPath
from django.core.validators import MinLengthValidator

class parameterform(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = " "
    
    time = forms.IntegerField(label="巡回時間(分)",validators=[MinValueValidator(10)],widget=forms.TextInput(attrs={'label_type': 'check'}))
    choice_speed=(
        (70,"速い(70m/分)"),
        (60,"普通(60m/分)"),
        (50,"遅い(50m/分)"),
        )
    speed = forms.ChoiceField(label="歩く速度",choices=choice_speed)
    choice_browse=(
        (2.0,"速い"),
        (1.5,"やや速い"),
        (1.0,"普通"),
        (0.75,"やや遅い"),
        (0.5,"遅い")
    )
    browse = forms.ChoiceField(label="閲覧時間",choices=choice_browse)
    choice_demand = (
        (0,"なし"),
        (1,"メダル"),
        (2,"瑞宝重光章"),
        (3,"大村智年譜"),
        (4,"研究業績"),
        (5,"文化勲章"),
        (6,"称号記"),
        (7,"発酵生産学科写真プレート"),
        (8,"卒論"),
        (9,"博論"),
        (10,"化学式模型"),
        (11,"ビデオ上映"),
        (12,"ギャラリー"),
        (13,"トロフィー"),
        (14,"来学時の写真"),
        (15,"座右の銘"),
        (16,"昭和時代の写真"),
        (17,"徴典館"),
        (18,"さとっちゃん"),
        (19,"SDGs研究紹介"),
    )
    demand = forms.ChoiceField(label="絶対に見たい展示",choices=choice_demand,widget=forms.Select(attrs={'label_type': 'f'}),required=False,initial=0)

class parameterEnform(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = " "
    
    time = forms.IntegerField(label="Staying Time(min)",validators=[MinValueValidator(10)],widget=forms.TextInput(attrs={'label_type': 'check'}))
    choice_speed=(
        (70,"Fast(70m/m)"),
        (60,"Normal(60m/m)"),
        (50,"Slow(50m/m)"),
        )
    speed = forms.ChoiceField(label="Walking Speed",choices=choice_speed)
    choice_browse=(
        (2.0,"Very Fast"),
        (1.5,"Fast"),
        (1.0,"Normal"),
        (0.75,"Slow"),
        (0.5,"Very Slow")
    )
    browse = forms.ChoiceField(label="Appreciation Speed",choices=choice_browse)
    choice_demand = (
        (0,"None"),
        (1,"Medal"),
        (2,"Order of the Sacred Treasure"),
        (3,"Chronology"),
        (4,"Research Achievements"),
        (5,"Order of Culture"),
        (6,"Title Record"),
        (7,"Photo Plate"),
        (8,"Graduation Thesis"),
        (9,"Doctoral Dissertation"),
        (10,"Chemical Formula Model"),
        (11,"Video"),
        (12,"Gallery"),
        (13,"Trophy"),
        (14,"Photo at the time of arrival at the university"),
        (15,"Favorite Motto"),
        (16,"Showa Era Photo"),
        (17,"Kitenkan"),
        (18,"Special Exhibit Corner"),
        (19,"SDGs Research"),
    )
    demand = forms.ChoiceField(widget=forms.Select(attrs={'label_type': 'f'}),label="Place to see",choices=choice_demand,required=True)

class NameForm(forms.ModelForm):
    class Meta:
        model=UserPath
        fields=['name']
        labels={
            'name':'名前',
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': '名前'}),}
class EvaluationForm(forms.Form):
    choice_evaluation=(
        (5,"☆☆☆☆☆"),
        (4,"☆☆☆☆"),
        (3,"☆☆☆"),
        (2,"☆☆"),
        (1,"☆"),
        (0,"評価なし"),
    )
    display_evaluation=forms.ChoiceField(label="満足度",choices=choice_evaluation)

class EvaluationEnForm(forms.Form):
    choice_evaluation=(
        (5,"☆☆☆☆☆"),
        (4,"☆☆☆☆"),
        (3,"☆☆☆"),
        (2,"☆☆"),
        (1,"☆"),
        (0,"None"),
    )
    display_evaluation=forms.ChoiceField(label="満足度",choices=choice_evaluation)

class LoginForm(forms.Form):
    """def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = " "
        """
    name = forms.CharField(label='name',max_length=20)
    password = forms.CharField(label='password',widget=forms.PasswordInput(),max_length=4,validators=[MinLengthValidator(4)])


class TSPParameterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = " "
    choice_speed=(
        (70,"速い(70m/分)"),
        (60,"普通(60m/分)"),
        (50,"遅い(50m/分)"),
        )
    speed = forms.ChoiceField(label="歩く速度",choices=choice_speed,widget=forms.Select(attrs={'class': 'form-param'}))
    choice_browse=(
        (2.0,"速い"),
        (1.5,"やや速い"),
        (1.0,"普通"),
        (0.75,"やや遅い"),
        (0.5,"遅い")
    )
    browse = forms.ChoiceField(label="閲覧時間",choices=choice_browse,widget=forms.Select(attrs={'class': 'form-param'}))
    
class TSPParameterEnForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = " "
    
    choice_speed=(
        (70,"Fast(70m/m)"),
        (60,"Normal(60m/m)"),
        (50,"Slow(50m/m)"),
        )
    speed = forms.ChoiceField(label="Walking Speed",choices=choice_speed,widget=forms.Select(attrs={'class': 'form-param'}))
    choice_browse=(
        (2.0,"Very Fast"),
        (1.5,"Fast"),
        (1.0,"Normal"),
        (0.75,"Slow"),
        (0.5,"Very Slow")
    )
    browse = forms.ChoiceField(label="Appreciation Speed",choices=choice_browse,widget=forms.Select(attrs={'class': 'form-param'}))
    