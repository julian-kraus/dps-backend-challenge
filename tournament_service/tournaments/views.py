from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .serializers import AddParticipantSerializer
from .serializers import TournamentsSerializer

from .models import Tournament, TournamentParticipant
from players.models import Player



class TournamentsViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.all()
    serializer_class = TournamentsSerializer


@api_view(["POST"])
def add_participant(request, tournament_id: int):
    """
    Add a player to a tournament.
    - URL: /tournaments/<tournament_id>/participants/
    - Body: { "player_id": <id> }
    """
    # 1. Check that the tournament exists
    try:
        tournament = Tournament.objects.get(id=tournament_id)
    except Tournament.DoesNotExist:
        return Response({"detail": "Tournament not found."}, status=status.HTTP_404_NOT_FOUND)

    # 2. Validate input data
    serializer = AddParticipantSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    player_id = serializer.validated_data["player_id"]

    # 3. Double check the player exists
    try:
        player = Player.objects.get(id=player_id)
    except Player.DoesNotExist:
        return Response({"detail": "Player not found."}, status=status.HTTP_404_NOT_FOUND)

    # 4. Enforce max 5 participants
    current_count = TournamentParticipant.objects.filter(tournament=tournament).count()
    if current_count >= 5:
        return Response(
            {"detail": "This tournament already has the maximum of 5 participants."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # 5. Avoid duplicates
    if TournamentParticipant.objects.filter(tournament=tournament, player=player).exists():
        return Response(
            {"detail": "Player is already a participant of this tournament."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # 6. Create the participant
    participant = TournamentParticipant.objects.create(
        tournament=tournament,
        player=player,
    )

    # 7. Return simple representation
    return Response(
        {
            "id": participant.id,
            "tournament_id": tournament.id,
            "player_id": player.id,
            "player_name": player.name,
        },
        status=status.HTTP_201_CREATED,
    )