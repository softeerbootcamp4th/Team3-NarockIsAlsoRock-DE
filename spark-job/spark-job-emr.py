import json
import sys

import boto3
from pyspark import SparkConf, SQLContext
from pyspark.sql import SparkSession, Row
from pyspark.sql.dataframe import DataFrame
from datetime import datetime
import pyspark.pandas as ps
import numpy as np

ps.set_option('compute.ops_on_diff_frames', True)

MAX_COMMENTS_NUM = 200
TIME_INTERVAL = 5 * 60  # seconds


def find_hot_criteria(row, model_df):
    condition = ((model_df['post_type'] == 1) \
                 & (model_df['relative_time'] == row.relatvie_time) \
                 & (model_df['cumulative_num'] == row.comments))
    # print(row.relatvie_time)
    # print(row.comments)
    hot_pdf_value = model_df[condition].pdf.values[0]
    return hot_pdf_value


def find_cold_criteria(row, model_df):
    condition = ((model_df['post_type'] == 0) \
                 & (model_df['relative_time'] == row.relatvie_time) \
                 & (model_df['cumulative_num'] == row.comments))
    # print(row.relatvie_time)
    # print(row.comments)
    hot_pdf_value = model_df[condition].pdf.values[0]
    return hot_pdf_value


def predict_post_type(post_df, model_df):
    per_post_hot_probability = post_df.apply(lambda x: find_hot_criteria(x, model_df), axis=1)
    per_post_cold_probability = post_df.apply(lambda x: find_cold_criteria(x, model_df), axis=1)
    post_df['impact'] = np.log(per_post_hot_probability / per_post_cold_probability).round(2)
    post_df['impact'] = post_df['impact'].replace(np.inf, 554.93) # set upper bound of impact 
    post_df['post_type'] = 0
    post_df.loc[post_df['impact'] > 0, 'post_type'] = 1
    return post_df


def parse_date(date_str):
    return ps.to_datetime(date_str, errors="coerce")


def get_db_credentials():
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name="ap-northeast-2",
    )
    get_secret_value_response = client.get_secret_value(
        SecretId="hmg-4th-de3-redshift-admin-credential"
    )
    secret = json.loads(get_secret_value_response['SecretString'])
    return secret['redshift_user'], secret['redshift_password']

def read_redshift(spark: SparkSession, dbtable, db_user, db_password, query=None):
    sql_context = SQLContext(spark.sparkContext)
    url = "jdbc:redshift://de3-workgroup.181252290322.ap-northeast-2.redshift-serverless.amazonaws.com:5439/dev?user=" + db_user + "&password=" + db_password
    # Access to Redshift cluster using Spark

    if query is None:
        rows = sql_context.read \
            .format("io.github.spark_redshift_community.spark.redshift") \
            .option("url", url) \
            .option("tempdir_region", "ap-northeast-2") \
            .option("dbtable", dbtable) \
            .option("tempdir", f"s3://spark-transient-emr-lambda-ap-northeast-2-181252290322/temp/data/{dbtable}") \
            .option("aws_iam_role",
                    "arn:aws:iam::181252290322:role/de3-team-project-Load-9ODBABB6O-RedshiftDefaultRole-JDX7MjpYhApU") \
            .load()
    else:
        rows = sql_context.read \
            .format("io.github.spark_redshift_community.spark.redshift") \
            .option("url", url) \
            .option("tempdir_region", "ap-northeast-2") \
            .option("tempdir", f"s3://spark-transient-emr-lambda-ap-northeast-2-181252290322/temp/data/{dbtable}") \
            .option("aws_iam_role",
                    "arn:aws:iam::181252290322:role/de3-team-project-Load-9ODBABB6O-RedshiftDefaultRole-JDX7MjpYhApU") \
            .option("query", query) \
            .load()

    return rows.to_pandas_on_spark()


def write_redshift(df: DataFrame, dbtable, db_user, db_password):
    url = "jdbc:redshift://de3-workgroup.181252290322.ap-northeast-2.redshift-serverless.amazonaws.com:5439/dev?user=" + db_user + "&password=" + db_password
    # Save results
    if dbtable=="view":
        (df.write
         .format("io.github.spark_redshift_community.spark.redshift")
         .option("url", url)
         .option("dbtable", dbtable)
         .option("tempdir", f"s3://spark-transient-emr-lambda-ap-northeast-2-181252290322/temp/data/{dbtable}")
         .option("tempformat", "CSV")
         .option("aws_iam_role","arn:aws:iam::181252290322:role/de3-team-project-Load-9ODBABB6O-RedshiftDefaultRole-JDX7MjpYhApU")
         .mode("overwrite")
         .save())

    else:
        (df.write
         .format("io.github.spark_redshift_community.spark.redshift")
         .option("url", url)
         .option("dbtable", dbtable)
         .option("tempdir", f"s3://spark-transient-emr-lambda-ap-northeast-2-181252290322/temp/data/{dbtable}")
         .option("tempformat", "CSV")
         .option("aws_iam_role","arn:aws:iam::181252290322:role/de3-team-project-Load-9ODBABB6O-RedshiftDefaultRole-JDX7MjpYhApU")
         .mode("append")
         .save())
    return

if __name__ == "__main__":
    batch_id = sys.argv[1]
    collected_at = datetime.strptime(batch_id, '%Y%m%d%H%M')
    # TODO: make merge all extracted posts and comments
    string_collected_at = collected_at.strftime("%Y-%m-%d")
    POST_FP = f"s3://de3-extract/bobae/{string_collected_at}/posts/{batch_id}.csv"  # 크롤링 결과 파일 위치
    COMMENT_FP = f"s3://de3-extract/bobae/{string_collected_at}/comments/{batch_id}.csv"  # 크롤링 결과 파일 위치

    spark = SparkSession.builder \
        .appName('transform') \
        .enableHiveSupport() \
        .getOrCreate()

    post_df = (spark.read
            .option("header", True)
            .option("quote", "\"")
            .option("escape", "\"")
            .option("multiline", "true")
            .option("sep", ",")
            .csv(POST_FP, sep=',')
            .to_pandas_on_spark())
    comment_df = (spark.read
                .option("header", True)
                .option("quote", "\"")
                .option("multiline", "true")
                .csv(COMMENT_FP, sep=',')
                .to_pandas_on_spark())

    db_user, db_password = get_db_credentials()
    model_df = read_redshift(spark, "model", db_user, db_password)

    # preprocessing
    post_df['created_at'] = post_df['created_at'].apply(parse_date)
    comment_df['cmt_created_at'] = comment_df['cmt_created_at'].apply(parse_date)
    model_df['pdf'] = model_df['pdf'].astype(float)
    model_df['cumulative_num'] = model_df['cumulative_num'].astype(int)


    model_df['post_type'] = model_df['post_type'].astype(int)

    # get number of comments per post
    number_of_comment_per_post_df = comment_df[['post_id', 'cmt_author']].groupby(['post_id']).agg(
        {'cmt_author': 'count'}).rename(columns={'cmt_author': 'comments'})
    number_of_comment_per_post_df = number_of_comment_per_post_df.reset_index()
    number_of_comment_per_post_df.loc[number_of_comment_per_post_df['comments'] > MAX_COMMENTS_NUM] = MAX_COMMENTS_NUM

    # collected_at = ps.to_datetime('2023-10-31 00:00:52').replace(second=0, microsecond=0)  # from S3 (crawling)
    # cutoff_time = collected_at - datetime.timedelta(hours=12)
    # post_df = post_df[post_df['created_at'] > cutoff_time]
    # comment_df = comment_df[comment_df['cmt_created_at'] > cutoff_time]
    # post_df = post_df[post_df['created_at'] <= collected_at]
    # comment_df = comment_df[comment_df['cmt_created_at'] <= collected_at]

    # Add columns to classify the type of post.
    post_df = ps.merge(post_df, number_of_comment_per_post_df, left_on='id', right_on='post_id', how='left')
    post_df['comments'] = post_df['comments'].fillna(0)


    post_df = post_df.drop(columns=['id', 'updated_at'])
    post_df['relatvie_time'] = ((collected_at - post_df['created_at']) // TIME_INTERVAL) * 5
    post_df = predict_post_type(post_df, model_df)
    post_df['sns_id'] = 0  # TODO: use sns_id from input data. (to be deleted)
    post_df['collected_at'] = collected_at
    post_df['batch_id'] = int(batch_id)
    post_df['likes'] = post_df['likes'].astype(int)
    post_df['views'] = post_df['views'].astype(int)


    # # Save result
    # write_redshift(post_df.to_spark(), 'post', db_user, db_password)

    # # Update view table
    # query = """
    # WITH ranked_posts AS (
    #     SELECT *,
    #         ROW_NUMBER() OVER (PARTITION BY post_id ORDER BY batch_id DESC) AS rn
    #     FROM post
    #     WHERE created_at >= DATEADD('month', -1, CURRENT_DATE)
    # )
    # SELECT *
    # FROM ranked_posts
    # WHERE rn = 1
    # """
    # view_df = read_redshift(spark, "post", db_user, db_password, query)
    # write_redshift(view_df, 'view', db_user, db_password)
