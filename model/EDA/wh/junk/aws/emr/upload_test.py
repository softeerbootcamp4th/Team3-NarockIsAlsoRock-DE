from pyspark.sql import SparkSession

# 1. Spark 세션 생성
spark = SparkSession.builder \
    .appName("CSV to Parquet") \
    .config("spark.hadoop.fs.s3a.access.key", "") \
    .config("spark.hadoop.fs.s3a.secret.key", "") \
    .config("spark.hadoop.fs.s3a.endpoint", "") \
    .getOrCreate()

# 2. 데이터 생성 (예: DataFrame)
data = [("Alice", 1), ("Bob", 2), ("Cathy", 3)]
columns = ["Name", "Value"]

# DataFrame 생성
df = spark.createDataFrame(data, columns)

# 3. S3에 Parquet 파일로 저장
parquet_file_path = "s3://wh-dest-bucket-test/sample_data.parquet"
df.write.parquet(parquet_file_path, mode="overwrite")

# 4. Spark 세션 종료
spark.stop()
