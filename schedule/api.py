from rest_framework import mixins, viewsets, serializers
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import logout as django_logout
from django.contrib.auth import login as django_login
from django.contrib.auth import authenticate
from django.db.models import Avg, Count, Max, Min, Q, Sum

from schedule.models import *
from schedule.serializers import *


class StatsSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    avg = serializers.FloatField(required=False)
    max = serializers.IntegerField(required=False)
    min = serializers.IntegerField(required=False)


def apply_search(qs, request, fields):
    search = request.query_params.get('search', '').strip()
    if not search:
        return qs
    query = Q()
    for field in fields:
        query |= Q(**{field + '__icontains': search})
    return qs.filter(query)


class RolePermissionMixin:
    def get_role(self, request):
        profile = getattr(request.user, 'profile', None)
        return profile.role if profile else None

    def is_privileged(self, request):
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return self.get_role(request) in (Profile.Role.METHODIST, Profile.Role.HEAD_TEACHER)

    def is_teacher(self, request):
        return self.get_role(request) == Profile.Role.TEACHER

    def perform_create(self, serializer):
        if not self.is_privileged(self.request):
            raise PermissionDenied('Недостаточно прав для создания')
        serializer.save()

    def perform_update(self, serializer):
        if not self.is_privileged(self.request):
            raise PermissionDenied('Недостаточно прав для изменения')
        serializer.save()

    def perform_destroy(self, instance):
        if not self.is_privileged(self.request):
            raise PermissionDenied('Недостаточно прав для удаления')
        instance.delete()


class ProfileViewSet(
    RolePermissionMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Profile.objects.select_related('user').all().order_by(
        'user__last_name', 'user__first_name', 'patronymic_name', 'id'
    )
    serializer_class = ProfileSerializer
    search_fields = ['user__last_name', 'user__first_name', 'patronymic_name', 'user__username']

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated:
            return qs.none()
        if self.is_privileged(self.request):
            user_id = self.request.query_params.get('user')
            if user_id:
                qs = qs.filter(user_id=user_id)
        elif not self.is_teacher(self.request):
            return qs.none()
        return apply_search(qs, self.request, self.search_fields)

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
        if not self.is_privileged(request):
            return Response({'error': 'Нет прав'}, status=403)
        users = User.objects.all().values(
            'id', 'username', 'first_name', 'last_name',
            'profile__patronymic_name'
        ).order_by('last_name', 'first_name', 'profile__patronymic_name', 'id')
        return Response(users)


class ClassroomViewSet(RolePermissionMixin, viewsets.ModelViewSet):
    queryset = Classroom.objects.all().order_by('id')
    serializer_class = ClassroomSerializer
    search_fields = ['number']

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated:
            return qs.none()
        if self.is_privileged(self.request):
            user_id = self.request.query_params.get('user')
            if user_id:
                qs = qs.filter(user_id=user_id)
        elif not self.is_teacher(self.request):
            return qs.none()
        qs = apply_search(qs, self.request, self.search_fields)
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


class SubjectViewSet(RolePermissionMixin, viewsets.ModelViewSet):
    queryset = Subject.objects.prefetch_related('classrooms', 'groups', 'pictures').all().order_by('id')
    serializer_class = SubjectSerializer
    search_fields = ['title']

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated:
            return qs.none()
        if self.is_privileged(self.request):
            user_id = self.request.query_params.get('user')
            if user_id:
                qs = qs.filter(user_id=user_id)
        elif not self.is_teacher(self.request):
            return qs.none()
        return apply_search(qs, self.request, self.search_fields)

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


class SubjectPictureViewSet(RolePermissionMixin, viewsets.ModelViewSet):
    queryset = SubjectPicture.objects.select_related('subject').all().order_by('id')
    serializer_class = SubjectPictureSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated:
            return qs.none()
        if self.is_privileged(self.request):
            user_id = self.request.query_params.get('user')
            if user_id:
                qs = qs.filter(user_id=user_id)
        elif not self.is_teacher(self.request):
            return qs.none()
        return qs

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        stats = self.get_queryset().aggregate(count=Count("*"))
        serializer = StatsSerializer(instance=stats)
        return Response(serializer.data)


class StudyYearViewSet(RolePermissionMixin, viewsets.ModelViewSet):
    queryset = StudyYear.objects.all().order_by('id')
    serializer_class = StudyYearSerializer
    search_fields = ['year']

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated:
            return qs.none()
        if self.is_privileged(self.request):
            user_id = self.request.query_params.get('user')
            if user_id:
                qs = qs.filter(user_id=user_id)
        elif not self.is_teacher(self.request):
            return qs.none()
        return apply_search(qs, self.request, self.search_fields)

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


class BellScheduleViewSet(RolePermissionMixin, viewsets.ModelViewSet):
    queryset = BellSchedule.objects.all().order_by('id')
    serializer_class = BellScheduleSerializer
    search_fields = ['lesson_number']

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated:
            return qs.none()
        if self.is_privileged(self.request):
            user_id = self.request.query_params.get('user')
            if user_id:
                qs = qs.filter(user_id=user_id)
        elif not self.is_teacher(self.request):
            return qs.none()
        return apply_search(qs, self.request, self.search_fields)

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


class UserSubjectViewSet(RolePermissionMixin, viewsets.ModelViewSet):
    queryset = UserSubject.objects.select_related('user', 'subject').all().order_by('id')
    serializer_class = UserSubjectSerializer
    search_fields = ['user__last_name', 'subject__title']

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated:
            return qs.none()
        if self.is_privileged(self.request):
            user_id = self.request.query_params.get('user')
            if user_id:
                qs = qs.filter(creator_id=user_id)
        elif not self.is_teacher(self.request):
            return qs.none()
        return apply_search(qs, self.request, self.search_fields)

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


class DifficultyViewSet(RolePermissionMixin, viewsets.ModelViewSet):
    queryset = Difficulty.objects.select_related('study_year', 'subject').all().order_by('id')
    serializer_class = DifficultySerializer
    search_fields = ['subject__title', 'study_year__year']

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated:
            return qs.none()
        if self.is_privileged(self.request):
            user_id = self.request.query_params.get('user')
            if user_id:
                qs = qs.filter(user_id=user_id)
        elif not self.is_teacher(self.request):
            return qs.none()
        return apply_search(qs, self.request, self.search_fields)

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


class StudyGroupViewSet(RolePermissionMixin, viewsets.ModelViewSet):
    queryset = StudyGroup.objects.select_related('study_year', 'parent').all().order_by('id')
    serializer_class = StudyGroupSerializer
    search_fields = ['name', 'letter']

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated:
            return qs.none()
        if self.is_privileged(self.request):
            user_id = self.request.query_params.get('user')
            if user_id:
                qs = qs.filter(user_id=user_id)
        elif not self.is_teacher(self.request):
            return qs.none()
        qs = apply_search(qs, self.request, self.search_fields)
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


class WorkloadViewSet(RolePermissionMixin, viewsets.ModelViewSet):
    queryset = Workload.objects.select_related('study_group', 'teacher', 'subject').all().order_by('id')
    serializer_class = WorkloadSerializer
    search_fields = ['teacher__last_name', 'subject__title', 'study_group__name']
    filter_params = {
        'teacher': 'teacher_id',
        'subject': 'subject_id',
        'group': 'study_group_id',
    }

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated:
            return qs.none()
        if self.is_privileged(self.request):
            user_id = self.request.query_params.get('user')
            if user_id:
                qs = qs.filter(user_id=user_id)
        elif self.is_teacher(self.request):
            qs = qs.filter(teacher=self.request.user)
        else:
            return qs.none()
        for param, field in self.filter_params.items():
            value = self.request.query_params.get(param)
            if value:
                try:
                    qs = qs.filter(**{field: value})
                except (ValueError, TypeError):
                    continue
        qs = apply_search(qs, self.request, self.search_fields)
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


class LessonViewSet(RolePermissionMixin, viewsets.ModelViewSet):
    queryset = Lesson.objects.select_related('workload__study_group', 'workload__teacher', 'workload__subject', 'classroom', 'bell_schedule').all().order_by('id')
    serializer_class = LessonSerializer
    filter_params = {
        'week_day': 'week_day',
        'teacher': 'workload__teacher_id',
        'group': 'workload__study_group_id',
        'subject': 'workload__subject_id',
        'classroom': 'classroom_id',
    }
    search_fields = ['workload__teacher__last_name', 'workload__subject__title', 'classroom__number', 'workload__study_group__name']

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated:
            return qs.none()
        if self.is_privileged(self.request):
            user_id = self.request.query_params.get('user')
            if user_id:
                qs = qs.filter(user_id=user_id)
        elif self.is_teacher(self.request):
            qs = qs.filter(workload__teacher=self.request.user)
        else:
            return qs.none()
        for param, field in self.filter_params.items():
            value = self.request.query_params.get(param)
            if value:
                try:
                    qs = qs.filter(**{field: value})
                except (ValueError, TypeError):
                    continue
        return apply_search(qs, self.request, self.search_fields)

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