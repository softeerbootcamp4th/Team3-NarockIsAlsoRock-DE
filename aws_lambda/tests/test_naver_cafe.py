from selenium import webdriver
from aws_lambda.sites import naver_cafe

if __name__ == '__main__':
    for event in [{
        "site": "naver_cafe",
        "keyword": "코나 화재",
        "page": i,
        "start_date": "2000-01-01",
        "end_date": "3000-12-30",
    } for i in range(9,10)]:
        print(naver_cafe.main(event, {}, webdriver.Chrome()))
