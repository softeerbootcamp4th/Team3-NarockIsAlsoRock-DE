import boto3
import json

# AWS Lambda 클라이언트 생성
lambda_client = boto3.client('lambda', region_name='ap-northeast-2')  # 예: 'us-west-2'


def invoke_lambda_function(payload, function_name= 'web-scraping', ):
    lambda_client.invoke(
        FunctionName=function_name,
        InvocationType='Event',
        Payload=json.dumps(payload)
    )


if __name__ == '__main__':
    payloads = [
        {
            "site": "naver_cafe",
            "keyword": "코나 화재",
            "page": i,
            "start_date": "2000-01-01",
            "end_date": "3000-12-30",
        } for i in range(1, 10)
    ]
    for index, payload in enumerate(payloads):
        invoke_lambda_function(payload)
        # 응답 출력 (비동기 호출이므로 결과는 없음)
        print(f"Lambda function {index} invoked asynchronously.")
