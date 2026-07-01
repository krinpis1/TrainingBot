from aiogram.types import InlineKeyboardButton
from datetime import datetime, timedelta
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import (
    DaysRepository, 
    LocationsRepository,
    GroupsRepository
)

from config.bot_config import TIMEZONE, MAX_DAYS_SHOW, TIMEZONE


def day_selection_keyboard():
    dates: list[datetime] = []

    now = datetime.now(TIMEZONE)

    for i in range(MAX_DAYS_SHOW):
        current_date = now + timedelta(days=i)
        dates.append(current_date)

    builder = InlineKeyboardBuilder()
    
    for date in dates:
        weekday_name = DaysRepository.get_day_name(date.weekday() + 1)
        
        date_str = date.strftime("%d.%m")
        
        button_text = f"{weekday_name} {date_str}"
        
        callback_data = f"date|{date.strftime('%Y-%m-%d')}"

        builder.add(InlineKeyboardButton(
            text=button_text,
            callback_data=callback_data
        ))

    builder.add(InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="cancel_to_selection"
    ))    
    
    builder.adjust(1)
    return builder.as_markup()

def locations_keyboard(training_datetime: datetime):
    locations = LocationsRepository.get_all_locations()
    if not locations:
        return None
    
    builder = InlineKeyboardBuilder()
    
    for location in locations:
        location_name = location['name']
        location_id = location['id']

        button_text = f"{location_name}"
        
        callback_data = f"datetime_location|{training_datetime}|{location_id}"

        builder.add(InlineKeyboardButton(
            text=button_text,
            callback_data=callback_data
        ))

    builder.add(InlineKeyboardButton(
            text="◀️ Назад",
            callback_data= f"date|{training_datetime.date()}"
        ))

    builder.adjust(1)
    return builder.as_markup()

def back_to_day_selection_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="◀️ Назад",
        callback_data=f"custom_training"
    ))
    builder.adjust(1)
    return builder.as_markup()

def without_places_keyboard(training_datetime: datetime, location_id: int, group_id: int, group_selection: bool):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="✅ Назначить",
        callback_data=f"confirm_custom_training|{training_datetime}|{location_id}|{group_id}"
    ))

    if group_selection:
        builder.add(InlineKeyboardButton(
            text="◀️ Назад",
            callback_data=f"datetime_location|{training_datetime}|{location_id}"
        ))
    else:
        builder.add(InlineKeyboardButton(
            text="◀️ Назад",
            callback_data=f"datetime|{training_datetime}"
        ))

    builder.adjust(1)
    return builder.as_markup()

def select_group_keyboard(groups_id: list, training_datetime: datetime, location_id: int):
    if not groups_id:
        return None
    
    builder = InlineKeyboardBuilder()

    for group_dict in groups_id:
        group_id = group_dict['group_id']
        group = GroupsRepository.get_group_by_id(group_id)
        group_name = group['name']
        builder.add(InlineKeyboardButton(
            text=f"{group_name}",
            callback_data=f"training_info|{training_datetime}|{location_id}|{group_id}"
        ))

    builder.add(InlineKeyboardButton(
        text=f"◀️ Назад",
        callback_data=f"datetime|{training_datetime}|{location_id}"
    ))
    
    builder.adjust(1)
    return builder.as_markup()