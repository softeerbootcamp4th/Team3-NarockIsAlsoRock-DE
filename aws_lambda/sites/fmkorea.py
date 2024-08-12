from datetime import datetime
from bs4 import BeautifulSoup, Comment
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from urllib.parse import urlparse
import re


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
            continue
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
            'cmt_author': comment_author,
            'cmt_content': comment_content,
            'cmt_created_at': comment_time
        })
    return comments

def main(event, context, driver: WebDriver):
    keyword = event.get('keyword', '')
    page = event.get('page', 1)
    start_date = datetime.strptime(event.get('start_date', '2024-06-29'), '%Y-%m-%d')
    end_date = datetime.strptime(event.get('end_date', '2024-07-29'), '%Y-%m-%d')
    driver.implicitly_wait(2)
    driver.get(
        f"https://www.fmkorea.com/search.php?act=IS&is_keyword={keyword}&mid=home&where=document&page={page}&search_target=title_content")
    # 'ul' 태그의 클래스가 'searchResult'인 요소 찾기
    try:
        search_result_ul = driver.find_element(By.CLASS_NAME, "searchResult")
    except NoSuchElementException:
        print("No search result")
        return {
            "posts": [],
            "comments": []
        }
    posts_parsed, comments_parsed = [], []
    # 'li' 태그 찾기
    li_elements = search_result_ul.find_elements(By.TAG_NAME, "li")
    post_links = []
    for li in li_elements:
        timestamp_str = li.find_element(By.CLASS_NAME, "time").text
        timestamp_datetime = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M")
        if not start_date <= timestamp_datetime:
            continue
        if not timestamp_datetime <= end_date:
            break
        a_tag = li.find_element(By.TAG_NAME, "a")
        post_link = a_tag.get_attribute("href")
        post_links.append(post_link)
    print(f"parsing {len(post_links)} posts")
    for link in post_links:
        try:
            driver.get(link)
            driver.find_element(By.CLASS_NAME, "np_18px_span").text.strip()
            post_detail, comments = parse_post_detail(BeautifulSoup(driver.page_source, 'html.parser'),
                                                      driver.current_url)
            posts_parsed.append(post_detail)
            comments_parsed.extend(comments)
        except Exception as e:
            print(e)
    print(f"parsed {len(posts_parsed)} posts, {len(comments_parsed)} comments")
    driver.quit()
    return {
        "posts": posts_parsed,
        "comments": comments_parsed
    }


if __name__ == '__main__':
    from selenium import webdriver
    import csv

    results = main({
        "keyword": "iccu",
        "page": 1,
        'start_date': '2000-06-29',
        'end_date': '2040-07-29'
    }, {}, webdriver.Chrome())
    posts = results["posts"]
    comments = results["comments"]
    # _posts를 CSV 파일로 저장
    with open('posts.csv', mode='w', newline='', encoding='utf-8') as posts_file:
        fieldnames = ["id", "title", "content", "likes", "url", "author", "views", "created_at", "updated_at"]
        writer = csv.DictWriter(posts_file, fieldnames=fieldnames)

        writer.writeheader()  # 헤더 작성
        for post in posts:
            writer.writerow(post)  # 각 포스트 데이터 작성
    with open('comments.csv', mode='w', newline='', encoding='utf-8') as comments_file:
        fieldnames = ["post_id", "cmt_content", "cmt_author", "cmt_created_at", "cmt_updated_at"]
        writer = csv.DictWriter(comments_file, fieldnames=fieldnames)

        writer.writeheader()  # 헤더 작성
        for comment in comments:
            writer.writerow(comment)  # 각 댓글 데이터 작성

    print("CSV 파일 저장 완료!")