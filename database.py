from mysql.connector import Error, connect
from datetime import datetime
from aiogram.types import Message
import logging

from config.bot_config import NEW_GROUP_NAME, TIMEZONE

from config.db_config import (
    DB_CONFIG,
    UserStatus, 
    TrainingStatus, 
    RegistrationStatus,
    SlotStatus,
    EventStatus
)

def is_admin(user_id: int):
    return UsersRepository.is_admin(user_id)

def is_participant(user_id: int):
    return UsersRepository.is_participant(user_id)

def now():
    return datetime.now(TIMEZONE)


def get_db_connection():
    try:
        return connect(**DB_CONFIG)
    except Error as e:
        logging.error(f"Ошибка подключения к БД: {e}")
        return None
    

def execute_query(query: str, params = None, fetch_one: bool = False, fetch_all: bool = False, rowcount: bool = False):
    connection = get_db_connection()
    if not connection:
        return None
    try:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(query, params or ())
            if fetch_one:
                return cursor.fetchone()
            if fetch_all:
                return cursor.fetchall()
            connection.commit()
            if rowcount:
                return cursor.rowcount
            return cursor.lastrowid
    except Exception as e:
        logging.error(f"Ошибка выполнения запроса: {e}\nQuery: {query}\nParams: {params}")
        raise
    finally:
        connection.close()

class StatisticsRepository:
    def clear():
        query = """
        TRUNCATE TABLE statistics
        """
        return execute_query(query)

    def get_periods(group_id: int):
        query = """
        SELECT DISTINCT period_name
        FROM statistics s
        JOIN users_groups ug ON ug.user_id = s.user_id
        WHERE ug.group_id = %s
        ORDER BY 
          CASE 
            WHEN period_name = %s THEN 1
            WHEN period_name = %s THEN 2
            ELSE 3
          END,
          period_name DESC
        """
        rows = execute_query(query, (group_id, "Текущая неделя", "Предыдущая неделя"), fetch_all=True)
        return [row['period_name'] for row in rows] if rows else []

    def get_group_stats(group_id: int):
        query = """
        SELECT *
        FROM statistics s
        JOIN users u ON u.id = s.user_id
        JOIN users_groups ug on ug.user_id = u.id
        WHERE ug.group_id = %s
        AND (u.user_status_id = %s
        OR u.user_status_id = %s)
        """
        return execute_query(
            query=query, 
            params=(group_id, UserStatus.PARTICIPANT, UserStatus.PARTICIPANT_ADMIN),
            fetch_all=True
        ) or []
    
    def insert_by_period(beg_date: datetime, end_date: datetime, period_name: str):
        query = """
        INSERT INTO statistics (user_id, period_name, trainings_count)
        SELECT r.user_id, %s AS period_name, COUNT(*) AS cnt
        FROM registrations r
        JOIN trainings t ON r.training_id = t.id
        JOIN trainings_groups tg ON t.id = tg.training_id
        WHERE r.registration_status_id = %s
        AND t.training_status_id = %s
        AND t.date_time >= %s
        AND t.date_time < %s
        GROUP BY r.user_id
        """
        execute_query(
            query=query,
            params=(period_name, RegistrationStatus.COMPLETED, TrainingStatus.COMPLETED, beg_date, end_date)
        )

    def insert_monthly_by_period(beg_date: datetime, end_date: datetime):
        query = """
        INSERT INTO statistics (user_id, period_name, trainings_count)
        SELECT r.user_id, DATE_FORMAT(t.date_time, '%m.%Y') AS period_name, COUNT(*) AS cnt
        FROM registrations r
        JOIN trainings t ON r.training_id = t.id
        JOIN trainings_groups tg ON t.id = tg.training_id
        WHERE r.registration_status_id = %s
        AND t.training_status_id = %s
        AND t.date_time >= %s
        AND t.date_time < %s
        GROUP BY r.user_id, period_name
        """
        execute_query(
            query=query,
            params=(RegistrationStatus.COMPLETED, TrainingStatus.COMPLETED, beg_date, end_date)
        )
    

class EventsRepository:
    def add_registration(registration_id: int):
        query = """
        INSERT INTO events (event_type_id, registration_id, happened_at)
        VALUES (%s, %s, %s)
        """
        return execute_query(query, (EventStatus.REGISTRATION_ADDED, registration_id, now()))

    def cancel_registration_by_participant(registration_id: int):
        query = """
        INSERT INTO events (event_type_id, registration_id, happened_at)
        VALUES (%s, %s, %s)
        """
        return execute_query(
            query=query, 
            params=(EventStatus.REGISTRATION_CANCELED_BY_PARTICIPANT, registration_id, now())
        )

    def cancel_registration_by_training(registration_id: int):
        query = """
        INSERT INTO events (event_type_id, registration_id, happened_at)
        VALUES (%s, %s, %s)
        """
        return execute_query(
            query=query, 
            params=(EventStatus.REGISTRATION_CANCELED_BY_TRAINING, registration_id, now())
        )
        
    def complete_registration(registration_id: int):
        query = """
        INSERT INTO events (event_type_id, registration_id, happened_at)
        VALUES (%s, %s, %s)
        """
        execute_query(query, (EventStatus.REGISTRATION_COMPLETED, registration_id, now()))

    def add_training(training_id: int, user_db_id: int):
        query = """
        INSERT INTO events (event_type_id, training_id, user_id, happened_at)
        VALUES (%s, %s, %s, %s)
        """
        return execute_query(query, (EventStatus.TRAINING_ADDED, training_id, user_db_id, now()))
        

    def cancel_training(training_id: int, user_db_id: int):
        query = """
            INSERT INTO events (event_type_id, training_id, user_id, happened_at)
            VALUES (%s, %s, %s, %s)
            """
        return execute_query(query, (EventStatus.TRAINING_CANCELED, training_id, user_db_id, now()))
        
 
    def complete_training(training_id: int):
        query = """
        INSERT INTO events (event_type_id, training_id, happened_at)
        VALUES (%s, %s, %s)
        """
        return execute_query(query, (EventStatus.TRAINING_COMPLETED, training_id, now()))
        
    def add_user(user_db_id: int):
        query = """
        INSERT INTO events (event_type_id, user_id, happened_at)
        VALUES (%s, %s, %s)
        """
        return execute_query(query, (EventStatus.USER_ADDED, user_db_id, now()))
        
    def add_group(group_id: int):
        query = """
        INSERT INTO events (event_type_id, group_id, happened_at)
        VALUES (%s, %s, %s)
        """
        return execute_query(query, (EventStatus.GROUP_ADDED, group_id, now()))
        

class MessagesRepository:
    def add_message(training_id: int, message: Message):
        query = """
        INSERT INTO messages (training_id, telegram_chat_id, telegram_message_id)
        VALUES (%s, %s, %s)
        """
        telegram_chat_id = message.chat.id
        telegram_message_id = message.message_id
        return execute_query(query, (training_id, telegram_chat_id, telegram_message_id))
        
    def get_private_message(training_id: int):
        query = """
        SELECT telegram_chat_id, telegram_message_id
        FROM messages
        WHERE (telegram_chat_id > 0 AND training_id = %s)
        """
        return execute_query(query, (training_id,), fetch_one=True)
        
    def get_group_message_by_chat_id(training_id: int, telegram_chat_id: int):
        query = """
                SELECT telegram_chat_id, telegram_message_id
                FROM messages
                WHERE (training_id = %s and telegram_chat_id = %s)
                """
        return execute_query(query, (training_id, telegram_chat_id), fetch_one=True)

    def get_group_message_by_group_id(training_id: int, group_id: int):
        query = """
        SELECT messages.telegram_chat_id, messages.telegram_message_id
        FROM messages
        JOIN participant_groups ON messages.telegram_chat_id = participant_groups.telegram_chat_id
        WHERE (messages.training_id = %s and participant_groups.id = %s)
        """
        return execute_query(query, (training_id, group_id), fetch_one=True)

    def get_group_messages(training_id: int):
        query = """
        SELECT telegram_chat_id, telegram_message_id
        FROM messages
        WHERE (training_id = %s and telegram_chat_id < 0)
        """
        return execute_query(query, (training_id,), fetch_all=True)
        

class TrainingsRepository:
    def add_training(date_time: datetime, location_id: int):
        query = """
        INSERT INTO trainings (date_time, location_id, training_status_id)
        VALUES (%s, %s, %s)
        """
        return execute_query(query, (date_time, location_id, TrainingStatus.ACTIVE))
    
    def add_training_with_slot(date_time: datetime, location_id: int, slot_id: int):
        query = """
        INSERT INTO trainings (date_time, location_id, slot_id, training_status_id)
        VALUES (%s, %s, %s, %s)
        """
        return execute_query(query, (date_time, location_id, slot_id, TrainingStatus.ACTIVE))
    
    def get_training_by_id(training_id: int):
        query = """
        SELECT * 
        FROM trainings 
        WHERE id = %s
        """
        return execute_query(query, (training_id,), fetch_one=True)
        
    def cancel_training(training_id: int):
        query = """
        UPDATE trainings 
        SET training_status_id = %s 
        WHERE id = %s 
        AND training_status_id = %s
        """
        result = execute_query(
            query=query, 
            params=(TrainingStatus.CANCELLED, training_id, TrainingStatus.ACTIVE), 
            rowcount=True
        )
        return result > 0
        
  
    def complete_training(training_id: int):
        query = """
        UPDATE trainings 
        SET training_status_id = %s
        WHERE id = %s 
        AND training_status_id = %s
        """
        result = execute_query(
            query=query, 
            params=(TrainingStatus.COMPLETED, training_id, TrainingStatus.ACTIVE), 
            rowcount=True
        )
        return result > 0
        
    def check_training_exists(date_time: datetime, location_id: int, slot_id: int):
        query = """
        SELECT COUNT(*) as count 
        FROM trainings 
        WHERE date_time = %s 
        AND location_id = %s
        AND slot_id = %s
        AND training_status_id = %s
        """
        result = execute_query(
            query=query, 
            params=(date_time, location_id, slot_id, TrainingStatus.ACTIVE), 
            fetch_one=True
        )
        return result['count'] > 0 if result else False
        
    def get_active_trainings():
        query = """
        SELECT *
        FROM trainings
        WHERE training_status_id = %s
        """
        return execute_query(query, (TrainingStatus.ACTIVE,), fetch_all=True)

# Функции для работы с пользователями
class UsersRepository:
    def add_user(name: str, telegram_id: int):
        query = """
        INSERT INTO users (name, telegram_id, user_status_id)
        VALUES (%s, %s, %s)
        """
        return execute_query(query, (name, telegram_id, UserStatus.PARTICIPANT))

    def is_admin(telegram_id: int):
        query = """
        SELECT id 
        FROM users 
        WHERE (user_status_id = %s
        OR user_status_id = %s)
        AND telegram_id = %s
        """
        result = execute_query(
            query=query, 
            params=(UserStatus.PARTICIPANT_ADMIN, UserStatus.COACH, telegram_id), 
            fetch_one=True
        )
        return result['id'] if result else None

    def is_participant(telegram_id: int):
        query = """
        SELECT id
        FROM users 
        WHERE (user_status_id = %s
        OR user_status_id = %s)
        AND telegram_id = %s
        """
        result = execute_query(
            query=query, 
            params=(UserStatus.PARTICIPANT, UserStatus.PARTICIPANT_ADMIN, telegram_id), 
            fetch_one=True
        )
        return result['id'] if result else None
        
    def get_user_db_id(telegram_id: int):
        query = """
        SELECT id
        FROM users 
        WHERE telegram_id = %s
        """
        result = execute_query(query, (telegram_id,), fetch_one=True)
        return result['id'] if result else None
        
    def get_user(telegram_id: int):
        query = """
        SELECT *
        FROM users
        WHERE telegram_id = %s
        """
        return execute_query(query, (telegram_id,), fetch_one=True)


class RegistrationsRepository:
    def add_registration(training_id: int, user_db_id: int):
        query = """
        INSERT INTO registrations (registration_status_id, training_id, user_id)
        VALUES (%s, %s, %s)
        """
        return execute_query(query, (RegistrationStatus.ACTIVE, training_id, user_db_id))
   
    def cancel_registration_by_participant(registration_id: int):
        query = """
        UPDATE registrations 
        SET registration_status_id = %s
        WHERE id = %s
        AND registration_status_id = %s
        """
        result = execute_query(
            query=query, 
            params=(RegistrationStatus.CANCELLED_BY_PARTICIPANT, registration_id, RegistrationStatus.ACTIVE), 
            rowcount=True
        )
        return result > 0
   
    def cancel_registration_by_training(registration_id: int):
        query = """
        UPDATE registrations 
        SET registration_status_id = %s
        WHERE id = %s 
        AND registration_status_id = %s
        """
        result = execute_query(
            query=query, 
            params=(RegistrationStatus.CANCELLED_BY_TRAINING, registration_id, RegistrationStatus.ACTIVE), 
            rowcount=True
        )
        return result > 0
           
    def complete_registration(registration_id: int):
        query = """
        UPDATE registrations 
        SET registration_status_id = %s
        WHERE id = %s
        AND registration_status_id = %s
        """
        result = execute_query(
            query=query, 
            params=(RegistrationStatus.COMPLETED, registration_id, RegistrationStatus.ACTIVE), 
            rowcount=True
        )
        return result > 0
    
    def check_registration_exist(training_id: int, user_db_id: int):
        query = """
        SELECT COUNT(*) as count
        FROM registrations 
        WHERE training_id = %s 
        AND user_id = %s
        AND registration_status_id = %s
        """
        result = execute_query(
            query=query, 
            params=(training_id, user_db_id, RegistrationStatus.ACTIVE), 
            fetch_one=True
        )
        return result['count'] > 0 if result else False

    def get_active_registration_id(training_id: int, user_db_id: int):
        query = """
        SELECT id
        FROM registrations
        WHERE training_id = %s
        AND user_id = %s
        AND registration_status_id = %s
        """
        result = execute_query(
            query=query, 
            params=(training_id, user_db_id, RegistrationStatus.ACTIVE), 
            fetch_one=True
        )
        return result['id'] if result else None
        
    def get_active_registrations_by_chat_id(training_id: int, telegram_chat_id: int):
        query = """
        SELECT registrations.id, users.name, users.telegram_id
        FROM registrations
        JOIN users ON registrations.user_id = users.id
        JOIN users_groups ON users_groups.user_id = users.id
        JOIN participant_groups ON participant_groups.id = users_groups.group_id
        WHERE (registrations.training_id = %s
        AND participant_groups.telegram_chat_id = %s
        AND registrations.registration_status_id = %s)
        ORDER BY registrations.id
        """
        return execute_query(
            query=query, 
            params=(training_id, telegram_chat_id, RegistrationStatus.ACTIVE), 
            fetch_all=True
        )
            
    def get_active_registrations(training_id: int):
        query = """
        SELECT registrations.id, users.name, users.telegram_id
        FROM registrations
        JOIN users ON registrations.user_id = users.id
        WHERE registrations.training_id = %s
        AND registrations.registration_status_id = %s
        ORDER BY registrations.id
        """
        return execute_query(query, (training_id, RegistrationStatus.ACTIVE), fetch_all=True)
        
    def get_completed_registrations(training_id: int):
        query = """
        SELECT registrations.id, users.name, users.telegram_id
        FROM registrations
        JOIN users ON registrations.user_id = users.id
        WHERE registrations.training_id = %s
        AND registrations.registration_status_id = %s
        ORDER BY registrations.id
        """
        return execute_query(query, (training_id, RegistrationStatus.COMPLETED), fetch_all=True)
    
    def get_completed_registrations_by_chat_id(training_id: int, telegram_chat_id: int):
        query = """
        SELECT registrations.id, users.name, users.telegram_id
        FROM registrations
        JOIN users ON registrations.user_id = users.id
        JOIN users_groups ON users_groups.user_id = users.id
        JOIN participant_groups ON participant_groups.id = users_groups.group_id
        WHERE (registrations.training_id = %s
        AND participant_groups.telegram_chat_id = %s
        AND registrations.registration_status_id = %s)
        ORDER BY registrations.id
        """
        return execute_query(
            query=query, 
            params=(training_id, telegram_chat_id, RegistrationStatus.COMPLETED), 
            fetch_all=True
        )
        
    def is_places_left(training_id: int, telegram_chat_id: int):
        query = """
        SELECT trainings_groups.max_places
        FROM trainings_groups
        JOIN participant_groups ON participant_groups.id = trainings_groups.group_id
        WHERE trainings_groups.training_id = %s 
        AND participant_groups.telegram_chat_id = %s;
        """
        result = execute_query(query, (training_id, telegram_chat_id), fetch_one=True)
        if not result or not result['max_places']:
            return True
        
        max_places = result['max_places']

        query = """
        SELECT COUNT(*) as count
        FROM registrations
        JOIN users ON registrations.user_id = users.id
        JOIN users_groups ON users.id = users_groups.user_id
        JOIN participant_groups ON participant_groups.id = users_groups.group_id
        WHERE registrations.training_id = %s
        AND participant_groups.telegram_chat_id = %s
        AND registrations.registration_status_id = %s
        """
        result = execute_query(
            query=query, 
            params=(training_id, telegram_chat_id, RegistrationStatus.ACTIVE), 
            fetch_one=True
        )
        if not result or not result['count']:
            return True

        return max_places > result['count']


class LocationsRepository:
    def get_location(location_id: int):
        query = """
        SELECT *
        FROM locations
        WHERE id = %s
        """
        return execute_query(query, (location_id,), fetch_one=True)
        
    def get_all_locations():
        query = """
        SELECT *
        FROM locations
        """
        return execute_query(query, fetch_all=True)
        
# Функции для работы с группами
class GroupsRepository:
    def get_group_by_chat_id(telegram_chat_id: int):
        query = """
        SELECT *
        FROM participant_groups
        WHERE telegram_chat_id = %s
        """
        return execute_query(query, (telegram_chat_id,), fetch_one=True)

    def get_group_by_id(group_id: int):
        query = """
        SELECT *
        FROM participant_groups
        WHERE id = %s
        """
        return execute_query(query, (group_id,), fetch_one=True)
    
    def get_all_groups():
        query = """
        SELECT *
        FROM participant_groups
        """
        return execute_query(query, fetch_all=True)

    def add_group(telegram_chat_id: int):
        query = """
        INSERT INTO participant_groups (name, telegram_chat_id)
        VALUES (%s, %s)
        """
        return execute_query(query, (NEW_GROUP_NAME, telegram_chat_id))

class SlotsGroupsRepository:
    def get_info(slot_id: int, group_id: int):
        query = """
        SELECT slots_groups.*, participant_groups.telegram_chat_id, participant_groups.name 
        FROM slots_groups
        JOIN participant_groups ON participant_groups.id = slots_groups.group_id
        WHERE slot_id = %s
        AND group_id = %s
        """
        return execute_query(query, (slot_id, group_id), fetch_one=True)

    def get_slot_groups(slot_id: int):
        query = """
        SELECT slots_groups.max_places, participant_groups.name, participant_groups.id, participant_groups.telegram_chat_id
        FROM slots_groups
        JOIN participant_groups ON participant_groups.id = slots_groups.group_id
        WHERE slots_groups.slot_id = %s
        """
        return execute_query(query, (slot_id,), fetch_all=True)
    
    def get_slot_groups_id(slot_id: int):
        query = """
        SELECT group_id
        FROM slots_groups
        WHERE slot_id = %s
        """
        return execute_query(query, (slot_id,), fetch_all=True)
        
    def get_max_places_by_group_id(slot_id: int, group_id: int):
        query = """
        SELECT max_places
        FROM slots_groups
        WHERE slot_id = %s
        AND group_id = %s
        """
        result = execute_query(query, (slot_id, group_id), fetch_one=True)
        return result['max_places'] if result else None
        
class TrainingsGroupsRepository:
    def get_max_places_by_group_id(training_id: int, group_id: int):
        query = """
        SELECT max_places
        FROM trainings_groups
        WHERE training_id = %s
        AND group_id = %s
        """
        result = execute_query(query, (training_id, group_id), fetch_one=True)
        return result['max_places'] if result else None

    def get_training_groups(training_id: int):
        query = """
        SELECT trainings_groups.max_places, participant_groups.name, participant_groups.telegram_chat_id
        FROM trainings_groups
        JOIN participant_groups ON participant_groups.id = trainings_groups.group_id
        WHERE trainings_groups.training_id = %s
        """
        return execute_query(query, (training_id,), fetch_all=True)
    
    def get_training_groups_id(training_id: int):
        query = """
        SELECT group_id
        FROM trainings_groups
        WHERE training_id = %s
        """
        return execute_query(query, (training_id,), fetch_all=True)
        
    def add(training_id: int, group_id: int, max_places: int = None):
        query = """
        INSERT INTO trainings_groups (training_id, group_id, max_places)
        VALUES (%s, %s, %s)
        """
        return execute_query(query, (training_id, group_id, max_places))
    
        
class DaysRepository:
    def get_day_name(day_id: int):
        query = """
        SELECT name 
        FROM days_of_week 
        WHERE id = %s
        """
        result = execute_query(query, (day_id,), fetch_one=True)
        return result['name'] if result else None


class SlotsRepository:
    def get_active_slots():
        query = """
        SELECT *
        FROM slots
        WHERE slot_status_id = %s
        ORDER BY day_id, time
        """
        return execute_query(query, (SlotStatus.ACTIVE,), fetch_all=True)
    
    def get_slot_by_id(slot_id: int):
        query = """
        SELECT *
        FROM slots
        WHERE id = %s
        """
        return execute_query(query, (slot_id,), fetch_one=True)
    
class UsersGroupsRepository:
    def add(user_db_id: int, group_id: int):
        query = """
        INSERT INTO users_groups (user_id, group_id)
        VALUES (%s, %s)
        """
        return execute_query(query, (user_db_id, group_id))
    
    def get_user_groups_id(user_db_id: int):
        query = """
        SELECT group_id
        FROM users_groups
        WHERE user_id = %s
        """
        return execute_query(query, (user_db_id,), fetch_all=True)
    
    def is_user_in_one_group(user_db_id: int):
        query = """
        SELECT group_id
        FROM users_groups
        WHERE user_id = %s
        """
        results = execute_query(query, (user_db_id,), fetch_all=True)
        
        if len(results) == 1:
            return results[0]['group_id']
        return None
    
    def get_participants(chat_id: int):
        query = """
        SELECT users.telegram_id
        FROM users_groups
        JOIN participant_groups ON participant_groups.id = users_groups.group_id
        JOIN users ON users.id = users_groups.user_id
        WHERE (users.user_status_id = %s
        OR users.user_status_id = %s)
        AND participant_groups.telegram_chat_id = %s
        """
        return execute_query(
            query=query, 
            params=(UserStatus.PARTICIPANT, UserStatus.PARTICIPANT_ADMIN, chat_id), 
            fetch_all=True
        )
    
    def get_participants_by_group_id(group_id: int):
        query = """
        SELECT users.id, users.name
        FROM users_groups
        JOIN users ON users.id = users_groups.user_id
        WHERE (users.user_status_id = %s
        OR users.user_status_id = %s)
        AND users_groups.group_id = %s
        ORDER BY users.name
        """
        return execute_query(
            query=query, 
            params=(UserStatus.PARTICIPANT, UserStatus.PARTICIPANT_ADMIN, group_id), 
            fetch_all=True
        )