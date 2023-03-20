import sys

import requests
import json
import csv


def import_to():
    url = 'http://localhost:8000/apis/import/'
    data = {'apps': apps}
    headers = {'Content-type': 'application/json'}

    response = requests.post(url, data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        result = response.text
        print(result)
    else:
        print('Request failed with status code', response.status_code)


with open('data.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    i = 0
    apps = []
    for row in reader:
        i = i + 1
        if i > 1:
            apps.append(row)
        print(f"第{i}行：{row}")

print(len(sys.argv))

import_to()
