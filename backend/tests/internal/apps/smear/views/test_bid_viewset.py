import pytest

from rest_framework.reverse import reverse
from rest_framework import status

from apps.smear.serializers import BidSerializer
from tests.internal.apps.smear.factories import BidFactory, HandFactory, PlayerFactory, GameFactory, TeamFactory
from tests.internal.apps.user.factories import UserFactory
from tests.utils import NotNull


@pytest.mark.django_db
def test_bid_viewset_list(authed_client):
    hand = HandFactory()
    PlayerFactory(user=hand.game.owner, game=hand.game, team=None)
    bids = [hand.high_bid, *[BidFactory(hand=hand) for i in range(3)]]
    url = reverse('bids-list', kwargs={'game_id': hand.game.id, 'hand_id': hand.id})
    client = authed_client(hand.game.owner)

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    results = sorted(response_json.pop('results'), key=lambda bid: bid['id'])
    expected_results = sorted([BidSerializer(bid).data for bid in bids], key=lambda bid: bid['id'])
    assert response_json == {
        'count': len(bids),
        'next': None,
        'previous': None,
    }
    assert expected_results == results


@pytest.mark.django_db
@pytest.mark.parametrize('is_bidder', [True, False])
def test_bid_viewset_create_fails_if_not_current_bidder(authed_client, is_bidder):
    owner_user = UserFactory()
    regular_user = UserFactory()
    game = GameFactory(owner=owner_user, num_players=2, num_teams=2)
    team1 = TeamFactory(game=game)
    team2 = TeamFactory(game=game)
    PlayerFactory(user=owner_user, game=game, team=team1)
    PlayerFactory(user=regular_user, game=game, team=team2)
    game.start_game()
    owner_client = authed_client(owner_user)
    regular_client = authed_client(regular_user)
    bid_data = {
        'bid': 2,
    }
    url = reverse('bids-list', kwargs={'game_id': game.id, 'hand_id': game.hands.last().id})

    bidder_client = owner_client if game.current_hand.bidder.user == owner_user else regular_client
    non_bidder_client = owner_client if game.current_hand.bidder.user != owner_user else regular_client
    client = bidder_client if is_bidder else non_bidder_client
    response = client.post(url, format="json", data=bid_data)

    if is_bidder:
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {
            'id': NotNull,
            'bid': bid_data['bid'],
            'player': NotNull,
        }
    else:
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "turn to bid" in response.json()['error']['validation_errors']['meta'][0]
