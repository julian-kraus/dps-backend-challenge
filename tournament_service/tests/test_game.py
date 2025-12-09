import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from tournaments.models import Tournament, TournamentParticipant, Game
from players.models import Player


class GameAPITests(APITestCase):
    def _create_tournament(self, name="Test Tournament"):
        return Tournament.objects.create(name=name)

    def _create_player(self, name="Test Player"):
        return Player.objects.create(name=name)

    def _create_participant(self, tournament, player):
        return TournamentParticipant.objects.create(tournament=tournament, player=player)

    def _add_game_url(self, tournament_id: int):
        return reverse("add-game", kwargs={"tournament_id": tournament_id})

    @pytest.mark.order(13)
    def test_add_game_success_home_wins(self):
        tournament = self._create_tournament("Winner Cup")
        p1 = self._create_player("Alice")
        p2 = self._create_player("Bob")

        home_p = self._create_participant(tournament, p1)
        away_p = self._create_participant(tournament, p2)

        url = self._add_game_url(tournament.id)
        payload = {
            "home_participant": home_p.id,
            "away_participant": away_p.id,
            "winner": p1.id,  # home wins
        }

        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["home_score"], 2)
        self.assertEqual(response.data["away_score"], 0)

    @pytest.mark.order(14)
    def test_add_game_draw(self):
        tournament = self._create_tournament("Draw Cup")
        p1 = self._create_player("Alice")
        p2 = self._create_player("Bob")

        home_p = self._create_participant(tournament, p1)
        away_p = self._create_participant(tournament, p2)

        url = self._add_game_url(tournament.id)
        payload = {
            "home_participant": home_p.id,
            "away_participant": away_p.id,
            "winner": None,  # draw
        }

        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["home_score"], 1)
        self.assertEqual(response.data["away_score"], 1)

    @pytest.mark.order(15)
    def test_add_game_invalid_winner_not_in_match(self):
        tournament = self._create_tournament("Wrong Winner Cup")
        p1 = self._create_player("Alice")
        p2 = self._create_player("Bob")
        p3 = self._create_player("Charlie")  # invalid winner

        home_p = self._create_participant(tournament, p1)
        away_p = self._create_participant(tournament, p2)

        url = self._add_game_url(tournament.id)
        payload = {
            "home_participant": home_p.id,
            "away_participant": away_p.id,
            "winner": p3.id,  # not one of the two
        }

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Winner must be one of the participants", response.data["detail"])

    @pytest.mark.order(16)
    def test_add_game_participants_not_in_tournament(self):
        tournament = self._create_tournament("Tournament A")
        other_t = self._create_tournament("Tournament B")

        p1 = self._create_player("A")
        p2 = self._create_player("B")

        # Participants of other tournament
        home_p = self._create_participant(other_t, p1)
        away_p = self._create_participant(other_t, p2)

        url = self._add_game_url(tournament.id)
        payload = {
            "home_participant": home_p.id,
            "away_participant": away_p.id,
            "winner": p1.id,
        }

        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @pytest.mark.order(17)
    def test_add_game_duplicate_pair(self):
        tournament = self._create_tournament("Duplicate Cup")
        p1 = self._create_player("A")
        p2 = self._create_player("B")

        home_p = self._create_participant(tournament, p1)
        away_p = self._create_participant(tournament, p2)

        url = self._add_game_url(tournament.id)

        # First game OK
        response1 = self.client.post(url, {
            "home_participant": home_p.id,
            "away_participant": away_p.id,
            "winner": p1.id,
        }, format="json")
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        # Duplicate should fail
        response2 = self.client.post(url, {
            "home_participant": home_p.id,
            "away_participant": away_p.id,
            "winner": p2.id,
        }, format="json")
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)