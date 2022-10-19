from apps.smear.cards import Card


def computer_bid(player, hand):
    # TODO: bidding logic
    bid_value = 0 if hand.high_bid else 2
    trump_value = Card(representation=player.cards_in_hand[0]).suit

    return bid_value, trump_value


def computer_play_card(player, trick):
  # TODO: playing logic
    card = next((card for card in player.get_cards() if not trick.is_card_invalid_to_play(card, player)), None)
    assert card is not None, f'unable to find a card for {player}, {player.cards_in_hand} are all invalid'

    return card
