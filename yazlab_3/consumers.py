
import json
from channels.generic.websocket import AsyncWebsocketConsumer
import logging
logger = logging.getLogger(__name__)

class WaiterConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        await self.channel_layer.group_add(
            'waiter_group',
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            'waiter_group',
            self.channel_name
        )

    
    async def receive(self, text_data):
        
        text_data_json = json.loads(text_data)    
        message = text_data_json['message']

        await self.channel_layer.group_send(
            'waiter_group',
            {
                'type': 'waiter_status',
                'message': message
            }
        )


    async def waiter_status(self, event):
        message = event['message']


        await self.send(text_data=json.dumps({
            'message': message
        }))
class ChefConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):

        await self.channel_layer.group_add(
            'chef_group',
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            'chef_group',
            self.channel_name
        )

    async def receive(self, text_data):
        
        text_data_json = json.loads(text_data)    
        message = text_data_json['message']

        await self.channel_layer.group_send(
            'chef_group',
            {
                'type': 'chef_status',
                'message': message
            }
        )

    async def chef_status(self, event):
        message = event['message']


        await self.send(text_data=json.dumps({
            'message': message
        }))
class TableConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):

        await self.channel_layer.group_add(
            'table_group',
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            'table_group',
            self.channel_name
        )

    async def receive(self, text_data):
        
        text_data_json = json.loads(text_data)    
        message = text_data_json['message']

        await self.channel_layer.group_send(
            'table_group',
            {
                'type': 'table_status',
                'message': message
            }
        )

    async def table_status(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))
    async def update_queue_status(self, event):

        await self.send(text_data=json.dumps({
            'type': 'update_queue',
            'status':event['message']['status'],
            'action': event['message']['action'],
            'customer_id': event['message']['customer_id']
        }))
class CashConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):

        await self.channel_layer.group_add(
            'cashRegister_group',
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            'cashRegister_group',
            self.channel_name
        )

    async def receive(self, text_data):
        
        text_data_json = json.loads(text_data)    
        message = text_data_json['message']
        logger.debug("sadasdsadasfasfas")


        await self.channel_layer.group_send(
            'cashRegister_group',
            {
                'type': 'cashRegister_status',
                'message': message
            }
        )

    async def cashRegister_status(self, event):
        logger.debug("sadasdsadasfasfas")
        message = event['message']


        await self.send(text_data=json.dumps({
            'message': message
        }))
