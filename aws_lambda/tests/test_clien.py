from selenium import webdriver
from aws_lambda.sites import clien

if __name__ == '__main__':
    for event in [{
        "site": "clien",
        "keyword": "코나 화재",
        "page": i,
        "start_date": "2000-01-01",
        "end_date": "3000-12-30",
    } for i in range(0, 31)]:
        print(clien.main(event, {}, webdriver.Chrome()))
