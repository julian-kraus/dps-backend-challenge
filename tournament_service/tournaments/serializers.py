from rest_framework import serializers
from .models import Tournament

class TournamentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = "__all__"