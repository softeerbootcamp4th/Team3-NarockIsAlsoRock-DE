from tempfile import mkdtemp
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import boto3


def save_to_s3(bucket_name, file_name, data):
    s3 = boto3.client('s3')
    csv_data = "\n".join([",".join(map(str, row.values())) for row in data])
    s3.put_object(Bucket=bucket_name, Key=file_name, Body=csv_data)


def setup_driver():
    chrome_options = Options()
    chrome_options.binary_location = "/opt/chrome/chrome-linux64/chrome"
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-tools")
    chrome_options.add_argument("--no-zygote")
    chrome_options.add_argument("--single-process")
    chrome_options.add_argument(f"--user-data-dir={mkdtemp()}")
    chrome_options.add_argument(f"--data-path={mkdtemp()}")
    chrome_options.add_argument(f"--disk-cache-dir={mkdtemp()}")
    chrome_options.add_argument("--remote-debugging-pipe")
    chrome_options.add_argument("--verbose")
    chrome_options.add_argument("--log-path=/tmp")

    service = Service(executable_path="/opt/chrome-driver/chromedriver-linux64/chromedriver",
                      service_log_path="/tmp/chromedriver.log")
    return webdriver.Chrome(service=service, options=chrome_options)


def lambda_handler(event, context):
    site = event.get('site', 'fmkorea')
    keyword = event.get('keyword', '')
    page = event.get('page', 1)

    result = {
        "posts": [],
        "comments": []
    }
    if site == "clien":
        from sites import clien
        result = clien.main(event, context, setup_driver())
    elif site == "fmkorea":
        from sites import fmkorea
        result = fmkorea.main(event, context, setup_driver())

    # S3에 저장
    if len(result["posts"]) != 0:
        save_to_s3("de3-web-scraping", f"{site}/{keyword}/posts/{keyword}_{page}.csv",
                   result["posts"])
        save_to_s3("de3-web-scraping", f"{site}/{keyword}/comments/{keyword}_{page}.csv",
                   result["comments"])
