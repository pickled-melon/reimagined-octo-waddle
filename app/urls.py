from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from rest_framework.routers import DefaultRouter

from schedule import views
from schedule.api import *


router = DefaultRouter()
router.register('profiles', ProfileViewSet, basename='profiles')
router.register('classrooms', ClassroomViewSet, basename='classrooms')
router.register('subjects', SubjectViewSet, basename='subjects')
router.register('subject-pictures', SubjectPictureViewSet, basename='subject-pictures')
router.register('study-years', StudyYearViewSet, basename='study-years')
router.register('bell-schedules', BellScheduleViewSet, basename='bell-schedules')
router.register('user-subjects', UserSubjectViewSet, basename='user-subjects')
router.register('difficulties', DifficultyViewSet, basename='difficulties')
router.register('study-groups', StudyGroupViewSet, basename='study-groups')
router.register('workloads', WorkloadViewSet, basename='workloads')
router.register('lessons', LessonViewSet, basename='lessons')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),

    path('profiles/', views.ShowProfilesView.as_view(), name='profiles'),
    path('classrooms/', views.ShowClassroomsView.as_view(), name='classrooms'),
    path('subjects/', views.ShowSubjectsView.as_view(), name='subjects'),
    path('study-years/', views.ShowStudyYearsView.as_view(), name='study-years'),
    path('bell-schedules/', views.ShowBellSchedulesView.as_view(), name='bell-schedules'),
    path('user-subjects/', views.ShowUserSubjectsView.as_view(), name='user-subjects'),
    path('difficulties/', views.ShowDifficultiesView.as_view(), name='difficulties'),
    path('study-groups/', views.ShowStudyGroupsView.as_view(), name='study-groups'),
    path('workloads/', views.ShowWorkloadsView.as_view(), name='workloads'),
    path('lessons/', views.ShowLessonsView.as_view(), name='lessons'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)