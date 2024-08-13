import re
import time
import urllib.parse
from bs4 import BeautifulSoup as bs
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from datetime import datetime
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


def main(event, context, driver: WebDriver):
    # from lambda event
    keyword = event.get('keyword', '')
    page_num = event.get('page', '')
    start_date_str = event.get('start_date', '2024-06-29')
    end_date_str = event.get('end_date', '2024-07-29')
    cookies = event.get('cookies', [])
    timestamp_datetime_start = datetime.strptime(start_date_str, '%Y-%m-%d')
    timestamp_datetime_end = datetime.strptime(end_date_str, '%Y-%m-%d')

    driver.get("https://www.naver.com/")
    for cookie in cookies:
        driver.add_cookie(cookie)
    search_keyword = urllib.parse.quote(keyword.encode('euc-kr'))
    board_url = f'https://cafe.naver.com/allfm01?iframe_url=/ArticleSearchList.nhn%3Fsearch.clubid=21771803%26search.media=0%26search.searchdate={start_date_str}{end_date_str}%26search.exact=%26search.include=%26userDisplay=50%26search.exclude=%26search.option=0%26search.sortBy=date%26search.searchBy=0%26search.includeAll=%26search.query={search_keyword}%26search.viewtype=title%26search.page={page_num}'
    driver.get(board_url)
    WebDriverWait(driver, 2).until(
        expected_conditions.frame_to_be_available_and_switch_to_it((By.ID, "cafe_main")))
    try:
        WebDriverWait(driver, 5).until(
            expected_conditions.element_to_be_clickable((By.CLASS_NAME, "article")))
    except TimeoutException:
        print(f"Nothing to parse page={page_num}")
        return {
            "posts": [],
            "comments": []
        }

    soup = bs(driver.page_source, 'html.parser')
    article = soup.select('div.inner_list a.article')
    titles = [link.text.strip() for link in article]
    links = [link['href'] for link in article]

    posts_parsed, comments_parsed = [], []
    for title, link in zip(titles, links):
        post_url = 'https://cafe.naver.com' + link
        driver.get(post_url)
        WebDriverWait(driver, 5).until(
            expected_conditions.frame_to_be_available_and_switch_to_it((By.ID, "cafe_main")))
        # 해당 페이지의 HTML 소스 가져오기, BeautifulSoup으로 HTML 파싱
        posts_data, comments_data = post_crawling(driver, title, post_url, timestamp_datetime_start,
                                                  timestamp_datetime_end)
        if posts_data != None:
            posts_parsed.append(posts_data)
        comments_parsed.extend(comments_data)
    driver.quit()
    return {
        "posts": posts_parsed,
        "comments": comments_parsed
    }


def comments_crawling(driver, post_id):  # 게시물 하나의 댓글들에 대한 크롤링
    try:
        WebDriverWait(driver, 2).until(
            expected_conditions.presence_of_element_located((By.CLASS_NAME, "comment_box")))
    except TimeoutException:  # 댓글이 없으면 return
        return []
    comment_box = driver.find_elements(By.CLASS_NAME, 'comment_box')
    comments = parse_comment_box(comment_box, post_id)
    try:# 댓글에 페이지가 있는지 확인하고, 파싱
        pages = driver.find_element(By.CLASS_NAME, 'CommentBox').find_element(By.CLASS_NAME, 'ArticlePaginate')
        buttons = pages.find_elements(By.TAG_NAME, 'button')
        for index, button in enumerate(buttons[1:]):
            button.click()
            WebDriverWait(driver, 5).until(
                expected_conditions.element_to_be_clickable(buttons[index-1])
            )
            # 댓글의 다른 페이지 클릭후 변경될 때까지 대기
            WebDriverWait(driver, 10).until(expected_conditions.staleness_of(comment_box[0]))
            comment_box = driver.find_elements(By.CLASS_NAME, 'comment_box')
            comments.extend(parse_comment_box(comment_box, post_id))
    except NoSuchElementException:# 댓글에 페이지가 없는 경우
        pass
    return comments


def parse_comment_box(cmt_elem, post_id):
    comments = []
    for elem in cmt_elem:
        try:  # 댓글에 내용이 없는 경우, 다음 댓글로 이동 (네이버 카페 클린봇)
            cmt_content = elem.find_element(By.CLASS_NAME, 'text_comment').get_attribute('textContent').strip()
            cmt_author = elem.find_element(By.CLASS_NAME, 'comment_nickname').get_attribute('textContent').strip()
            cmt_created_at_str = elem.find_element(By.CLASS_NAME, 'comment_info_date').get_attribute(
                'textContent').strip()
            cmt_created_at = datetime.strptime(cmt_created_at_str, "%Y.%m.%d. %H:%M")
        except:
            continue
        comments_data = {"post_id": post_id,
                         "cmt_content": clean_content(cmt_content),
                         "cmt_author": cmt_author,
                         "cmt_created_at": cmt_created_at}
        comments.append(comments_data)
    return comments


def post_crawling(driver, title, url, datetime_start, datetime_end):  # 게시물 하나에 대한 크롤링
    WebDriverWait(driver, 5).until(expected_conditions.any_of(
        expected_conditions.presence_of_element_located((By.CLASS_NAME, 'date')),
        expected_conditions.presence_of_element_located(
            (By.CSS_SELECTOR, "#app > div > div > div > div.guide_btns > a:nth-child(2)"))
    ))
    page_source = driver.page_source
    soup_article = bs(page_source, 'html.parser')

    try:
        post_created_at_str = soup_article.find('div', class_='article_info').find('span', class_='date').text.strip()
        post_created_at = datetime.strptime(post_created_at_str, "%Y.%m.%d. %H:%M")
        assert in_range(post_created_at, datetime_start, datetime_end)
    except:
        # 계정의 등급 문제 등으로 게시물을 읽을 수 없는 경우 / 설정한 날짜 범위를 벗어나는 경우
        return None, []

    post_id = int(
        soup_article.find('div', class_='text_area').find(class_='naver-splugin').get('data-url').split('/')[-1])
    post_title = title
    content_elem = driver.find_elements(By.CLASS_NAME, 'se-fs-')
    post_content = ""
    for element in content_elem:
        post_content += element.text
    post_like = driver.find_element(By.CLASS_NAME, 'u_cnt._count').text
    post_url = url
    post_author = soup_article.find('div', class_='article_writer').find('strong', class_='user').text.strip()
    post_view = driver.find_element(By.CLASS_NAME, 'article_info').find_element(By.CLASS_NAME, 'count').text.replace(
        "조회 ", '')

    post_parsed = {
        'id': post_id,
        'title': clean_content(post_title),
        'content': clean_content(post_content),
        'likes': post_like,
        'url': post_url,
        'author': post_author,
        'views': post_view,
        'created_at': post_created_at,
        'updated_at': None,
    }

    comments_parsed = comments_crawling(driver, post_id)
    return post_parsed, comments_parsed


def in_range(datetime, datetime_start, datetime_end):
    return datetime_start <= datetime <= datetime_end


def clean_content(content):
    return re.sub(r'\s+', ' ', content.replace('\r\n', ' ').replace('\n', ' ')).strip()
