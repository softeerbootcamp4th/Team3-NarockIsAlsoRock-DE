import os
import time
from datetime import datetime, timedelta
from unittest import TestCase
from urllib.parse import urlparse, parse_qs

from pandas import read_html
from selenium import webdriver

from extract.sites.bobae import parse_post, click_latest_post, get_post_id, should_stop


class Test(TestCase):

    def setup_headless_driver(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument("--single-process")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko")
        chrome_options.add_argument("disable-gpu")
        driver = webdriver.Chrome(options=chrome_options)
        return driver

    def setUp(self):
        self.post = {'id': '2323683', 'title': '1년,2년,3년전 탔던 차들 한번 나열해봤습니다..[21]',
                     'content': "문득 1년전2년전3년전에는 이맘때 무슨 차를 타고 있었지?..생각이 들어서 한번 찾아봤습니다일단 현재 24년8월에는 K9 5.0 퀀텀을 타고 있고.. 작년 23년8월에는 W222 후기형 S400d를 타고 있었습니다.. 2년전 22년8월에는 W222 전기형 S350d를... 3년전 21년8월과 4년전 20년8월에는 제네시스 EQ900을..ㅡ.ㅡ;이렇게 보니 진짜 징하게도 바꿔가면서 탔네요 하하..그나마 EQ900을 좀 길게 탔네요..내년 8월에는 지금 타는 K9을 그대로 타고 있기를 희망해봅니다 ..'=';;",
                     'likes': '45', 'url': 'https://www.bobaedream.co.kr/view?code=national&No=2323683&bm=1',
                     'author': '프레기온', 'views': '4,018', 'created_at': '2024.08.24 13:07',
                     'updated_at': '2024.08.24 13:08'}
        self.driver = self.setup_headless_driver()
        self.post_url = "https://www.bobaedream.co.kr/view?code=national&No=2323683&bm=1"
        self.board_url = "https://www.bobaedream.co.kr/list?code=national"

    def test_parse_post(self):
        self.driver.get(self.post_url)
        post = parse_post(self.driver)
        self.assertEqual(post['id'], self.post['id'], "The dictionaries do not have the same keys and values")

    def test_get_post_id(self):
        id = get_post_id(self.post_url)
        self.assertEqual(id, self.post['id'], "The post id does not match")

    def test_should_stop_true(self):
        self.assertTrue(should_stop(datetime.now() - timedelta(hours=5), datetime.now(), 3))

    def test_should_stop_fail(self):
        self.assertFalse(should_stop(datetime.now() - timedelta(hours=1), datetime.now(), 3))

    def test_should_stop_edge(self):
        self.assertFalse(should_stop(datetime.now(), datetime.now() - timedelta(hours=3), 3))
