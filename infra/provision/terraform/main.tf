provider "aws" {
  region = "eu-west-1"
}

resource "aws_eks_cluster" "agenticarchitect" {
  name     = "agenticarchitect-cluster"
  role_arn = aws_iam_role.eks.arn
  vpc_config {
    subnet_ids = [aws_subnet.main.id]
  }
}

resource "aws_iam_role" "eks" {
  name = "eks-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
      }
    ]
  })
}

output "kubeconfig" {
  value = "aws eks --region eu-west-1 update-kubeconfig --name agenticarchitect-cluster"
}
