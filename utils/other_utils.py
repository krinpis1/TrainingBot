from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
import logging

from database import SlotsGroupsRepository, UsersGroupsRepository, GroupsRepository, UsersRepository

def get_group_intersection(slot_id: int, user_db_id: int):
    slot_groups = SlotsGroupsRepository.get_slot_groups_id(slot_id) or []
    slot_groups_id = []
    for slot_group in slot_groups:
        slot_groups_id.append(slot_group['group_id'])

    user_groups = UsersGroupsRepository.get_user_groups_id(user_db_id) or []
    user_groups_id = []
    for user_group in user_groups:
        user_groups_id.append(user_group['group_id'])

    groups_intersection = set(user_groups_id).intersection(slot_groups_id)

    return groups_intersection

async def is_user_in_chat(bot: Bot, chat_id: int, user_id: int):
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        if member.status in ['left', 'kicked']:
            return False
        return True
        
    except TelegramBadRequest as e:
        if "user not found" in str(e).lower() or "chat not found" in str(e).lower():
            return False
        
async def update_user_groups(bot: Bot, user_id: int):
    groups = GroupsRepository.get_all_groups()
    if not groups:
        logging.info(f"В БД нет групп (update_user_groups, пользователь {user_id})")
        return
    
    user_db_id = UsersRepository.get_user_db_id(user_id)

    user_groups = UsersGroupsRepository.get_user_groups_id(user_db_id)
    user_groups_id = [group['group_id'] for group in user_groups]
    
    for group in groups:
        chat_id = group['telegram_chat_id']
        group_id = group['id']
        if (group_id not in user_groups_id) and (await is_user_in_chat(bot, chat_id, user_id)):
            UsersGroupsRepository.add(user_db_id, group_id)
            logging.info(f"Добавлена новая группа {group_id} у пользователя {user_db_id} (update_user_groups)")