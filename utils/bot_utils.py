from database import (
    GroupsRepository,
    EventsRepository
)
from aiogram.types import ChatMemberUpdated
from aiogram.enums import ChatType, ChatMemberStatus
import logging

async def bot_added(event: ChatMemberUpdated):
    if event.new_chat_member.user.id != event.bot.id:
        return
    
    old_status = event.old_chat_member.status
    new_status = event.new_chat_member.status
    
    # Добавляем дополнительную проверку на реальное изменение статуса
    if old_status == new_status:
        return
    
    if (old_status in [ChatMemberStatus.LEFT, ChatMemberStatus.KICKED, ChatMemberStatus.RESTRICTED] and \
        new_status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]):

        chat = event.chat
        if chat.type in [ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL]:
            chat_id = chat.id
            group_id = GroupsRepository.add_group(chat_id)
            EventsRepository.add_group(group_id)
            logging.info(f"Группа {group_id} добавлена (bot_added)")