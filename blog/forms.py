from django import forms
from django.contrib.auth.models import User
from django.forms.forms import Form
from blog.models import Post

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
            raise forms.ValidationError('Пользователь с логином {Username} не найден в системе')
        user = User.objects.filter(username=username).first()
        if user :
            if not user.check_password(password):
                raise forms.ValidationError('Неверный пароль')
        return self.cleaned_data
