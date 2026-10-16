# RDS Connection

The application uses Amazon RDS PostgreSQL as its production database. By the time I worked on the application connection, the RDS instance and its network/security configuration were already in place. This document focuses on how I connected the deployed application on EC2 to that database and verified the connection.

## Database Details

The application connects to:

| Property | Value |
|---|---|
| RDS instance | `cloudops-postgres` |
| Database | `cloudops` |
| Engine | PostgreSQL 16.4 |
| Username | `cloudopsadmin` |
| Port | `5432` |
| Region | `us-east-1` |

The RDS instance is private and does not have public access. The application reaches it from the EC2 instance through the VPC.

The database password is kept private and is not included in this document.

## Application Configuration

On EC2, I configured the application environment with the RDS connection details:

```dotenv
DB_HOST=<RDS endpoint>
DB_PORT=5432
DB_NAME=cloudops
DB_USER=cloudopsadmin
DB_PASSWORD=<private RDS password>
```

The RDS endpoint was provided to the application through `DB_HOST` rather than hard-coding it into the Python source code.

The `.env` file containing the actual password was created directly on EC2 and was not copied from my local development environment.

I also restricted its permissions:

```bash
chmod 600 .env
```

This keeps the database credentials out of the application source and limits access to the file on the server.

## Verify Network Connectivity

Before testing the Python application, I checked whether the EC2 instance could reach the RDS endpoint on PostgreSQL port `5432`.

I used:

```bash
nc -zv <RDS endpoint> 5432
```

The connection succeeded.

This was useful as a first-level test because it confirmed that the EC2 host could establish a TCP connection to the database endpoint before involving the application or PostgreSQL client libraries.

The successful connection was also consistent with the intended security model: PostgreSQL traffic is allowed from the EC2 security group to the RDS security group rather than from the public Internet.

## Verify the Application Database Connection

After confirming network connectivity, I tested the database connection through the application's existing connection function.

From the application directory, I ran:

```bash
python -c "from db import get_connection; conn=get_connection(); print('RDS connection successful'); conn.close()"
```

The command returned:

```text
RDS connection successful
```

This confirmed that the application could:

- Resolve and reach the RDS endpoint
- Establish a PostgreSQL connection
- Authenticate using the configured database credentials
- Close the connection successfully

This was a stronger validation than a network-only test because it exercised the same database connection code used by the Flask application.

### Evidence: Application and RDS Integration

![Application and RDS integration verification](app_rds_integration_verified.PNG)

## Create the Application Table

The RDS database was available, but the application's orders table had not yet been created.

I connected through the application's database connection and created the table:

```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    amount NUMERIC(10,2) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

The table provides the basic data model required by the application.

I then verified the database through the application environment before continuing with the web deployment.

## Application-Level Verification

After the table was available, I verified the database through the running application.

The application dashboard reported:

```text
PostgreSQL: CONNECTED
```

I also tested the order API.

A test order was created with:

```bash
curl -X POST http://127.0.0.1/orders \
  -H "Content-Type: application/json" \
  -d '{"customer_name":"AWS Test Customer","amount":1499.99,"status":"PENDING"}'
```

The application returned:

```json
{"message":"Order created","order_id":1}
```

I then retrieved the orders:

```bash
curl http://127.0.0.1/orders
```

The response included:

```json
[{"amount":1499.99,"customer_name":"AWS Test Customer","id":1,"status":"PENDING"}]
```

This verified the complete application-to-database path rather than only testing connectivity.

### Evidence: Order API and RDS Verification

![Order API and RDS verification](app_rds_order_api_verified.PNG)

## Final Connection Flow

The resulting database flow is:

```text
Flask application
       |
       | PostgreSQL connection
       | TCP 5432
       v
EC2 instance
       |
       | VPC internal network
       v
RDS PostgreSQL
cloudops-postgres
```

The important security property is that RDS remains private. The application does not require PostgreSQL to be exposed to the Internet.

## Verification Summary

The RDS integration was considered successful after these checks passed:

- EC2 could reach the RDS endpoint on port `5432`.
- The application's `get_connection()` function successfully connected to RDS.
- The orders table was created successfully.
- The application dashboard reported PostgreSQL as connected.
- An order could be inserted through the application API.
- The inserted order could be retrieved through the application API.

The connection was therefore validated at both the network level and the application level.

## Security Note

I did not place the RDS password, AWS access keys, or private SSH key in the project documentation.

The RDS password remains an environment-specific secret on the EC2 host and should not be committed to source control.