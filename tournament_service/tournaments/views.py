from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .serializers import AddParticipantSerializer, AddGameResultSerializer, TournamentsSerializer, GameSerializer

from .models import Tournament, TournamentParticipant, Game
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





@api_view(["POST"])
def add_game_result(request, tournament_id: int):
    """
    Enter a game result using:
      - home_participant: int
      - away_participant: int
      - winner: int | null (null = draw)

    URL:
      POST /api/tournaments/<tournament_id>/games/
    """
    # 1. Tournament must exist
    try:
        tournament = Tournament.objects.get(id=tournament_id)
    except Tournament.DoesNotExist:
        return Response({"detail": "Tournament not found."},
                        status=status.HTTP_404_NOT_FOUND)

    # 2. Validate input
    serializer = AddGameResultSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    home_id = serializer.validated_data["home_participant"]
    away_id = serializer.validated_data["away_participant"]
    winner = serializer.validated_data["winner"]

    # 3. Load participants
    try:
        home_participant = TournamentParticipant.objects.get(id=home_id)
        away_participant = TournamentParticipant.objects.get(id=away_id)
    except TournamentParticipant.DoesNotExist:
        return Response({"detail": "One or both participants do not exist."},
                        status=status.HTTP_404_NOT_FOUND)

    # 4. Cannot play against themselves
    if home_id == away_id:
        return Response({"detail": "A participant cannot play against themselves."},
                        status=status.HTTP_400_BAD_REQUEST)

    # 5. Validate participants belong to this tournament
    if home_participant.tournament_id != tournament.id or away_participant.tournament_id != tournament.id:
        return Response(
            {"detail": "Both participants must belong to this tournament."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # 6. Validate winner is one of the participants or null
    if winner not in (None, home_participant.player_id, away_participant.player_id):
        return Response(
            {"detail": "Winner must be one of the participants or null for draw."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # 7. Only one game per pair
    if Game.objects.filter(
        tournament=tournament,
        home_participant=home_participant,
        away_participant=away_participant,
    ).exists() or Game.objects.filter(
        tournament=tournament,
        home_participant=away_participant,
        away_participant=home_participant,
    ).exists():
        return Response(
            {"detail": "A game between these participants already exists for this tournament."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # 8. Convert winner into internal scores
    if winner is None:
        home_score, away_score = 1, 1
    elif winner == home_participant.player_id:
        home_score, away_score = 2, 0
    else:  # winner == away participant
        home_score, away_score = 0, 2

    # 9. Create the game
    game = Game.objects.create(
        tournament=tournament,
        home_participant=home_participant,
        away_participant=away_participant,
        home_score=home_score,
        away_score=away_score,
    )

    return Response(GameSerializer(game).data, status=status.HTTP_201_CREATED)