from pyspark.sql import SparkSession

# 1. Spark 세션 생성
spark = SparkSession.builder \
    .appName("CSV to Parquet") \
    .config("spark.hadoop.fs.s3a.access.key", "AKIASUM32O4JGGSJIKFX") \
    .config("spark.hadoop.fs.s3a.secret.key", "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") \
    .config("spark.hadoop.fs.s3a.endpoint", "s3.ap-northeast-2.amazonaws.com") \
    .getOrCreate()

# 2. S3에서 CSV 파일 로드
csv_file_path = "s3://wh-src-bucket-test/naver_cafe_posts.csv"
df = spark.read.csv(csv_file_path, header=True, inferSchema=True)

# 3. DataFrame을 Parquet 형식으로 변환
parquet_file_path = "s3://wh-dest-bucket-test/naver_cafe_posts.parquet"
df.write.parquet(parquet_file_path, mode="overwrite")

# 4. Spark 세션 종료
spark.stop()


