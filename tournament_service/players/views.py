from rest_framework import viewsets
from drf_spectacular.utils import extend_schema
from .models import Player
from .serializers import PlayerSerializer


class PlayerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing players.
    
    Provides CRUD operations for players.
    """
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
