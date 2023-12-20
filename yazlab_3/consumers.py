# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
import logging
logger = logging.getLogger(__name__)

class WaiterConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        # Join waiter group
        await self.channel_layer.group_add(
            'waiter_group',
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave waiter group
        await self.channel_layer.group_discard(
            'waiter_group',
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        
        text_data_json = json.loads(text_data)    
        message = text_data_json['message']
        logger.debug("sadasdsadasfasfas")

        # Send message to group
        await self.channel_layer.group_send(
            'waiter_group',
            {
                'type': 'waiter_status',
                'message': message
            }
        )

    # Receive message from group
    async def waiter_status(self, event):
        logger.debug("sadasdsadasfasfas")
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
class ChefConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        # Join waiter group
        await self.channel_layer.group_add(
            'chef_group',
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave waiter group
        await self.channel_layer.group_discard(
            'chef_group',
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        
        text_data_json = json.loads(text_data)    
        message = text_data_json['message']
        logger.debug("sadasdsadasfasfas")

        # Send message to group
        await self.channel_layer.group_send(
            'chef_group',
            {
                'type': 'chef_status',
                'message': message
            }
        )

    # Receive message from group
    async def chef_status(self, event):
        logger.debug("sadasdsadasfasfas")
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
class TableConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        # Join waiter group
        await self.channel_layer.group_add(
            'table_group',
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave waiter group
        await self.channel_layer.group_discard(
            'table_group',
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        
        text_data_json = json.loads(text_data)    
        message = text_data_json['message']
        logger.debug("sadasdsadasfasfas")

        # Send message to group
        await self.channel_layer.group_send(
            'table_group',
            {
                'type': 'table_status',
                'message': message
            }
        )

    # Receive message from group
    async def table_status(self, event):
        logger.debug("sadasdsadasfasfas")
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
