import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from tournaments.models import Tournament, TournamentParticipant
from players.models import Player


# ====================================================
#               TOURNAMENT API TESTS
# ====================================================

class TournamentAPITests(APITestCase):
    def setUp(self):
        # From DRF router: basename="tournament" -> tournament-list, tournament-detail
        self.tournament_list_url = reverse("tournament-list")

    @pytest.mark.order(4)
    def test_list_tournaments_initially_empty(self):
        """
        GET /api/tournaments/ should return an empty list when no tournaments exist.
        """
        response = self.client.get(self.tournament_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 0)

    @pytest.mark.order(5)
    def test_create_tournament_and_see_in_list(self):
        """
        POST /api/tournaments/ should create a tournament,
        and subsequent GET should include it.
        """
        create_data = {"name": "Spring Cup"}
        create_response = self.client.post(self.tournament_list_url, create_data, format="json")

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create_response.data["name"], "Spring Cup")
        tournament_id = create_response.data["id"]
        self.assertTrue(Tournament.objects.filter(id=tournament_id, name="Spring Cup").exists())

        # Now list tournaments and check "Spring Cup" is there
        list_response = self.client.get(self.tournament_list_url)
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(list_response.data, list)
        names = [t["name"] for t in list_response.data]
        self.assertIn("Spring Cup", names)

    @pytest.mark.order(6)
    def test_update_tournament(self):
        """
        PUT /api/tournaments/<id>/ should update an existing tournament.
        """
        # First create a tournament
        create_response = self.client.post(self.tournament_list_url, {"name": "Old Name"}, format="json")
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        tournament_id = create_response.data["id"]

        tournament_detail_url = reverse("tournament-detail", kwargs={"pk": tournament_id})

        update_data = {"name": "New Name"}
        update_response = self.client.put(tournament_detail_url, update_data, format="json")

        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data["name"], "New Name")
        self.assertTrue(Tournament.objects.filter(id=tournament_id, name="New Name").exists())

    @pytest.mark.order(7)
    def test_delete_tournament(self):
        """
        DELETE /api/tournaments/<id>/ should remove the tournament.
        """
        # Create a tournament to delete
        create_response = self.client.post(self.tournament_list_url, {"name": "To Delete"}, format="json")
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        tournament_id = create_response.data["id"]

        tournament_detail_url = reverse("tournament-detail", kwargs={"pk": tournament_id})

        delete_response = self.client.delete(tournament_detail_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tournament.objects.filter(id=tournament_id).exists())

    # ---------- add_participant endpoint tests ----------

    def _create_tournament(self, name="Test Tournament"):
        resp = self.client.post(self.tournament_list_url, {"name": name}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        return resp.data["id"]

    def _create_player(self, name="Test Player"):
        player_list_url = reverse("player-list")
        resp = self.client.post(player_list_url, {"name": name}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        return resp.data["id"]

    @pytest.mark.order(8)
    def test_add_participant_success(self):
        """
        POST /api/tournaments/<id>/participants/ with valid player_id
        should add the player to the tournament.
        """
        tournament_id = self._create_tournament("Participants Cup")
        player_id = self._create_player("Alice")

        add_participant_url = reverse(
            "add-participant",
            kwargs={"tournament_id": tournament_id},
        )

        response = self.client.post(add_participant_url, {"player_id": player_id}, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["tournament_id"], tournament_id)
        self.assertEqual(response.data["player_id"], player_id)
        self.assertTrue(
            TournamentParticipant.objects.filter(
                tournament_id=tournament_id,
                player_id=player_id,
            ).exists()
        )

    @pytest.mark.order(9)
    def test_add_participant_tournament_not_found(self):
        """
        If the tournament does not exist, should return 404 with appropriate message.
        """
        player_id = self._create_player("Bob")

        add_participant_url = reverse(
            "add-participant",
            kwargs={"tournament_id": 9999},  # non-existent
        )

        response = self.client.post(add_participant_url, {"player_id": player_id}, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("Tournament not found", response.data["detail"])

    @pytest.mark.order(10)
    def test_add_participant_player_not_found(self):
        """
        If the player does not exist, should return 404.
        """
        tournament_id = self._create_tournament("No Player Cup")
        add_participant_url = reverse(
            "add-participant",
            kwargs={"tournament_id": tournament_id},
        )

        response = self.client.post(add_participant_url, {"player_id": 9999}, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("Player not found", response.data["detail"])

    @pytest.mark.order(11)
    def test_add_participant_max_five_participants(self):
        """
        Adding more than 5 participants to the same tournament should return 400.
        """
        tournament_id = self._create_tournament("Small Cup")
        add_participant_url = reverse(
            "add-participant",
            kwargs={"tournament_id": tournament_id},
        )

        # Add 5 players -> all should succeed
        for i in range(5):
            player_id = self._create_player(f"Player {i}")
            resp = self.client.post(add_participant_url, {"player_id": player_id}, format="json")
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # 6th player -> should fail with 400
        extra_player_id = self._create_player("Too Many")
        resp = self.client.post(add_participant_url, {"player_id": extra_player_id}, format="json")

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("maximum of 5 participants", resp.data["detail"].lower())

    @pytest.mark.order(12)
    def test_add_participant_duplicate_player(self):
        """
        Adding the same player twice to the same tournament should return 400.
        """
        tournament_id = self._create_tournament("Duplicate Cup")
        player_id = self._create_player("Charlie")

        add_participant_url = reverse(
            "add-participant",
            kwargs={"tournament_id": tournament_id},
        )

        # First add -> success
        first = self.client.post(add_participant_url, {"player_id": player_id}, format="json")
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)

        # Second add -> should fail
        second = self.client.post(add_participant_url, {"player_id": player_id}, format="json")
        self.assertEqual(second.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already a participant", second.data["detail"].lower())