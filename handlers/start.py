from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram import Bot
import logging

from config.bot_config import ADMIN_USERNAME
from config.db_config import UserStatus
from database import GroupsRepository, UsersRepository
from utils import send_slot_selection, is_user_in_chat, update_user_groups
from states import RegistrationStates
from keyboards import user_status_update_keyboard


async def cmd_start(message: Message, bot: Bot, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id

    if message.chat.id < 0:
        logging.info(f"Команда /start написана в общий чат {message.chat.id} (cmd_start)")
        return
    
    user = UsersRepository.get_user(user_id)
    if user:
        await update_user_groups(bot, user_id)
        
        name = user['name']
        if user['user_status_id'] in (UserStatus.PARTICIPANT_ADMIN, UserStatus.COACH):
            await message.answer(f"{name}, Вы можете управлять тренировками!")
            logging.info(f"Пользователь {user['id']} имеет доступ к боту (cmd_start)")
            return await send_slot_selection(bot, user_id, user['id'])

        if user['user_status_id'] == UserStatus.PARTICIPANT:
            await message.answer(
                    (f"{name}, Вы уже являетесь участником!\n\n"
                    f"Если вам потребуется доступ к управлению тренировками, обратитесь к {ADMIN_USERNAME}"),
                    reply_markup=user_status_update_keyboard()
                )
            logging.info(f"Пользователь {user['id']} уже участник (cmd_start)")
            return
        
    groups = GroupsRepository.get_all_groups()
    if not groups:
        await message.answer("Сначала добавьте бота в чат клуба!")
        logging.error(f"В БД нет групп (cmd_start, пользователь {user_id})")
        return
    
    is_user_in_any_chat = False
    groups_id = []
    for group in groups:
        chat_id = group['telegram_chat_id']
        if await is_user_in_chat(bot, chat_id, user_id):
            is_user_in_any_chat = True
            groups_id.append(group['id'])

    if not is_user_in_any_chat:
        await message.answer("У вас нет доступа к этому боту. Сначала добавьтесь в группу клуба!")
        logging.info(f"Пользователь {user_id} не состоит в группе (cmd_start)")
        return

    await state.update_data(groups_id=groups_id)
    await message.answer(
        "Напишите вашу <b>фамилию</b> и <b>имя</b>",
        parse_mode="HTML"
    )
    await state.set_state(RegistrationStates.waiting_for_name)
    logging.info(f"Ожидается ФИ от пользователя {user_id} (cmd_start)")
    return