from aiogram.types import InlineKeyboardButton
from datetime import datetime, timedelta
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import (
    DaysRepository,
    TrainingsRepository,
    SlotsRepository
)

from config.bot_config import TIMEZONE, TIMEZONE, MAX_TRAININGS_SHOW
from utils.other_utils import get_group_intersection

def get_next_trainings(user_db_id: int):
    slots = SlotsRepository.get_active_slots()
    if not slots:
        return []
    
    now = datetime.now(TIMEZONE)

    today_weekday = now.weekday() + 1  # 1-Пн, 2-Вт, ..., 7-Вс
    
    trainings = []
    
    for slot in slots:
        # Вычисляем дату следующей тренировки для этого слота
        day_id = slot['day_id']
        time_str = str(slot['time'])
        
        # Определяем сколько дней ждать до следующего дня недели
        days_ahead = day_id - today_weekday
        if days_ahead < 0:
            days_ahead += 7
        elif days_ahead == 0:
            # Если сегодня тот же день недели, проверяем время
            slot_time = datetime.strptime(time_str, "%H:%M:%S").time()
            current_time = now.time()
            # Если время уже прошло, берем следующую неделю
            if current_time >= slot_time:
                days_ahead = 7
        
        # Вычисляем дату
        training_date = now.date() + timedelta(days=days_ahead)
        
        # Создаем полную дату и время
        training_datetime = datetime.combine(training_date, datetime.strptime(time_str, "%H:%M:%S").time())
        
        exists = TrainingsRepository.check_training_exists(training_datetime, slot['location_id'], slot['id'])
        
        if exists:
            continue

        groups_intersection = get_group_intersection(slot['id'], user_db_id)
        if not groups_intersection:
            continue
        
        # Получаем название дня недели из базы данных
        day_name = DaysRepository.get_day_name(slot['day_id'])
        
        training_time = datetime.strptime(time_str, "%H:%M:%S").strftime("%H:%M")
        formatted_date = training_date.strftime("%d.%m")
        
        trainings.append({
            'slot_id': slot['id'],
            'day_name': day_name,
            'date': formatted_date,
            'time': training_time,
            'datetime': training_datetime
        })
    
    # Сортируем по дате (ближайшие первые)
    trainings.sort(key=lambda x: x['datetime'])
    return trainings[:MAX_TRAININGS_SHOW]


def slot_selection_keyboard(user_db_id: int):
    builder = InlineKeyboardBuilder()
    
    # Получаем ближайшие тренировки из БД
    trainings = get_next_trainings(user_db_id)
    
    for training in trainings:
        button_text = f"{training['day_name']} {training['time']} ({training['date']})"
        
        datetime = training['datetime']
        callback_data = f"training_slot|{training['slot_id']}|{datetime}"
        
        builder.add(InlineKeyboardButton(
            text=button_text,
            callback_data=callback_data
        ))
    
    button_text = "Другое"
    callback_data = "custom_training"
    
    builder.add(InlineKeyboardButton(
        text=button_text,
        callback_data=callback_data
    ))
    
    builder.adjust(1)
    return builder.as_markup()

def confirmation_keyboard(slot_id: int, training_datetime: datetime):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="✅ Назначить",
        callback_data=f"confirm_training|{slot_id}|{training_datetime}"
    ))
    builder.add(InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="cancel_to_selection"
    ))
    builder.adjust(1)
    return builder.as_markup()

def after_appointment_keyboard(training_id: int):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="❌ Отменить",
        callback_data=f"cancel_training_confirm|{training_id}"
    ))
    builder.adjust(1)
    return builder.as_markup()

def cancel_confirmation_keyboard(training_id: int):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="✅ Отменить",
        callback_data=f"cancel_training_final|{training_id}"
    ))
    builder.add(InlineKeyboardButton(
        text="◀️ Назад",
        callback_data=f"keep_training|{training_id}"
    ))
    builder.adjust(1)
    return builder.as_markup()