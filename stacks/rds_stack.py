from aws_cdk import (
    core
)
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_iam as iam
import aws_cdk.aws_rds as rds
import aws_cdk.aws_secretsmanager as secrets
from enum import Enum
import yaml

# Importing data from config.yaml file to data
with open("config.yaml", "r") as config:
    data = yaml.load(config, Loader=yaml.FullLoader)

# Converting from string to enum
class InstanceType(Enum):
    def __str__(self):
        return self.value

    CLASS = data['rds_stack']['database_Cluster']['instance_props']['instance_type']['class']
    SIZE = data['rds_stack']['database_Cluster']['instance_props']['instance_type']['size']

class RDSStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, vpc: ec2.Vpc, **kwargs) -> None:
 
        super().__init__(scope, construct_id, **kwargs)

        cluster = rds.DatabaseCluster(self, data['rds_stack']['database_Cluster']['type'],
                                      engine=rds.DatabaseClusterEngine.aurora_postgres(
                                          version=eval(data['rds_stack']['database_Cluster']['version'])),
                                      # credentials=rds.Credentials.from_generated_secret("syscdk"),
                                      # Optional - wsill default to 'admin' username and generated password
                                      instance_props={
                                          # optional , defaults to t3.medium
                                          "instance_type": ec2.InstanceType.of(eval(f'ec2.InstanceClass.{InstanceType.CLASS}'),
                                                                               eval(f'ec2.InstanceSize.{InstanceType.SIZE}')),
                                          "vpc_subnets": {
                                              "subnet_type": ec2.SubnetType.PRIVATE
                                          },
                                          "vpc": vpc
                                      }
                                      )

