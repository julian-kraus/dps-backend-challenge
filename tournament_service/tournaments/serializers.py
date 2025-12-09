from rest_framework import serializers
from .models import Tournament, TournamentParticipant, Game

class TournamentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = "__all__"


class TournamentParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = TournamentParticipant
        fields = "__all__"

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = "__all__"