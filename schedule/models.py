from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Classroom(models.Model):
    number = models.CharField(max_length=10, unique=True, verbose_name="Номер")
    capacity = models.PositiveIntegerField(verbose_name="Вместимость")

    class Meta:
        verbose_name = "Кабинет"
        verbose_name_plural = "Кабинеты"

    def __str__(self):
        return f"Кабинет {self.number}"


class Subject(models.Model):
    SUBJECT_TYPES = [
        ('classroom', 'Классно-урочный'),
        ('extracurricular', 'Внеурочный'),
    ]

    title = models.CharField(max_length=200, unique=True, verbose_name="Название")
    type = models.CharField(
        max_length=20, choices=SUBJECT_TYPES,
        default='classroom', verbose_name="Тип"
    )

    classrooms = models.ManyToManyField(
        Classroom, blank=True,
        related_name='subjects',
        verbose_name="Требуемые кабинеты"
    )

    class Meta:
        verbose_name = "Дисциплина"
        verbose_name_plural = "Дисциплины"

    def __str__(self):
        return self.title


class StudyYear(models.Model):
    year = models.PositiveSmallIntegerField(
        unique=True,
        validators=[MinValueValidator(1), MaxValueValidator(11)],
        verbose_name="Год обучения"
    )
    max_weekly_hours = models.PositiveIntegerField(verbose_name="Предельная недельная нагрузка")
    max_daily_hours = models.PositiveIntegerField(verbose_name="Предельная дневная нагрузка")

    class Meta:
        verbose_name = "Год обучения"
        verbose_name_plural = "Годы обучения"

    def __str__(self):
        return f"{self.year} класс"


class BellSchedule(models.Model):
    lesson_number = models.PositiveSmallIntegerField(verbose_name="Номер урока")
    start_time = models.TimeField(verbose_name="Время начала")
    end_time = models.TimeField(verbose_name="Время конца")

    class Meta:
        verbose_name = "Расписание звонков"
        verbose_name_plural = "Расписание звонков"
        unique_together = ('lesson_number',)

    def __str__(self):
        return f"{self.lesson_number}-й урок ({self.start_time:%H:%M}–{self.end_time:%H:%M})"


class Teacher(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='teacher',
        null=True, blank=True,
        verbose_name="Пользователь"
    )
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    patronymic_name = models.CharField(max_length=100, blank=True, verbose_name="Отчество")

    subjects = models.ManyToManyField(
        Subject, blank=True,
        related_name='teachers',
        verbose_name="Преподаваемые дисциплины"
    )

    class Meta:
        verbose_name = "Учитель"
        verbose_name_plural = "Учителя"

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.patronymic_name}".strip()


class Difficulty(models.Model):
    study_year = models.ForeignKey(
        StudyYear, on_delete=models.CASCADE,
        related_name='difficulties',
        verbose_name="Год обучения"
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE,
        related_name='difficulties',
        verbose_name="Дисциплина"
    )
    points = models.PositiveSmallIntegerField(verbose_name="Количество баллов")

    class Meta:
        verbose_name = "Трудность"
        verbose_name_plural = "Трудности"
        unique_together = ('study_year', 'subject')

    def __str__(self):
        return f"{self.subject} — {self.study_year}: {self.points}"


class StudyGroup(models.Model):
    GROUP_TYPES = [
        ('group', 'Группа'),
        ('subgroup', 'Подгруппа'),
    ]
    SUBGROUP_NUMBERS = [
        ('first', '1'),
        ('second', '2'),
    ]

    name = models.CharField(max_length=50, verbose_name="Название")
    students_count = models.PositiveIntegerField(verbose_name="Количество человек")
    letter = models.CharField(max_length=1, blank=True, verbose_name="Литера")
    type = models.CharField(
        max_length=9, choices=GROUP_TYPES,
        default='group', verbose_name="Тип"
    )
    subgroup_number = models.CharField(
        max_length=6, choices=SUBGROUP_NUMBERS,
        blank=True, verbose_name="Номер подгруппы"
    )

    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='subgroups',
        verbose_name="Родительская группа"
    )
    study_year = models.ForeignKey(
        StudyYear,
        on_delete=models.PROTECT,
        related_name='groups',
        verbose_name="Год обучения"
    )

    class Meta:
        verbose_name = "Учебная группа"
        verbose_name_plural = "Учебные группы"
        unique_together = ('name', 'study_year')

    def __str__(self):
        return self.name


class Workload(models.Model):
    hours_count = models.PositiveSmallIntegerField(verbose_name="Количество часов")

    study_group = models.ForeignKey(
        StudyGroup, on_delete=models.CASCADE,
        related_name='workloads',
        verbose_name="Учебная группа"
    )
    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE,
        related_name='workloads',
        verbose_name="Учитель"
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE,
        related_name='workloads',
        verbose_name="Дисциплина"
    )

    class Meta:
        verbose_name = "Нагрузка"
        verbose_name_plural = "Нагрузки"
        unique_together = ('study_group', 'subject', 'teacher')

    def __str__(self):
        return f"{self.teacher} → {self.subject} ({self.study_group})"

    @property
    def difficulty_points(self):
        d = Difficulty.objects.filter(
            study_year=self.study_group.study_year,
            subject=self.subject,
        ).first()
        return d.points if d else None


class Lesson(models.Model):
    WEEK_DAYS = [
        (1, 'Понедельник'),
        (2, 'Вторник'),
        (3, 'Среда'),
        (4, 'Четверг'),
        (5, 'Пятница'),
        (6, 'Суббота'),
    ]

    week_day = models.PositiveSmallIntegerField(
        choices=WEEK_DAYS, verbose_name="День недели"
    )
    is_test = models.BooleanField(default=False, verbose_name="Контрольная работа")

    workload = models.ForeignKey(
        Workload, on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name="Нагрузка"
    )
    classroom = models.ForeignKey(
        Classroom, on_delete=models.PROTECT,
        related_name='lessons',
        verbose_name="Кабинет"
    )
    bell_schedule = models.ForeignKey(
        BellSchedule, on_delete=models.PROTECT,
        related_name='lessons',
        verbose_name="Слот расписания"
    )

    class Meta:
        verbose_name = "Занятие"
        verbose_name_plural = "Занятия"
        constraints = [
            models.UniqueConstraint(
                fields=['week_day', 'bell_schedule', 'classroom'],
                name='unique_classroom_slot',
            ),
        ]

    def __str__(self):
        return f"{self.get_week_day_display()}, {self.bell_schedule}, {self.workload.subject}"