import boto3
import json


def invoke_lambda_function(lambda_client, payload, function_name='web-scraping', ):
    lambda_client.invoke(
        FunctionName=function_name,
        InvocationType='Event',
        Payload=json.dumps(payload)
    )


if __name__ == '__main__':
    # AWS Lambda 클라이언트 생성
    lambda_client = boto3.client('lambda', region_name='ap-northeast-2')
    payloads = [
        {
            "site": "fmkorea",
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
