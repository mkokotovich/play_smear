import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from apps.smear.serializers import TeamSummarySerializer
from tests.internal.apps.smear.factories import GameFactory, PlayerFactory, TeamFactory
from tests.internal.apps.user.factories import UserFactory


@pytest.mark.django_db
def test_team_viewset_list(authed_client):
    owner_user = UserFactory()
    game = GameFactory(owner=owner_user, num_players=2, num_teams=2)
    team = TeamFactory(game=game)
    PlayerFactory(user=owner_user, game=game, team=team)
    TeamFactory()

    url = reverse("teams-list", kwargs={"game_id": game.id})
    client = authed_client(owner_user)

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    results = sorted(response_json.pop("results"), key=lambda team: team["id"])
    expected_results = sorted([TeamSummarySerializer(team).data], key=lambda team: team["id"])
    assert response_json == {
        "count": 1,
        "next": None,
        "previous": None,
    }
    assert expected_results == results


@pytest.mark.django_db
@pytest.mark.parametrize("owner", [True, False])
@pytest.mark.parametrize("on_team", [True, False])
def test_team_viewset_rename(authed_client, owner, on_team):
    owner_user = UserFactory()
    regular_user = UserFactory()
    game = GameFactory(owner=owner_user, num_players=2, num_teams=2)
    team1 = TeamFactory(game=game)
    team2 = TeamFactory(game=game)
    PlayerFactory(user=owner_user, game=game, team=team1)
    PlayerFactory(user=regular_user, game=game, team=team2)
    owner_client = authed_client(owner_user)
    regular_client = authed_client(regular_user)
    if owner:
        if on_team:
            team = team1
        else:
            team = team2
    else:
        if on_team:
            team = team2
        else:
            team = team1

    url = reverse("teams-detail", kwargs={"game_id": game.id, "pk": team.id})

    client = owner_client if owner else regular_client
    response = client.patch(url, json={"name": "cool new name"})

    assert response.status_code == status.HTTP_200_OK if owner or on_team else status.HTTP_403_FORBIDDEN
    if owner or on_team:
        assert response.json() == TeamSummarySerializer(team).data
