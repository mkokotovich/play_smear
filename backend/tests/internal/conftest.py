import pytest


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
