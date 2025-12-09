from rest_framework import serializers
from .models import Tournament, TournamentParticipant, Game
from players.models import Player
from rest_framework.exceptions import NotFound

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



class AddParticipantSerializer(serializers.Serializer):
    player_id = serializers.IntegerField()

    def validate_player_id(self, value):
        return value