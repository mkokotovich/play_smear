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

    def start(self):
        if self.players.count() != self.num_players:
            raise ValidationError(f"Unable to start game, game requires {self.num_players} players, but {self.players.count()} have joined")

        hand = Hand.objects.create(game=self)
        LOG.info(f"Started hand {hand} on game {self}")

    def add_computer_player(self):
        computers = list(User.objects.filter(username__startswith="mkokotovich+computer").all())
        shuffle(computers)
        for player in computers:
            if not self.players.filter(id=player.id).exists():
                Player.objects.create(
                    game=self,
                    user=player,
                    is_computer=True
                )
                LOG.info(f"Added computer {player} to {self}")
                return


class Player(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    is_computer = models.BooleanField(blank=True, default=False)
    name = models.CharField(max_length=1024)
    team = models.CharField(max_length=1024)

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
        for player in self.game.players.all():
            player.accept_dealt_cards(deck.deal(3))
        for player in self.game.players.all():
            player.accept_dealt_cards(deck.deal(3))
