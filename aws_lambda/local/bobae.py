from aws_lambda.local.utils import save_csv
from aws_lambda.sites import bobae
from selenium import webdriver

if __name__ == '__main__':
    payloads = [
        {
            "site": "bobae",
            "keyword": "코나 화재",
            "page": i,
            "start_date": "2019-07-26",
            "end_date": "2024-08-30",
        } for i in [32, 38, 12, 2, 9]
    ]
    for payload in payloads:
        results = bobae.main(payload, {}, webdriver.Chrome())
        posts = results["posts"]
        comments = results["comments"]
        print(f"posts {len(posts)}")
        print(f"comments {len(comments)}")
        keyword = payload["keyword"]
        site = payload["site"]
        page = payload["page"]
        save_csv(results, f"./{keyword}/{site}", page)
