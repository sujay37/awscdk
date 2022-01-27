## Deploy EKS environment with applications using the aws cdk

### Prerequisites
- aws-cdk 1.116.0
- python 3.6


### Deploy

```bash
$ npm install -g aws-cdk
$ pip install -r requirements.txt    # Best to do this in a virtualenv
$ cdk diff                           # View proposed changes
$ cdk deploy --all                        # Deploys the CloudFormation template

# Cleanup
$ cdk destroy
```




