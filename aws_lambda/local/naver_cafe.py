import csv
import json
import multiprocessing
import os
import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

from aws_lambda.local.utils import saveCookies, save_csv, setup_headless_driver
from aws_lambda.sites import naver_cafe


def driver_naver_login(driver, id, pw):
    login_url = 'https://nid.naver.com/nidlogin.login'
    driver.get(login_url)
    time.sleep(2)
    driver.execute_script("document.getElementsByName('id')[0].value=\'" + id + "\'")
    driver.execute_script("document.getElementsByName('pw')[0].value=\'" + pw + "\'")
    driver.find_element(by=By.XPATH, value='//*[@id="log.login"]').click()
    time.sleep(1)
    return driver


def divide_by_6_month(start_date="2020-01-01", end_date="2024-06-30"):
    # 날짜 범위 생성
    date_range = pd.date_range(start=start_date, end=end_date, freq='6ME')
    # 시작과 끝 날짜를 튜플로 묶기
    date_tuples = [(date_range[i].strftime('%Y-%m-%d'), date_range[i + 1].strftime('%Y-%m-%d')) for i in
                   range(len(date_range) - 1)]
    date_tuples.insert(0, (start_date, date_tuples[0][0]))
    date_tuples.append((date_tuples[-1][1], end_date))
    return date_tuples

def worker(payload):
    for i in range(0, 10):
        try:
            payload['page'] = i + payload['page']
            print(f"{payload} start")
            results = naver_cafe.main(payload, {}, setup_headless_driver())
            if len(results['posts']) == 0:
                break
            keyword = payload["keyword"]
            site = payload["site"]
            page = payload["page"]
            start = payload["start_date"]
            save_csv(results, f"{keyword}/{site}/{start}", page)

        except Exception as e:
            print(e)
        print(f"{payload} failed")
if __name__ == '__main__':
    driver = webdriver.Chrome()
    # info for naver login
    id_ = 'hmg_de'
    pw = 'hmg_de_hmg_de1'

    driver = driver_naver_login(driver, id_, pw)
    saveCookies(driver)
    driver.quit()

    if 'cookies.json' in os.listdir():
        # Load cookies to a vaiable from a file
        with open('cookies.json', 'r') as file:
            cookies = json.load(file)


    # start_date, end_date = "2023-01-31", "2024-08-30"
    # for start, end in divide_by_6_month(start_date=start_date, end_date=end_date):
    #     payloads = [
    #         {
    #             "site": "naver_cafe",
    #             "keyword": "코나 화재",
    #             "start_date": start,
    #             "end_date": end,
    #             "cookies": cookies,
    #         }
    #     ]
    #
    #     for payload in payloads:
    #         for i in range(1, 42):
    #             payload['page'] = i
    #             results = naver_cafe.main(payload, {}, webdriver.Chrome())
    #             if len(results['posts']) == 0:
    #                 break
    #             keyword = payload["keyword"]
    #             site = payload["site"]
    #             page = payload["page"]
    #             save_csv(results, f"{keyword}/{site}/{start}", page)
    #
    #
    # #==================================================================================================================
    # start_date, end_date = "2021-02-01", "2024-08-30"
    # for start, end in divide_by_6_month(start_date=start_date, end_date=end_date):
    #     payloads = [
    #         {
    #             "site": "naver_cafe",
    #             "keyword": "아이오닉 iccu",
    #             "start_date": start,
    #             "end_date": end,
    #             "cookies": cookies,
    #         }
    #     ]
    #
    #     for payload in payloads:
    #         for i in range(1, 42):
    #             payload['page'] = i
    #             results = naver_cafe.main(payload, {}, webdriver.Chrome())
    #             if len(results['posts']) == 0:
    #                 break
    #             keyword = payload["keyword"]
    #             site = payload["site"]
    #             page = payload["page"]
    #             save_csv(results, f"{keyword}/{site}/{start}", page)
    #
    # #==================================================================================================================
    # start_date, end_date = "2024-07-31", "2024-08-30"
    # payloads = [
    #     {
    #         "site": "naver_cafe",
    #         "keyword": "아이오닉 누수",
    #         "start_date": start_date,
    #         "end_date": end_date,
    #         "cookies": cookies,
    #     }
    # ]
    #
    # for payload in payloads:
    #     for i in range(1, 42):
    #         payload['page'] = i
    #         results = naver_cafe.main(payload, {}, setup_headless_driver())
    #         if len(results['posts']) == 0:
    #             break
    #         keyword = payload["keyword"]
    #         site = payload["site"]
    #         page = payload["page"]
    #         start = payload["start_date"]
    #         save_csv(results, f"{keyword}/{site}/{start}", page)

    # ==================================================================================================================
    start_date, end_date = "2024-08-01", "2024-08-30"
    payloads = [
        {
            "site": "naver_cafe",
            "keyword": "벤츠 화재",
            "start_date": start_date,
            "end_date": end_date,
            "cookies": cookies,
        }
    ]

    for payload in payloads:
        for i in range(12, 42):
            payload['page'] = i
            results = naver_cafe.main(payload, {}, setup_headless_driver())
            if len(results['posts']) == 0:
                break
            keyword = payload["keyword"]
            site = payload["site"]
            page = payload["page"]
            start = payload["start_date"]
            save_csv(results, f"{keyword}/{site}/{start}", page)




