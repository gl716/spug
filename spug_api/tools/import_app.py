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
    old_apps = []
    apps = []
    for row in reader:
        i = i + 1
        if i > 1:
            if len(sys.argv) > 1:
                if sys.argv[1] in row[0]:
                    old_apps.append(row)
            else:
                old_apps.append(row)

    for i in range(len(old_apps)):
        current = old_apps[i]
        if not current[1]:
            current[1] = current[0].replace("-", "_")
        if "multi" in old_apps[i][2]:
            for hostname in current[3].split(",", maxsplit=3):
                cp_current = current[:]
                cp_current[3] = hostname
                if "host26" in hostname:
                    cp_current[2] = "dev"
                elif "host27" in hostname:
                    cp_current[2] = "test"
                elif "host28" in hostname:
                    cp_current[2] = "uat"
                else:
                    cp_current[2] = "prod"
                apps.append(cp_current)
        else:
            apps.append(current)
    for i in range(len(apps)):
        print(f"第{i}行：{apps[i]}")

import_to()
