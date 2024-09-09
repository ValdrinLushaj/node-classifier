
resource "aws_security_group" "private-vpc-SG" {
  name        = "private-vpc-SG"
  description = "Security group allowing ports 443 from everywhere"
  vpc_id      = "vpc-0c0d44f06ee02cd3e"

  ingress {
    description = "Allow HTTPS from anywhere"
    from_port   = 443
    to_port     = 443
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

resource "aws_vpc_endpoint" "enc-vpc-endpoint" {
  vpc_id              = "vpc-0c0d44f06ee02cd3e"
  service_name        = "com.amazonaws.us-east-1.execute-api"
  vpc_endpoint_type   = "Interface"
  private_dns_enabled = true
   subnet_configuration {
    ipv4      = "10.237.55.206"
    subnet_id = "subnet-004f2a9bae9ca2cd0"
  }
  subnet_configuration {
    ipv4      = "10.237.55.23"
    subnet_id = "subnet-012f337a7cf91bae7"
  }
  subnet_configuration {
    ipv4      = "10.237.55.218"
    subnet_id = "subnet-09bacf4a8ce850044"
  }
  
  security_group_ids = [aws_security_group.private-vpc-SG.id]
  tags = {
    Name = "node-classifier-vpc-endpoint"
  }

  subnet_ids = [
    "subnet-004f2a9bae9ca2cd0", "subnet-012f337a7cf91bae7", "subnet-09bacf4a8ce850044"
  ]
}
