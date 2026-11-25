import os
import random
import re
from datetime import time, timedelta, datetime, date

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from faker import Faker
from PIL import Image, ImageDraw
from tqdm import tqdm
from transliterate import translit

from schedule.models import (
    Profile, Classroom, Subject, SubjectPicture, StudyYear,
    BellSchedule, UserSubject, Difficulty, StudyGroup,
    Workload, Lesson,
)


class Command(BaseCommand):
    def handle(self, *args, **options):
        random.seed(42)
        fake = Faker('ru_RU')

        self.stdout.write('Генерация пользователей...')
        users = self._create_users(fake)

        self.stdout.write('Генерация годов обучения...')
        study_years = self._create_study_years(users)

        self.stdout.write('Генерация дисциплин...')
        subjects = self._create_subjects(users)

        self.stdout.write('Генерация кабинетов...')
        classrooms = self._create_classrooms(users)

        self.stdout.write('Генерация расписания звонков...')
        bells = self._create_bell_schedules(users)

        self.stdout.write('Генерация учебных групп...')
        groups = self._create_study_groups(users, study_years)

        self.stdout.write('Генерация M2M связей предмет-группы...')
        self._create_subject_groups(subjects, groups, study_years)

        self.stdout.write('Генерация дисциплин учителей...')
        user_subjects = self._create_user_subjects(users, subjects)

        self.stdout.write('Генерация трудностей...')
        self._create_difficulties(users, study_years, subjects)

        self.stdout.write('Генерация нагрузок...')
        workloads = self._create_workloads(users, groups, user_subjects, study_years)

        self.stdout.write('Генерация занятий...')
        self._create_lessons(users, workloads, classrooms, bells)

        self.stdout.write(self.style.SUCCESS('Готово'))

    def _create_users(self, fake):
        users = []
        existing_usernames = set(User.objects.values_list('username', flat=True))

        admin = User.objects.create_superuser(
            username='admin',
            email='admin@school.gosuslugi.ru',
            first_name='Тыжпрограммист',
            last_name='Сисадминов',
            password='admin123'
        )
        users.append(admin)
        existing_usernames.add('admin')

        for role_value, prefix in [(Profile.Role.METHODIST, 'methodist'), (Profile.Role.HEAD_TEACHER, 'headteacher')]:
            is_male = random.choice([True, False])
            last_name = fake.last_name_male() if is_male else fake.last_name_female()
            first_name = fake.first_name_male() if is_male else fake.first_name_female()
            patronymic = fake.middle_name_male() if is_male else fake.middle_name_female()

            fio = f"{last_name} {first_name} {patronymic}"
            fio_translited = translit(fio, 'ru', reversed=True).lower()
            fio_translited = re.sub(r"['\-]", "", fio_translited)
            fio_translited = fio_translited.replace(" ", "_")
            username = f"{prefix}_{fio_translited}"

            while username in existing_usernames:
                username = f"{prefix}_{fio_translited}_{random.randint(1000, 9999)}"

            existing_usernames.add(username)

            user = User.objects.create_user(
                username=username,
                email=f"{username}@school.gosuslugi.ru",
                first_name=first_name,
                last_name=last_name,
                password="password123"
            )
            user.profile.role = role_value
            user.profile.patronymic_name = patronymic
            user.profile.save()
            
            if role_value == Profile.Role.HEAD_TEACHER:
                user.is_superuser = True
                user.is_staff = True
                user.save()
                
            users.append(user)

        for _ in tqdm(range(97)):
            is_male = random.choice([True, False])
            last_name = fake.last_name_male() if is_male else fake.last_name_female()
            first_name = fake.first_name_male() if is_male else fake.first_name_female()
            patronymic = fake.middle_name_male() if is_male else fake.middle_name_female()

            fio = f"{last_name} {first_name} {patronymic}"
            fio_translited = translit(fio, 'ru', reversed=True).lower()
            fio_translited = re.sub(r"['\-]", "", fio_translited)
            fio_translited = fio_translited.replace(" ", "_")
            username = f"teacher_{fio_translited}"

            attempts = 0
            while username in existing_usernames and attempts < 100:
                username = f"teacher_{fio_translited}_{random.randint(1000, 9999)}"
                attempts += 1

            if username in existing_usernames:
                continue

            existing_usernames.add(username)

            user = User.objects.create_user(
                username=username,
                email=f"{username}@school.ru",
                first_name=first_name,
                last_name=last_name,
                password="password123"
            )
            user.profile.role = Profile.Role.TEACHER
            user.profile.patronymic_name = patronymic
            user.profile.save()
            users.append(user)

        return users

    def _create_study_years(self, users):
        study_years = []
        max_daily = {1: 4, 2: 5, 3: 5, 4: 5, 5: 6, 6: 6, 7: 7, 8: 7, 9: 7, 10: 7, 11: 7}
        max_weekly = {1: 20, 2: 20, 3: 23, 4: 23, 5: 26, 6: 26, 7: 29, 8: 29, 9: 29, 10: 30, 11: 30}

        for year in range(1, 12):
            sy = StudyYear.objects.create(
                year=year,
                max_daily_hours=max_daily[year],
                max_weekly_hours=max_weekly[year],
                user=random.choice(users)
            )
            study_years.append(sy)

        return study_years

    def _create_subjects(self, users):
        subject_titles = [
            'Математика', 'Русский язык', 'Литературное чтение', 'Литература',
            'Окружающий мир', 'Природоведение', 'История', 'Обществознание',
            'География', 'Биология', 'Физика', 'Химия', 'Алгебра', 'Геометрия',
            'Иностранный язык', 'Информатика и ИКТ', 'Изобразительное искусство',
            'Музыка', 'Мировая художественная культура', 'Технология', 'Черчение',
            'Основы безопасности жизнедеятельности', 'Физическая культура',
            'Астрономия', 'Индивидуальный проект'
        ]

        subjects = []
        for title in subject_titles:
            subj = Subject.objects.create(
                title=title,
                type='classroom',
                user=random.choice(users)
            )
            subjects.append(subj)

        return subjects

    def _create_classrooms(self, users):
        classrooms = []
        room_numbers = [
            101, 102, 103, 104, 105, 106,
            201, 202, 203, 204, 205, 206,
            301, 302, 303, 304, 305, 306, 307, 308,
            401, 402, 403, 404, 405, 406,
            501, 502, 503, 504,
            601, 602, 603, 604, 605, 606, 607, 608, 609, 610
        ]

        for number in room_numbers:
            room = Classroom.objects.create(
                number=f"{number}",
                capacity=random.randint(15, 35),
                user=random.choice(users)
            )
            classrooms.append(room)

        return classrooms

    def _create_bell_schedules(self, users):
        bells = []
        schedule = [
            (8, 0, 45),
            (8, 55, 45),
            (9, 50, 45),
            (10, 55, 45),
            (11, 50, 45),
            (12, 45, 45),
            (13, 40, 45),
            (14, 35, 45),
        ]

        for i, (hour, minute, duration) in enumerate(schedule, 1):
            start = time(hour=hour, minute=minute)
            end_time = (datetime.combine(date.today(), start) + timedelta(minutes=duration)).time()
            bell = BellSchedule.objects.create(
                lesson_number=i,
                start_time=start,
                end_time=end_time,
                user=random.choice(users)
            )
            bells.append(bell)

        return bells

    def _create_study_groups(self, users, study_years):
        groups = []

        for year in study_years:
            if year.year == 1:
                letters = ['А']
            else:
                letters = ['А', 'Б']

            for letter in letters:
                group = StudyGroup.objects.create(
                    students_count=random.randint(20, 28),
                    letter=letter,
                    type='group',
                    study_year=year,
                    enrollment_year=2026 - year.year + 1,
                    user=random.choice(users)
                )
                groups.append(group)

        return groups

    def _create_subject_groups(self, subjects, groups, study_years):
        subject_ranges = {
            'Математика': (1, 6),
            'Русский язык': (1, 11),
            'Литературное чтение': (1, 4),
            'Литература': (5, 11),
            'Окружающий мир': (1, 4),
            'Природоведение': (5, 5),
            'История': (5, 11),
            'Обществознание': (5, 11),
            'География': (5, 11),
            'Биология': (5, 11),
            'Физика': (7, 11),
            'Химия': (8, 11),
            'Алгебра': (7, 11),
            'Геометрия': (7, 11),
            'Иностранный язык': (2, 11),
            'Информатика и ИКТ': (5, 11),
            'Изобразительное искусство': (1, 7),
            'Музыка': (1, 7),
            'Мировая художественная культура': (8, 9),
            'Технология': (1, 9),
            'Черчение': (8, 9),
            'Основы безопасности жизнедеятельности': (1, 11),
            'Физическая культура': (1, 11),
            'Астрономия': (11, 11),
            'Индивидуальный проект': (10, 11),
        }

        for subject in subjects:
            if subject.title in subject_ranges:
                min_year, max_year = subject_ranges[subject.title]
                valid_groups = [
                    g for g in groups
                    if min_year <= g.study_year.year <= max_year
                ]
                subject.groups.set(valid_groups)

    def _create_user_subjects(self, users, subjects):
        user_subjects = []
        combos = set()

        for user in tqdm(users):
            if user.profile.role in [Profile.Role.METHODIST, Profile.Role.HEAD_TEACHER]:
                continue

            num_subjects = random.choices([1, 2, 3], weights=[0.6, 0.35, 0.05])[0]
            chosen_subjects = random.sample(subjects, min(num_subjects, len(subjects)))

            for subject in chosen_subjects:
                key = (user.id, subject.id)
                if key in combos:
                    continue

                combos.add(key)
                us = UserSubject.objects.create(
                    user=user,
                    subject=subject,
                    creator=user
                )
                user_subjects.append(us)

        return user_subjects

    def _create_difficulties(self, users, study_years, subjects):
        difficulty_table = {
            'Математика': {1: 8, 2: 9, 3: 10, 4: 11, 5: 10, 6: 13},
            'Русский язык': {1: 7, 2: 8, 3: 9, 4: 10, 5: 8, 6: 12, 7: 11, 8: 7, 9: 6, 10: 9, 11: 9},
            'Литературное чтение': {1: 5, 2: 6, 3: 7, 4: 8},
            'Литература': {5: 4, 6: 6, 7: 4, 8: 4, 9: 7, 10: 8, 11: 8},
            'Окружающий мир': {1: 4, 2: 5, 3: 6, 4: 7},
            'Природоведение': {5: 7, 6: 8},
            'История': {5: 5, 6: 8, 7: 6, 8: 8, 9: 10, 10: 5, 11: 5},
            'Обществознание': {5: 6, 6: 9, 7: 9, 8: 5, 9: 5, 10: 5, 11: 5},
            'География': {5: 0, 6: 7, 7: 6, 8: 6, 9: 5, 10: 3, 11: 3},
            'Биология': {5: 10, 6: 8, 7: 7, 8: 7, 9: 7, 10: 7, 11: 7},
            'Физика': {7: 8, 8: 9, 9: 13, 10: 12, 11: 12},
            'Химия': {8: 10, 9: 12, 10: 11, 11: 11},
            'Алгебра': {7: 10, 8: 9, 9: 7, 10: 10, 11: 10},
            'Геометрия': {7: 12, 8: 10, 9: 8, 10: 11, 11: 11},
            'Иностранный язык': {2: 6, 3: 7, 4: 8, 5: 9, 6: 11, 7: 10, 8: 8, 9: 9, 10: 8, 11: 8},
            'Информатика и ИКТ': {5: 4, 6: 10, 7: 4, 8: 7, 9: 7, 10: 6, 11: 6},
            'Изобразительное искусство': {1: 2, 2: 2, 3: 3, 4: 3, 5: 3, 6: 3, 7: 1},
            'Музыка': {1: 2, 2: 2, 3: 2, 4: 3, 5: 2, 6: 1, 7: 1},
            'Мировая художественная культура': {8: 8, 9: 5},
            'Технология': {1: 3, 2: 3, 3: 4, 4: 4, 5: 4, 6: 3, 7: 2, 8: 1, 9: 4},
            'Черчение': {8: 5, 9: 4},
            'Основы безопасности жизнедеятельности': {1: 2, 2: 3, 3: 3, 4: 4, 5: 1, 6: 2, 7: 3, 8: 3, 9: 3, 10: 2, 11: 2},
            'Физическая культура': {1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 4, 7: 2, 8: 2, 9: 2, 10: 1, 11: 1},
            'Астрономия': {11: 5},
            'Индивидуальный проект': {10: 3, 11: 3},
        }

        for subject in subjects:
            if subject.title in difficulty_table:
                for year_obj in study_years:
                    if year_obj.year in difficulty_table[subject.title]:
                        points = difficulty_table[subject.title][year_obj.year]
                        if points > 0:
                            Difficulty.objects.create(
                                study_year=year_obj,
                                subject=subject,
                                points=points,
                                user=random.choice(users)
                            )

    def _create_workloads(self, users, groups, user_subjects, study_years):
        workloads = []
        combos = set()
        group_hours = {g.id: 0 for g in groups}
        max_weekly = {year.year: year.max_weekly_hours for year in study_years}

        subject_hours = {
            'Математика': (3, 5),
            'Русский язык': (3, 5),
            'Литературное чтение': (3, 4),
            'Литература': (3, 4),
            'Окружающий мир': (2, 3),
            'Природоведение': (2, 3),
            'История': (2, 3),
            'Обществознание': (1, 2),
            'География': (1, 2),
            'Биология': (1, 2),
            'Физика': (2, 3),
            'Химия': (2, 3),
            'Алгебра': (3, 4),
            'Геометрия': (2, 3),
            'Иностранный язык': (2, 4),
            'Информатика и ИКТ': (1, 2),
            'Изобразительное искусство': (1, 2),
            'Музыка': (1, 2),
            'Мировая художественная культура': (1, 2),
            'Технология': (2, 3),
            'Черчение': (1, 2),
            'Основы безопасности жизнедеятельности': (1, 2),
            'Физическая культура': (2, 3),
            'Астрономия': (1, 1),
            'Индивидуальный проект': (1, 2),
        }

        for group in groups:
            max_hours = max_weekly[group.study_year.year]
            subjects_for_group = list(group.subjects.all())
            random.shuffle(subjects_for_group)

            for subject in subjects_for_group:
                if group_hours[group.id] >= max_hours:
                    break

                if subject.title not in subject_hours:
                    continue

                min_hours, max_hours_per_subject = subject_hours[subject.title]
                hours = random.randint(min_hours, max_hours_per_subject)

                if group_hours[group.id] + hours > max_hours:
                    hours = max_hours - group_hours[group.id]

                if hours <= 0:
                    continue

                valid_teachers = [
                    us.user for us in user_subjects
                    if us.subject == subject and us.user.profile.role == Profile.Role.TEACHER
                ]

                if not valid_teachers:
                    continue

                teacher = random.choice(valid_teachers)
                key = (group.id, subject.id, teacher.id)

                if key in combos:
                    continue

                combos.add(key)
                workload = Workload.objects.create(
                    hours_count=hours,
                    study_group=group,
                    teacher=teacher,
                    subject=subject,
                    user=random.choice(users)
                )
                workloads.append(workload)
                group_hours[group.id] += hours

        return workloads

    def _create_lessons(self, users, workloads, classrooms, bells):
        teacher_slots = set()
        group_slots = set()
        classroom_slots = set()

        for _ in tqdm(range(1000)):
            workload = random.choice(workloads)
            classroom = random.choice(classrooms)
            bell = random.choice(bells)
            week_day = random.randint(1, 6)

            key_teacher = (workload.teacher_id, week_day, bell.id)
            key_group = (workload.study_group_id, week_day, bell.id)
            key_classroom = (classroom.id, week_day, bell.id)

            if key_teacher in teacher_slots or key_group in group_slots or key_classroom in classroom_slots:
                continue

            teacher_slots.add(key_teacher)
            group_slots.add(key_group)
            classroom_slots.add(key_classroom)

            Lesson.objects.create(
                week_day=week_day,
                is_test=random.choice([True, False]),
                workload=workload,
                classroom=classroom,
                bell_schedule=bell,
                user=random.choice(users)
            )