from datetime import datetime
from aiogoogle import Aiogoogle

from app.core.config import settings

FORMAT = "%Y/%m/%d %H:%M:%S"
now_date_time = datetime.now().strftime(FORMAT)
SPREADSHEET_BODY = {
    'properties': {'title': f'Отчет на {now_date_time}',
                   'locale': 'ru_RU'},
    'sheets': [{'properties': {'sheetType': 'GRID',
                               'sheetId': 0,
                               'title': 'Лист1',
                               'gridProperties': {'rowCount': 100,
                                                  'columnCount': 11}}}]}
TABLE_VALUES = [
    ['Отчет от', datetime.now().strftime(FORMAT)],
    ['Топ проектов по скорости закрытия'],
    ['Название проекта', 'Время сбора', 'Описание']]


async def spreadsheets_create(wrapper_services: Aiogoogle) -> str:
    # now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    spreadsheet_body = SPREADSHEET_BODY
    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body))
    return response['spreadsheetId']


async def set_user_permissions(
        spreadsheet_id: str, wrapper_services: Aiogoogle) -> None:
    permissions_body = {
        'type': 'user', 'role': 'writer', 'emailAddress': settings.email}
    service = await wrapper_services.discover('drive', 'v3')
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheet_id, json=permissions_body, fields="id"))


async def spreadsheets_update_value(
        spreadsheet_id: str, projects: list,
        wrapper_services: Aiogoogle) -> None:
    service = await wrapper_services.discover('sheets', 'v4')
    table_values = TABLE_VALUES
    for res in projects:
        new_row = [res['name'], str(res['delta']), res['description']]
        table_values.append(new_row)
    update_body = {'majorDimension': 'ROWS', 'values': table_values}
    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range='A1:E30',
            valueInputOption='USER_ENTERED',
            json=update_body))
