from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SponsorViewSet, UserViewSet
from . import views

router = DefaultRouter()
router.register(r'sponsors', SponsorViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('api', include(router.urls)),
    path('', views.home, name="home"),
    path('add_sponsor/', views.add_sponsor, name='add_sponsor'),
    path('edit_sponsor/', views.edit_sponsor, name='edit_sponsor'),


]