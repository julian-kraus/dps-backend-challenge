from rest_framework import serializers
from .models import Tournament, TournamentParticipant, Game
from players.models import Player


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
        if not Player.objects.filter(id=value).exists():
            raise serializers.ValidationError("Player with this ID does not exist.")
        return value