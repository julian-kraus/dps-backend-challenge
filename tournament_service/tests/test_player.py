import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from players.models import Player


# ====================================================
#               PLAYER API TESTS
# ====================================================

class PlayerAPITests(APITestCase):
    def setUp(self):
        # Base URL for list/create endpoints from DRF router
        self.player_list_url = reverse("player-list")

    @pytest.mark.order(1)
    def test_list_players_initially_empty(self):
        """
        GET /api/players/ should return an empty list when no players exist.
        """
        response = self.client.get(self.player_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 0)

    @pytest.mark.order(2)
    def test_create_player_and_see_in_list(self):
        """
        POST /api/players/ should create a player, and subsequent GET should include it.
        """
        create_data = {"name": "Alice"}
        create_response = self.client.post(self.player_list_url, create_data, format="json")

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create_response.data["name"], "Alice")
        player_id = create_response.data["id"]
        self.assertTrue(Player.objects.filter(id=player_id, name="Alice").exists())

        # Now list players and check Alice is there
        list_response = self.client.get(self.player_list_url)
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(list_response.data, list)
        names = [p["name"] for p in list_response.data]
        self.assertIn("Alice", names)

    @pytest.mark.order(3)
    def test_update_player(self):
        """
        PUT /api/players/<id>/ should update an existing player.
        """
        # First create a player
        create_response = self.client.post(self.player_list_url, {"name": "Old Name"}, format="json")
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        player_id = create_response.data["id"]

        player_detail_url = reverse("player-detail", kwargs={"pk": player_id})

        update_data = {"name": "New Name"}
        update_response = self.client.put(player_detail_url, update_data, format="json")

        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data["name"], "New Name")
        self.assertTrue(Player.objects.filter(id=player_id, name="New Name").exists())

    @pytest.mark.order(4)
    def test_delete_player(self):
        """
        DELETE /api/players/<id>/ should remove the player.
        """
        # Create a player to delete
        create_response = self.client.post(self.player_list_url, {"name": "To Delete"}, format="json")
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        player_id = create_response.data["id"]

        player_detail_url = reverse("player-detail", kwargs={"pk": player_id})

        delete_response = self.client.delete(player_detail_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Player.objects.filter(id=player_id).exists())