from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import os

def in_range(datetime, datetime_start, datetime_end):
    return datetime_start <= datetime <= datetime_end


def open_url(driver, url):
    driver.get(url)
    time.sleep(2)
    return driver


def make_dummy_data(n):
    return [None for _ in range(n)]


def search_board_crawling(driver):
    # per page
    titles_elems = driver.find_elements(By.CLASS_NAME, "subject_fixed")
    created_ats_elems = driver.find_elements(By.CLASS_NAME, "timestamp")
    authors_elems = driver.find_elements(By.CLASS_NAME, "nickname")
    gif_authors_elems = driver.find_elements(By.CSS_SELECTOR, 'span.nickname img') # for gif nickname
    gif_authors_cnt = 0

    titles = []
    urls = []
    created_ats = []
    authors = []

    assert len(titles_elems) == len(created_ats_elems) and len(created_ats_elems) == len(authors_elems)
    posts_cnt = len(titles_elems)    
    for i in range(posts_cnt):
        titles.append(titles_elems[i].text) # get title
        urls.append(titles_elems[i].get_attribute('href')) # get url
        created_ats.append(created_ats_elems[i].get_attribute('textContent')) # get created time
        nickname = authors_elems[i].text
        if nickname == '':
            nickname = gif_authors_elems[gif_authors_cnt].get_attribute('alt')
            gif_authors_cnt+=1
        authors.append(nickname)
    return titles, urls, created_ats, authors, posts_cnt


def save_dict_to_csv(data, fp):
    df = pd.DataFrame(data)
    if not os.path.exists(fp):
        df.to_csv(fp, index=False, mode='w', encoding='utf-8-sig')
    else:
        df.to_csv(fp, index=False, mode='a', encoding='utf-8-sig', header=False)
    return
    
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
    if len(updated_at_elem)!=0:
        updated_at = updated_at_elem[0].text.split(" : ")[1].strip()
        
    # get view count
    view_cnt_elem = driver.find_element(By.CSS_SELECTOR, 'span.view_count > strong')
    view_cnt = int(view_cnt_elem.text.replace(',', ''))

    # get content
    class_name = 'post_article' 
    content_elems = driver.find_elements(By.CSS_SELECTOR, f'.{class_name} p, .{class_name} h1, \
    .{class_name} h2, .{class_name} h3, .{class_name} h4, .{class_name} h5, .{class_name} h6')
    
    content=""
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
    cmt_gif_authors_elem = cmt_ad_banner_elem.find_elements(By.CSS_SELECTOR, 'span.nickname img') # for gif nickname
    cmt_contents_elem = cmt_ad_banner_elem.find_elements(By.CLASS_NAME, "comment_view")
    cmt_gif_authors_cnt = 0
    cmt_created_at_elem = cmt_ad_banner_elem.find_elements(By.CLASS_NAME, "timestamp")

    assert len(cmt_authors_elem)==len(cmt_contents_elem)    
    cmt_cnt = len(cmt_authors_elem)
    
    for idx in range(cmt_cnt):
        cmt_author = cmt_authors_elem[idx].text
        if cmt_author=='': # for gif nickname
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


if __name__=="__main__":
    started=False
    end=False
    output_dir='/Users/admin/Desktop/HMG/ws/Project/Prototype-1/Crawling-르노/output/'

    # datetime_start='2024-06-20 00:00:00'
    # datetime_end='2024-07-20 23:59:59'
    # post_file_name='clien-르노-posts.csv'
    # comments_file_name='clien-르노-comments.csv'
    
    datetime_start='2024-06-29 00:00:00'
    datetime_end='2024-07-29 23:59:59'
    post_file_name='clien-홍명보-posts.csv'
    comments_file_name='clien-홍명보-comments.csv'
    
    post_fp = output_dir + post_file_name
    comment_fp = output_dir + comments_file_name
    
    driver = webdriver.Chrome()
    page_num=0
    while not end:
        post_idx = 0
        # 르노
        # search_board_url = f'https://www.clien.net/service/search?q=%EB%A5%B4%EB%85%B8&sort=recency&p={page_num}&boardCd=&isBoard=false'
        
        # 홍명보
        search_board_url = f'https://www.clien.net/service/search?q=%ED%99%8D%EB%AA%85%EB%B3%B4&sort=recency&p={page_num}&boardCd=&isBoard=false'
        driver = open_url(driver, search_board_url)
        titles, urls, created_ats, authors, posts_cnt = search_board_crawling(driver)
        updated_ats = []
        contents = []
        likes = []
        views = []
        post_ids = []
        end_idx = -1
        start_idx = -1
           
        for post_idx in range(len(titles)):
            if (not in_range(created_ats[post_idx], datetime_start, datetime_end)) and not started: # 코드 시작 후 원하는 범위에 포함되지 않는 게시물들 pass
                continue
            if started==True and created_ats[post_idx] < datetime_start: # 범위에 해당하는 모든 post를 확인한 경우, while문 종료
                end=True
                end_idx = post_idx
                break
            if (in_range(created_ats[post_idx], datetime_start, datetime_end)) and not started: # 처음 시작하는 경우
                started = True
                start_idx = post_idx
            if start_idx == -1:
                start_idx = 0
            post_url = urls[post_idx]
            driver = open_url(driver, post_url)
            content, like_cnt, view_cnt, cmt_authors, cmt_contents, cmt_post_ids, cmt_created_ats, cmt_updated_ats, cmt_cnt, post_id, updated_at = per_post_crawling(driver)

            # Save to comments.csv
            comment_data = {"post_id": cmt_post_ids, "cmt_content": cmt_contents, "cmt_author": cmt_authors, "cmt_created_at": cmt_created_ats, "cmt_updated_at": cmt_updated_ats}
            save_dict_to_csv(comment_data, comment_fp)

            post_ids.append(post_id)
            contents.append(content)
            likes.append(like_cnt)
            views.append(view_cnt)
            updated_ats.append(updated_at)
            print(f"title: {titles[post_idx]}\nnumber of comments: {cmt_cnt}" )

        # Save to posts.csv 
        if end_idx != -1:
            titles = titles[start_idx:end_idx]
            urls = urls[start_idx:end_idx]
            created_ats = created_ats[start_idx:end_idx]
            authors = authors[start_idx:end_idx]
        elif start_idx == -1 and end_idx == -1:
            titles, urls, created_ats, authors = [], [], [], []
        else:
            titles = titles[start_idx:]
            urls = urls[start_idx:]
            created_ats = created_ats[start_idx:]
            authors = authors[start_idx:]
                    
        post_data = {"id": post_ids, "title": titles, 'content': contents, 'likes': likes, 'url': urls, \
            'author': authors, 'views': views, "created_at": created_ats, "updated_at": updated_ats}
        save_dict_to_csv(post_data, post_fp)
        page_num += 1
    driver.quit()