from rest_framework import mixins, viewsets, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import logout as django_logout
from django.contrib.auth import login as django_login
from django.contrib.auth import authenticate
from django.db.models import Avg, Count, Max, Min

from schedule.models import *
from schedule.serializers import *


class StatsSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    avg = serializers.FloatField(required=False)
    max = serializers.IntegerField(required=False)
    min = serializers.IntegerField(required=False)


class ProfileViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Profile.objects.select_related('user').all().order_by('id')
    serializer_class = ProfileSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated:
            return qs.none()
        if self.request.user.is_superuser:
            return qs
        return qs.filter(user=self.request.user)

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        stats = self.get_queryset().aggregate(count=Count("*"))
        serializer = StatsSerializer(instance=stats)
        return Response(serializer.data)

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
        users = User.objects.all().values('id', 'username').order_by('id')
        return Response(users)


class ClassroomViewSet(viewsets.ModelViewSet):
    queryset = Classroom.objects.all().order_by('id')
    serializer_class = ClassroomSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated: return qs.none()
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user')
            if user_id: qs = qs.filter(user_id=user_id)
            return qs
        return qs.filter(user=self.request.user)

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        stats = self.get_queryset().aggregate(
            count=Count("*"),
            avg=Avg("capacity"),
            max=Max("capacity"),
            min=Min("capacity")
        )
        serializer = StatsSerializer(instance=stats)
        return Response(serializer.data)


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.prefetch_related('classrooms', 'pictures').all().order_by('id')
    serializer_class = SubjectSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated: return qs.none()
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user')
            if user_id: qs = qs.filter(user_id=user_id)
            return qs
        return qs.filter(user=self.request.user)

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        stats = self.get_queryset().aggregate(count=Count("*"))
        serializer = StatsSerializer(instance=stats)
        return Response(serializer.data)


class SubjectPictureViewSet(viewsets.ModelViewSet):
    queryset = SubjectPicture.objects.select_related('subject').all().order_by('id')
    serializer_class = SubjectPictureSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated: return qs.none()
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user')
            if user_id: qs = qs.filter(user_id=user_id)
            return qs
        return qs.filter(user=self.request.user)

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        stats = self.get_queryset().aggregate(count=Count("*"))
        serializer = StatsSerializer(instance=stats)
        return Response(serializer.data)


class StudyYearViewSet(viewsets.ModelViewSet):
    queryset = StudyYear.objects.all().order_by('id')
    serializer_class = StudyYearSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated: return qs.none()
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user')
            if user_id: qs = qs.filter(user_id=user_id)
            return qs
        return qs.filter(user=self.request.user)

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        stats = self.get_queryset().aggregate(
            count=Count("*"),
            avg=Avg("max_weekly_hours"),
            max=Max("max_weekly_hours"),
            min=Min("max_weekly_hours")
        )
        serializer = StatsSerializer(instance=stats)
        return Response(serializer.data)


class BellScheduleViewSet(viewsets.ModelViewSet):
    queryset = BellSchedule.objects.all().order_by('id')
    serializer_class = BellScheduleSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated: return qs.none()
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user')
            if user_id: qs = qs.filter(user_id=user_id)
            return qs
        return qs.filter(user=self.request.user)

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        stats = self.get_queryset().aggregate(count=Count("*"))
        serializer = StatsSerializer(instance=stats)
        return Response(serializer.data)


class UserSubjectViewSet(viewsets.ModelViewSet):
    queryset = UserSubject.objects.select_related('user', 'subject').all().order_by('id')
    serializer_class = UserSubjectSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated: return qs.none()
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user')
            if user_id: qs = qs.filter(creator_id=user_id)
            return qs
        return qs.filter(creator=self.request.user)

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        stats = self.get_queryset().aggregate(count=Count("*"))
        serializer = StatsSerializer(instance=stats)
        return Response(serializer.data)


class DifficultyViewSet(viewsets.ModelViewSet):
    queryset = Difficulty.objects.select_related('study_year', 'subject').all().order_by('id')
    serializer_class = DifficultySerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated: return qs.none()
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user')
            if user_id: qs = qs.filter(user_id=user_id)
            return qs
        return qs.filter(user=self.request.user)

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        stats = self.get_queryset().aggregate(
            count=Count("*"),
            avg=Avg("points"),
            max=Max("points"),
            min=Min("points")
        )
        serializer = StatsSerializer(instance=stats)
        return Response(serializer.data)


class StudyGroupViewSet(viewsets.ModelViewSet):
    queryset = StudyGroup.objects.select_related('study_year', 'parent').all().order_by('id')
    serializer_class = StudyGroupSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated: return qs.none()
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user')
            if user_id: qs = qs.filter(user_id=user_id)
            return qs
        return qs.filter(user=self.request.user)

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        stats = self.get_queryset().aggregate(
            count=Count("*"),
            avg=Avg("students_count"),
            max=Max("students_count"),
            min=Min("students_count")
        )
        serializer = StatsSerializer(instance=stats)
        return Response(serializer.data)


class WorkloadViewSet(viewsets.ModelViewSet):
    queryset = Workload.objects.select_related('study_group', 'teacher', 'subject').all().order_by('id')
    serializer_class = WorkloadSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated: return qs.none()
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user')
            if user_id: qs = qs.filter(user_id=user_id)
            return qs
        return qs.filter(user=self.request.user)

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        stats = self.get_queryset().aggregate(
            count=Count("*"),
            avg=Avg("hours_count"),
            max=Max("hours_count"),
            min=Min("hours_count")
        )
        serializer = StatsSerializer(instance=stats)
        return Response(serializer.data)


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.select_related('workload__study_group', 'workload__teacher', 'workload__subject', 'classroom', 'bell_schedule').all().order_by('id')
    serializer_class = LessonSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated: return qs.none()
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user')
            if user_id: qs = qs.filter(user_id=user_id)
            return qs
        return qs.filter(user=self.request.user)

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        stats = self.get_queryset().aggregate(count=Count("*"))
        serializer = StatsSerializer(instance=stats)
        return Response(serializer.data)