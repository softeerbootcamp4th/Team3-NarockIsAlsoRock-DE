from selenium import webdriver
from aws_lambda.sites import bobae

if __name__ == '__main__':
    print(bobae.main({
        "duration": 6
    }, {}, webdriver.Chrome()))
