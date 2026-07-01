from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram import Bot
import logging

from database import UsersRepository, EventsRepository, UsersGroupsRepository
from config.bot_config import ADMIN_USERNAME
from config.db_config import UserStatus
from keyboards import user_status_update_keyboard
from utils import send_slot_selection

async def handle_user_name(message: Message, state: FSMContext):
    name = message.text.strip()
    user_id = message.from_user.id

    state_data = await state.get_data()
    await state.clear()
    groups_id = state_data.get('groups_id')
    
    if not groups_id:
        await message.answer(
            "❌ Ошибка: не удалось определить группу. Попробуйте снова /start"
        )
        logging.error(f"Ошибка с пользователем {user_id} (handle_user_name)")
        return
    
    user_db_id = UsersRepository.add_user(name, user_id)
    EventsRepository.add_user(user_db_id)
    
    for group_id in groups_id:
        UsersGroupsRepository.add(user_db_id, group_id)

    
    await message.answer(
        (f"{name}, теперь Вы можете записываться на тренировки в группе!\n\n"
        f"Если вам потребуется доступ к управлению тренировками, обратитесь к {ADMIN_USERNAME}"),
        reply_markup=user_status_update_keyboard(),
        parse_mode="HTML"
    )
    logging.info(f"Пользователь {user_db_id} добавлен (handle_user_name)")

async def handle_user_status_update(callback_query: CallbackQuery, bot: Bot):
    user_id = callback_query.from_user.id

    user = UsersRepository.get_user(telegram_id=user_id)
    if user and user['user_status_id'] in (UserStatus.PARTICIPANT_ADMIN, UserStatus.COACH):
        name = user['name']
        await callback_query.message.edit_text(
            f"{name}, Вы можете управлять тренировками!",
            reply_markup=None
        )
        logging.info(f"Пользователь {user['id']} получил доступ к управлению тренировками (handle_user_status_update)")
        return await send_slot_selection(bot, user_id, user['id'])
    
    await callback_query.answer("Недоступно")
    logging.info(f"Пользователь {user['id']} не получил доступ (handle_user_status_update)")
    return
    