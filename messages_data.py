from aiogram.types import Message
from aiogram import Bot

from utils import update_slot_selection_message

messages_dict = {}

def delete_message(user_id: int):
    if user_id in messages_dict:
        del messages_dict[user_id]

async def update_old_message(user_id: int, bot: Bot):
    if user_id in messages_dict:
        old_message_data = messages_dict[user_id]
        chat_id = old_message_data['chat_id']
        message_id = old_message_data['message_id']
        await update_slot_selection_message(bot, chat_id=chat_id, message_id=message_id)
        return True
    
    return False
    

async def update_message(user_id: int, new_message: Message, bot: Bot):
    if not new_message:
        return

    new_message_data = {
        'message_id': new_message.message_id,
        'chat_id': new_message.chat.id,
    } 

    if user_id in messages_dict:
        old_message_data = messages_dict[user_id]
        if new_message_data == old_message_data:
            return
        
        messages_dict[user_id] = new_message_data
        await bot.delete_message(
            chat_id=old_message_data['chat_id'],
            message_id=old_message_data['message_id']
        )
    
    messages_dict[user_id] = new_message_data