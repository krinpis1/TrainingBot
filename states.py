from aiogram.filters.state import State, StatesGroup

class RegistrationStates(StatesGroup):
    waiting_for_name = State()

class TrainingStates(StatesGroup):
    waiting_for_time = State()
    waiting_for_places = State()