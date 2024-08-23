import logging
import http.client
import json
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

SLACK_WEBHOOK_URL = 'hooks.slack.com'  # Webhook URL의 도메인

def send_slack_message(message):
    SLACK_WEBHOOK_PATH = os.environ['SLACK_WEBHOOK_PATH']
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


def lambda_handler(event, context):
    send_slack_message(f"https://prod-apnortheast-a.online.tableau.com/t/wnl101206515e9cf6/views/dashboard-view-table/1?:origin=card_share_link&:embed=n")
