provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "portfolio" {
  bucket = "gemini-designs-portfolio-2026-v2"
  
  tags = {
    Name        = "Gemini Designs Portfolio"
    Description = "Consolidated bucket for all design projects"
  }
}

resource "aws_s3_bucket_public_access_block" "portfolio" {
  bucket = aws_s3_bucket.portfolio.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "public_read" {
  bucket = aws_s3_bucket.portfolio.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.portfolio.arn}/*"
      }
    ]
  })
}

resource "aws_s3_bucket_website_configuration" "portfolio" {
  bucket = aws_s3_bucket.portfolio.id

  index_document {
    suffix = "index.html"
  }
}

# The build script must be run before terraform apply
# This syncs the local dist folder to S3
resource "null_resource" "sync_dist" {
  triggers = {
    # Run sync on every apply to ensure dist is uploaded
    always_run = timestamp()
  }

  provisioner "local-exec" {
    command = "aws s3 sync ../dist/ s3://${aws_s3_bucket.portfolio.bucket} --delete"
  }
}

output "portfolio_url" {
  value = "http://${aws_s3_bucket_website_configuration.portfolio.website_endpoint}"
}
