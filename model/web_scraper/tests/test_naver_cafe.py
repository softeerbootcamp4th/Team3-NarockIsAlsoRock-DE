import os
from unittest import TestCase

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from web_scraper.local.naver_cafe import divide_by_6_month, driver_naver_login
from web_scraper.src.sites.naver_cafe import comments_crawling


class Test(TestCase):
    def test_divide_by_6_month(self):
        for start_date, end_date in [["2023-01-31", "2024-08-30"], ["2021-02-01", "2024-08-30"],
                                     ["2024-08-01", "2024-08-30"]]:
            dates = divide_by_6_month(start_date, end_date)
            print(dates)

    def test_divide_by_6_month2(self):
        for start_date, end_date in [["2024-07-31", "2024-08-30"]]:
            dates = divide_by_6_month(start_date, end_date)
            print(dates)

    def test_crawl_multi_page_comment(self):
        url = "https://cafe.naver.com/ArticleRead.nhn?referrerAllArticles=true&page=1&searchBy=1&query=%5B%ED%98%84%EB%8C%80%EC%9E%90%EB%8F%99%EC%B0%A8%5D%20%EC%BD%94%EB%82%98%20EV%20%EB%A6%AC%EC%BD%9C%20%EA%B4%80%EB%A0%A8%20%EC%95%88%EB%82%B4&exclude=&include=&exact=&searchdate=all&media=0&sortBy=date&inCafeSearch=true&clubid=21771803&articleid=1165741"
        driver = webdriver.Chrome()
        # Load the .env file
        load_dotenv()
        # Access environment variables
        id_ = os.getenv('NAVER_ID')
        pw = os.getenv('NAVER_PASSWORD')

        driver = driver_naver_login(driver, id_, pw)
        driver.get(url)
        WebDriverWait(driver, 5).until(
            expected_conditions.frame_to_be_available_and_switch_to_it((By.ID, "cafe_main")))
        comments = comments_crawling(driver, 521228)
        self.assertTrue(len(comments)>300)