
from django.contrib import admin
from django.urls import path, include
from users.views import LoginView, LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("login", LoginView.as_view(), name="login"),
    path("logout", LogoutView.as_view(), name="logout"),
    path('student/', include('student.urls')),
    path('teacher/', include('teacher.urls')),
    path('client/', include('payment.urls')),
]
