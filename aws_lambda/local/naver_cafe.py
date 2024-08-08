import csv
import os
from selenium import webdriver
from aws_lambda.sites import naver_cafe

if __name__ == '__main__':
    keyword = "코나 화재"

    # 폴더 생성
    base_folder = f'../resources/{keyword}/naver_cafe'
    os.makedirs(base_folder, exist_ok=True)

    for event in [{
        "site": "naver_cafe",
        "keyword": keyword,
        "page": i,
        "start_date": "2000-01-01",
        "end_date": "3000-12-30",
    } for i in range(1, 10)]:

        result = naver_cafe.main(event, {}, webdriver.Chrome())
        posts = result['posts']
        comments = result['comments']

        # posts CSV 파일 저장
        posts_folder = os.path.join(base_folder, 'posts')
        os.makedirs(posts_folder, exist_ok=True)
        with open(f'{posts_folder}/naver_cafe_posts_{keyword}_{event["page"]}.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=posts[0].keys())
            writer.writeheader()
            writer.writerows(posts)

        # comments CSV 파일 저장
        comments_folder = os.path.join(base_folder, 'comments')
        os.makedirs(comments_folder, exist_ok=True)
        with open(f'{comments_folder}/naver_cafe_comments_{keyword}_{event["page"]}.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=comments[0].keys())
            writer.writeheader()
            writer.writerows(comments)
