from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.views import View
from django.views.generic.base import TemplateView 
from blog.forms import LoginForm
from django.http import HttpResponseRedirect

class LoginView(View):

    def get(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        context = {'Form': form}
        return render(request, 'login.html', context)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect('/')
            return render(request, 'login.html', {'form': form})


class IndexPage(TemplateView):
    template_name = "blog/base.html"