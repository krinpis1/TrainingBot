from aiogram.types import CallbackQuery, LinkPreviewOptions
from aiogram import Bot
from datetime import datetime
import logging

from keyboards.schedule_training_keyboards import (
    confirmation_keyboard,
)
from database import (
    is_admin,
    TrainingsRepository, 
    SlotsRepository,
    EventsRepository,
    MessagesRepository,
    SlotsGroupsRepository,
    TrainingsGroupsRepository
)
from utils import (
    send_slot_selection,
    send_registration_message,
    update_private_message,
    get_slot_info,
    get_group_intersection,
    update_slot_selection_message
)

# Обработчик выбора тренировки
async def handle_slot_selection(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    user_db_id = is_admin(user_id)
    if not user_db_id:
        await callback_query.answer("У вас нет доступа")
        logging.info(f"Пользователь {user_id} не админ (handle_slot_selection)")
        return

    callback_data = callback_query.data
    parts = callback_data.split("|")
    
    slot_id = int(parts[1])
    training_datetime_str = parts[2]
    training_datetime = datetime.strptime(training_datetime_str, "%Y-%m-%d %H:%M:%S")

    slot = SlotsRepository.get_slot_by_id(slot_id)
    if not slot:
        await callback_query.answer(f"Слот {slot_id} не найден")
        logging.error(f"Слот {slot_id} не найден (handle_slot_selection)")
        return
    
    location_id = slot['location_id']
    already_exist = TrainingsRepository.check_training_exists(training_datetime, location_id, slot_id)
    if already_exist:
        await callback_query.answer(f"Эта тренировка уже назначена")
        logging.info(f"Тренировка по слоту {slot_id} уже назначена (handle_slot_selection)")
        return
    
    groups_intersection = get_group_intersection(slot_id, user_db_id)
    if not groups_intersection:
        await callback_query.answer(f"Недоступно")
        logging.info(f"Слот {slot_id} и пользователь {user_db_id} не имеют общих групп (handle_slot_selection)")
        return

    slot_info = get_slot_info(slot_id, training_datetime_str, user_db_id)

    await callback_query.message.edit_text(
        f"{slot_info}",
        reply_markup=confirmation_keyboard(slot_id, training_datetime_str),
        parse_mode="HTML",
        link_preview_options=LinkPreviewOptions(is_disabled=True)
    )
    logging.info(f"Пользователь {user_db_id} выбрал слот {slot_id} (handle_slot_selection)")


async def handle_return_slot_selection(callback_query: CallbackQuery, bot: Bot):
    user_id = callback_query.from_user.id
    user_db_id = is_admin(user_id)
    if not user_db_id:
        await callback_query.answer("У вас нет доступа")
        logging.info(f"Пользователь {user_id} не админ (handle_return_slot_selection)")
        return
    
    await update_slot_selection_message(bot, message=callback_query.message)
    logging.info(f"Пользователь {user_db_id} вернулся к выбору слота (handle_return_slot_selection)")

# Обработчик подтверждения назначения тренировки
async def handle_training_confirmation(callback_query: CallbackQuery, bot: Bot):
    user_id = callback_query.from_user.id
    user_db_id = is_admin(user_id)
    if not user_db_id:
        await callback_query.answer("У вас нет доступа")
        logging.info(f"Пользователь {user_id} не админ (handle_training_confirmation)")
        return
    
    callback_data = callback_query.data
    parts = callback_data.split("|")

    slot_id = int(parts[1])
    training_datetime_str = parts[2]
    training_datetime = datetime.strptime(training_datetime_str, "%Y-%m-%d %H:%M:%S")
    
    slot = SlotsRepository.get_slot_by_id(slot_id)
    if not slot:
        await callback_query.answer(f"Слот {slot_id} не найден")
        logging.info(f"Слот {slot_id} не найден (handle_training_confirmation)")
        return
    
    location_id = slot['location_id']
    
    already_exist = TrainingsRepository.check_training_exists(training_datetime, location_id, slot_id)
    if already_exist:
        await callback_query.answer(f"Эта тренировка уже назначена")
        logging.info(f"Тренировка по слоту {slot_id} уже назначена (handle_training_confirmation)")
        return

    training_id = TrainingsRepository.add_training_with_slot(
        date_time=training_datetime,
        location_id=location_id,
        slot_id=slot_id
    )
    if not training_id:
        await callback_query.answer(f"Не удалось добавить тренировку в базу данных")
        logging.error(f"Не удалось добавить тренировку по слоту {slot_id} (handle_training_confirmation)")
        return

    EventsRepository.add_training(training_id, user_db_id)
    
    groups_id = get_group_intersection(slot_id, user_db_id)
    if not groups_id:
        await callback_query.answer(f"Недоступно")
        logging.info(f"Слот {slot_id} и пользователь {user_db_id} не имеют общих групп (handle_training_confirmation)")
        return

    groups = [SlotsGroupsRepository.get_info(slot_id, group_id) for group_id in groups_id]

    telegram_chats_id = [group['telegram_chat_id'] for group in groups]

    for group in groups:
        TrainingsGroupsRepository.add(training_id, group['group_id'], group['max_places'])

    MessagesRepository.add_message(training_id, callback_query.message)

    for telegram_chat_id in telegram_chats_id:
        registration_message = await send_registration_message(bot, telegram_chat_id, training_id)
        MessagesRepository.add_message(training_id, registration_message)

    await update_private_message(bot, training_id, callback_query.message)

    logging.info(f"Тренировка {training_id} назначена пользователем {user_db_id} (handle_training_confirmation)")
    
    return await send_slot_selection(bot, user_id, user_db_id)