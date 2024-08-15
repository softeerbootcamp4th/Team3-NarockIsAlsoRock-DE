from pyspark import SparkConf
from pyspark.sql import SparkSession, Row
from pyspark.sql.functions import isnull, avg, min, date_format
from pyspark.sql.functions import pandas_udf, PandasUDFType
from pyspark.sql.types import DoubleType, StructField
import pyspark.sql.functions as F
import pyspark.pandas as ps

ps.set_option('compute.ops_on_diff_frames', True)

POSTS_FP = "s3://de3-extract-results/naver_cafe_posts.csv"  # 크롤링 결과 파일 위치
VIEW_TABLE_DIR = "s3://softter-de3-quicksight/"  # 대시보드에서 사용하는 directory 위치


def make_full_range_date(df):
    date_min = df.agg({'created_day': 'min'})[0]
    date_max = df.agg({'created_day': 'max'})[0]
    full_date_df = ps.date_range(start=date_min, end=date_max, freq='D', name='date').to_frame()
    return full_date_df


if __name__ == "__main__":
    spark = SparkSession.builder \
        .appName('spark-job') \
        .config('spark.executor.memory', '4gb') \
        .config("spark.executor.cores", "5") \
        .getOrCreate()

    posts_df = spark.read.option("header", True).csv(POSTS_FP)

    # Datetime formatting
    posts_df = posts_df.withColumn("created_day", F.to_date(posts_df["created_at"], "yyyy-MM-dd HH:mm:ss"))
    posts_df = posts_df.fillna(0)

    # Calc Per day total likes, views and count of posts.
    posts_group_by_day_df = posts_df.groupby("created_day").agg({'title': 'count', 'likes': 'sum', 'views': 'sum'})
    new_col_names = ['created_day', 'count_title', 'sum_views', 'sum_likes']
    posts_group_by_day_df = posts_group_by_day_df.toDF(*new_col_names)
    posts_group_by_day_df = posts_group_by_day_df.fillna(0)

    posts_group_by_day_df = posts_group_by_day_df.to_pandas_on_spark()
    full_range_date_df = make_full_range_date(posts_group_by_day_df)

    output_df = ps.merge(full_range_date_df, posts_group_by_day_df, left_on='date', right_on='created_day',
                         how='left').sort_values(by=['date'])

    count_title_df = output_df[['count_title']]
    output_df['count_smoothed'] = count_title_df.ewm(alpha=0.7).mean()
    output_df = output_df.sort_values('created_day')
    output_df = output_df.drop(columns=['created_day'])
    output_df.fillna(0)

    # Save Results
    output_df.to_csv(VIEW_TABLE_DIR + "dashboard_example", mode='overwrite')
    posts_df.coalesce(1).write.mode('overwrite').csv(VIEW_TABLE_DIR + "naver_cafe_posts")