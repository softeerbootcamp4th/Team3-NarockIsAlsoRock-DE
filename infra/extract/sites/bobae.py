import re
from urllib.parse import urlparse, parse_qs

from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from datetime import datetime, timedelta

from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


def main(event, context, driver: WebDriver):
    # from lambda event
    duration = event.get('duration', 12)
    path = f"https://www.bobaedream.co.kr/list.php?code=national&pagescale=70&page=1"
    driver.get(path)

    WebDriverWait(driver, 2).until(expected_conditions.element_to_be_clickable(
        (By.CSS_SELECTOR, '#boardlist')))

    driver = click_latest_post(driver)

    posts_parsed, comments_parsed = [], []
    current_time = datetime.now()
    while True:
        if not is_post_exist(driver):
            driver = move_to_next_post(driver)
            continue

        created_at = parse_created_at(driver)
        if should_stop(created_at, current_time, duration):
            break

        post = parse_post(driver)
        comments = parse_comments(driver)
        if post is not None:
            posts_parsed.append(post)
            comments_parsed.extend(comments)

        driver = move_to_next_post(driver)

    driver.quit()
    return {
        "posts": posts_parsed,
        "comments": comments_parsed
    }


def should_stop(created_at, current_time, duration):
    return current_time - timedelta(hours=duration) > created_at


def click_latest_post(driver):
    posts = driver.find_element(By.CSS_SELECTOR, '#boardlist').find_element(By.TAG_NAME, "tbody").find_elements(
        By.TAG_NAME, "tr")
    for post in posts:
        if post.get_attribute("class") == "best":
            continue
        post.find_element(By.TAG_NAME, "a").click()
        break
    return driver

def move_to_next_post(driver):
    next_button = driver.find_element(By.CLASS_NAME, "topBtnGroup").find_element(By.XPATH, "//a[text()='다음글']")
    next_button.click()
    return driver


def is_post_exist(driver):
    try:
        driver.find_element(By.CLASS_NAME, "countGroup")
        return True
    except:
        return False


def parse_created_at(driver):
    # 요소에서 텍스트를 가져오고 필요 없는 부분을 제거
    created_at_str = driver.find_element(By.CLASS_NAME, "countGroup").text.split("|")[-1].strip()
    # 괄호와 괄호 안의 문자 삭제
    cleaned_str = re.sub(r'\s*\(.*?\)', '', created_at_str)
    # datetime 객체로 변환
    created_at = datetime.strptime(cleaned_str, "%Y.%m.%d %H:%M")
    return created_at


def parse_post(driver):
    id, title, content, likes, views, created_at, updated_at = None, None, None, None, None, None, None
    url = driver.current_url
    title = driver.find_element(By.XPATH,
                                '/html/body/div[1]/div[6]/div/div/div[1]/div[3]/div[1]/div[1]/dl/dt/strong').text
    try:
        contents = driver.find_element(By.CLASS_NAME, 'bodyCont')
    except:
        print(f"blinded post {url}")
        return None, []
    content = ''
    for p in contents.find_elements(By.TAG_NAME, 'p'):
        content += p.text

    likes = driver.find_element(By.ID, "tempPublic").text
    id = get_post_id(url)
    author = driver.find_element(By.CLASS_NAME, 'nickName').text
    views = driver.find_element(By.XPATH,
                                '/html/body/div[1]/div[6]/div/div/div[1]/div[3]/div[1]/div[1]/dl/dt/span/em[1]').text
    countGroup = driver.find_element(By.CLASS_NAME, 'countGroup')
    cnt_group_text_list = countGroup.text.split(' ')
    created_at = cnt_group_text_list[6] + ' ' + cnt_group_text_list[8]

    isDtTopBtns = True
    try:
        dtTopBtns = driver.find_element(By.CLASS_NAME, 'dtTopBtns')
    except:
        isDtTopBtns = False

    if isDtTopBtns:
        dtTopBtns_texts = dtTopBtns.text.split('|')
        if len(dtTopBtns_texts) == 4:
            text_splited = dtTopBtns_texts[0].split(' ')
            updated_at = text_splited[1] + " " + text_splited[3]

            # content 에서 , \n 제거
    content = re.sub(',', '', content)
    content = re.sub('\n', '', content)

    post_parsed = {
        'id': id,
        'title': title,
        'content': content,
        'likes': likes,
        'url': url,
        'author': author,
        'views': views,
        'created_at': created_at,
        'updated_at': updated_at,
    }

    return post_parsed


def get_post_id(url):
    # URL을 파싱합니다
    parsed_url = urlparse(url)
    # 쿼리 문자열에서 파라미터를 추출합니다
    parameters = parse_qs(parsed_url.query)
    id = parameters['No'][0]
    return id


def parse_comments(driver):
    comments_parsed = []
    comments = cmt_crawling(driver, post_id=id)
    comments_parsed.extend(comments)

    inSearchG = driver.find_element(By.ID, 'cmt_search')

    # 댓글 첫 페이지는 1
    cmt_page = 1

    # 댓글 페이지가 1보다 크면 ( 애초애 존재해야 1보다 큼)
    try:
        cmt_page = inSearchG.find_element(By.TAG_NAME, 'strong').text
        cmt_page = int(cmt_page)
    except:
        pass
    if cmt_page > 1:
        for i in range(cmt_page - 1, 0, -1):
            driver.execute_script(f"javascript:sel_cmt_paging('{i}');")
            comments = cmt_crawling(driver, post_id=id)
            comments_parsed.extend(comments)

    return comments_parsed


def cmt_crawling(driver, post_id):
    try:
        basiclist = driver.find_element(By.ID, 'cmt_reply')
    except:
        # 댓글이 없는 경우임
        return []
    comments = []
    if basiclist is not None:
        lis = basiclist.find_elements(By.TAG_NAME, 'li')

    for li in lis:
        try:
            content = li.find_element(By.TAG_NAME, 'dd').text
            content = re.sub(',', '', content)
            content = re.sub('\n', '', content)
            author = li.find_element(By.CLASS_NAME, 'author').text
            date = li.find_element(By.CLASS_NAME, 'date').text
            comments.append({
                "post_id": post_id,
                "cmt_content": content,
                "cmt_author": author,
                "cmt_created_at": date,
            })
        except:
            pass
    return comments
