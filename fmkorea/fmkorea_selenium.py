from bs4 import BeautifulSoup, Comment
from datetime import datetime
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from urllib.parse import urlparse
import pandas as pd
import time
import csv
import traceback
import os


def merge_csv(folder_name):
    # CSV 파일들이 있는 폴더 경로를 지정합니다.
    folder_path = f'./raw/{folder_name}'

    # 폴더 내의 모든 CSV 파일 리스트를 가져옵니다.
    csv_files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]

    # 빈 리스트를 생성하여 모든 DataFrame을 저장합니다.
    dataframes = []

    # 각 CSV 파일을 읽어서 리스트에 추가합니다.
    for file in csv_files:
        file_path = os.path.join(folder_path, file)
        df = pd.read_csv(file_path)
        dataframes.append(df)

    # 모든 DataFrame을 하나로 합칩니다.
    combined_df = pd.concat(dataframes, ignore_index=True)

    combined_df.to_csv(f"./{folder_name}.csv", index=False, encoding='utf-8-sig')


def save_as_csv(posts, comments, page):
    # posts.csv 저장
    if len(posts) != 0:
        with open(f'./raw/posts/posts_{page}.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ["id", "title", "content", "likes", "url", "author", "views", "created_at", "updated_at"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for post in posts:
                writer.writerow(post)
    if len(comments) != 0:
        # comments.csv 저장
        with open(f'./raw/comments/comments_{page}.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['post_id', 'author', 'content', 'time']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for comment in comments:
                writer.writerow(comment)


def parse_post_detail(bs: BeautifulSoup, current_url: str):
    # URL 파싱
    parsed_url = urlparse(current_url)
    # 경로에서 게시물 ID 추출
    post_id = parsed_url.path.split('/')[-1]
    title = bs.find('span', class_='np_18px_span').text.strip()
    content = []

    article = bs.find('div', class_='xe_content')
    # 주석 제거
    for comment in article.find_all(text=lambda text: isinstance(text, Comment)):
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
        "content": ' \n'.join(content).replace('\r\n', ' ').replace('\n', ' '),
        "likes": likes,
        "url": current_url,
        "author": author,
        "views": views,
        "created_at": created_at,
        "updated_at": None
    }
    return post, comments


if __name__ == '__main__':
    keyword = '홍명보'
    page = 96
    start_date = datetime(2024, 6, 29)
    end_date = datetime(2024, 7, 29)
    # Chrome 브라우저를 실행합니다.
    driver = webdriver.Chrome()
    # Google 홈페이지를 엽니다.
    driver.get(
        url=f"https://www.fmkorea.com/search.php?act=IS&is_keyword={keyword}&mid=home&where=document&page={page}&search_target=title"
    )
    time.sleep(3)
    while page <= 1000:
        try:
            print(f"parsing page {page}")
            bs = BeautifulSoup(driver.page_source, 'html.parser')
            posts = bs.find("ul", attrs={"class": "searchResult"}).find_all("li")
            # 게시물 목록에서 모든 게시물 제목 링크를 찾습니다.
            post_links = driver.find_elements(By.CSS_SELECTOR, "ul.searchResult li dl dt a")
            posts_parsed = []
            comments_parsed = []
            for index, (post, post_link) in enumerate(zip(posts, post_links)):
                if not post_link or not post:
                    print(f"post link not found for {post.find("a").text}")
                    continue
                timestamp_str = post.find("span", attrs={"class": "time"}).text
                timestamp_datetime = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M")
                if not start_date <= timestamp_datetime <= end_date:
                    print(f"date not desired {timestamp_datetime}")
                    continue

                # Windows/Linux에서는 Ctrl + Enter, macOS에서는 Command + Enter
                post_link.send_keys(Keys.COMMAND + Keys.RETURN)
                time.sleep(2)  # 페이지가 로드될 때까지 대기
                # 모든 탭 핸들 가져오기
                tabs = driver.window_handles
                # 새 탭으로 전환 (예: 두 번째 탭으로 전환)
                new_tab = tabs[1]
                driver.switch_to.window(new_tab)
                time.sleep(2)
                # 페이지 로딩을 위해 잠시 대기합니다.
                post, comments = parse_post_detail(BeautifulSoup(driver.page_source, 'html.parser'), driver.current_url)
                posts_parsed.append(post)
                comments_parsed.extend(comments)
                driver.close()
                # 원래 탭으로 돌아가기
                original_tab = tabs[0]
                driver.switch_to.window(original_tab)

            save_as_csv(posts_parsed, comments_parsed, page)
            page += 1
            next_page = driver.find_element(By.XPATH, f"//a[contains(@href, 'page={page}')]")
            next_page.click()
            time.sleep(2)
        except Exception as e:
            print(f"다음 페이지 링크를 찾는 데 실패했습니다: {page}")
            print(e)
            traceback.print_exc()

    # 작업 완료 후 브라우저를 닫습니다.
    driver.quit()
