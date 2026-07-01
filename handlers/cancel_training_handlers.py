from aiogram.types import CallbackQuery, LinkPreviewOptions
from aiogram import Bot
from aiogram.utils.markdown import hlink
from aiogram.exceptions import TelegramBadRequest
import logging

from config.db_config import TrainingStatus
from keyboards.schedule_training_keyboards import cancel_confirmation_keyboard
from database import (
    is_admin,
    TrainingsRepository,
    EventsRepository,
    MessagesRepository,
    RegistrationsRepository
)
from utils import (
    send_training_cancel_message,
    get_private_training_info,
    update_private_message
)

async def handle_cancel_training_confirm(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    user_db_id = is_admin(user_id)
    if not user_db_id:
        await callback_query.answer("У вас нет доступа")
        logging.info(f"Пользователь {user_id} не админ (handle_cancel_training_confirm)")
        return
    
    training_id = callback_query.data.split("|")[1]
    
    training = TrainingsRepository.get_training_by_id(training_id)
    if not training:
        await callback_query.answer(f"Тренировка {training_id} не найдена")
        logging.error(f"Тренировка {training_id} не найдена (handle_cancel_training_confirm)")
        return
    
    if training['training_status_id'] == TrainingStatus.CANCELLED:
        await callback_query.answer(f"Тренировка уже отменена")
        logging.info(f"Тренировка {training_id} уже отменена (handle_cancel_training_confirm)")
        return
    
    if training['training_status_id'] == TrainingStatus.COMPLETED:
        await callback_query.answer(f"Тренировка уже прошла")
        logging.info(f"Тренировка {training_id} уже прошла (handle_cancel_training_confirm)")
        return
    
    training_info = get_private_training_info(training_id, user_db_id)
    
    try:
        await callback_query.message.edit_text(
            (f"{training_info}\n"
            f"Отменить тренировку?"),
            reply_markup=cancel_confirmation_keyboard(training_id),
            parse_mode="HTML",
            link_preview_options=LinkPreviewOptions(is_disabled=True)
        )
        logging.info(f"Пользователь {user_db_id} хочет отменить тренировку {training_id} (handle_cancel_training_confirm)")
    
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            logging.error("Сообщение не было изменено (handle_cancel_training_confirme)")
        else:
            raise e
    

async def handle_cancel_training_final(callback_query: CallbackQuery, bot: Bot):
    user_id = callback_query.from_user.id
    user_db_id = is_admin(user_id)
    if not user_db_id:
        await callback_query.answer("У вас нет доступа")
        logging.info(f"Пользователь {user_id} не админ (handle_cancel_training_final)")
        return
    
    training_id = callback_query.data.split("|")[1]

    training = TrainingsRepository.get_training_by_id(training_id)    
    if not training:
        await callback_query.answer(f"Тренировка {training_id} не найдена")
        logging.info(f"Тренировка {training_id} не найдена (handle_cancel_training_final)")
        return
    
    if training['training_status_id'] == TrainingStatus.CANCELLED:
        await callback_query.answer(f"Тренировка уже отменена")
        logging.info(f"Тренировка {training_id} уже отменена (handle_cancel_training_final)")
        return
    
    if training['training_status_id'] == TrainingStatus.COMPLETED:
        await callback_query.answer(f"Тренировка уже прошла")
        logging.info(f"Тренировка {training_id} уже прошла (handle_cancel_training_final)")
        return

    success = TrainingsRepository.cancel_training(training_id)
    if not success:
        await callback_query.answer(f"Тренировку {training_id} не удалось отменить")
        logging.error(f"Тренировку {training_id} не удалось отменить (handle_cancel_training_final)")
        return
    
    EventsRepository.cancel_training(training_id, user_db_id)

    messages = MessagesRepository.get_group_messages(training_id)
    for message in messages:
        chat_id = message['telegram_chat_id']
        message_id = message['telegram_message_id']
        await bot.delete_message(chat_id, message_id)

        registrations = RegistrationsRepository.get_active_registrations_by_chat_id(training_id, chat_id)
        if not registrations:
            continue

        participants_info = ""

        for registration in registrations:
            registration_id = registration['id']
            telegram_id = registration['telegram_id']
            name = registration['name']
            link = f"tg://user?id={telegram_id}"
            participants_info += f"{hlink(name, link)}, "

            if not (RegistrationsRepository.cancel_registration_by_training(registration_id)
                    and EventsRepository.cancel_registration_by_training(registration_id)):
                
                await callback_query.answer(f"Запись не удалось отменить")
                logging.error(f"Запись {registration_id} не удалось отменить (handle_cancel_training_final)")
                return

        participants_info = participants_info[:-2]
        await send_training_cancel_message(bot, chat_id, participants_info, training_id)
        
    
    await update_private_message(bot, training_id, callback_query.message)

    logging.info(f"Тренировка {training_id} отменена пользователем {user_db_id} (handle_cancel_training_final)")
    

async def handle_keep_training(callback_query: CallbackQuery, bot: Bot):
    user_id = callback_query.from_user.id
    user_db_id = is_admin(user_id)
    if not user_db_id:
        await callback_query.answer("У вас нет доступа")
        logging.info(f"Пользователь {user_id} не админ (handle_keep_training)")
        return
    
    training_id = callback_query.data.split("|")[1]

    training = TrainingsRepository.get_training_by_id(training_id)    
    if not training:
        await callback_query.answer(f"Тренировка {training_id} не найдена")
        logging.error(f"Тренировка {training_id} не найдена (handle_keep_training)")
        return
    
    logging.info(f"Пользователь {user_db_id} оставил тренировку {training_id} (handle_keep_training)")
    
    await update_private_message(bot, training_id, callback_query.message)