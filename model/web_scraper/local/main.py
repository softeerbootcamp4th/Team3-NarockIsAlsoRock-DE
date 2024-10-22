from selenium import webdriver
from local.utils import save_csv
from src.sites import fmkorea

if __name__ == '__main__':
    payloads = [
        {
            "site": "fmkorea",
            "keyword": "코나 화재",
            "page": i,
            "start_date": "2019-07-26",
            "end_date": "2024-08-30",
        } for i in range(1,20)
    ]
    for payload in payloads:
        results = fmkorea.main(payload, {}, webdriver.Chrome())
        posts = results["posts"]
        comments = results["comments"]
        print(f"posts {len(posts)}")
        print(f"comments {len(comments)}")
        keyword = payload["keyword"]
        site = payload["site"]
        page = payload["page"]
        save_csv(results, f"./{keyword}/{site}", page)
