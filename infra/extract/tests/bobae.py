from selenium import webdriver

from infra.extract.sites import bobae

if __name__ == '__main__':
    print(bobae.main({
        "duration": 6
    }, {}, webdriver.Chrome()))
