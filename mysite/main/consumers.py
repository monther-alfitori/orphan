# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class SponsorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("sponsors", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("sponsors", self.channel_name)

    async def receive(self, text_data):
        pass  # Placeholder for handling incoming WebSocket messages if needed

    async def send_new_sponsor(self, event):
        sponsor = event['sponsor']
        await self.send(text_data=json.dumps({
            'name': sponsor['name'],
            'residence_location': sponsor['residence_location'],
            'primary_phone': sponsor['primary_phone'],
            'sponsorship_amount': sponsor['sponsorship_amount'],
        }))
