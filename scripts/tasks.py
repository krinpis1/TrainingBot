from aiogram import Bot
from asyncio import sleep
import logging

from config.bot_config import TRAINING_COMPLETE_UPDATE_TIME
from .complete_trainings import complete_trainings

async def complete_trainings_task(bot: Bot):
    while True:
        try:
            await complete_trainings(bot)
        except Exception as e:
            logging.error(f"Ошибка в complete_trainings: {e}")
        await sleep(TRAINING_COMPLETE_UPDATE_TIME)