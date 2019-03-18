import pytest

from tests.internal.apps.smear.factories import HandFactory


@pytest.fixture
def authed_client():
    def client_generator(user):
        from rest_framework.test import APIClient
        client = APIClient()
        if not user:
            return client
        client.force_authenticate(user=user)

        return client

    return client_generator


@pytest.fixture
def bid_context():
    def context_generator(high_bid):
        hand = HandFactory()
        hand.high_bid.bid = high_bid
        return {
            'extra_kwargs': {'hand': hand}
        }
    return context_generator
