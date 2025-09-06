output "jenkins_url" {
  value       = "http://${aws_instance.jenkins.public_ip}:8080"
  description = "Open in your browser"
}

output "ssh_command" {
  value       = "ssh -i ${var.key_name}.pem ubuntu@${aws_instance.jenkins.public_ip}"
  description = "Use your actual PEM path if different"
}



output "bucket_name" {
  value       = aws_s3_bucket.artifacts.bucket
  description = "Artifacts bucket (private)"
}