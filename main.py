from asyncio import create_task, run
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.types import ChatMemberUpdated
from aiogram.fsm.context import FSMContext

from config.bot_config import BOT_TOKEN
from handlers import (
    cmd_start,
    handle_slot_selection,
    handle_return_slot_selection,
    handle_training_confirmation,
    handle_cancel_training_confirm,
    handle_cancel_training_final,
    handle_keep_training,
    handle_new_registration,
    handle_cancel_registration,
    handle_user_name,
    handle_user_status_update,
    handle_custom_training,
    handle_day_selection,
    handle_training_time,
    handle_location_selection,
    handle_max_places,
    handle_confirm_custom_training,
    handle_back_to_location_selection,
    handle_group_selection
)
from states import RegistrationStates, TrainingStates
from utils import bot_added, send_slot_selection
from messages_data import update_message, update_old_message, delete_message
from scripts.tasks import complete_trainings_task
from database import UsersRepository

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# При старте бота запускаем фоновую задачу
async def on_startup(bot: Bot):
    create_task(complete_trainings_task(bot))

# При добавлении бота в чат сохраняем чат в базу данных
@dp.my_chat_member()
async def bot_added_wrapper(event:ChatMemberUpdated):
    await bot_added(event)

@dp.message(RegistrationStates.waiting_for_name)
async def user_name_wrapper(message: Message, state: FSMContext):
    await handle_user_name(message, state)

@dp.message(TrainingStates.waiting_for_time)
async def training_time_wrapper(message: Message, state: FSMContext):
    new_message = await handle_training_time(message, state)
    user_id = message.from_user.id
    if new_message:
        await update_message(user_id, new_message, bot)
    else:
        delete_message(user_id)

@dp.message(TrainingStates.waiting_for_places)
async def max_places_wrapper(message: Message, state: FSMContext):
    user_id = message.from_user.id
    new_message = await handle_max_places(message, bot, state)
    await update_message(user_id, new_message, bot)

@dp.message(Command("start"))
async def start_wrapper(message: Message, state: FSMContext):
    user_id = message.from_user.id
    new_message = await cmd_start(message, bot, state)
    await update_message(user_id, new_message, bot)

@dp.callback_query(lambda c: c.data == "update_status")
async def user_status_update_wrapper(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    new_message = await handle_user_status_update(callback_query, bot)
    await update_message(user_id, new_message, bot)

@dp.callback_query(lambda c: c.data.startswith("training_slot|"))
async def slot_selection_wrapper(callback_query: CallbackQuery):
    await handle_slot_selection(callback_query)

@dp.callback_query(lambda c: c.data == "cancel_to_selection")
async def cancel_to_selection_slot_wrapper(callback_query: CallbackQuery):
    await handle_return_slot_selection(callback_query, bot)

@dp.callback_query(lambda c: c.data.startswith("confirm_training|"))
async def training_confirmation_wrapper(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    delete_message(user_id)
    new_message = await handle_training_confirmation(callback_query, bot)
    await update_message(user_id, new_message, bot)

@dp.callback_query(lambda c: c.data.startswith("cancel_training_confirm|"))
async def cancel_training_confirm_wrapper(callback_query: CallbackQuery):
    await handle_cancel_training_confirm(callback_query)

@dp.callback_query(lambda c: c.data.startswith("cancel_training_final|"))
async def cancel_training_final_wrapper(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    await handle_cancel_training_final(callback_query, bot)
    succes = await update_old_message(user_id, bot)
    if not succes:
        user_db_id = UsersRepository.get_user_db_id(user_id)
        new_message = await send_slot_selection(bot, user_id, user_db_id)
        await update_message(user_id, new_message, bot)

@dp.callback_query(lambda c: c.data.startswith("keep_training|"))
async def keep_training_wrapper(callback_query: CallbackQuery):
    await handle_keep_training(callback_query, bot)

@dp.callback_query(lambda c: c.data.startswith("new_registration|"))
async def new_registration_wrapper(callback_query: CallbackQuery):
    await handle_new_registration(callback_query, bot)

@dp.callback_query(lambda c: c.data.startswith("cancel_registration|"))
async def cancel_registration_wrapper(callback_query: CallbackQuery):
    await handle_cancel_registration(callback_query, bot)

@dp.callback_query(lambda c: c.data == "custom_training")
async def custom_training_wrapper(callback_query: CallbackQuery, state: FSMContext):
    await handle_custom_training(callback_query, state)

@dp.callback_query(lambda c: c.data.startswith("date|"))
async def day_selection_wrapper(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    new_message = await handle_day_selection(callback_query, state)
    await update_message(user_id, new_message, bot)

@dp.callback_query(lambda c: c.data.startswith("datetime_location|"))
async def location_selection_wrapper(callback_query: CallbackQuery, state: FSMContext):
    await handle_location_selection(callback_query, state)

@dp.callback_query(lambda c: c.data.startswith("datetime|"))
async def back_wrapper(callback_query: CallbackQuery):
    await handle_back_to_location_selection(callback_query)

@dp.callback_query(lambda c: c.data.startswith("training_info|"))
async def group_selection_wrapper(callback_query: CallbackQuery, state: FSMContext):
    await handle_group_selection(callback_query, state)

@dp.callback_query(lambda c: c.data.startswith("confirm_custom_training"))
async def confirm_custom_training_wrapper(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    new_message = await handle_confirm_custom_training(callback_query, bot, state)
    await update_message(user_id, new_message, bot)

async def main():
    await on_startup(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен")