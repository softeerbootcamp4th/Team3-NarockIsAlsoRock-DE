import json
import sys
import boto3
import numpy as np

from pyspark import SparkConf, SQLContext
from datetime import datetime
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.types import IntegerType, FloatType

MAX_COMMENTS_NUM = 200
TIME_INTERVAL = 5 * 60  # seconds


def predict_post_type(post_df, model_df):
    post_df = post_df.withColumnRenamed(
        "relative_time", "post_relative_time"
    ).withColumnRenamed("comments", "post_comments")

    model_df_hot = (
        model_df.filter(F.col("post_type") == 1)
        .withColumnRenamed("relative_time", "model_relative_time")
        .withColumnRenamed("cumulative_num", "model_cumulative_num")
        .withColumnRenamed("pdf", "hot_pdf")
    ).drop("post_type", "index")

    model_df_cold = (
        model_df.filter(F.col("post_type") == 0)
        .withColumnRenamed("relative_time", "model_relative_time_cold")
        .withColumnRenamed("cumulative_num", "model_cumulative_num_cold")
        .withColumnRenamed("pdf", "cold_pdf")
    ).drop("post_type")

    hot_join = post_df.join(
        model_df_hot,
        (post_df["post_relative_time"] == model_df_hot["model_relative_time"])
        & (post_df["post_comments"] == model_df_hot["model_cumulative_num"]),
        how="left",
    )

    cold_join = hot_join.join(
        model_df_cold,
        (hot_join["post_relative_time"] == model_df_cold["model_relative_time_cold"])
        & (hot_join["post_comments"] == model_df_cold["model_cumulative_num_cold"]),
        how="left",
    )

    result_df = cold_join.withColumn(
        "impact", F.round(F.log(F.col("hot_pdf") / F.col("cold_pdf")), 2)
    ).withColumn("post_type", F.when(F.col("impact") > 0, 1).otherwise(0))

    result_df = result_df.drop(
        "model_relative_time",
        "model_cumulative_num",
        "model_relative_time_cold",
        "model_cumulative_num_cold",
    )

    return result_df


def get_db_credentials():
    session = boto3.session.Session()
    client = session.client(
        service_name="secretsmanager",
        region_name="ap-northeast-2",
    )
    get_secret_value_response = client.get_secret_value(
        SecretId="hmg-4th-de3-redshift-admin-credential"
    )
    secret = json.loads(get_secret_value_response["SecretString"])
    return secret["redshift_user"], secret["redshift_password"]


def read_redshift(spark: SparkSession, dbtable, db_user, db_password, query=None):
    sql_context = SQLContext(spark.sparkContext)
    url = (
        "jdbc:redshift://de3-workgroup.181252290322.ap-northeast-2.redshift-serverless.amazonaws.com:5439/dev?user="
        + db_user
        + "&password="
        + db_password
    )
    # Access to Redshift cluster using Spark

    if query is None:
        rows = (
            sql_context.read.format("io.github.spark_redshift_community.spark.redshift")
            .option("url", url)
            .option("tempdir_region", "ap-northeast-2")
            .option("dbtable", dbtable)
            .option(
                "tempdir",
                f"s3://spark-transient-emr-lambda-ap-northeast-2-181252290322/temp/data/{dbtable}",
            )
            .option(
                "aws_iam_role",
                "arn:aws:iam::181252290322:role/de3-team-project-Load-9ODBABB6O-RedshiftDefaultRole-JDX7MjpYhApU",
            )
            .load()
        )
    else:
        rows = (
            sql_context.read.format("io.github.spark_redshift_community.spark.redshift")
            .option("url", url)
            .option("tempdir_region", "ap-northeast-2")
            .option(
                "tempdir",
                f"s3://spark-transient-emr-lambda-ap-northeast-2-181252290322/temp/data/{dbtable}",
            )
            .option(
                "aws_iam_role",
                "arn:aws:iam::181252290322:role/de3-team-project-Load-9ODBABB6O-RedshiftDefaultRole-JDX7MjpYhApU",
            )
            .option("query", query)
            .load()
        )

    return rows


def write_redshift(df: DataFrame, dbtable, db_user, db_password):
    url = (
        "jdbc:redshift://de3-workgroup.181252290322.ap-northeast-2.redshift-serverless.amazonaws.com:5439/dev?user="
        + db_user
        + "&password="
        + db_password
    )
    # Save results
    (
        df.write.format("io.github.spark_redshift_community.spark.redshift")
        .option("url", url)
        .option("dbtable", dbtable)
        .option(
            "tempdir",
            f"s3://spark-transient-emr-lambda-ap-northeast-2-181252290322/temp/data/{dbtable}",
        )
        .option("tempformat", "CSV")
        .option(
            "aws_iam_role",
            "arn:aws:iam::181252290322:role/de3-team-project-Load-9ODBABB6O-RedshiftDefaultRole-JDX7MjpYhApU",
        )
        .mode("append")
        .save()
    )
    return


if __name__ == "__main__":
    batch_id = "202408261530"
    collected_at = datetime.strptime(batch_id, "%Y%m%d%H%M")
    string_collected_at = collected_at.strftime("%Y-%m-%d")
    POST_FP = f"s3://de3-extract/bobae/{string_collected_at}/posts/{batch_id}.csv"  # 크롤링 결과 파일 위치
    COMMENT_FP = f"s3://de3-extract/bobae/{string_collected_at}/comments/{batch_id}.csv"  # 크롤링 결과 파일 위치

    spark = SparkSession.builder.appName("transform").enableHiveSupport().getOrCreate()

    post_df = (
        spark.read.option("header", True)
        .option("quote", '"')
        .option("escape", '"')
        .option("multiline", "true")
        .option("sep", ",")
        .csv(POST_FP, sep=",")
    )
    comment_df = (
        spark.read.option("header", True)
        .option("quote", '"')
        .option("multiline", "true")
        .csv(COMMENT_FP, sep=",")
    )

    db_user, db_password = get_db_credentials()
    model_df = read_redshift(spark, "model", db_user, db_password)

    # preprocessing
    post_df = post_df.withColumn("created_at", F.to_timestamp("created_at"))
    comment_df = comment_df.withColumn(
        "cmt_created_at", F.to_timestamp("cmt_created_at")
    )
    model_df = (
        model_df.withColumn("pdf", F.col("pdf").cast(FloatType()))
        .withColumn("cumulative_num", F.col("cumulative_num").cast(IntegerType()))
        .withColumn("post_type", F.col("post_type").cast(IntegerType()))
    )
    model_df = model_df.cache()

    # get number of comments per post
    number_of_comment_per_post_df = comment_df.groupBy("post_id").agg(
        F.count("cmt_author").alias("comments")
    )
    number_of_comment_per_post_df = number_of_comment_per_post_df.withColumn(
        "comments",
        F.when(F.col("comments") > MAX_COMMENTS_NUM, MAX_COMMENTS_NUM).otherwise(
            F.col("comments")
        ),
    )

    # Add columns to classify the type of post.
    post_df = post_df.join(
        F.broadcast(number_of_comment_per_post_df),
        post_df["id"] == number_of_comment_per_post_df["post_id"],
        how="left",
    ).drop("id", "updated_at", "content", "index")

    post_df = post_df.fillna({"comments": 0})
    post_df = post_df.cache()

    post_df = post_df.withColumn(
        "relative_time",
        ((F.lit(collected_at) - F.col("created_at")) / F.lit(TIME_INTERVAL)).cast(
            IntegerType()
        )
        * 5,
    ).filter(F.col("relative_time") >= 0)

    post_df = predict_post_type(post_df, model_df)

    post_df = post_df.withColumn("sns_id", F.lit(0))
    post_df = post_df.withColumn("collected_at", F.lit(collected_at))
    post_df = post_df.withColumn("batch_id", F.lit(int(batch_id)))

    post_df = post_df.withColumn(
        "likes", F.regexp_replace("likes", ",", "").cast(IntegerType())
    )
    post_df = post_df.withColumn(
        "views", F.regexp_replace("views", ",", "").cast(IntegerType())
    )

    # Save result
    write_redshift(post_df, "post", db_user, db_password)
