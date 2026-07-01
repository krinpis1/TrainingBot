from datetime import datetime
import logging
from aiogram.utils.markdown import hlink

from database import (
    LocationsRepository, 
    DaysRepository,
    SlotsGroupsRepository,
    TrainingsGroupsRepository,
    RegistrationsRepository,
    UsersGroupsRepository,
    TrainingsRepository,
    SlotsRepository,
    GroupsRepository,
    MessagesRepository
)
from .other_utils import get_group_intersection
from config.bot_config import SHOW_LOCATION_MAPS_LINK

def get_slot_info(slot_id: int, training_datetime_str: str, user_db_id: int):
    slot = SlotsRepository.get_slot_by_id(slot_id)
    if not slot:
        logging.error(f"Слот {slot_id} не найден (get_slot_info)")
        return

    training_datetime = datetime.strptime(training_datetime_str, "%Y-%m-%d %H:%M:%S")
    formatted_date = training_datetime.strftime("%d.%m")
    formatted_time = training_datetime.strftime("%H:%M")
    
    location_info = get_location_info(slot['location_id'])
    day_name = DaysRepository.get_day_name(training_datetime.weekday() + 1)

    group_id = UsersGroupsRepository.is_user_in_one_group(user_db_id)

    if group_id:
        add_info = get_places_info(slot_id = slot['id'], group_id=group_id)
    else:
        add_info = get_groups_info(user_db_id, slot_id = slot['id'])
    
    return (f"<b>{day_name} {formatted_time} ({formatted_date})</b>\n"
            f"{location_info}\n"
            f"{add_info}")

def get_private_training_info(training_id: int, user_db_id: int):
    training = TrainingsRepository.get_training_by_id(training_id)
    if not training:
        logging.error(f"Тренировка {training_id} не найдена (get_private_training_info)")
        return f"Ошибка: тренировка {training_id} не найдена"
    
    training_datetime: datetime = training['date_time']
    
    day_name = DaysRepository.get_day_name(training_datetime.weekday() + 1)
    formatted_date = training_datetime.strftime("%d.%m")
    formatted_time = training_datetime.strftime("%H:%M")
    
    location_info = get_location_info(training['location_id'])

    one_group_id = UsersGroupsRepository.is_user_in_one_group(user_db_id)

    if one_group_id:
        add_info = get_places_info(training_id = training['id'], group_id=one_group_id)
    else:
        add_info = get_groups_info(training_id = training['id'])
    
    return (f"<b>{day_name} {formatted_time} ({formatted_date})</b>\n"
            f"{location_info}\n"
            f"{add_info}")

def get_public_training_info(training_id: int, chat_id: int):
    training = TrainingsRepository.get_training_by_id(training_id)
    if not training:
        logging.error(f"Тренировка {training_id} не найдена (get_public_training_info)")
        return f"Ошибка: тренировка {training_id} не найдена"
    
    training_datetime: datetime = training['date_time']
    
    day_name = DaysRepository.get_day_name(training_datetime.weekday() + 1)
    formatted_date = training_datetime.strftime("%d.%m")
    formatted_time = training_datetime.strftime("%H:%M")
    
    location_info = get_location_info(training['location_id'])

    group = GroupsRepository.get_group_by_chat_id(chat_id)
    if not group:
        logging.error(f"Группа {group_id} не найдена (get_private_training_info)")
        return
    group_id = group['id']

    add_info = get_places_info(training_id = training['id'], group_id=group_id)
    
    return (f"<b>{day_name} {formatted_time} ({formatted_date})</b>\n"
            f"{location_info}\n"
            f"{add_info}")

def get_registration_message_info(training_id: int):
    registration_messages = MessagesRepository.get_group_messages(training_id=training_id)

    if not registration_messages:
        logging.info(f"Не найдено сообщений в группах для тренировки {training_id} (get_registration_message_info)")
        return f"✅ Тренировка доступна для записи!"
    
    if len(registration_messages) > 1:
        return f"✅ Тренировка доступна для записи!"
    
    registration_message = registration_messages[0]

    telegram_chat_id = registration_message['telegram_chat_id']
    telegram_message_id = registration_message['telegram_message_id']

    formatted_chat_id = str(telegram_chat_id).replace("-100", "").replace("-", "")
    link = f"https://t.me/c/{formatted_chat_id}/{telegram_message_id}"

    return f"✅ Тренировка {hlink('доступна для записи', link)}!"
     

def get_groups_info(user_db_id: int = None, training_id: int = None, slot_id: int = None):
    groups = None

    if training_id:
        groups = TrainingsGroupsRepository.get_training_groups(training_id)
    elif slot_id and user_db_id:
        groups_id = get_group_intersection(slot_id, user_db_id)
        groups = [SlotsGroupsRepository.get_info(slot_id, group_id) for group_id in groups_id]
    else: 
        logging.error(f"В функцию get_groups_info не переданы необходимые параметры")
        return ""
    
    if not groups:
        logging.info(f"Не найдено групп (get_groups_info)")
        return ""

    info = f"• Для групп: "

    for group in groups:
        group_name = group['name']
        group_info = f"{group_name}"

        if group['max_places']:
            group_info += f" (мест: {group['max_places']})"
        
        info += group_info + ", "
        
    info = info[:-2]
    return f"{info}\n"

def get_places_info(group_id: int, training_id: int = None, slot_id: int = None):
    if training_id:
        max_places = TrainingsGroupsRepository.get_max_places_by_group_id(training_id, group_id)
    elif slot_id:
        max_places = SlotsGroupsRepository.get_max_places_by_group_id(slot_id, group_id)
    else: 
        logging.error(f"В функцию get_places_info не переданы необходимые параметры")
        return ""
    
    if not max_places:
        return ""
    
    return f"• Мест: {max_places}\n"


def get_private_registrations_info(training_id: int, only_completed: bool = False):
    if only_completed:
        registrations = RegistrationsRepository.get_completed_registrations(training_id)    
    else:
        registrations = RegistrationsRepository.get_active_registrations(training_id)
    
    if not registrations:
        return f"Пока никто не записан!"

    info = f"Записались:\n"

    for i in range(len(registrations)):
        registration = registrations[i]
        name = registration['name']
        info += f"{i+1}. {name}\n"
            
    return info

def get_public_registrations_info(training_id: int, chat_id: int, only_completed: bool = False):
    if only_completed:
        registrations = RegistrationsRepository.get_completed_registrations_by_chat_id(training_id, chat_id)    
    else:
        registrations = RegistrationsRepository.get_active_registrations_by_chat_id(training_id, chat_id)
    
    if not registrations:
        return f"Пока никто не записан!"

    info = f"Записались:\n"

    for i in range(len(registrations)):
        registration = registrations[i]
        
        telegram_id = registration['telegram_id']
        name = registration['name']
        link = f"tg://user?id={telegram_id}"
        info += f"{i+1}. {hlink(name, link)}\n"
            
    return info


def get_mention_participants_info(chat_id: int):
    invisible_text = '\u200b'
    participants = UsersGroupsRepository.get_participants(chat_id)

    if not participants:
        return ""
    
    info = ""
    for participant in participants:
        user_id = participant['telegram_id']
        link = f"tg://user?id={user_id}"
        info += f"{hlink(invisible_text, link)}"

    return info
        
def get_location_info(location_id: int):
    location = LocationsRepository.get_location(location_id)
    if not location:
        logging.error(f"Не найдена локация {location_id} (get_location_info)")
        return ""
    
    location_name = location['name']
    
    if SHOW_LOCATION_MAPS_LINK:
        link = location['maps_link']
        return f"• <i>{hlink(location_name, link)}</i>"
    
    return f"• <i>{location_name}</i>"