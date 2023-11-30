# Prj: "Deploy your Flask application to Kubernetes using EKS"

## Prerequisites
- Docker Desktop - Installation instructions for all OSes can be found <a href="https://docs.docker.com/install/" target="_blank">here</a>.
- Git: <a href="https://git-scm.com/downloads" target="_blank">Download and install Git</a> for your system.
- Code editor: You can <a href="https://code.visualstudio.com/download" target="_blank">download and install VS code</a> here.
- AWS Account
- Python version from 3.7 to 3.9. Check the current version using:
```bash
#  Mac/Linux/Windows
python --version
```
You can download a specific release version from <a href="https://www.python.org/downloads/" target="_blank">here</a>.

* Python package manager - PIP 19.x or higher. PIP is already installed in Python 3 >=3.4 downloaded from python.org . However, you can upgrade to a specific version, say 20.2.3, using the command:
```bash
#  Mac/Linux/Windows Check the current version
pip --version

# Mac/Linux
pip install --upgrade pip==20.2.3

# Windows
python -m pip install --upgrade pip==20.2.3
```
- Terminal
   - Mac/Linux users can use the default terminal.
   - Windows users can use the GitBash or WSL terminal.
- Command line utilities:
  - The AWS CLI is install and configure using the `aws configure` command. Another important configuration is the region. Do not use the us-east-1 because the cluster creation may fails mostly in us-east-1. Let's change the default region to:
  ```bash
  aws configure set region us-east-2
  ```
  Make sure to create all your resources in a single area.
  - EKSCTL installed in your system. Follow the instructions [available here](https://docs.aws.amazon.com/eks/latest/userguide/eksctl.html#installing-eksctl) or <a href="https://eksctl.io/introduction/#installation" target="_blank">here</a> to download and install `eksctl` utility.
  - The KUBECTL installed in your system. Installation instructions for kubectl can be found <a href="https://kubernetes.io/docs/tasks/tools/install-kubectl/" target="_blank">here</a>.

## Installation
### Install AWS CLI
```bash
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /
```
Reference: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

### AWS Configure
```bash
aws configure
export AWS_CONFIG_FILE=~/.aws/config
export AWS_SHARED_CREDENTIALS_FILE=~/.aws/credentials
```

### Install Eksctl
```bash
brew tap weaveworks/tap
brew install weaveworks/tap/eksctl
```

### Install Kubectl
```bash
brew install kubectl
```

### Monitoring Kubernetes Cluster
```bash
brew install k9s
```

### Install packages
```bash
pip install -r requirements.txt
```

## Build Application
### Run locally
```bash
python main.py
```

Request method `GET`:
```bash
curl --request GET 'http://localhost:8080/contents' -H "Authorization: Bearer ${TOKEN}" | jq .
```

### Run Pytest
```bash
pytest test_main.py --disable-pytest-warnings
```

### Build Docker Image
```bash
docker build -t token-flask-app .
```

### Run Docker Container
```bash
docker run --detach --publish 80:8080 --env-file=.env_file token-flask-app
```

### Push Docker Image to Docker Hub
```bash
docker tag token-flask-app:latest vnk8071/token-flask-app:latest
docker push vnk8071/token-flask-app:latest
```

## Deploy Application to Kubernetes Cluster
### Create EKS Cluster
```bash
eksctl create cluster --name eksctl-demo-flask-token --nodes=2 --instance-types=t2.medium --region=us-east-1
```


Get cluster information:
```bash
kubectl get nodes
```

### Get current AWS account
```bash
aws sts get-caller-identity --query Account --output text
```
Result: `993324276116`

### Create IAM Role and attach policy
```bash
aws iam create-role --role-name UdacityFlaskDeployCBKubectlRole --assume-role-policy-document file://trust.json --output text --query 'Role.Arn'
```

Result: `arn:aws:iam::993324276116:role/UdacityFlaskDeployCBKubectlRole`

```bash
aws iam put-role-policy --role-name UdacityFlaskDeployCBKubectlRole --policy-name eks-describe --policy-document file://iam-role-policy.json
```

### Create Kubernetes ConfigMap
```bash
kubectl get -n kube-system configmap/aws-auth -o yaml > /tmp/aws-auth-patch.yml
kubectl patch configmap/aws-auth -n kube-system --patch "$(cat /tmp/aws-auth-patch.yml)"
```

Result: `configmap/aws-auth patched`

### Get GitHub Access Token
In GitHub, go to Settings > Developer settings > Personal access tokens > Generate new token

### Create CloudFormation Stack
* Modify `ci-cd-codepipeline.cfn.yaml` file.
* Review the resources.
* Create stack.

### Create CodePipeline
Details in `buildspec.yml` file

### Test Endpoint
```bash
kubectl get services simple-jwt-api -o wide
```

### Delete CloudFormation Stack
```bash
aws cloudformation delete-stack --stack-name <stack-name>
```

### Delete EKS Cluster
```bash
eksctl delete cluster --name <eksname> --region=us-east-1
```

URL: http://a03a1577fc7684874a3d313df1b1e3f5-257712390.us-east-1.elb.amazonaws.com/
