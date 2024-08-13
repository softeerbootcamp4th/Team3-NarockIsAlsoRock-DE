import boto3
import json
import pandas as pd

def invoke_lambda_function(lambda_client, payload, function_name='web-scraping', ):
    lambda_client.invoke(
        FunctionName=function_name,
        InvocationType='Event',
        Payload=json.dumps(payload)
    )

def divide_by_6_month(start_date="2020-01-01", end_date="2024-06-30"):
    # 날짜 범위 생성
    date_range = pd.date_range(start=start_date, end=end_date, freq='6ME')
    # 시작과 끝 날짜를 튜플로 묶기
    date_tuples = [(date_range[i].strftime('%Y-%m-%d'), date_range[i + 1].strftime('%Y-%m-%d')) for i in
                   range(len(date_range) - 1)]
    date_tuples.insert(0, (start_date, date_tuples[0][0]))
    date_tuples.append((date_tuples[-1][1], end_date))
    return date_tuples

if __name__ == '__main__':
    # AWS Lambda 클라이언트 생성
    lambda_client = boto3.client('lambda', region_name='ap-northeast-2')
    # 코나 화재는 40 페이지
    payloads = [
        {
            "site": "naver_cafe",
            "keyword": "코나 화재",
            "page": i,
            "start_date": "2019-07-26",
            "end_date": "2024-08-30",
        } for i in range(1, 18)
    ]
    for index, payload in enumerate(payloads):
        invoke_lambda_function(lambda_client, payload)
        # 응답 출력 (비동기 호출이므로 결과는 없음)
        print(f"Lambda function {payload['page']} invoked asynchronously.")
