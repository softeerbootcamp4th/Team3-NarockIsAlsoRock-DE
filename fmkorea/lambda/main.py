from datetime import datetime
from bs4 import BeautifulSoup, Comment
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from urllib.parse import urlparse
from tempfile import mkdtemp

import boto3
import time
import re


def save_to_s3(bucket_name, file_name, data):
    s3 = boto3.client('s3')
    csv_data = "\n".join([",".join(map(str, row.values())) for row in data])
    s3.put_object(Bucket=bucket_name, Key=file_name, Body=csv_data)


def parse_post_detail(bs: BeautifulSoup, current_url: str):
    post_id = urlparse(current_url).path.split('/')[-1]
    title = bs.find('span', class_='np_18px_span').text.strip()

    content = extract_content(bs)
    author = bs.find('a', class_='member_plate').text.strip()
    views, likes = extract_views_likes(bs)
    created_at = bs.find('span', class_='date').text.strip()

    comments = extract_comments(bs, post_id)

    return {
        "id": post_id,
        "title": title,
        "content": clean_content(content),
        "likes": likes,
        "url": current_url,
        "author": author,
        "views": views,
        "created_at": created_at,
        "updated_at": None
    }, comments


def extract_content(bs: BeautifulSoup):
    article = bs.find('div', class_='xe_content')
    for comment in article.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    content = []
    for element in article.find_all():
        if element.name in ['img', 'video']:
            content.append(element.get('src'))
        else:
            text = element.get_text(strip=True)
            if text:
                content.append(text)
    return content


def clean_content(content):
    return re.sub(r'\s+', ' ', ' \n'.join(content).replace('\r\n', ' ').replace('\n', ' ')).strip()


def extract_views_likes(bs: BeautifulSoup):
    side = bs.find("div", class_="side fr")
    views = side.find_all('b')[0].text.strip()
    likes = side.find_all('b')[1].text.strip()
    return views, likes


def extract_comments(bs: BeautifulSoup, post_id: str):
    comments = []
    for comment in bs.find_all('li', class_='fdb_itm'):
        comment_author = comment.find('a', class_='member_plate').text.strip()
        comment_content = comment.find('div', class_='xe_content').text.strip()
        comment_time = comment.find('span', class_='date').text.strip()
        comments.append({
            'post_id': post_id,
            'author': comment_author,
            'content': comment_content,
            'time': comment_time
        })
    return comments


def setup_driver():
    chrome_options = Options()
    chrome_options.binary_location = "/opt/chrome/chrome-linux64/chrome"
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-tools")
    chrome_options.add_argument("--no-zygote")
    chrome_options.add_argument("--single-process")
    chrome_options.add_argument(f"--user-data-dir={mkdtemp()}")
    chrome_options.add_argument(f"--data-path={mkdtemp()}")
    chrome_options.add_argument(f"--disk-cache-dir={mkdtemp()}")
    chrome_options.add_argument("--remote-debugging-pipe")
    chrome_options.add_argument("--verbose")
    chrome_options.add_argument("--log-path=/tmp")

    service = Service(executable_path="/opt/chrome-driver/chromedriver-linux64/chromedriver",
                      service_log_path="/tmp/chromedriver.log")
    return webdriver.Chrome(service=service, options=chrome_options)


def lambda_handler(event, context):
    keyword = event.get('keyword', '')
    page = event.get('page', 1)
    start_date = datetime.strptime(event.get('start_date', '2024-06-29'), '%Y-%m-%d')
    end_date = datetime.strptime(event.get('end_date', '2024-07-29'), '%Y-%m-%d')
    bucket_name = event.get('bucket_name')

    driver = setup_driver()
    driver.get(
        f"https://www.fmkorea.com/search.php?act=IS&is_keyword={keyword}&mid=home&where=document&page={page}&search_target=title_content")
    time.sleep(3)

    bs = BeautifulSoup(driver.page_source, 'html.parser')
    posts = bs.find("ul", attrs={"class": "searchResult"}).find_all("li")
    post_links = driver.find_elements(By.CSS_SELECTOR, "ul.searchResult li dl dt a")

    posts_parsed, comments_parsed = [], []

    for post, post_link in zip(posts, post_links):
        timestamp_str = post.find("span", attrs={"class": "time"}).text
        timestamp_datetime = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M")
        if not start_date <= timestamp_datetime <= end_date:
            continue

        post_link.send_keys(Keys.CONTROL + Keys.RETURN)
        time.sleep(2)
        driver.switch_to.window(driver.window_handles[1])
        time.sleep(2)

        post_detail, comments = parse_post_detail(BeautifulSoup(driver.page_source, 'html.parser'), driver.current_url)
        posts_parsed.append(post_detail)
        comments_parsed.extend(comments)

        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    driver.quit()

    # S3에 저장
    save_to_s3(bucket_name, f"{keyword}/posts/posts_{keyword}_page_{page}.csv", posts_parsed)
    save_to_s3(bucket_name, f"{keyword}/comments/comments_{keyword}_page_{page}.csv", comments_parsed)

    return {
        "posts": posts_parsed,
        "comments": comments_parsed
    }
