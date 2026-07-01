from aiogram import Bot
from aiogram.types import Message, LinkPreviewOptions
from aiogram.exceptions import TelegramBadRequest
import logging

from database import (
    TrainingsRepository,
    MessagesRepository,
    UsersRepository
)
from config.db_config import TrainingStatus
from utils import (
    get_private_registrations_info, 
    get_private_training_info,
    get_public_registrations_info,
    get_public_training_info,
    get_registration_message_info
)
from keyboards import after_appointment_keyboard, registration_keyboard, slot_selection_keyboard

async def update_private_message(bot: Bot, training_id: int, message: Message = None):
    training = TrainingsRepository.get_training_by_id(training_id)
    if not training:
        logging.error(f"Тренировка {training_id} не найдена (update_private_message)")
        return
    
    if message:
        chat_id = message.chat.id
        message_id = message.message_id
    
    else:
        private_message = MessagesRepository.get_private_message(training_id)
        if not private_message:
            logging.error(f"Личное сообщение для тренировки {training_id} не найдено (update_private_message)")
            return
        
        chat_id = private_message['telegram_chat_id']
        message_id = private_message['telegram_message_id']
        
    
    training_status_id = training['training_status_id']

    if training_status_id == TrainingStatus.ACTIVE:
        status_info = get_registration_message_info(training_id)
        registrations_info = get_private_registrations_info(training_id)
        keyboard = after_appointment_keyboard(training_id)

    elif training_status_id == TrainingStatus.CANCELLED:
        status_info = "❌ Тренировка отменена"
        registrations_info = ""
        keyboard = None

    elif training_status_id == TrainingStatus.COMPLETED:
        status_info = "<b>Тренировка прошла!</b>"
        registrations_info = get_private_registrations_info(training_id, only_completed=True)
        keyboard = None

    user_db_id = UsersRepository.get_user_db_id(chat_id)
    
    training_info = get_private_training_info(training_id, user_db_id)

    text = (f"{training_info}\n"
            f"{status_info}\n\n"
            f"{registrations_info}")

    try:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            reply_markup=keyboard,
            parse_mode="HTML",
            link_preview_options=LinkPreviewOptions(is_disabled=True)
        )
        logging.info(f"Личное сообщение в чате {chat_id} о тренироке {training_id} обновлено (update_private_message)")

    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            logging.error("Сообщение не было изменено (update_private_message)")
        else:
            raise e


async def update_group_message(bot: Bot, training_id: int, chat_id: int = None, message_id: int = None, message: Message = None):
    if message:
        chat_id = message.chat.id
        message_id = message.message_id
    
    elif not (chat_id and message_id):
        logging.error(f"В функцию update_group_message не переданы необходимые параметры")
        return
    
    training = TrainingsRepository.get_training_by_id(training_id)
    if not training:
        logging.error(f"Тренировка {training_id} не найдена (update_group_message)")
        return

    training_status_id = training['training_status_id']

    training_info = get_public_training_info(training_id, chat_id)

    if training_status_id == TrainingStatus.ACTIVE:
        status_info = ""
        registrations_info = get_public_registrations_info(training_id, chat_id)
        keyboard = registration_keyboard(training_id)

    elif training_status_id == TrainingStatus.CANCELLED:
        status_info = "❌ Тренировка отменена\n\n"
        registrations_info = ""
        keyboard = None

    elif training_status_id == TrainingStatus.COMPLETED:
        status_info = "<b>Тренировка прошла!</b>\n\n"
        registrations_info = get_public_registrations_info(training_id, chat_id=chat_id, only_completed=True)
        keyboard = None

    text = (f"{training_info}\n"
            f"{status_info}"
            f"{registrations_info}\n")
    
    try:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            reply_markup=keyboard,
            parse_mode="HTML",
            link_preview_options=LinkPreviewOptions(is_disabled=True)
        )
        logging.info(f"Сообщение в группе {chat_id} о тренироке {training_id} обновлено (update_group_message)")

    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            logging.error("Сообщение не было изменено (update_group_message)")
        else:
            raise e


async def update_slot_selection_message(bot: Bot, chat_id: int = None, message_id: int = None, message: Message = None):
    if message:
        chat_id = message.chat.id
        message_id = message.message_id

    elif not (chat_id and message_id):
        logging.error(f"В функцию update_slot_selection_message не переданы необходимые параметры")
        return

    user_db_id = UsersRepository.get_user_db_id(chat_id)
    if not user_db_id:
        logging.error(f"Не найден пользователь {chat_id} в БД (update_slot_selection_message)")
        return
    
    try:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="<b>Назначить новую тренировку</b>",
            reply_markup=slot_selection_keyboard(user_db_id),
            parse_mode="HTML"
        )
        logging.info(f"У пользователя {user_db_id} обновлён выбор слота (update_slot_selection_message)")

    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            logging.error("Сообщение не было изменено (update_slot_selection_message)")
        else:
            raise e