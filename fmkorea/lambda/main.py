from datetime import datetime
from bs4 import BeautifulSoup, Comment
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from urllib.parse import urlparse
import time
import re
import requests
from tempfile import mkdtemp


def parse_post_detail(bs: BeautifulSoup, current_url: str):
    # URL 파싱
    parsed_url = urlparse(current_url)
    # 경로에서 게시물 ID 추출
    post_id = parsed_url.path.split('/')[-1]
    title = bs.find('span', class_='np_18px_span').text.strip()
    content = []

    def replace_multiple_spaces(text):
        return re.sub(r'\s+', ' ', text).strip()

    article = bs.find('div', class_='xe_content')
    # 주석 제거
    for comment in article.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()
    # article 태그 직접 자식 노드들의 텍스트 처리
    for child in article.children:
        if isinstance(child, str) and child.strip():
            content.append(child.strip())
    for element in article.find_all():
        # img 또는 video 태그가 포함된 경우
        if element.name in ['img', 'video']:
            # img 또는 video 태그의 src 속성 추출
            src = element.get('src')
            content.append(src)
        else:
            text = element.get_text(strip=True)
            content.append(text)

    author = bs.find('a', class_='member_plate').text.strip()
    side = bs.find("div", attrs={"class": "side fr"})
    views = side.find_next('b').text.strip()
    likes = side.find_next('b').text.strip()
    created_at = bs.find('span', class_='date').text.strip()

    comments = []
    comment_elements = bs.find_all('li', class_='fdb_itm')
    for comment in comment_elements:
        comment_author = comment.find('a', class_='member_plate').text.strip()
        comment_content = comment.find('div', class_='xe_content').text.strip()
        comment_time = comment.find('span', class_='date').text.strip()
        comments.append({
            'post_id': post_id,
            'author': comment_author,
            'content': comment_content,
            'time': comment_time
        })
    post = {
        "id": post_id,
        "title": title,
        "content": replace_multiple_spaces(' \n'.join(content).replace('\r\n', ' ').replace('\n', ' ')),
        "likes": likes,
        "url": current_url,
        "author": author,
        "views": views,
        "created_at": created_at,
        "updated_at": None
    }
    return post, comments


def lambda_handler(event, context):
    keyword = '홍명보'
    page = 96
    start_date = datetime(2024, 6, 29)
    end_date = datetime(2024, 7, 29)

    # Chrome 옵션 설정
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
    service = Service(
        executable_path="/opt/chrome-driver/chromedriver-linux64/chromedriver",
        service_log_path="/tmp/chromedriver.log"
    )
    driver = webdriver.Chrome(
        service=service,
        options=chrome_options
    )
    driver.get(
        url=f"https://www.fmkorea.com/search.php?act=IS&is_keyword={keyword}&mid=home&where=document&page={page}&search_target=title"
    )
    time.sleep(3)
    bs = BeautifulSoup(driver.page_source, 'html.parser')
    posts = bs.find("ul", attrs={"class": "searchResult"}).find_all("li")
    # 게시물 목록에서 모든 게시물 제목 링크를 찾습니다.
    post_links = driver.find_elements(By.CSS_SELECTOR, "ul.searchResult li dl dt a")
    posts_parsed = []
    comments_parsed = []
    post_link = post_links[0]
    # for post_link in post_links:
    #     url = post_link.get_attribute("href")
    #     post, comments = parse_post_detail(BeautifulSoup(requests.get(url).content, 'html.parser'),
    #                                        url)
    #     posts_parsed.append(post)
    #     comments_parsed.extend(comments)
    #     time.sleep(5)
    url = post_link.get_attribute("href")
    response = requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        "accept":
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "cache-control": "no-cache"
    })
    print(response.text)
    post, comments = parse_post_detail(BeautifulSoup(response.text, 'html.parser'), url)
    posts_parsed.append(post)
    comments_parsed.extend(comments)
    print(post)
    return {
        "posts": posts_parsed,
        "comments": comments_parsed
    }
