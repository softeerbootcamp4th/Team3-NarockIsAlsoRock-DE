from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
from selenium.webdriver.chrome.options import Options
from tempfile import mkdtemp
from selenium.webdriver.chrome.service import Service

import boto3
import time
import re


def save_to_s3(bucket_name, file_name, data):
    s3 = boto3.client('s3')
    csv_data = "\n".join([",".join(map(str, row.values())) for row in data])
    s3.put_object(Bucket=bucket_name, Key=file_name, Body=csv_data)


def search_board_crawling(driver):
    # per page
    titles_elems = driver.find_elements(By.CLASS_NAME, "subject_fixed")
    created_ats_elems = driver.find_elements(By.CLASS_NAME, "timestamp")
    authors_elems = driver.find_elements(By.CLASS_NAME, "nickname")
    gif_authors_elems = driver.find_elements(By.CSS_SELECTOR, 'span.nickname img')  # for gif nickname
    gif_authors_cnt = 0

    titles = []
    urls = []
    created_ats = []
    authors = []

    assert len(titles_elems) == len(created_ats_elems) and len(created_ats_elems) == len(authors_elems)
    for i in range(len(titles_elems)):
        titles.append(titles_elems[i].text)  # get title
        urls.append(titles_elems[i].get_attribute('href'))  # get url
        created_ats.append(created_ats_elems[i].get_attribute('textContent'))  # get created time
        nickname = authors_elems[i].text
        if nickname == '':
            nickname = gif_authors_elems[gif_authors_cnt].get_attribute('alt')
            gif_authors_cnt += 1
        authors.append(nickname)
    return titles, urls, created_ats, authors


def per_post_crawling(driver):
    # per post
    # get post_id
    meta_tag = driver.find_element(By.CSS_SELECTOR, 'meta[property="url"]')
    url_value = meta_tag.get_attribute('content')
    match = re.search(r'/(\d+)$', url_value)
    post_id = int(match.group(1))

    # get likes
    like_cnt_element = driver.find_element(By.CSS_SELECTOR, 'a.symph_count > strong')
    like_cnt = int(like_cnt_element.text)

    # updated_at
    updated_at = None
    updated_at_elem = driver.find_elements(By.CLASS_NAME, "lastdate")
    if len(updated_at_elem) != 0:
        updated_at = updated_at_elem[0].text.split(" : ")[1].strip()

    # get view count
    view_cnt_elem = driver.find_element(By.CSS_SELECTOR, 'span.view_count > strong')
    view_cnt = int(view_cnt_elem.text.replace(',', ''))

    # get content
    class_name = 'post_article'
    content_elems = driver.find_elements(By.CSS_SELECTOR, f'.{class_name} p, .{class_name} h1, \
    .{class_name} h2, .{class_name} h3, .{class_name} h4, .{class_name} h5, .{class_name} h6')

    content = ""
    for content_elem in content_elems:
        content += content_elem.text

    # get comments
    cmt_authors = []
    cmt_contents = []
    cmt_post_ids = []
    cmt_created_ats = []
    cmt_updated_ats = []

    cmt_ad_banner_elem = driver.find_element(By.CLASS_NAME, "comment.ad_banner")
    cmt_authors_elem = cmt_ad_banner_elem.find_elements(By.CLASS_NAME, "nickname")
    cmt_gif_authors_elem = cmt_ad_banner_elem.find_elements(By.CSS_SELECTOR, 'span.nickname img')  # for gif nickname
    cmt_contents_elem = cmt_ad_banner_elem.find_elements(By.CLASS_NAME, "comment_view")
    cmt_gif_authors_cnt = 0
    cmt_created_at_elem = cmt_ad_banner_elem.find_elements(By.CLASS_NAME, "timestamp")

    assert len(cmt_authors_elem) == len(cmt_contents_elem)
    cmt_cnt = len(cmt_authors_elem)

    for idx in range(cmt_cnt):
        cmt_author = cmt_authors_elem[idx].text
        if cmt_author == '':  # for gif nickname
            cmt_author = cmt_gif_authors_elem[cmt_gif_authors_cnt].get_attribute('alt')
            cmt_gif_authors_cnt += 1
        cmt_authors.append(cmt_author)
        cmt_contents.append(cmt_contents_elem[idx].text)
        cmt_datetime_info = cmt_created_at_elem[idx].get_attribute('textContent')
        cmt_updated_at = None
        if "/" in cmt_datetime_info:
            cmt_created_at, cmt_updated_at = cmt_datetime_info.split("/")
            cmt_updated_at = cmt_updated_at.split(": ")[1]
        else:
            cmt_created_at = cmt_datetime_info
        cmt_created_at = cmt_created_at.strip()

        if cmt_updated_at != None:
            cmt_updated_at = cmt_updated_at.strip()

        cmt_created_ats.append(cmt_created_at)
        cmt_updated_ats.append(cmt_updated_at)
        cmt_post_ids.append(post_id)

    return content, like_cnt, view_cnt, cmt_authors, cmt_contents, cmt_post_ids, cmt_created_ats, cmt_updated_ats, cmt_cnt, post_id, updated_at


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
    datetime_start = datetime.strptime(event.get('start_date', '2024-06-29'), '%Y-%m-%d')
    datetime_end = datetime.strptime(event.get('end_date', '2024-07-29'), '%Y-%m-%d')
    bucket_name = event.get('bucket_name')

    driver = setup_driver()
    driver.get(f'https://www.clien.net/service/search?q={keyword}&sort=recency&p={page}&boardCd=&isBoard=false')
    time.sleep(2)

    titles, urls, created_ats, authors = search_board_crawling(driver)

    post_ids = []
    _titles = []
    _urls = []
    _created_ats = []
    _authors = []
    updated_ats = []
    contents = []
    likes = []
    views = []

    _cmt_post_ids = []
    _cmt_contents = []
    _cmt_authors = []
    _cmt_created_ats = []
    _cmt_updated_ats = []
    for title, post_url, created_at, author in zip(titles, urls, created_ats, authors):
        if not datetime_start <= created_at <= datetime_end:
            continue
        driver.get(post_url)
        time.sleep(2)
        content, like_cnt, view_cnt, cmt_authors, cmt_contents, cmt_post_ids, cmt_created_ats, cmt_updated_ats, cmt_cnt, post_id, updated_at = per_post_crawling(
            driver)
        _cmt_post_ids.extend(cmt_authors)
        _cmt_contents.extend(cmt_contents)
        _cmt_authors.extend(cmt_post_ids)
        _cmt_created_ats.extend(cmt_created_ats)
        _cmt_updated_ats.extend(cmt_updated_ats)
        post_ids.append(post_id)
        _titles.append(title)
        _urls.append(post_url)
        _created_ats.append(created_at)
        _authors.append(author)
        contents.append(content)
        likes.append(like_cnt)
        views.append(view_cnt)
        updated_ats.append(updated_at)
    driver.quit()

    posts = {"id": post_ids, "title": _titles, 'content': contents, 'likes': likes, 'url': _urls, \
             'author': _authors, 'views': views, "created_at": _created_ats, "updated_at": updated_ats}
    comments = {"post_id": _cmt_post_ids, "cmt_content": _cmt_contents, "cmt_author": _cmt_authors,
                "cmt_created_at": _cmt_created_ats, "cmt_updated_at": _cmt_updated_ats}

    # 변환 작업
    _posts = []
    for i in range(len(post_ids)):
        _posts.append({
            "id": posts["id"][i],
            "title": posts["title"][i],
            "content": posts["content"][i],
            "likes": posts["likes"][i],
            "url": posts["url"][i],
            "author": posts["author"][i],
            "views": posts["views"][i],
            "created_at": posts["created_at"][i],
            "updated_at": posts["updated_at"][i]
        })
    # 변환 작업
    _comments = []
    for i in range(len(comments)):
        _comments.append({
            "post_id": comments["post_id"][i],
            "cmt_content": comments["cmt_content"][i],
            "cmt_author": comments["cmt_author"][i],
            "cmt_created_at": comments["cmt_created_at"][i],
            "cmt_updated_at": comments["cmt_updated_at"][i],
        })

    # S3에 저장
    save_to_s3(bucket_name, f"{keyword}/posts/posts_{keyword}_page_{page}.csv", _posts)
    save_to_s3(bucket_name, f"{keyword}/comments/comments_{keyword}_page_{page}.csv", _comments)

    return {
        "posts": posts,
        "comments": comments
    }
