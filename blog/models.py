from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from functools import reduce
from datetime import datetime
import math


class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title

def getPrevWeekDay(weekDay):
    weekDayToPrevWeekDay = {
        SleepAction.WeekDays.MONDAY: SleepAction.WeekDays.SUNDAY,
        SleepAction.WeekDays.TUESDAY: SleepAction.WeekDays.MONDAY,
        SleepAction.WeekDays.WEDNESDAY: SleepAction.WeekDays.TUESDAY,
        SleepAction.WeekDays.THURSDAY: SleepAction.WeekDays.WEDNESDAY,
        SleepAction.WeekDays.FRIDAY: SleepAction.WeekDays.THURSDAY,
        SleepAction.WeekDays.SATURDAY: SleepAction.WeekDays.FRIDAY,
        SleepAction.WeekDays.SUNDAY: SleepAction.WeekDays.SATURDAY,
    }

    nextWeekDay = weekDayToPrevWeekDay[weekDay]
    return nextWeekDay


class SleepAction(models.Model):
    class WeekDays(models.TextChoices):
        MONDAY = 'monday', 'Понедельник'
        TUESDAY = 'tuesday', 'Вторник'
        WEDNESDAY = 'wednesday', 'Среда'
        THURSDAY = 'thursday', 'Четверг'
        FRIDAY = 'friday', 'Пятница'
        SATURDAY = 'saturday', 'Суббота'
        SUNDAY = 'sunday', 'Воскресенье'

    Morning_Time = models.TimeField(null=True)  # Во сколько встал
    Awake_Sleep = models.IntegerField(null=True)  # Состояние после пробуждения
    Quality_Sleep = models.IntegerField(null=True)  # Качество сна

    Night_Time = models.TimeField(null=True)  # Во сколько лёг
    Productivity = models.IntegerField(null=True)  # Продуктивность
    Quality_Day = models.IntegerField(null=True)  # Состояние в течение дня

    Created_At = models.DateTimeField(auto_now_add=True)
    Updated_At = models.DateTimeField(auto_now=True)

    Week_Day = models.CharField(
        max_length=10,
        choices=WeekDays.choices,
        default=WeekDays.MONDAY
    )

    User = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'MorningTime:{self.Morning_Time}--NightTime:{self.Night_Time}--' \
               f'AwakeSleep:{self.Awake_Sleep}'

    @staticmethod
    def withUser(user):
        return SleepAction.objects.filter(User=user)

    def getMorningTimeMinutes(self):
        sleepStartTimeHour = self.Morning_Time.hour if self.Morning_Time else 0
        sleepStartTimeMinute = self.Morning_Time.minute if self.Morning_Time else 0
        sleepStartTimeMinutesTotal = sleepStartTimeHour * 60 + sleepStartTimeMinute

        return sleepStartTimeMinutesTotal

    def getMorningTimeHours(self):
        return round(self.getMorningTimeMinutes() / 60, 2)

    def getNightTimeMinutes(self):
        sleepEndTimeHour = self.Night_Time.hour if self.Night_Time else 0
        sleepEndTimeMinutes = self.Night_Time.minute if self.Night_Time else 0
        sleepEndTimeMinutesTotal = sleepEndTimeHour * 60 + sleepEndTimeMinutes

        return sleepEndTimeMinutesTotal

    def getNightTimeHours(self):
        return round(self.getNightTimeMinutes() / 60, 2)

    def getSleepDurationHours(self):
        prevWeekDay = getPrevWeekDay(self.Week_Day)
        sleepRecordForPrevDay = SleepAction.withUser(self.User).get(Week_Day=prevWeekDay) if SleepAction.withUser(self.User).filter(Week_Day=prevWeekDay).exists() else None
        
        if (not sleepRecordForPrevDay):
            return float(0)

        sleepEndTimeMinutesTotal = self.getMorningTimeMinutes()
        sleepStartTimeMinutesTotal = sleepRecordForPrevDay.getNightTimeMinutes()

        durationTimeMinutes = (1440 - sleepStartTimeMinutesTotal) + sleepEndTimeMinutesTotal
        durationTimeHours = durationTimeMinutes / 60

        return float(format(durationTimeHours, ".2f"))

    @staticmethod
    def getAverageSleepDuration(user):
        allSleepRecords = SleepAction.withUser(user).all()

        if (not allSleepRecords.exists()):
            return float(0)

        averageSleepDurationTime = reduce(
            (lambda average, sleepRecord: average + sleepRecord.getSleepDurationHours()),
            list(allSleepRecords),
            0
        ) / allSleepRecords.count()

        return averageSleepDurationTime

    @staticmethod
    def getAverageSleepStartTime(user):
        sleepRecordsThatHaveAwakeQualityFourOrFive = SleepAction.withUser(user).filter(Awake_Sleep__gte=4).all()

        if (sleepRecordsThatHaveAwakeQualityFourOrFive.count() == 0):
            return (0, 0)

        averageSleepStartTimeTotalMinutes = reduce(
            (lambda average, sleepRecord: average + sleepRecord.getNightTimeMinutes()),
            list(sleepRecordsThatHaveAwakeQualityFourOrFive),
            0
        ) / sleepRecordsThatHaveAwakeQualityFourOrFive.count()

        averageSleepStartTimeWholeHours = math.floor(averageSleepStartTimeTotalMinutes / 60)
        averageSleepStartTimeLeftMinutes = averageSleepStartTimeTotalMinutes - averageSleepStartTimeWholeHours * 60;
        # TODO: count average only when Awake_Sleep

        return int(averageSleepStartTimeWholeHours), int(averageSleepStartTimeLeftMinutes),

    @staticmethod
    def getAverageSleepEndTime(user):
        sleepRecordsThatHaveAwakeQualityFourOrFive = SleepAction.withUser(user).filter(Awake_Sleep__gte=4).all()

        if (sleepRecordsThatHaveAwakeQualityFourOrFive.count() == 0):
            return (0, 0)

        averageSleepEndTimeTotalMinutes = reduce(
            (lambda average, sleepRecord: average + sleepRecord.getMorningTimeMinutes()),
            list(sleepRecordsThatHaveAwakeQualityFourOrFive),
            0
        ) / sleepRecordsThatHaveAwakeQualityFourOrFive.count()

        averageSleepEndTimeWholeHours = math.floor(averageSleepEndTimeTotalMinutes / 60)
        averageSleepEndTimeLeftMinutes = averageSleepEndTimeTotalMinutes - averageSleepEndTimeWholeHours * 60

        return int(averageSleepEndTimeWholeHours), int(averageSleepEndTimeLeftMinutes)

    @staticmethod
    def getLastThreeDaysProductivity(user):
        threeLatestSleepRecords = SleepAction.withUser(user).order_by('Updated_At').exclude(Productivity__isnull=True)[:3]

        if (threeLatestSleepRecords.count() == 0):
            return float(0)
        
        averageProductivityPerThreeDays = reduce(
            (lambda average, sleepRecord: average + sleepRecord.Productivity),
            list(threeLatestSleepRecords),
            0
        ) / 3

        return averageProductivityPerThreeDays

    @staticmethod
    def getSleepStability(user):
        def getLatestTimeRecordStability(averageTime, lastestTimeMinutesTotal):
            timeHour, timeMinute = averageTime
            averageMinutesTotal = timeHour * 60 + timeMinute
            latestTimeRecordDeviation = abs(lastestTimeMinutesTotal - averageMinutesTotal)
            latestTimeRecordDeviationPercentage = latestTimeRecordDeviation / averageMinutesTotal \
                if averageMinutesTotal > 0 \
                else 0
            latestTimeRecordStability = 1 - latestTimeRecordDeviationPercentage
            return latestTimeRecordStability

        twoLatestSleepRecords = SleepAction.withUser(user).order_by('Updated_At').all()[:2]

        if (twoLatestSleepRecords.count() < 2):
            return 0

        startingSleepRecord = twoLatestSleepRecords[0]
        endingSleepRecord = twoLatestSleepRecords[1]

        sleepStartStability = getLatestTimeRecordStability(
            SleepAction.getAverageSleepStartTime(user),
            startingSleepRecord.getNightTimeMinutes()
        )

        sleepEndStability = getLatestTimeRecordStability(
            SleepAction.getAverageSleepEndTime(user),
            endingSleepRecord.getMorningTimeMinutes()
        )

        sleepStability = (sleepStartStability + sleepEndStability) / 2

        return sleepStability

    @staticmethod
    def checkShouldShowGetMoreSleepRecommendation(user):
        latestSleepRecord = SleepAction.withUser(user).order_by('Updated_At').exclude(
            Productivity__isnull=True,
            Awake_Sleep__isnull=True,
            Quality_Day__isnull=True,
        ).last()

        if (not latestSleepRecord):
            return False
        
        productivity = latestSleepRecord.Productivity \
            if latestSleepRecord.Productivity != None \
            else 0
        
        awakeSleep = latestSleepRecord.Awake_Sleep \
            if latestSleepRecord.Awake_Sleep != None \
            else 0

        qualitySleep = latestSleepRecord.Quality_Day \
            if latestSleepRecord.Quality_Day != None \
            else 0
         
        return productivity \
               or awakeSleep \
               or qualitySleep
