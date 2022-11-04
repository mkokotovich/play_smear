import pytest

from apps.smear.serializers import BidSerializer


@pytest.mark.django_db
@pytest.mark.parametrize(
    "suit,expected_valid",
    [
        ("SpaDes", True),
        ("spades", True),
        ("spaades", False),
        ("Diamonds", True),
        ("hearts", True),
        ("clubs", True),
        ("S", False),
        (7, False),
        ("long string that is more than 16", False),
    ],
)
def test_is_valid_verifies_suit(bid_context, suit, expected_valid):
    serializer = BidSerializer(data={"trump": suit, "bid": 0}, context=bid_context(high_bid=2))

    assert expected_valid == serializer.is_valid()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "high_bid,bid,expected_valid",
    [
        (0, 0, True),
        (0, 2, True),
        (0, 5, True),
        (2, 0, True),
        (2, 3, True),
        (0, 6, False),
        (0, -1, False),
        (3, 2, False),
        (3, 3, False),
    ],
)
def test_is_valid_verifies_bid(bid_context, high_bid, bid, expected_valid):
    serializer = BidSerializer(data={"bid": bid}, context=bid_context(high_bid=high_bid))

    assert expected_valid == serializer.is_valid()
