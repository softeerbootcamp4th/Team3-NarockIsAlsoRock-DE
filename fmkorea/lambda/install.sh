aws ecr get-login-password --region ap-northeast-2 --profile default | docker login --username AWS --password-stdin 571495482396.dkr.ecr.ap-northeast-2.amazonaws.com
docker build --platform linux/amd64 -t softeer .
docker tag softeer:latest 571495482396.dkr.ecr.ap-northeast-2.amazonaws.com/softeer:latest
docker push 571495482396.dkr.ecr.ap-northeast-2.amazonaws.com/softeer:latest