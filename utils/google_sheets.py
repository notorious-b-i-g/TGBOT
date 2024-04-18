import gspread
from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials


def authenticate_google_docs():
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    creds = Credentials.from_service_account_file(
        '.json',
        scopes=scopes
    )
    client = gspread.authorize(creds)
    return client


def get_time_range(callback_data):
    today = datetime.now()
    start_date = datetime.now()
    if callback_data == 'month_one':
        start_date = today - timedelta(days=30)
    elif callback_data == 'month_two':
        start_date = today - timedelta(days=60)
    elif callback_data == 'month_three':
        start_date = today - timedelta(days=90)
    return start_date.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')


def input_time_range(time):
    today = datetime.now()
    start_date = today - timedelta(time)
    return start_date.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
