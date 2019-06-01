from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.exceptions import (
    AcceptConnection,
    DenyConnection,
    InvalidChannelLayerError,
)
import asyncio
from channels.db import database_sync_to_async
from session.models import Thread, ChatMessage
from asgiref.sync import sync_to_async
from session.forms import ComposeForm


class WhoIsOnlineConsumer(AsyncJsonWebsocketConsumer):
    groups = ["whoisonline"]

    async def connect(self):
        await self.accept()

        if bool(int(self.scope["url_route"]["kwargs"]["askmanifest"])):
            await self.channel_layer.group_send(
                self.groups[0],
                {
                    "type": "online.manifest.presence",
                }
            )
        else:
            await self.online_manifest_presence({"from_groud_send": False})

    async def online_manifest_presence(self, event):
        if not self.scope['user'].is_anonymous \
                and self.scope['user'].is_superuser:
            await self.channel_layer.group_send(
                self.groups[0],
                {
                    "type": "online.join",
                    "user_id": self.scope["user"].pk,
                    "from_groud_send": event.get("from_groud_send", True)
                }
            )

    async def online_join(self, event):
        """
        Called when someone has joined our chat.
        """
        # Send a message down to the client
        if ((event.get("from_groud_send")) or
            (not event.get("from_groud_send") and self.scope['user'].pk != event.get("user_id"))) \
                and bool(int(self.scope["url_route"]["kwargs"]["askmanifest"])):
            await self.send_json(
                {
                    "user_id": event['user_id'],
                    "connected": True,
                },
            )

    async def online_leave(self, event):
        if bool(int(self.scope["url_route"]["kwargs"]["askmanifest"])):
            await self.send_json(
                {
                    "user_id": event["user_id"],
                    "connected": False
                }
            )

    async def disconnect(self, code):
        if not self.scope['user'].is_anonymous and self.scope['user'].is_superuser:
            await self.channel_layer.group_send(
                self.groups[0],
                {
                    "type": "online.leave",
                    "user_id": self.scope['user'].pk,
                }
            )


class WhoIsOnlineThreadConsumer(AsyncJsonWebsocketConsumer):
    groups = ["whoisonlinethread"]

    async def connect(self):
        if self.scope["user"].is_anonymous:
            # Reject the connection
            await self.close()
        else:
            await self.accept()

            # je me connect puis je demande à mes threads de se synchronysé si ils sont en thread avec moi.
            for thread in await self.get_threads_by_user():
                await self.channel_layer.group_send(
                    f'thread_{thread.pk}',
                    {
                        "type": "thread.synchronise"
                    }
                )

    async def online_synchronise_thread(self, event):
        name_group = f"whoisonline_thread_{event['thread_id']}"

        if self.scope['user'].is_authenticated and self.scope['user'].pk == event["from_user_id"]:
            if not self.scope['session'].get('listen_thread_group_name', set()):
                self.scope['session']['listen_thread_group_name'] = set()
            await self.channel_layer.group_add(name_group, self.channel_name)
            self.scope['session']['listen_thread_group_name'].add(name_group)

        elif self.scope['user'].is_authenticated and self.scope['user'].pk == event["recipient_user_id"]:
            if not self.scope['session'].get('listen_thread_group_name', set()):
                self.scope['session']['listen_thread_group_name'] = set()
            await self.channel_layer.group_add(name_group, self.channel_name)
            self.scope['session']['listen_thread_group_name'].add(name_group)

    async def online_manifest_presence_thread(self, event):
        if self.scope['user'].is_authenticated and self.scope['user'].pk == event["recipient_user_id"]:
            await self.channel_layer.group_send(
                f"whoisonline_thread_{event['thread_id']}",
                {
                    "type": "online.join",
                    "user_id": self.scope["user"].pk,
                }
            )

    async def online_clean_im(self, event):
        if self.scope['user'].is_authenticated and self.scope['user'].pk == event["recipient_user_id"]:
            await self.channel_layer.group_discard(event['group_name'], self.channel_name)
            try:
                self.scope['session']['listen_thread_group_name'].remove(event['group_name'])
            except ValueError:
                pass

    async def online_join(self, event):
        """
        Called when someone has joined our chat.
        """
        # Send a message down to the client
        if self.scope['user'].pk != event['user_id']:
            await self.send_json(
                {
                    "user_id": event['user_id'],
                    "connected": True,
                },
            )

    async def online_leave(self, event):
        if self.scope['user'].pk != event['user_id'] and bool(int(self.scope["url_route"]["kwargs"]["thread_pk"])):
            await self.send_json(
                {
                    "user_id": event["user_id"],
                    "connected": False,
                }
            )

    async def online_manifest_notification_thread(self, event):
        if self.scope['user'].is_authenticated and self.scope['user'].pk == event["recipient_user_id"] \
                and int(self.scope["url_route"]["kwargs"]["thread_pk"]) != event['thread_id']:
            await self.send_json({
                "notification": True,
                "username": event['username'],
            })

    async def disconnect(self, code):
        if self.scope['session'].get('listen_thread_group_name'):
            try:
                for i, group in enumerate(self.scope['session']['listen_thread_group_name']):
                    await self.channel_layer.group_discard(group, self.channel_name)
                    await self.channel_layer.group_send(
                        group,
                        {
                            "type": "online.leave",
                            "user_id": self.scope['user'].pk,
                        }
                    )
            except AttributeError:
                raise InvalidChannelLayerError(
                    "BACKEND is unconfigured or doesn't support groups"
                )

    @database_sync_to_async
    def get_threads_by_user(self):
        return Thread.objects.by_user(self.scope['user'])


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

    async def thread_synchronise(self, event):
        await self.channel_layer.group_send(
            "whoisonlinethread",
            {
                "type": "online.synchronise.thread",
                "from_user_id": self.scope['user'].pk,
                "recipient_user_id": await self.thread_get_recipient_user(),
                "thread_id": self.thread.pk
            }
        )

        await asyncio.sleep(1)

        await self.channel_layer.group_send(
            f"whoisonline_thread_{self.thread.pk}",
            {
                "type": "online.manifest.presence.thread",
                "recipient_user_id": await self.thread_get_recipient_user(),
                "thread_id": self.thread.pk
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
                        "user_id": self.scope["user"].pk,
                        "message": msg,
                        "errors_form": errors
                    }
                )

                await self.thread_notification()
            else:
                errors = validate_form[0]
                event = {
                    "username": self.scope["user"].username,
                    "user_id": self.scope["user"].pk,
                    "message": msg,
                    "errors_form": errors
                }
                await self.thread_send_message(event)

    async def thread_send_message(self, event):
        await self.send_json({
            "username": event['username'],
            "message": event['message'],
            "user_id": event['user_id'],
            "errors_form": event['errors_form']
        })

    async def thread_notification(self):
        await self.channel_layer.group_send(
            f"whoisonline_thread_{self.thread.pk}",
            {
                "type": "online.manifest.notification.thread",
                "recipient_user_id": await self.thread_get_recipient_user(),
                "username": self.scope['user'].username,
                "thread_id": self.thread.pk
            }
        )

    async def thread_get_recipient_user(self):
        if self.thread.first == self.scope['user']:
            return self.thread.second.pk
        else:
            return self.thread.first.pk

    async def disconnect(self, code):
        g = f"whoisonline_thread_{self.thread.pk}"

        await self.channel_layer.group_send(
            g,
            {
                "type": "online.clean.im",
                "recipient_user_id": await self.thread_get_recipient_user(),
                "thread_id": self.thread.pk,
                "group_name": g
            }
        )

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
