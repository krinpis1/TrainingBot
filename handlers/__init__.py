from .start import cmd_start
from .schedule_training_handlers import (
    handle_slot_selection,
    handle_return_slot_selection,
    handle_training_confirmation
)
from .cancel_training_handlers import (
    handle_cancel_training_confirm,
    handle_cancel_training_final,
    handle_keep_training
)
from .registration_handlers import(
    handle_new_registration,
    handle_cancel_registration
)
from .custom_training_handlers import(
    handle_custom_training,
    handle_day_selection,
    handle_training_time,
    handle_location_selection,
    handle_max_places,
    handle_confirm_custom_training,
    handle_back_to_location_selection,
    handle_group_selection
)
from .new_user_handlers import handle_user_name, handle_user_status_update

__all__ = [
    'cmd_start',
    'handle_slot_selection',
    'handle_return_slot_selection',
    'handle_training_confirmation',
    'handle_cancel_training_confirm',
    'handle_cancel_training_final',
    'handle_keep_training',
    'handle_new_registration',
    'handle_cancel_registration',
    'handle_user_name',
    'handle_user_status_update',
    'handle_custom_training',
    'handle_day_selection',
    'handle_training_time',
    'handle_location_selection',
    'handle_max_places',
    'handle_confirm_custom_training',
    'handle_back_to_location_selection',
    'handle_group_selection'
]