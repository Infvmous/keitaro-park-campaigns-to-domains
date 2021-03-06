import os
import sys
import json
import csv

import requests

from pprint import pprint


def get_api_key():
    return os.getenv('API_KEY')


def get_keitaro_host():
    return os.getenv('HOST')


def build_request_url(endpoint):
    """ Формирует URL для запроса к апи """
    host = get_keitaro_host()
    if host.endswith('/'):
        host = host + endpoint
    else:
        host = f'{host}/{endpoint}'
    return host


def send_request(method, endpoint, payload=None):
    """ Отправляет http запрос с методом method
    на api endpoint, с телом запроса payload """
    return requests.request(
        method, build_request_url(endpoint),
        headers = {'Api-Key': get_api_key()},
        data=json.dumps(payload))


def clone_campaign(cid):
    """ Клонирует keitaro кампанию по ее
    идентификатору campaign_id """
    return send_request('POST', f'admin_api/v1/campaigns/{cid}/clone')


def export_from_csv(filename, campaigns=[]):
    with open(f'{filename}.csv', newline='') as f:
        for row in csv.reader(f):
            campaigns.append(row)
    return campaigns


def update_campaign(cid, payload):
    return send_request('PUT',
        f'admin_api/v1/campaigns/{cid}', payload)


def create_domain(payload):
    return send_request('POST',
        f'admin_api/v1/domains', payload)


def get_all_domains():
    return send_request('GET', f'admin_api/v1/domains')


def update_domains_in_campaigns(filename):
    data = export_from_csv(filename)[1:]
    for row in data:
        domain_id = int(row[0])
        campaign_id = row[2]
        updated_campaign = update_campaign(campaign_id, {'domain_id': domain_id})
        print(updated_campaign)
        

def main(filename):
    choice = input('Enter, чтобы припарковать домены\n1, чтобы обновить домены в кампаниях\n')
    if choice == '1':
        update_domains_in_campaigns(filename)
    else:
        campaigns = export_from_csv(filename)[1:]
        for campaign in campaigns:
            campaign_name = campaign[0]
            domain = campaign[1]
            template_id = campaign[2]
            group_id = campaign[3]

            # Клонирую кампании и меняю имена
            cloned_campaign = clone_campaign(template_id).json()
            cloned_campaign_id = cloned_campaign[0]['id']
            
            cloned_campaign = update_campaign(cloned_campaign_id,
                {'name': campaign_name, 'group_id': group_id})
            if cloned_campaign.status_code == 200:
                print(f'Кампания {campaign_name} успешно создана!')
            else:
                print(cloned_campaign.json())

            # Создаю и Паркую кампании к доменам
            domain = create_domain({
                'name': domain,
                'is_ssl': True,
                'default_campaign_id': cloned_campaign_id,
                'catch_not_found': True
            }).json()
            # print(domain.json())

            # Добавляю домен к кампании
            campaign_with_updated_domain = update_campaign(cloned_campaign_id,
                {'domain_id': int(domain[0]['id'])}).json()
            pprint(campaign_with_updated_domain)
    

if __name__ == "__main__":
    try:
        main(sys.argv[1])
    except IndexError:
        print('Не указано имя импортируемого файла')