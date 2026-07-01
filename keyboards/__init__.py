from .schedule_training_keyboards import (
    slot_selection_keyboard,
    confirmation_keyboard,
    after_appointment_keyboard,
    cancel_confirmation_keyboard
)
from .custom_training_keyboards import (
    day_selection_keyboard,
    locations_keyboard,
    back_to_day_selection_keyboard,
    without_places_keyboard,
    select_group_keyboard
)
from .registration_keyboards import (
    registration_keyboard
)
from .new_user_keyboards import user_status_update_keyboard

__all__ = [
    'slot_selection_keyboard',
    'confirmation_keyboard',
    'after_appointment_keyboard',
    'cancel_confirmation_keyboard',
    'registration_keyboard',
    'user_status_update_keyboard',
    'day_selection_keyboard',
    'locations_keyboard',
    'back_to_day_selection_keyboard',
    'without_places_keyboard',
    'select_group_keyboard'
]