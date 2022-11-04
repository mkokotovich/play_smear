import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from apps.smear.serializers import GameSerializer
from tests.internal.apps.smear.factories import GameFactory, PlayerFactory
from tests.internal.apps.user.factories import UserFactory


@pytest.mark.django_db
def test_game_viewset_list(authed_client):
    games = [GameFactory() for i in range(3)]
    url = reverse('games-list')
    client = authed_client(games[0].owner)

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    results = sorted(response_json.pop('results'), key=lambda game: game['id'])
    expected_results = sorted([GameSerializer(game).data for game in games], key=lambda game: game['id'])
    assert response_json == {
        'count': 3,
        'next': None,
        'previous': None,
    }
    assert expected_results == results


@pytest.mark.django_db
@pytest.mark.parametrize('owner', [True, False])
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
