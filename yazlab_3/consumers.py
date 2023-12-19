# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class WaiterConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send the message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

    # This helper function can be called to send the waiter's status to the WebSocket
    async def waiter_status(self, message):
        await self.send(text_data=json.dumps({
            'message': message
        }))
