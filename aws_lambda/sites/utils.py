from selenium import webdriver
import csv
import os


def save_csv(dict,directory, page):
    # 디렉토리가 없으면 생성
    if not os.path.exists(directory):
        os.makedirs(directory)
    # CSV 파일로 저장
    with open(f"{directory}/{page}.csv", mode='w', newline='', encoding='utf-8') as comments_file:
        writer = csv.DictWriter(comments_file, fieldnames=dict[0].keys())  # 헤더를 위해 필드명 설정
        writer.writeheader()
        for row in dict:
            writer.writerow(row)
