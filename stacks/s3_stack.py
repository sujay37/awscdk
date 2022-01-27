from aws_cdk import (
    aws_s3 as s3,
    aws_ssm as ssm,
    core
) 
from enum import Enum
import yaml

# Importing data from config.yaml file to data
with open("config.yaml", "r") as config:
    data = yaml.load(config, Loader=yaml.FullLoader)

# Converting from string to enum
class Build(Enum):
    def __str__(self):
        return self.value

    artifact_access_control = data['s3_stack']['artifacts_bucket']['access_control']
    artifact_encryption = data['s3_stack']['artifacts_bucket']['encryption']
    artifact_removal_policy = data['s3_stack']['artifacts_bucket']['removal_policy']

class S3Stack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        prj_name = self.node.try_get_context("project_name")
        env_name = self.node.try_get_context("env")

        account_id = core.Aws.ACCOUNT_ID

        artifacts_bucket = s3.Bucket(self, data['s3_stack']['artifacts_bucket']['idName']+'-'+env_name,
            access_control=eval(f's3.BucketAccessControl.{Build.artifact_access_control}'),
            encryption=eval(f's3.BucketEncryption.{Build.artifact_encryption}'),
            bucket_name=account_id+'-'+env_name+data['s3_stack']['artifacts_bucket']['bucket_name']+'-'+env_name,
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=True,
                block_public_policy=True,
                ignore_public_acls=True,
                restrict_public_buckets=True
            ),
            removal_policy=eval(f'core.RemovalPolicy.{Build.artifact_removal_policy}')
        )
        
        core.CfnOutput(self,data['s3_stack']['cfnOutput']['idName'],
            value=artifacts_bucket.bucket_name,
            export_name=data['s3_stack']['cfnOutput']['export_name']+'-'+env_name
        )
