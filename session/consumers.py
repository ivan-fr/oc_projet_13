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
            try:
                if not self.scope['session'].get('listen_thread_group_name', set()):
                    self.scope['session']['listen_thread_group_name'] = set()
                for thread_id in self.scope['session'].get('im', {}).keys():
                    name_group = f"whoisonline_thread_{thread_id}"
                    self.scope['session']['listen_thread_group_name'].add(name_group)
                    await self.channel_layer.group_add(name_group, self.channel_name)
            except AttributeError:
                raise InvalidChannelLayerError(
                    "BACKEND is unconfigured or doesn't support groups"
                )
            await self.accept()

            for thread_id, recipient_user_id in \
                    self.scope['session'].get('im', {}).items():
                await self.online_manifest_presence_thread({
                    "thread_id": thread_id,
                    "recipient_user_id": recipient_user_id
                })

    async def online_synchronise_thread(self, event):
        if not self.scope['session'].get('im', {}):
            self.scope['session']['im'] = {}
        name_group = f"whoisonline_thread_{event['thread_id']}"

        if self.scope['user'].is_authenticated and self.scope['user'].pk == event["from_user_id"]:
            if not self.scope['session'].get('listen_thread_group_name', set()):
                self.scope['session']['listen_thread_group_name'] = set()
            await self.channel_layer.group_add(name_group, self.channel_name)
            self.scope['session']['listen_thread_group_name'].add(name_group)

        elif self.scope['user'].is_authenticated and self.scope['user'].pk == event["recipient_user_id"]:
            if event['thread_id'] not in self.scope['session']['im'].keys():
                self.scope['session']['im'][event['thread_id']] = event["recipient_user_id"]
                await self.save_session()

            if not self.scope['session'].get('listen_thread_group_name', set()):
                self.scope['session']['listen_thread_group_name'] = set()
            await self.channel_layer.group_add(name_group, self.channel_name)
            self.scope['session']['listen_thread_group_name'].add(name_group)

    async def online_manifest_presence_thread(self, event):
        if self.scope['user'].is_authenticated and self.scope['user'].pk == event["recipient_user_id"]:
            await self.channel_layer.group_send(
                f"whoisonline_thread_{event['thread_id']}",
                {
                    "group": f"whoisonline_thread_{event['thread_id']}",
                    "type": "online.join",
                    "user_id": self.scope["user"].pk,
                }
            )

    async def online_clean_im(self, event):
        if self.scope['user'].is_authenticated and self.scope['user'].pk == event["recipient_user_id"]:
            if self.scope['session'].get('im', {}):
                try:
                    del self.scope['session']['im'][event["thread_id"]]
                except KeyError:
                    del self.scope['session']['im'][str(event["thread_id"])]
                # await self.channel_layer.group_discard(event['group_name'], self.channel_name)
                # self.scope['session']['listen_thread_group_name'].remove(event['group_name'])
            await self.save_session()

    async def online_join(self, event):
        """
        Called when someone has joined our chat.
        """
        # Send a message down to the client
        if self.scope['user'].pk != event['user_id']:
            await self.send_json(
                {
                    "groups": event['group'],
                    "user_id": event['user_id'],
                    "connected": True,
                },
            )

    async def online_leave(self, event):
        if self.scope['user'].pk != event['user_id']:
            await self.send_json(
                {
                    "user_id": event["user_id"],
                    "connected": False,
                    "groups": event['group']
                }
            )

    async def disconnect(self, code):
        if self.scope['session']['listen_thread_group_name']:
            try:
                for i, group in enumerate(self.scope['session']['listen_thread_group_name']):
                    await self.channel_layer.group_discard(group, self.channel_name)
                    await self.channel_layer.group_send(
                        group,
                        {
                            "group": group,
                            "type": "online.leave",
                            "user_id": self.scope['user'].pk,
                        }
                    )
                del self.scope['session']['listen_thread_group_name']
                await self.save_session()
            except AttributeError:
                raise InvalidChannelLayerError(
                    "BACKEND is unconfigured or doesn't support groups"
                )

    @database_sync_to_async
    def save_session(self):
        before = self.scope['session'].get('listen_thread_group_name', set())
        try:
            del self.scope['session']['listen_thread_group_name']
        except KeyError:
            pass
        self.scope['session'].save()
        self.scope['session']['listen_thread_group_name'] = before


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
        if self.thread.first == self.scope['user']:
            recipient_user_id = self.thread.second.pk
        else:
            recipient_user_id = self.thread.first.pk

        await self.channel_layer.group_send(
            "whoisonlinethread",
            {
                "type": "online.synchronise.thread",
                "from_user_id": self.scope['user'].pk,
                "recipient_user_id": recipient_user_id,
                "thread_id": self.thread.pk
            }
        )
        await asyncio.sleep(1)
        await self.channel_layer.group_send(
            "whoisonlinethread",
            {
                "type": "online.manifest.presence.thread",
                "recipient_user_id": recipient_user_id,
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

    async def disconnect(self, code):
        if self.thread.first == self.scope['user']:
            recipient_user_id = self.thread.second.pk
        else:
            recipient_user_id = self.thread.first.pk

        g = f"whoisonline_thread_{self.thread.pk}"

        await self.channel_layer.group_send(
            g,
            {
                "type": "online.clean.im",
                "from_user_id": self.scope['user'].pk,
                "recipient_user_id": recipient_user_id,
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
