from google.oauth2 import service_account
from googleapiclient.discovery import build
import logging
from datetime import datetime, timedelta

from database import StatisticsRepository, UsersGroupsRepository
from config.google_sheets_config import (
    SERVICE_ACCOUNT_FILE,
    SPREADSHEETS_ID,
    SHEET_NAME
)
from config.bot_config import TIMEZONE

def get_google_sheets_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    return build('sheets', 'v4', credentials=creds, cache_discovery=False)

def build_data_matrix(participants, periods, stats_rows):
    stats_map = {}
    for row in stats_rows:
        uid = row['user_id']
        period = row['period_name']
        count = row['trainings_count']
        stats_map.setdefault(uid, {})[period] = count

    matrix = [[''] + periods]

    for user in participants:
        row = [user['name']]
        for period in periods:
            row.append(stats_map.get(user['id'], {}).get(period, 0))
        matrix.append(row)

    return matrix

def update_google_sheet(service, matrix, group_id: int):
    sheet = service.spreadsheets()

    if group_id in SPREADSHEETS_ID:
        spreadsheetId = SPREADSHEETS_ID[group_id]
    else:
        logging.error(f"У группы {group_id} нет google-таблицы (update_google_sheet)")
        return False

    sheet.values().clear(spreadsheetId=spreadsheetId, range=f"'{SHEET_NAME}'!A:Z").execute()

    body_values = {'values': matrix}
    result = sheet.values().update(
        spreadsheetId=spreadsheetId, 
        range=f"'{SHEET_NAME}'!A1",
        valueInputOption='USER_ENTERED',
        body=body_values
    ).execute()

    num_columns = len(matrix[0]) if matrix else 0
    requests = []
    
    # Применяем формат даты для каждой колонки с датами (начиная со второй)
    for col_index in range(1, num_columns):
        requests.append({
            'repeatCell': {
                'range': {
                    'sheetId': 0,
                    'startRowIndex': 0,
                    'endRowIndex': 1,  # Только первая строка
                    'startColumnIndex': col_index,
                    'endColumnIndex': col_index + 1
                },
                'cell': {
                    'userEnteredFormat': {
                        'numberFormat': {
                            'type': 'DATE',
                            'pattern': 'MMM'  # февр. мар. апр.
                        }
                    }
                },
                'fields': 'userEnteredFormat.numberFormat'
            }
        })

    # Если есть запросы на форматирование
    if requests:
        body_requests = {'requests': requests}
        response = service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheetId,
            body=body_requests
        ).execute()

    return True if (result and response) else False

def update_statistics_table():
    now = datetime.now(TIMEZONE)
    start_of_curr_week = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0)
    start_of_previous_week = (now - timedelta(days=now.weekday() + 7)).replace(hour=0, minute=0)

    StatisticsRepository.clear()

    StatisticsRepository.insert_by_period(start_of_curr_week, now, "Текущая неделя")
    StatisticsRepository.insert_by_period(start_of_previous_week, start_of_curr_week, "Предыдущая неделя")

    beg_date = datetime.strptime("01.01.2026", "%d.%m.%Y")
    StatisticsRepository.insert_monthly_by_period(beg_date, now)

async def update_statistics_sheet(group_id):
    participants = UsersGroupsRepository.get_participants_by_group_id(group_id)
    if not participants:
        logging.info(f"Нет пользователей в группе {group_id} (update_statistics_sheet)")
        return

    periods = StatisticsRepository.get_periods(group_id)
    stats_rows = StatisticsRepository.get_group_stats(group_id)

    matrix = build_data_matrix(participants, periods, stats_rows)

    service = get_google_sheets_service()
    success = update_google_sheet(service, matrix, group_id)

    if success:
        logging.info(f"Google-таблица для группы {group_id} обновлена (update_statistics_sheet)")
    else:
        logging.error(f"Не удалось обновить Google-таблицу для группы {group_id} (update_statistics_sheet)")