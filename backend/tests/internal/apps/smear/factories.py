import factory

from apps.smear.models import Hand
from tests.internal.apps.user.factories import UserFactory


class GameFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "smear.Game"

    owner = factory.SubFactory("tests.internal.apps.user.factories.UserFactory")
    name = factory.Faker("name")
    num_players = 4
    num_teams = 2
    score_to_play_to = 11
    passcode_required = factory.Faker("boolean")
    passcode = factory.Faker("text", max_nb_chars=64)
    single_player = factory.Faker("boolean")


class TeamFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "smear.Team"

    game = factory.SubFactory("tests.internal.apps.smear.factories.GameFactory")
    name = factory.Faker("name")


class HandFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "smear.Hand"

    game = factory.SubFactory("tests.internal.apps.smear.factories.GameFactory")
    num = 1

    @factory.post_generation
    def high_bid(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            self.high_bid = extracted
        else:
            self.high_bid = BidFactory(hand=self, bid=5, trump="spades")


class TrickFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "smear.Trick"

    hand = factory.SubFactory("tests.internal.apps.smear.factories.HandFactory")
    num = 1


class PlayerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "smear.Player"

    user = factory.SubFactory("tests.internal.apps.user.factories.UserFactory")
    game = factory.SubFactory("tests.internal.apps.smear.factories.GameFactory")


class GameFactoryWithPlayer(GameFactory):
    membership = factory.RelatedFactory(PlayerFactory, "game")


class GameFactoryWithHandsAndTricks(GameFactory):
    @factory.post_generation
    def hands(game, create, extracted, **kwargs):
        if not create:
            return

        users = UserFactory.create_batch(4)
        players = [PlayerFactory(user=u, game=game) for u in users]
        for h in range(4):
            hand = Hand.objects.create(game=game, num=h)
            for t in range(6):
                trick = TrickFactory(hand=hand, num=t)
                for p in range(len(players)):
                    PlayFactory(trick=trick, player=players[p])


class BidFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "smear.Bid"

    hand = factory.SubFactory("tests.internal.apps.smear.factories.HandFactory")
    player = factory.SubFactory("tests.internal.apps.smear.factories.PlayerFactory")
    bid = 2


class PlayFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "smear.Play"

    trick = factory.SubFactory("tests.internal.apps.smear.factories.TrickFactory")
    player = factory.SubFactory("tests.internal.apps.smear.factories.PlayerFactory")
    card = "AS"
