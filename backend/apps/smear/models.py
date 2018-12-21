from django.db import models


class Game(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey('auth.User', related_name='games', on_delete=models.CASCADE)

    class Meta:
        ordering = ('created_at',)
