import time
import re
import time
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
from selenium.webdriver.chrome.webdriver import WebDriver
from datetime import datetime


def cmt_crawling(driver, post_id):
    try:
        basiclist = driver.find_element(By.ID, 'cmt_reply')
    except:
        # 댓글이 없는 경우임
        return None
        
    if basiclist is not None:
        lis = basiclist.find_elements(By.TAG_NAME, 'li')
    
    for li in lis:
        try:
            content = li.find_element(By.TAG_NAME, 'dd').text
            content = re.sub(',', '', content)
            content = re.sub('\n', '', content)
            author = li.find_element(By.CLASS_NAME, 'author').text
            date = li.find_element(By.CLASS_NAME, 'date').text
            cmt_likes = li.find_element(By.CLASS_NAME, 'link1').text.split(' ')[1].rstrip('')
        except:
            return None

        comments_data = {
            "post_id": post_id,
            "cmt_content": content,
            "cmt_author": author,
            "cmt_created_at": date,
            "cmt_updated_at": None,
            "cmt_likes": cmt_likes
        }
    return comments_data


def post_crawling(driver, url, author):
    id, title, content, likes, views, created_at, updated_at = None, None, None, None, None, None, None
    
    driver.get(url)
    title = driver.find_element(By.XPATH, '/html/body/div[1]/div[6]/div/div/div[1]/div[3]/div[1]/div[1]/dl/dt/strong').text
    contents = driver.find_element(By.XPATH, '/html/body/div[1]/div[6]/div/div/div[1]/div[3]/div[1]/div[2]/div')
    content = ''
    for p in contents.find_elements(By.TAG_NAME, 'p'):
        content += p.text

    likes = driver.find_element(By.ID, "tempPublic").text
    id = url.split('=')[-1]
    views = driver.find_element(By.XPATH, '/html/body/div[1]/div[6]/div/div/div[1]/div[3]/div[1]/div[1]/dl/dt/span/em[1]').text
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
    
    #######################
    # 댓글 크롤링
    #######################
    comments_parsed = []
    comments_data = cmt_crawling(driver, post_id=id)
    comments_parsed.append(comments_data)
    
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
        for i in range(cmt_page-1, 0, -1):
            driver.execute_script(f"javascript:sel_cmt_paging('{i}');")
            time.sleep(0.3)
            comments_data = cmt_crawling(driver, post_id=id)
            if comments_data is not None:
                comments_parsed.append(comments_data)
    
    return post_parsed, comments_parsed


def main(event, context, driver: WebDriver):
    # from lambda event
    keyword = event.get('keyword', '')
    page_num = event.get('page', '')
    start_date_str = event.get('start_date', '2024-06-29')
    end_date_str = event.get('end_date', '2024-07-29')
    timestamp_datetime_start = datetime.strptime(start_date_str, '%Y-%m-%d')
    timestamp_datetime_end = datetime.strptime(end_date_str, '%Y-%m-%d')
    
    # 검색어
    search_keyword = urllib.parse.quote(keyword.encode('euc-kr'))
    
    path ="https://www.bobaedream.co.kr/"
    driver = webdriver.Chrome()
    driver.get(path)
    time.sleep(0.5)

    # 검색창 클릭
    driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div/div[2]/ul/li[1]/button/span').click()

    # input element 찾기
    input_element = driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div/div[2]/ul/li[1]/div/form/span/input')

    # '검색어' 텍스트 입력 및 제출
    input_element.send_keys(search_keyword)
    input_element.submit()

    # 커뮤니티 더보기 클릭
    driver.find_element(By.XPATH, '/html/body/div/div[3]/div[2]/div[5]/div[2]/a').click()
    
    # Go to page page_num    
    new_href = f"javascript:s_go('community','ALL','{page_num}');"
    driver.execute_script(new_href)
    
    soup = bs(driver.page_source, 'html.parser')
    
    article = soup.select('div.search_Community ul dl')
    texts = [i.find('dd', class_='path').text.strip().split('\n') for i in article]
    links = [link.a['href'] for link in article]
    boards = [i[0] for i in texts]
    authors = [i[1] for i in texts]
    dates = [i[2] for i in texts]
    
    # 게시글 제목, 링크
    # article = soup.select('div.inner_list a.article')
    # titles = [link.text.strip() for link in article]
    # links = [link['href'] for link in article]
    
    posts_parsed, comments_parsed = [], []
    # 10개의 글에 대해
    for link, author in zip(links, authors):
        posts_data, comments_data = post_crawling(driver, link, author)

        if posts_data != None:
            posts_parsed.append(posts_data)
        if comments_data != None:
            comments_parsed.extend(comments_data)
    driver.quit()
    return {
        "posts": posts_parsed,
        "comments": comments_parsed
    }