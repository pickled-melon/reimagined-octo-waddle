from rest_framework import mixins, viewsets, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import logout as django_logout
from django.contrib.auth import login as django_login
from django.contrib.auth import authenticate
from django.db.models import Avg, Count, Max, Min, Sum, F, Q

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
        if not self.request.user.is_authenticated:
            return qs.none()
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user')
            if user_id:
                qs = qs.filter(user_id=user_id)
        else:
            qs = qs.filter(user=self.request.user)
        return qs.annotate(
            weekly_lessons=Count('lessons', distinct=True),
            teachers_count=Count('lessons__workload__teacher', distinct=True),
            groups_count=Count('lessons__workload__study_group', distinct=True),
            subjects_count=Count('lessons__workload__subject', distinct=True),
        )

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        distinct_slots = BellSchedule.objects.values('start_time').distinct().count()
        max_daily = distinct_slots or 7
        ctx['max_daily_slots'] = max_daily
        return ctx

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        stats = self.get_queryset().aggregate(
            count=Count("id"),
            avg=Avg("capacity"),
            max=Max("capacity"),
            min=Min("capacity"),
        )
        serializer = StatsSerializer(instance=stats)
        return Response(serializer.data)


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.prefetch_related('classrooms', 'pictures').all().order_by('id')
    serializer_class = SubjectSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated:
            return qs.none()
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user')
            if user_id:
                qs = qs.filter(user_id=user_id)
            return qs
        return qs.filter(user=self.request.user)

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        qs = self.get_queryset()
        total = qs.count()
        extra = qs.filter(type='extracurricular').count()
        extra_percent = round(extra / total * 100, 1) if total else 0
        
        total_hours = qs.aggregate(total=Sum('workloads__hours_count'))['total'] or 0
        avg_diff = qs.aggregate(avg=Avg('difficulties__points'))['avg'] or 0

        stats = {
            'count': total,
            'extracurricular_percent': extra_percent,
            'total_hours': total_hours,
            'avg_difficulty': round(avg_diff, 1),
        }
        return Response(stats)


class SubjectPictureViewSet(viewsets.ModelViewSet):
    queryset = SubjectPicture.objects.select_related('subject').all().order_by('id')
    serializer_class = SubjectPictureSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated:
            return qs.none()
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user')
            if user_id:
                qs = qs.filter(user_id=user_id)
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
        if not self.request.user.is_authenticated:
            return qs.none()
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user')
            if user_id:
                qs = qs.filter(user_id=user_id)
            return qs
        return qs.filter(user=self.request.user)

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        qs = self.get_queryset()
        count = qs.count()
        total_groups = StudyGroup.objects.filter(study_year__in=qs, type='group').count()
        avg_groups = round(total_groups / count, 1) if count else 0

        stats = qs.aggregate(
            avg_weekly=Avg("max_weekly_hours"),
            avg_daily=Avg("max_daily_hours"),
        )
        stats['count'] = count
        stats['avg_groups'] = avg_groups
        return Response(stats)


class BellScheduleViewSet(viewsets.ModelViewSet):
    queryset = BellSchedule.objects.all().order_by('id')
    serializer_class = BellScheduleSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated:
            return qs.none()
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user')
            if user_id:
                qs = qs.filter(user_id=user_id)
        else:
            qs = qs.filter(user=self.request.user)
        return qs

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        qs = self.get_queryset()
        count = qs.count()
        
        total_lessons = Lesson.objects.filter(bell_schedule__in=qs).count()
        
        unique_times = qs.values('start_time').distinct().count()
        avg_lessons_per_slot = round(total_lessons / unique_times, 1) if unique_times else 0

        durations = []
        from datetime import datetime, date
        for b in qs:
            start = datetime.combine(date.today(), b.start_time)
            end = datetime.combine(date.today(), b.end_time)
            durations.append((end - start).total_seconds() / 60)
            
        avg_duration = round(sum(durations) / count, 1) if count else 0

        stats = {
            'count': count,
            'avg_duration': avg_duration,
            'total_lessons': total_lessons,
            'avg_lessons_per_slot': avg_lessons_per_slot,
        }
        return Response(stats)


class UserSubjectViewSet(viewsets.ModelViewSet):
    queryset = UserSubject.objects.select_related('user', 'subject').all().order_by('id')
    serializer_class = UserSubjectSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated:
            return qs.none()
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user')
            if user_id:
                qs = qs.filter(creator_id=user_id)
        else:
            qs = qs.filter(creator=self.request.user)
        
        return qs

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        qs = self.get_queryset()
        count = qs.count()
        teachers_count = qs.values('user').distinct().count()
        subjects_count = qs.values('subject').distinct().count()
        avg_subjects = round(count / teachers_count, 1) if teachers_count else 0

        stats = {
            'count': count,
            'teachers_count': teachers_count,
            'subjects_count': subjects_count,
            'avg_subjects': avg_subjects,
        }
        return Response(stats)
    queryset = UserSubject.objects.select_related('user', 'subject').all().order_by('id')
    serializer_class = UserSubjectSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated:
            return qs.none()
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user')
            if user_id:
                qs = qs.filter(creator_id=user_id)
        else:
            qs = qs.filter(creator=self.request.user)
        
        return qs.annotate(
            assigned_hours=Sum('user__workloads__hours_count', filter=Q(user__workloads__subject=F('subject'))),
            assigned_groups=Count('user__workloads__study_group', filter=Q(user__workloads__subject=F('subject')), distinct=True)
        )

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        qs = self.get_queryset()
        count = qs.count()
        teachers_count = qs.values('user').distinct().count()
        subjects_count = qs.values('subject').distinct().count()
        avg_subjects = round(count / teachers_count, 1) if teachers_count else 0

        stats = {
            'count': count,
            'teachers_count': teachers_count,
            'subjects_count': subjects_count,
            'avg_subjects': avg_subjects,
        }
        return Response(stats)


class DifficultyViewSet(viewsets.ModelViewSet):
    queryset = Difficulty.objects.select_related('study_year', 'subject').all().order_by('id')
    serializer_class = DifficultySerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated:
            return qs.none()
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user')
            if user_id:
                qs = qs.filter(user_id=user_id)
            return qs
        return qs.filter(user=self.request.user)

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        qs = self.get_queryset()
        
        stats = qs.aggregate(
            count=Count("*"),
            avg=Avg("points"),
            max=Max("points"),
            min=Min("points")
        )
        
        stats['hard_count'] = qs.filter(points__gte=8).count()
        stats['easy_count'] = qs.filter(points__lte=4).count()

        return Response(stats)


class StudyGroupViewSet(viewsets.ModelViewSet):
    queryset = StudyGroup.objects.select_related('study_year', 'parent').all().order_by('id')
    serializer_class = StudyGroupSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated:
            return qs.none()
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user')
            if user_id:
                qs = qs.filter(user_id=user_id)
        else:
            qs = qs.filter(user=self.request.user)
        
        return qs.annotate(
            total_hours=Sum('workloads__hours_count'),
            subgroups_count=Count('subgroups', distinct=True)
        )

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        stats = self.get_queryset().aggregate(
            count=Count("id"),
            total_students=Sum("students_count"),
            avg_students=Avg("students_count"),
        )
        return Response(stats)


class WorkloadViewSet(viewsets.ModelViewSet):
    queryset = Workload.objects.select_related('study_group', 'teacher', 'subject').all().order_by('id')
    serializer_class = WorkloadSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated:
            return qs.none()
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user')
            if user_id:
                qs = qs.filter(user_id=user_id)
        else:
            qs = qs.filter(user=self.request.user)
        return qs.annotate(distributed_lessons=Count('lessons', distinct=True))

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        qs = self.get_queryset()
        total_planned = qs.aggregate(total=Sum('hours_count'))['total'] or 0
        total_distributed = Lesson.objects.filter(workload__in=qs).count()
        stats = {
            'count': qs.count(),
            'planned': total_planned,
            'distributed': total_distributed,
            'unassigned': max(0, total_planned - total_distributed),
        }
        return Response(stats)


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.select_related('workload__study_group', 'workload__teacher', 'workload__subject', 'classroom', 'bell_schedule').all().order_by('id')
    serializer_class = LessonSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated:
            return qs.none()
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user')
            if user_id:
                qs = qs.filter(user_id=user_id)
            return qs
        return qs.filter(user=self.request.user)

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        qs = self.get_queryset()
        total = qs.count()
        test_count = qs.filter(is_test=True).count()

        teacher_conflicts = qs.values('week_day', 'bell_schedule', 'workload__teacher').annotate(c=Count('id')).filter(c__gt=1).count()
        group_conflicts = qs.values('week_day', 'bell_schedule', 'workload__study_group').annotate(c=Count('id')).filter(c__gt=1).count()

        stats = {
            'count': total,
            'test_count': test_count,
            'teacher_conflicts': teacher_conflicts,
            'group_conflicts': group_conflicts,
        }
        return Response(stats)
