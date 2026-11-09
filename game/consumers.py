import json
import chess
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Game


class ChessConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.room_group_name = f'game_{self.game_id}'
        self.player_color = None

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        game = await self.get_game()
        if game:
            await self.send(text_data=json.dumps({
                'type': 'game_state',
                'fen': game.fen,
                'status': game.status,
                'white': game.white,
                'black': game.black,
            }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'join':
            color = data.get('color')
            name = data.get('name', 'Player')
            await self.join_game(color, name)

        elif action == 'move':
            move = data.get('move')
            await self.make_move(move)

    async def join_game(self, color, name):
        game = await self.get_game()
        if not game:
            return

        if color == 'white' and not game.white:
            game.white = name
            self.player_color = 'white'
        elif color == 'black' and not game.black:
            game.black = name
            self.player_color = 'black'
        else:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Bu rang allaqachon band'
            }))
            return

        if game.white and game.black:
            game.status = 'playing'

        await self.save_game(game)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_update',
                'fen': game.fen,
                'status': game.status,
                'white': game.white,
                'black': game.black,
            }
        )

    async def make_move(self, move_uci):
        game = await self.get_game()
        if not game or game.status != 'playing':
            return

        board = chess.Board(game.fen)

        try:
            move = chess.Move.from_uci(move_uci)
            if move not in board.legal_moves:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Noto‘g‘ri yurish'
                }))
                return

            board.push(move)
            game.fen = board.fen()

            if board.is_checkmate():
                game.status = 'finished'
            elif board.is_stalemate() or board.is_insufficient_material():
                game.status = 'finished'

            await self.save_game(game)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'move_made',
                    'move': move_uci,
                    'fen': game.fen,
                    'status': game.status,
                }
            )
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    @database_sync_to_async
    def get_game(self):
        try:
            return Game.objects.get(id=self.game_id)
        except Game.DoesNotExist:
            return None

    @database_sync_to_async
    def save_game(self, game):
        game.save()

    async def game_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_state',
            'fen': event['fen'],
            'status': event['status'],
            'white': event['white'],
            'black': event['black'],
        }))

    async def move_made(self, event):
        await self.send(text_data=json.dumps({
            'type': 'move',
            'move': event['move'],
            'fen': event['fen'],
            'status': event['status'],
        }))
