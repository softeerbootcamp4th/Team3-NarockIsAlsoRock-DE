from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from datetime import datetime
import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions


def clean_content(content):
    return re.sub(r'\s+', ' ', content.replace('\r\n', ' ').replace('\n', ' ')).strip()


def search_board_crawling(driver: WebDriver):
    WebDriverWait(driver, 2).until(expected_conditions.visibility_of_element_located((By.CLASS_NAME, "subject_fixed")))
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
    try:
        # get post_id
        WebDriverWait(driver, 2).until(
            expected_conditions.presence_of_element_located((By.CSS_SELECTOR, 'meta[property="url"]')))
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
        cmt_contents_elem = cmt_ad_banner_elem.find_elements(By.CLASS_NAME, "comment_view")
        cmt_gif_authors_cnt = 0
        cmt_created_at_elem = cmt_ad_banner_elem.find_elements(By.CLASS_NAME, "timestamp")

        assert len(cmt_authors_elem) == len(cmt_contents_elem)
        cmt_cnt = len(cmt_authors_elem)

        for idx in range(cmt_cnt):
            cmt_author = cmt_authors_elem[idx].text
            if cmt_author == '':  # for gif nickname
                cmt_author = cmt_ad_banner_elem.find_elements(By.CSS_SELECTOR, 'span.nickname img')[
                    cmt_gif_authors_cnt].get_attribute('alt')
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
    except Exception as e:
        print(e)
        return None, None, None, None, None, None, None, None, None, None, None


def main(event, context, driver: WebDriver):
    keyword = event.get('keyword', '')
    page = event.get('page', 1)
    datetime_start = datetime.strptime(event.get('start_date', '2024-06-29'), '%Y-%m-%d')
    datetime_end = datetime.strptime(event.get('end_date', '2024-07-29'), '%Y-%m-%d')
    driver.get(f'https://www.clien.net/service/search?q={keyword}&sort=recency&p={page}&boardCd=&isBoard=false')

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
        if not datetime_start <= datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S') <= datetime_end:
            continue
        if not datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S') <= datetime_end:
            break
        driver.get(post_url)
        content, like_cnt, view_cnt, cmt_authors, cmt_contents, cmt_post_ids, cmt_created_ats, cmt_updated_ats, cmt_cnt, post_id, updated_at = per_post_crawling(
            driver)
        if post_id is None:
            continue
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
    for i in range(len(posts["id"])):
        _posts.append({
            "id": posts["id"][i],
            "title": clean_content(posts["title"][i]),
            "content": clean_content(posts["content"][i]),
            "likes": posts["likes"][i],
            "url": posts["url"][i],
            "author": posts["author"][i],
            "views": posts["views"][i],
            "created_at": posts["created_at"][i],
            "updated_at": posts["updated_at"][i]
        })
    # 변환 작업
    _comments = []
    for i in range(len(comments["post_id"])):
        _comments.append({
            "post_id": comments["post_id"][i],
            "cmt_content": clean_content(comments["cmt_content"][i]),
            "cmt_author": comments["cmt_author"][i],
            "cmt_created_at": comments["cmt_created_at"][i],
            "cmt_updated_at": comments["cmt_updated_at"][i],
        })

    return {
        "posts": _posts,
        "comments": _comments
    }


if __name__ == '__main__':
    from selenium import webdriver
    import csv

    results = main({
        "keyword": "iccu",
        "page": 20,
        'start_date': '2020-06-29',
        'end_date': '2024-07-29'
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
    # _comments를 CSV 파일로 저장
    with open('comments.csv', mode='w', newline='', encoding='utf-8') as comments_file:
        fieldnames = ["post_id", "cmt_content", "cmt_author", "cmt_created_at", "cmt_updated_at"]
        writer = csv.DictWriter(comments_file, fieldnames=fieldnames)

        writer.writeheader()  # 헤더 작성
        for comment in comments:
            writer.writerow(comment)  # 각 댓글 데이터 작성

    print("CSV 파일 저장 완료!")