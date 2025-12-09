from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TournamentsViewSet, add_participant, add_game_result

router = DefaultRouter()
router.register(r'tournaments', TournamentsViewSet, basename='tournament')

urlpatterns = [
    path('', include(router.urls)),
    path("tournaments/<int:tournament_id>/participants/", add_participant, name="add-participant"),
    path("tournaments/<int:tournament_id>/games/", add_game_result, name="add-game"),
]
