import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from apps.smear.cards import Card
from apps.smear.models import Play
from tests.internal.apps.smear.factories import HandFactory, PlayerFactory, PlayFactory, TrickFactory


@pytest.mark.django_db
def test_play_viewset_submit_invalid_card_is_atomic(authed_client):
    hand = HandFactory(game__num_players=3, game__num_teams=0)
    trump = hand.high_bid.trump
    trump_rep = trump[:1].upper()
    other_suit = Card.jick_suit(trump)
    other_rep = other_suit[:1].upper()
    p1_card_reps = [
        f"A{trump_rep}",
        f"K{trump_rep}",
        f"Q{trump_rep}",
        f"J{trump_rep}",
        f"0{trump_rep}",
        f"2{trump_rep}",
    ]
    p1 = PlayerFactory(user=hand.game.owner, game=hand.game, team=None, cards_in_hand=p1_card_reps)
    p2_card_reps = [
        f"3{trump_rep}",
        f"9{other_rep}",
        f"8{other_rep}",
        f"7{other_rep}",
        f"6{other_rep}",
        f"5{other_rep}",
    ]
    p2 = PlayerFactory(game=hand.game, team=None, cards_in_hand=p2_card_reps)
    p3_card_reps = [
        f"4{trump_rep}",
        f"5{trump_rep}",
        f"6{trump_rep}",
        f"4{other_rep}",
        f"3{other_rep}",
        f"2{other_rep}",
    ]
    PlayerFactory(game=hand.game, team=None, cards_in_hand=p3_card_reps)
    trick = TrickFactory(hand=hand)

    url = reverse(
        "plays-list",
        kwargs={
            "game_id": hand.game.id,
            "hand_id": hand.id,
            "trick_id": trick.id,
        },
    )
    client = authed_client(p2.user)
    PlayFactory(trick=trick, player=p1, card=f"A{trump_rep}")
    play_data = {"card": f"9{other_rep}"}
    num_plays_before = Play.objects.filter(trick=trick).count()

    response = client.post(url, play_data)

    num_plays_after = Play.objects.filter(trick=trick).count()

    assert num_plays_before == num_plays_after
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_play_viewset_submit_out_of_order_is_atomic(authed_client):
    hand = HandFactory(game__num_players=3, game__num_teams=0)
    trump = hand.high_bid.trump
    trump_rep = trump[:1].upper()
    other_suit = Card.jick_suit(trump)
    other_rep = other_suit[:1].upper()
    p1_card_reps = [
        f"A{trump_rep}",
        f"K{trump_rep}",
        f"Q{trump_rep}",
        f"J{trump_rep}",
        f"0{trump_rep}",
        f"2{trump_rep}",
    ]
    p1 = PlayerFactory(user=hand.game.owner, game=hand.game, team=None, cards_in_hand=p1_card_reps)
    p2_card_reps = [
        f"3{trump_rep}",
        f"9{other_rep}",
        f"8{other_rep}",
        f"7{other_rep}",
        f"6{other_rep}",
        f"5{other_rep}",
    ]
    PlayerFactory(game=hand.game, team=None, cards_in_hand=p2_card_reps)
    p3_card_reps = [
        f"4{trump_rep}",
        f"5{trump_rep}",
        f"6{trump_rep}",
        f"4{other_rep}",
        f"3{other_rep}",
        f"2{other_rep}",
    ]
    p3 = PlayerFactory(game=hand.game, team=None, cards_in_hand=p3_card_reps)
    trick = TrickFactory(hand=hand)

    url = reverse(
        "plays-list",
        kwargs={
            "game_id": hand.game.id,
            "hand_id": hand.id,
            "trick_id": trick.id,
        },
    )
    client = authed_client(p3.user)

    # Player 1 leads Ace of Trump
    PlayFactory(trick=trick, player=p1, card=f"A{trump_rep}")

    # Player 3 plays a valid card, but out of order
    play_data = {"card": f"4{trump_rep}"}
    num_plays_before = Play.objects.filter(trick=trick).count()

    response = client.post(url, play_data)

    num_plays_after = Play.objects.filter(trick=trick).count()

    assert num_plays_before == num_plays_after
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_play_viewset_database_queries(authed_client, django_assert_num_queries):
    hand = HandFactory(game__num_players=3, game__num_teams=0)
    trump = hand.high_bid.trump
    trump_rep = trump[:1].upper()
    other_suit = Card.jick_suit(trump)
    other_rep = other_suit[:1].upper()
    p1_card_reps = [
        f"A{trump_rep}",
        f"K{trump_rep}",
        f"Q{trump_rep}",
        f"J{trump_rep}",
        f"0{trump_rep}",
        f"2{trump_rep}",
    ]
    p1 = PlayerFactory(user=hand.game.owner, game=hand.game, team=None, cards_in_hand=p1_card_reps)
    p2_card_reps = [
        f"3{trump_rep}",
        f"9{other_rep}",
        f"8{other_rep}",
        f"7{other_rep}",
        f"6{other_rep}",
        f"5{other_rep}",
    ]
    p2 = PlayerFactory(game=hand.game, team=None, cards_in_hand=p2_card_reps)
    p3_card_reps = [
        f"4{trump_rep}",
        f"5{trump_rep}",
        f"6{trump_rep}",
        f"4{other_rep}",
        f"3{other_rep}",
        f"2{other_rep}",
    ]
    p3 = PlayerFactory(game=hand.game, team=None, cards_in_hand=p3_card_reps, is_computer=True)
    hand.game.set_seats()
    hand.game.set_plays_after()
    trick = TrickFactory(hand=hand)
    hand.dealer = p3
    hand.bidder = p1
    hand.save()
    trick.start_trick(p1)

    url = reverse(
        "plays-list",
        kwargs={
            "game_id": hand.game.id,
            "hand_id": hand.id,
            "trick_id": trick.id,
        },
    )
    client1 = authed_client(p1.user)
    client2 = authed_client(p2.user)

    # Player 1 leads Ace of Trump
    play_data = {"card": f"A{trump_rep}"}
    with django_assert_num_queries(17):
        response = client1.post(url, play_data)
        assert response.status_code == status.HTTP_201_CREATED, response.json()

    # Player 2 plays a valid card
    play_data = {"card": f"3{trump_rep}"}

    # This used to be 119!!!
    with django_assert_num_queries(33):
        response = client2.post(url, play_data)
        assert response.status_code == status.HTTP_201_CREATED, response.json()
