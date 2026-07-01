from aiogram.types import CallbackQuery
from aiogram import Bot
import logging

from database import (
    is_participant,
    RegistrationsRepository,
    TrainingsRepository,
    EventsRepository,
    UsersGroupsRepository,
    MessagesRepository
)
from utils import (
    update_private_message,
    update_group_message
)
from config.bot_config import ALLOW_REGISTRATION_IN_FULL_TRAINING
from config.db_config import TrainingStatus

async def handle_new_registration(callback_query: CallbackQuery, bot: Bot):
    user_id = callback_query.from_user.id
    user_db_id = is_participant(user_id)
    if not user_db_id:
        await callback_query.answer("У вас нет доступа")
        logging.info(f"Пользователь {user_id} не участник (handle_new_registration)")
        return
    
    callback_data = callback_query.data
    training_id = int(callback_data.split('|')[1])

    training = TrainingsRepository.get_training_by_id(training_id)    
    if not training:
        await callback_query.answer(f"Тренировка {training_id} не найдена")
        logging.error(f"Тренировка {training_id} не найдена (handle_new_registration)")
        return

    if training['training_status_id'] == TrainingStatus.CANCELLED:
        await callback_query.answer(f"Тренировка уже отменена")
        logging.info(f"Тренировка {training_id} уже отменена (handle_new_registration)")
        return
    
    if training['training_status_id'] == TrainingStatus.COMPLETED:
        await callback_query.answer(f"Тренировка уже прошла")
        logging.info(f"Тренировка {training_id} уже прошла (handle_new_registration)")
        return

    already_exist = RegistrationsRepository.check_registration_exist(training_id, user_db_id)
    if already_exist:
        await callback_query.answer("Вы уже записаны")
        logging.info(f"Пользователь {user_db_id} уже записан на тренировку {training_id} (handle_new_registration)")
        return
    
    chat_id = callback_query.message.chat.id

    if not RegistrationsRepository.is_places_left(training_id, chat_id) \
        and not ALLOW_REGISTRATION_IN_FULL_TRAINING:
        await callback_query.answer("Мест нет")
        logging.info(f"Для пользователя {user_db_id} нет мест на тренировку {training_id} (handle_new_registration)")
        return

    registration_id = RegistrationsRepository.add_registration(training_id, user_db_id)
    if not registration_id:
        await callback_query.answer("Не удалось добавить запись в базу данных")
        logging.error(f"Запись {registration_id} не удалось добавить (handle_new_registration)")
        return

    EventsRepository.add_registration(registration_id)

    groups = UsersGroupsRepository.get_user_groups_id(user_db_id)
    for group in groups:
        group_id = group['group_id']
        message = MessagesRepository.get_group_message_by_group_id(training_id, group_id)
        if not message:
            continue

        message_id = message['telegram_message_id']
        chat_id = message['telegram_chat_id']
        await update_group_message(bot, training_id, chat_id=chat_id, message_id=message_id)

    await update_private_message(bot, training_id)
    logging.info(f"Запись {registration_id} добавлена (handle_new_registration)")

async def handle_cancel_registration(callback_query: CallbackQuery, bot: Bot):
    user_id = callback_query.from_user.id
    user_db_id = is_participant(user_id)
    if not user_db_id:
        await callback_query.answer("У вас нет доступа")
        logging.info(f"Пользователь {user_id} не участник (handle_cancel_registration)")
        return
    
    callback_data = callback_query.data
    training_id = int(callback_data.split('|')[1])

    training = TrainingsRepository.get_training_by_id(training_id)    
    if not training:
        await callback_query.answer(f"Тренировка {training_id} не найдена")
        logging.error(f"Тренировка {training_id} не найдена (handle_cancel_registration)")
        return

    if training['training_status_id'] == TrainingStatus.CANCELLED:
        await callback_query.answer(f"Тренировка уже отменена")
        logging.info(f"Тренировка {training_id} уже отменена (handle_cancel_registration)")
        return
    
    if training['training_status_id'] == TrainingStatus.COMPLETED:
        await callback_query.answer(f"Тренировка уже прошла")
        logging.info(f"Тренировка {training_id} уже прошла (handle_cancel_registration)")
        return
    
    registration_id = RegistrationsRepository.get_active_registration_id(training_id, user_db_id)
    if not registration_id:
        await callback_query.answer(f"Вы ещё не записались")
        logging.info(f"Пользователь {user_db_id} ещё не записан на тренировку {training_id}  (handle_cancel_registration)")
        return

    success = RegistrationsRepository.cancel_registration_by_participant(registration_id)
    if not success:
        await callback_query.answer(f"Запись не удалось отменить")
        logging.error(f"Запись {registration_id} не удалось отменить (handle_cancel_registration)")
        return
    
    EventsRepository.cancel_registration_by_participant(registration_id)

    groups = UsersGroupsRepository.get_user_groups_id(user_db_id)
    for group in groups:
        group_id = group['group_id']
        message = MessagesRepository.get_group_message_by_group_id(training_id, group_id)
        if not message:
            continue
        
        message_id = message['telegram_message_id']
        chat_id = message['telegram_chat_id']
        await update_group_message(bot, training_id, chat_id=chat_id, message_id=message_id)
        
    await update_private_message(bot, training_id)
    logging.info(f"Запись {registration_id} отменена (handle_cancel_registration)")