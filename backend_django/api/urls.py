from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'ads', views.AdViewSet, basename='ad')
router.register(r'materials', views.MaterialViewSet, basename='material')
router.register(r'interviews', views.InterviewPostViewSet, basename='interview')
router.register(r'notifications', views.NotificationViewSet, basename='notification')
router.register(r'reports', views.ReportedAdViewSet, basename='report')

urlpatterns = [
    path('auth/register', views.register),
    path('auth/login', views.login),
    path('auth/me', views.me),
    path('', include(router.urls)),
]
