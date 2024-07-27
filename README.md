# End to End MLOps Project

A project that starts from data preprocessing to the monitoring of the deployed model(s). A detailed breakdown of what is entailed in this data can be found in this [post](https://medium.com/@midegageorge2/predictive-model-development-maximizing-ifoods-marketing-campaign-profitability-by-targeting-95fe1ae79478). However, in this project, the data has been split into four parts which may lead to the difference in results observed in the article. There is a notebook detailing how the four datasets were created in the `data` folder.

## Environment Preparation

The following installations will be based on your operating system. Just click the link to visit the official documentation page on how to install them.

1. [Anaconda](https://docs.anaconda.com/anaconda/install/)
2. [Docker Engine](https://docs.docker.com/engine/install/)
3. (Optional if running on Ubuntu distribution)[Docker Compose](https://docs.docker.com/compose/install/)
4. (Optional) Ubuntu distribution
5. [Terraform](https://developer.hashicorp.com/terraform/install)

Create, activate, and deactivate a conda environment with Python version 3.9.16. Make sure to run the commands one at a time

```bash
conda create -n ifood_mlops python=3.9.16
conda activate ifood_mlops
conda deactivate
```
Install the required packages

```bash
pip install -r requirements.txt
```

## Experiment Tracking using MLFLOW

### Configuring AWS

Since the model artifacts are going to be stored in S3 buckets, we will have to configure our AWS through the Identity and Access Management (IAM) services. Instructions for doing that can be found [here](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html). We'll then use the generated access key id and the secret access key to configure it locally. The second command is to check if everything is okay.

```bash
aws configure
ls ~/.aws
```

For this project, I will create a new AWS profile (`demiga-g`) different from the default one. 

- First approach involves using the command and filling in the required entries :

```bash
aws configure --profile demiga-g
```

- Second way is by editing the `credentials` file. 

```bash
nano ~/.aws/credentials
nano ~/.aws/config
```

### Using Terraform to Manage AWS Resources

Terraform is used to manage the aws infrastructure which in this case will include the EC2 instance, S3 bucket, and Relational Database Services (PostgreSQL). These configuration are saved in the `main.tf` and `variables.tf` files and some of the important commands to run the file include the following:

```bash
terraform init
terraform fmt
terraform validate
```

### Accessing the Remote Machine Locally

To access a Linux-based EC2 instance via SSH, you’ll need an SSH key pair. For that, run the following commands to generate a new SSH key pair:

```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/mlops-ete-key-pair
```
This will create a public and private key using the `RSA` algorithm with 4096 bits and store them in the `.ssh` folder in the `home` directory.

Now you can run the following command to create the needed resources in AWS

```bash
terraform apply
```

The EC2 instance is then connected to the local machine using the command below. Note that the public ip address changes when the instance is terminated. And for this project we use the Amazon Linux given that it has Python installed thus saving me some trouble of installing it. 

```bash
ssh -i ~/.ssh/mlops-ete-key-pair  ec2-user@54.197.95.246
```
To simplify this process on every subsequent connections, we can create a configuration file using the command:

```bash
nano ~/.ssh/config
```
With the file opened, copy the following snippet and modify as necessary. 

```bash
Host mlops-ete
    HostName 16.171.136.194
    User ec2-user
    IdentityFile /home/midega-g/.ssh/mlops-ete-key-pair
    StrictHostKeyChecking no
```
That is:

- `Host` is your preferred host name
- `User` is `user` if your created an instance with aws or `ubuntu` if you used ubuntu. Note that every time you  terminate the instance, you'll have to change the value here too.
- `IdentityFile` is the full path to the key pair
- `StrictHostKeyChecking` set to `no` ensures that we are not frequently asked if we trust the key.

With these set, we can now run (remember to change the name based on what you used):

```bash
ssh mlops-ete
```
Once in the remote machine, run the following commands to update the machine and install the necessary packages and libraries for use:

```bash
sudo yum update && sudo yum upgrade -y
sudo yum install python3-pip -y
pip3 install mlflow boto3 psycopg2-binary --use-feature=2020-resolver
```
Installing docker in Amazon Linux 2

```bash
sudo yum update && sudo yum upgrade -y
sudo amazon-linux-extras install docker
sudo service docker start
sudo usermod -a -G docker ec2-user
newgrp docker
docker ps
```

It is also important to run `aws configure` to configure the aws credentials in the remote machine just like we did in the local machine and import it as shown below:

```bash
aws configure export-credentials --profile demiga-g
```

To logout of the the EC2 instance use `logout` command.

To delete these resource, you can either run the first command to remove all of them at a go, or the second command to remove one, or the third to remove more than one:

```bash
terraform destroy
terraform destroy -target aws_db_instance.postgresql_db_ete_mlops
```

### Running MLFlow Remotely

With everything configured, we run the following command to get mlflow server up. 

- Remember to replace the values in the in the bracket with the relevant entries

```bash
mlflow server \
	-h 0.0.0.0 \
	-p 5000 \
	--backend-store-uri postgresql://<DB_USER>:<DB_PASSWORD>@<DB_ENDPOINT>:<DB_PORT>/<DB_NAME> \
	--default-artifact-root s3://midega-mlflow-artifacts
```
This would look like this:

```bash
mlflow server \
	-h 0.0.0.0 \
	-p 5000 \
	--backend-store-uri postgresql://postgres:password@ifood-artifacts.c7g4iwo6ky4f.eu-north-1.rds.amazonaws.com:5432/mlflow_ifood_db \
	--default-artifact-root s3://midega-mlflow-artifacts
```

To access the MLFlow tracking serve in the browser or local machine, you can use the EC2 instance IP address and then append the port number. Something like this:

```bash
16.171.136.194:5000
```

Running the server locally but storing the artifacts in S3 bucket:

```bash
mlflow server \
	--backend-store-uri sqlite:///mlflow_runs.db \
	--default-artifact-root s3://midega-mlflow-artifacts
```

### Tracking the Models

Five machine learning models were used to find a suitable binary classifier with high precision score. Apparently, the scores were low and ranging between 0.16 to 0.22.  



## Deployment

Creating a virtual environment with only the packages required to run the deployed model in a web-service.

```bash
pipenv install scikit-learn==1.0.2 fastapi --python=3.9
```

### Batch Deployment

```bash
python 03_batch_deployment.py \
	--input_data_path='../data/val_df2.csv' \
	--experiment_id=6 \
	--run_id='45a3990ff1e140afbe48334a8422bec7' \
	--output_data_path='../data/predictions.csv'
```


```bash
docker build -t customer_response:v1 .
docker run -v ~/.aws:/root/.aws \
	-it \ 
	--rm \
	--name ifood_response \
	-p 9696:9696  \
	customer_response:v1
```

Pushing Docker image to Docker Hub

```bash
docker tag customer_response:v1 midega/ifood-response-classifier
docker login -u "midega" -p "<your password>" docker.io
docker push midega/ifood-response-classifier
```
terraform state rm aws_ecs_cluster.ecs_cluster_ete_mlops aws_ecs_service.ifood_response_api aws_ecs_task_definition.ecs_task_ete_mlops

CMD-SHELL,curl-f http://localhost/||exit 1

```bash
python -m http.server
```

Check linting issues and fix them where necessary

```bash
pylint --recursive=y .
black --diff . | less
black .
isort --diff . | less
isort .
```

Create new branch and checkout to it

```bash
git checkout -b ci-cd-branch
```

### Setup GitHub Secrets

```bash
Settings > Secrets and variables > Actions > New repository secret
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=
AWS_ECR_LOGIN_URI=
ECR_REPOSITORY_NAME=
```

### Configuring EC2 as Self-hosted Runner (Alternative to ECS)

```bash
Settings > Actions > Runners > New self--hosted runner > Runner image (Linux)
```
Run the commands provided in EC2 instance since this project is run on AmazonLinux2 you may need to install shasum:

```bash
sudo yum install perl-Digest-SHA
```
During configuration, the name of the runner (second command request) should be `self-hosted` with the rest remaining as default.


Open pull request from base `develop` and compare it to `ci-cd-branch` created earlier.

