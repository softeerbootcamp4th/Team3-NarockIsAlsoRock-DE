"""
Copy paste the following code in your Lambda function. Make sure to change the following key parameters for the API as per your account

-Name (Name of Spark cluster)
-LogUri (S3 bucket to store EMR logs)
-Ec2SubnetId (The subnet to launch the cluster into)
-JobFlowRole (Service role for EC2)
-ServiceRole (Service role for Amazon EMR)

The following parameters are additional parameters for the Spark job itself. Change the bucket name and prefix for the Spark job (located at the bottom).

-s3://your-bucket-name/prefix/lambda-emr/SparkProfitCalc.jar (Spark jar file)
-s3://your-bucket-name/prefix/fake_sales_data.csv (Input data file in S3)
-s3://your-bucket-name/prefix/outputs/report_1/ (Output location in S3)
"""
import os

import boto3

client = boto3.client('emr')


def lambda_handler(event, context):
    service_role = os.environ['ServiceRole']
    job_flow_role = os.environ['JobFlowRole']
    ec2_subnet_id = os.environ['Ec2SubnetId']
    s3_bucket = os.environ['S3Bucket']
    script_path = event.get('script_path', None)
    script_args = event.get('script_args', [])

    if script_path is None:
        return {
            'msg' : "script path is none"
        }
    # PySpark 스크립트 위치 (S3 경로)
    script_location = f's3://{s3_bucket}/{script_path}'

    response = client.run_job_flow(
        Name='transformer',
        LogUri=f's3://{s3_bucket}/prefix/logs',
        ReleaseLabel='emr-7.2.0',
        Instances={
            'MasterInstanceType': 'm4.large',
            'SlaveInstanceType': 'm4.large',
            'InstanceCount': 2,
            'KeepJobFlowAliveWhenNoSteps': False,
            'TerminationProtected': False,
            'Ec2SubnetId': ec2_subnet_id
        },
        Applications=[{'Name': 'Spark'}],
        Configurations=[
            {'Classification': 'spark-hive-site',
             'Properties': {
                 'hive.metastore.client.factory.class': 'com.amazonaws.glue.catalog.metastore.AWSGlueDataCatalogHiveClientFactory'}
             }
        ],
        VisibleToAllUsers=True,
        JobFlowRole=job_flow_role,
        ServiceRole=service_role,
        Steps=[
            {
                'Name': 'transform',
                'ActionOnFailure': 'TERMINATE_CLUSTER',
                'HadoopJarStep': {
                    'Jar': 'command-runner.jar',
                    'Args': [
                                'spark-submit',
                                '--deploy-mode', 'cluster',
                                script_location
                            ] + script_args
                }
            }
        ]
    )