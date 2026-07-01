from aiogram.types import LinkPreviewOptions
from aiogram import Bot
from datetime import datetime
import logging

from database import (
    TrainingsRepository,
    DaysRepository,
    UsersRepository
)
from keyboards import (
    after_appointment_keyboard, 
    slot_selection_keyboard,
    registration_keyboard,
    day_selection_keyboard
)
from utils import (
    get_public_training_info,
    get_private_training_info,
    get_private_registrations_info,
    get_mention_participants_info,
    get_registration_message_info
)
from config.bot_config import TAG_PARTICIPANTS_ABOUT_TRAINING

async def send_day_selection(bot: Bot, user_id: int):
    message = await bot.send_message(
        chat_id=user_id,
        text="<b>Выберите день</b>",
        reply_markup=day_selection_keyboard(),
        parse_mode="HTML",
    )
    logging.info(f"Пользователю {user_id} отправлен выбор дня (send_day_selection)")
    return message

async def send_slot_selection(bot: Bot, user_id: int, user_db_id: int):
    message = await bot.send_message(
        chat_id=user_id,
        text="<b>Назначить новую тренировку</b>",
        reply_markup=slot_selection_keyboard(user_db_id),
        parse_mode="HTML"
    )
    logging.info(f"Пользователю {user_db_id} отправлен выбор слота (send_slot_selection)")
    return message

async def send_registration_message(bot: Bot, chat_id: int, training_id: int):
    training_info = get_public_training_info(training_id, chat_id)
    mention_participants = get_mention_participants_info(chat_id) if TAG_PARTICIPANTS_ABOUT_TRAINING else ""

    text = (f"{training_info}\n"
            f"{mention_participants}"
            f"Пока никто не записан!")
    
    message = await bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=registration_keyboard(training_id),
        parse_mode="HTML",
        link_preview_options=LinkPreviewOptions(is_disabled=True)
    )
    logging.info(f"В чат {chat_id} отправлено сообщение для регистрации на тренировку {training_id} (send_registration_message)")
    return message
    
   
async def send_training_cancel_message(bot: Bot, chat_id: int, participants_info: str, training_id: int):
    training = TrainingsRepository.get_training_by_id(training_id)
    if not training:
        logging.error(f"Тренировка {training_id} не найдена в send_training_cancel_message")
    
    training_datetime: datetime = training['date_time']
    
    day_name = DaysRepository.get_day_name(training_datetime.weekday() + 1)
    formatted_date = training_datetime.strftime("%d.%m")
    formatted_time = training_datetime.strftime("%H:%M")

    await bot.send_message(
        text=
        (f"❌ {day_name} {formatted_time} ({formatted_date})\n\n"
        f"{participants_info}, <b>эта тренировка отменена!</b>"),
        chat_id=chat_id,
        parse_mode="HTML"
    )
    logging.info(f"В чат {chat_id} отправлено сообщение об отмене тренировки {training_id} (send_training_cancel_message)")

async def send_private_message(bot: Bot, training_id: int, chat_id: int):
    training = TrainingsRepository.get_training_by_id(training_id)
    if not training:
        logging.error(f"Тренировка {training_id} не найдена (send_private_message)")
        return
        
    status_info = get_registration_message_info(training_id)
    registrations_info = get_private_registrations_info(training_id)
    keyboard = after_appointment_keyboard(training_id)

    user_db_id = UsersRepository.get_user_db_id(chat_id)
    
    training_info = get_private_training_info(training_id, user_db_id)

    text = (f"{training_info}\n"
            f"{status_info}\n\n"
            f"{registrations_info}")

    message = await bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=keyboard,
        parse_mode="HTML",
        link_preview_options=LinkPreviewOptions(is_disabled=True)
    )
    logging.info(f"В чат {chat_id} отправлено сообщение о тренировке {training_id} (send_private_message)")
    return message