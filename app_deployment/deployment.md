# Application Deployment

Once the AWS infrastructure foundation was in place, I moved on to deploying the application itself on the EC2 instance.

At this point, the VPC, subnets, routing, security groups, S3 bucket, IAM role, RDS PostgreSQL instance, and EC2 instance were already created. This document focuses only on the application deployment work performed after that infrastructure was ready.

## Deployment Approach

The application is a small Python Flask application. I deployed it to the existing EC2 instance and connected it to the PostgreSQL database running on Amazon RDS.

The application also uses the existing S3 bucket for file uploads. The EC2 instance already has the `cloudops-ec2-s3-role` IAM role attached, so the application can access S3 without storing AWS access keys on the server.

The deployment flow is:

```text
Internet
   |
   v
EC2 / Nginx
   |
   v
Gunicorn / Flask application
   |
   +------> RDS PostgreSQL
   |
   +------> Amazon S3
```

## Application Files

I copied the application code to the EC2 instance under:

```text
/home/ubuntu/app
```

The application contains the Flask code, database connection logic, HTML template, and Python dependency definition.

I kept the AWS deployment environment separate from my local development environment. In particular, the RDS connection details and other environment-specific values were configured directly on the EC2 host rather than copying the local `.env` file.

## Python Environment

The EC2 instance was running Ubuntu 24.04 LTS with Python 3.12.

I created a Python virtual environment inside the application directory and installed the dependencies from `requirements.txt`.

The main dependencies are:

- Flask
- boto3
- psycopg2-binary
- python-dotenv
- gunicorn

Using a virtual environment keeps the application's Python dependencies isolated from the system Python installation.

## Connecting the Application to RDS

After the application was copied to EC2, I configured its environment to point to the private RDS endpoint.

The application uses:

```text
DB_HOST=<RDS endpoint>
DB_PORT=5432
DB_NAME=cloudops
DB_USER=cloudopsadmin
DB_PASSWORD=<private password>
```

The database password is intentionally not included in this documentation.

Before starting the application, I verified network connectivity from EC2 to RDS using a TCP connection test on port `5432`.

I then tested the application's database connection directly through its database connection function. The connection succeeded.

The orders table was also created in the RDS database so that the deployed application could use the same basic data model as the local application.

The important point here is that RDS remained private. The application reached it from EC2 over the VPC rather than exposing PostgreSQL to the Internet.

## Connecting the Application to S3

The application was configured to use:

```text
S3_BUCKET=cloudops-bucket-01
AWS_REGION=us-east-1
```

No AWS access key or secret access key was placed in the application configuration.

The EC2 instance uses the existing `cloudops-ec2-s3-role`, which provides the permissions required by the application to work with the project bucket.

I verified the integration by uploading a test file through the application and then confirming that the object appeared in the S3 bucket using the AWS CLI.

This confirmed both the application-side S3 integration and the IAM role-based access.

## Running the Application

I first ran Gunicorn manually on the EC2 instance to verify that the Flask application could start successfully:

```bash
gunicorn --bind 127.0.0.1:8000 app:app
```

I then tested the application locally on the EC2 host with:

```bash
curl http://127.0.0.1:8000/health
```

The health endpoint returned a healthy response, confirming that Gunicorn was serving the Flask application.

## Nginx

After confirming that Gunicorn was working, I placed Nginx in front of the application.

Nginx listens on port `80` and forwards incoming requests to Gunicorn on:

```text
127.0.0.1:8000
```

This means the application process itself does not need to listen directly on the public interface.

I validated the Nginx configuration with:

```bash
sudo nginx -t
```

The configuration test succeeded, and Nginx was restarted successfully.

At this point, opening the EC2 public address in a browser displayed the application dashboard.

### Application Running on EC2

![Application dashboard running on EC2](app_running_on_aws.PNG)

## Running the Application as a Service

The final deployment step was to remove the dependency on a manually running Gunicorn process.

I created a systemd service for the application:

```text
/etc/systemd/system/cloudops.service
```

The service runs Gunicorn with two workers and restarts automatically if the application process exits.

The service was then enabled so that it starts automatically when the EC2 instance boots.

I verified that the service was active and that the application remained accessible through Nginx.

This gave me a more realistic server deployment rather than leaving the application dependent on an interactive SSH session.

## Deployment Verification

The deployed application was verified at several levels:

- Flask health endpoint responded successfully.
- PostgreSQL on RDS was connected successfully.
- The application reported S3 as available.
- The application dashboard was accessible through the EC2 public address.
- A test file uploaded through the application appeared in the S3 bucket.
- An order was created through the application API.
- The order was retrieved successfully from RDS through the application.
- The application continued running after Gunicorn was moved from a manual process to systemd.

The final deployed flow was therefore:

```text
Browser
   |
   v
EC2 public interface :80
   |
   v
Nginx
   |
   v
Gunicorn :8000
   |
   +------------------> RDS PostgreSQL :5432
   |
   +------------------> S3 via EC2 IAM role
```

### Deployment Evidence

The following screenshots provide supporting evidence for the deployment and integration steps.

**Application service running under systemd**

![Application systemd deployment](app_systemd_deployment.PNG)

**Application and RDS integration**

![Application RDS integration verification](app_rds_integration_verified.PNG)

**Order API and database verification**

![Order API and RDS verification](app_rds_order_api_verified.PNG)

**S3 upload and object verification**

![S3 upload selected](s3_upload_selected.PNG)

![S3 upload successful](s3_upload_success.PNG)

![S3 object verified using AWS CLI](s3_cli_object_verified.PNG)

No credentials, private keys, or database passwords are included in the screenshots or documentation.