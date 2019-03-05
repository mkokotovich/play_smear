import pytest

from rest_framework.reverse import reverse
from rest_framework import status

from apps.smear.serializers import BidSerializer
from tests.internal.apps.smear.factories import BidFactory, HandFactory


@pytest.mark.django_db
def test_bid_viewset_list(authed_client):
    hand = HandFactory()
    bids = [BidFactory(hand=hand) for i in range(3)]
    url = reverse('bids-list', kwargs={'game_id': hand.game.id, 'hand_id': hand.id})
    client = authed_client(hand.game.owner)

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    results = sorted(response_json.pop('results'), key=lambda bid: bid['id'])
    expected_results = sorted([BidSerializer(bid).data for bid in bids], key=lambda bid: bid['id'])
    assert response_json == {
        'count': 3,
        'next': None,
        'previous': None,
    }
    assert expected_results == results
