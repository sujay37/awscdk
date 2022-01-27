from aws_cdk import (
    aws_codepipeline as cp,
    aws_codepipeline_actions as cp_actions,
    aws_codebuild as cb,
    aws_s3 as s3,
    aws_secretsmanager as sm,
    aws_iam as iam,
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

    build_project_image = data['codepipeline_backend']['build_project']['env_build_image']

class CodePipelineBackendStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, artifactbucket, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        prj_name = self.node.try_get_context("project_name")
        env_name = self.node.try_get_context("env")

        artifact_bucket = s3.Bucket.from_bucket_name(self,data['codepipeline_backend']['artifact_bucket'], artifactbucket)

        github_token = core.SecretValue.secrets_manager(
            env_name+'/'+data['codepipeline_backend']['github_token'], json_field=data['codepipeline_backend']['github_token']
        )

        build_project=cb.PipelineProject(self,data['codepipeline_backend']['build_project']['idName'],
            project_name=data['codepipeline_backend']['build_project']['project_name'],
            description=data['codepipeline_backend']['build_project']['description'],
            environment=cb.BuildEnvironment(
                build_image=eval(f'cb.LinuxBuildImage.{Build.build_project_image}'),
                privileged=True,
                environment_variables={
                    'AWS_DEFAULT_REGION': cb.BuildEnvironmentVariable(value=data['codepipeline_backend']['build_project']['enviornment_variables']['AWS_DEFAULT_REGION']),
                    'AWS_CLUSTER_NAME': cb.BuildEnvironmentVariable(value=data['codepipeline_backend']['build_project']['enviornment_variables']['AWS_CLUSTER_NAME']),
                    'AWS_ACCOUNT_ID': cb.BuildEnvironmentVariable(value=data['codepipeline_backend']['build_project']['enviornment_variables']['AWS_ACCOUNT_ID']),
                    'IMAGE_REPO_NAME': cb.BuildEnvironmentVariable(value=data['codepipeline_backend']['build_project']['enviornment_variables']['IMAGE_REPO_NAME']),
                    'IMAGE_TAG': cb.BuildEnvironmentVariable(value=data['codepipeline_backend']['build_project']['enviornment_variables']['IMAGE_TAG'])
                }
            ),
            cache=cb.Cache.bucket(artifact_bucket, prefix=data['codepipeline_backend']['build_project']['cache_prefix']),
            build_spec=cb.BuildSpec.from_object({
                'version': '0.2',
                'phases': {
                    'install':{
                        'commands': [
                            'curl -o kubectl https://amazon-eks.s3.us-west-2.amazonaws.com/1.18.9/2020-11-02/bin/linux/amd64/kubectl',
                             'chmod +x ./kubectl',
                             'mkdir -p $HOME/bin && cp ./kubectl $HOME/bin/kubectl && export PATH=$PATH:$HOME/bin',
                             "echo 'export PATH=$PATH:$HOME/bin' >> ~/.bashrc",
                             'source ~/.bashrc',
                             "echo 'Check kubectl version'",
                             'kubectl version --short --client',
                             'aws eks --region $AWS_DEFAULT_REGION update-kubeconfig --name $AWS_CLUSTER_NAME',
                             'kubectl get po',
                             'aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com',
                             'docker build -t $IMAGE_REPO_NAME .',
                             'docker tag $IMAGE_REPO_NAME:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:latest',
                             'docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:latest',
                             'kubectl apply -f eks_cicd/deployment.yaml',
                             'kubectl rollout restart -f eks_cicd/deployment.yaml'
                        ]
                        }        
                    }
            })    

         
        )

        pipeline = cp.Pipeline(self, data['codepipeline_backend']['pipeline']+'-'+env_name,
            pipeline_name=env_name+'-'+prj_name+'-'+data['codepipeline_backend']['pipeline']+'-'+env_name,
            artifact_bucket=artifact_bucket,
            restart_execution_on_update=True
        )

        source_output = cp.Artifact(artifact_name="source")
        build_output = cp.Artifact(artifact_name="build")

        pipeline.add_stage(stage_name='Source',actions=[
            cp_actions.GitHubSourceAction(
                oauth_token=github_token,
                output=source_output,
                repo=data['codepipeline_backend']['pipeline_stage_Source']['repo'],
                branch=data['codepipeline_backend']['pipeline_stage_Source']['branch'],
                owner=data['codepipeline_backend']['pipeline_stage_Source']['owner'],
                action_name=data['codepipeline_backend']['pipeline_stage_Source']['action_name']
            )
        ])
        pipeline.add_stage(stage_name='Build', actions=[
            cp_actions.CodeBuildAction(
                action_name='Build',
                input=source_output,
                project=build_project,
                outputs=[build_output]
            )
        ])
       
        build_project.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(data['codepipeline_backend']['build_project_role_name'])
        )

        