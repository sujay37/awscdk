from aws_cdk import (
    aws_lambda as _lambda,
    aws_apigateway as _apigateway,
    core
)

import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_iam as iam
import aws_cdk.aws_eks as eks
import aws_cdk.aws_ecr as ecr
import aws_cdk.aws_codebuild as codebuild
import aws_cdk.aws_elasticloadbalancingv2 as elbv2
import aws_cdk.aws_apigatewayv2 as apigt2

import requests
import yaml

# import js_yaml as yaml
# import sync_request as request

# Importing data from config.yaml file to data
with open("config.yaml", "r") as config:
    data = yaml.load(config, Loader=yaml.FullLoader)

class EKSStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, vpc: ec2.Vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        eks_role = iam.Role(self, data['eks_stack']['eks_role']['type'],
                            assumed_by=iam.ServicePrincipal(service='eks.amazonaws.com'),
                            role_name=data['eks_stack']['eks_role']['name'],
                            managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name(
                                managed_policy_name=data['eks_stack']['eks_role']['managed_policy_name'])])

        nodegroup_role = iam.Role(self, data['eks_stack']['nodegroup_role']['type'],
                                  assumed_by=iam.ServicePrincipal(service='ec2.amazonaws.com'),
                                  role_name=data['eks_stack']['nodegroup_role']['name'],
                                  managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name(
                                      managed_policy_name=data['eks_stack']['nodegroup_role']['managed_policy_name'])])

        eks_instance_profile = iam.CfnInstanceProfile(self, data['eks_stack']['eks_instance_profile']['type'],
                                                      roles=[eks_role.role_name],
                                                      instance_profile_name=data['eks_stack']['eks_instance_profile']['name'])

        cluster = eks.Cluster(self, ( ''.join(data['eks_stack']['cluster']['type'])),
                                        
                              cluster_name=data['eks_stack']['cluster']['name'],
                              version=eval(data['eks_stack']['cluster']['version']),
                              vpc=vpc,
                              default_capacity_instance=ec2.InstanceType(data['eks_stack']['cluster']['ec2.instanceType']),
                              default_capacity=data['eks_stack']['cluster']['default_capacity'],
                              # masters_role=eks_role
                              )

        nodegroup = cluster.add_nodegroup_capacity((''.join(data['eks_stack']['nodeGroup']['name'])),
                    
                                                   instance_type=ec2.InstanceType(data['eks_stack']['cluster']['ec2.instanceType']),
                                                   disk_size=data['eks_stack']['nodeGroup']['disk_size'],
                                                   min_size=data['eks_stack']['nodeGroup']['min_size'],
                                                   nodegroup_name=(''.join(data['eks_stack']['nodeGroup']['name'])),
                                        
                                                   # node_role=nodegroup_role
                                                   )

        nsing = yaml.load(open("./ingress/ingressnamespace1.yaml"), Loader=yaml.FullLoader)
        cluster.add_manifest("naing", nsing)

        nsflu = yaml.load(open("./ingress/fluentbitnamespace.yaml"), Loader=yaml.FullLoader)
        cluster.add_manifest("nsflu", nsflu)

        # asg = cluster.add_auto_scaling_group_capacity((''.join(data['eks_stack']['asg.auto_scaling_group_capacity']['type'])),
        #                                               
        #                                               instance_type=ec2.InstanceType(data['eks_stack']['cluster']['ec2.instanceType']),
        #                                               min_capacity=data['eks_stack']['asg.auto_scaling_group_capacity']['min_capacity'],
        #                                               max_capacity=data['eks_stack']['asg.auto_scaling_group_capacity']['max_capacity'],
        #                                               desired_capacity=data['eks_stack']['asg.auto_scaling_group_capacity']['desired_capacity']
        #                                               )

        tml1 = yaml.load_all(open("./ingress/servicedeployment.yaml"), Loader=yaml.Loader)
        servicedeployment = ["deployment", "service"]
        for temp3, temp4 in zip(tml1, servicedeployment):
            cluster.add_manifest(temp4, temp3)

        ingservice = yaml.load(open("./ingress/ingresservice.yaml"), Loader=yaml.FullLoader)
        cluster.add_manifest("ingservice", ingservice)

        tml = yaml.load_all(open("./ingress/ingress.yaml"), Loader=yaml.Loader)
        ingress = ["ing2", "ing3", "ing4", "ing5", "ing6", "ing7", "ing8", "ing9", "ing10", "ing11", "ing12", "ing13","ing14", "ing15", "ing16", "ing17", "ing18"]
        for temp1, temp2 in zip(tml, ingress):
            cluster.add_manifest(temp2, temp1)

        fluent = yaml.load_all(open("./ingress/fluentbit.yaml"), Loader=yaml.Loader)
        fluentbit = ["flu2", "flu3", "flu4", "flu5", "flu6", "flu7", "flu8", "flu9", "flu10", "flu11"]
        for fluentnew, fluentnew1 in zip(fluent, fluentbit):
            cluster.add_manifest(fluentnew1, fluentnew)

        my_lambda = _lambda.Function(self, id='lambdafunction',
                                     runtime=_lambda.Runtime.PYTHON_3_8,
                                     handler='authorizer.lambda_handler',
                                     code=_lambda.Code.asset('lambdacode'),
                                     environment={
                                         # 'x-api-key': 'staging',
                                         'cognito_api': (''.join(data['eks_stack']['my_lambda_environment_cognito_api'][0]))
                                                         
                                     }
                                     )

        api_with_method = _apigateway.LambdaRestApi(self, id='restapi',
                                                    rest_api_name=data['eks_stack']['api_with_method_LambdaRestApi']['rest_api_name'],
                                                    handler=my_lambda)
#        authorizer = api_with_method.root.add_resource('authorizer')
#        authorizer.add_method('GET')
#        authorizer.add_method("DELETE", _apigateway.HttpIntegration("http://aws.amazon.com"))
