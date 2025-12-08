from rest_framework import viewsets
from .models import Tournament
from .serializers import TournamentsSerializer

class TournamentsViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.all()
    serializer_class = TournamentsSerializer
