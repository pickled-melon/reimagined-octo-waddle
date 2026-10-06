from rest_framework import serializers

from schedule.models import *


class ProfileSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'user', 'role', 'role_display']


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
    class Meta:
        model = UserSubject
        fields = ['id', 'user', 'subject']


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

    class Meta:
        model = Workload
        fields = [
            'id', 'hours_count', 'study_group',
            'teacher', 'subject', 'difficulty_points',
        ]


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = [
            'id', 'week_day', 'is_test',
            'workload', 'classroom', 'bell_schedule',
        ]