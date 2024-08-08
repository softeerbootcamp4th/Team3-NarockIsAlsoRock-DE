from selenium import webdriver
from aws_lambda.sites import naver_cafe

if __name__ == '__main__':
    for event in [{
        "site": "naver_cafe",
        "keyword": "iccu",
        "page": i,
        "start_date": "2000-01-01",
        "end_date": "3000-12-30",
    } for i in range(4, 5)]:
        print(naver_cafe.main(event, {}, webdriver.Chrome()))
