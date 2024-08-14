import csv
import json
import multiprocessing
import os
import time
import traceback

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
    if len(date_tuples) == 0:
        return [(start_date, end_date)]
    if start_date != date_tuples[0][0]:
        date_tuples.insert(0, (start_date, date_tuples[0][0]))
    if date_tuples[-1][1] != end_date:
        date_tuples.append((date_tuples[-1][1], end_date))
    return date_tuples


def scrap(start_date, end_date, keyword, cookies):
    for start, end in divide_by_6_month(start_date=start_date, end_date=end_date):
        payload = {
            "site": "naver_cafe",
            "keyword": keyword,
            "start_date": start,
            "end_date": end,
            "cookies": cookies,
        }
        for i in range(1, 42):
            try:
                payload['page'] = i
                print(f"start site={payload['site']}, keyword={payload['keyword']}, page={payload['page']}")
                results = naver_cafe.main(payload, {}, setup_headless_driver())
                if len(results['posts']) == 0:
                    print(f"scrap done. site={payload['site']}, keyword={keyword}, page={i}")
                    break
                keyword = payload["keyword"]
                site = payload["site"]
                page = payload["page"]
                save_csv(results, f"{keyword}/{site}/{start}", page)
            except Exception as e:
                print(f"error parsing site={payload['site']}, page={payload['page']}")
                traceback.print_exc()  # 전체 스택 트레이스를 출력


if __name__ == '__main__':
    driver = webdriver.Chrome()
    id_ = 'hmg_de'
    pw = 'hmg_de_hmg_de1'

    driver = driver_naver_login(driver, id_, pw)
    saveCookies(driver)
    driver.quit()

    if 'cookies.json' in os.listdir():
        # Load cookies to a vaiable from a file
        with open('cookies.json', 'r') as file:
            cookies = json.load(file)
    processes = []

    for i in [
        ("2024-01-31", "2024-08-30", "코나 화재", cookies),
            # ("2021-02-01", "2024-08-30", "아이오닉 iccu", cookies),
            # ("2024-07-31", "2024-08-30", "아이오닉 누수", cookies),
            # ("2024-08-01", "2024-08-30", "벤츠 화재", cookies)
    ]:
        p = multiprocessing.Process(target=scrap, args=(i[0],i[1],i[2],i[3]))
        time.sleep(5)
        processes.append(p)
        p.start()

    for p in processes:
        p.join()  # 모든 프로세스가 끝날 때까지 기다림
