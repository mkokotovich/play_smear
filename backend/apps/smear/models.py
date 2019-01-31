from random import shuffle
import logging

from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from rest_framework.exceptions import ValidationError

from apps.smear.cards import Card, Deck


LOG = logging.getLogger(__name__)


class Game(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    owner = models.ForeignKey('auth.User', related_name='games', on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=256, blank=True, default="")
    num_players = models.IntegerField()
    num_teams = models.IntegerField()
    score_to_play_to = models.IntegerField()
    passcode_required = models.BooleanField(blank=True, default=False)
    passcode = models.CharField(max_length=256, blank=True, default="")
    single_player = models.BooleanField(blank=False, default=True)
    players = models.ManyToManyField('auth.User', through='Player')

    class Meta:
        ordering = ('created_at',)

    def get_status(self):
        if self.hands.count() == 0:
            return {
                'state': 'waiting_for_start',
                'metadata': {},
            }
        return self.hands.last().get_status()

    def start(self, start_data):
        if self.players.count() != self.num_players:
            raise ValidationError(f"Unable to start game, game requires {self.num_players} players, but {self.players.count()} have joined")

        self.set_teams_and_seats(start_data)

        hand = Hand.objects.create(game=self)
        hand.start()
        # hand.advance_bidding()
        LOG.info(f"Started hand {hand} on game {self}")

    def create_initial_teams(self):
        for i in range(0, self.num_teams):
            Team.objects.create(game=self, name=f"Team {i+1}")

    def set_teams_and_seats(self, start_data):
        teams = start_data.get('teams', [])
        if len(teams) != self.num_teams:
            raise ValidationError(f"Unable to start game, {len(teams)} were supplied but {self.num_teams} were expected")

        # Assign players to their teams (if necessary)
        for team_num, teamMeta in enumerate(teams):
            try:
                team = self.teams.get(id=teamMeta['id'])
            except Team.DoesNotExist:
                raise ValidationError(
                    f"Unable to start game, team with id {teamMeta['id']} was "
                    "given but could not be found"
                )

            for player_num, player_obj in enumerate(teamMeta['players']):
                try:
                    player = self.player_set.get(id=player_obj['id'])
                except Player.DoesNotExist:
                    raise ValidationError(
                        f"Unable to start game, player id {player_obj['id']} was "
                        f"listed as a member of team {team} but could "
                        "not be found in this game"
                    )
                player.team = team
                player.seat = team_num + (self.num_teams * player_num)
                LOG.info(f"Added {player.name} to game {self.name}, team {team}, at seat {player.seat}")
                player.save()

        if not teams:
            for player_num, player in enumerate(self.player_set.all()):
                player.seat = player_num
                LOG.info(f"Added {player.name} to game {self.name} at seat {player.seat}")
                player.save()

    def add_computer_player(self):
        if self.players.count() >= self.num_players:
            raise ValidationError(f"Unable to add computer, already containers {self.num_players} players")

        computers = list(User.objects.filter(username__startswith="mkokotovich+computer").all())
        shuffle(computers)
        for computer in computers:
            if not self.players.filter(id=computer.id).exists():
                computer_player = Player.objects.create(
                    game=self,
                    user=computer,
                    is_computer=True
                )
                LOG.info(f"Added computer {computer} to {self}")
                return computer_player


class Team(models.Model):
    game = models.ForeignKey(Game, related_name='teams', on_delete=models.CASCADE)
    name = models.CharField(max_length=1024)

    def __str__(self):
        return f"{self.name} ({self.id})"


class Player(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    is_computer = models.BooleanField(blank=True, default=False)
    name = models.CharField(max_length=1024)
    team = models.ForeignKey(Team, related_name='players', on_delete=models.CASCADE, null=True, blank=True)
    seat = models.IntegerField(blank=True, null=True)

    cards_in_hand = ArrayField(
        models.CharField(max_length=2),
        default=list
    )

    def __init__(self, *args, **kwargs):
        name = kwargs.pop('name', self._get_name_from_user(kwargs.get('user', None)))
        super().__init__(name=name, *args, **kwargs)

    def _get_name_from_user(self, user):
        if not user:
            return 'Unknown'
        name = user.first_name + f"{' ' + user.last_name[:1] if user.last_name else ''}"
        if not name:
            name = user.username.split('@')[0]
        return name

    def accept_dealt_cards(self, cards):
        representations = [card.to_representation() for card in cards]
        self.cards_in_hand.extend(representations)
        self.save()

    def get_cards(self):
        return [Card(representation=rep) for rep in self.cards_in_hand]


class Hand(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    game = models.ForeignKey(Game, related_name='hands', on_delete=models.CASCADE, null=True)

    def get_status(self):
        return {
            'state': 'bidding',
            'metadata': {
                'hand': self.id,
            },
        }

    def start(self):
        # Deal out six cards
        deck = Deck()
        for player in self.game.player_set.all():
            player.accept_dealt_cards(deck.deal(3))
        for player in self.game.player_set.all():
            player.accept_dealt_cards(deck.deal(3))

    def advance_bidding(self):
        pass
