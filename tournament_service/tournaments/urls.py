from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TournamentsViewSet

router = DefaultRouter()
router.register(r'tournaments', TournamentsViewSet, basename='tournament')

urlpatterns = [
    path('', include(router.urls)),
]