from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from model_bakery import baker
from model_bakery.recipe import seq

from schedule.models import *

# Create your tests here.
# https://vkvideo.ru/video-201762718_456239086?t=4s
# https://django.tealeaf.su/tasks/1835.html
class ClassroomsViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_list(self):
        classroom = Classroom.objects.create(
            number = "55",
            capacity = 15
        )

        r = self.client.get("/api/classrooms/")
        data = r.json()
        print(data)

        assert classroom.number == data[0]["number"]
        assert classroom.capacity == data[0]["capacity"]
        assert len(data) == 1

    def test_create_classroom(self):
        classroom = baker.make("schedule.Classroom")

        r = self.client.get("/api/classrooms/")
        data = r.json()

        assert classroom.number == data[0]["number"]
        assert classroom.id == data[0]["id"]
        assert classroom.capacity == data[0]["capacity"]
        assert len(data) == 1

    def test_delete_classroom(self):
        classrooms = baker.make("Classroom", 10)
        r = self.client.get("/api/classrooms/")
        data = r.json()
        assert len(data) == 10

        classroom_id_to_delete = classrooms[3].id
        self.client.delete(f"/api/classrooms/{classroom_id_to_delete}/")

        r = self.client.get("/api/classrooms/")
        data = r.json()
        assert len(data) == 9

        assert classroom_id_to_delete not in [i["id"] for i in data]

    def test_update_classroom(self):
        classrooms = baker.make("Classroom", 10)
        classroom: Classroom = classrooms[2]

        r = self.client.get(f"/api/classrooms/{classroom.id}/")
        data = r.json()
        assert data['number'] == classroom.number

        r = self.client.patch(f"/api/classrooms/{classroom.id}/", {
            "number": "14"
        })
        assert r.status_code == 200

        r = self.client.get(f"/api/classrooms/{classroom.id}/")
        data = r.json()
        assert data["number"] == "14"

        classroom.refresh_from_db()
        assert data["number"] == classroom.number


class ProfileViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_list(self):
        user = baker.make(User)
        r = self.client.get('/api/profiles/')
        data = r.json()

        assert len(data) == 1
        assert data[0]['user'] == user.id
        assert data[0]['role'] == Profile.Role.UNDEFINED
        assert data[0]['role_display'] == 'Не определена'

    def test_update_profile(self):
        user = baker.make(User)
        profile = user.profile

        r = self.client.patch(f'/api/profiles/{profile.id}/', {
            'role': Profile.Role.METHODIST,
        }, format='json')

        assert r.status_code == 200

        profile.refresh_from_db()
        assert profile.role == Profile.Role.METHODIST

    def test_delete_profile(self):
        user = baker.make(User)
        profile_id = user.profile.id

        r = self.client.delete(f'/api/profiles/{profile_id}/')

        assert r.status_code == 204
        assert not Profile.objects.filter(id=profile_id).exists()


class SubjectViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_list(self):
        subject = baker.make('schedule.Subject')
        r = self.client.get('/api/subjects/')
        data = r.json()

        assert len(data) == 1
        assert data[0]['title'] == subject.title
        assert data[0]['type'] == subject.type

    def test_create_subject(self):
        r = self.client.post('/api/subjects/', {
            'title': 'Физика',
            'type': 'classroom',
        }, format='json')

        assert r.status_code == 201
        assert Subject.objects.filter(title='Физика').exists()

    def test_update_subject(self):
        subject = baker.make('schedule.Subject')
        r = self.client.patch(f'/api/subjects/{subject.id}/', {
            'title': 'Алгебра',
        }, format='json')

        assert r.status_code == 200

        subject.refresh_from_db()
        assert subject.title == 'Алгебра'

    def test_delete_subject(self):
        subjects = baker.make('schedule.Subject', 5, title=seq('subject-'))
        r = self.client.get('/api/subjects/')
        assert len(r.json()) == 5

        id_to_delete = subjects[2].id
        self.client.delete(f'/api/subjects/{id_to_delete}/')
        r = self.client.get('/api/subjects/')
        data = r.json()

        assert len(data) == 4
        assert id_to_delete not in [i['id'] for i in data]


class StudyYearViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_list(self):
        year = baker.make('schedule.StudyYear',
                          year=7, max_weekly_hours=32, max_daily_hours=7)
        r = self.client.get('/api/study-years/')
        data = r.json()

        assert len(data) == 1
        assert data[0]['year'] == year.year
        assert data[0]['max_weekly_hours'] == year.max_weekly_hours
        assert data[0]['max_daily_hours'] == year.max_daily_hours

    def test_create_study_year(self):
        r = self.client.post('/api/study-years/', {
            'year': 5,
            'max_weekly_hours': 29,
            'max_daily_hours': 6,
        }, format='json')

        assert r.status_code == 201
        assert StudyYear.objects.filter(year=5).exists()

    def test_update_study_year(self):
        year = baker.make('schedule.StudyYear',
                          year=7, max_weekly_hours=32, max_daily_hours=7)
        r = self.client.patch(f'/api/study-years/{year.id}/', {
            'max_weekly_hours': 35,
        }, format='json')

        assert r.status_code == 200
        year.refresh_from_db()
        assert year.max_weekly_hours == 35

    def test_delete_study_year(self):
        years = baker.make('schedule.StudyYear', 5,
                           year=seq(1), max_weekly_hours=30, max_daily_hours=6)
        r = self.client.get('/api/study-years/')

        assert len(r.json()) == 5

        id_to_delete = years[2].id
        self.client.delete(f'/api/study-years/{id_to_delete}/')
        r = self.client.get('/api/study-years/')
        data = r.json()

        assert len(data) == 4
        assert id_to_delete not in [i['id'] for i in data]


class BellScheduleViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_list(self):
        bell = baker.make('schedule.BellSchedule',
                          lesson_number=1, start_time='08:00', end_time='08:45')
        r = self.client.get('/api/bell-schedules/')
        data = r.json()

        assert len(data) == 1
        assert data[0]['lesson_number'] == bell.lesson_number
        assert data[0]['start_time'] == '08:00:00'
        assert data[0]['end_time'] == '08:45:00'

    def test_create_bell_schedule(self):
        r = self.client.post('/api/bell-schedules/', {
            'lesson_number': 2,
            'start_time': '09:00:00',
            'end_time': '09:45:00',
        }, format='json')

        assert r.status_code == 201
        assert BellSchedule.objects.filter(lesson_number=2).exists()

    def test_update_bell_schedule(self):
        bell = baker.make('schedule.BellSchedule',
                          lesson_number=1, start_time='08:00', end_time='08:45')
        
        r = self.client.patch(f'/api/bell-schedules/{bell.id}/', {
            'start_time': '08:15:00',
        }, format='json')

        assert r.status_code == 200

        bell.refresh_from_db()
        assert bell.start_time.strftime('%H:%M') == '08:15'

    def test_delete_bell_schedule(self):
        bells = baker.make('schedule.BellSchedule', 5,
                           lesson_number=seq(1),
                           start_time='08:00', end_time='08:45')
        r = self.client.get('/api/bell-schedules/')

        assert len(r.json()) == 5

        id_to_delete = bells[2].id
        self.client.delete(f'/api/bell-schedules/{id_to_delete}/')
        r = self.client.get('/api/bell-schedules/')
        data = r.json()

        assert len(data) == 4
        assert id_to_delete not in [i['id'] for i in data]


class UserSubjectViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_list(self):
        user = baker.make(User)
        subject = baker.make('schedule.Subject')
        us = baker.make('schedule.UserSubject', user=user, subject=subject)

        r = self.client.get('/api/user-subjects/')
        data = r.json()

        assert len(data) == 1
        assert data[0]['user'] == us.user_id
        assert data[0]['subject'] == us.subject_id

    def test_create_user_subject(self):
        user = baker.make(User)
        subject = baker.make('schedule.Subject')

        r = self.client.post('/api/user-subjects/', {
            'user': user.id,
            'subject': subject.id,
        }, format='json')

        assert r.status_code == 201
        assert UserSubject.objects.count() == 1

    def test_update_user_subject(self):
        user1 = baker.make(User)
        user2 = baker.make(User)
        subject = baker.make('schedule.Subject')

        us = baker.make('schedule.UserSubject', user=user1, subject=subject)
        r = self.client.patch(f'/api/user-subjects/{us.id}/', {
            'user': user2.id,
        }, format='json')

        assert r.status_code == 200
        
        us.refresh_from_db()
        assert us.user == user2

    def test_delete_user_subject(self):
        subject = baker.make('schedule.Subject')
        users = baker.make(User, 5, username=seq('user-'))
        items = [
            baker.make('schedule.UserSubject', user=u, subject=subject)
            for u in users
        ]

        r = self.client.get('/api/user-subjects/')
        assert len(r.json()) == 5

        id_to_delete = items[2].id
        self.client.delete(f'/api/user-subjects/{id_to_delete}/')
        r = self.client.get('/api/user-subjects/')
        data = r.json()

        assert len(data) == 4
        assert id_to_delete not in [i['id'] for i in data]


class DifficultyViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_list(self):
        year = baker.make('schedule.StudyYear',
                          year=7, max_weekly_hours=32, max_daily_hours=7)
        subject = baker.make('schedule.Subject')
        d = baker.make('schedule.Difficulty',
                       study_year=year, subject=subject, points=8)
        r = self.client.get('/api/difficulties/')

        data = r.json()

        assert len(data) == 1
        assert data[0]['study_year'] == d.study_year_id
        assert data[0]['subject'] == d.subject_id
        assert data[0]['points'] == 8

    def test_create_difficulty(self):
        year = baker.make('schedule.StudyYear',
                          year=7, max_weekly_hours=32, max_daily_hours=7)
        subject = baker.make('schedule.Subject')

        r = self.client.post('/api/difficulties/', {
            'study_year': year.id,
            'subject': subject.id,
            'points': 10,
        }, format='json')

        assert r.status_code == 201
        assert Difficulty.objects.count() == 1

    def test_update_difficulty(self):
        year = baker.make('schedule.StudyYear',
                          year=7, max_weekly_hours=32, max_daily_hours=7)
        subject = baker.make('schedule.Subject')
        d = baker.make('schedule.Difficulty',
                       study_year=year, subject=subject, points=8)
        
        r = self.client.patch(f'/api/difficulties/{d.id}/', {
            'points': 12,
        }, format='json')

        assert r.status_code == 200

        d.refresh_from_db()
        assert d.points == 12

    def test_delete_difficulty(self):
        year = baker.make('schedule.StudyYear',
                          year=7, max_weekly_hours=32, max_daily_hours=7)
        subjects = baker.make('schedule.Subject', 5, title=seq('subject-'))
        
        difficulties = [
            baker.make('schedule.Difficulty',
                       study_year=year, subject=s, points=i + 1)
            for i, s in enumerate(subjects)
        ]

        r = self.client.get('/api/difficulties/')

        assert len(r.json()) == 5

        id_to_delete = difficulties[2].id
        self.client.delete(f'/api/difficulties/{id_to_delete}/')
        r = self.client.get('/api/difficulties/')
        data = r.json()

        assert len(data) == 4
        assert id_to_delete not in [i['id'] for i in data]


class StudyGroupViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.year = baker.make('schedule.StudyYear',
                               year=7, max_weekly_hours=32, max_daily_hours=7)

    def test_get_list(self):
        group = baker.make('schedule.StudyGroup',
                           study_year=self.year, letter='А', type='group')
        
        r = self.client.get('/api/study-groups/')
        data = r.json()

        assert len(data) == 1
        assert data[0]['name'] == '7А'
        assert data[0]['students_count'] == group.students_count
        assert data[0]['study_year'] == self.year.id

    def test_create_study_group(self):
        r = self.client.post('/api/study-groups/', {
            'students_count': 28,
            'letter': 'Б',
            'type': 'group',
            'study_year': self.year.id,
        }, format='json')

        assert r.status_code == 201
        assert StudyGroup.objects.filter(name='7Б').exists()

    def test_create_subgroup(self):
        parent = baker.make('schedule.StudyGroup',
                            study_year=self.year, letter='А', type='group')
        
        r = self.client.post('/api/study-groups/', {
            'students_count': 14,
            'type': 'subgroup',
            'subgroup_number': 'first',
            'parent': parent.id,
            'study_year': self.year.id,
        }, format='json')

        assert r.status_code == 201
        assert StudyGroup.objects.filter(name='7А-1').exists()

    def test_update_study_group(self):
        group = baker.make('schedule.StudyGroup',
                           study_year=self.year, letter='А', type='group')
        r = self.client.patch(f'/api/study-groups/{group.id}/', {
            'students_count': 30,
        }, format='json')

        assert r.status_code == 200

        group.refresh_from_db()
        assert group.students_count == 30

    def test_delete_study_group(self):
        letters = ['А', 'Б', 'В', 'Г', 'Д']
        groups = [
            baker.make('schedule.StudyGroup',
                       study_year=self.year, letter=letter, type='group')
            for letter in letters
        ]

        r = self.client.get('/api/study-groups/')

        assert len(r.json()) == 5

        id_to_delete = groups[2].id
        self.client.delete(f'/api/study-groups/{id_to_delete}/')
        r = self.client.get('/api/study-groups/')
        data = r.json()

        assert len(data) == 4
        assert id_to_delete not in [i['id'] for i in data]


class WorkloadViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.year = baker.make('schedule.StudyYear',
                               year=7, max_weekly_hours=32, max_daily_hours=7)
        self.group = baker.make('schedule.StudyGroup',
                                study_year=self.year, letter='А', type='group')
        self.subject = baker.make('schedule.Subject')
        self.teacher = baker.make(User)

    def test_get_list(self):
        w = baker.make('schedule.Workload',
                       study_group=self.group, teacher=self.teacher,
                       subject=self.subject, hours_count=5)
        r = self.client.get('/api/workloads/')

        data = r.json()

        assert len(data) == 1
        assert data[0]['hours_count'] == 5
        assert data[0]['study_group'] == self.group.id
        assert data[0]['teacher'] == self.teacher.id
        assert data[0]['subject'] == self.subject.id

    def test_create_workload(self):
        r = self.client.post('/api/workloads/', {
            'hours_count': 5,
            'study_group': self.group.id,
            'teacher': self.teacher.id,
            'subject': self.subject.id,
        }, format='json')

        assert r.status_code == 201
        assert Workload.objects.count() == 1

    def test_update_workload(self):
        w = baker.make('schedule.Workload',
                       study_group=self.group, teacher=self.teacher,
                       subject=self.subject, hours_count=5)
        r = self.client.patch(f'/api/workloads/{w.id}/', {
            'hours_count': 6,
        }, format='json')

        assert r.status_code == 200

        w.refresh_from_db()
        assert w.hours_count == 6

    def test_delete_workload(self):
        subjects = baker.make('schedule.Subject', 5, title=seq('subject-'))
        workloads = [
            baker.make('schedule.Workload',
                       study_group=self.group, teacher=self.teacher, subject=s)
            for s in subjects
        ]

        r = self.client.get('/api/workloads/')

        assert len(r.json()) == 5

        id_to_delete = workloads[2].id
        self.client.delete(f'/api/workloads/{id_to_delete}/')
        r = self.client.get('/api/workloads/')
        data = r.json()

        assert len(data) == 4
        assert id_to_delete not in [i['id'] for i in data]


class LessonViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.year = baker.make('schedule.StudyYear',
                               year=7, max_weekly_hours=32, max_daily_hours=7)
        self.group = baker.make('schedule.StudyGroup',
                                study_year=self.year, letter='А', type='group')
        self.subject = baker.make('schedule.Subject')
        self.teacher = baker.make(User)
        self.workload = baker.make('schedule.Workload',
                                   study_group=self.group, teacher=self.teacher,
                                   subject=self.subject)
        self.classroom = baker.make('schedule.Classroom')
        self.bell = baker.make('schedule.BellSchedule', lesson_number=1)

    def test_get_list(self):
        lesson = baker.make('schedule.Lesson',
                            workload=self.workload, classroom=self.classroom,
                            bell_schedule=self.bell, week_day=1, is_test=False)
        r = self.client.get('/api/lessons/')

        data = r.json()

        assert len(data) == 1
        assert data[0]['week_day'] == 1
        assert data[0]['is_test'] is False
        assert data[0]['workload'] == self.workload.id
        assert data[0]['classroom'] == self.classroom.id
        assert data[0]['bell_schedule'] == self.bell.id

    def test_create_lesson(self):
        r = self.client.post('/api/lessons/', {
            'week_day': 2,
            'is_test': True,
            'workload': self.workload.id,
            'classroom': self.classroom.id,
            'bell_schedule': self.bell.id,
        }, format='json')

        assert r.status_code == 201
        assert Lesson.objects.count() == 1

        lesson = Lesson.objects.first()

        assert lesson.week_day == 2
        assert lesson.is_test is True

    def test_update_lesson(self):
        lesson = baker.make('schedule.Lesson',
                            workload=self.workload, classroom=self.classroom,
                            bell_schedule=self.bell, week_day=1, is_test=False)
        r = self.client.patch(f'/api/lessons/{lesson.id}/', {
            'is_test': True,
        }, format='json')

        assert r.status_code == 200

        lesson.refresh_from_db()
        assert lesson.is_test is True

    def test_delete_lesson(self):
        bells = baker.make('schedule.BellSchedule', 5,
                           lesson_number=seq(1),
                           start_time='08:00', end_time='08:45')
        lessons = [
            baker.make('schedule.Lesson',
                       workload=self.workload, classroom=self.classroom,
                       bell_schedule=b, week_day=1, is_test=False)
            for b in bells
        ]

        r = self.client.get('/api/lessons/')

        assert len(r.json()) == 5

        id_to_delete = lessons[2].id
        self.client.delete(f'/api/lessons/{id_to_delete}/')
        r = self.client.get('/api/lessons/')
        data = r.json()

        assert len(data) == 4
        assert id_to_delete not in [i['id'] for i in data]
