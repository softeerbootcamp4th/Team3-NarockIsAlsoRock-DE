# 개요
EDA를 진행하기 위해 SNS에서 게시물과 댓글을 스크랭핑하는 코드입니다.

src/sites 안에 AWS Lambda, 로컬에서 모두 사용 가능한 SNS별 웹스크래핑 로직이 들어있습니다.

lambda 경로에는 웹 스크래핑 로직을 AWS Lambda 함수로 만들기 위해 도커 이미로 빌드하는 코드가 있습니다.

local은 웹 스크래핑을 로컬에서 실행하는 코드입니다..

tests는 스크래핑에 필요한 핵심 로직을 테스트하는 코드입니다. 



