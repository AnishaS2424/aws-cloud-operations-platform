
# Incident 02 — S3 AccessDenied / IAM Policy Misconfiguration

## Incident Objective

I intentionally introduced an S3 upload failure by changing the resource scope of the object permissions in the IAM policy attached to the EC2 instance.

The purpose was to simulate a more realistic AWS support scenario where the IAM role is still attached and S3 access is still partially working, but a specific application operation fails because the policy resource does not match the object being accessed.

The failure was introduced in a controlled environment and restored after identifying the policy scope mismatch.

## Baseline

Before introducing the failure, I confirmed that the application could upload a file to Amazon S3 successfully.

The existing application upload screenshot was used as the baseline evidence.

The EC2 instance was also able to list the S3 bucket through its IAM role:

```bash
aws s3 ls s3://cloudops-bucket-01/
```

The command returned the existing object:

```text
2026-09-13 01:32:56         18 s3_upload_test.txt
```

This established that the EC2 instance had working S3 access before the incident.

### Baseline Evidence

![Baseline screenshot showing all systems healthy](../../screenshots/incident_02/incident-02-baseline-all-systems-healthy.png)

## Failure Introduction

The existing IAM role was:

`cloudops-ec2-s3-role`

The original object-level permission allowed:

`arn:aws:s3:::cloudops-bucket-01/*`

I intentionally changed only the `ManageObjects` resource to:

`arn:aws:s3:::cloudops-bucket-01/uploads/*`

The `ListBucket` permission was left unchanged:

`arn:aws:s3:::cloudops-bucket-01`

This created a controlled resource-scope mismatch.

The application uploads files to the bucket root, for example:

`arn:aws:s3:::cloudops-bucket-01/s3_upload_test_02.txt`

However, the IAM policy now allowed object operations only under:

`arn:aws:s3:::cloudops-bucket-01/uploads/*`

No application code, S3 bucket settings, or IAM role attachment was changed.

## Detecting the Failure

I tested the application upload after introducing the IAM policy change.

The upload failed with an AWS `AccessDenied` error during the `s3:PutObject` operation.

The error identified the exact object being requested:

`arn:aws:s3:::cloudops-bucket-01/s3_upload_test_02.txt`

The application was therefore able to reach S3, but it was not authorized to perform the requested object upload.

### Failure Evidence

![S3 upload failure showing AccessDenied](../../screenshots/incident_02/incident-02-failure-s3-access-denied.png)

## Diagnosis

I investigated the failure without immediately changing the policy back.

### Step 1 — Verify S3 Bucket Access

From the EC2 instance, I ran:

```bash
aws s3 ls s3://cloudops-bucket-01/
```

The command succeeded and returned:

```text
2026-09-13 01:32:56         18 s3_upload_test.txt
```

This showed that the EC2 instance still had the expected IAM role, the role could communicate with Amazon S3, and `s3:ListBucket` was still working.

The problem was therefore more specific than a general S3 access or connectivity failure.

### Step 2 — Inspect IAM Policy Resource Scope

I then inspected the `cloudops-s3-access` policy attached to:

`cloudops-ec2-s3-role`

The `ListBucket` statement correctly targeted the bucket:

`arn:aws:s3:::cloudops-bucket-01`

However, the `ManageObjects` statement was restricted to:

`arn:aws:s3:::cloudops-bucket-01/uploads/*`

The failed application request targeted:

`arn:aws:s3:::cloudops-bucket-01/s3_upload_test_02.txt`

These resources do not match.

The application was attempting to operate on an object at the bucket root, while the policy only authorized object operations under the `uploads/` prefix.

### Diagnosis Evidence

![IAM policy resource scope showing the mismatch](../../screenshots/incident_02/incident-02-diagnosis-iam-resource-scope.png)

## Root Cause

The root cause was an IAM resource-scope mismatch.

The `s3:PutObject` action was still present in the policy, but its resource was restricted to:

`arn:aws:s3:::cloudops-bucket-01/uploads/*`

The application was uploading to the bucket root:

`arn:aws:s3:::cloudops-bucket-01/s3_upload_test_02.txt`

Because the requested object ARN did not fall within the permitted resource scope, AWS denied the `s3:PutObject` operation.

The key diagnostic picture was:

```text
IAM role attached       → Yes
S3 bucket access        → Yes
ListBucket              → Allowed
s3:PutObject action     → Present
Object resource match   → No
Result                  → AccessDenied
```

## Resolution

I restored the intended object-level resource scope in the `ManageObjects` statement:

`arn:aws:s3:::cloudops-bucket-01/*`

The final policy structure was:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ListBucket",
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket"
      ],
      "Resource": "arn:aws:s3:::cloudops-bucket-01"
    },
    {
      "Sid": "ManageObjects",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::cloudops-bucket-01/*"
    }
  ]
}
```

### Resolution Evidence

![IAM policy showing the restored resource scope](../../screenshots/incident_02/incident-02-resolution-iam-policy-restored.png)

## Verification

### Step 1 — Verify Application Upload

I repeated the application upload after restoring the IAM policy.

The application successfully uploaded:

`s3_upload_test_02.txt`

The application returned:

```json
{
  "filename": "s3_upload_test_02.txt",
  "message": "File uploaded successfully"
}
```

This confirmed that the previously failing `s3:PutObject` operation had recovered.

### Step 2 — Verify the Object Through AWS CLI

I then independently verified the S3 bucket from the EC2 instance:

```bash
aws s3 ls s3://cloudops-bucket-01/
```

The command confirmed that the uploaded object was present in the bucket.

This provided an independent verification after the application-level recovery.

### Verification Evidence

![S3 access successfully recovered after the IAM policy was restored](../../screenshots/incident_02/incident-02-verification-s3-access-recovered.png)

## Troubleshooting Summary

| Check | Result | Conclusion |
|---|---|---|
| Application upload before incident | Successful | S3 integration was working |
| EC2 `aws s3 ls` | Successful | IAM role and bucket access were working |
| Application upload after policy change | AccessDenied | `s3:PutObject` was denied |
| `ListBucket` | Still allowed | General S3 access was not broken |
| IAM `ManageObjects` resource | `bucket/uploads/*` | Object access was restricted to a different prefix |
| Application requested object | `bucket/s3_upload_test_02.txt` | Requested object was outside permitted scope |
| IAM resource restored | `bucket/*` | Intended object access restored |
| Application upload after fix | Successful | `PutObject` recovered |
| CLI verification | Object present | S3 upload confirmed independently |

## Lessons Learned

### 1. IAM Permissions Are Evaluated Against the Requested Resource

Having `s3:PutObject` in a policy does not automatically authorize every object in a bucket. The resource specified in the policy must also match the object being accessed.

### 2. Partial Access Is an Important Troubleshooting Clue

The successful `aws s3 ls` command showed that S3 was not completely inaccessible. This helped narrow the investigation toward object-level permissions.

### 3. Bucket and Object ARNs Are Different

The `s3:ListBucket` operation uses the bucket ARN:

`arn:aws:s3:::cloudops-bucket-01`

Object operations such as `GetObject` and `PutObject` use an object ARN:

`arn:aws:s3:::cloudops-bucket-01/*`

### 4. Compare the Requested Resource with the Policy Resource

The most useful comparison in this incident was:

**Requested:**

`arn:aws:s3:::cloudops-bucket-01/s3_upload_test_02.txt`

**Allowed:**

`arn:aws:s3:::cloudops-bucket-01/uploads/*`

Once these were compared, the resource-scope mismatch explained the `AccessDenied` error.

### 5. Least Privilege Must Match the Workload

Restricting object access to a prefix can be useful when the application is designed to use that prefix. The permission scope must still match the application's actual object path.
