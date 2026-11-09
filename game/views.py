from django.shortcuts import render, redirect
from .models import Game


def home(request):
    return render(request, 'game/home.html')


def create_game(request):
    game = Game.objects.create()
    return redirect('game_room', game_id=game.id)


def game_room(request, game_id):
    try:
        game = Game.objects.get(id=game_id)
    except Game.DoesNotExist:
        return redirect('home')
    return render(request, 'game/room.html', {'game': game})
