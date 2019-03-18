import factory


class GameFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'smear.Game'
    owner = factory.SubFactory('tests.internal.apps.user.factories.UserFactory')
    name = factory.Faker("name")
    num_players = 4
    num_teams = 2
    score_to_play_to = 11
    passcode_required = factory.Faker("boolean")
    passcode = factory.Faker("text", max_nb_chars=64)
    single_player = factory.Faker("boolean")


class TeamFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'smear.Team'
    game = factory.SubFactory('tests.internal.apps.smear.factories.GameFactory')
    name = factory.Faker("name")


class HandFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'smear.Hand'
    game = factory.SubFactory('tests.internal.apps.smear.factories.GameFactory')

    @factory.post_generation
    def high_bid(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            self.high_bid = extracted
        else:
            self.high_bid = BidFactory(hand=self)


class PlayerFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'smear.Player'
    user = factory.SubFactory('tests.internal.apps.user.factories.UserFactory')
    game = factory.SubFactory('tests.internal.apps.smear.factories.GameFactory')


class GameFactoryWithPlayer(GameFactory):
    membership = factory.RelatedFactory(PlayerFactory, 'game')


class BidFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'smear.Bid'
    hand = factory.SubFactory('tests.internal.apps.smear.factories.HandFactory')
    player = factory.SubFactory('tests.internal.apps.smear.factories.PlayerFactory')
    bid = 2
