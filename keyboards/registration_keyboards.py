from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def registration_keyboard(training_id: int):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="Записаться",
        callback_data=f"new_registration|{training_id}"
    ))
    builder.add(InlineKeyboardButton(
        text="Отменить запись",
        callback_data=f"cancel_registration|{training_id}"
    ))
    builder.adjust(1)
    return builder.as_markup()