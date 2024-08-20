from selenium import webdriver

from aws_lambda.local.utils import setup_headless_driver
from prototype.extract.sites import bobae

if __name__ == '__main__':
    print(bobae.main({
        "duration": 6
    }, {}, webdriver.Chrome()))
