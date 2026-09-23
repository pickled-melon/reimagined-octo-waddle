from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView

from schedule.models import *

# Create your views here.
class ShowProfilesView(View):
    def get(self, request, *args, **kwargs):
        result = ""
        for obj in Profile.objects.select_related('user').all():
            result += f"{obj}<br>"
        return HttpResponse(result)


class ShowClassroomsView(TemplateView):
    template_name = "classrooms/show_classrooms.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classrooms'] = Classroom.objects.all()

        return context


class ShowSubjectsView(View):
    def get(self, request, *args, **kwargs):
        result = ""
        for obj in Subject.objects.all():
            result += f"{obj}<br>"
        return HttpResponse(result)


class ShowStudyYearsView(View):
    def get(self, request, *args, **kwargs):
        result = ""
        for obj in StudyYear.objects.all():
            result += f"{obj}<br>"
        return HttpResponse(result)


class ShowBellSchedulesView(View):
    def get(self, request, *args, **kwargs):
        result = ""
        for obj in BellSchedule.objects.all():
            result += f"{obj}<br>"
        return HttpResponse(result)


class ShowUserSubjectsView(View):
    def get(self, request, *args, **kwargs):
        result = ""
        for obj in UserSubject.objects.select_related('user', 'subject').all():
            result += f"{obj}<br>"
        return HttpResponse(result)


class ShowDifficultiesView(View):
    def get(self, request, *args, **kwargs):
        result = ""
        for obj in Difficulty.objects.select_related('study_year', 'subject').all():
            result += f"{obj}<br>"
        return HttpResponse(result)


class ShowStudyGroupsView(View):
    def get(self, request, *args, **kwargs):
        result = ""
        for obj in StudyGroup.objects.select_related('study_year', 'parent').all():
            result += f"{obj}<br>"
        return HttpResponse(result)


class ShowWorkloadsView(View):
    def get(self, request, *args, **kwargs):
        result = ""
        for obj in Workload.objects.select_related(
            'study_group', 'teacher', 'subject'
        ).all():
            result += f"{obj}<br>"
        return HttpResponse(result)


class ShowLessonsView(View):
    def get(self, request, *args, **kwargs):
        result = ""
        for obj in Lesson.objects.select_related(
            'workload__study_group',
            'workload__teacher',
            'workload__subject',
            'classroom',
            'bell_schedule',
        ).all():
            result += f"{obj}<br>"
        return HttpResponse(result)