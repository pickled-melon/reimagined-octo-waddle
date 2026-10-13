from django.contrib import admin

from schedule.models import *

# Register your models here.
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role']
    list_filter = ['role']
    search_fields = ['user__username', 'user__last_name', 'user__first_name']

    @admin.display(description='Роль')
    def get_role_display(self, obj):
        return obj.get_role_display()


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


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'type']


@admin.register(UserSubject)
class UserSubjectAdmin(admin.ModelAdmin):
    list_display = ['user', 'subject']

@admin.register(Difficulty)
class DifficultyAdmin(admin.ModelAdmin):
    list_display = ['study_year', 'subject', 'points']


@admin.register(Workload)
class WorkloadAdmin(admin.ModelAdmin):
    list_display = ['hours_count', 'study_group', 'teacher', 'subject']

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['week_day', 'workload', 'classroom', 'bell_schedule']
