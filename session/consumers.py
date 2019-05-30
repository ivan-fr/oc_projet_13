from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.exceptions import (
    AcceptConnection,
    DenyConnection,
    InvalidChannelLayerError,
)
import traceback
from channels.db import database_sync_to_async
from session.models import Thread, ChatMessage
from asgiref.sync import sync_to_async
from session.forms import ComposeForm


class WhoIsOnlineConsumer(AsyncJsonWebsocketConsumer):
    groups = ["whoisonline"]
    user_special_pass = False

    async def connect(self):
        await self.accept()

        if not bool(int(self.scope["url_route"]["kwargs"]["thread"])):
            await self.channel_layer.group_send(
                self.groups[0],
                {
                    "type": "online.check.presence",
                }
            )

    async def receive_json(self, content, **kwargs):
        if not self.scope['user'].is_anonymous and self.scope['user'].is_superuser \
                or self.user_special_pass and not self.scope['user'].is_anonymous:
            await self.channel_layer.group_send(
                self.groups[0],
                {
                    "type": "online.join",
                    "user_id": self.scope["user"].pk,
                    "all_user": content.get('all_user')
                }
            )
        elif content.get('all_user') and not self.scope['user'].is_anonymous and \
                self.scope['user'].pk in content.get('user_ids'):
            self.user_special_pass = True
            await self.channel_layer.group_send(
                self.groups[0],
                {
                    "type": "online.join",
                    "user_id": self.scope["user"].pk,
                    "all_user": content.get('all_user')
                }
            )

    async def online_check_presence(self, event):
        _dict = {
            'check': True,
            'all_user': False
        }

        if event.get('all_user'):
            _dict['all_user'] = True

        await self.send_json(_dict)

    async def online_join(self, event):
        """
        Called when someone has joined our chat.
        """
        # Send a message down to the client
        await self.send_json(
            {
                "user_id": event['user_id'],
                "connected": True
            },
        )

    async def online_leave(self, event):
        await self.send_json(
            {
                "user_id": event["user_id"],
                "connected": False
            }
        )

    async def disconnect(self, code):
        if not self.scope['user'].is_anonymous and self.scope['user'].is_superuser \
                or self.user_special_pass and not self.scope['user'].is_anonymous:
            await self.channel_layer.group_send(
                self.groups[0],
                {
                    "type": "online.leave",
                    "user_id": self.scope['user'].pk,
                }
            )


class ThreadConsumer(AsyncJsonWebsocketConsumer):

    async def websocket_connect(self, message):
        if self.scope["user"].is_anonymous:
            # Reject the connection
            await self.close()
        else:
            # Accept the connection
            self.thread = await self.get_thread()
            if self.thread is None:
                await self.close()
            self.groups = [f'thread_{self.thread.pk}']
            """
            Called when a WebSocket connection is opened.
            """
            try:
                for group in self.groups:
                    await self.channel_layer.group_add(group, self.channel_name)
            except AttributeError:
                raise InvalidChannelLayerError(
                    "BACKEND is unconfigured or doesn't support groups"
                )

            try:
                await self.connect()
            except AcceptConnection:
                await self.accept()
            except DenyConnection:
                await self.close()

    async def connect(self):
        await self.accept()
        await self.channel_layer.group_send(
            "whoisonline",
            {
                "type": "online.check.presence",
                "all_user": True
            }
        )

    async def receive_json(self, content, **kwargs):
        if self.scope['user'].is_authenticated:
            msg, errors = None, None
            validate_form = await sync_to_async(self.validate_form)({'data': content})
            if validate_form[1]:
                msg = await self.create_thread_message(validate_form[0].cleaned_data.get("message"))
                msg = msg.message

                await self.channel_layer.group_send(
                    self.groups[0],
                    {
                        "type": "thread.send.message",
                        "username": self.scope["user"].username,
                        "message": msg,
                        "errors_form": errors
                    }
                )
            else:
                errors = validate_form[0]
                event = {
                    "username": self.scope["user"].username,
                    "message": msg,
                    "errors_form": errors
                }
                await self.thread_send_message(event)

    async def thread_send_message(self, event):
        await self.send_json({
            "username": event['username'],
            "message": event['message'],
            "errors_form": event['errors_form']
        })

    @database_sync_to_async
    def get_thread(self):
        return Thread.objects.get_or_new(self.scope['user'], self.scope["url_route"]["kwargs"]["username"])[0]

    @database_sync_to_async
    def create_thread_message(self, message):
        return ChatMessage.objects.create(thread=self.thread, user=self.scope['user'], message=message)

    @staticmethod
    def validate_form(data_post):
        form = ComposeForm(**data_post)
        if form.is_valid():
            return form, True
        else:
            return list(form.errors.items()), False
