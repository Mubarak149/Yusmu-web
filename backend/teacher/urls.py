#rest_framework imports
from rest_framework.routers import DefaultRouter
#django imports
from django.urls import path
#app imports
from .views import *

router = DefaultRouter()
router.register(r'projects', TeacherProjectsViewSet, basename='teacher-projects')

urlpatterns = [
    
]
urlpatterns += router.urls