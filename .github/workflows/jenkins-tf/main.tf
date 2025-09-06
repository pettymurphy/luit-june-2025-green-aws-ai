# Default VPC + subnets
data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default_all" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# Canonical Ubuntu 22.04 (Jammy)
data "aws_ami" "ubuntu_2204" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Unique artifacts bucket name
locals {
  bucket_name = "${var.project}-artifacts-${replace(lower(uuid()), "-", "")}"
}

# Security Group: restrict 22/8080 to allowed_cidrs
resource "aws_security_group" "jenkins_sg" {
  name        = "${var.project}-sg"
  description = "Allow SSH and Jenkins from allowed CIDRs"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidrs
  }

  ingress {
    description = "Jenkins UI"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidrs
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.project}-sg"
    Environment = "dev"
    Role        = "jenkins"
  }
}

# Private S3 bucket for artifacts
resource "aws_s3_bucket" "artifacts" {
  bucket = local.bucket_name
  tags = {
    Name        = "${var.project}-artifacts"
    Environment = "dev"
  }
}

resource "aws_s3_bucket_public_access_block" "artifacts_pab" {
  bucket                  = aws_s3_bucket.artifacts.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "artifacts_own" {
  bucket = aws_s3_bucket.artifacts.id
  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

# Jenkins install script
locals {
  jenkins_user_data = <<-EOF
    #!/bin/bash
    set -euxo pipefail
    export DEBIAN_FRONTEND=noninteractive
    apt-get update -y
    apt-get install -y openjdk-17-jdk curl gnupg
    curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key | tee /usr/share/keyrings/jenkins-keyring.asc >/dev/null
    echo "deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/" | tee /etc/apt/sources.list.d/jenkins.list >/dev/null
    apt-get update -y
    apt-get install -y jenkins
    systemctl enable --now jenkins
  EOF
}

# EC2 instance
resource "aws_instance" "jenkins" {
  ami                         = data.aws_ami.ubuntu_2204.id
  instance_type               = var.instance_type
  subnet_id                   = element(data.aws_subnets.default_all.ids, 0)
  associate_public_ip_address = true
  vpc_security_group_ids      = [aws_security_group.jenkins_sg.id]
  key_name                    = var.key_name
  user_data                   = local.jenkins_user_data

  tags = {
    Name        = var.project
    Environment = "dev"
    Role        = "jenkins-controller"
  }

  lifecycle {
    create_before_destroy = true
  }
}