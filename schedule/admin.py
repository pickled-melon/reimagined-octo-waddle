from django.contrib import admin

from schedule.models import *
# Register your models here.
@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ['number', 'capacity']


@admin.register(BellSchedule)
class BellScheduleAdmin(admin.ModelAdmin):
    list_display = ['lesson_number', 'start_time', 'end_time']


@admin.register(StudyGroup)
class StudyGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'students_count']


@admin.register(StudyYear)
class StudyYearAdmin(admin.ModelAdmin):
    list_display = ['year', 'max_weekly_hours', 'max_daily_hours']
