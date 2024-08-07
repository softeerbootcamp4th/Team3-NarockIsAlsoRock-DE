import boto3
import json

# AWS Lambda 클라이언트 생성
lambda_client = boto3.client('lambda', region_name='ap-northeast-2')  # 예: 'us-west-2'


def invoke_lambda_function(function_name, payload):
    lambda_client.invoke(
        FunctionName=function_name,
        InvocationType='Event',
        Payload=json.dumps(payload)
    )


# 실행할 Lambda 함수 이름
function_name = 'web-scraping'

# 여러 파라미터로 Lambda 함수 호출
parameters = [
    {
        "keyword": "홍명보",
        "page": 150,
        "start_date": "2024-01-01",
        "end_date": "2024-12-30",
        "bucket_name": "fmkore-scraping-lambda"
    },
    {
        "keyword": "홍명보",
        "page": 151,
        "start_date": "2024-01-01",
        "end_date": "2024-12-30",
        "bucket_name": "fmkore-scraping-lambda"
    },
    {
        "keyword": "홍명보",
        "page": 152,
        "start_date": "2024-01-01",
        "end_date": "2024-12-30",
        "bucket_name": "fmkore-scraping-lambda"
    },
    {
        "keyword": "홍명보",
        "page": 153,
        "start_date": "2024-01-01",
        "end_date": "2024-12-30",
        "bucket_name": "fmkore-scraping-lambda"
    },
    {
        "keyword": "홍명보",
        "page": 154,
        "start_date": "2024-01-01",
        "end_date": "2024-12-30",
        "bucket_name": "fmkore-scraping-lambda"
    },
]

for param in parameters:
    invoke_lambda_function(function_name, param)
    # 응답 출력 (비동기 호출이므로 결과는 없음)
    print("Lambda function invoked asynchronously.")
