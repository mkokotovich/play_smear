from rest_framework import serializers

from apps.smear.models import Game


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = '__all__'
