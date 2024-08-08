from selenium import webdriver
from ..sites import clien

if __name__ == '__main__':
    print(clien.main({
        "site": "clien",
        "keyword": "코나 화재",
        "page": 4,
        "start_date": "2000-01-01",
        "end_date": "3000-12-30",
    }, {}, webdriver.Chrome()))

    print(clien.main({
        "site": "clien",
        "keyword": "코나 화재",
        "page":3,
        "start_date": "2000-01-01",
        "end_date": "3000-12-30",
    }, {}, webdriver.Chrome()))

    print(clien.main({
        "site": "clien",
        "keyword": "코나 화재",
        "page": 5,
        "start_date": "2000-01-01",
        "end_date": "3000-12-30",
    }, {}, webdriver.Chrome()))
