import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from tournaments.models import Tournament, TournamentParticipant, Game
from players.models import Player


class TournamentStatusLeaderboardTests(APITestCase):
    def _create_tournament(self, name="Test Tournament"):
        return Tournament.objects.create(name=name)

    def _create_player(self, name):
        return Player.objects.create(name=name)

    def _create_participant(self, tournament, player):
        return TournamentParticipant.objects.create(tournament=tournament, player=player)

    def _status_url(self, tournament_id: int):
        return reverse("tournament-status", kwargs={"tournament_id": tournament_id})

    @pytest.mark.order(18)
    def test_status_tournament_not_found(self):
        url = self._status_url(9999)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("Tournament not found", response.data["detail"])

    @pytest.mark.order(19)
    def test_status_in_planning(self):
        """
        Tournament with participants but no games -> in_planning.
        """
        t = self._create_tournament("Planning Cup")
        p1 = self._create_player("Alice")
        p2 = self._create_player("Bob")
        self._create_participant(t, p1)
        self._create_participant(t, p2)

        url = self._status_url(t.id)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "in_planning")
        self.assertEqual(response.data["participants_count"], 2)
        self.assertEqual(response.data["games_played"], 0)
        self.assertEqual(response.data["total_required_games"], 1)  # 2 * 1 / 2
        # Status endpoint should include leaderboard
        self.assertIn("leaderboard", response.data)
        self.assertEqual(len(response.data["leaderboard"]), 2)
        # All participants should have 0 points with no games
        for entry in response.data["leaderboard"]:
            self.assertEqual(entry["points"], 0)
            self.assertEqual(entry["games_played"], 0)

    @pytest.mark.order(20)
    def test_status_started_and_finished(self):
        """
        With some games (but not all) -> started;
        when everyone has played everyone once -> finished.
        """
        t = self._create_tournament("Progress Cup")
        # 3 participants -> required_games = 3 (AB, AC, BC)
        pA = self._create_player("A")
        pB = self._create_player("B")
        pC = self._create_player("C")

        pa = self._create_participant(t, pA)
        pb = self._create_participant(t, pB)
        pc = self._create_participant(t, pC)

        # One game: A beats B (A gets 2 points, B gets 0)
        Game.objects.create(
            tournament=t,
            home_participant=pa,
            away_participant=pb,
            home_score=2,  # A wins -> 2 points
            away_score=0,  # B loses -> 0 points
        )

        url = self._status_url(t.id)
        resp_started = self.client.get(url)
        self.assertEqual(resp_started.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_started.data["status"], "started")
        self.assertEqual(resp_started.data["games_played"], 1)
        self.assertEqual(resp_started.data["total_required_games"], 3)
        self.assertIn("leaderboard", resp_started.data)
        leaderboard_started = resp_started.data["leaderboard"]
        self.assertEqual(len(leaderboard_started), 3)
        # A should have 2 points, B and C should have 0
        points_by_name = {e["player_name"]: e["points"] for e in leaderboard_started}
        self.assertEqual(points_by_name["A"], 2)
        self.assertEqual(points_by_name["B"], 0)
        self.assertEqual(points_by_name["C"], 0)

        # Add remaining games: A vs C (draw), B vs C (C wins)
        Game.objects.create(
            tournament=t,
            home_participant=pa,
            away_participant=pc,
            home_score=1,  # draw -> both get 1 point
            away_score=1,
        )
        Game.objects.create(
            tournament=t,
            home_participant=pb,
            away_participant=pc,
            home_score=0,  # C wins -> C gets 2, B gets 0
            away_score=2,
        )

        resp_finished = self.client.get(url)
        self.assertEqual(resp_finished.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_finished.data["status"], "finished")
        self.assertEqual(resp_finished.data["games_played"], 3)
        self.assertEqual(resp_finished.data["total_required_games"], 3)
        self.assertIn("leaderboard", resp_finished.data)
        leaderboard_finished = resp_finished.data["leaderboard"]
        self.assertEqual(len(leaderboard_finished), 3)
        # Final points: A = 2+1=3, B = 0+0=0, C = 1+2=3
        # Sorted by points desc, then name: A (3), C (3), B (0)
        points_by_name_final = {e["player_name"]: e["points"] for e in leaderboard_finished}
        self.assertEqual(points_by_name_final["A"], 3)
        self.assertEqual(points_by_name_final["B"], 0)
        self.assertEqual(points_by_name_final["C"], 3)

    @pytest.mark.order(21)
    def test_leaderboard_tournament_not_found(self):
        """Test that status endpoint returns 404 for non-existent tournament."""
        url = self._status_url(9999)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("Tournament not found", response.data["detail"])

    @pytest.mark.order(22)
    def test_leaderboard_no_games_zero_points(self):
        """
        All participants should show up with 0 points and 0 games if no games played.
        """
        t = self._create_tournament("Empty Cup")
        p1 = self._create_player("Alice")
        p2 = self._create_player("Bob")
        self._create_participant(t, p1)
        self._create_participant(t, p2)

        url = self._status_url(t.id)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("leaderboard", response.data)
        self.assertEqual(len(response.data["leaderboard"]), 2)

        for entry in response.data["leaderboard"]:
            self.assertEqual(entry["points"], 0)
            self.assertEqual(entry["games_played"], 0)

    @pytest.mark.order(23)
    def test_leaderboard_points_after_games(self):
        """
        Points should be computed as:
          win = 2, draw = 1, loss = 0
        and leaderboard sorted by points desc.
        """
        t = self._create_tournament("Points Cup")
        pA = self._create_player("Alice")
        pB = self._create_player("Bob")
        pC = self._create_player("Charlie")

        pa = self._create_participant(t, pA)
        pb = self._create_participant(t, pB)
        pc = self._create_participant(t, pC)

        # Games:
        # A beats B (A +2, B +0)
        Game.objects.create(
            tournament=t,
            home_participant=pa,
            away_participant=pb,
            home_score=2,  # A wins -> 2 points
            away_score=0,  # B loses -> 0 points
        )
        # B draws C (B +1, C +1)
        Game.objects.create(
            tournament=t,
            home_participant=pb,
            away_participant=pc,
            home_score=1,  # draw -> both get 1 point
            away_score=1,
        )
        # C beats A (C +2, A +0)
        Game.objects.create(
            tournament=t,
            home_participant=pc,
            away_participant=pa,
            home_score=2,  # C wins -> 2 points
            away_score=0,  # A loses -> 0 points
        )

        url = self._status_url(t.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("leaderboard", response.data)

        leaderboard = response.data["leaderboard"]
        # Expected points:
        #   A: win vs B (+2), loss vs C (+0) = 2
        #   B: loss vs A (0), draw vs C (+1) = 1
        #   C: draw vs B (+1), win vs A (+2) = 3
        # Sorted by points desc: C (3), A (2), B (1)

        self.assertEqual(len(leaderboard), 3)
        self.assertEqual(leaderboard[0]["player_name"], "Charlie")
        self.assertEqual(leaderboard[0]["points"], 3)

        self.assertEqual(leaderboard[1]["player_name"], "Alice")
        self.assertEqual(leaderboard[1]["points"], 2)

        self.assertEqual(leaderboard[2]["player_name"], "Bob")
        self.assertEqual(leaderboard[2]["points"], 1)