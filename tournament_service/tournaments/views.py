from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .serializers import AddParticipantSerializer, AddGameResultSerializer, TournamentsSerializer, GameSerializer

from .models import Tournament, TournamentParticipant, Game
from players.models import Player

from collections import defaultdict



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


@api_view(["GET"])
def tournament_status(request, tournament_id: int):
    """
    Return the status of a tournament.

    URL:
      GET /api/tournaments/<tournament_id>/status/

    Status:
      - in_planning: participants exist, 0 games
      - started:     some games played, but not all
      - finished:    everybody has played everybody once
    """
    try:
        tournament = Tournament.objects.get(id=tournament_id)
    except Tournament.DoesNotExist:
        return Response({"detail": "Tournament not found."},
                        status=status.HTTP_404_NOT_FOUND)

    participants = TournamentParticipant.objects.filter(tournament=tournament)
    games = Game.objects.filter(tournament=tournament)

    n = participants.count()
    games_played = games.count()
    total_required_games = n * (n - 1) // 2 if n >= 2 else 0

    if games_played == 0:
        status_str = "in_planning"
    elif games_played < total_required_games:
        status_str = "started"
    else:
        status_str = "finished"

    return Response(
        {
            "tournament_id": tournament.id,
            "tournament_name": tournament.name,
            "participants_count": n,
            "total_required_games": total_required_games,
            "games_played": games_played,
            "status": status_str,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
def tournament_leaderboard(request, tournament_id: int):
    """
    Return the leaderboard for a tournament.

    URL:
      GET /api/tournaments/<tournament_id>/leaderboard/

    Leaderboard entry:
      - player_id
      - player_name
      - points (2 win, 1 draw, 0 loss)
      - wins, draws, losses, games_played
    """
    try:
        tournament = Tournament.objects.get(id=tournament_id)
    except Tournament.DoesNotExist:
        return Response({"detail": "Tournament not found."},
                        status=status.HTTP_404_NOT_FOUND)

    participants = TournamentParticipant.objects.select_related("player").filter(tournament=tournament)
    games = Game.objects.select_related(
        "home_participant__player",
        "away_participant__player",
    ).filter(tournament=tournament)

    # Initialize stats per player
    stats = defaultdict(lambda: {
        "points": 0,
        "wins": 0,
        "draws": 0,
        "losses": 0,
        "games_played": 0,
    })

    for p in participants:
        stats[p.player_id]

    for g in games:
        home_player = g.home_participant.player
        away_player = g.away_participant.player

        stats[home_player.id]["games_played"] += 1
        stats[away_player.id]["games_played"] += 1

        if g.home_score > g.away_score:
            stats[home_player.id]["points"] += 2
            stats[home_player.id]["wins"] += 1
            stats[away_player.id]["losses"] += 1
        elif g.home_score < g.away_score:
            stats[away_player.id]["points"] += 2
            stats[away_player.id]["wins"] += 1
            stats[home_player.id]["losses"] += 1
        else:
            stats[home_player.id]["points"] += 1
            stats[away_player.id]["points"] += 1
            stats[home_player.id]["draws"] += 1
            stats[away_player.id]["draws"] += 1

    leaderboard = []
    for p in participants:
        s = stats[p.player_id]
        leaderboard.append(
            {
                "player_id": p.player_id,
                "player_name": p.player.name,
                "points": s["points"],
                "wins": s["wins"],
                "draws": s["draws"],
                "losses": s["losses"],
                "games_played": s["games_played"],
            }
        )

    # Sort by points desc, then name for deterministic order
    leaderboard.sort(key=lambda e: (-e["points"], e["player_name"]))

    return Response(
        {
            "tournament_id": tournament.id,
            "tournament_name": tournament.name,
            "leaderboard": leaderboard,
        },
        status=status.HTTP_200_OK,
    )