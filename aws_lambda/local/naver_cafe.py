import csv
import multiprocessing
import os
import pandas as pd
from aws_lambda.local.driver import setup_headless_driver
from aws_lambda.sites import naver_cafe


def divide_by_6_month(start_date="2020-01-01", end_date="2024-06-30"):
    # 날짜 범위 생성
    date_range = pd.date_range(start=start_date, end=end_date, freq='6ME')
    # 시작과 끝 날짜를 튜플로 묶기
    date_tuples = [(date_range[i].strftime('%Y-%m-%d'), date_range[i + 1].strftime('%Y-%m-%d')) for i in
                   range(len(date_range) - 1)]
    date_tuples.insert(0, (start_date, date_tuples[0][0]))
    date_tuples.append((date_tuples[-1][1], end_date))
    return date_tuples


def worker(event):
    base_folder = f'../../resources/{event['keyword']}/naver_cafe'
    for i in range(1, 41):
        try:
            event['page'] = i
            print(f"{event} start")
            result = naver_cafe.main(event, {}, setup_headless_driver())
            print(f"{event} done. posts : {len(result['posts'])}")
            posts = result['posts']
            comments = result['comments']

            posts_folder = os.path.join(base_folder, f'posts/{event['start_date']}')
            os.makedirs(posts_folder, exist_ok=True)
            if len(posts) == 0:
                print(f"{event} empty page")
                break
            with open(f'{posts_folder}/{event["page"]}.csv', mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=posts[0].keys())
                writer.writeheader()
                writer.writerows(posts)

            if len(comments) == 0:
                continue
            comments_folder = os.path.join(base_folder, f'comments/{event['start_date']}')
            os.makedirs(comments_folder, exist_ok=True)
            with open(f'{comments_folder}/{event["page"]}.csv', mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=comments[0].keys())
                writer.writeheader()
                writer.writerows(comments)
        except Exception as e:
            print(e)
            print(f"{event} failed")


if __name__ == '__main__':
    keyword = "코나EV"
    base_folder = f'../../resources/{keyword}/naver_cafe'
    os.makedirs(base_folder, exist_ok=True)
    start_date = "2018-01-01"
    end_date = "2021-06-30"
    processes = []
    for event in [{
        "site": "naver_cafe",
        "keyword": keyword,
        "start_date": start,
        "end_date": end,
    } for start, end in divide_by_6_month(start_date, end_date)]:
        p = multiprocessing.Process(target=worker, args=(event,))
        processes.append(p)
        p.start()
    for p in processes:
        p.join()
