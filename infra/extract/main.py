import logging
import os
import urllib.parse
from datetime import datetime
from tempfile import mkdtemp
from typing import Dict, List, Any
import csv
import io
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import http.client
import json
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

SLACK_WEBHOOK_URL = 'hooks.slack.com'  # Webhook URL의 도메인
SLACK_WEBHOOK_PATH = '/services/T070MKQ7CJY/B07G10BC7U3/nRkzmVy5QIxTxwgWvc1R6i4x'  # Webhook URL의 경로


def lambda_handler(event, context):
    site = event.get('site', '')
    current_time = set_to_nearest_half_hour()
    logger.info(f"scraping start site={site}, time={current_time}")
    try:
        result = scrap(context, event, site)
        save_result(result, site, current_time)
        return {
            "batch_id": current_time.strftime('%Y%m%d%H%M')
        }
    except Exception as e:
        logger.error(f"error site={site}, time={current_time}")
        logger.error(str(e))
        region = os.environ['AWS_REGION']
        log_group_name = urllib.parse.unquote(context.log_group_name)
        cloudwatch_url = f"https://{region}.console.aws.amazon.com/cloudwatch/home?region={region}#logsV2:log-groups/log-group/{log_group_name}"
        send_slack_message(f"error site={site}, time={current_time}, cloudwatch_url={cloudwatch_url}")
        raise e


def scrap(context, event, site):
    result = {}
    if site == "bobae":
        from sites import bobae
        result = bobae.main(event, context, setup_driver())
    #     from sites import clien
    #     result = clien.main(event, context, setup_driver())
    # elif site == "fmkorea":
    #     from sites import fmkorea
    #     result = fmkorea.main(event, context, setup_driver())
    # elif site == "naver_cafe":
    #     from sites import naver_cafe
    #     result = naver_cafe.main(event, context, setup_driver())
    # elif site == "bobae":
    else:
        error_message = f"Site function not found: {site}"
        logger.error(error_message)
        raise ValueError(error_message)
    return result


def set_to_nearest_half_hour():
    collected_at = datetime.now().replace(second=0, microsecond=0)
    if collected_at.minute >= 30:
        collected_at = collected_at.replace(minute=30)
    else:
        collected_at = collected_at.replace(minute=00)
    return collected_at


def save_result(result: Dict[str, List[Any]], site, current_time: datetime):
    # S3에 저장
    for key, value in result.items():
        logger.info(f"saving results for {key}={len(value)}")
        if len(value) == 0:
            continue
        save_to_s3("de3-extract",
                   f"{site}/{current_time.strftime("%Y-%m-%d")}/{key}/{current_time.strftime('%Y%m%d%H%M')}.csv",
                   value)


def save_to_s3(bucket_name, file_name, data):
    s3 = boto3.client('s3')
    # 메모리 내에서 CSV 형식으로 데이터 저장
    csv_buffer = io.StringIO()
    writer = csv.DictWriter(csv_buffer, fieldnames=data[0].keys(), quoting=csv.QUOTE_ALL)
    # 헤더 작성
    writer.writeheader()
    # 데이터 작성
    for row in data:
        writer.writerow(row)
    # S3에 CSV 데이터 업로드
    s3.put_object(Bucket=bucket_name, Key=file_name, Body=csv_buffer.getvalue())


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


def send_slack_message(message):
    conn = http.client.HTTPSConnection(SLACK_WEBHOOK_URL)
    payload = json.dumps({'text': message})
    headers = {'Content-Type': 'application/json'}

    try:
        conn.request("POST", SLACK_WEBHOOK_PATH, payload, headers)
        response = conn.getresponse()
        if response.status != 200:
            logger.error(f"Slack 메시지 전송 실패: {response.status}, {response.read().decode()}")
    except Exception as e:
        logger.error(f"Slack 메시지 전송 중 오류 발생: {e}")
