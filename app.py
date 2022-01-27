#!/usr/bin/env python3
from aws_cdk import core

from stacks.vpc_stack import VPCStack
from stacks.rds_stack import RDSStack
from stacks.eks_stack import EKSStack
#from stacks.lambda_stack import Lambda_stack
from stacks.s3_stack import S3Stack
from stacks.codepipeline_backend import CodePipelineBackendStack

import yaml
import json

# Importing data from config.yaml file to data
with open("config.yaml", "r") as config, open("cdk.json", "w") as jsonConfig:
    data = yaml.load(config, Loader=yaml.FullLoader)
    json.dump(data['json'], jsonConfig)

app = core.App()
vpc_stack_name = ''.join(data['app']['vpc_stack'])
vpc_stack = VPCStack(app, vpc_stack_name)

eks_stack_name = ''.join(data['app']['eks_stack'])
eks_stack = EKSStack(app, eks_stack_name, vpc=vpc_stack.vpc)

rds_stack_name = ''.join(data['app']['rds_stack'])
rds_stack = RDSStack(app, rds_stack_name, vpc=vpc_stack.vpc)

s3_stack_name = ''.join(data['app']['s3_stack'])
s3_stack = S3Stack(app, s3_stack_name)

codepipeline_backend_name = ''.join(data['app']['codepipeline_backend']['name'])
codepipeline_backend = CodePipelineBackendStack(app, codepipeline_backend_name,
                                                artifactbucket=core.Fn.import_value(data['app']['codepipeline_backend']['artifact_bucket_name']))

app.synth()
