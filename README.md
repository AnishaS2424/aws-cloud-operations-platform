# AWS Cloud Operations Platform

A hands-on AWS cloud operations project focused on infrastructure setup, application deployment, monitoring, security, and infrastructure troubleshooting.

The project demonstrates how a Python web application can be deployed on AWS, connected to a managed PostgreSQL database, integrated with Amazon S3, and monitored to investigate and resolve operational issues.

## Project Overview

This project was built to practise real-world cloud operations workflows, including provisioning AWS resources, configuring secure network access, deploying an application, monitoring infrastructure health, and documenting incidents from diagnosis through resolution.

Rather than focusing only on deploying an application, the project explores the operational responsibilities involved in keeping a cloud-hosted application accessible, connected to its dependencies, and functioning correctly.

### Key Objectives

- Provision AWS infrastructure using the AWS Management Console and AWS CLI.
- Configure networking, subnets, routing, and security groups.
- Deploy a Python Flask application on Amazon EC2.
- Connect the application to Amazon RDS for PostgreSQL.
- Integrate Amazon S3 for application file operations.
- Use IAM roles to grant application access to AWS services without storing long-term AWS credentials on the EC2 instance.
- Monitor infrastructure and application dependencies using Amazon CloudWatch.
- Investigate infrastructure and connectivity failures through documented incidents.
- Apply troubleshooting steps and verify recovery.

## Architecture

The application runs on Amazon EC2 in a public subnet. Amazon RDS for PostgreSQL is deployed in private subnets, while Amazon S3 provides object storage for application file operations.

```text
                    User
                      |
                      v
               HTTP Application
                      |
                      v
                Amazon EC2
                Flask App
                 /      \
                /        \
               v          v
       Amazon RDS       Amazon S3
       PostgreSQL       Object Storage
       Private Subnets

                EC2 IAM Role
                      |
                      v
             Temporary AWS Credentials

          Amazon CloudWatch
          Monitoring and Logs
```

The architecture separates application hosting, database storage, and object storage. Database access is controlled through security groups, and the EC2 instance uses an IAM role for authorised S3 access.

## Technology Stack

| Category | Technologies |
|---|---|
| Application | Python, Flask |
| Database | PostgreSQL, Amazon RDS |
| Object storage | Amazon S3 |
| Compute | Amazon EC2, Ubuntu Server |
| Networking | Amazon VPC, public and private subnets, Internet Gateway, route tables |
| Identity and access | AWS IAM roles and custom S3 permissions |
| Monitoring | Amazon CloudWatch |
| Application integration | Boto3 |
| Administration | AWS Management Console, AWS CLI, Linux |
| Documentation | Markdown, Git, GitHub |

## Project Structure

The repository is organised into application source code, infrastructure setup, deployment documentation, monitoring, and incident reports.

| Directory or file | Purpose |
|---|---|
| [`app/`](app/) | Python application source code and configuration |
| [`app_documentation/`](app_documentation/) | Local application development notes and screenshots |
| [`app_deployment/`](app_deployment/) | EC2 deployment, RDS connectivity, S3 integration, and deployment verification |
| [`aws_setup/`](aws_setup/) | AWS infrastructure provisioning and configuration |
| [`monitoring/`](monitoring/) | CloudWatch monitoring, metrics, logs, and dashboards |
| [`incident_01/`](incident_01/) | First documented infrastructure troubleshooting exercise |
| [`incident_02/`](incident_02/) | Second documented infrastructure troubleshooting exercise |
| [`incident_03/`](incident_03/) | Third documented infrastructure troubleshooting exercise |
| [`requirements.txt`](app/requirements.txt) | Python application dependencies |

## Application Development

The application was initially developed and tested locally before being deployed to AWS.

The Flask application includes a dashboard, health-check functionality, database connectivity checks, and order-related functionality. Boto3 is used for AWS integration.

Local development helped establish that the application and its database functionality worked before moving to cloud deployment.

**Documentation:** [Local Application Development](app_documentation/app_readme.md)

## AWS Infrastructure Setup

The infrastructure was configured to provide the application with compute, networking, storage, and database resources.

The setup includes:

- A VPC with public and private subnets.
- An Internet Gateway and route-table configuration.
- Security groups controlling application and database connectivity.
- An EC2 instance running Ubuntu Server.
- An RDS PostgreSQL database deployed in private subnets.
- An S3 bucket for application object storage.
- An IAM role with a custom policy for the application's S3 operations.

Detailed setup guides:

- [VPC Setup](aws_setup/vpc-setup.md)
- [Security Groups](aws_setup/security-groups.md)
- [EC2 Setup](aws_setup/ec2-setup.md)
- [RDS Setup](aws_setup/rds-setup.md)
- [S3 Setup](aws_setup/s3-setup.md)
- [IAM Role and S3 Access](aws_setup/iam-setup.md)

## Application Deployment and Integration

The application was deployed to EC2 and configured to run as a Linux system service. The deployment process also covers connecting the application to RDS and integrating S3.

The deployment documentation records the configuration and verification steps for the application and its dependencies.

- [Application Deployment Overview](app_deployment/deployment.md)
- [EC2 Application Setup](app_deployment/ec2-application-setup.md)
- [RDS Connection](app_deployment/rds-connection.md)
- [S3 Integration](app_deployment/s3-integration.md)

## Monitoring and Observability

Amazon CloudWatch is used to observe infrastructure behaviour and support operational troubleshooting.

The monitoring documentation covers the configured EC2 and RDS monitoring dashboards, CPU and disk-related metrics, memory utilisation, and Nginx access logs.

This monitoring information helps establish infrastructure behaviour, investigate symptoms, and verify the system after troubleshooting.

**Documentation:** [CloudWatch Monitoring](monitoring/monitoring.md)

## Infrastructure Troubleshooting and Incident Reports

A key part of this project is practising a structured troubleshooting process rather than simply recording that a service failed.

The incident reports document infrastructure troubleshooting exercises, including the observed symptoms, investigation, diagnosis, corrective action, and verification of recovery.

Each incident is maintained separately so that the investigation and evidence can be reviewed independently.

- [Incident 01](incident_01/)
- [Incident 02](incident_02/)
- [Incident 03](incident_03/)

## Security Considerations

Security is considered throughout the infrastructure and application configuration.

- The RDS database is deployed in private subnets and is not publicly accessible.
- Security groups restrict inbound connectivity to the required ports and sources.
- The S3 bucket remains private, with public access blocked.
- The EC2 instance accesses S3 through an IAM role rather than stored long-term AWS access keys.
- The custom S3 policy limits access to the project's bucket and its objects.
- Application configuration and credentials are kept separate from source code.

Local environment files containing credentials must not be committed to GitHub.

## Deployment and Verification Workflow

The project follows this general workflow:

1. Develop and test the application locally.
2. Provision the AWS network and infrastructure.
3. Configure IAM permissions and security groups.
4. Launch and configure the EC2 instance.
5. Deploy the application and configure its runtime.
6. Connect the application to RDS.
7. Configure and verify S3 integration.
8. Set up CloudWatch monitoring.
9. Perform controlled troubleshooting exercises.
10. Document the investigation, corrective action, and recovery verification.

## Current Scope

The project focuses on practical AWS operations and infrastructure troubleshooting using a working Python application and supporting AWS services.

The repository contains separate documentation for infrastructure provisioning, application deployment, monitoring, and incident investigations. Each section provides implementation details and supporting evidence.

## Future Improvements

Potential extensions to the project include:

- Infrastructure provisioning with Terraform.
- Automated deployment through a CI/CD pipeline.
- Expanded monitoring and alerting.
- Additional operational failure scenarios and recovery exercises.

These are potential extensions rather than claims about functionality already implemented.

## Author
Anisha S.

This project was developed as a practical demonstration of AWS cloud infrastructure, application operations, monitoring, security, and troubleshooting skills.