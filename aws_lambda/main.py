import logging
from tempfile import mkdtemp
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    site = event.get('site', 'fmkorea')
    keyword = event.get('keyword', '')
    page = event.get('page', 1)
    logger.info(f"scraping start site: {site}, page: {page}, keyword: {keyword} ")
    try:
        result = method_name(context, event, site)
        save_result(keyword, page, result, site)
    except Exception as e:
        logger.error(f"error site: {site}, page: {page}, keyword: {keyword}")
        logger.error(str(e))
        raise


def method_name(context, event, site):
    result = {}
    if site == "clien":
        from sites import clien
        result = clien.main(event, context, setup_driver())
    elif site == "fmkorea":
        from sites import fmkorea
        result = fmkorea.main(event, context, setup_driver())
    return result


def save_result(keyword, page, result, site):
    # S3에 저장
    for key, value in result.items():
        if len(value) == 0:
            continue
        save_to_s3("de3-web-scraping", f"{site}/{keyword}/{key}/{keyword}_{page}.csv",
                   value)


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
