from django import forms
from django.contrib.auth.models import User
from django.forms.forms import Form
from blog.models import Post, SleepAction


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('title', 'text',)

class LoginForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'password']

    def __init__ (self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Логин'
        self.fields['password'].label = 'Пароль'

    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError('Пользователь с данным логином не найден в системе')
        user = User.objects.filter(username=username).first()
        if user :
            if not user.check_password(password):
                raise forms.ValidationError('Неверный пароль')
        return self.cleaned_data


class MorningTimeForm(forms.ModelForm):
    Week_Day = forms.ChoiceField(label='День недели?', choices=SleepAction.WeekDays.choices)

    Morning_Time = forms.TimeField(label='Во сколько ты встал?',
                                   help_text='Пример: 8:00, 11:00',
                                   widget=forms.TimeInput,)
    Awake_Sleep = forms.IntegerField(label='Твоё состояние после пробуждения?',
                                     help_text='Дай оценку по шкале от 1 до 5')
    User = None

    def __init__(self, *args, **kwargs):
        self.User = kwargs.pop('User', None)
        super(MorningTimeForm, self).__init__(*args, **kwargs)

    class Meta:
        model = SleepAction
        fields = ('Morning_Time', 'Awake_Sleep', 'Week_Day')

    field_order = ['Week_Day', 'Morning_Time', 'Awake_Sleep']


class NightTimeForm(forms.ModelForm):
    Week_Day = forms.ChoiceField(label='День недели?', choices=SleepAction.WeekDays.choices)

    Night_Time = forms.TimeField(label='Во сколько ты лёг?',
                                 help_text='Пример: 21:00, 22:00')
    Productivity = forms.IntegerField(label='Как ты оцениваешь свою продуктивность?',
                                      help_text='Дай оценку по шкале от 1 до 5')
    Quality_Day = forms.IntegerField(label='Твое состояние в течении дня?',
                                     help_text='Дай оценку по шкале от 1 до 5')

    def __init__(self, *args, **kwargs):
        self.User = kwargs.pop('User', None)
        super(NightTimeForm, self).__init__(*args, **kwargs)

    class Meta:
        model = SleepAction
        fields = ('Night_Time', 'Productivity', 'Quality_Day', 'Week_Day')

    field_order = ['Week_Day', 'Night_Time', 'Quality_Day', 'Productivity']
