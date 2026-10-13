from rest_framework import serializers

from schedule.models import *


def user_full_name(user):
    if user is None:
        return '-'
    profile = getattr(user, 'profile', None)
    patronymic = profile.patronymic_name if profile else ''
    parts = [user.last_name, user.first_name, patronymic]
    full = ' '.join(p for p in parts if p).strip()
    return full or user.username


class ProfileSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    user_display = serializers.SerializerMethodField()
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Profile
        fields = [
            'id', 'user', 'username', 'user_display',
            'last_name', 'first_name', 'patronymic_name',
            'role', 'role_display',
        ]

    def get_user_display(self, obj):
        if obj.user is None:
            return '-'
        parts = [obj.user.last_name, obj.user.first_name, obj.patronymic_name]
        full = ' '.join(p for p in parts if p).strip()
        return full or obj.user.username

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.user:
            data['first_name'] = instance.user.first_name
            data['last_name'] = instance.user.last_name
        return data

    def update(self, instance, validated_data):
        first_name = validated_data.pop('first_name', None)
        last_name = validated_data.pop('last_name', None)
        if instance.user:
            changed = False
            if first_name is not None and instance.user.first_name != first_name:
                instance.user.first_name = first_name
                changed = True
            if last_name is not None and instance.user.last_name != last_name:
                instance.user.last_name = last_name
                changed = True
            if changed:
                instance.user.save()
        return super().update(instance, validated_data)


class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = ['id', 'number', 'capacity', 'picture']


class SubjectSerializer(serializers.ModelSerializer):
    classrooms = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Classroom.objects.all(), required=False
    )
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Subject
        fields = ['id', 'title', 'type', 'type_display', 'classrooms', 'picture']


class StudyYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyYear
        fields = ['id', 'year', 'max_weekly_hours', 'max_daily_hours']


class BellScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = BellSchedule
        fields = ['id', 'lesson_number', 'start_time', 'end_time']


class UserSubjectSerializer(serializers.ModelSerializer):
    user_display = serializers.SerializerMethodField()
    subject_display = serializers.CharField(source='subject.title', read_only=True)

    class Meta:
        model = UserSubject
        fields = ['id', 'user', 'subject', 'user_display', 'subject_display']

    def get_user_display(self, obj):
        return user_full_name(obj.user)


class DifficultySerializer(serializers.ModelSerializer):
    study_year_display = serializers.CharField(source='study_year.year', read_only=True)
    subject_display = serializers.CharField(source='subject.title', read_only=True)

    class Meta:
        model = Difficulty
        fields = [
            'id', 'study_year', 'subject', 'points',
            'study_year_display', 'subject_display',
        ]


class StudyGroupSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = StudyGroup
        fields = [
            'id', 'name', 'students_count', 'letter',
            'type', 'type_display', 'subgroup_number',
            'parent', 'study_year',
        ]


class WorkloadSerializer(serializers.ModelSerializer):
    difficulty_points = serializers.IntegerField(read_only=True)
    study_group_display = serializers.CharField(source='study_group.name', read_only=True)
    teacher_display = serializers.SerializerMethodField()
    subject_display = serializers.CharField(source='subject.title', read_only=True)

    class Meta:
        model = Workload
        fields = [
            'id', 'hours_count', 'study_group', 'teacher', 'subject',
            'difficulty_points',
            'study_group_display', 'teacher_display', 'subject_display',
        ]

    def get_teacher_display(self, obj):
        return user_full_name(obj.teacher)


class LessonSerializer(serializers.ModelSerializer):
    classroom_display = serializers.CharField(source='classroom.number', read_only=True)
    bell_schedule_display = serializers.SerializerMethodField()
    workload_display = serializers.SerializerMethodField()
    week_day_display = serializers.CharField(source='get_week_day_display', read_only=True)

    class Meta:
        model = Lesson
        fields = [
            'id', 'week_day', 'week_day_display', 'is_test',
            'workload', 'classroom', 'bell_schedule',
            'workload_display', 'classroom_display', 'bell_schedule_display',
        ]

    def get_workload_display(self, obj):
        w = obj.workload
        if w is None:
            return '-'
        return f"{w.study_group.name} - {w.subject.title}"

    def get_bell_schedule_display(self, obj):
        b = obj.bell_schedule
        if b is None:
            return '-'
        return f"{b.lesson_number}-й урок ({b.start_time:%H:%M}–{b.end_time:%H:%M})"