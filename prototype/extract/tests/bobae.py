from selenium import webdriver
from monitor.scrapper.sites import bobae

if __name__ == '__main__':
    print(bobae.main({
        "duration": 6
    }, {}, webdriver.Chrome()))
