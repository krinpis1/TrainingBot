from aiogram import Bot
from datetime import datetime, timedelta
import logging
from asyncio import sleep

from database import (
    RegistrationsRepository, 
    TrainingsRepository, 
    EventsRepository,
    MessagesRepository,
    TrainingsGroupsRepository,
    GroupsRepository
)
from utils import (
    update_group_message, 
    update_private_message
)
from config.bot_config import TIMEZONE, TRAINING_DURATION, TRAINING_COMPLETE_UPDATE_TIME
from .update_statistics import update_statistics_sheet, update_statistics_table

async def complete_trainings(bot: Bot):
    now = datetime.now(TIMEZONE)
    target_time = datetime.combine(now.date(), datetime.min.time()) + timedelta(seconds=TRAINING_COMPLETE_UPDATE_TIME)
    target_time = TIMEZONE.localize(target_time)

    if now.weekday() == 0 and now < target_time:
        update_statistics_table()
        logging.info("Статистика в БД обновлена")
        await sleep(10)
        
        groups = GroupsRepository.get_all_groups()
        for group in groups:
            await update_statistics_sheet(group['id'])
        
        return

    active_trainings = TrainingsRepository.get_active_trainings()
    if not active_trainings:
        return

    updated_groups_id = []
    
    for training in active_trainings:
        training_id = training['id']
        training_datetime: datetime = training['date_time']
        training_datetime = TIMEZONE.localize(training_datetime)

        if training_datetime + TRAINING_DURATION > now:
            continue
        
        TrainingsRepository.complete_training(training_id)
        EventsRepository.complete_training(training_id)

        logging.info(f"Тренировка {training_id} завершена (update_passed_trainings)")

        registrations = RegistrationsRepository.get_active_registrations(training_id)
        if not registrations:
            continue

        for registration in registrations:
            registration_id = registration['id']
            RegistrationsRepository.complete_registration(registration_id)
            EventsRepository.complete_registration(registration_id)

        groups = TrainingsGroupsRepository.get_training_groups_id(training_id)
        if groups:
            for group in groups:
                updated_groups_id.append(group['group_id'])
            
        await update_private_message(bot, training_id)

        messages = MessagesRepository.get_group_messages(training_id)
        if not messages:
            continue
        
        for message in messages:
            chat_id = message['telegram_chat_id']
            message_id = message['telegram_message_id']
            await update_group_message(bot, training_id, chat_id=chat_id, message_id=message_id)

    if not updated_groups_id:
        return
    
    updated_groups_id = set(updated_groups_id)
    
    update_statistics_table()
    logging.info("Статистика в БД обновлена")
    await sleep(10)
    
    for group_id in updated_groups_id:
        await update_statistics_sheet(group_id)