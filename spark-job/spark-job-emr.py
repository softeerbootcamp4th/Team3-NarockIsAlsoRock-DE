from pyspark import SparkConf
from pyspark.sql import SparkSession, Row
from pyspark.sql.functions import isnull, avg, min, date_format
from pyspark.sql.functions import pandas_udf, PandasUDFType
import pyspark.sql.functions as F
import pyspark.pandas as ps
import numpy as np
import datetime
from pyspark.sql.types import StructType, StructField, IntegerType, FloatType, DoubleType

ps.set_option('compute.ops_on_diff_frames', True)

# from S3, to S3 (To be updated)
POSTS_FP = "s3://de3-extract-results/clien_posts.csv"  # 크롤링 결과 파일 위치 
COMMENT_FP = "s3://de3-extract-results/clien_comments.csv"  # 크롤링 결과 파일 위치
MODEL_FP = "s3://de3-extract-results/model_result.csv" # from RedShift
OUTPUT_FP = "s3://de3-extract-results/transform_output"  # to RedShift


def find_hot_criteria(row, model_df):
    condition = ((model_df['post_type']==1) \
        & (model_df['relative_time']==row.relatvie_time) \
        & (model_df['cumulative_num']==row.comments))
    hot_pdf_value = model_df[condition].pdf.values[0]
    return hot_pdf_value


def find_cold_criteria(row, model_df):
    condition = ((model_df['post_type']==0) \
        & (model_df['relative_time']==row.relatvie_time) \
        & (model_df['cumulative_num']==row.comments))
    hot_pdf_value = model_df[condition].pdf.values[0]
    return hot_pdf_value


def predict_post_type(post_df, model_df):    
    per_post_hot_probability = post_df.apply(lambda x: find_hot_criteria(x, model_df), axis=1)
    per_post_cold_probability = post_df.apply(lambda x: find_cold_criteria(x, model_df), axis=1)
    post_df['impact'] = np.log(per_post_hot_probability/per_post_cold_probability)
    post_df['post_type'] = 0
    post_df.loc[post_df['impact'] > 0, 'post_type'] = 1
    return post_df


def parse_date(date_str):
    return ps.to_datetime(date_str, errors="coerce")

if __name__ == "__main__":
    spark = SparkSession.builder \
        .master("local[*]") \
        .appName('spark-job') \
        .config('spark.executor.memory', '4gb') \
        .config("spark.executor.cores", "4") \
        .getOrCreate()
        
    post_df = spark.read.option("header", True).option("quote", "\"").option("escape", "\"").option("multiline", "true").option("sep", ",").csv(POST_FP, sep=',',).to_pandas_on_spark()
    comment_df = spark.read.option("header", True).option("quote", "\"").option("multiline", "true").csv(COMMENT_FP, sep=',').to_pandas_on_spark() 
    model_df = spark.read.option("header", True).csv(MODEL_FP, sep=',').to_pandas_on_spark()

    # collected_at = datetime.datetime.now().replace(second=0, microsecond=0)
    collected_at = ps.to_datetime('2023-10-31 00:00:52').replace(second=0, microsecond=0) # from S3 (crawling)
    if collected_at.minute >= 30:
        collected_at = collected_at.replace(minute=30)
    else:
        collected_at = collected_at.replace(minute=00)
        
    
    # preprocessing
    post_df['created_at'] = post_df['created_at'].apply(parse_date)
    comment_df.columns = ['cmt_author', 'cmt_count', 'post_id', 'cmt_created_at']     
    comment_df['cmt_created_at'] = comment_df['cmt_created_at'].apply(parse_date)
    model_df['pdf'] = model_df['pdf'].astype(float)
    model_df['cumulative_num'] = model_df['cumulative_num'].astype(int)
    model_df['post_type'] = model_df['post_type'].astype(int)
    
    # filtering 
    cutoff_time = collected_at - datetime.timedelta(hours=35)
    post_df = post_df[post_df['created_at'] > cutoff_time]
    comment_df = comment_df[comment_df['cmt_created_at'] > cutoff_time]

    # To be deleted (below)
    post_df = post_df[post_df['created_at'] <= collected_at] 
    comment_df = comment_df[comment_df['cmt_created_at'] <= collected_at]
    
    
    df = ps.merge(post_df, comment_df, left_on='id', right_on='post_id', how='left')

    time_interval = 5 * 60 # seconds 
    df['relative_time'] = ((df['cmt_created_at'] - df['created_at']) // time_interval) * 5
    
    df_group_by_post_id = df.groupby('id').agg({'cmt_author': 'count'}).rename(columns={'cmt_author': 'comments'})
    df_group_by_post_id = df_group_by_post_id.reset_index()
    
    post_df = ps.merge(post_df, df_group_by_post_id, left_on='id', right_on='id', how='inner')
    post_df['relatvie_time'] =  ((collected_at - df['created_at']) // time_interval) * 5
    
    model_df['pdf'] = model_df['pdf'].astype(float)
    model_df['cumulative_num'] = model_df['cumulative_num'].astype(int)
    model_df['relative_time'] = model_df['relative_time'].astype(int)
    model_df['post_type'] = model_df['post_type'].astype(int)

    post_df = predict_post_type(post_df, model_df)
    
    post_df['sns_id'] = 0
    post_df['collected_at'] = collected_at
    
    batch_id = int(collected_at.strftime('%Y%m%d%H%M'))
    post_df['batch_id'] = batch_id
    post_df.rename(columns={'id': 'post_id'}, inplace = True) 
    
    post_df.to_csv(OUTPUT_FP, header=True)