#rest_framework imports
from rest_framework.routers import DefaultRouter
#django imports
from django.urls import path
#app imports
from .views import *

router = DefaultRouter()
router.register(r'projects', StudentProjectsViewSet, basename='projects')

urlpatterns = [
    path('courses/', CourseListView.as_view(), name='course-list-create'),
    path('course-payment/<int:id>/', CourseDetailsPayment.as_view(), name='course-payment'),
    path('new/', NewStudentView.as_view(), name='new-student'),
    path('details/', StudentView.as_view(), name='student-detail'),
    path("update/", StudentView.as_view(), name="update-student"),
    path("dashboard/", StudentDashboardView.as_view(), name="dashboard"),
    path("verify/", StudentVerify.as_view(), name="student-verify"),
    path("test/", StudentTakingTest.as_view(), name="student-test"),
]
urlpatterns += router.urls