S3 Integration

After the S3 bucket and EC2 IAM role were already configured, I connected the Flask application to the bucket and verified that the application could upload objects without using AWS access keys.

This document focuses on the application-side S3 integration. The bucket configuration and IAM policy are documented separately under architecture/.

Application configuration

On the EC2 instance, the application was configured with:

S3_BUCKET=cloudops-bucket-01
AWS_REGION=us-east-1

The bucket name is provided through the environment rather than being embedded directly in the application configuration.

The application uses boto3 to communicate with Amazon S3.

IAM-based authentication

I did not configure an AWS access key or secret access key on the EC2 server.

The EC2 instance uses the existing:

cloudops-ec2-s3-role

IAM role.

Because the role is attached to the instance, boto3 can obtain temporary AWS credentials automatically through the EC2 environment.

This keeps long-lived AWS credentials out of the application and server configuration.

The role was intentionally created with only the S3 permissions required by this application.

Verify AWS CLI access

Before testing the Flask application, I verified that the EC2 instance could access the project bucket through its IAM role.

I used:

aws s3 ls s3://cloudops-bucket-01/

The command successfully returned the contents of the bucket.

This confirmed that the EC2 instance was receiving usable temporary credentials through its IAM role.

Application upload test

After confirming CLI access, I tested the S3 integration through the application itself.

I selected a small test file through the application's upload interface and submitted it.

The application returned:

{"filename":"s3_upload_test.txt","message":"File uploaded successfully"}

This confirmed that the Flask application was able to send the file to S3 using boto3 and the EC2 instance role.

Verify the uploaded object

I then verified the object independently using the AWS CLI:

aws s3 ls s3://cloudops-bucket-01/

The uploaded object appeared in the bucket:

2026-09-13 01:32:56         18 s3_upload_test.txt

This provided a second point of verification outside the application UI.

The complete flow was therefore:

Browser
   |
   v
Flask application
   |
   v
boto3
   |
   v
EC2 IAM role
   |
   v
Amazon S3
cloudops-bucket-01

What this verified

The test confirmed several things at once:

The application could read its S3 configuration from the environment.

boto3 was available in the application's Python environment.

The EC2 instance could obtain temporary AWS credentials through its IAM role.

The IAM role allowed the application to upload an object to the project bucket.

The object was actually stored in S3.

The uploaded object could be independently verified using the AWS CLI.

Security considerations

The application does not require AWS access keys stored in .env.

The S3 bucket remains private, and application access is provided through the EC2 IAM role.

The project also has S3 Versioning enabled, which will be useful later when demonstrating recovery from an object-level change or deletion.

No AWS credentials, database passwords, or private SSH keys are included in this documentation or in the deployment screenshots.