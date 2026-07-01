from aiogram.types import CallbackQuery, Message, LinkPreviewOptions
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from datetime import datetime
import logging

from states import TrainingStates
from utils import (
    send_slot_selection,
    send_registration_message,
    update_private_message,
    get_location_info,
    send_private_message
)
from database import (
    is_admin,
    DaysRepository,
    TrainingsRepository, 
    EventsRepository,
    TrainingsGroupsRepository,
    GroupsRepository,
    MessagesRepository, 
    UsersGroupsRepository
)

from keyboards import (
    day_selection_keyboard, 
    locations_keyboard, 
    back_to_day_selection_keyboard,
    without_places_keyboard, 
    select_group_keyboard
)

async def handle_custom_training(callback_query: CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback_query.from_user.id
    user_db_id = is_admin(user_id)
    if not user_db_id:
        await callback_query.answer("У вас нет доступа")
        logging.info(f"Пользователь {user_id} не админ (handle_custom_training)")
        return
    
    await callback_query.message.edit_text(
        f"<b>Выберите день</b>",
        reply_markup=day_selection_keyboard(),
        parse_mode="HTML"
    )
    logging.info(f"Пользователь {user_db_id} выбрал кастомную тренировку (handle_custom_training)")

async def handle_day_selection(callback_query: CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback_query.from_user.id
    user_db_id = is_admin(user_id)
    if not user_db_id:
        await callback_query.answer("У вас нет доступа")
        logging.info(f"Пользователь {user_id} не админ (handle_day_selection)")
        return
    
    callback_data = callback_query.data
    training_date_str = callback_data.split('|')[1]

    training_date = datetime.strptime(training_date_str, "%Y-%m-%d")

    formatted_date = training_date.strftime("%d.%m")
    day_name = DaysRepository.get_day_name(training_date.weekday() + 1)
    
    await state.update_data(training_date=training_date, bot_message=callback_query.message)
    message = await callback_query.message.edit_text(
        text=(f"<b>{day_name} {formatted_date}</b>\n\n"
              f"<b>Напишите время тренировки</b>"),
        reply_markup=back_to_day_selection_keyboard(),
        parse_mode="HTML"
    )

    logging.info(f"Пользователь {user_db_id} выбрал день (handle_day_selection)")
    await state.set_state(TrainingStates.waiting_for_time)
    return message

async def handle_training_time(message: Message, state: FSMContext):
    state_data = await state.get_data()
    await state.clear()

    user_id = message.from_user.id
    user_db_id = is_admin(user_id)
    if not user_db_id:
        await message.answer("У вас нет доступа")
        logging.info(f"Пользователь {user_id} не админ (handle_training_time)")
        return
    
    bot_message: Message = state_data['bot_message']
    await bot_message.edit_reply_markup(reply_markup=None)
    
    time_str = message.text.strip()
    training_date: datetime = state_data.get('training_date')
    formatted_date = training_date.strftime("%d.%m")
    day_name = DaysRepository.get_day_name(training_date.weekday() + 1)
    
    try:
        if ":" in time_str:
            training_time = datetime.strptime(time_str, "%H:%M")
        elif "." in time_str:
            training_time = datetime.strptime(time_str, "%H.%M")
        else:
            training_time = datetime.strptime(time_str, "%H %M")
    except:
        
        new_message = await message.answer(
            text=(f"<b>{day_name} {formatted_date}</b>\n\n"
                f"<b>Неверный формат времени, напишите ещё раз</b> <i>(например 19:45, 19.45, 19 45)</i>"),
            reply_markup=back_to_day_selection_keyboard(),
            parse_mode="HTML"
        )
        await state.update_data(training_date=training_date, bot_message=new_message)
        await state.set_state(TrainingStates.waiting_for_time)
        logging.info(f"Пользователь {user_db_id} неверно ввёл время (handle_training_time)")
        return new_message

    training_datetime = datetime.combine(training_date.date(), training_time.time())
    formatted_time = training_datetime.strftime("%H:%M")

    await message.answer(
        text=(f"<b>{day_name} {formatted_time} ({formatted_date})</b>\n\n"
            f"<b>Выберите локацию тренировки</b>"),
        reply_markup=locations_keyboard(training_datetime),
        parse_mode="HTML"
    )
    logging.info(f"Пользователь {user_db_id} ввёл время (handle_training_time)")


async def handle_location_selection(callback_query: CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback_query.from_user.id
    user_db_id = is_admin(user_id)
    if not user_db_id:
        await callback_query.answer("У вас нет доступа")
        logging.info(f"Пользователь {user_id} не админ (handle_location_selection)")
        return

    callback_data = callback_query.data
    parts = callback_data.split('|')

    training_datetime_str = parts[1]
    location_id = parts[2]

    training_datetime = datetime.strptime(training_datetime_str, "%Y-%m-%d %H:%M:%S")
    day_name = DaysRepository.get_day_name(training_datetime.weekday() + 1)

    formatted_date = training_datetime.strftime("%d.%m")
    formatted_time = training_datetime.strftime("%H:%M")
    location_info = get_location_info(location_id)

    groups_id = UsersGroupsRepository.get_user_groups_id(user_db_id)

    if len(groups_id) == 1:
        group_id = groups_id[0]['group_id']
        await state.update_data(
            training_datetime=training_datetime,
            location_id=location_id,
            group_id=group_id,
            bot_message=callback_query.message
        )
        await callback_query.message.edit_text(
            text=(f"<b>{day_name} {formatted_time} ({formatted_date})</b>\n"
            f"{location_info}\n\n"
            f"<b>Назначьте тренировку или напишите количество доступных мест</b>"),
            reply_markup=without_places_keyboard(training_datetime, location_id, group_id, group_selection=False),
            parse_mode="HTML",
            link_preview_options=LinkPreviewOptions(is_disabled=True)
        )
        await state.set_state(TrainingStates.waiting_for_places)
        logging.info(f"Пользователь {user_db_id} с одной группой выбрал локацию {location_id} (handle_location_selection)")
        return

    if len(groups_id) > 1:
        await callback_query.message.edit_text(
            text=(f"<b>{day_name} {formatted_time} ({formatted_date})</b>\n"
            f"{location_info}\n\n"
            f"<b>Выберите группу</b>"),
            reply_markup=select_group_keyboard(groups_id, training_datetime, location_id),
            parse_mode="HTML",
            link_preview_options=LinkPreviewOptions(is_disabled=True)
        )
        logging.info(f"Пользователь {user_db_id} с несколькими группами выбрал локацию {location_id} (handle_location_selection)")


async def handle_back_to_location_selection(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    user_db_id = is_admin(user_id)
    if not user_db_id:
        await callback_query.answer("У вас нет доступа")
        logging.info(f"Пользователь {user_id} не админ (handle_back_to_location_selection)")
        return
    
    callback_data = callback_query.data
    training_datetime_str = callback_data.split('|')[1]
    training_datetime = datetime.strptime(training_datetime_str, "%Y-%m-%d %H:%M:%S")

    formatted_date = training_datetime.strftime("%d.%m")
    formatted_time = training_datetime.strftime("%H:%M")
    day_name = DaysRepository.get_day_name(training_datetime.weekday() + 1)

    await callback_query.message.edit_text(
        text=(f"<b>{day_name} {formatted_time} ({formatted_date})</b>\n\n"
            f"<b>Выберите локацию тренировки</b>"),
        reply_markup=locations_keyboard(training_datetime),
        parse_mode="HTML"
    )
    logging.info(f"Пользователь {user_db_id} вернулся к выбору локации (handle_back_to_location_selection)")
    


async def handle_max_places(message: Message, bot: Bot, state: FSMContext):
    state_data = await state.get_data()
    await state.clear()

    user_id = message.from_user.id
    user_db_id = is_admin(user_id)
    if not user_db_id:
        await message.answer("У вас нет доступа")
        logging.info(f"Пользователь {user_id} не админ (handle_max_places)")
        return
    

    training_datetime: datetime = state_data['training_datetime']

    location_id = state_data['location_id']
    group_id = state_data['group_id']
    bot_message: Message = state_data['bot_message']

    groups_id = UsersGroupsRepository.get_user_groups_id(user_db_id)
    if len(groups_id) == 1:
        group_selection = False
    elif len(groups_id) > 1:
        group_selection = True

    await bot_message.edit_reply_markup(reply_markup=None)

    try:
        max_places = int(message.text.strip())
        if max_places <= 0:
            raise ValueError
        
    except:
        day_name = DaysRepository.get_day_name(training_datetime.weekday() + 1)
        formatted_date = training_datetime.strftime("%d.%m")
        formatted_time = training_datetime.strftime("%H:%M")
        location_info = get_location_info(location_id)

        new_message = await message.answer(
            text=(f"<b>{day_name} {formatted_time} ({formatted_date})</b>\n"
            f"{location_info}\n\n"
            f"<b>Назначьте тренировку или напишите ещё раз количество доступных мест (неверный формат)</b>"),
            reply_markup=without_places_keyboard(training_datetime, location_id, group_id, group_selection=group_selection),
            parse_mode="HTML",
            link_preview_options=LinkPreviewOptions(is_disabled=True)
        )
        await state.update_data(
            training_datetime=training_datetime,
            location_id=location_id,
            group_id=group_id,
            bot_message=new_message
        )
        await state.set_state(TrainingStates.waiting_for_places)
        logging.info(f"Пользователь {user_db_id} неверно ввёл количество мест (handle_max_places)")
        return

    user_id = message.from_user.id
    chat_id = message.chat.id

    training_id = TrainingsRepository.add_training(
        date_time=training_datetime,
        location_id=location_id
    )
    if not training_id:
        await message.answer(f"Не удалось добавить тренировку в базу данных")
        logging.error(f"Не удалось создать тренировку (handle_max_places)")
        return

    EventsRepository.add_training(training_id, user_db_id)

    group = GroupsRepository.get_group_by_id(group_id)
    if not group:
        await message.answer("Ошибка: группа не найдена")
        logging.error(f"Группа {group_id} не найдена (handle_max_places)")
        return

    telegram_chat_id = group['telegram_chat_id']

    TrainingsGroupsRepository.add(training_id, group['id'], max_places=max_places)

    registration_message = await send_registration_message(bot, telegram_chat_id, training_id)
    MessagesRepository.add_message(training_id, registration_message)

    private_message = await send_private_message(bot, training_id, chat_id)
    MessagesRepository.add_message(training_id, private_message)

    logging.info(f"Пользователь {user_db_id} назначил кастомную тренировку {training_id} (handle_max_places)")

    return await send_slot_selection(bot, user_id, user_db_id)

async def handle_confirm_custom_training(callback_query: CallbackQuery, bot: Bot, state: FSMContext):
    await state.clear()
    user_id = callback_query.from_user.id
    user_db_id = is_admin(user_id)
    if not user_db_id:
        await callback_query.answer("У вас нет доступа")
        logging.info(f"Пользователь {user_id} не админ (handle_confirm_custom_training)")
        return
    
    callback_data = callback_query.data
    parts = callback_data.split("|")

    training_datetime_str = parts[1]
    location_id = parts[2]
    group_id = int(parts[3])

    training_datetime = datetime.strptime(training_datetime_str, "%Y-%m-%d %H:%M:%S")

    training_id = TrainingsRepository.add_training(
        date_time=training_datetime,
        location_id=location_id
    )
    if not training_id:
        await callback_query.answer(f"Не удалось добавить тренировку в базу данных")
        logging.error(f"Не удалось добавить тренировку (handle_confirm_custom_training)")
        return

    EventsRepository.add_training(training_id, user_db_id)

    group = GroupsRepository.get_group_by_id(group_id)
    if not group:
        await callback_query.answer("Ошибка: группа не найдена")
        logging.error(f"Не удалось найти группу {group_id} (handle_confirm_custom_training)")
        return
    
    telegram_chat_id = group['telegram_chat_id']

    TrainingsGroupsRepository.add(training_id, group['id'], max_places=None)

    MessagesRepository.add_message(training_id, callback_query.message)

    registration_message = await send_registration_message(bot, telegram_chat_id, training_id)
    MessagesRepository.add_message(training_id, registration_message)

    await update_private_message(bot, training_id, callback_query.message)

    logging.info(f"Пользователь {user_db_id} назначил кастомную тренировку {training_id} (handle_confirm_custom_training)")
    
    return await send_slot_selection(bot, user_id, user_db_id)

async def handle_group_selection(callback_query: CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback_query.from_user.id
    user_db_id = is_admin(user_id)
    if not user_db_id:
        await callback_query.answer("У вас нет доступа")
        logging.info(f"Пользователь {user_id} не админ (handle_group_selection)")
        return

    callback_data = callback_query.data
    parts = callback_data.split('|')

    training_datetime_str = parts[1]
    location_id = parts[2]
    group_id = parts[3]

    group = GroupsRepository.get_group_by_id(group_id)
    if not group:
        await callback_query.answer("Ошибка: группа не найдена")
        logging.error(f"Не удалось найти группу {group_id} (handle_confirm_custom_training)")
        return

    group_name = group['name']
    group_info = f"• Для группы: {group_name}"
    

    training_datetime = datetime.strptime(training_datetime_str, "%Y-%m-%d %H:%M:%S")
    day_name = DaysRepository.get_day_name(training_datetime.weekday() + 1)

    formatted_date = training_datetime.strftime("%d.%m")
    formatted_time = training_datetime.strftime("%H:%M")
    location_info = get_location_info(location_id)

    
    await state.update_data(
        training_datetime=training_datetime,
        location_id=location_id,
        group_id=group_id,
        bot_message=callback_query.message
    )
    await callback_query.message.edit_text(
        text=(f"<b>{day_name} {formatted_time} ({formatted_date})</b>\n"
        f"{location_info}\n"
        f"{group_info}\n\n"
        f"<b>Назначьте тренировку или напишите количество доступных мест</b>"),
        reply_markup=without_places_keyboard(training_datetime, location_id, group_id, group_selection=True),
        parse_mode="HTML",
        link_preview_options=LinkPreviewOptions(is_disabled=True)
    )
    await state.set_state(TrainingStates.waiting_for_places)
    logging.info(f"Пользователь {user_db_id} выбрал группу {group_id} (handle_group_selection)")