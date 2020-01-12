import datetime as dt
import os
import time as t
from datetime import date
from pathlib import Path
import json
import matplotlib.pyplot as plt
import pandas as pd
import requests
import pyro_func_module as pyt


def check_for_existing_querry_in_db(query_begin, query_finish, list_of_dates):
    """This function only checks if new query dates lie """
    for item in list_of_dates:
        if query_begin >= item[0] and query_finish <= item[1]:
            return True


def pyro_summ(set):
    """Training version of summ function with rounding the float point to 7 digit"""
    local_summ = 0
    for item in set:
        local_summ += set[item]
    return (round(local_summ, 7))


def pyro_max(set):
    '''Training version of max function with rounding the float point to 7 digit'''
    maxi = 0
    for item in set:
        if float(set[item]) > maxi:
            maxi = float(set[item])
    return maxi


def pyro_min(set):
    '''Training version of min function with rounding the float point to 7 digit'''
    mini = float(set[date1_req])
    for item in set:
        if float(set[item]) < mini:
            mini = float(set[item])
    return mini


def pyro_average(set):
    '''Training version of average function with rounding the float point to 7 digit'''
    return round(pyro_summ(set) / len(set), 6)


def pyro_mediana(set: object) -> object:
    '''Training version of mediana function with rounding the float point to 7 digit'''
    data = sorted(set.values())
    if (len(set) % 2) == 0:
        temp_median = (data[int(len(data) // 2)] + data[int((len(data) // 2) - 1)]) / 2
    else:
        temp_median = data[int(len(data) // 2)]
    return round(temp_median, 6)


def pyro_sqrt_deviation(set):
    '''Training version of square root deviation function with rounding the float point to 7 digit'''
    temp_accum = 0
    for item in set:
        temp_accum += (set[item] - pyro_average(set)) ** 2
    return round((temp_accum / len(set)) ** 0.5, 6)


PROJECT = "ForEx_UA"
in_web = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"
try:
    Path(PROJECT).mkdir()
except OSError as error:
    pass
# currency_req = input("Currency to check the rate (3 char code): ").upper()
currency_req = "EUR"
# date1_req = input("First date to get the EX rate (YYYYMMDD format): ")
# date2_req = input("Second date YYYYMMDD: ")

date1_req = "20191020"
date2_req = "20191030"
storage = Path(PROJECT) / Path(currency_req)
try:
    storage.mkdir()
except OSError as error:
    pass
os.chdir(storage)
filename = f'{date1_req}_{date2_req}'
directory_content = []
for item in Path.iterdir(Path.cwd()):
    if item.suffix == '.json':
        directory_content.append(item.stem.split("_"))

for i in range(len(directory_content)):
    for j in range(len(directory_content[i])):
        directory_content[i][j] = t.strptime(directory_content[i][j], "%Y%m%d")
        directory_content[i][j] = dt.date(*directory_content[i][j][0:3])

begin = t.strptime(date1_req, "%Y%m%d")
finish = t.strptime(date2_req, "%Y%m%d")
begin: date = dt.date(*begin[0:3])
finish = dt.date(*finish[0:3])

if check_for_existing_querry_in_db(begin, finish, directory_content):
    with open(filename + '.json', "r") as read_file:
        collection = json.load(read_file)
    print(f'{currency_req} rate on {date1_req} was {collection[date1_req]}')
    print(f'{currency_req} rate on {date2_req} was {collection[date2_req]}')
else:
    param_dict1 = {"date": date1_req, "valcode": currency_req}
    param_dict2 = {"date": date2_req, "valcode": currency_req}
    collection = {}
    delta = finish - begin
    for i in range(delta.days + 1):
        date_req = (begin + dt.timedelta(days=i)).strftime("%Y%m%d")
        query_dict = {"valcode": currency_req, "date": date_req}
        collection[date_req] = round(float(requests.get(in_web, params=query_dict).json()[0]['rate']), 6)

        print(requests.get(in_web, params=param_dict1).json()[0]['exchangedate'], ' - ',
              requests.get(in_web, params=param_dict1).json()[0]['rate'])
        print(requests.get(in_web, params=param_dict2).json()[0]['exchangedate'], ' - ',
              requests.get(in_web, params=param_dict2).json()[0]['rate'])

print(pyro_summ(collection), pyro_max(collection), pyro_min(collection), pyro_mediana(collection),
      pyro_average(collection), pyro_sqrt_deviation(collection))
print(pyt.pyro_summ(collection))
ts_df = pd.DataFrame.from_dict(collection, orient='index')

with open(filename + '.txt', 'w') as file_db:
    file_db.write(str(collection))

with open(filename + '.json', 'w') as file_js:
    json.dump(collection, file_js)

ts_df.plot()
plt.title(f'ForEx Rates for {currency_req} during {date1_req}-{date2_req}')
plt.grid(True, linestyle='--')
plt.ylabel(currency_req)
plt.xlabel("Time Period")
# plt.show()
