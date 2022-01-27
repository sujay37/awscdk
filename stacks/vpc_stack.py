from aws_cdk import (
    aws_ec2 as ec2,
    aws_ssm as ssm,
    core
)
import yaml

# Importing data from config.yaml file to data
with open("config.yaml", "r") as config:
    data = yaml.load(config, Loader=yaml.FullLoader)


class VPCStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.vpc = ec2.Vpc(self, (''.join(data['vpc_stack']['vpc_type'])),
                           cidr='10.50.0.0/16',
                           max_azs=2,
                           enable_dns_hostnames=True,
                           enable_dns_support=True,
                           subnet_configuration=[
                               ec2.SubnetConfiguration(
                                   name=(''.join(data['vpc_stack']['vpc_subnetConfig']['public_name'])),
                                   subnet_type=ec2.SubnetType.PUBLIC,
                                   cidr_mask=26
                               ),
                               ec2.SubnetConfiguration(
                                   name=(''.join(data['vpc_stack']['vpc_subnetConfig']['private_name'])),
                                   subnet_type=ec2.SubnetType.PRIVATE,
                                   cidr_mask=26
                               )
                           ],
                           nat_gateways=1,

                           )
