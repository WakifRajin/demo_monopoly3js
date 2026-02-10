import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.models import User
from monopoly.models import Profile
from .core.game import *
from monopoly.ws_handlers.game_handler import *
from monopoly.ws_handlers.game_change_handler import *

# Maintain these globally as the original code intended
rooms = {}
games = {}
changehandlers = {}


class MonopolyConsumer(WebsocketConsumer):
    def connect(self):
        # Use URL kwargs provided by URLRouter
        self.user = self.scope.get("user")
        route_kwargs = self.scope.get('url_route', {}).get('kwargs', {})
        self.mode = route_kwargs.get('mode')
        self.room_name = route_kwargs.get('room_name')

        # Accept the connection
        self.accept()

        if self.mode == 'join':
            self.handle_join()
        elif self.mode == 'game':
            # Add to game group
            async_to_sync(self.channel_layer.group_add)(
                self.room_name,
                self.channel_name
            )

            # --- ADD THIS LOGIC HERE ---
            # This triggers the 'init' message that hides the "Loading..." screen
            from monopoly.ws_handlers.game_handler import build_init_msg

            if self.room_name in games:
                game = games[self.room_name]
                players = game.get_players()
                profiles = list(rooms.get(self.room_name, []))

                cash_change = [p.get_money() for p in game.get_players()]
                pos_change = [p.get_position() for p in game.get_players()]
                owners = game.get_land_owners()

                # You might need to import get_building_type or just send 0s for now
                houses = [0] * 40

                init_msg = build_init_msg(profiles, cash_change, pos_change, "false", None,
                                          game.get_current_player().get_index(),
                                          None, None, owners, houses)

                try:
                    self.send(text_data=init_msg)
                except Exception:
                    pass

    def disconnect(self, close_code):
        # Equivalent to ws_disconnect
        try:
            async_to_sync(self.channel_layer.group_discard)(
                self.room_name,
                self.channel_name
            )
        except Exception:
            pass

    def receive(self, text_data):
        # Equivalent to ws_message
        msg = json.loads(text_data)
        action = msg.get("action")
        hostname = self.room_name

        if action == "start":
            handle_start(hostname)
        elif action == "roll":
            handle_roll(hostname, games, changehandlers)
        elif action == "confirm_decision":
            handle_confirm_decision(hostname, games)
        elif action == "cancel_decision":
            handle_cancel_decision(hostname, games)
        elif action == "chat":
            # handle_chat now returns the message string; send to group
            chat_text = handle_chat(hostname, msg)
            if chat_text:
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    hostname,
                    {
                        "type": "room_message",
                        "message": chat_text
                    }
                )
        elif action == "end_game":
            handle_end_game(hostname, games)
            if hostname in games: del games[hostname]
            if hostname in rooms: del rooms[hostname]

    def handle_join(self):
        # Logic from ws_connect_for_join
        player_name = self.user.username

        if not add_player(self.room_name, player_name):
            self.send(text_data=build_join_failed_msg())
            return

        async_to_sync(self.channel_layer.group_add)(
            self.room_name,
            self.channel_name
        )

        async_to_sync(self.channel_layer.group_send)(
            self.room_name,
            {
                "type": "room_message",
                "message": build_join_reply_msg(self.room_name)
            }
        )

    def room_message(self, event):
        # Helper to send messages to the group
        self.send(text_data=event["message"])


# Keep your helper functions (add_player, build_join_reply_msg, etc.)
# below the class, adapted to use channel_layer instead of channels.Group


def build_start_msg():
    ret = {"action": "start"}
    return json.dumps(ret)


def build_join_failed_msg():
    ret = {"action": "fail_join"}
    return json.dumps(ret)


def build_join_reply_msg(room_name):
    players = rooms.get(room_name, [])
    data = []
    for player in players:
        try:
            profile_user = User.objects.get(username=player)
        except Exception:
            continue
        try:
            profile = Profile.objects.get(user=profile_user)
        except Exception:
            profile = None
        avatar = profile.avatar.url if profile else ""
        data.append({"id": profile_user.id, "name": player, "avatar": avatar})

    ret = {"action": "join", "data": data}
    return json.dumps(ret)


def add_player(room_name, player_name):
    if room_name not in rooms:
        rooms[room_name] = set()
        rooms[room_name].add(room_name)

    if len(rooms[room_name]) >= 4:
        return False

    rooms[room_name].add(player_name)
    return True


def handle_start(hostname):
    # init game
    if hostname not in games:
        players = rooms.get(hostname, [])
        player_num = len(players)
        game = Game(player_num)
        games[hostname] = game

        change_handler = ChangeHandler(game, hostname)
        game.add_game_change_listner(change_handler)
        changehandlers[hostname] = change_handler

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        hostname,
        {
            "type": "room_message",
            "message": build_start_msg()
        }
    )