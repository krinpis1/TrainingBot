from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def user_status_update_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="Обновить",
        callback_data=f"update_status"
    ))
    builder.adjust(1)
    return builder.as_markup()