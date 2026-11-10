from rest_framework import serializers
from django.db.models import Sum, Avg
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
        fields = ['id', 'user', 'username', 'user_display', 'last_name', 'first_name', 'patronymic_name', 'role', 'role_display']

    def get_user_display(self, obj):
        return user_full_name(obj.user)

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
    user_display = serializers.SerializerMethodField(read_only=True)
    weekly_lessons = serializers.SerializerMethodField()
    utilization_percent = serializers.SerializerMethodField()
    teachers_count = serializers.SerializerMethodField()
    groups_count = serializers.SerializerMethodField()
    subjects_count = serializers.SerializerMethodField()
    daily_load = serializers.SerializerMethodField()

    class Meta:
        model = Classroom
        fields = [
            'id', 'number', 'capacity', 'picture', 'user', 'user_display',
            'weekly_lessons', 'utilization_percent',
            'teachers_count', 'groups_count', 'subjects_count', 'daily_load',
        ]

    def get_user_display(self, obj):
        return user_full_name(obj.user)

    def get_weekly_lessons(self, obj):
        return getattr(obj, 'weekly_lessons', 0)

    def get_utilization_percent(self, obj):
        weekly = getattr(obj, 'weekly_lessons', 0)
        max_daily = self.context.get('max_daily_slots', 7)
        total = max_daily * 6
        if not total:
            return 0
        return round(weekly / total * 100, 1)

    def get_teachers_count(self, obj):
        return getattr(obj, 'teachers_count', 0)

    def get_groups_count(self, obj):
        return getattr(obj, 'groups_count', 0)

    def get_subjects_count(self, obj):
        return getattr(obj, 'subjects_count', 0)

    def get_daily_load(self, obj):
        from django.db.models import Count
        rows = Lesson.objects.filter(classroom=obj).values('week_day').annotate(c=Count('id'))
        by_day = {r['week_day']: r['c'] for r in rows}
        return {str(d): by_day.get(d, 0) for d in range(1, 7)}

    def create(self, validated_data):
        if 'request' in self.context:
            validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class SubjectPictureSerializer(serializers.ModelSerializer):
    user_display = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = SubjectPicture
        fields = ['id', 'image', 'subject', 'user', 'user_display']
    def get_user_display(self, obj):
        return user_full_name(obj.user)
    def create(self, validated_data):
        if 'request' in self.context:
            validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class SubjectSerializer(serializers.ModelSerializer):
    classrooms = serializers.PrimaryKeyRelatedField(many=True, queryset=Classroom.objects.all(), required=False)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    pictures = SubjectPictureSerializer(many=True, read_only=True)
    user_display = serializers.SerializerMethodField(read_only=True)
    
    total_hours = serializers.SerializerMethodField()
    avg_difficulty = serializers.SerializerMethodField()
    classrooms_count = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = [
            'id', 'title', 'type', 'type_display', 'classrooms', 'classrooms_count',
            'pictures', 'user', 'user_display', 'total_hours', 'avg_difficulty'
        ]

    def get_user_display(self, obj):
        return user_full_name(obj.user)

    def get_total_hours(self, obj):
        val = obj.workloads.aggregate(total=Sum('hours_count'))['total']
        return val or 0

    def get_avg_difficulty(self, obj):
        if obj.type == 'extracurricular':
            return None
        val = obj.difficulties.aggregate(avg=Avg('points'))['avg']
        return round(val, 1) if val else 0

    def get_classrooms_count(self, obj):
        return obj.classrooms.count()

    def create(self, validated_data):
        if 'request' in self.context:
            validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class StudyYearSerializer(serializers.ModelSerializer):
    user_display = serializers.SerializerMethodField(read_only=True)
    groups_count = serializers.SerializerMethodField()
    avg_students = serializers.SerializerMethodField()
    avg_difficulty = serializers.SerializerMethodField()

    class Meta:
        model = StudyYear
        fields = [
            'id', 'year', 'max_weekly_hours', 'max_daily_hours', 
            'groups_count', 'avg_students', 'avg_difficulty', 
            'user', 'user_display'
        ]

    def get_user_display(self, obj):
        return user_full_name(obj.user)

    def get_groups_count(self, obj):
        return obj.groups.filter(type='group').count()

    def get_avg_students(self, obj):
        val = obj.groups.aggregate(avg=Avg('students_count'))['avg']
        return round(val) if val else 0

    def get_avg_difficulty(self, obj):
        val = obj.difficulties.aggregate(avg=Avg('points'))['avg']
        return round(val, 1) if val else 0

    def create(self, validated_data):
        if 'request' in self.context:
            validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class BellScheduleSerializer(serializers.ModelSerializer):
    user_display = serializers.SerializerMethodField(read_only=True)
    duration_minutes = serializers.SerializerMethodField()
    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = BellSchedule
        fields = [
            'id', 'lesson_number', 'start_time', 'end_time', 
            'duration_minutes', 'lessons_count', 'user', 'user_display'
        ]

    def get_user_display(self, obj):
        return user_full_name(obj.user)

    def get_duration_minutes(self, obj):
        from datetime import datetime, date
        start = datetime.combine(date.today(), obj.start_time)
        end = datetime.combine(date.today(), obj.end_time)
        delta = end - start
        return int(delta.total_seconds() // 60)

    def get_lessons_count(self, obj):
        return Lesson.objects.filter(bell_schedule__start_time=obj.start_time).count()

    def create(self, validated_data):
        if 'request' in self.context:
            validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class UserSubjectSerializer(serializers.ModelSerializer):
    user_display = serializers.SerializerMethodField()
    subject_display = serializers.CharField(source='subject.title', read_only=True)
    creator_display = serializers.SerializerMethodField(read_only=True)
    
    assigned_hours = serializers.SerializerMethodField()
    assigned_groups = serializers.SerializerMethodField()

    class Meta:
        model = UserSubject
        fields = [
            'id', 'user', 'subject', 'user_display', 'subject_display', 
            'creator', 'creator_display', 'assigned_hours', 'assigned_groups'
        ]

    def get_user_display(self, obj):
        return user_full_name(obj.user)
        
    def get_creator_display(self, obj):
        return user_full_name(obj.creator)
        
    def get_assigned_hours(self, obj):
        val = obj.user.workloads.filter(subject=obj.subject).aggregate(total=Sum('hours_count'))['total']
        return val or 0
        
    def get_assigned_groups(self, obj):
        return obj.user.workloads.filter(subject=obj.subject).values('study_group').distinct().count()

    def create(self, validated_data):
        if 'request' in self.context:
            validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)

class DifficultySerializer(serializers.ModelSerializer):
    study_year_display = serializers.CharField(source='study_year.year', read_only=True)
    subject_display = serializers.CharField(source='subject.title', read_only=True)
    user_display = serializers.SerializerMethodField(read_only=True)
    category = serializers.SerializerMethodField()

    class Meta:
        model = Difficulty
        fields = ['id', 'study_year', 'subject', 'points', 'category', 'study_year_display', 'subject_display', 'user', 'user_display']

    def get_user_display(self, obj):
        return user_full_name(obj.user)

    def get_category(self, obj):
        if obj.points >= 8:
            return 'Высокая'
        if obj.points >= 5:
            return 'Средняя'
        return 'Низкая'

    def create(self, validated_data):
        if 'request' in self.context:
            validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class StudyGroupSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    user_display = serializers.SerializerMethodField(read_only=True)
    
    total_hours = serializers.SerializerMethodField()
    subgroups_count = serializers.SerializerMethodField()
    max_weekly_hours = serializers.IntegerField(source='study_year.max_weekly_hours', read_only=True)
    load_percent = serializers.SerializerMethodField()

    class Meta:
        model = StudyGroup
        fields = [
            'id', 'name', 'students_count', 'letter', 'type', 'type_display', 
            'subgroup_number', 'parent', 'study_year', 'user', 'user_display',
            'total_hours', 'subgroups_count', 'max_weekly_hours', 'load_percent'
        ]

    def get_user_display(self, obj):
        return user_full_name(obj.user)

    def get_total_hours(self, obj):
        val = getattr(obj, 'total_hours', None)
        if val is not None:
            return val
        return obj.workloads.aggregate(total=Sum('hours_count'))['total'] or 0

    def get_subgroups_count(self, obj):
        val = getattr(obj, 'subgroups_count', None)
        if val is not None:
            return val
        return obj.subgroups.count()

    def get_load_percent(self, obj):
        hours = self.get_total_hours(obj)
        max_h = obj.study_year.max_weekly_hours if obj.study_year else 0
        if not max_h:
            return 0
        return round(hours / max_h * 100, 1)

    def create(self, validated_data):
        if 'request' in self.context:
            validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class WorkloadSerializer(serializers.ModelSerializer):
    difficulty_points = serializers.IntegerField(read_only=True)
    study_group_display = serializers.CharField(source='study_group.name', read_only=True)
    teacher_display = serializers.SerializerMethodField()
    subject_display = serializers.CharField(source='subject.title', read_only=True)
    user_display = serializers.SerializerMethodField(read_only=True)
    
    distributed_lessons = serializers.SerializerMethodField()
    unassigned_hours = serializers.SerializerMethodField()
    progress_percent = serializers.SerializerMethodField()

    class Meta:
        model = Workload
        fields = [
            'id', 'hours_count', 'study_group', 'teacher', 'subject', 
            'difficulty_points', 'study_group_display', 'teacher_display', 'subject_display', 
            'user', 'user_display', 'distributed_lessons', 'unassigned_hours', 'progress_percent'
        ]

    def get_teacher_display(self, obj):
        return user_full_name(obj.teacher)

    def get_user_display(self, obj):
        return user_full_name(obj.user)

    def get_distributed_lessons(self, obj):
        return getattr(obj, 'distributed_lessons', 0)

    def get_unassigned_hours(self, obj):
        dist = self.get_distributed_lessons(obj)
        return max(0, obj.hours_count - dist)

    def get_progress_percent(self, obj):
        if not obj.hours_count:
            return 0
        dist = self.get_distributed_lessons(obj)
        return min(100, round(dist / obj.hours_count * 100, 1))

    def create(self, validated_data):
        if 'request' in self.context:
            validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class LessonSerializer(serializers.ModelSerializer):
    classroom_display = serializers.CharField(source='classroom.number', read_only=True)
    bell_schedule_display = serializers.SerializerMethodField()
    workload_display = serializers.SerializerMethodField()
    teacher_display = serializers.SerializerMethodField()
    week_day_display = serializers.CharField(source='get_week_day_display', read_only=True)
    user_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Lesson
        fields = [
            'id', 'week_day', 'week_day_display', 'is_test', 'workload', 'classroom', 
            'bell_schedule', 'workload_display', 'teacher_display', 'classroom_display', 
            'bell_schedule_display', 'user', 'user_display'
        ]

    def get_workload_display(self, obj):
        w = obj.workload
        if w is None:
            return '-'
        return f"{w.study_group.name} - {w.subject.title}"

    def get_teacher_display(self, obj):
        if obj.workload is None:
            return '-'
        return user_full_name(obj.workload.teacher)

    def get_bell_schedule_display(self, obj):
        b = obj.bell_schedule
        if b is None:
            return '-'
        time_str = f"{b.start_time:%H:%M}–{b.end_time:%H:%M}"
        if b.lesson_number <= 8:
            return f"{b.lesson_number}-й урок ({time_str})"
        return time_str

    def get_user_display(self, obj):
        return user_full_name(obj.user)

    def create(self, validated_data):
        if 'request' in self.context:
            validated_data['user'] = self.context['request'].user
        return super().create(validated_data)