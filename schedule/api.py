from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import logout as django_logout
from django.contrib.auth import login as django_login
from django.contrib.auth import authenticate

from schedule.models import *
from schedule.serializers import *

class ProfileViewSet(GenericViewSet):
    queryset = User.objects.all()

    @action(detail=False, url_path="me", methods=['GET'])
    def get_me(self, request, *args, **kwargs):
        data = {'is_authenticated': self.request.user.is_authenticated}
        if self.request.user.is_authenticated:
            profile = getattr(self.request.user, 'profile', None)
            data.update({
                "username": self.request.user.username,
                "id": self.request.user.id,
                "role": profile.role if profile else 0,
                "is_superuser": self.request.user.is_superuser,
            })
        return Response(data=data)

    @action(detail=False, url_path="logout", methods=['POST'])
    def logout(self, *args, **kwargs):
        django_logout(self.request)
        return Response()

    @action(detail=False, url_path="login", methods=['POST'])
    def login(self, *args, **kwargs):
        username = self.request.data.get('username')
        password = self.request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            django_login(self.request, user)
            return Response({'success': True}, status=200)
        return Response({'success': False}, status=403)

    @action(detail=False, url_path="register", methods=['POST'])
    def register(self, *args, **kwargs):
        username = self.request.data.get('username')
        password = self.request.data.get('password')
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Пользователь существует'}, status=400)
        user = User.objects.create_user(username=username, password=password)
        django_login(self.request, user)
        return Response({'success': True}, status=201)
    
    @action(detail=False, url_path="all", methods=['GET'])
    def get_all(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({'error': 'Нет прав'}, status=403)
        users = User.objects.all().values('id', 'username')
        return Response(users)

class ClassroomViewSet(viewsets.ModelViewSet):
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer
    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated: return qs.none()
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user')
            if user_id: qs = qs.filter(user_id=user_id)
            return qs
        return qs.filter(user=self.request.user)

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.prefetch_related('classrooms', 'pictures').all()
    serializer_class = SubjectSerializer
    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated: return qs.none()
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user')
            if user_id: qs = qs.filter(user_id=user_id)
            return qs
        return qs.filter(user=self.request.user)

class SubjectPictureViewSet(viewsets.ModelViewSet):
    queryset = SubjectPicture.objects.select_related('subject').all()
    serializer_class = SubjectPictureSerializer
    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated: return qs.none()
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user')
            if user_id: qs = qs.filter(user_id=user_id)
            return qs
        return qs.filter(user=self.request.user)

class StudyYearViewSet(viewsets.ModelViewSet):
    queryset = StudyYear.objects.all()
    serializer_class = StudyYearSerializer
    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated: return qs.none()
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user')
            if user_id: qs = qs.filter(user_id=user_id)
            return qs
        return qs.filter(user=self.request.user)

class BellScheduleViewSet(viewsets.ModelViewSet):
    queryset = BellSchedule.objects.all()
    serializer_class = BellScheduleSerializer
    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated: return qs.none()
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user')
            if user_id: qs = qs.filter(user_id=user_id)
            return qs
        return qs.filter(user=self.request.user)

class UserSubjectViewSet(viewsets.ModelViewSet):
    queryset = UserSubject.objects.select_related('user', 'subject').all()
    serializer_class = UserSubjectSerializer
    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated: return qs.none()
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user')
            if user_id: qs = qs.filter(creator_id=user_id)
            return qs
        return qs.filter(creator=self.request.user)

class DifficultyViewSet(viewsets.ModelViewSet):
    queryset = Difficulty.objects.select_related('study_year', 'subject').all()
    serializer_class = DifficultySerializer
    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated: return qs.none()
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user')
            if user_id: qs = qs.filter(user_id=user_id)
            return qs
        return qs.filter(user=self.request.user)

class StudyGroupViewSet(viewsets.ModelViewSet):
    queryset = StudyGroup.objects.select_related('study_year', 'parent').all()
    serializer_class = StudyGroupSerializer
    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated: return qs.none()
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user')
            if user_id: qs = qs.filter(user_id=user_id)
            return qs
        return qs.filter(user=self.request.user)

class WorkloadViewSet(viewsets.ModelViewSet):
    queryset = Workload.objects.select_related('study_group', 'teacher', 'subject').all()
    serializer_class = WorkloadSerializer
    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated: return qs.none()
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user')
            if user_id: qs = qs.filter(user_id=user_id)
            return qs
        return qs.filter(user=self.request.user)

class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.select_related('workload__study_group', 'workload__teacher', 'workload__subject', 'classroom', 'bell_schedule').all()
    serializer_class = LessonSerializer
    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated: return qs.none()
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user')
            if user_id: qs = qs.filter(user_id=user_id)
            return qs
        return qs.filter(user=self.request.user)