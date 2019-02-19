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
        game.start()


@pytest.mark.django_db()
def test_Game_start(mocker):
    num_players = 6
    game = GameFactory(num_players=num_players)
    [Player.objects.create(game=game, user=UserFactory()) for i in range(0, num_players)]
    mock_set_seats = mocker.patch.object(game, 'set_seats')
    mock_hand_class = mocker.patch('apps.smear.models.Hand')
    mock_hand = mocker.Mock()
    mock_hand_class.objects.create.return_value = mock_hand

    game.start()

    assert mock_set_seats.mock_calls == [
        mocker.call(),
    ]

    assert mocker.call(game=game) in mock_hand_class.objects.create.mock_calls

    assert mock_hand.start.mock_calls == [
        mocker.call()
    ]


@pytest.mark.django_db()
@pytest.mark.parametrize('num_players', [2, 4, 6, 8])
@pytest.mark.parametrize('num_teams', [0, 2, 3, 4])
def test_Game_set_seats(mocker, num_teams, num_players):
    if num_teams != 0 and num_players % num_teams != 0:
        pytest.skip(f"Uneven number of player ({num_players}) for teams ({num_teams})")

    game = GameFactory(num_players=num_players, num_teams=num_teams)
    game.create_initial_teams()
    teams = list(game.teams.all())
    players = [Player.objects.create(game=game, user=UserFactory()) for i in range(0, num_players)]
    if num_teams != 0:
        for player_num, player in enumerate(players):
            player.team = teams[player_num % num_teams]
            player.save()

    game.set_seats()

    for team_num, team in enumerate(teams):
        for player_num, player in enumerate(team.members.all()):
            db_player = Player.objects.get(id=player.id)
            assert db_player in players
            assert db_player.game == game
            assert db_player.seat == team_num + player_num * num_teams

    if num_teams == 0:
        game_players = Player.objects.filter(game=game).order_by('seat')
        for player_num, db_player in enumerate(game_players):
            assert db_player in players
            assert db_player.game == game
            assert db_player.seat == player_num


@pytest.mark.django_db()
@pytest.mark.parametrize('num_players', [2, 4, 6, 8])
@pytest.mark.parametrize('num_teams', [2, 3, 4])
def test_Game_autofill_teams(mocker, num_teams, num_players):
    if num_teams != 0 and num_players % num_teams != 0:
        pytest.skip(f"Uneven number of player ({num_players}) for teams ({num_teams})")

    game = GameFactory(num_players=num_players, num_teams=num_teams)
    game.create_initial_teams()
    players = [Player.objects.create(game=game, user=UserFactory()) for i in range(0, num_players)]

    game.autofill_teams()

    teams = list(game.teams.all())
    total_members = 0
    for team_num, team in enumerate(teams):
        for player_num, player in enumerate(team.members.all()):
            db_player = Player.objects.get(id=player.id)
            assert db_player in players
            assert db_player.game == game
            total_members += 1
    assert total_members == game.num_players
