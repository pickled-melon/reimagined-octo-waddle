from rest_framework import viewsets

from schedule.models import *
from schedule.serializers import *


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.select_related('user').all()
    serializer_class = ProfileSerializer


class ClassroomViewSet(viewsets.ModelViewSet):
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.prefetch_related('classrooms').all()
    serializer_class = SubjectSerializer


class StudyYearViewSet(viewsets.ModelViewSet):
    queryset = StudyYear.objects.all()
    serializer_class = StudyYearSerializer


class BellScheduleViewSet(viewsets.ModelViewSet):
    queryset = BellSchedule.objects.all()
    serializer_class = BellScheduleSerializer


class UserSubjectViewSet(viewsets.ModelViewSet):
    queryset = UserSubject.objects.select_related('user', 'subject').all()
    serializer_class = UserSubjectSerializer


class DifficultyViewSet(viewsets.ModelViewSet):
    queryset = Difficulty.objects.select_related('study_year', 'subject').all()
    serializer_class = DifficultySerializer


class StudyGroupViewSet(viewsets.ModelViewSet):
    queryset = StudyGroup.objects.select_related('study_year', 'parent').all()
    serializer_class = StudyGroupSerializer


class WorkloadViewSet(viewsets.ModelViewSet):
    queryset = Workload.objects.select_related(
        'study_group', 'teacher', 'subject'
    ).all()
    serializer_class = WorkloadSerializer


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.select_related(
        'workload__study_group',
        'workload__teacher',
        'workload__subject',
        'classroom',
        'bell_schedule',
    ).all()
    serializer_class = LessonSerializer
