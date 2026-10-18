export const WORDS = [
  { answer: "REGION", term: "Region", clue: "Geographic area such as eu-west-1, made of several AZs" },
  { answer: "AZ", term: "Availability Zone", clue: "One or more isolated datacenters inside a region" },
  { answer: "EDGE", term: "Edge location", clue: "Point of presence used by CloudFront and Route 53" },
  { answer: "IAM", term: "IAM", clue: "Service for users, roles and permission policies" },
  { answer: "ROLE", term: "IAM role", clue: "Identity with temporary credentials that services or people assume" },
  { answer: "POLICY", term: "Policy", clue: "JSON document of Allow and Deny statements" },
  { answer: "DENY", term: "Explicit deny", clue: "Effect that always wins in IAM evaluation" },
  { answer: "STS", term: "STS", clue: "Security Token Service that issues temporary credentials" },
  { answer: "MFA", term: "MFA", clue: "Second factor you can require in policy conditions" },
  { answer: "AMI", term: "AMI", clue: "Machine image used to launch EC2 instances" },
  { answer: "SPOT", term: "Spot instance", clue: "Spare capacity at a big discount that can be reclaimed" },
  { answer: "EBS", term: "EBS", clue: "Block storage volume attached to an instance in one AZ" },
  { answer: "VPC", term: "VPC", clue: "Your private, isolated network in AWS" },
  { answer: "SUBNET", term: "Subnet", clue: "IP range inside a VPC that lives in exactly one AZ" },
  { answer: "IGW", term: "Internet gateway", clue: "Attaches to a VPC to give public subnets internet access" },
  { answer: "NAT", term: "NAT gateway", clue: "Lets private instances reach the internet without being reachable" },
  { answer: "SECURITYGROUP", term: "Security group", clue: "Stateful instance-level firewall with allow rules only" },
  { answer: "NACL", term: "Network ACL", clue: "Stateless subnet-level firewall with numbered allow and deny rules" },
  { answer: "ENDPOINT", term: "VPC endpoint", clue: "Private path from a VPC to S3 or other AWS services" },
  { answer: "BUCKET", term: "S3 bucket", clue: "Container for objects with a globally unique name" },
  { answer: "GLACIER", term: "S3 Glacier", clue: "Archive storage class: cheap to keep, slower to retrieve" },
  { answer: "RDS", term: "RDS", clue: "Managed relational databases like Postgres and MySQL" },
  { answer: "AURORA", term: "Aurora", clue: "AWS-built MySQL/Postgres-compatible engine with shared storage" },
  { answer: "DYNAMODB", term: "DynamoDB", clue: "Serverless key-value and document database" },
  { answer: "ALB", term: "ALB", clue: "Layer 7 load balancer with path and host routing" },
  { answer: "AUTOSCALING", term: "Auto Scaling group", clue: "Keeps the right number of healthy instances running" },
  { answer: "LAMBDA", term: "Lambda", clue: "Run functions on events without managing servers" },
  { answer: "COLDSTART", term: "Cold start", clue: "Extra latency when Lambda creates a new execution environment" },
  { answer: "SQS", term: "SQS", clue: "Fully managed message queue" },
  { answer: "SNS", term: "SNS", clue: "Pub/sub topics that fan out to many subscribers" },
  { answer: "EVENTBRIDGE", term: "EventBridge", clue: "Event bus with rules that route events to targets" },
  { answer: "CLOUDFRONT", term: "CloudFront", clue: "AWS content delivery network" },
  { answer: "CLOUDWATCH", term: "CloudWatch", clue: "Metrics, logs and alarms" },
  { answer: "CLOUDTRAIL", term: "CloudTrail", clue: "Audit log of API calls in your account" },
];

export const RUSH = [
  { task: "Give an EC2 app access to S3 without keys", answer: "Attach an IAM role (instance profile)", wrong: ["Put access keys in the AMI", "Store keys in user data", "Make the bucket public"] },
  { task: "Private instances need OS updates from the internet", answer: "NAT gateway + route 0.0.0.0/0 → NAT", wrong: ["Attach an IGW to the private subnet", "Give them public IPs", "Open SG 0.0.0.0/0 inbound"] },
  { task: "Private access to S3 without NAT charges", answer: "S3 gateway endpoint", wrong: ["Bigger NAT gateway", "Direct Connect only", "Public bucket policy"] },
  { task: "Firewall that is stateful and attached to instances", answer: "Security group", wrong: ["Network ACL", "Route table", "Internet gateway"] },
  { task: "Survive the loss of one datacenter", answer: "Spread across multiple AZs", wrong: ["Bigger instance type", "Use one AZ with backups", "Use spot instances"] },
  { task: "Decouple a spiky producer from a slow worker", answer: "SQS queue", wrong: ["SNS topic only", "Synchronous HTTP call", "Bigger EC2 instance"] },
  { task: "One event must reach email, SQS and a Lambda", answer: "SNS fan-out", wrong: ["Three cron jobs", "One SQS queue", "CloudTrail"] },
  { task: "Cheapest storage for compliance archives read once a year", answer: "S3 Glacier Deep Archive", wrong: ["S3 Standard", "EBS gp3", "EFS"] },
  { task: "Route /api to one service and / to another", answer: "Application Load Balancer rules", wrong: ["Network Load Balancer", "Route 53 weighted records", "Security group rules"] },
  { task: "Key-value store at single-digit ms for any scale", answer: "DynamoDB", wrong: ["RDS MySQL", "Redshift", "S3 Select"] },
  { task: "Who deleted that bucket?", answer: "CloudTrail", wrong: ["CloudWatch metrics", "VPC Flow Logs", "Trusted Advisor"] },
  { task: "Alert when CPU > 80% for 5 minutes", answer: "CloudWatch alarm", wrong: ["CloudTrail rule", "IAM policy", "AWS Config snapshot"] },
  { task: "Store a database password for a Lambda", answer: "Secrets Manager (read via its IAM role)", wrong: ["Hardcode in the function", "Environment variable in git", "S3 public object"] },
  { task: "Cut steady 24/7 compute cost", answer: "Savings Plans / Reserved Instances", wrong: ["On-demand only", "Spot for the database", "Bigger instances"] },
  { task: "Cap what a developer's roles can ever be granted", answer: "Permissions boundary", wrong: ["Bucket policy", "Security group", "Route table"] },
  { task: "Block every account in the org from using other regions", answer: "Service control policy (SCP)", wrong: ["IAM user policy", "NACL", "CloudFront geo-restriction"] },
  { task: "Make a static site fast worldwide", answer: "S3 origin + CloudFront", wrong: ["EC2 in one region", "Route 53 alone", "Lambda per request"] },
  { task: "Run a container without managing servers", answer: "ECS on Fargate", wrong: ["EC2 with Docker by hand", "Elastic Beanstalk on bare metal", "Lightsail VPS"] },
];

export const BUGS = [
  {
    symptom: "Security review: this policy lets the app do anything to every bucket.",
    lang: "json",
    code: `{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "s3:*",
    "Resource": "*"
  }]
}`,
    bug: [4, 5],
    why: "Least privilege: allow only the actions the app needs (e.g. s3:GetObject, s3:PutObject) on only its bucket, arn:aws:s3:::app-uploads/*.",
  },
  {
    symptom: "The web server in the public subnet is unreachable from the internet.",
    lang: "text",
    code: `VPC 10.0.0.0/16  + internet gateway attached
Public subnet 10.0.1.0/24 route table:
  10.0.0.0/16  -> local
Web instance: public IP 54.x.x.x
Security group: allow tcp/443 from 0.0.0.0/0`,
    bug: [2],
    why: "The route table has no 0.0.0.0/0 → igw-… route, so the subnet is not public and replies cannot leave. Add the default route to the internet gateway.",
  },
  {
    symptom: "Audit flagged a credential exposure in this Lambda.",
    lang: "python",
    code: `import boto3, os

AWS_SECRET = os.environ["AWS_SECRET_ACCESS_KEY_FROM_REPO"]
s3 = boto3.client("s3", aws_secret_access_key=AWS_SECRET)

def handler(event, context):
    return s3.list_objects_v2(Bucket="reports")`,
    bug: [2, 3],
    why: "Lambda already has temporary credentials from its execution role. Remove long-lived keys entirely and grant the role s3:ListBucket on the reports bucket only.",
  },
  {
    symptom: "Clients get timeouts on the replies even though inbound 443 is allowed.",
    lang: "text",
    code: `Network ACL (public subnet)
Inbound:  100 ALLOW tcp 443   0.0.0.0/0
Inbound:  *   DENY  all
Outbound: 100 ALLOW tcp 443   0.0.0.0/0
Outbound: *   DENY  all`,
    bug: [3],
    why: "NACLs are stateless: responses go back to the client's ephemeral port, not 443. Allow outbound tcp 1024-65535 (and usually rely on security groups instead).",
  },
  {
    symptom: "Every customer's private files can be downloaded by anyone.",
    lang: "json",
    code: `{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::acme-customer-files/*"
  }]
}`,
    bug: [4],
    why: "Principal \"*\" makes the bucket public. Keep Block Public Access on, grant specific roles, and give users presigned URLs or CloudFront with origin access control.",
  },
  {
    symptom: "The whole site went down when one AZ had an outage.",
    lang: "text",
    code: `Auto Scaling group "web"
  min 2, desired 4, max 10
  subnets: subnet-a (eu-west-1a)
  health check: ELB
RDS: db.r6g.large, Multi-AZ: false`,
    bug: [2, 4],
    why: "All instances live in one AZ and the database has no standby. List subnets in at least two AZs and enable Multi-AZ on RDS.",
  },
];

export const META = {
  rushLabel: "AWS Rush",
  rushIntro: "Pick the AWS service or setting that does the job.",
  rushMono: false,
  bugLabel: "Cloud Bug Hunt",
  bugNoun: "finding",
};
