from os import getenv
from dotenv import load_dotenv

class UserStatus:
    PARTICIPANT = 1
    PARTICIPANT_ADMIN = 2
    COACH = 3
    INACTIVE = 4

class RegistrationStatus:
    ACTIVE = 1
    CANCELLED_BY_PARTICIPANT = 2
    CANCELLED_BY_TRAINING = 3
    COMPLETED = 4

class TrainingStatus:
    ACTIVE = 1
    CANCELLED = 2
    COMPLETED = 3

class SlotStatus:
    ACTIVE = 1
    INACTIVE = 2

class EventStatus:
    REGISTRATION_ADDED = 1
    REGISTRATION_CANCELED_BY_PARTICIPANT = 2
    REGISTRATION_CANCELED_BY_TRAINING = 3
    REGISTRATION_COMPLETED = 4

    TRAINING_ADDED = 5
    TRAINING_CANCELED = 6
    TRAINING_COMPLETED = 7

    USER_ADDED = 8

    SLOT_ADDED = 9
    SLOT_CHANGED = 10

    GROUP_ADDED = 11

load_dotenv()

DB_CONFIG = {
    'host': getenv("DB_HOST"),
    'user': getenv("DB_USER"),
    'password': getenv("DB_PASSWORD"),
    'database': getenv("DB_NAME"),
    'port': int(getenv("DB_PORT", 3306)), # значение по умолчанию
    'auth_plugin': 'mysql_native_password'
}