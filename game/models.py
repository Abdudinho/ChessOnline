from django.db import models
import uuid


class Game(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    white = models.CharField(max_length=50, blank=True, null=True)
    black = models.CharField(max_length=50, blank=True, null=True)
    fen = models.TextField(default="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    status = models.CharField(max_length=20, default="waiting")  # waiting, playing, finished
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)
