from django.db import models
from players.models import Player

class Tournament(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class TournamentParticipant(models.Model):
    tournament = models.ForeignKey(
        Tournament, on_delete=models.CASCADE, related_name="participants"
    )
    player = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="tournament_participations"
    )

    class Meta:
        unique_together = ("tournament", "player")


class Game(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name="games")
    home_participant = models.ForeignKey(TournamentParticipant, on_delete=models.CASCADE, related_name="home_games")
    away_participant = models.ForeignKey(TournamentParticipant, on_delete=models.CASCADE, related_name="away_games")
    home_score = models.PositiveIntegerField()
    away_score = models.PositiveIntegerField()