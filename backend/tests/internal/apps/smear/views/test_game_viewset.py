import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from apps.smear.serializers import GameSerializer
from tests.internal.apps.smear.factories import GameFactory, PlayerFactory
from tests.internal.apps.user.factories import UserFactory
from tests.utils import NotNull


@pytest.mark.django_db
def test_game_viewset_list(authed_client):
    games = [GameFactory() for i in range(3)]
    url = reverse("games-list")
    client = authed_client(games[0].owner)

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    results = sorted(response_json.pop("results"), key=lambda game: game["id"])
    expected_results = sorted([GameSerializer(game).data for game in games], key=lambda game: game["id"])
    assert response_json == {
        "count": 3,
        "next": None,
        "previous": None,
    }
    assert expected_results == results


@pytest.mark.django_db
@pytest.mark.parametrize("owner", [True, False])
def test_game_viewset_start(authed_client, owner):
    owner_user = UserFactory()
    regular_user = UserFactory()
    game = GameFactory(owner=owner_user, num_players=2)
    PlayerFactory(user=owner_user, game=game)
    PlayerFactory(user=regular_user, game=game)
    owner_client = authed_client(owner_user)
    regular_client = authed_client(regular_user)
    url = f"{reverse('games-detail', kwargs={'pk': game.id})}start/"

    client = owner_client if owner else regular_client
    response = client.post(url)

    assert response.status_code == status.HTTP_200_OK if owner else status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_game_viewset_status_bidding(authed_client, django_assert_num_queries, mocker):
    owner_user = UserFactory()
    game = GameFactory(owner=owner_user, num_players=4, num_teams=2)
    game.create_initial_teams()
    p1 = PlayerFactory(user=owner_user, game=game, is_computer=False)
    PlayerFactory(game=game, is_computer=True)
    PlayerFactory(game=game, is_computer=True)
    PlayerFactory(game=game, is_computer=True)
    game.autofill_teams()
    client = authed_client(owner_user)
    game.start_game()

    url = f"{reverse('games-detail', kwargs={'pk': game.id})}status/"

    with django_assert_num_queries(11):
        response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    p1.refresh_from_db()
    assert response.json() == {
        "current_hand": {
            "bidder": game.current_hand.bidder.id,
            "bids": NotNull,
            "cards": p1.cards_in_hand,
            "dealer": game.current_hand.dealer.id,
            "high_bid": mocker.ANY,
            "finished": False,
            "id": game.current_hand.id,
            "num": game.current_hand.num,
            "results": None,
            "trump": "",
        },
        "state": "bidding",
        "players": NotNull,
        "teams": NotNull,
    }


@pytest.mark.django_db
def test_game_viewset_create(authed_client, django_assert_num_queries):
    owner_user = UserFactory()
    client = authed_client(owner_user)

    url = reverse("games-list")
    new_game_data = {
        "name": "test",
        "num_players": 6,
        "num_teams": 3,
        "score_to_play_to": 11,
        "single_player": True,
    }

    with django_assert_num_queries(13):
        response = client.post(url, data=new_game_data)

    assert response.status_code == status.HTTP_201_CREATED
