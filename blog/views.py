from django.http.response import HttpResponseServerError
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib import messages

from django.views import View
from django.views.generic.base import TemplateView 
from blog.forms import LoginForm
from django.http import HttpResponseRedirect
from .forms import MorningTimeForm
from .forms import NightTimeForm
from .models import SleepAction
import json
from django.core.serializers.json import DjangoJSONEncoder

from django.contrib.auth.forms import UserCreationForm

class LoginView(View):
    template_name = 'login.html'

    def get(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        context = {'form': form}

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)

            if user:
                login(request, user)
                return HttpResponseRedirect("/")

            return render(request, self.template_name, {'form': form})

        else:
            return render(request, self.template_name, {'form': form})


class IndexPage(TemplateView):
    template_name = "sleep/index.html"
    
    def get(self, request):
        sleepRecords = []
        sleepStartHour, sleepStartMinute = [0, 0]
        sleepEndHour, sleepEndMinute = [0, 0]
        averageProductivityPerThreeLatestRecords = float(0)
        sleepStability = 0
        isMoreSleepRecommended = 0
        averageSleepDuration = float(0)
        hasSleepData = False

        if (not request.user.is_anonymous and SleepAction.withUser(request.user).exists()):
            user = request.user
            
            sleepRecords = SleepAction.withUser(request.user).values()
            sleepStartHour, sleepStartMinute = SleepAction.getAverageSleepStartTime(user)
            sleepEndHour, sleepEndMinute = SleepAction.getAverageSleepEndTime(user)
            averageProductivityPerThreeLatestRecords = SleepAction.getLastThreeDaysProductivity(user)
            sleepStability = SleepAction.getSleepStability(user)
            isMoreSleepRecommended = SleepAction.checkShouldShowGetMoreSleepRecommendation(user)
            averageSleepDuration = SleepAction.getAverageSleepDuration(user)
            hasSleepData = True

        context = {
            'sleepRecords': json.dumps(list(sleepRecords), cls=DjangoJSONEncoder),
            'averageSleepDurationTime': format(averageSleepDuration, '.2f'),
            'averageSleepStartTime': f'{sleepStartHour:02}:{sleepStartMinute:02}',
            'averageSleepEndTime': f'{sleepEndHour:02}:{sleepEndMinute:02}',
            'averageProductivityPerThreeLatestRecords': f'{averageProductivityPerThreeLatestRecords:.{2}}',
            'sleepStability': f'{sleepStability:.2%}',
            'isMoreSleepRecommended': isMoreSleepRecommended,
            'hasSleepData': hasSleepData,
        }

        return render(request, self.template_name, context)


def regist(request):
    context = {}
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        context['form'] = form

        if form.is_valid():
            form.save()
            messages.success(request, 'Регистрация прошла успешно!')
            return HttpResponseRedirect('/login')
        else:
            context['error'] = "Ваш пароль не прошел валидацию"
            return render(request, 'registr.html', context) 
    else:
        form = UserCreationForm()
        context['form'] = form
        return render(request, 'registr.html', context)


def index_day(request):
    sleepRecords = SleepAction.withUser(request.user).values()
    is_sleep_record_updated_successfully = None

    if request.method == 'POST':
        morningSleepRecordForm = MorningTimeForm(request.POST, User=request.user)
        is_sleep_record_updated_successfully = False

        if morningSleepRecordForm.is_valid():
            SleepAction.objects.update_or_create(
                Week_Day=morningSleepRecordForm.cleaned_data.get('Week_Day'),
                User=request.user,
                defaults=morningSleepRecordForm.cleaned_data
            )
            is_sleep_record_updated_successfully = True
    else:
        morningSleepRecordForm = MorningTimeForm(User=request.user)

    context = {
        'sleepRecords': json.dumps(list(sleepRecords), cls=DjangoJSONEncoder),
        'is_sleep_record_updated_successfully': is_sleep_record_updated_successfully,
        'form': morningSleepRecordForm,
    }

    return render(request, 'sleep/index_day.html', context)


def index_night(request):
    sleepRecords = SleepAction.withUser(request.user).values()
    is_sleep_record_updated_successfully = None

    if request.method == 'POST':
        nightSleepRecordForm = NightTimeForm(request.POST, User=request.user)
        is_sleep_record_updated_successfully = False

        if nightSleepRecordForm.is_valid():
            SleepAction.objects.update_or_create(
                Week_Day=nightSleepRecordForm.cleaned_data.get('Week_Day'),
                User=request.user,
                defaults=nightSleepRecordForm.cleaned_data,
            )
            is_sleep_record_updated_successfully = True

    else:
        nightSleepRecordForm = NightTimeForm(User=request.user)

    context = {
        'sleepRecords': json.dumps(list(sleepRecords), cls=DjangoJSONEncoder),
        'is_sleep_record_updated_successfully': is_sleep_record_updated_successfully,
        'form': nightSleepRecordForm,
    }

    return render(request, 'sleep/index_night.html', context)