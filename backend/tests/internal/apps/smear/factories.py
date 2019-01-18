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


class HandFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'smear.Hand'
    game = factory.SubFactory('tests.internal.apps.smear.factories.GameFactory')


class PlayerFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'smear.Player'
    user = factory.SubFactory('tests.internal.apps.user.factories.UserFactory')
    game = factory.SubFactory('tests.internal.apps.smear.factories.GameFactory')


class GameFactoryWithPlayer(GameFactory):
    membership = factory.RelatedFactory(PlayerFactory, 'game')
