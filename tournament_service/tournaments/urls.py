from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TournamentsViewSet, add_participant, add_game_result, tournament_status, tournament_leaderboard

router = DefaultRouter()
router.register(r'tournaments', TournamentsViewSet, basename='tournament')

urlpatterns = [
    path('', include(router.urls)),
    path("tournaments/<int:tournament_id>/participants/", add_participant, name="add-participant"),
    path("tournaments/<int:tournament_id>/games/", add_game_result, name="add-game"),
    path("tournaments/<int:tournament_id>/status/", tournament_status, name="tournament-status"),
    path("tournaments/<int:tournament_id>/leaderboard/", tournament_leaderboard, name="tournament-leaderboard"),
]
