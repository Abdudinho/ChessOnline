from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.create_game, name='create_game'),
    path('game/<uuid:game_id>/', views.game_room, name='game_room'),
]
