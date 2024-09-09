resource "aws_lb" "enc-sandbox-alb" {
  name                       = "enc-sandbox-alb"
  internal                   = true
  load_balancer_type         = "application"
  security_groups            = [aws_security_group.private-vpc-SG.id]
  subnets                    = ["subnet-004f2a9bae9ca2cd0", "subnet-012f337a7cf91bae7", "subnet-09bacf4a8ce850044"] 
  enable_deletion_protection = true

  depends_on = [aws_security_group.private-vpc-SG]

  tags = {
    Name = "enc-sandbox-alb"
  }
}

resource "aws_lb_listener" "https_listener" {
  load_balancer_arn = aws_lb.enc-sandbox-alb.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = "arn:aws:acm:us-east-1:767397798793:certificate/59b06792-6faf-4102-a7cb-7143b2d1501a" 

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.enc-targetgroup.arn
  }

  depends_on = [aws_lb.enc-sandbox-alb, aws_lb_target_group.enc-targetgroup]
}


resource "aws_lb_target_group" "enc-targetgroup" {
  name        = "enc-sandbox-tg"
  port        = 443
  protocol    = "HTTPS"
  target_type = "ip"
  vpc_id      = "vpc-0c0d44f06ee02cd3e"
  health_check {
    path                = "/healthcheck"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 3
    unhealthy_threshold = 2
    matcher             = "200"
  }

  depends_on = [aws_lb.enc-sandbox-alb]
}


resource "aws_lb_target_group_attachment" "target1" {
  target_group_arn = aws_lb_target_group.enc-targetgroup.arn
  target_id        = "10.237.55.206"
  port             = 443
}

resource "aws_lb_target_group_attachment" "target2" {
  target_group_arn = aws_lb_target_group.enc-targetgroup.arn
  target_id        = "10.237.55.23"
  port             = 443
}

resource "aws_lb_target_group_attachment" "target3" {
  target_group_arn = aws_lb_target_group.enc-targetgroup.arn
  target_id        = "10.237.55.218"
  port             = 443
}