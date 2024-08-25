# Spark Job
> Serverless EMR에서 수행하는 script에 대한 정보를 제공합니다.   
> 최종적으로, spark-job-emr-optimized.py를 사용합니다.  

## Role
- 30분마다 실행되는 Extract step의 결과물은 AWS S3에 저장된다.
- Serverless EMR에서 수행하는 과정은 아래와 같다.
    1. S3에서 크롤링 결과를 읽어온다.
    2. Redshift(model table)에서 모델 정보를 읽어온다. 
    3. 각 게시물 별 relative time 정보와 누적 댓글 수 정보를 기반으로, 모델을 활용하여 impact 값과 post type 정보를 추가한다.
    4. 모든 정보를 Redshift(post table)에 적재한다. 

## Simple Diagram
<img width="1002" alt="image" src="https://github.com/user-attachments/assets/000bde3e-0bd7-445b-8d5d-5956e0489b4b">

## Optimization
- 적절한 caching과 broadcast join을 수행하도록 하기 위한 [hint](https://spark.apache.org/docs/latest/api/python/reference/pyspark.pandas/api/pyspark.pandas.DataFrame.spark.hint.html)를 제공하여 transform 과정이 효율적으로 진행될 수 있도록 하였다.
    - 그 결과, 약 6분 정도가 소요되었던 기존의 transform 과정을 1.7분으로 줄일 수 있었다.
- Before Optimization
<img width="1728" alt="before-optimization" src="https://github.com/user-attachments/assets/5c610b99-b3b6-491e-8c9e-ce70d2cc695b">

- After Optimization
<img width="1728" alt="after-optimization" src="https://github.com/user-attachments/assets/87ce32a4-6492-43ac-9d8e-386dcc3c2c05">