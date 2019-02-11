import pytest

from rest_framework.exceptions import ValidationError

from apps.smear.models import Player
from tests.internal.apps.smear.factories import GameFactory
from tests.internal.apps.user.factories import UserFactory


@pytest.mark.django_db()
def test_Game_start_fails_if_not_enough_players():
    num_players = 6
    game = GameFactory(num_players=num_players)
    [Player.objects.create(game=game, user=UserFactory()) for i in range(0, num_players - 1)]

    with pytest.raises(ValidationError):
        game.start({})


@pytest.mark.django_db()
def test_Game_start(mocker):
    num_players = 6
    game = GameFactory(num_players=num_players)
    [Player.objects.create(game=game, user=UserFactory()) for i in range(0, num_players)]
    mock_set_teams_and_seats = mocker.patch.object(game, 'set_teams_and_seats')
    mock_hand_class = mocker.patch('apps.smear.models.Hand')
    mock_hand = mocker.Mock()
    mock_hand_class.objects.create.return_value = mock_hand

    game.start(mocker.sentinel.DATA)

    assert mock_set_teams_and_seats.mock_calls == [
        mocker.call(mocker.sentinel.DATA),
    ]

    assert mocker.call(game=game) in mock_hand_class.objects.create.mock_calls

    assert mock_hand.start.mock_calls == [
        mocker.call()
    ]


@pytest.mark.django_db()
@pytest.mark.parametrize('num_players', [2, 4, 6, 8])
@pytest.mark.parametrize('num_teams', [0, 2, 3, 4])
def test_Game_set_teams_and_seats_with_teams(mocker, num_teams, num_players):
    if num_teams != 0 and num_players % num_teams != 0:
        pytest.skip(f"Uneven number of player ({num_players}) for teams ({num_teams})")

    game = GameFactory(num_players=num_players, num_teams=num_teams)
    game.create_initial_teams()
    players = [Player.objects.create(game=game, user=UserFactory()) for i in range(0, num_players)]

    start_data = {
        'teams': [
            {
                'id': team.id,
                'players': [
                    {'id': player.id}
                    for player_num, player in enumerate(players) if player_num % num_teams == team_num
                ]
            } for team_num, team in enumerate(list(game.teams.all()))
        ]
    } if num_teams != 0 else {}

    game.set_teams_and_seats(start_data)

    for team_num, team in enumerate(start_data.get('teams', [])):
        for player_num, player in enumerate(team['players']):
            db_player = Player.objects.get(id=player['id'])
            assert db_player in players
            assert db_player.game == game
            assert db_player.seat == team_num + player_num * num_teams

    if num_teams == 0:
        game_players = Player.objects.filter(game=game).order_by('seat')
        for player_num, db_player in enumerate(game_players):
            assert db_player in players
            assert db_player.game == game
            assert db_player.seat == player_num
