#!/usr/bin/python3.7
# -*- coding: utf-8
version = 'UISP_Backup_Creator Version 1.4'

import requests
import datetime
import urllib3
urllib3.disable_warnings()
api_token = # Ваш токен api
uisp_ip = # Ваш IP сервера UISP


def dev_id_list():
    '''
    Формируем список всех устройств подключенных к UISP.
    '''
    response = requests.get(
        'https://{uisp_ip}/nms/api/v2.1/devices',
        headers={'accept': 'application/json',
                 'content-type': 'application/json',
                 'x-auth-token': f"{api_token}"},
        verify=False
    )
    result = response.json()
    return result


def create_new_backup(dev_id, dev_name, dev_status):
    '''
    Создаем бекап конфигурации устройства если оно активно.
    '''
    if dev_status == 'active':
        print(f"{dev_name} Create new backup...")
        requests.post(
            f"https://{uisp_ip}/nms/api/v2.1/devices/{dev_id}/backups",
            headers={'accept': 'application/json',
                     'content-type': 'application/json',
                     'x-auth-token': f"{api_token}"},
            verify=False
        )
    else:
        print(f"{dev_name} Disconnected...")


def backup_list(dev_id):
    '''
    Формируем список бекапов конкретного устройства.
    '''
    response = requests.get(
        f"https://{uisp_ip}/nms/api/v2.1/devices/{dev_id}/backups",
        headers={'accept': 'application/json',
                'content-type': 'application/json',
                'x-auth-token': f"{api_token}"},
        verify=False
    )
    result = response.json()
    return result


def date_sorted(date_mas):
    '''
    Формируем сокрированный список бекапов для последующего удаления.
    '''
    dates = [datetime.datetime.strptime(ts, "%Y-%m-%d") for ts in date_mas]
    dates.sort()
    sorted_dates = [datetime.datetime.strftime(ts, "%Y-%m-%d") for ts in dates]
    sorted_dates.reverse()

    final_dates = []
    count = 0
    for date in sorted_dates:
        if count < 5:
            count += 1
        else:
            final_dates.append(date)
            count += 1

    return final_dates


def del_old_backup(dev_id, dev_name):
    '''
    Запускаем процедуру удаления старых бекапов если их общее количество больше пяти. 
    '''
    try:
        backup = backup_list(dev_id)
        if len(backup) > 5:
            print(f"{dev_name} Backups = {len(backup)}")
            date_mas = []
            for row in backup:
                date = (row['timestamp'].split('T')[0])
                date_mas.append(date)

            for row in backup:
                if row['timestamp'].split('T')[0] in date_sorted(date_mas):
                    print(f"Delete {row['filename']}")
                    backup_id = row['id']
                    requests.delete(
                        f"https://{uisp_ip}/nms/api/v2.1/devices/{dev_id}/backups/{backup_id}", 
                        headers={'accept': 'application/json',
                                 'content-type': 'application/json',
                                 'x-auth-token': f"{api_token}"},
                        verify=False
                    )
        else:
            print(f"{dev_name} Backups = {len(backup)}")
    except:
        print('Произошла ошибка при выполнении операции!')


print("Запускаю службу резервного копирования...")
for dev_row in dev_id_list():
    try:
        create_new_backup(dev_row['identification']['id'],
                          dev_row['identification']['site']['name'],
                          dev_row['identification']['site']['status'])
    except:
        print('Что-то пошло не так...')

    try:
        del_old_backup(dev_row['identification']['id'],
                       dev_row['identification']['site']['name'])
    except:
        print('Что-то пошло не так...')
