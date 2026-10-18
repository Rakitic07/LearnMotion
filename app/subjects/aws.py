"""AWS: core services from global infrastructure to Well-Architected. Account ids are AWS documentation placeholders."""

from ._dsl import ex, flow, node, pkt, qa, step

CATEGORIES = [
    {"id": "foundations", "title": "Foundations", "color": "sky", "blurb": "Regions, identity and access."},
    {"id": "compute", "title": "Compute", "color": "peach", "blurb": "EC2, scaling and serverless."},
    {"id": "networking", "title": "Networking", "color": "mint", "blurb": "VPCs, edge and DNS."},
    {"id": "storage-data", "title": "Storage & Data", "color": "lilac", "blurb": "S3, RDS, DynamoDB."},
    {"id": "integration-ops", "title": "Integration & Ops", "color": "lemon", "blurb": "Messaging, monitoring, best practices."},
]

TOPICS = [
    {
        "id": "global-infra", "title": "Regions, AZs & the Shared Responsibility Model", "category": "foundations", "level": "basic", "code": "GI",
        "tagline": "Where AWS runs your stuff, and which parts of security are yours.",
        "analogy": "A hotel chain: cities (Regions), separate buildings in each city with their own power (Availability Zones), and lobby kiosks near you (edge locations). The hotel secures the building; you lock your room and your suitcase.",
        "what": "A Region is a geographic area (eu-west-1) with multiple isolated Availability Zones, each one or more data centres with independent power and networking, connected by low-latency links. Deploy across at least two AZs for high availability; across Regions for disaster recovery and latency. Edge locations host CloudFront and Route 53. Under the shared responsibility model AWS secures the cloud (hardware, facilities, hypervisor); you secure what you put in it (IAM, data, encryption, OS patching on EC2, network rules). The more managed the service, the less you manage.",
        "use_cases": ["Choosing a Region for data residency (GDPR).", "Multi-AZ deployments for 99.9%+ availability.", "Explaining to auditors who patches what."],
        "key_points": [
            "Not all services or instance types exist in every Region.",
            "Cross-AZ traffic costs money; cross-Region more.",
            "Some services are global (IAM, Route 53, CloudFront).",
            "Use Organizations + multiple accounts to isolate environments.",
        ],
        "examples": [
            ex("List Regions and AZs", "basic", "AWS CLI with your configured profile (credentials come from SSO or a role, never from code).", "bash", """
                aws ec2 describe-regions --query "Regions[].RegionName" --output table
                aws ec2 describe-availability-zones --region eu-west-1 \\
                  --query "AvailabilityZones[].ZoneName"
            """, runnable=False),
            ex("Who am I?", "basic", "Check which identity your CLI is using before you run anything.", "bash", """
                aws sso login --profile dev
                aws sts get-caller-identity --profile dev
            """, runnable=False),
        ],
        "commands": ["aws configure sso · aws sso login --profile p", "aws sts get-caller-identity", "aws ec2 describe-regions", "--region eu-west-1 · AWS_PROFILE=dev"],
        "gotchas": ["Long-lived access keys on laptops: use IAM Identity Center (SSO) or roles.", "Assuming one AZ is enough: an AZ outage takes you down.", "Accidentally creating resources in the wrong Region and paying for them."],
        "interview": [
            qa("basic", "Region vs Availability Zone?", "A Region is a geographic area containing multiple AZs. An AZ is one or more isolated data centres with independent power and networking. Spread across AZs for availability, across Regions for DR and latency."),
            qa("basic", "Explain the shared responsibility model.", "AWS is responsible for security of the cloud (facilities, hardware, virtualization, managed service internals). Customers are responsible for security in the cloud: identities, permissions, data, encryption, network config, and OS/app patching on IaaS."),
            qa("intermediate", "How do you choose a Region?", "Compliance/data residency, latency to users, service and instance availability, and price."),
            qa("intermediate", "Why use multiple AWS accounts?", "Hard isolation of blast radius, billing and permissions between environments and teams, governed centrally with Organizations, SCPs and Control Tower."),
        ],
        "related": ["iam", "observability-well-architected"],
        "flow": flow(
            [node("r", "Region eu-west-1", 50, 10, "lilac", "Ireland", "pill"), node("az1", "AZ a", 18, 50, "sky", "data centre(s)"), node("az2", "AZ b", 50, 50, "sky", "data centre(s)"),
             node("az3", "AZ c", 82, 50, "sky", "data centre(s)"), node("edge", "Edge location", 50, 90, "mint", "CloudFront · Route 53", "round")],
            [("r", "az1"), ("r", "az2"), ("r", "az3"), ("az1", "az2"), ("az2", "az3")],
            [
                step("A Region", "A geographic area with 3+ isolated Availability Zones.", ["r"]),
                step("Availability Zones", "Separate power, cooling and network; connected with low-latency fibre.", ["az1", "az2", "az3"], [pkt("az1", "az2", "<2 ms"), pkt("az2", "az3", "<2 ms")]),
                step("Survive an AZ failure", "Run in two or more AZs: if AZ a fails, b and c keep serving.", ["az2", "az3"], set={"az1": {"tint": "rose", "sub": "outage"}}),
                step("Edge locations", "Hundreds of points of presence cache content and answer DNS close to users.", ["edge"], [pkt("edge", "az2", "origin fetch")]),
            ],
        ),
    },
    {
        "id": "iam", "title": "IAM: Users, Roles & Policies", "category": "foundations", "level": "intermediate", "code": "IA",
        "tagline": "Who can do what to which resource, and how AWS evaluates it.",
        "analogy": "An office building: an ID badge (principal) plus access rules on doors (policies). Temporary visitor passes (roles) beat handing out permanent keys (access keys).",
        "what": "IAM controls authentication and authorization. Principals: users (avoid for humans; use IAM Identity Center), roles (assumed for temporary credentials via STS by services, workloads and federated users), and groups. Policies are JSON documents with Effect, Action, Resource and optional Condition. Types: identity-based, resource-based (S3 bucket policy), permissions boundaries, SCPs (Organizations), session policies. Evaluation: default deny → an explicit Deny anywhere wins → otherwise need an Allow (and every applicable boundary/SCP must also allow).",
        "use_cases": ["EC2/Lambda accessing S3 via an instance/execution role.", "Cross-account access with a role and trust policy.", "Guardrails with SCPs (deny leaving approved Regions)."],
        "key_points": [
            "Least privilege; start narrow and use IAM Access Analyzer to refine.",
            "Roles have two policies: trust (who can assume) and permissions (what they can do).",
            "Prefer roles and short-lived credentials; never embed access keys in code.",
            "Explicit deny > allow > implicit deny.",
        ],
        "examples": [
            ex("Least-privilege S3 read policy", "basic", "Read objects under one prefix only. Try it in the IAM Policy Evaluator.", "json", """
                {
                  "Version": "2012-10-17",
                  "Statement": [
                    {
                      "Sid": "ReadReports",
                      "Effect": "Allow",
                      "Action": ["s3:GetObject"],
                      "Resource": "arn:aws:s3:::acme-reports/finance/*"
                    }
                  ]
                }
            """, runnable=False),
            ex("Role trust policy for Lambda", "intermediate", "Who may assume the role: the Lambda service.", "json", """
                {
                  "Version": "2012-10-17",
                  "Statement": [
                    {
                      "Effect": "Allow",
                      "Principal": { "Service": "lambda.amazonaws.com" },
                      "Action": "sts:AssumeRole"
                    }
                  ]
                }
            """, runnable=False),
            ex("Deny outside approved Regions (SCP)", "advanced", "An explicit deny with a condition overrides any allow.", "json", """
                {
                  "Version": "2012-10-17",
                  "Statement": [
                    {
                      "Sid": "DenyOtherRegions",
                      "Effect": "Deny",
                      "NotAction": ["iam:*", "sts:*", "cloudfront:*", "route53:*"],
                      "Resource": "*",
                      "Condition": { "StringNotEquals": { "aws:RequestedRegion": ["eu-west-1", "eu-central-1"] } }
                    }
                  ]
                }
            """, runnable=False),
        ],
        "commands": ["aws iam create-role --assume-role-policy-document file://trust.json", "aws sts assume-role --role-arn arn:aws:iam::123456789012:role/Deploy --role-session-name me", "aws iam simulate-principal-policy", "IAM Access Analyzer: unused access, policy validation"],
        "gotchas": ["\"Action\": \"*\", \"Resource\": \"*\" for convenience.", "Access keys committed to Git (bots find them in minutes).", "Forgetting that an S3 bucket policy can grant access independently of identity policies (same account)."],
        "interview": [
            qa("intermediate", "IAM user vs role?", "A user has long-term credentials tied to one identity. A role has no credentials of its own; trusted principals assume it to get temporary STS credentials. Prefer roles for workloads, cross-account access and federated humans."),
            qa("intermediate", "How does AWS evaluate a request?", "Start with implicit deny. If any applicable policy has an explicit Deny, deny. Otherwise, the request must be allowed by identity or resource policies, and also permitted by any SCPs, permissions boundaries and session policies in play."),
            qa("advanced", "How do you give a service in account A access to a bucket in account B?", "Create a role in B with a trust policy for A's principal and permissions on the bucket; A assumes it via STS. Or use a bucket policy granting A's role, with A's identity policy also allowing it (cross-account needs both sides)."),
            qa("advanced", "What is a permissions boundary?", "A managed policy that sets the maximum permissions an identity-based policy can grant to a user or role; effective permissions are the intersection. Used to safely delegate role creation."),
            qa("basic", "How should an application on EC2 get AWS credentials?", "Through an instance profile (IAM role); the SDK fetches rotating temporary credentials from the instance metadata service (IMDSv2). Never hardcode keys."),
        ],
        "related": ["s3", "global-infra"],
        "flow": flow(
            [node("req", "Request", 8, 50, "slate", "s3:GetObject", "pill"), node("deny", "Explicit Deny?", 34, 20, "rose", "any policy"), node("scp", "SCP / boundary allow?", 34, 80, "lemon", "guardrails"),
             node("allow", "Allow?", 64, 50, "mint", "identity or resource"), node("ok", "ALLOW", 92, 30, "mint", "", "round"), node("no", "DENY", 92, 72, "rose", "", "round")],
            [("req", "deny"), ("req", "scp"), ("deny", "allow"), ("scp", "allow"), ("allow", "ok"), ("allow", "no")],
            [
                step("Default deny", "Every request starts implicitly denied.", ["req"]),
                step("Any explicit Deny?", "If any policy says Deny for this action/resource, the answer is DENY. Full stop.", ["deny"], [pkt("req", "deny", "check")]),
                step("Guardrails", "SCPs and permissions boundaries must also permit the action.", ["scp"], [pkt("req", "scp", "check")]),
                step("Need an Allow", "An identity or resource policy must allow it.", ["allow"], [pkt("deny", "allow"), pkt("scp", "allow")]),
                step("Decision", "Allowed → ALLOW. No matching allow → implicit DENY.", ["ok", "no"], [pkt("allow", "ok", "match", "mint"), pkt("allow", "no", "none", "rose")]),
            ],
        ),
    },
    {
        "id": "ec2", "title": "EC2: Instances, AMIs & Pricing", "category": "compute", "level": "basic", "code": "EC",
        "tagline": "Virtual servers, instance families, storage and the purchase options that cut costs.",
        "analogy": "Renting cars: pick the model (instance type), the starting configuration (AMI), pay by the minute (on-demand), sign a yearly lease for a discount (Savings Plans), or grab a standby car cheaply that may be recalled (Spot).",
        "what": "EC2 provides virtual machines. Instance types by family: general purpose (m, t burstable), compute (c), memory (r, x), storage (i, d), accelerated (g, p, inf). Graviton (ARM, the 'g' suffix) instances are often cheaper per performance. An AMI is the boot image. Storage: EBS volumes (network block storage, persists independently; gp3 default) or instance store (ephemeral). Access via security groups (stateful firewall) and SSM Session Manager instead of SSH keys. Pricing: On-Demand, Savings Plans/Reserved (1–3 years, up to ~70% off), Spot (up to ~90% off, can be interrupted with 2 minutes notice).",
        "use_cases": ["Long-running services that need full OS control.", "Batch/ML jobs on Spot.", "Legacy apps lifted and shifted."],
        "key_points": [
            "Use IMDSv2 only (token-based metadata) to block SSRF credential theft.",
            "User data runs a bootstrap script at first boot.",
            "Placement groups: cluster (low latency), spread (isolation), partition (big distributed systems).",
            "Right-size with Compute Optimizer; stop or schedule idle instances.",
        ],
        "examples": [
            ex("Launch an instance with a role and IMDSv2", "intermediate", "No SSH key: connect with SSM Session Manager.", "bash", """
                aws ec2 run-instances \\
                  --image-id resolve:ssm:/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-arm64 \\
                  --instance-type t4g.small \\
                  --iam-instance-profile Name=web-app-profile \\
                  --metadata-options HttpTokens=required,HttpEndpoint=enabled \\
                  --security-group-ids sg-0123456789abcdef0 \\
                  --user-data file://bootstrap.sh
                aws ssm start-session --target i-0123456789abcdef0
            """, runnable=False),
            ex("Bootstrap with user data", "basic", "Install and start a web server at first boot.", "bash", """
                #!/bin/bash
                dnf install -y nginx
                systemctl enable --now nginx
                TOKEN=$(curl -sX PUT http://169.254.169.254/latest/api/token -H "X-aws-ec2-metadata-token-ttl-seconds: 60")
                curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/instance-id
            """, runnable=False),
        ],
        "commands": ["aws ec2 run-instances / describe-instances / stop-instances", "aws ssm start-session --target i-…", "Instance families: t, m, c, r, i, g, p (+g = Graviton)", "EBS gp3 · io2 · st1 · snapshots", "On-Demand · Savings Plans · Reserved · Spot"],
        "gotchas": ["Opening port 22 to 0.0.0.0/0.", "Using Spot for stateful workloads without interruption handling.", "Forgetting unattached EBS volumes and old snapshots keep billing."],
        "interview": [
            qa("basic", "On-Demand vs Reserved/Savings Plans vs Spot?", "On-Demand: pay per second, no commitment. Savings Plans/RIs: commit to usage for 1–3 years for large discounts. Spot: spare capacity up to 90% cheaper but reclaimable with 2 minutes notice; for fault-tolerant work."),
            qa("intermediate", "EBS vs instance store?", "EBS is network-attached, persistent, snapshot-able and survives stop/start. Instance store is physically attached, very fast, but data is lost when the instance stops or fails."),
            qa("intermediate", "Why IMDSv2?", "It requires a session token obtained with a PUT, which blocks most SSRF attacks from reading instance role credentials via the metadata endpoint."),
            qa("advanced", "How do you make EC2 workloads highly available?", "Stateless instances in an Auto Scaling group across multiple AZs behind a load balancer, AMI or launch template based immutable deploys, state in managed services (RDS, S3, ElastiCache)."),
        ],
        "related": ["elb-autoscaling", "vpc"],
        "flow": flow(
            [node("ami", "AMI", 10, 30, "lemon", "Amazon Linux 2023"), node("lt", "Launch", 36, 30, "slate", "t4g.small + user data"), node("ec2", "EC2 instance", 64, 30, "peach", "pending"),
             node("ebs", "EBS gp3", 64, 80, "lilac", "root volume", "db"), node("role", "IAM role", 92, 30, "mint", "temp creds via IMDSv2"), node("sg", "Security group", 36, 80, "sky", "443 from ALB")],
            [("ami", "lt"), ("lt", "ec2"), ("ec2", "ebs"), ("ec2", "role"), ("sg", "ec2")],
            [
                step("Pick an image", "The AMI provides the OS and pre-installed software.", ["ami"]),
                step("Launch", "Choose the instance type, subnet, security group and user data.", ["lt", "ec2"], [pkt("ami", "lt"), pkt("lt", "ec2", "run")]),
                step("Attach storage and firewall", "An EBS root volume attaches; the security group allows only 443 from the load balancer.", ["ebs", "sg"], [pkt("ec2", "ebs"), pkt("sg", "ec2", "rules")], {"ec2": {"sub": "running"}}),
                step("Credentials without keys", "The app gets rotating temporary credentials from its instance role.", ["role"], [pkt("role", "ec2", "STS creds")]),
            ],
        ),
    },
    {
        "id": "vpc", "title": "VPC Networking", "category": "networking", "level": "intermediate", "code": "VP",
        "tagline": "Subnets, route tables, gateways, security groups and NACLs.",
        "analogy": "A gated campus: the campus (VPC), buildings (subnets), signposts (route tables), the main gate to the street (Internet Gateway), a one-way exit for staff only (NAT Gateway), door guards who remember who left (security groups) and checkpoint barriers that check everyone both ways (NACLs).",
        "what": "A VPC is your isolated network with a CIDR block (10.0.0.0/16) in a Region. Subnets live in one AZ. A subnet is public if its route table sends 0.0.0.0/0 to an Internet Gateway; private subnets reach the internet outbound through a NAT Gateway in a public subnet. Instances need a public IP to be reachable from the internet. Security groups are stateful, allow-only, attached to ENIs. Network ACLs are stateless, ordered allow/deny rules at the subnet boundary. VPC endpoints reach AWS services privately; peering and Transit Gateway connect VPCs.",
        "use_cases": ["Three-tier app: public ALB, private app, isolated DB subnets.", "Private access to S3 via a gateway endpoint.", "Connecting many VPCs and on-prem with Transit Gateway."],
        "key_points": [
            "Spread subnets over at least 2 AZs.",
            "SG rules can reference other SGs (app-sg allows from alb-sg).",
            "NACLs need ephemeral port rules for return traffic (stateless).",
            "NAT Gateways cost per hour and per GB; endpoints can save money.",
        ],
        "examples": [
            ex("Security group chain", "intermediate", "Only the ALB can reach the app, only the app can reach the DB.", "bash", """
                aws ec2 authorize-security-group-ingress --group-id sg-app \\
                  --protocol tcp --port 8080 --source-group sg-alb
                aws ec2 authorize-security-group-ingress --group-id sg-db \\
                  --protocol tcp --port 5432 --source-group sg-app
            """, runnable=False),
            ex("CloudFormation snippet: public subnet", "advanced", "IGW + route makes the subnet public.", "yaml", """
                Resources:
                  Vpc:
                    Type: AWS::EC2::VPC
                    Properties: { CidrBlock: 10.0.0.0/16, EnableDnsHostnames: true }
                  Igw:
                    Type: AWS::EC2::InternetGateway
                  Attach:
                    Type: AWS::EC2::VPCGatewayAttachment
                    Properties: { VpcId: !Ref Vpc, InternetGatewayId: !Ref Igw }
                  PublicA:
                    Type: AWS::EC2::Subnet
                    Properties: { VpcId: !Ref Vpc, CidrBlock: 10.0.0.0/24, AvailabilityZone: eu-west-1a, MapPublicIpOnLaunch: true }
                  PublicRt:
                    Type: AWS::EC2::RouteTable
                    Properties: { VpcId: !Ref Vpc }
                  DefaultRoute:
                    Type: AWS::EC2::Route
                    Properties: { RouteTableId: !Ref PublicRt, DestinationCidrBlock: 0.0.0.0/0, GatewayId: !Ref Igw }
            """, runnable=False),
        ],
        "commands": ["aws ec2 create-vpc --cidr-block 10.0.0.0/16", "Route: 0.0.0.0/0 → igw-… (public) / nat-… (private)", "SG: stateful, allow only · NACL: stateless, numbered allow/deny", "Gateway endpoint (S3, DynamoDB) · Interface endpoint (PrivateLink)", "VPC Flow Logs · Reachability Analyzer"],
        "gotchas": ["Overlapping CIDRs block peering later; plan address space.", "A NAT Gateway in only one AZ is a single point of failure.", "Forgetting NACL ephemeral ports (1024-65535) for return traffic."],
        "interview": [
            qa("intermediate", "What makes a subnet public?", "Its route table has a route to an Internet Gateway (0.0.0.0/0 → igw). Instances also need a public or Elastic IP to be reachable."),
            qa("intermediate", "Security group vs NACL?", "SG: instance/ENI level, stateful (return traffic automatic), allow rules only, all rules evaluated. NACL: subnet level, stateless (must allow return traffic), allow and deny rules evaluated in number order."),
            qa("intermediate", "How do private instances reach the internet?", "Through a NAT Gateway in a public subnet: private route table 0.0.0.0/0 → nat-gw. Inbound connections from the internet are still impossible."),
            qa("advanced", "How do you access S3 from a private subnet without NAT?", "A gateway VPC endpoint for S3 added to the route table; traffic stays on the AWS network and you can restrict it with endpoint and bucket policies (aws:SourceVpce)."),
            qa("advanced", "Peering vs Transit Gateway?", "Peering is one-to-one, non-transitive, simple and cheap for few VPCs. Transit Gateway is a hub that routes between many VPCs and on-prem with central route tables."),
        ],
        "related": ["ec2", "elb-autoscaling"],
        "flow": flow(
            [node("net", "Internet", 50, 6, "slate", "", "round"), node("igw", "Internet GW", 50, 22, "lilac", "", "pill"), node("alb", "ALB", 25, 45, "sky", "public subnet"),
             node("nat", "NAT GW", 75, 45, "lemon", "public subnet"), node("app", "App", 25, 72, "mint", "private subnet"), node("db", "RDS", 75, 90, "peach", "isolated subnet", "db")],
            [("net", "igw"), ("igw", "alb"), ("igw", "nat"), ("alb", "app"), ("app", "nat"), ("app", "db")],
            [
                step("Inbound via IGW", "Users reach the ALB in a public subnet through the Internet Gateway.", ["net", "igw", "alb"], [pkt("net", "igw", "HTTPS"), pkt("igw", "alb")]),
                step("SG chain", "The app's security group only allows traffic from the ALB's security group.", ["app"], [pkt("alb", "app", ":8080")]),
                step("Outbound via NAT", "The private app downloads updates through the NAT Gateway; nobody can connect in.", ["nat"], [pkt("app", "nat", "egress"), pkt("nat", "igw")]),
                step("Database stays isolated", "RDS has no internet route at all and accepts 5432 only from the app SG.", ["db"], [pkt("app", "db", ":5432")]),
            ],
        ),
    },
    {
        "id": "s3", "title": "S3: Object Storage", "category": "storage-data", "level": "basic", "code": "S3",
        "tagline": "Buckets, storage classes, lifecycle, security and presigned URLs.",
        "analogy": "An infinite warehouse of labelled boxes: you never manage shelves, you just store and fetch boxes by label, and choose cheaper back rooms for boxes you rarely open.",
        "what": "S3 stores objects (up to 5 TB) in buckets, addressed by key. It offers 11 nines of durability and strong read-after-write consistency. Storage classes: Standard, Intelligent-Tiering, Standard-IA, One Zone-IA, Glacier Instant/Flexible/Deep Archive. Lifecycle rules transition or expire objects. Versioning protects against overwrites and deletes; Object Lock gives WORM retention. Security: Block Public Access on by default, bucket policies, encryption (SSE-S3 by default, SSE-KMS for key control), presigned URLs for temporary access. Event notifications trigger Lambda, SQS or EventBridge.",
        "use_cases": ["Static assets and user uploads.", "Data lake for analytics (Athena, EMR).", "Backups and archives with lifecycle to Glacier."],
        "key_points": [
            "Keep Block Public Access on; serve public content via CloudFront with OAC.",
            "Presigned URLs let clients upload/download directly without credentials.",
            "Multipart upload for files > 100 MB.",
            "Request rates scale per prefix (thousands of requests/s each).",
        ],
        "examples": [
            ex("Bucket policy: enforce TLS and allow CloudFront only", "advanced", "Deny any non-HTTPS request; grant reads to one distribution via OAC.", "json", """
                {
                  "Version": "2012-10-17",
                  "Statement": [
                    {
                      "Sid": "DenyInsecureTransport",
                      "Effect": "Deny",
                      "Principal": "*",
                      "Action": "s3:*",
                      "Resource": ["arn:aws:s3:::acme-site", "arn:aws:s3:::acme-site/*"],
                      "Condition": { "Bool": { "aws:SecureTransport": "false" } }
                    },
                    {
                      "Sid": "AllowCloudFrontOAC",
                      "Effect": "Allow",
                      "Principal": { "Service": "cloudfront.amazonaws.com" },
                      "Action": "s3:GetObject",
                      "Resource": "arn:aws:s3:::acme-site/*",
                      "Condition": { "StringEquals": { "AWS:SourceArn": "arn:aws:cloudfront::123456789012:distribution/EDFDVBD6EXAMPLE" } }
                    }
                  ]
                }
            """, runnable=False),
            ex("Lifecycle rule", "intermediate", "Move logs to cheaper tiers, then delete.", "json", """
                {
                  "Rules": [
                    {
                      "ID": "logs-tiering",
                      "Status": "Enabled",
                      "Filter": { "Prefix": "logs/" },
                      "Transitions": [
                        { "Days": 30, "StorageClass": "STANDARD_IA" },
                        { "Days": 90, "StorageClass": "GLACIER" }
                      ],
                      "Expiration": { "Days": 365 }
                    }
                  ]
                }
            """, runnable=False),
            ex("Presigned upload URL with boto3", "intermediate", "The browser uploads straight to S3; credentials come from the app's role.", "python", """
                import boto3

                s3 = boto3.client("s3")
                url = s3.generate_presigned_url(
                    "put_object",
                    Params={"Bucket": "acme-uploads", "Key": "avatars/user-42.png", "ContentType": "image/png"},
                    ExpiresIn=300,
                )
                print(url)
            """, runnable=False),
        ],
        "commands": ["aws s3 cp file s3://bucket/key · aws s3 sync dir s3://bucket/prefix", "aws s3api put-bucket-versioning --versioning-configuration Status=Enabled", "aws s3 presign s3://bucket/key --expires-in 300", "Storage classes: STANDARD · INTELLIGENT_TIERING · STANDARD_IA · GLACIER · DEEP_ARCHIVE"],
        "gotchas": ["Disabling Block Public Access to 'quickly share' a file.", "Many tiny objects in IA/Glacier: minimum size and duration charges.", "Versioning without lifecycle rules for noncurrent versions grows costs silently."],
        "interview": [
            qa("basic", "How durable and consistent is S3?", "Designed for 99.999999999% durability across multiple AZs, with strong read-after-write consistency for all operations."),
            qa("intermediate", "How do you let users upload files securely?", "Generate a short-lived presigned PUT (or POST) URL server-side with the app's role; the client uploads directly to S3; S3 events trigger processing."),
            qa("intermediate", "How do you serve a private bucket publicly?", "Keep the bucket private and put CloudFront in front with Origin Access Control; the bucket policy allows only that distribution."),
            qa("advanced", "SSE-S3 vs SSE-KMS?", "SSE-S3 uses S3-managed keys, transparent. SSE-KMS uses KMS keys you control: key policies, rotation, CloudTrail audit of every decrypt, cross-account control; adds KMS request costs (use bucket keys)."),
        ],
        "related": ["cloudfront-route53", "iam"],
        "flow": flow(
            [node("u", "Browser", 8, 50, "slate"), node("api", "App API", 38, 20, "sky", "has IAM role"), node("s3", "S3 bucket", 70, 50, "lilac", "private · encrypted", "db"),
             node("ev", "S3 event", 92, 20, "lemon", "ObjectCreated", "pill"), node("fn", "Lambda", 92, 82, "peach", "make thumbnail"), node("gl", "Glacier", 70, 92, "slate", "after 90 days", "db")],
            [("u", "api"), ("u", "s3"), ("s3", "ev"), ("ev", "fn"), ("s3", "gl")],
            [
                step("Ask for an upload URL", "The browser asks the API; the API signs a presigned PUT valid for 5 minutes.", ["api"], [pkt("u", "api", "POST /uploads"), pkt("api", "u", "presigned URL")]),
                step("Upload directly", "The browser PUTs the file straight to S3; no credentials ever reach the client.", ["s3"], [pkt("u", "s3", "PUT avatar.png")]),
                step("React to events", "ObjectCreated triggers a Lambda that makes a thumbnail.", ["ev", "fn"], [pkt("s3", "ev"), pkt("ev", "fn", "invoke")]),
                step("Lifecycle", "Older objects move automatically to cheaper storage classes.", ["gl"], [pkt("s3", "gl", "transition")]),
            ],
        ),
    },
    {
        "id": "databases", "title": "RDS, Aurora & DynamoDB", "category": "storage-data", "level": "intermediate", "code": "DB",
        "tagline": "Managed relational and NoSQL databases and when to use each.",
        "analogy": "RDS is a fully serviced apartment (you choose the furniture: Postgres/MySQL), Aurora is the same apartment in a building with shared super-resilient plumbing, DynamoDB is a vending machine: instant, endless, but only sells what you designed it to sell.",
        "what": "RDS runs managed MySQL, PostgreSQL, MariaDB, Oracle and SQL Server: automated backups, patching, Multi-AZ synchronous standby for failover, read replicas for scale. Aurora is AWS's cloud-native MySQL/Postgres-compatible engine with storage replicated six ways across three AZs, fast failover, up to 15 replicas and Serverless v2. DynamoDB is serverless key-value/document NoSQL with single-digit-millisecond latency at any scale; design around partition and sort keys, GSIs, on-demand or provisioned capacity, Streams, TTL and global tables. ElastiCache adds Redis/Valkey/Memcached caching.",
        "use_cases": ["Transactional app data with joins (RDS/Aurora Postgres).", "Shopping carts, sessions, IoT data at huge scale (DynamoDB).", "Read-heavy dashboards with replicas plus ElastiCache."],
        "key_points": [
            "Multi-AZ = availability; read replicas = read scale (async).",
            "Store DB credentials in Secrets Manager with rotation, or use IAM auth.",
            "DynamoDB hot partitions come from low-cardinality keys.",
            "RDS Proxy pools connections for Lambda.",
        ],
        "examples": [
            ex("DynamoDB single-table query (boto3)", "advanced", "All orders of one customer, newest first.", "python", """
                import boto3
                from boto3.dynamodb.conditions import Key

                table = boto3.resource("dynamodb").Table("shop")
                resp = table.query(
                    KeyConditionExpression=Key("PK").eq("CUSTOMER#42") & Key("SK").begins_with("ORDER#"),
                    ScanIndexForward=False,
                    Limit=10,
                )
                print(resp["Items"])
            """, runnable=False),
            ex("Connect to RDS with a secret", "intermediate", "Fetch credentials at runtime from Secrets Manager; nothing in code or env files.", "python", """
                import json, boto3, psycopg

                secret = json.loads(boto3.client("secretsmanager").get_secret_value(SecretId="prod/orders-db")["SecretString"])
                with psycopg.connect(host=secret["host"], dbname="orders", user=secret["username"],
                                     password=secret["password"], sslmode="require") as conn:
                    print(conn.execute("select now()").fetchone())
            """, runnable=False),
        ],
        "commands": ["aws rds create-db-instance --multi-az --engine postgres …", "aws rds create-db-instance-read-replica", "aws dynamodb query --key-condition-expression 'PK = :pk'", "DynamoDB: on-demand vs provisioned + auto scaling · GSI · Streams · TTL", "Secrets Manager rotation · RDS IAM authentication"],
        "gotchas": ["Treating a read replica as a backup or failover target with zero lag.", "DynamoDB Scan in request paths.", "Lambda opening a new DB connection per invocation without RDS Proxy."],
        "interview": [
            qa("intermediate", "Multi-AZ vs read replicas?", "Multi-AZ keeps a synchronous standby in another AZ for automatic failover (availability), not for reads (except Multi-AZ cluster readers). Read replicas replicate asynchronously to scale reads and can be promoted."),
            qa("intermediate", "When choose DynamoDB over RDS?", "Known access patterns, massive or spiky scale, single-digit-ms latency, serverless operations. Choose RDS/Aurora for ad-hoc queries, joins, complex transactions and relational integrity."),
            qa("advanced", "What makes Aurora different from RDS Postgres?", "A distributed storage layer replicated six ways across three AZs, with compute nodes sharing it: faster failover, replicas with low lag, storage auto-growth, backtrack, global database, serverless v2."),
            qa("advanced", "How do you avoid DynamoDB hot partitions?", "Choose high-cardinality partition keys, spread writes (write sharding with suffixes), cache hot reads with DAX, and use on-demand capacity for unpredictable traffic."),
        ],
        "related": ["vpc", "lambda"],
        "flow": flow(
            [node("app", "App", 10, 50, "slate"), node("w", "Primary", 45, 28, "lilac", "AZ a", "db"), node("sb", "Standby", 45, 78, "slate", "AZ b · sync", "db"),
             node("rr", "Read replica", 82, 28, "sky", "async", "db"), node("ddb", "DynamoDB", 82, 78, "mint", "PK/SK", "db")],
            [("app", "w"), ("w", "sb"), ("w", "rr"), ("app", "rr"), ("app", "ddb")],
            [
                step("Writes to the primary", "RDS writes go to the primary instance.", ["w"], [pkt("app", "w", "INSERT")]),
                step("Synchronous standby", "Multi-AZ replicates synchronously to a standby in another AZ.", ["sb"], [pkt("w", "sb", "sync")]),
                step("Failover", "If the primary's AZ fails, DNS flips to the standby in about a minute.", ["sb"], set={"w": {"tint": "rose", "sub": "failed"}, "sb": {"tint": "lilac", "sub": "new primary"}}),
                step("Scale reads and NoSQL", "Read replicas serve reports; DynamoDB handles the high-scale session data.", ["rr", "ddb"], [pkt("app", "rr", "SELECT"), pkt("app", "ddb", "GetItem")]),
            ],
        ),
    },
    {
        "id": "elb-autoscaling", "title": "Load Balancers & Auto Scaling", "category": "compute", "level": "intermediate", "code": "AS",
        "tagline": "ALB/NLB, target groups, health checks and scaling policies.",
        "analogy": "A call centre: the switchboard (load balancer) routes calls to available agents (targets), and the manager (Auto Scaling) calls in more agents when the queue grows and sends them home when it's quiet.",
        "what": "Elastic Load Balancing: ALB (layer 7: HTTP/HTTPS, host/path routing, gRPC, WebSockets, WAF integration), NLB (layer 4: TCP/UDP/TLS, static IPs, millions of requests per second), GWLB (inline appliances). Load balancers send traffic to target groups (instances, IPs, Lambda) that pass health checks. Auto Scaling groups keep a desired number of instances from a launch template across AZs; scaling policies: target tracking (keep CPU at 50%), step, scheduled, predictive. Lifecycle hooks and instance refresh support safe rollouts.",
        "use_cases": ["Web tier scaling with traffic.", "Blue/green with weighted target groups.", "Scheduled scale-up before a daily peak."],
        "key_points": [
            "Target tracking is the simplest, most robust policy.",
            "Health check grace periods avoid killing booting instances.",
            "Terminate TLS at the ALB with ACM certificates (auto-renewed).",
            "Cross-zone load balancing evens traffic across AZs.",
        ],
        "examples": [
            ex("Target tracking policy", "intermediate", "Keep average CPU around 50%.", "bash", """
                aws autoscaling put-scaling-policy \\
                  --auto-scaling-group-name web-asg \\
                  --policy-name cpu50 \\
                  --policy-type TargetTrackingScaling \\
                  --target-tracking-configuration '{"PredefinedMetricSpecification":{"PredefinedMetricType":"ASGAverageCPUUtilization"},"TargetValue":50}'
            """, runnable=False),
            ex("ALB listener rule", "advanced", "Route /api/* to the API target group (CloudFormation).", "yaml", """
                ApiRule:
                  Type: AWS::ElasticLoadBalancingV2::ListenerRule
                  Properties:
                    ListenerArn: !Ref HttpsListener
                    Priority: 10
                    Conditions:
                      - Field: path-pattern
                        Values: ["/api/*"]
                    Actions:
                      - Type: forward
                        TargetGroupArn: !Ref ApiTargetGroup
            """, runnable=False),
        ],
        "commands": ["ALB (L7) · NLB (L4) · GWLB (appliances)", "Target group health check: path, interval, thresholds", "ASG: min / desired / max · launch template", "Policies: target tracking · step · scheduled · predictive", "aws autoscaling start-instance-refresh"],
        "gotchas": ["Health check path that hits the database, so a DB blip kills every instance.", "Scaling on CPU when the bottleneck is connections or queue depth.", "Min capacity of 1 in a single AZ."],
        "interview": [
            qa("intermediate", "ALB vs NLB?", "ALB: HTTP-aware routing (paths, hosts, headers), TLS termination, WAF, redirects. NLB: layer-4 TCP/UDP, ultra-low latency, static/Elastic IPs, preserves source IP, PrivateLink."),
            qa("intermediate", "How does Auto Scaling decide to add instances?", "Scaling policies watch CloudWatch metrics; target tracking adjusts desired capacity to keep a metric (CPU, requests per target) near the target value."),
            qa("advanced", "How do you deploy without downtime on an ASG?", "Instance refresh or blue/green with a new launch template, health checks plus deregistration delay (connection draining), and minimum healthy percentage."),
            qa("basic", "What happens when an instance fails its health check?", "The load balancer stops routing to it; the ASG (with ELB health checks enabled) terminates and replaces it."),
        ],
        "related": ["ec2", "vpc"],
        "flow": flow(
            [node("u", "Users", 8, 50, "slate", "rps ↑"), node("alb", "ALB", 32, 50, "lilac", "HTTPS :443"), node("i1", "EC2 a", 62, 20, "peach", "CPU 80%"),
             node("i2", "EC2 b", 62, 50, "peach", "CPU 80%"), node("i3", "EC2 c", 62, 80, "mint", "launching", hidden=True), node("cw", "CloudWatch", 90, 50, "lemon", "target 50%", "round")],
            [("u", "alb"), ("alb", "i1"), ("alb", "i2"), ("alb", "i3"), ("i1", "cw"), ("i2", "cw")],
            [
                step("Traffic rises", "The ALB spreads requests over two healthy instances.", ["alb", "i1", "i2"], [pkt("u", "alb"), pkt("alb", "i1"), pkt("alb", "i2")]),
                step("Alarm", "Average CPU 80% exceeds the 50% target.", ["cw"], [pkt("i1", "cw", "80%"), pkt("i2", "cw", "80%")]),
                step("Scale out", "The ASG launches a third instance from the launch template.", ["i3"], [pkt("cw", "i3", "+1")], {"i3": {"hidden": False}}),
                step("Healthy, then serve", "After passing health checks it joins the target group; CPU settles near 50%.", ["i3", "alb"], [pkt("alb", "i3")], {"i1": {"sub": "CPU 52%"}, "i2": {"sub": "CPU 51%"}, "i3": {"sub": "CPU 49%", "tint": "peach"}}),
            ],
        ),
    },
    {
        "id": "lambda", "title": "Lambda & Serverless", "category": "compute", "level": "intermediate", "code": "LA",
        "tagline": "Event-driven functions, cold starts, concurrency and API Gateway.",
        "analogy": "A taxi instead of owning a car: it shows up when called, you pay per ride, and sometimes you wait a moment for one to arrive (cold start).",
        "what": "Lambda runs code in response to events (API Gateway/function URLs, S3, SQS, EventBridge, DynamoDB Streams) without managing servers, billed per request and per GB-second, up to 15 minutes per invocation. Each concurrent request uses its own execution environment; new environments incur a cold start (init code runs once and is reused). Concurrency limits (account and reserved) protect downstreams; provisioned concurrency and SnapStart reduce cold starts. Invocation types: synchronous, asynchronous (retries + DLQ/destinations), poll-based (event source mappings with batches).",
        "use_cases": ["REST APIs with API Gateway.", "Image processing on S3 upload.", "Queue consumers and scheduled jobs."],
        "key_points": [
            "Initialize SDK clients outside the handler to reuse them.",
            "Memory setting also scales CPU.",
            "Make handlers idempotent: async and SQS invocations can repeat.",
            "Use environment variables for config, Secrets Manager/Parameter Store for secrets.",
        ],
        "examples": [
            ex("Handler for an S3 event", "basic", "Init code outside the handler runs once per environment.", "python", """
                import json, os, boto3

                s3 = boto3.client("s3")            # reused across warm invocations
                BUCKET_OUT = os.environ["THUMBS_BUCKET"]

                def handler(event, context):
                    for record in event["Records"]:
                        key = record["s3"]["object"]["key"]
                        print(json.dumps({"msg": "processing", "key": key, "request_id": context.aws_request_id}))
                    return {"processed": len(event["Records"])}
            """, runnable=False),
            ex("SAM template: API + function", "intermediate", "Least-privilege policy template and a reserved concurrency cap.", "yaml", """
                AWSTemplateFormatVersion: "2010-09-09"
                Transform: AWS::Serverless-2016-10-31
                Resources:
                  OrdersFn:
                    Type: AWS::Serverless::Function
                    Properties:
                      Runtime: python3.13
                      Handler: app.handler
                      MemorySize: 512
                      Timeout: 10
                      ReservedConcurrentExecutions: 50
                      Policies:
                        - DynamoDBCrudPolicy: { TableName: !Ref OrdersTable }
                      Events:
                        Api:
                          Type: HttpApi
                          Properties: { Path: /orders, Method: post }
                  OrdersTable:
                    Type: AWS::Serverless::SimpleTable
            """, runnable=False),
        ],
        "commands": ["sam build && sam deploy --guided", "aws lambda invoke --function-name f out.json", "Reserved concurrency · provisioned concurrency · SnapStart", "Event source mapping: batch size, batch window, partial batch response", "Powertools for AWS Lambda (logging, tracing, idempotency)"],
        "gotchas": ["Recursive triggers (function writes to the bucket that triggers it).", "Unbounded concurrency overwhelming a database.", "Large deployment packages and heavy init increasing cold starts."],
        "interview": [
            qa("intermediate", "What is a cold start and how do you reduce it?", "The time to create a new execution environment and run init code. Reduce with smaller packages, lighter frameworks, init outside the handler, provisioned concurrency or SnapStart, and choosing faster runtimes/arm64."),
            qa("intermediate", "When is Lambda a bad fit?", "Long-running (>15 min) or steady high-throughput workloads (containers can be cheaper), very low-latency requirements sensitive to cold starts, or workloads needing GPUs or special OS control."),
            qa("advanced", "How does Lambda process SQS messages?", "An event source mapping polls the queue and invokes the function with batches; on success messages are deleted; failures return to the queue after the visibility timeout and go to a DLQ after maxReceiveCount. Use partial batch responses to avoid reprocessing successes."),
            qa("advanced", "How do you protect a database from Lambda concurrency spikes?", "Reserved concurrency to cap the function, RDS Proxy for connection pooling, or buffer writes through SQS."),
        ],
        "related": ["messaging", "databases"],
        "flow": flow(
            [node("ev", "Event", 8, 50, "slate", "API / S3 / SQS", "pill"), node("svc", "Lambda service", 34, 50, "lilac", "routing"), node("e1", "Env 1", 66, 22, "mint", "warm"),
             node("e2", "Env 2", 66, 78, "sky", "cold start", hidden=True), node("ddb", "DynamoDB", 92, 50, "peach", "", "db")],
            [("ev", "svc"), ("svc", "e1"), ("svc", "e2"), ("e1", "ddb"), ("e2", "ddb")],
            [
                step("Event arrives", "An HTTP request reaches the Lambda service through API Gateway.", ["ev", "svc"], [pkt("ev", "svc", "POST /orders")]),
                step("Warm environment", "An idle warm environment runs the handler immediately.", ["e1"], [pkt("svc", "e1", "invoke"), pkt("e1", "ddb", "PutItem")]),
                step("Concurrency grows", "A second simultaneous request needs a new environment: init code runs (cold start).", ["e2"], [pkt("svc", "e2", "init + invoke")], {"e2": {"hidden": False}}),
                step("Reuse", "Both environments stay warm for later requests; idle ones are eventually reclaimed.", ["e1", "e2"], set={"e2": {"sub": "warm", "tint": "mint"}}),
            ],
        ),
    },
    {
        "id": "messaging", "title": "SQS, SNS & EventBridge", "category": "integration-ops", "level": "intermediate", "code": "MS",
        "tagline": "Queues, fan-out topics and event buses for decoupled architectures.",
        "analogy": "SQS is a ticket queue at a deli, SNS is a loudspeaker announcement everyone subscribed hears, and EventBridge is a mail room that reads each envelope and routes it to the right desks by rules.",
        "what": "SQS: fully managed queues. Standard (at-least-once, best-effort order, nearly unlimited throughput) and FIFO (ordered per message group, exactly-once processing within a dedupe window). Visibility timeout hides in-flight messages; DLQs catch failures; long polling reduces cost. SNS: pub/sub topics pushing to SQS, Lambda, HTTP, email, SMS; filter policies; SNS→SQS fan-out. EventBridge: event bus with content-based rules, schema registry, archive/replay, SaaS integrations, Scheduler and Pipes. Step Functions orchestrate multi-step workflows with retries and compensation.",
        "use_cases": ["Order placed → billing, shipping, email (SNS → SQS fan-out or EventBridge).", "Smoothing spiky work with an SQS buffer.", "Cron-like schedules with EventBridge Scheduler."],
        "key_points": [
            "Visibility timeout should exceed processing time (≈6× the Lambda timeout for SQS triggers).",
            "FIFO throughput scales by message group id.",
            "EventBridge for routing many event types; SNS for high-throughput simple fan-out.",
            "Consumers must be idempotent.",
        ],
        "examples": [
            ex("EventBridge rule pattern", "intermediate", "Route only large paid orders to a fraud-check target.", "json", """
                {
                  "source": ["acme.orders"],
                  "detail-type": ["OrderPlaced"],
                  "detail": {
                    "status": ["PAID"],
                    "amount": [{ "numeric": [">=", 1000] }]
                  }
                }
            """, runnable=False),
            ex("SQS with DLQ (CLI)", "basic", "Messages failing 5 times move to the dead-letter queue.", "bash", """
                aws sqs create-queue --queue-name orders-dlq
                aws sqs create-queue --queue-name orders \\
                  --attributes '{"VisibilityTimeout":"60","ReceiveMessageWaitTimeSeconds":"20","RedrivePolicy":"{\\"deadLetterTargetArn\\":\\"arn:aws:sqs:eu-west-1:123456789012:orders-dlq\\",\\"maxReceiveCount\\":\\"5\\"}"}'
            """, runnable=False),
            ex("Publish an event (boto3)", "intermediate", "Producers don't know who consumes.", "python", """
                import json, boto3

                boto3.client("events").put_events(Entries=[{
                    "Source": "acme.orders",
                    "DetailType": "OrderPlaced",
                    "Detail": json.dumps({"orderId": "o-123", "status": "PAID", "amount": 1499}),
                    "EventBusName": "default",
                }])
            """, runnable=False),
        ],
        "commands": ["SQS: Standard vs FIFO · visibility timeout · DLQ · long polling", "SNS: topic → subscriptions (SQS, Lambda, HTTPS) · filter policies", "EventBridge: bus · rule pattern · targets · archive/replay · Scheduler", "Step Functions: Standard vs Express workflows"],
        "gotchas": ["Visibility timeout shorter than processing time → duplicates.", "No DLQ: poison messages retry forever or vanish.", "Using FIFO with a single message group id, capping throughput."],
        "interview": [
            qa("intermediate", "SQS vs SNS vs EventBridge?", "SQS: queue, one consumer group pulls, buffering and retries. SNS: push pub/sub fan-out to many subscribers. EventBridge: event bus with rich content filtering, many AWS/SaaS sources, schema registry and replay."),
            qa("intermediate", "Standard vs FIFO queues?", "Standard: virtually unlimited throughput, at-least-once, best-effort ordering. FIFO: strict ordering per message group and deduplication, with lower (but high) throughput limits."),
            qa("advanced", "How do you implement fan-out with independent retries?", "SNS topic (or EventBridge rule) delivering to one SQS queue per consumer; each consumer has its own DLQ and scaling."),
            qa("advanced", "When use Step Functions instead of chaining queues?", "When the workflow has multiple steps, branching, waits, human approval, retries and compensations that need visibility and state: orchestration instead of hidden choreography."),
        ],
        "related": ["lambda", "observability-well-architected"],
        "flow": flow(
            [node("svc", "Orders service", 8, 50, "sky", "producer"), node("eb", "EventBridge", 36, 50, "lilac", "rules", "round"), node("q1", "billing queue", 66, 18, "lemon", "SQS", "pill"),
             node("q2", "shipping queue", 66, 50, "lemon", "SQS", "pill"), node("fr", "fraud check", 66, 82, "rose", "amount ≥ 1000"), node("dlq", "DLQ", 92, 50, "slate", "failed 5×", "pill")],
            [("svc", "eb"), ("eb", "q1"), ("eb", "q2"), ("eb", "fr"), ("q2", "dlq")],
            [
                step("Publish once", "The orders service emits OrderPlaced and moves on.", ["svc", "eb"], [pkt("svc", "eb", "OrderPlaced")]),
                step("Rules route", "Every rule whose pattern matches gets a copy.", ["q1", "q2"], [pkt("eb", "q1"), pkt("eb", "q2")]),
                step("Content filter", "Only orders ≥ 1000 reach the fraud check.", ["fr"], [pkt("eb", "fr", "1499", "rose")]),
                step("Failures isolated", "Shipping fails repeatedly on one message; it moves to its own DLQ without affecting billing.", ["dlq"], [pkt("q2", "dlq", "poison")]),
            ],
        ),
    },
    {
        "id": "cloudfront-route53", "title": "CloudFront & Route 53", "category": "networking", "level": "intermediate", "code": "CF",
        "tagline": "Edge caching, TLS, routing policies and health-checked DNS failover.",
        "analogy": "Route 53 is the phone book that can send you to the nearest or healthiest branch; CloudFront is a network of local convenience stores stocking popular items so you don't drive to the warehouse.",
        "what": "Route 53 is managed DNS and domain registration with alias records to AWS resources and routing policies: simple, weighted, latency-based, failover (with health checks), geolocation/geoproximity, multivalue. CloudFront is a CDN with hundreds of edge locations: caches content from origins (S3 via OAC, ALB, custom), terminates TLS with ACM certificates (us-east-1), applies cache and origin request policies, runs edge logic (CloudFront Functions, Lambda@Edge), and integrates AWS WAF and Shield for DDoS protection.",
        "use_cases": ["Static website: S3 + CloudFront + Route 53 alias.", "Active-passive DR with failover routing.", "Canary releases with weighted DNS."],
        "key_points": [
            "Alias records are free and work at the zone apex.",
            "DNS TTLs limit how fast failover takes effect.",
            "Cache key = what varies the response; keep it minimal for high hit ratio.",
            "Invalidations cost after the free tier; version file names instead.",
        ],
        "examples": [
            ex("Failover record set", "advanced", "Primary in eu-west-1, secondary in eu-central-1 with a health check.", "json", """
                {
                  "Changes": [
                    {
                      "Action": "UPSERT",
                      "ResourceRecordSet": {
                        "Name": "api.example.com", "Type": "A", "SetIdentifier": "primary", "Failover": "PRIMARY",
                        "HealthCheckId": "abcdef11-2222-3333-4444-555555fedcba",
                        "AliasTarget": { "HostedZoneId": "Z32O12XQLNTSW2", "DNSName": "primary-alb.eu-west-1.elb.amazonaws.com", "EvaluateTargetHealth": true }
                      }
                    },
                    {
                      "Action": "UPSERT",
                      "ResourceRecordSet": {
                        "Name": "api.example.com", "Type": "A", "SetIdentifier": "secondary", "Failover": "SECONDARY",
                        "AliasTarget": { "HostedZoneId": "Z215JYRZR1TBD5", "DNSName": "dr-alb.eu-central-1.elb.amazonaws.com", "EvaluateTargetHealth": true }
                      }
                    }
                  ]
                }
            """, runnable=False),
            ex("Invalidate and inspect cache behaviour", "basic", "Prefer versioned file names; invalidate only when needed.", "bash", """
                aws cloudfront create-invalidation --distribution-id EDFDVBD6EXAMPLE --paths "/index.html"
                curl -sI https://www.example.com/app.3f9c1a.js | grep -i -E "x-cache|age|cache-control"
            """, runnable=False),
        ],
        "commands": ["Route 53 policies: simple · weighted · latency · failover · geolocation · multivalue", "Alias record → CloudFront / ALB / S3 website", "CloudFront: origins, behaviors, cache policy, OAC, ACM cert in us-east-1", "AWS WAF managed rules · Shield Standard (free)"],
        "gotchas": ["ACM certificate for CloudFront created outside us-east-1.", "Forwarding all headers/cookies to the origin, destroying the hit ratio.", "Long DNS TTLs during a planned migration."],
        "interview": [
            qa("intermediate", "How does Route 53 failover routing work?", "Records marked PRIMARY and SECONDARY; health checks (or target health) monitor the primary; when unhealthy, Route 53 answers with the secondary. Effective time depends on health check interval and record TTL."),
            qa("intermediate", "How do you host a static site securely on AWS?", "Private S3 bucket + CloudFront with Origin Access Control, ACM certificate, Route 53 alias, security headers via response headers policy, and WAF if needed."),
            qa("advanced", "Latency vs geolocation routing?", "Latency routing picks the Region with the lowest measured latency for the user. Geolocation routes by the user's location (country/continent), used for compliance or localized content."),
            qa("advanced", "CloudFront Functions vs Lambda@Edge?", "CloudFront Functions: lightweight JS at viewer request/response, sub-millisecond, very cheap (redirects, header tweaks). Lambda@Edge: Node/Python, origin events, network access, longer runtime, higher cost."),
        ],
        "related": ["s3", "elb-autoscaling"],
        "flow": flow(
            [node("u", "User (Mumbai)", 8, 50, "slate"), node("dns", "Route 53", 32, 20, "lilac", "www → CloudFront", "round"), node("edge", "Edge (Mumbai)", 40, 70, "mint", "cache"),
             node("o1", "Origin eu-west-1", 80, 30, "sky", "ALB + S3"), node("o2", "DR eu-central-1", 80, 80, "slate", "standby")],
            [("u", "dns"), ("u", "edge"), ("edge", "o1"), ("edge", "o2")],
            [
                step("DNS lookup", "Route 53 answers with the CloudFront distribution's nearest edge addresses.", ["dns"], [pkt("u", "dns", "www.example.com?"), pkt("dns", "u", "edge IPs")]),
                step("Edge hit", "Cached assets come from the Mumbai edge in a few milliseconds.", ["edge"], [pkt("u", "edge", "GET app.js"), pkt("edge", "u", "HIT", "mint")]),
                step("Miss → origin", "Uncached requests go to the origin over the AWS backbone, then get cached.", ["o1"], [pkt("edge", "o1", "MISS")]),
                step("Region failure", "Health checks fail; failover routing sends origin traffic to the DR Region.", ["o2"], [pkt("edge", "o2", "failover", "lemon")], {"o1": {"tint": "rose", "sub": "unhealthy"}, "o2": {"tint": "sky", "sub": "active"}}),
            ],
        ),
    },
    {
        "id": "observability-well-architected", "title": "CloudWatch, CloudTrail & Well-Architected", "category": "integration-ops", "level": "advanced", "code": "WA",
        "tagline": "Metrics, logs, alarms, audit trails, infrastructure as code and the six pillars.",
        "analogy": "Running a factory: gauges and alarms on the machines (CloudWatch), a security camera log of who touched what (CloudTrail), written blueprints so you can rebuild the factory (IaC), and an inspector's checklist (Well-Architected).",
        "what": "CloudWatch collects metrics, logs (Logs Insights queries), alarms, dashboards and traces (X-Ray/Application Signals). CloudTrail records API calls for auditing and security investigations; Config tracks resource configuration and compliance; GuardDuty detects threats. Infrastructure as code (CloudFormation, CDK, Terraform) makes environments reproducible and reviewable. The Well-Architected Framework has six pillars: operational excellence, security, reliability, performance efficiency, cost optimization and sustainability. Cost tools: Cost Explorer, Budgets, tagging, Savings Plans.",
        "use_cases": ["Alerting on 5xx rate and latency SLOs.", "Investigating who deleted a resource.", "Architecture reviews before launch."],
        "key_points": [
            "Alarm on symptoms users feel (errors, latency), not only CPU.",
            "Enable an organization-wide CloudTrail to a locked-down log archive account.",
            "Tag everything (owner, env, cost-center) for cost allocation.",
            "Encrypt with KMS, rotate secrets, least privilege: security pillar basics.",
        ],
        "examples": [
            ex("Logs Insights: top errors", "intermediate", "Find the noisiest error messages in the last hour.", "text", """
                fields @timestamp, @message
                | filter level = "ERROR"
                | stats count(*) as errors by message
                | sort errors desc
                | limit 10
            """, runnable=False),
            ex("Alarm on ALB 5xx", "intermediate", "Notify an SNS topic when errors spike.", "bash", """
                aws cloudwatch put-metric-alarm --alarm-name web-5xx \\
                  --namespace AWS/ApplicationELB --metric-name HTTPCode_Target_5XX_Count \\
                  --dimensions Name=LoadBalancer,Value=app/web/50dc6c495c0c9188 \\
                  --statistic Sum --period 60 --evaluation-periods 3 --threshold 20 \\
                  --comparison-operator GreaterThanThreshold \\
                  --alarm-actions arn:aws:sns:eu-west-1:123456789012:oncall
            """, runnable=False),
            ex("CDK stack in Python", "advanced", "A versioned, encrypted, private bucket as code.", "python", """
                from aws_cdk import App, Stack, RemovalPolicy, aws_s3 as s3
                from constructs import Construct

                class StorageStack(Stack):
                    def __init__(self, scope: Construct, id: str, **kw):
                        super().__init__(scope, id, **kw)
                        s3.Bucket(self, "Reports",
                                  versioned=True,
                                  encryption=s3.BucketEncryption.KMS_MANAGED,
                                  block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
                                  enforce_ssl=True,
                                  removal_policy=RemovalPolicy.RETAIN)

                app = App()
                StorageStack(app, "storage-dev")
                app.synth()
            """, runnable=False),
        ],
        "commands": ["CloudWatch: metrics · alarms · Logs Insights · dashboards · Synthetics", "CloudTrail: management + data events · org trail", "AWS Config rules · Security Hub · GuardDuty", "cdk deploy · cloudformation deploy · terraform apply", "Six pillars: OpEx · Security · Reliability · Performance · Cost · Sustainability"],
        "gotchas": ["Logs kept forever by default: set retention.", "Click-ops in production with no IaC.", "Alarms nobody receives (no SNS subscription) or that fire constantly and get ignored."],
        "interview": [
            qa("intermediate", "CloudWatch vs CloudTrail vs Config?", "CloudWatch: performance and operational telemetry (metrics, logs, alarms). CloudTrail: audit log of API calls (who did what, when, from where). Config: history of resource configurations and compliance rules."),
            qa("advanced", "Name the Well-Architected pillars and one practice each.", "Operational excellence (IaC, runbooks), security (least privilege, encryption), reliability (multi-AZ, backups, tested recovery), performance efficiency (right-size, managed services), cost optimization (Savings Plans, tagging, autoscaling), sustainability (efficient utilization, Graviton)."),
            qa("advanced", "How do you reduce an unexpectedly high AWS bill?", "Cost Explorer by service/tag, find idle or oversized resources (Compute Optimizer, Trusted Advisor), NAT/data transfer costs, storage lifecycle, Savings Plans for steady usage, Spot for flexible work, and Budgets with alerts."),
            qa("intermediate", "Why infrastructure as code?", "Reproducible environments, code review and history for changes, drift detection, easy rollback and disaster recovery, and fewer manual mistakes."),
        ],
        "related": ["iam", "global-infra"],
        "flow": flow(
            [node("app", "Workload", 12, 50, "sky", "ALB · Lambda · RDS"), node("cw", "CloudWatch", 45, 20, "mint", "metrics + logs"), node("ct", "CloudTrail", 45, 80, "lilac", "API audit"),
             node("al", "Alarm", 78, 20, "rose", "5xx > 20/min", "pill"), node("sns", "On-call", 95, 50, "lemon", "SNS → pager", "round"), node("s3", "Log archive", 78, 80, "slate", "locked bucket", "db")],
            [("app", "cw"), ("app", "ct"), ("cw", "al"), ("al", "sns"), ("ct", "s3")],
            [
                step("Telemetry", "Services emit metrics and logs to CloudWatch automatically.", ["cw"], [pkt("app", "cw", "metrics")]),
                step("Audit trail", "Every API call (who, what, when, from where) goes to CloudTrail and a locked log archive.", ["ct", "s3"], [pkt("app", "ct", "DeleteBucket?"), pkt("ct", "s3")]),
                step("Alarm on symptoms", "5xx errors cross the threshold for 3 minutes.", ["al"], [pkt("cw", "al", "breach", "rose")]),
                step("Notify", "SNS pages the on-call engineer with a link to the dashboard and runbook.", ["sns"], [pkt("al", "sns", "page")]),
            ],
        ),
    },
]

SCENARIOS = [
    {"level": "advanced", "topic": "iam", "q": "An access key for a production IAM user was found in a public GitHub repo.", "a": "Deactivate and delete the key immediately, check CloudTrail for its usage and revert damage, rotate any exposed secrets, then remove long-lived keys entirely: move workloads to IAM roles and humans to Identity Center, enable secret scanning and GuardDuty."},
    {"level": "intermediate", "topic": "vpc", "q": "EC2 instances in a private subnet can't download OS updates.", "a": "The private route table lacks 0.0.0.0/0 → NAT Gateway, the NAT is in a subnet without an IGW route, or SG/NACL egress rules block it. Check with Reachability Analyzer; for AWS services prefer VPC endpoints."},
    {"level": "advanced", "topic": "lambda", "q": "A Lambda consuming SQS overloads the RDS database during traffic spikes.", "a": "Cap concurrency (reserved concurrency or the event source mapping's maximum concurrency), add RDS Proxy for connection pooling, tune batch size, and let the queue absorb the burst."},
    {"level": "intermediate", "topic": "s3", "q": "A security scan reports an S3 bucket with customer files is public.", "a": "Enable Block Public Access at account and bucket level, remove public ACLs/policy statements, review access logs/CloudTrail data events for exposure, serve needed public content via CloudFront OAC, and add a Config rule to detect regressions."},
    {"level": "advanced", "topic": "observability-well-architected", "q": "Your AWS bill doubled this month with no new features.", "a": "Use Cost Explorer grouped by service, usage type and tag to find the jump; common culprits are NAT Gateway data processing, cross-AZ traffic, forgotten instances/volumes, log ingestion, or a runaway Lambda loop. Fix, then set Budgets alerts and anomaly detection."},
]

from .aws_more import CATEGORIES as _MORE_CATEGORIES, SCENARIOS as _MORE_SCENARIOS, TOPICS as _MORE_TOPICS

CATEGORIES += _MORE_CATEGORIES
TOPICS += _MORE_TOPICS
SCENARIOS += _MORE_SCENARIOS
