import csv
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver


def saveCookies(driver: WebDriver):
    # Get and store cookies after login
    cookies = driver.get_cookies()

    # Store cookies in a file
    with open('cookies.json', 'w') as file:
        json.dump(cookies, file)
    print('New Cookies saved successfully')


def loadCookies(driver: WebDriver):
    # Check if cookies file exists
    if 'cookies.json' in os.listdir():

        # Load cookies to a vaiable from a file
        with open('cookies.json', 'r') as file:
            cookies = json.load(file)

        # Set stored cookies to maintain the session
        for cookie in cookies:
            driver.add_cookie(cookie)
    else:
        print('No cookies file found')

    driver.refresh()  # Refresh Browser after login
    return driver


def setup_headless_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--single-process")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko")
    chrome_options.add_argument("disable-gpu")
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def save_csv(result, directory, page):
    for key, value in result.items():
        path = f"./{directory}/{key}"
        # 디렉토리가 없으면 생성
        if not os.path.exists(path):
            os.makedirs(path)
        # CSV 파일로 저장
        with open(f"{path}/{page}.csv", mode='w', newline='', encoding='utf-8') as comments_file:
            writer = csv.DictWriter(comments_file, fieldnames=value[0].keys())  # 헤더를 위해 필드명 설정
            writer.writeheader()
            for row in value:
                writer.writerow(row)
