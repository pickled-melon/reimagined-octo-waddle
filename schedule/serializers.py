from rest_framework import serializers

from schedule.models import *


class ProfileSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    user_display = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['id', 'user', 'user_display', 'role', 'role_display']
    
    def get_user_display(self, obj):
        if obj.user is None:
            return '-'
        
        full = obj.user.get_full_name().strip()
        return full or obj.user.username


class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = ['id', 'number', 'capacity']


class SubjectSerializer(serializers.ModelSerializer):
    classrooms = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Classroom.objects.all(), required=False
    )

    class Meta:
        model = Subject
        fields = ['id', 'title', 'type', 'classrooms']


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
        if obj.user is None:
            return '-'
        full = obj.user.get_full_name().strip()
        return full or obj.user.username


class DifficultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Difficulty
        fields = ['id', 'study_year', 'subject', 'points']


class StudyGroupSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)

    class Meta:
        model = StudyGroup
        fields = [
            'id', 'name', 'students_count', 'letter', 'type',
            'subgroup_number', 'parent', 'study_year',
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
        if obj.teacher is None:
            return '-'
        full = obj.teacher.get_full_name().strip()
        return full or obj.teacher.username


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