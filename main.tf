terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}


# configure the aws provider
provider "aws" {
  region  = "us-east-1"
  profile = "demiga-g"
}


# read the public key file
resource "tls_private_key" "ssh_private_key" {
  algorithm = "RSA"
  rsa_bits  = 4096
}


# create a key pair with the public key
resource "aws_key_pair" "deployer" {
  key_name   = "mlops-ete-key-pair"
  public_key = file("~/.ssh/mlops-ete-key-pair.pub")
}


# security group for EC2 SSH and custom TCP
resource "aws_security_group" "ec2_instance_security_group" {
  name        = "instance_security_group"
  description = "Allow SSH and custom TCP traffic"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}


# ec2 instance configuration
resource "aws_instance" "instance_ete_mlops" {
  ami             = "ami-06c68f701d8090592"
  instance_type   = "t2.micro"
  key_name        = aws_key_pair.deployer.key_name
  security_groups = [aws_security_group.ec2_instance_security_group.name]

  root_block_device {
    volume_size = 25
    volume_type = "gp3"
  }

  tags = {
    Name = "mlflow-mlops"
  }
}


# s3 bucket configuration
resource "aws_s3_bucket" "bucket_ete_mlops" {
  bucket = "midega-mlflow-artifacts"
  force_destroy = true
}


# postgresql security group
resource "aws_security_group" "postgres_security_group" {
  name        = "rds_security_group"
  description = "Allow traffic from the EC2 instance"

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ec2_instance_security_group.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}


# retrieving the default VPC
data "aws_vpc" "default" {
  filter {
    name   = "isDefault"
    values = ["true"]
  }
}

# retrieving the default security group within the default vpc
data "aws_security_group" "default" {
  vpc_id = data.aws_vpc.default.id
  filter {
    name   = "group-name"
    values = ["default"]
  }
}

# add ingress rule to the default security group that allows postgresql
# to run in the remote machine
resource "aws_security_group_rule" "allow_postgres" {
  type                     = "ingress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  security_group_id        = data.aws_security_group.default.id
  source_security_group_id = aws_security_group.ec2_instance_security_group.id
}

# postgres database configuration
resource "aws_db_instance" "postgresql_db_ete_mlops" {

  db_name                 = "mlflow_ifood_db"
  username                = "postgres"
  identifier              = "ifood-artifacts"
  password                = "password"
  port                    = 5432
  allocated_storage       = 20
  storage_type            = "gp2"
  engine                  = "postgres"
  engine_version          = "16.3"
  instance_class          = "db.t3.micro"
  parameter_group_name    = "default.postgres16" # change according to your engine version
  skip_final_snapshot     = true
  publicly_accessible     = false
  backup_retention_period = 1


  tags = {
    Name = "db-instance"
  }
}

## uncomment to create custome s3 bucket policy if needed
# # IAM policy
# resource "aws_iam_policy" "s3_bucket_policies" {
#   name        = "S3BucketPolicy"
#   description = "Policy to allow specific S3 bucket action"
#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Action = [
#           "s3:CreateBucket",
#           "s3:ListBucket",
#           "s3:GetObject",
#           "s3:PutObject"
#         ]
#         Effect = "Allow"
#         Resource = [
#           "arn:aws:s3:::${aws_s3_bucket.bucket_ete_mlops.bucket}",
#           "arn:aws:s3:::${aws_s3_bucket.bucket_ete_mlops.bucket}/*"
#         ]
#       }
#     ]
#   })
# }

# # IAM role
# resource "aws_iam_role" "MlopsEteAccess" {
#   name = "mlops-ete-role"
#   assume_role_policy = jsonencode(
#     {
#       Version = "2012-10-17"
#       Statement = [
#         {
#           Effect = "Allow"
#           Action = "sts:AssumeRole"
#           Principal = {
#             Service = "ec2.amazonaws.com"
#           }
#         },
#       ]

#     }
#   )
# }

# # attaching policy to role
# resource "aws_iam_role_policy_attachment" "mlops_role_policy_attach" {
#   role       = aws_iam_role.MlopsEteAccess.name
#   policy_arn = aws_iam_policy.s3_bucket_policies.arn
# }