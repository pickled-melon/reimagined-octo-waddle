import os
import random
from datetime import time

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker
from PIL import Image, ImageDraw

from schedule.models import (
    Profile, Classroom, Subject, SubjectPicture, StudyYear,
    BellSchedule, UserSubject, Difficulty, StudyGroup,
    Workload, Lesson,
)


class Command(BaseCommand):
    help = 'Генерирует тестовые данные'

    def handle(self, *args, **options):
        random.seed(42)
        fake = Faker(['ru_RU'])
        N = 1000

        self.stdout.write('Генерация картинок-заглушек...')
        classroom_files, album_files = self._ensure_placeholder_images()

        self.stdout.write('Генерация пользователей...')
        users = self._create_users(fake, N)

        self.stdout.write('Генерация профилей...')
        self._create_profiles(users, fake)

        self.stdout.write('Генерация кабинетов...')
        classrooms = self._create_classrooms(users, classroom_files, N)

        self.stdout.write('Генерация дисциплин...')
        subjects = self._create_subjects(users, classrooms, N)

        self.stdout.write('Генерация фотографий дисциплин...')
        self._create_subject_pictures(users, subjects, album_files, N)

        self.stdout.write('Генерация годов обучения...')
        study_years = self._create_study_years(users)

        self.stdout.write('Генерация звонков...')
        bells = self._create_bell_schedules(users, N)

        self.stdout.write('Генерация групп и подгрупп...')
        groups = self._create_study_groups(users, study_years, N)

        self.stdout.write('Генерация дисциплин учителей...')
        self._create_user_subjects(users, subjects, N)

        self.stdout.write('Генерация трудностей...')
        self._create_difficulties(users, study_years, subjects, N)

        self.stdout.write('Генерация нагрузок...')
        workloads = self._create_workloads(users, groups, subjects, N)

        self.stdout.write('Генерация занятий...')
        self._create_lessons(users, workloads, classrooms, bells, N)

        self.stdout.write(self.style.SUCCESS('Готово'))

    def _ensure_placeholder_images(self, count_per_model=20):
        media_root = settings.MEDIA_ROOT
        os.makedirs(os.path.join(media_root, 'classrooms'), exist_ok=True)
        os.makedirs(os.path.join(media_root, 'subject_albums'), exist_ok=True)

        classroom_files = []
        album_files = []

        palette = [
            (52, 152, 219), (46, 204, 113), (155, 89, 182),
            (241, 196, 15), (230, 126, 34), (231, 76, 60),
            (26, 188, 156), (52, 73, 94), (142, 68, 173),
            (22, 160, 133), (192, 57, 43), (41, 128, 185),
        ]

        for i in range(count_per_model):
            path_c = f'classrooms/classroom_{i}.jpg'
            full_c = os.path.join(media_root, path_c)
            if not os.path.exists(full_c):
                color = palette[i % len(palette)]
                img = Image.new('RGB', (400, 300), color=color)
                draw = ImageDraw.Draw(img)
                draw.text((20, 140), f'Classroom #{i + 1}', fill=(255, 255, 255))
                img.save(full_c, 'JPEG', quality=85)
            classroom_files.append(path_c)

            path_a = f'subject_albums/subject_{i}.jpg'
            full_a = os.path.join(media_root, path_a)
            if not os.path.exists(full_a):
                color = palette[(i + 5) % len(palette)]
                img = Image.new('RGB', (400, 300), color=color)
                draw = ImageDraw.Draw(img)
                draw.text((20, 140), f'Subject photo #{i + 1}', fill=(255, 255, 255))
                img.save(full_a, 'JPEG', quality=85)
            album_files.append(path_a)

        return classroom_files, album_files

    def _create_users(self, fake, N):
        count = User.objects.count()
        if count >= N:
            self.stdout.write(f'  Уже есть {count} пользователей, пропускаем.')
            return list(User.objects.all()[:N])

        needed = N - count
        common_password = make_password('password123')
        users = []
        for i in range(1, needed + 1):
            is_male = random.choice([True, False])
            first_name = fake.first_name_male() if is_male else fake.first_name_female()
            last_name = fake.last_name_male() if is_male else fake.last_name_female()
            username = f'{fake.user_name()}_{count + i}'[:150]

            while User.objects.filter(username=username).exists():
                username = f'{fake.user_name()}_{random.randint(10000, 99999)}'[:150]

            users.append(
                User(
                    username=username,
                    password=common_password,
                    first_name=first_name,
                    last_name=last_name,
                    email=fake.email(),
                )
            )
        with transaction.atomic():
            User.objects.bulk_create(users, batch_size=200)
        return list(User.objects.all()[:N])

    def _create_profiles(self, users, fake):
        roles = [Profile.Role.TEACHER] * 8 + [Profile.Role.METHODIST, Profile.Role.HEAD_TEACHER]
        male_exceptions = ('никита', 'илья', 'фома', 'лука', 'кузьма', 'савва', 'данила')

        profiles = []
        for user in users:
            if not hasattr(user, 'profile') or user.profile is None:
                first_name_lower = user.first_name.lower() if user.first_name else ''
                if first_name_lower in male_exceptions:
                    is_female = False
                else:
                    is_female = first_name_lower.endswith(('а', 'я', 'ия', 'ья'))

                patronymic = fake.middle_name_female() if is_female else fake.middle_name_male()
                profiles.append(
                    Profile(
                        user=user,
                        patronymic_name=patronymic,
                        role=random.choice(roles)
                    )
                )
            else:
                profile = user.profile
                first_name_lower = user.first_name.lower() if user.first_name else ''
                if first_name_lower in male_exceptions:
                    is_female = False
                else:
                    is_female = first_name_lower.endswith(('а', 'я', 'ия', 'ья'))
                profile.patronymic_name = fake.middle_name_female() if is_female else fake.middle_name_male()
                profile.role = random.choice(roles)
                profile.save()

        if profiles:
            with transaction.atomic():
                Profile.objects.bulk_create(profiles, batch_size=200)

    def _create_classrooms(self, users, classroom_files, N):
        count = Classroom.objects.count()
        if count >= N:
            self.stdout.write(f'  Уже есть {count} кабинетов, пропускаем.')
            return list(Classroom.objects.all()[:N])

        needed = N - count
        classrooms = [
            Classroom(
                number=f'{count + i:04d}',
                capacity=random.randint(10, 50),
                user=random.choice(users),
                picture=random.choice(classroom_files),
            )
            for i in range(1, needed + 1)
        ]
        with transaction.atomic():
            Classroom.objects.bulk_create(classrooms, batch_size=200)
        return list(Classroom.objects.all()[:N])

    def _create_subjects(self, users, classrooms, N):
        count = Subject.objects.count()
        if count < N:
            needed = N - count
            base_subjects = [
                'Математика', 'Русский язык', 'Литература', 'История',
                'Обществознание', 'Физика', 'Химия', 'Биология',
                'География', 'Английский язык', 'Информатика', 'ОБЖ',
                'Физкультура', 'Технология', 'Музыка', 'ИЗО'
            ]
            subjects = [
                Subject(
                    title=f'{random.choice(base_subjects)} {count + i}',
                    type=random.choice(['classroom', 'extracurricular']),
                    user=random.choice(users),
                )
                for i in range(1, needed + 1)
            ]
            with transaction.atomic():
                Subject.objects.bulk_create(subjects, batch_size=200)

        subjects = list(Subject.objects.all()[:N])

        Through = Subject.classrooms.through
        existing_links = set(Through.objects.values_list('subject_id', flat=True))

        m2m_links = []
        for subject in subjects:
            if subject.id in existing_links:
                continue
            chosen = random.sample(classrooms, k=random.randint(1, 5))
            for c in chosen:
                m2m_links.append(Through(subject_id=subject.id, classroom_id=c.id))

        if m2m_links:
            with transaction.atomic():
                Through.objects.bulk_create(m2m_links, batch_size=500)

        return subjects

    def _create_subject_pictures(self, users, subjects, album_files, N):
        count = SubjectPicture.objects.count()
        if count >= N:
            return
        needed = N - count
        pictures = [
            SubjectPicture(
                subject=random.choice(subjects),
                image=random.choice(album_files),
                user=random.choice(users),
            )
            for _ in range(needed)
        ]
        with transaction.atomic():
            SubjectPicture.objects.bulk_create(pictures, batch_size=200)

    def _create_study_years(self, users):
        existing_years = set(StudyYear.objects.values_list('year', flat=True))
        needed_years = [y for y in range(1, 12) if y not in existing_years]
        if not needed_years:
            self.stdout.write('  Все 11 классов уже есть, пропускаем.')
            return list(StudyYear.objects.all())

        study_years = [
            StudyYear(
                year=y,
                max_weekly_hours=random.randint(20, 40),
                max_daily_hours=random.randint(4, 8),
                user=random.choice(users),
            )
            for y in needed_years
        ]
        with transaction.atomic():
            StudyYear.objects.bulk_create(study_years, batch_size=200)
        return list(StudyYear.objects.all())

    def _create_bell_schedules(self, users, N):
        count = BellSchedule.objects.count()
        if count >= N:
            self.stdout.write(f'  Уже есть {count} звонков, пропускаем.')
            return list(BellSchedule.objects.all()[:N])

        needed = N - count
        max_lesson = BellSchedule.objects.order_by('-lesson_number').values_list('lesson_number', flat=True).first() or 0
        start = max_lesson + 1

        bells = []
        for i in range(start, start + needed):
            start_hour = 8 + (i % 8)
            bells.append(
                BellSchedule(
                    lesson_number=i,
                    start_time=time(hour=start_hour, minute=0),
                    end_time=time(hour=start_hour, minute=45),
                    user=random.choice(users),
                )
            )
        with transaction.atomic():
            BellSchedule.objects.bulk_create(bells, batch_size=200)
        return list(BellSchedule.objects.all()[:N])

    def _create_study_groups(self, users, study_years, N):
        letters = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЭЮЯ'

        count = StudyGroup.objects.filter(type='group').count()
        if count < N:
            needed = N - count
            existing_keys = set(
                StudyGroup.objects.filter(type='group').values_list('study_year_id', 'letter')
            )
            groups = []
            for year in study_years:
                for letter in letters:
                    if len(groups) >= needed:
                        break
                    key = (year.id, letter)
                    if key in existing_keys:
                        continue
                    existing_keys.add(key)
                    groups.append(
                        StudyGroup(
                            name=f"{year.year}{letter}",
                            students_count=random.randint(10, 40),
                            letter=letter,
                            type='group',
                            study_year=year,
                            user=random.choice(users),
                        )
                    )
                if len(groups) >= needed:
                    break
            with transaction.atomic():
                StudyGroup.objects.bulk_create(groups, batch_size=200)

        groups = list(StudyGroup.objects.filter(type='group')[:N])

        count_sub = StudyGroup.objects.filter(type='subgroup').count()
        if count_sub < N:
            needed_sub = N - count_sub
            existing_sub_keys = set(
                StudyGroup.objects.filter(type='subgroup').values_list('parent_id', 'subgroup_number')
            )
            subgroups = []
            subgroup_combos = set()
            for parent in groups:
                for number in ('first', 'second'):
                    if len(subgroups) >= needed_sub:
                        break
                    key = (parent.id, number)
                    if key in existing_sub_keys or key in subgroup_combos:
                        continue
                    subgroup_combos.add(key)
                    subgroups.append(
                        StudyGroup(
                            name=f"{parent.name}-{1 if number == 'first' else 2}",
                            students_count=random.randint(5, 20),
                            type='subgroup',
                            subgroup_number=number,
                            parent=parent,
                            study_year=parent.study_year,
                            user=random.choice(users),
                        )
                    )
                if len(subgroups) >= needed_sub:
                    break
            with transaction.atomic():
                StudyGroup.objects.bulk_create(subgroups, batch_size=200)

        return list(StudyGroup.objects.all()[:N])

    def _create_user_subjects(self, users, subjects, N):
        count = UserSubject.objects.count()
        if count >= N:
            return
        needed = N - count
        combos = set()
        items = []
        max_attempts = needed * 50
        attempts = 0

        while len(items) < needed and attempts < max_attempts:
            attempts += 1
            u = random.choice(users)
            s = random.choice(subjects)
            key = (u.id, s.id)
            if key in combos:
                continue
            combos.add(key)
            items.append(
                UserSubject(user=u, subject=s, creator=random.choice(users))
            )

        if items:
            with transaction.atomic():
                UserSubject.objects.bulk_create(items, batch_size=200)

    def _create_difficulties(self, users, study_years, subjects, N):
        count = Difficulty.objects.count()
        if count >= N:
            return
        needed = N - count
        combos = set()
        items = []
        max_attempts = needed * 50
        attempts = 0

        while len(items) < needed and attempts < max_attempts:
            attempts += 1
            y = random.choice(study_years)
            s = random.choice(subjects)
            key = (y.id, s.id)
            if key in combos:
                continue
            combos.add(key)
            items.append(
                Difficulty(
                    study_year=y,
                    subject=s,
                    points=random.randint(1, 10),
                    user=random.choice(users),
                )
            )

        if items:
            with transaction.atomic():
                Difficulty.objects.bulk_create(items, batch_size=200)

    def _create_workloads(self, users, groups, subjects, N):
        count = Workload.objects.count()
        if count >= N:
            return list(Workload.objects.all()[:N])
        needed = N - count
        combos = set()
        items = []
        max_attempts = needed * 50
        attempts = 0

        while len(items) < needed and attempts < max_attempts:
            attempts += 1
            g = random.choice(groups)
            s = random.choice(subjects)
            t = random.choice(users)
            key = (g.id, s.id, t.id)
            if key in combos:
                continue
            combos.add(key)
            items.append(
                Workload(
                    hours_count=random.randint(1, 6),
                    study_group=g,
                    teacher=t,
                    subject=s,
                    user=random.choice(users),
                )
            )

        if items:
            with transaction.atomic():
                Workload.objects.bulk_create(items, batch_size=200)
        return list(Workload.objects.all()[:N])

    def _create_lessons(self, users, workloads, classrooms, bells, N):
        count = Lesson.objects.count()
        if count >= N:
            return

        needed = N - count
        teacher_slots = set()
        group_slots = set()
        classroom_slots = set()

        for lesson in Lesson.objects.all():
            teacher_slots.add((lesson.workload.teacher_id, lesson.week_day, lesson.bell_schedule_id))
            group_slots.add((lesson.workload.study_group_id, lesson.week_day, lesson.bell_schedule_id))
            classroom_slots.add((lesson.classroom_id, lesson.week_day, lesson.bell_schedule_id))

        items = []
        attempts = 0
        max_attempts = needed * 200

        while len(items) < needed and attempts < max_attempts:
            attempts += 1
            w = random.choice(workloads)
            wd = random.randint(1, 6)
            b = random.choice(bells)
            c = random.choice(classrooms)

            key_teacher = (w.teacher_id, wd, b.id)
            key_group = (w.study_group_id, wd, b.id)
            key_classroom = (c.id, wd, b.id)

            if key_teacher in teacher_slots or key_group in group_slots or key_classroom in classroom_slots:
                continue

            teacher_slots.add(key_teacher)
            group_slots.add(key_group)
            classroom_slots.add(key_classroom)

            items.append(
                Lesson(
                    week_day=wd,
                    is_test=random.choice([True, False]),
                    workload=w,
                    classroom=c,
                    bell_schedule=b,
                    user=random.choice(users),
                )
            )

        if items:
            with transaction.atomic():
                Lesson.objects.bulk_create(items, batch_size=200)