"""More aws topics, appended to the core module."""

from ._dsl import chain, ex, qa, topic

CATEGORIES = [
    {"id": "security", "title": "Security & Governance", "color": "rose", "blurb": "Identity, encryption, detection and guardrails."},
    {"id": "devops", "title": "DevOps & IaC", "color": "slate", "blurb": "Infrastructure as code, containers registry and fleet ops."},
    {"id": "analytics", "title": "Analytics & Streaming", "color": "peach", "blurb": "Streams, data lakes and query engines."},
]

TOPICS = []

# --- Security & governance -------------------------------------------------------------------------------------------

TOPICS += [
    topic(
        "iam-roles-sts", "IAM Roles, STS & AssumeRole", "security", "intermediate", "RS",
        "Temporary credentials on demand: how workloads and people borrow permissions safely.",
        "A hotel key card: reception (STS) checks who you are against the guest list (trust policy) and hands you a card that opens specific doors (permissions policy) and stops working at checkout (session expiry).",
        "An IAM role is an identity with permissions but no long-term credentials. A principal that is trusted by the role's trust policy calls sts:AssumeRole (or AssumeRoleWithWebIdentity / AssumeRoleWithSAML) and receives an access key id, secret key and session token that expire after 15 minutes to 12 hours. AWS services assume roles for you: EC2 through instance profiles, Lambda through execution roles, EKS pods through IRSA or Pod Identity, ECS tasks through task roles. Cross-account access works by trusting another account's principal in the trust policy, often guarded with an ExternalId condition to prevent the confused-deputy problem. Session policies and session tags can further narrow or label a session at assume time. Every assumption is logged in CloudTrail with the role session name, so you can attribute actions to a human or job. Role chaining (assuming a role from a role session) is limited to a one-hour session.",
        ["Cross-account deployment pipelines assuming a Deploy role in each target account.", "GitHub Actions or GitLab CI authenticating with OIDC instead of stored access keys.", "Third-party SaaS reading your account via a role with an ExternalId.", "Break-glass admin access that is time-bound and audited."],
        ["Trust policy = who can assume; permissions policy = what the session can do.", "Credentials are short-lived and rotate automatically; SDKs refresh them for you.", "Use ExternalId for third parties and aws:SourceArn/SourceAccount for service principals.", "Set a meaningful role-session-name so CloudTrail shows who acted.", "MaxSessionDuration is configurable per role (1 to 12 hours)."],
        [
            ex("Cross-account trust with ExternalId", "intermediate", "Account 111122223333 may assume this role only when it presents the agreed external id.", "json", """
                {
                  "Version": "2012-10-17",
                  "Statement": [
                    {
                      "Effect": "Allow",
                      "Principal": { "AWS": "arn:aws:iam::111122223333:root" },
                      "Action": "sts:AssumeRole",
                      "Condition": { "StringEquals": { "sts:ExternalId": "partner-ref-EXAMPLE" } }
                    }
                  ]
                }
            """, runnable=False),
            ex("GitHub Actions OIDC trust", "advanced", "Only the main branch of one repository can assume the deploy role; no stored keys.", "json", """
                {
                  "Version": "2012-10-17",
                  "Statement": [
                    {
                      "Effect": "Allow",
                      "Principal": { "Federated": "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com" },
                      "Action": "sts:AssumeRoleWithWebIdentity",
                      "Condition": {
                        "StringEquals": {
                          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
                          "token.actions.githubusercontent.com:sub": "repo:acme/web:ref:refs/heads/main"
                        }
                      }
                    }
                  ]
                }
            """, runnable=False),
            ex("Assume a role with boto3", "basic", "Credentials come from the current role or SSO profile; nothing is hardcoded.", "python", """
                import boto3

                sts = boto3.client("sts")
                resp = sts.assume_role(
                    RoleArn="arn:aws:iam::123456789012:role/ReadOnlyAudit",
                    RoleSessionName="audit-alice",
                    DurationSeconds=3600,
                )
                c = resp["Credentials"]
                s3 = boto3.client("s3", aws_access_key_id=c["AccessKeyId"],
                                  aws_secret_access_key=c["SecretAccessKey"],
                                  aws_session_token=c["SessionToken"])
                print([b["Name"] for b in s3.list_buckets()["Buckets"]])
            """, runnable=False),
        ],
        ["aws sts get-caller-identity", "aws sts assume-role --role-arn arn:aws:iam::123456789012:role/Deploy --role-session-name ci", "aws iam update-assume-role-policy --role-name Deploy --policy-document file://trust.json", "~/.aws/config: role_arn + source_profile", "aws iam get-role --role-name Deploy --query Role.MaxSessionDuration"],
        ["Trusting an entire account root when you meant a single role: any admin in that account can then assume it.", "OIDC trust without a sub condition lets every repository on GitHub assume your role.", "Role chaining silently caps sessions at one hour."],
        [
            qa("basic", "Why are roles preferred over IAM users with access keys?", "Roles issue temporary credentials that expire and rotate automatically, so a leaked credential has a short lifetime. There is no secret to store or rotate, and every assumption is attributable in CloudTrail."),
            qa("intermediate", "What does a role trust policy do?", "It is a resource-based policy on the role that names which principals (accounts, roles, services, federated identities) may call an sts:AssumeRole* action, optionally with conditions such as ExternalId, MFA or OIDC claims. Without a matching trust statement nobody can assume the role, regardless of their own permissions."),
            qa("advanced", "What is the confused-deputy problem and how does ExternalId help?", "A third-party service that assumes roles for many customers could be tricked into using its access against another customer's account. Requiring a unique sts:ExternalId per customer in the trust policy ensures the service only assumes your role when acting on your behalf."),
            qa("intermediate", "How does a pod in EKS get AWS permissions?", "Through IRSA (an OIDC provider plus a service-account-annotated role assumed with AssumeRoleWithWebIdentity) or EKS Pod Identity (an agent that vends role credentials to mapped service accounts). Either way, pods get scoped temporary credentials instead of using the node role."),
            qa("advanced", "Both accounts need to agree for cross-account role access. What does each side configure?", "The target account's role trust policy must trust the source principal. The source principal's identity policy must allow sts:AssumeRole on that role ARN. SCPs in either organization can still block it."),
        ],
        ["iam", "global-infra"],
        chain(
            ("Caller", "CI job / app", "Request", "A principal with its own identity calls sts:AssumeRole with a role ARN and session name."),
            ("Trust policy", "who may assume", "Check trust", "STS checks the role's trust policy and its conditions (ExternalId, OIDC sub, MFA).", "AssumeRole"),
            ("STS", "issue session", "Issue credentials", "STS returns an access key id, secret key and session token that expire.", "trusted"),
            ("Session", "temp creds", "Act", "The caller uses the session; permissions are the role policy intersected with any session policy.", "creds"),
            ("CloudTrail", "audit", "Audit", "Every API call is logged with the assumed role and session name.", "events"),
        ),
    ),
    topic(
        "iam-policy-evaluation", "Policy Evaluation, Boundaries & SCPs", "security", "advanced", "PE",
        "How identity, resource, boundary, session and organization policies combine into one decision.",
        "Several locks on the same door: the building owner (SCP), your manager's limit (boundary) and your own key (identity policy) must all agree; one red light (explicit deny) anywhere keeps it shut.",
        "Every request starts as an implicit deny. AWS gathers all applicable policies: SCPs and RCPs from AWS Organizations, resource-based policies, identity-based policies, permissions boundaries and session policies. An explicit Deny in any of them ends evaluation with a deny. For an allow, every guardrail layer in play (SCP, boundary, session policy) must permit the action, and an identity-based or resource-based policy must grant it. SCPs never grant permissions; they only cap what identities in member accounts can do and do not affect the management account. Within one account, a resource policy that names a principal directly can grant access even without an identity policy; across accounts both sides must allow. Permissions boundaries let you delegate role creation to developers while ensuring their roles can never exceed a ceiling. Tools such as the IAM policy simulator and IAM Access Analyzer help you prove what a policy actually allows.",
        ["Delegating role creation to teams with a mandatory permissions boundary.", "Org-wide guardrails: deny disabling CloudTrail, deny leaving approved Regions.", "Debugging an AccessDenied that only happens in one account.", "Attribute-based access control (ABAC) with tags."],
        ["Explicit Deny always wins; there is no allow override.", "Effective permissions = intersection of guardrails, then union of grants.", "SCPs and boundaries filter; they never add permissions.", "NotAction with Deny is a common guardrail pattern; NotAction with Allow is risky.", "Error messages now often name the policy type that denied the request."],
        [
            ex("Permissions boundary for delegated roles", "advanced", "Roles created by developers can use app services but never touch IAM or the boundary itself.", "json", """
                {
                  "Version": "2012-10-17",
                  "Statement": [
                    {
                      "Sid": "AllowAppServices",
                      "Effect": "Allow",
                      "Action": ["s3:*", "dynamodb:*", "sqs:*", "logs:*", "cloudwatch:*"],
                      "Resource": "*"
                    },
                    {
                      "Sid": "DenyIamChanges",
                      "Effect": "Deny",
                      "Action": ["iam:*", "organizations:*"],
                      "Resource": "*"
                    }
                  ]
                }
            """, runnable=False),
            ex("ABAC: only touch resources of your team", "advanced", "Allow EC2 start/stop only when the resource tag matches the caller's principal tag.", "json", """
                {
                  "Version": "2012-10-17",
                  "Statement": [
                    {
                      "Effect": "Allow",
                      "Action": ["ec2:StartInstances", "ec2:StopInstances"],
                      "Resource": "arn:aws:ec2:*:123456789012:instance/*",
                      "Condition": { "StringEquals": { "aws:ResourceTag/team": "${aws:PrincipalTag/team}" } }
                    }
                  ]
                }
            """, runnable=False),
            ex("Simulate before you ship", "intermediate", "Ask IAM whether a role can perform an action on a resource.", "bash", """
                aws iam simulate-principal-policy \\
                  --policy-source-arn arn:aws:iam::123456789012:role/app \\
                  --action-names s3:GetObject s3:PutObject \\
                  --resource-arns arn:aws:s3:::acme-reports/finance/q1.csv
                aws accessanalyzer validate-policy --policy-type IDENTITY_POLICY \\
                  --policy-document file://policy.json
            """, runnable=False),
        ],
        ["aws iam simulate-principal-policy", "aws iam put-role-permissions-boundary --role-name r --permissions-boundary arn", "aws accessanalyzer validate-policy", "aws organizations list-policies --filter SERVICE_CONTROL_POLICY", "aws iam get-account-authorization-details"],
        ["Expecting an SCP to grant access: it only limits.", "Boundary not enforced on role creation: require iam:PermissionsBoundary in the creator's policy or the delegation is bypassable.", "SCPs do not apply to the management account, so do not run workloads there."],
        [
            qa("intermediate", "Can an SCP grant permissions?", "No. An SCP defines the maximum permissions for principals in member accounts; identities still need identity or resource policies that allow the action. With the default FullAWSAccess SCP attached, only your deny statements restrict."),
            qa("advanced", "Walk through the evaluation logic for a same-account request.", "Implicit deny, then any explicit Deny in any policy type denies. Next the SCPs (and RCPs) must allow, the resource policy may grant directly, then the identity policy must allow while the permissions boundary and session policy also allow. If no grant survives the intersections, the result is an implicit deny."),
            qa("advanced", "How do you safely let developers create IAM roles?", "Allow iam:CreateRole only with a condition that iam:PermissionsBoundary equals an approved boundary ARN, deny modifying or deleting that boundary, and deny removing boundaries from roles. Their roles then can never exceed the boundary."),
            qa("intermediate", "What is the difference between a resource-based policy and an identity-based policy?", "Identity policies attach to users, groups or roles and say what that principal can do. Resource policies attach to a resource such as an S3 bucket, KMS key or SQS queue and include a Principal element saying who can access it; they are what make cross-account access possible."),
        ],
        ["iam", "global-infra"],
        chain(
            ("Request", "action+resource", "Context", "AWS builds the request context: principal, action, resource, conditions."),
            ("Deny?", "any policy", "Explicit deny", "Any explicit Deny in any policy ends evaluation with DENY.", "evaluate"),
            ("SCP / RCP", "org guardrail", "Organization", "Service and resource control policies must permit the action.", "no deny"),
            ("Boundary", "ceiling", "Boundary & session", "Permissions boundary and session policy must also permit it.", "in scope"),
            ("Grant", "identity/resource", "Allow needed", "An identity or resource policy must allow the action.", "in scope"),
            ("Decision", "ALLOW or DENY", "Result", "All layers agree: ALLOW. Otherwise implicit DENY.", "allowed"),
        ),
    ),
    topic(
        "organizations-control-tower", "AWS Organizations & Control Tower", "security", "advanced", "OR",
        "Many accounts, one governance model: OUs, SCPs, landing zones and account vending.",
        "A franchise: head office (management account) sets rules every branch must follow (SCPs), groups branches by region or type (OUs), and Control Tower is the playbook that opens a new compliant branch in an afternoon.",
        "AWS Organizations groups accounts into a tree of organizational units (OUs) under one management account, with consolidated billing and shared volume discounts. Policies attach to the root, OUs or accounts: SCPs and RCPs as permission guardrails, plus tag, backup and AI opt-out policies. Trusted access lets services such as CloudTrail, Config, GuardDuty, Security Hub and IAM Identity Center operate organization-wide, often from a delegated administrator account rather than the management account. Control Tower builds a landing zone on top: a Log Archive account, an Audit (security tooling) account, preventive controls (SCPs), detective controls (Config rules) and proactive controls (CloudFormation hooks). Account Factory vends new accounts with baselines applied, and Account Factory for Terraform (AFT) does the same via pipelines. A typical OU layout is Security, Infrastructure, Workloads (Prod, Non-Prod), Sandbox and Suspended.",
        ["Isolating prod and dev in separate accounts with different guardrails.", "Central security tooling and an immutable log archive.", "Self-service account vending for teams.", "Consolidated billing with Savings Plans shared across accounts."],
        ["The management account should hold almost nothing: billing and org admin only.", "Use delegated administrators for security services.", "Accounts are the strongest isolation boundary in AWS.", "Control Tower drift happens if you change its resources by hand; re-register the OU.", "Test SCPs on a sandbox OU before attaching to production."],
        [
            ex("SCP: protect the audit trail", "intermediate", "Nobody in member accounts can stop or delete CloudTrail or Config.", "json", """
                {
                  "Version": "2012-10-17",
                  "Statement": [
                    {
                      "Sid": "ProtectAudit",
                      "Effect": "Deny",
                      "Action": [
                        "cloudtrail:StopLogging",
                        "cloudtrail:DeleteTrail",
                        "config:StopConfigurationRecorder",
                        "config:DeleteConfigurationRecorder"
                      ],
                      "Resource": "*"
                    }
                  ]
                }
            """, runnable=False),
            ex("Create an OU and move an account", "basic", "Organize accounts by environment.", "bash", """
                aws organizations create-organizational-unit --parent-id r-ab12 --name Workloads-Prod
                aws organizations move-account --account-id 123456789012 \\
                  --source-parent-id r-ab12 --destination-parent-id ou-ab12-11111111
                aws organizations attach-policy --policy-id p-examplescp --target-id ou-ab12-11111111
            """, runnable=False),
        ],
        ["aws organizations describe-organization", "aws organizations list-accounts", "aws organizations create-policy --type SERVICE_CONTROL_POLICY", "aws organizations register-delegated-administrator", "Control Tower: Account Factory · controls · landing zone"],
        ["Running workloads in the management account, where SCPs do not apply.", "An over-broad Region-deny SCP that blocks global services (IAM, CloudFront, Route 53).", "Closing an account is not instant; it stays suspended for 90 days."],
        [
            qa("basic", "Why use multiple AWS accounts instead of one?", "Accounts give hard boundaries for blast radius, IAM, quotas and billing. Separating prod from dev, and security tooling from workloads, means a compromise or mistake in one does not reach the others."),
            qa("intermediate", "What does Control Tower add on top of Organizations?", "An opinionated landing zone: log archive and audit accounts, Identity Center setup, a library of preventive, detective and proactive controls, drift detection and Account Factory for vending baseline-compliant accounts."),
            qa("advanced", "What is a delegated administrator and why use it?", "A member account registered to administer an organization-wide service such as GuardDuty or Security Hub. It keeps day-to-day security operations out of the management account, which should be tightly restricted because SCPs cannot constrain it."),
            qa("advanced", "SCP vs RCP?", "SCPs limit what principals in your accounts can do. Resource control policies limit what can be done to resources in your accounts, including by external principals, which helps enforce a data perimeter (for example, only principals from your org can access your S3 buckets)."),
        ],
        ["iam", "global-infra", "observability-well-architected"],
        chain(
            ("Management", "org root", "Organization", "The management account owns the org and billing; it runs no workloads."),
            ("OUs", "Security/Prod/Dev", "Structure", "Accounts are grouped into OUs that share policies.", "tree"),
            ("Guardrails", "SCP · Config", "Controls", "Preventive SCPs and detective Config rules attach to OUs.", "attach"),
            ("Factory", "vend account", "Vend", "Account Factory creates a new account with baselines and SSO access.", "request"),
            ("Log archive", "central logs", "Centralize", "CloudTrail and Config from every account flow to an immutable archive.", "logs"),
        ),
    ),
    topic(
        "identity-center", "IAM Identity Center (SSO)", "security", "basic", "IC",
        "One login for humans across every account, with short-lived credentials for console and CLI.",
        "A company badge that works at every office: HR (your identity provider) issues it once, and each building (account) decides which floors (permission sets) your badge opens.",
        "IAM Identity Center is the recommended way for humans to access AWS. It connects to an identity source (its own directory, Active Directory, or an external IdP such as Entra ID, Okta or Google via SAML 2.0 and SCIM provisioning). Administrators define permission sets, which are templates of IAM policies, and assign users or groups to permission sets in specific accounts. Identity Center then creates matching roles in each account and users sign in to an access portal to pick an account and role. The CLI uses aws configure sso and aws sso login to obtain cached short-lived credentials, so no access keys sit on laptops. MFA can be enforced centrally, and session duration is set per permission set. Applications can also use Identity Center as an OIDC/SAML identity provider.",
        ["Workforce access to dozens of accounts without IAM users.", "Federating corporate Entra ID or Okta groups into AWS roles.", "Developer CLI access with automatic credential expiry.", "Temporary elevated access workflows."],
        ["Permission sets become roles named AWSReservedSSO_<set>_<hash> in each account.", "SCIM keeps users and groups in sync with your IdP.", "Assign groups, not individual users.", "Use customer-managed policies in permission sets for reuse across accounts."],
        [
            ex("Configure the CLI with SSO", "basic", "Interactive setup, then short-lived credentials on each login.", "bash", """
                aws configure sso --profile dev
                aws sso login --profile dev
                aws sts get-caller-identity --profile dev
                aws s3 ls --profile dev
            """, runnable=False),
            ex("~/.aws/config profile", "basic", "The resulting profile: no secrets, only pointers to the SSO session.", "text", """
                [sso-session corp]
                sso_start_url = https://example.awsapps.com/start
                sso_region = eu-west-1
                sso_registration_scopes = sso:account:access

                [profile dev]
                sso_session = corp
                sso_account_id = 123456789012
                sso_role_name = DeveloperAccess
                region = eu-west-1
            """, runnable=False),
            ex("Assign a group to a permission set", "intermediate", "Give the platform group admin in one account.", "bash", """
                aws sso-admin create-account-assignment \\
                  --instance-arn arn:aws:sso:::instance/ssoins-EXAMPLE \\
                  --target-id 123456789012 --target-type AWS_ACCOUNT \\
                  --permission-set-arn arn:aws:sso:::permissionSet/ssoins-EXAMPLE/ps-EXAMPLE \\
                  --principal-type GROUP --principal-id 11111111-2222-3333-4444-555555555555
            """, runnable=False),
        ],
        ["aws configure sso", "aws sso login --profile p", "aws sso logout", "aws sso-admin list-permission-sets --instance-arn arn", "export AWS_PROFILE=dev"],
        ["Keeping old IAM users with console passwords alongside SSO.", "Editing the AWSReservedSSO roles directly; changes are overwritten by the permission set.", "Very long session durations that defeat the point of short-lived credentials."],
        [
            qa("basic", "Why use Identity Center instead of IAM users?", "One identity per human, managed in your IdP, with MFA and offboarding in one place. Users get short-lived role credentials per account instead of long-lived passwords and access keys in each account."),
            qa("intermediate", "What is a permission set?", "A template of managed, customer-managed and inline policies plus session settings. When assigned to a user or group in an account, Identity Center provisions a corresponding IAM role there."),
            qa("intermediate", "How does SCIM fit in?", "SCIM automatically provisions and deprovisions users and groups from your external IdP into Identity Center, so group membership changes in Okta or Entra ID immediately change AWS access."),
            qa("basic", "How do developers use the CLI with Identity Center?", "They run aws configure sso once and aws sso login per session; the CLI opens a browser for authentication and caches temporary credentials that the SDKs read through the profile."),
        ],
        ["iam", "global-infra"],
        chain(
            ("User", "browser / CLI", "Sign in", "The user runs aws sso login or opens the access portal."),
            ("IdP", "Okta · Entra ID", "Authenticate", "The external IdP verifies password and MFA and returns a SAML assertion.", "SAML"),
            ("Identity Ctr", "permission sets", "Authorize", "Identity Center maps group membership to account + permission set assignments.", "groups"),
            ("Account role", "AWSReservedSSO", "Assume", "Temporary credentials for the provisioned role are issued.", "creds"),
        ),
    ),
    topic(
        "kms-encryption", "KMS & Envelope Encryption", "security", "intermediate", "KM",
        "Managed keys that never leave the HSM, and the data-key pattern that encrypts everything else.",
        "A bank vault (KMS) keeps the master key and never lends it out. When you need to lock a box, the vault hands you a fresh small key plus a copy of it sealed by the master key; you lock the box, throw away the small key and tape the sealed copy to the box.",
        "AWS KMS manages keys stored in FIPS-validated hardware security modules; the key material of a KMS key never leaves KMS unencrypted. Direct Encrypt is limited to 4 KB, so services use envelope encryption: GenerateDataKey returns a plaintext data key and the same key encrypted under the KMS key. You encrypt data locally with AES-256-GCM, discard the plaintext key and store the encrypted data key next to the ciphertext; to decrypt, call KMS Decrypt on the data key. Access is controlled by the key policy (the primary resource policy), IAM policies when the key policy allows them, and grants for services. Key types include AWS owned, AWS managed (aws/s3) and customer managed keys, which you can rotate automatically, share cross-account and audit in CloudTrail. Encryption context binds additional authenticated data to a ciphertext and appears in audit logs. Multi-Region keys and external key stores (XKS) or CloudHSM-backed custom key stores cover special requirements.",
        ["Server-side encryption for S3, EBS, RDS, DynamoDB with a customer managed key.", "Application-level envelope encryption of sensitive fields.", "Cross-account sharing of encrypted snapshots.", "Crypto-shredding: disable or schedule deletion of a key to make data unreadable."],
        ["Key policy is mandatory; without it nobody, not even admins, can use the key.", "Use encryption context and kms:EncryptionContext conditions to scope use.", "Automatic rotation keeps old key material so old ciphertexts still decrypt.", "Deleting a key has a 7 to 30 day waiting period and is irreversible.", "KMS has request quotas; S3 Bucket Keys reduce calls and cost."],
        [
            ex("Envelope encryption with AES-256-GCM", "advanced", "Data key from KMS, local authenticated encryption, only the encrypted key is stored.", "python", """
                import os
                import boto3
                from cryptography.hazmat.primitives.ciphers.aead import AESGCM

                kms = boto3.client("kms")
                ctx = {"tenant": "acme", "purpose": "invoice"}

                def encrypt(plaintext: bytes) -> dict:
                    dk = kms.generate_data_key(KeyId="alias/app-data", KeySpec="AES_256", EncryptionContext=ctx)
                    nonce = os.urandom(12)
                    ct = AESGCM(dk["Plaintext"]).encrypt(nonce, plaintext, b"invoice-v1")
                    return {"key": dk["CiphertextBlob"], "nonce": nonce, "ct": ct}

                def decrypt(blob: dict) -> bytes:
                    key = kms.decrypt(CiphertextBlob=blob["key"], EncryptionContext=ctx)["Plaintext"]
                    return AESGCM(key).decrypt(blob["nonce"], blob["ct"], b"invoice-v1")
            """, runnable=False),
            ex("Key policy: admins vs users", "advanced", "Separate key administration from key usage, and only via S3 for the app role.", "json", """
                {
                  "Version": "2012-10-17",
                  "Statement": [
                    {
                      "Sid": "AccountRoot",
                      "Effect": "Allow",
                      "Principal": { "AWS": "arn:aws:iam::123456789012:root" },
                      "Action": "kms:*",
                      "Resource": "*"
                    },
                    {
                      "Sid": "AppUseViaS3",
                      "Effect": "Allow",
                      "Principal": { "AWS": "arn:aws:iam::123456789012:role/app" },
                      "Action": ["kms:Encrypt", "kms:Decrypt", "kms:GenerateDataKey"],
                      "Resource": "*",
                      "Condition": { "StringEquals": { "kms:ViaService": "s3.eu-west-1.amazonaws.com" } }
                    }
                  ]
                }
            """, runnable=False),
            ex("Create and rotate a key", "basic", "Customer managed symmetric key with yearly automatic rotation.", "bash", """
                aws kms create-key --description "app data" --key-spec SYMMETRIC_DEFAULT
                aws kms create-alias --alias-name alias/app-data --target-key-id 1234abcd-12ab-34cd-56ef-1234567890ab
                aws kms enable-key-rotation --key-id alias/app-data
            """, runnable=False),
        ],
        ["aws kms create-key · create-alias", "aws kms enable-key-rotation --key-id alias/x", "aws kms generate-data-key --key-id alias/x --key-spec AES_256", "aws kms schedule-key-deletion --pending-window-in-days 30", "aws kms list-grants --key-id alias/x"],
        ["Removing the account root statement from the key policy and locking everyone out.", "Calling KMS Encrypt for large payloads instead of envelope encryption.", "Sharing encrypted snapshots cross-account with an AWS managed key, which cannot be shared; use a customer managed key."],
        [
            qa("intermediate", "Explain envelope encryption.", "KMS generates a data key and returns it both in plaintext and encrypted under a KMS key. You encrypt data locally with the plaintext key (AES-256-GCM), discard it, and store the encrypted data key with the ciphertext. Decryption sends only the small encrypted key to KMS, which keeps the master key inside the HSM and avoids the 4 KB limit."),
            qa("intermediate", "AWS managed key vs customer managed key?", "AWS managed keys (aws/service) are created and rotated by AWS, and you cannot edit their policy or share them cross-account. Customer managed keys give you control of the key policy, rotation, grants, cross-account use and deletion, at a monthly cost."),
            qa("advanced", "What is encryption context?", "Non-secret key-value pairs bound to the ciphertext as additional authenticated data. Decrypt fails unless the exact same context is supplied, it appears in CloudTrail, and key policies can require specific context values."),
            qa("advanced", "How does key rotation affect existing data?", "Automatic rotation creates new backing key material for the same key ID; KMS keeps old material so existing ciphertexts still decrypt and new encryptions use the new material. No re-encryption is needed."),
        ],
        ["s3", "iam", "databases"],
        chain(
            ("App", "has plaintext", "Request key", "The app calls GenerateDataKey for alias/app-data with an encryption context."),
            ("KMS", "HSM-backed", "Data key", "KMS returns a plaintext data key and the same key encrypted under the KMS key.", "GenerateDataKey"),
            ("AES-256-GCM", "local encrypt", "Encrypt locally", "The app encrypts the data with the plaintext key, then wipes it from memory.", "data key"),
            ("Storage", "ct + enc key", "Store", "Ciphertext, nonce and encrypted data key are stored together.", "ciphertext"),
            ("Decrypt", "KMS Decrypt", "Read back", "To read, send the encrypted data key to KMS, which checks policy and context.", "enc key"),
        ),
    ),
    topic(
        "secrets-parameter-store", "Secrets Manager & Parameter Store", "security", "basic", "SP",
        "Keep passwords and config out of code, fetch them at runtime, and rotate them automatically.",
        "A key safe at the office reception: staff sign out the key they are allowed, every checkout is logged, and the locks are re-keyed on a schedule so copies stop working.",
        "AWS Secrets Manager stores secrets such as database credentials and API tokens encrypted with KMS, controls access with IAM and resource policies, and can rotate them on a schedule with a Lambda function; managed rotation exists for RDS, Aurora, Redshift and DocumentDB. Systems Manager Parameter Store holds configuration and secrets as String, StringList or SecureString (KMS-encrypted) parameters in a hierarchy like /app/prod/db/host. Parameter Store standard tier is free and good for config; Secrets Manager costs per secret but adds rotation, cross-Region replication, versioning stages (AWSCURRENT, AWSPENDING, AWSPREVIOUS) and native integrations. Applications fetch secrets at startup or on demand via the SDK, a caching client, the Lambda extension, ECS/EKS secret injection or the Secrets Store CSI driver. RDS can manage its master password in Secrets Manager directly. Never bake secrets into AMIs, images, environment files in Git or CloudFormation templates.",
        ["Database credentials rotated every 30 days without app downtime.", "Feature flags and endpoints per environment in Parameter Store.", "Injecting secrets into ECS task definitions or EKS pods.", "Sharing a secret with another account via a resource policy."],
        ["Grant secretsmanager:GetSecretValue on specific secret ARNs only.", "Cache secrets in the app to cut latency and cost.", "Rotation requires the app to tolerate changing credentials (re-fetch on auth failure).", "SecureString uses KMS; choose a customer managed key for cross-account access."],
        [
            ex("Store and read a secret", "basic", "The value is read from a local file you do not commit, never typed inline.", "bash", """
                aws secretsmanager create-secret --name prod/orders/db \\
                  --kms-key-id alias/app-data --secret-string file://db-secret.json
                aws secretsmanager get-secret-value --secret-id prod/orders/db \\
                  --query SecretString --output text
                aws secretsmanager rotate-secret --secret-id prod/orders/db \\
                  --rotation-rules AutomaticallyAfterDays=30
            """, runnable=False),
            ex("Fetch at runtime with boto3", "basic", "No secret in code or config, only the secret name.", "python", """
                import json, os
                import boto3

                sm = boto3.client("secretsmanager")
                secret = json.loads(sm.get_secret_value(SecretId=os.environ["DB_SECRET_ID"])["SecretString"])
                dsn = f"postgresql://{secret['username']}@{secret['host']}:5432/orders"
                # pass secret["password"] to the driver separately, never log it
            """, runnable=False),
            ex("Parameter hierarchy", "intermediate", "Config and an encrypted parameter for one environment.", "bash", """
                aws ssm put-parameter --name /orders/prod/api-url --type String --value https://api.example.com
                aws ssm put-parameter --name /orders/prod/webhook-token --type SecureString \\
                  --key-id alias/app-data --value "EXAMPLE-ONLY-not-a-real-secret"
                aws ssm get-parameters-by-path --path /orders/prod --with-decryption
            """, runnable=False),
        ],
        ["aws secretsmanager create-secret --name n --secret-string file://s.json", "aws secretsmanager get-secret-value --secret-id n", "aws secretsmanager rotate-secret --secret-id n", "aws ssm get-parameter --name /a/b --with-decryption", "aws ssm get-parameters-by-path --path /app/prod --recursive"],
        ["Putting secrets in Lambda or ECS plain environment variables visible in the console.", "Logging the secret value while debugging.", "Rotation Lambda in a private subnet with no route to Secrets Manager (add a VPC endpoint)."],
        [
            qa("basic", "Secrets Manager vs Parameter Store?", "Both store encrypted values with IAM control. Secrets Manager adds built-in rotation, replication and versioning stages at a per-secret cost; Parameter Store is cheaper (standard tier free) and suits configuration and simple SecureStrings without rotation."),
            qa("intermediate", "How does Secrets Manager rotation work?", "A rotation Lambda runs four steps: createSecret (new AWSPENDING version), setSecret (change it in the database), testSecret, and finishSecret (move AWSCURRENT to the new version). Apps reading AWSCURRENT get the new value; AWSPREVIOUS remains briefly for rollback."),
            qa("intermediate", "How should a container on ECS get a database password?", "Reference the secret ARN in the task definition's secrets section; the ECS agent fetches it with the task execution role and injects it as an environment variable at start. The task role or execution role needs GetSecretValue on that ARN only."),
            qa("advanced", "A secret was accidentally committed to Git. What do you do?", "Treat it as compromised: rotate it immediately at the source, check CloudTrail and application logs for misuse, purge it from history if needed, and add secret scanning in CI and pre-commit hooks. Rewriting history alone is not enough."),
        ],
        ["iam", "lambda", "databases"],
        chain(
            ("App", "secret name only", "Ask", "The app knows only the secret's name via an env var."),
            ("IAM", "GetSecretValue", "Authorize", "IAM checks the app role may read this secret ARN.", "request"),
            ("Secrets Mgr", "AWSCURRENT", "Retrieve", "Secrets Manager decrypts the current version using KMS.", "allowed"),
            ("Cache", "in memory", "Cache", "The app caches the value for a few minutes to limit calls.", "secret"),
            ("Rotation", "Lambda · 30 days", "Rotate", "On schedule, a Lambda creates, sets, tests and promotes a new version.", "rotate"),
        ),
    ),
    topic(
        "s3-security", "S3 Security: Policies, BPA & SSE-KMS", "security", "intermediate", "SX",
        "Lock buckets down by default, grant precisely, encrypt with KMS and require TLS.",
        "A storage unit facility: the gate (Block Public Access) is locked for everyone by default, the rental agreement (bucket policy) lists who may enter, and every box is sealed (SSE-KMS) before it goes on the shelf.",
        "S3 access is the union of identity policies and bucket policies, filtered by Block Public Access (BPA), SCPs/RCPs and VPC endpoint policies. Block Public Access at account and bucket level overrides any policy or ACL that would make data public and should be on everywhere except deliberate public buckets, which are better served via CloudFront with Origin Access Control. Object Ownership set to Bucket owner enforced disables ACLs so only policies matter. All new objects are encrypted at rest (SSE-S3 by default); SSE-KMS with a customer managed key adds key-level access control and audit, and S3 Bucket Keys cut KMS request costs. Bucket policies commonly deny requests without aws:SecureTransport, deny unencrypted or wrong-key uploads, and restrict access to your organization (aws:PrincipalOrgID) or a VPC endpoint (aws:SourceVpce). Access Points and Access Grants simplify per-application or per-user access on shared buckets. IAM Access Analyzer for S3 flags buckets shared outside your zone of trust.",
        ["Private data lake buckets shared with specific roles only.", "Enforcing TLS and KMS on every upload.", "Restricting a bucket to traffic from one VPC endpoint.", "Serving a static site via CloudFront OAC without a public bucket."],
        ["Turn on account-level Block Public Access.", "Disable ACLs with Object Ownership: Bucket owner enforced.", "Deny aws:SecureTransport false in every bucket policy.", "SSE-KMS readers need kms:Decrypt on the key too.", "Use Access Analyzer and Macie to find exposure and sensitive data."],
        [
            ex("Bucket policy: TLS only, org only", "intermediate", "Deny plain HTTP and principals outside the organization.", "json", """
                {
                  "Version": "2012-10-17",
                  "Statement": [
                    {
                      "Sid": "DenyInsecureTransport",
                      "Effect": "Deny",
                      "Principal": "*",
                      "Action": "s3:*",
                      "Resource": ["arn:aws:s3:::acme-data", "arn:aws:s3:::acme-data/*"],
                      "Condition": { "Bool": { "aws:SecureTransport": "false" } }
                    },
                    {
                      "Sid": "DenyOutsideOrg",
                      "Effect": "Deny",
                      "Principal": "*",
                      "Action": "s3:*",
                      "Resource": ["arn:aws:s3:::acme-data", "arn:aws:s3:::acme-data/*"],
                      "Condition": { "StringNotEquals": { "aws:PrincipalOrgID": "o-exampleorgid" } }
                    }
                  ]
                }
            """, runnable=False),
            ex("Default SSE-KMS and Block Public Access", "basic", "Bucket-level defaults with a Bucket Key to reduce KMS calls.", "bash", """
                aws s3api put-public-access-block --bucket acme-data --public-access-block-configuration \\
                  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
                aws s3api put-bucket-ownership-controls --bucket acme-data \\
                  --ownership-controls 'Rules=[{ObjectOwnership=BucketOwnerEnforced}]'
                aws s3api put-bucket-encryption --bucket acme-data --server-side-encryption-configuration \\
                  '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"aws:kms","KMSMasterKeyID":"alias/app-data"},"BucketKeyEnabled":true}]}'
            """, runnable=False),
        ],
        ["aws s3control put-public-access-block --account-id 123456789012", "aws s3api get-bucket-policy-status --bucket b", "aws s3api put-bucket-encryption", "aws accessanalyzer list-findings", "aws s3api put-bucket-ownership-controls"],
        ["Granting s3:GetObject but forgetting kms:Decrypt on the bucket's KMS key, causing AccessDenied.", "A Deny with NotPrincipal or broad conditions locking out your own admins.", "Pre-signed URLs with long expiry shared widely."],
        [
            qa("basic", "What does Block Public Access do?", "It is a set of four settings, at account or bucket level, that block or ignore public ACLs and reject or neutralize public bucket policies. It overrides any grant that would make data public, which prevents accidental exposure."),
            qa("intermediate", "SSE-S3 vs SSE-KMS vs SSE-C?", "SSE-S3 uses S3-managed keys with no extra control. SSE-KMS uses a KMS key, adding key-policy access control, CloudTrail audit and the ability to revoke access by disabling the key. SSE-C means you provide the key on each request and S3 does not store it."),
            qa("intermediate", "How do you force all access to a bucket over TLS?", "Add a bucket policy statement that denies s3:* for all principals when aws:SecureTransport is false. Optionally also require a minimum TLS version with s3:TlsVersion."),
            qa("advanced", "How do you restrict a bucket so it is reachable only from your VPC?", "Create an S3 gateway or interface endpoint and add a bucket policy that denies requests where aws:SourceVpce is not your endpoint ID (with an exception for admin roles if needed). Combine with an endpoint policy that allows only your buckets to prevent exfiltration."),
        ],
        ["s3", "iam", "cloudfront-route53"],
        chain(
            ("Request", "GetObject", "Arrive", "A principal requests an object over HTTPS."),
            ("BPA", "public blocked", "Public check", "Block Public Access neutralizes any public grant.", "request"),
            ("Bucket policy", "TLS · org · vpce", "Policy", "Deny statements enforce TLS, org membership and endpoint.", "not public"),
            ("IAM", "identity policy", "Grant", "The caller's role must allow s3:GetObject on the prefix.", "pass"),
            ("KMS", "kms:Decrypt", "Decrypt", "S3 asks KMS to decrypt the object's data key; the caller needs kms:Decrypt.", "allowed"),
        ),
    ),
    topic(
        "guardduty-security-hub", "GuardDuty, Security Hub & Inspector", "security", "intermediate", "GD",
        "Managed threat detection, vulnerability scanning and one dashboard for security findings.",
        "A building's security desk: motion sensors and cameras (GuardDuty) spot suspicious behaviour, an inspector checks the locks and wiring (Inspector), and the duty manager's board (Security Hub) collects every alert in one place.",
        "Amazon GuardDuty analyses CloudTrail management and data events, VPC Flow Logs and DNS logs, plus optional EKS audit logs, runtime monitoring, S3, RDS login, Lambda network and malware protection, to detect threats such as credential exfiltration, crypto mining, port scanning and calls from known malicious IPs. It needs no agents for the core sources and is enabled organization-wide from a delegated administrator. Amazon Inspector continuously scans EC2, ECR images and Lambda functions for CVEs and network reachability. AWS Security Hub aggregates findings from GuardDuty, Inspector, Macie, IAM Access Analyzer, Config and partners in the AWS Security Finding Format, and runs security standards such as AWS Foundational Security Best Practices and CIS. Amazon Detective helps investigate findings with graph-based context. Automated response is built by routing findings through EventBridge to Lambda, Step Functions or ticketing tools.",
        ["Detecting compromised instance credentials used from outside AWS.", "Org-wide posture scoring against CIS and FSBP.", "Blocking deployment of images with critical CVEs.", "Auto-isolating an instance flagged for crypto mining."],
        ["Enable GuardDuty in every account and every Region, including unused ones.", "Use a delegated admin account for GuardDuty and Security Hub.", "Suppression rules reduce noise for known-benign patterns.", "Findings flow to EventBridge for automation.", "Inspector scores CVEs with network reachability context."],
        [
            ex("Route high-severity findings to automation", "intermediate", "EventBridge rule pattern for GuardDuty findings with severity 7 or higher.", "json", """
                {
                  "source": ["aws.guardduty"],
                  "detail-type": ["GuardDuty Finding"],
                  "detail": { "severity": [{ "numeric": [">=", 7] }] }
                }
            """, runnable=False),
            ex("Enable org-wide", "basic", "From the management account, delegate admin, then auto-enable members.", "bash", """
                aws guardduty enable-organization-admin-account --admin-account-id 123456789012
                aws securityhub enable-organization-admin-account --admin-account-id 123456789012
                # in the delegated admin account:
                aws guardduty update-organization-configuration --detector-id 12abc34d567e8fa901bc2d34e56789f0 \\
                  --auto-enable-organization-members ALL
            """, runnable=False),
            ex("Quarantine an instance", "advanced", "Lambda response: swap the instance's security groups for an isolation group with no rules.", "python", """
                import boto3

                ec2 = boto3.client("ec2")

                def handler(event, context):
                    instance_id = event["detail"]["resource"]["instanceDetails"]["instanceId"]
                    ec2.modify_instance_attribute(InstanceId=instance_id, Groups=["sg-0isolation00000000"])
                    ec2.create_tags(Resources=[instance_id], Tags=[{"Key": "quarantine", "Value": "guardduty"}])
            """, runnable=False),
        ],
        ["aws guardduty list-findings --detector-id d", "aws securityhub get-findings --filters file://f.json", "aws inspector2 list-findings", "aws securityhub batch-enable-standards", "aws detective list-graphs"],
        ["Enabling only in your main Region; attackers spin up resources where nobody looks.", "Hundreds of unreviewed findings: tune suppression and automate triage.", "Isolating an instance with a security group change does not cut already-established tracked connections; use a NACL or stop the instance if needed."],
        [
            qa("basic", "What data sources does GuardDuty use?", "Foundational sources are CloudTrail management events, VPC Flow Logs and Route 53 DNS logs, read directly without you enabling them. Optional protection plans add S3 data events, EKS audit logs, runtime monitoring, RDS logins, Lambda network activity and malware scanning."),
            qa("intermediate", "GuardDuty vs Security Hub?", "GuardDuty detects threats from activity logs. Security Hub is an aggregator and posture manager: it collects findings from many services, normalizes them and runs compliance checks against standards."),
            qa("intermediate", "How would you automate response to a finding?", "Create an EventBridge rule matching the finding type and severity, target a Lambda or Step Functions workflow that isolates the resource, snapshots it for forensics, revokes sessions and notifies on-call via SNS or a ticket."),
            qa("advanced", "A finding says instance credentials were used from an external IP. What happened and what do you do?", "Role credentials from the instance metadata service were likely stolen (often SSRF) and used outside AWS. Revoke active sessions on the role (deny tokens issued before now), enforce IMDSv2, rotate anything the role could access, investigate in CloudTrail and patch the vulnerable app."),
        ],
        ["observability-well-architected", "iam", "ec2"],
        chain(
            ("Logs", "Trail · Flow · DNS", "Signals", "CloudTrail, VPC Flow Logs and DNS queries feed detection."),
            ("GuardDuty", "ML + threat intel", "Detect", "GuardDuty spots anomalies like crypto mining or credential exfiltration.", "events"),
            ("Security Hub", "ASFF findings", "Aggregate", "Findings from GuardDuty, Inspector and Config land in one place.", "finding"),
            ("EventBridge", "severity >= 7", "Route", "A rule matches high-severity findings.", "ASFF"),
            ("Response", "Lambda · SNS", "Respond", "Automation isolates the resource and pages on-call.", "trigger"),
        ),
    ),
    topic(
        "waf-shield", "AWS WAF & Shield", "security", "intermediate", "WF",
        "Filter malicious HTTP at the edge and absorb DDoS before it reaches your app.",
        "A nightclub entrance: Shield is the crowd barrier that stops a stampede, WAF is the bouncer checking each guest against the rules (no fake IDs, no known troublemakers, not too many from one group at once).",
        "AWS WAF is a layer-7 web application firewall attached to CloudFront, Application Load Balancers, API Gateway, AppSync, Cognito and App Runner. A web ACL contains ordered rules: AWS managed rule groups (Core rule set, Known bad inputs, SQL injection, IP reputation, Bot Control, Account Takeover Prevention), custom match rules on headers, paths and bodies, rate-based rules per IP or key, and geo or IP-set rules. Each rule has an action: Allow, Block, Count, CAPTCHA or Challenge; start new rules in Count mode and review sampled requests and logs before blocking. Shield Standard is free and automatic, protecting against common layer-3/4 attacks for all customers. Shield Advanced adds enhanced detection, automatic application-layer mitigation, the Shield Response Team, cost protection for scaling during attacks, and health-based detection. Put CloudFront in front of origins so that attacks are absorbed across the global edge network.",
        ["Blocking SQL injection and XSS probes on a public API.", "Rate limiting login endpoints to slow credential stuffing.", "Geo-blocking for licensing or compliance.", "DDoS resilience for a high-profile launch."],
        ["Rules are evaluated in priority order; first terminating action wins.", "Rate-based rules count over a sliding window (1 to 10 minutes).", "Log to CloudWatch Logs, S3 or Firehose and redact sensitive fields.", "WAF capacity units (WCU) limit rule complexity per web ACL.", "Shield Advanced is per organization subscription with a monthly fee."],
        [
            ex("Rate limit a login path", "intermediate", "Block an IP that sends more than 100 requests to /login in 5 minutes (WAFv2 rule JSON).", "text", """
                {
                  "Name": "login-rate-limit",
                  "Priority": 10,
                  "Action": { "Block": {} },
                  "Statement": {
                    "RateBasedStatement": {
                      "Limit": 100,
                      "EvaluationWindowSec": 300,
                      "AggregateKeyType": "IP",
                      "ScopeDownStatement": {
                        "ByteMatchStatement": {
                          "SearchString": "/login",
                          "FieldToMatch": { "UriPath": {} },
                          "TextTransformations": [{ "Priority": 0, "Type": "LOWERCASE" }],
                          "PositionalConstraint": "STARTS_WITH"
                        }
                      }
                    }
                  },
                  "VisibilityConfig": { "SampledRequestsEnabled": true, "CloudWatchMetricsEnabled": true, "MetricName": "loginRate" }
                }
            """, runnable=False),
            ex("Web ACL with managed rules (CloudFormation)", "intermediate", "Core rule set plus IP reputation for an ALB.", "yaml", """
                WebAcl:
                  Type: AWS::WAFv2::WebACL
                  Properties:
                    Scope: REGIONAL
                    DefaultAction: { Allow: {} }
                    VisibilityConfig: { SampledRequestsEnabled: true, CloudWatchMetricsEnabled: true, MetricName: web }
                    Rules:
                      - Name: core
                        Priority: 1
                        OverrideAction: { None: {} }
                        Statement:
                          ManagedRuleGroupStatement: { VendorName: AWS, Name: AWSManagedRulesCommonRuleSet }
                        VisibilityConfig: { SampledRequestsEnabled: true, CloudWatchMetricsEnabled: true, MetricName: core }
                      - Name: ip-reputation
                        Priority: 2
                        OverrideAction: { None: {} }
                        Statement:
                          ManagedRuleGroupStatement: { VendorName: AWS, Name: AWSManagedRulesAmazonIpReputationList }
                        VisibilityConfig: { SampledRequestsEnabled: true, CloudWatchMetricsEnabled: true, MetricName: iprep }
            """, runnable=False),
        ],
        ["aws wafv2 list-web-acls --scope REGIONAL", "aws wafv2 associate-web-acl --web-acl-arn a --resource-arn alb-arn", "aws wafv2 get-sampled-requests", "--scope CLOUDFRONT requires --region us-east-1", "aws shield describe-subscription"],
        ["Turning on managed rule groups in Block mode on day one and breaking legitimate uploads.", "Leaving the ALB reachable directly so attackers bypass CloudFront and WAF; restrict origin with a prefix list or custom header.", "Forgetting that CLOUDFRONT-scope web ACLs live in us-east-1."],
        [
            qa("basic", "Shield Standard vs Shield Advanced?", "Standard is free and automatic for all customers against common network and transport layer DDoS. Advanced is paid and adds layer-7 automatic mitigation, 24/7 Shield Response Team access, detailed attack diagnostics and cost protection for scaling during an attack."),
            qa("intermediate", "How do you introduce a new WAF rule safely?", "Deploy it with action Count (or override managed group rules to Count), watch metrics, sampled requests and logs for false positives, add scope-down statements or exclusions, then switch to Block."),
            qa("intermediate", "How do rate-based rules work?", "WAF counts requests per aggregation key (IP, forwarded IP, header, or a custom combination) over the evaluation window and applies the action to keys exceeding the limit until their rate drops. A scope-down statement narrows what is counted, such as only /login."),
            qa("advanced", "How do you make sure attackers cannot bypass WAF on CloudFront?", "Lock the origin so it only accepts CloudFront: for ALB use the CloudFront managed prefix list in the security group plus a secret custom header checked by a listener rule; for S3 use Origin Access Control. Then WAF on CloudFront is the only path."),
        ],
        ["cloudfront-route53", "elb-autoscaling", "observability-well-architected"],
        chain(
            ("Client", "HTTP request", "Request", "A request from the internet arrives at an edge location."),
            ("Shield", "L3/L4 DDoS", "Absorb", "Shield filters volumetric floods before they reach your stack.", "packets"),
            ("WAF", "web ACL rules", "Inspect", "Managed and custom rules check IP reputation, SQLi, XSS and rates.", "HTTP"),
            ("Decision", "allow · block", "Act", "The first terminating rule decides: allow, block, CAPTCHA or challenge.", "match"),
            ("Origin", "ALB / API GW", "Serve", "Clean requests reach the locked-down origin.", "allowed"),
        ),
    ),
    topic(
        "acm-tls", "ACM Certificates & TLS 1.3 Policies", "security", "intermediate", "TL",
        "Free managed certificates that renew themselves, and the listener policies that pick modern TLS.",
        "A notary who issues your shop's official ID card for free, renews it before it expires and hands it straight to the front desk (load balancer), so you never handle the private stamp yourself.",
        "AWS Certificate Manager (ACM) issues public TLS certificates for free for use with integrated services such as ELB, CloudFront, API Gateway and App Runner, and renews DNS-validated certificates automatically. The private key is generated and kept by ACM and cannot be exported for public certificates, which removes a whole class of key handling mistakes. Domain ownership is proven with DNS validation (a CNAME record, ideal with Route 53) or email validation. ACM Private CA issues private certificates for internal services and mTLS. CloudFront requires its certificate in us-east-1; regional services need the certificate in the same Region. TLS behaviour is controlled by security policies on the listener: for ALB and NLB choose a TLS 1.3 policy such as ELBSecurityPolicy-TLS13-1-2-2021-06 (TLS 1.3 with TLS 1.2 fallback) or ELBSecurityPolicy-TLS13-1-3-2021-06 for TLS 1.3 only, and for CloudFront TLSv1.2_2021 or newer. Certificates should be RSA 2048 or ECDSA P-256 or stronger, signed with SHA-256.",
        ["HTTPS on an ALB with automatic renewal.", "A wildcard certificate for many subdomains on CloudFront.", "Internal mTLS between services with ACM Private CA.", "Upgrading listeners from legacy TLS 1.0/1.1 policies."],
        ["DNS validation enables hands-off renewal as long as the CNAME stays.", "CloudFront certificates must be in us-east-1.", "Prefer ECDSA P-256 certificates for performance; keep RSA 2048 for old clients only if needed.", "Use TLS 1.3 security policies; avoid policies that allow TLS 1.0/1.1.", "Monitor DaysToExpiry for imported certificates, which ACM cannot renew."],
        [
            ex("Request and validate a certificate", "basic", "DNS validation via Route 53 so renewal is automatic.", "bash", """
                aws acm request-certificate --domain-name app.example.com \\
                  --subject-alternative-names "*.app.example.com" \\
                  --validation-method DNS --key-algorithm EC_prime256v1
                aws acm describe-certificate --certificate-arn arn:aws:acm:eu-west-1:123456789012:certificate/EXAMPLE \\
                  --query Certificate.DomainValidationOptions
            """, runnable=False),
            ex("HTTPS listener with a TLS 1.3 policy", "intermediate", "CloudFormation listener using ACM and a modern security policy, plus HTTP redirect.", "yaml", """
                HttpsListener:
                  Type: AWS::ElasticLoadBalancingV2::Listener
                  Properties:
                    LoadBalancerArn: !Ref Alb
                    Port: 443
                    Protocol: HTTPS
                    SslPolicy: ELBSecurityPolicy-TLS13-1-2-2021-06
                    Certificates:
                      - CertificateArn: !Ref Certificate
                    DefaultActions:
                      - Type: forward
                        TargetGroupArn: !Ref Targets
                HttpRedirect:
                  Type: AWS::ElasticLoadBalancingV2::Listener
                  Properties:
                    LoadBalancerArn: !Ref Alb
                    Port: 80
                    Protocol: HTTP
                    DefaultActions:
                      - Type: redirect
                        RedirectConfig: { Protocol: HTTPS, Port: "443", StatusCode: HTTP_301 }
            """, runnable=False),
            ex("Inspect a certificate", "basic", "Check expiry, key size and signature algorithm of what a server presents.", "bash", """
                openssl s_client -connect app.example.com:443 -servername app.example.com -tls1_3 </dev/null \\
                  | openssl x509 -text -noout | grep -E "Not After|Public-Key|Signature Algorithm"
            """, runnable=False),
        ],
        ["aws acm request-certificate --validation-method DNS", "aws acm list-certificates --certificate-statuses ISSUED", "aws elbv2 modify-listener --ssl-policy ELBSecurityPolicy-TLS13-1-2-2021-06", "aws elbv2 describe-ssl-policies", "CloudFront: MinimumProtocolVersion TLSv1.2_2021"],
        ["Requesting the CloudFront certificate in the wrong Region.", "Deleting the validation CNAME, which silently breaks automatic renewal.", "Keeping a legacy security policy (TLS 1.0) on a listener long after clients upgraded."],
        [
            qa("basic", "What does ACM do for you?", "It provisions public certificates for free, stores the private key securely, deploys the certificate to integrated services and renews it automatically before expiry when validation is still in place."),
            qa("intermediate", "Why is DNS validation preferred over email?", "DNS validation uses a CNAME record that ACM re-checks at renewal, so renewal is fully automatic. Email validation requires someone to click a link each time and is easy to miss."),
            qa("intermediate", "How do you enforce TLS 1.3 on an ALB?", "Set the HTTPS listener's security policy to a TLS 1.3 policy, for example ELBSecurityPolicy-TLS13-1-3-2021-06 for TLS 1.3 only or ELBSecurityPolicy-TLS13-1-2-2021-06 to also allow TLS 1.2 with strong AEAD ciphers. Redirect port 80 to 443."),
            qa("advanced", "Can you export an ACM public certificate's private key to install on EC2?", "No. Public ACM certificates are only usable through integrated services. For EC2 you would terminate TLS at a load balancer, use Nitro Enclaves with ACM, or use ACM Private CA certificates, which are exportable."),
        ],
        ["elb-autoscaling", "cloudfront-route53"],
        chain(
            ("Request", "app.example.com", "Request", "You request a certificate for the domain and SANs."),
            ("DNS", "CNAME record", "Validate", "ACM gives a CNAME; adding it to Route 53 proves ownership.", "validate"),
            ("ACM", "issue + renew", "Issue", "ACM issues the certificate and keeps the private key.", "proved"),
            ("Listener", "TLS13 policy", "Attach", "The ALB listener uses the certificate with a TLS 1.3 security policy.", "cert"),
            ("Client", "TLS 1.3", "Handshake", "Browsers negotiate TLS 1.3 with an AEAD cipher.", "handshake"),
        ),
    ),
    topic(
        "cloudtrail-config", "CloudTrail & AWS Config", "security", "intermediate", "CT",
        "Who did what (CloudTrail) and what everything looked like over time (Config).",
        "CloudTrail is the building's visitor log: every door opened, by whom, at what time. Config is a photographer who snaps each room after every change and flags anything that breaks the house rules.",
        "AWS CloudTrail records API activity: management events (control plane, such as RunInstances or PutBucketPolicy) are on by default for 90 days in Event history, while a trail or CloudTrail Lake event data store keeps them long-term and can add data events (S3 object reads, Lambda invokes) and network activity events. An organization trail delivers logs from every account to a central S3 bucket in the log archive account, with log file integrity validation using SHA-256 digests and optional SSE-KMS. AWS Config records configuration items for supported resources whenever they change, building a timeline and relationship graph. Config rules (managed or custom Lambda/Guard rules) evaluate compliance, for example s3-bucket-public-read-prohibited or encrypted-volumes, and conformance packs bundle rules for frameworks. Remediation actions via SSM Automation can fix non-compliant resources automatically. Together they answer audit questions: who changed the security group, when, and was it compliant before and after.",
        ["Forensics after an incident: who deleted the database?", "Continuous compliance against CIS or PCI conformance packs.", "Detecting and auto-fixing unencrypted volumes or public buckets.", "Change history for troubleshooting."],
        ["Create an organization trail to a dedicated, locked-down log archive bucket.", "Enable log file validation and protect the bucket with Object Lock.", "Data events cost extra; enable selectively with advanced event selectors.", "Config is regional; use an aggregator for an org-wide view.", "CloudTrail Lake allows SQL queries over events."],
        [
            ex("Organization trail", "intermediate", "Multi-Region, all accounts, integrity validation and KMS encryption.", "bash", """
                aws cloudtrail create-trail --name org-trail --s3-bucket-name acme-org-cloudtrail \\
                  --is-multi-region-trail --is-organization-trail \\
                  --enable-log-file-validation --kms-key-id alias/cloudtrail
                aws cloudtrail start-logging --name org-trail
                aws cloudtrail validate-logs --trail-arn arn:aws:cloudtrail:eu-west-1:123456789012:trail/org-trail \\
                  --start-time 2026-10-01T00:00:00Z
            """, runnable=False),
            ex("Who changed this security group?", "basic", "Search the last 90 days of management events.", "bash", """
                aws cloudtrail lookup-events \\
                  --lookup-attributes AttributeKey=ResourceName,AttributeValue=sg-0123456789abcdef0 \\
                  --query "Events[].{t:EventTime,who:Username,what:EventName}" --output table
            """, runnable=False),
            ex("Config rule with auto-remediation", "advanced", "Flag S3 buckets without default encryption.", "yaml", """
                S3EncryptionRule:
                  Type: AWS::Config::ConfigRule
                  Properties:
                    ConfigRuleName: s3-default-encryption-kms
                    Source:
                      Owner: AWS
                      SourceIdentifier: S3_DEFAULT_ENCRYPTION_KMS
                    Scope:
                      ComplianceResourceTypes: ["AWS::S3::Bucket"]
            """, runnable=False),
        ],
        ["aws cloudtrail lookup-events --lookup-attributes AttributeKey=EventName,AttributeValue=DeleteBucket", "aws cloudtrail create-trail --is-organization-trail", "aws configservice describe-compliance-by-config-rule", "aws configservice get-resource-config-history --resource-type AWS::EC2::SecurityGroup --resource-id sg-x", "CloudTrail Lake: SELECT eventName, userIdentity.arn FROM <eds> WHERE ..."],
        ["Relying on 90-day Event history instead of a trail; evidence disappears.", "Log bucket in the same account an attacker controls; use a separate log archive account with Object Lock.", "Recording every resource type in Config in every Region without considering cost."],
        [
            qa("basic", "CloudTrail vs CloudWatch?", "CloudTrail records API calls for audit (who did what, when, from where). CloudWatch collects operational metrics and logs and triggers alarms. You often send CloudTrail to CloudWatch Logs to alarm on specific API calls."),
            qa("intermediate", "Management events vs data events?", "Management events are control-plane operations on resources such as creating a bucket or changing IAM, logged by default. Data events are high-volume operations on data such as S3 GetObject or Lambda Invoke, which you must explicitly enable and pay for."),
            qa("intermediate", "How do you prove CloudTrail logs were not tampered with?", "Enable log file integrity validation: CloudTrail writes hourly digest files containing SHA-256 hashes, signed with SHA-256 and RSA. aws cloudtrail validate-logs verifies them. Store logs in a separate account with Object Lock for immutability."),
            qa("advanced", "What does AWS Config give you that CloudTrail does not?", "A point-in-time and historical view of resource configuration and relationships, plus continuous compliance evaluation with rules and automatic remediation. CloudTrail tells you the API call; Config tells you the resulting state and whether it complies."),
        ],
        ["observability-well-architected", "iam", "s3"],
        chain(
            ("API call", "PutBucketPolicy", "Change", "Someone changes a resource through the console, CLI or SDK."),
            ("CloudTrail", "event record", "Record", "CloudTrail records identity, time, source IP and parameters.", "event"),
            ("Log archive", "S3 + Object Lock", "Store", "The org trail delivers signed logs to an immutable bucket.", "logs"),
            ("Config", "config item", "Snapshot", "Config captures the new configuration and evaluates rules.", "change"),
            ("Remediate", "SSM Automation", "Fix", "A non-compliant result triggers automatic remediation and a notification.", "NON_COMPLIANT"),
        ),
    ),
]

# --- Networking & containers ----------------------------------------------------------------------------------------

TOPICS += [
    topic(
        "sg-vs-nacl", "Security Groups vs Network ACLs", "networking", "basic", "SG",
        "Two firewall layers: stateful per-ENI security groups and stateless per-subnet NACLs.",
        "A security group is a doorman for each apartment who remembers who went out and lets them back in. A NACL is the checkpoint at the street entrance that checks every person in both directions against a numbered list, with no memory.",
        "Security groups attach to elastic network interfaces (EC2, RDS, Lambda in VPC, ENIs of load balancers) and contain only allow rules; they are stateful, so return traffic for an allowed connection is permitted automatically. Rules can reference CIDRs, prefix lists or other security groups, which lets you say 'the app tier may reach the DB tier on 5432' without IP addresses. Network ACLs attach to subnets, are stateless, support both allow and deny, and are evaluated in rule-number order with the first match winning. Because NACLs are stateless, you must allow ephemeral return ports (1024-65535) explicitly. The default NACL allows everything; custom NACLs deny everything until you add rules. Most designs rely on security groups for fine-grained control and use NACLs sparingly for coarse subnet-level denies, such as blocking a malicious CIDR. VPC Flow Logs and Reachability Analyzer show which layer is dropping traffic.",
        ["Tiered app: ALB SG -> app SG -> DB SG references.", "Blocking a known bad CIDR at the subnet edge with a NACL deny.", "Isolating a compromised instance with an empty SG.", "Compliance requirement for subnet-level controls."],
        ["SG: stateful, allow-only, instance/ENI level, all rules evaluated.", "NACL: stateless, allow and deny, subnet level, ordered rules.", "Reference security groups instead of IPs where possible.", "Remember ephemeral ports in NACL outbound/inbound rules.", "Default SG allows all outbound and inbound from itself."],
        [
            ex("SG chaining for tiers", "basic", "DB accepts Postgres only from the app security group.", "bash", """
                aws ec2 authorize-security-group-ingress --group-id sg-0db00000000000000 \\
                  --ip-permissions 'IpProtocol=tcp,FromPort=5432,ToPort=5432,UserIdGroupPairs=[{GroupId=sg-0app0000000000000}]'
                aws ec2 authorize-security-group-ingress --group-id sg-0app0000000000000 \\
                  --ip-permissions 'IpProtocol=tcp,FromPort=8080,ToPort=8080,UserIdGroupPairs=[{GroupId=sg-0alb0000000000000}]'
            """, runnable=False),
            ex("NACL deny a bad range", "intermediate", "Rule 50 runs before the broader allow at 100.", "bash", """
                aws ec2 create-network-acl-entry --network-acl-id acl-0123456789abcdef0 \\
                  --ingress --rule-number 50 --protocol -1 --cidr-block 203.0.113.0/24 --rule-action deny
                aws ec2 create-network-acl-entry --network-acl-id acl-0123456789abcdef0 \\
                  --egress --rule-number 100 --protocol tcp --port-range From=1024,To=65535 \\
                  --cidr-block 0.0.0.0/0 --rule-action allow
            """, runnable=False),
        ],
        ["aws ec2 describe-security-groups --group-ids sg-x", "aws ec2 authorize-security-group-ingress", "aws ec2 describe-network-acls --filters Name=vpc-id,Values=vpc-x", "aws ec2 create-network-acl-entry --rule-number 50 --rule-action deny", "VPC Reachability Analyzer · Flow Logs"],
        ["Custom NACL without ephemeral port rules: connections open but replies are dropped.", "0.0.0.0/0 on port 22 in a security group; use SSM Session Manager instead.", "Trying to add a deny rule to a security group; only NACLs support deny."],
        [
            qa("basic", "Stateful vs stateless, and which is which?", "Security groups are stateful: if inbound is allowed, the response is automatically allowed out, and vice versa. NACLs are stateless: each direction is evaluated independently, so return traffic needs its own rule."),
            qa("intermediate", "How are rules evaluated in each?", "All security group rules are evaluated together and any allow permits the traffic. NACL rules are evaluated in ascending rule-number order and the first match (allow or deny) applies; the final asterisk rule denies everything else."),
            qa("intermediate", "When would you use a NACL deny instead of a security group?", "When you need to explicitly block a source across a whole subnet, such as a malicious IP range, because security groups cannot deny. It also acts as a second layer if someone opens a security group too widely."),
            qa("advanced", "Traffic from the ALB to instances times out. How do you debug?", "Check the instance SG allows the ALB SG on the target port, the subnet NACL allows the port inbound and ephemeral ports outbound, the target group health check path and port, and use Reachability Analyzer or Flow Logs to see REJECT records."),
        ],
        ["vpc", "ec2", "elb-autoscaling"],
        chain(
            ("Internet", "client", "Packet", "A packet arrives from a client to port 443."),
            ("NACL in", "subnet, ordered", "Subnet check", "The subnet NACL evaluates inbound rules in order; allow 443.", "TCP 443"),
            ("SG", "ENI, stateful", "Instance check", "The security group allows 443 from the ALB SG and records the connection.", "allowed"),
            ("Instance", "app server", "Process", "The application handles the request and responds.", "request"),
            ("NACL out", "ephemeral ports", "Return path", "The response leaves; the stateless NACL must allow ephemeral ports outbound.", "reply"),
        ),
    ),
    topic(
        "vpc-endpoints-privatelink", "VPC Endpoints & PrivateLink", "networking", "advanced", "PL",
        "Reach AWS services and partner APIs privately, without internet gateways or NAT.",
        "Instead of driving across town on public roads to the post office (internet), the post office opens a counter inside your office building (endpoint) that only your staff can use.",
        "VPC endpoints let resources in private subnets reach AWS services without traversing the internet. Gateway endpoints exist only for S3 and DynamoDB; they add a route to the subnet's route table using a prefix list and are free. Interface endpoints, powered by AWS PrivateLink, place an ENI with private IPs in your subnets for almost every other service (STS, Secrets Manager, ECR, CloudWatch Logs, SSM, KMS, and S3 too), with private DNS so the normal service hostname resolves to the endpoint. Endpoint policies are resource policies on the endpoint that restrict which principals, actions and resources can be used through it, which is a key data-exfiltration control. PrivateLink also lets you expose your own service behind a Network Load Balancer (or Gateway Load Balancer) as an endpoint service that consumers in other VPCs or accounts connect to, without peering or overlapping-CIDR concerns. Interface endpoints are billed per hour per AZ plus per GB, which is often cheaper than NAT Gateway data processing for heavy AWS API traffic.",
        ["Private subnets pulling images from ECR without NAT.", "Locking S3 access to your VPC and your buckets only.", "Offering a SaaS API privately to customer VPCs.", "Air-gapped workloads that still use SSM and CloudWatch."],
        ["Gateway endpoint: S3/DynamoDB, route table, free.", "Interface endpoint: ENI per AZ, security group, private DNS, hourly + per-GB.", "Endpoint policies + bucket policies with aws:SourceVpce form a data perimeter.", "PrivateLink is one-directional: consumer to provider.", "ECR needs ecr.api, ecr.dkr and the S3 gateway endpoint."],
        [
            ex("Gateway and interface endpoints", "intermediate", "S3 via route table; Secrets Manager via ENIs with private DNS.", "bash", """
                aws ec2 create-vpc-endpoint --vpc-id vpc-0123456789abcdef0 --vpc-endpoint-type Gateway \\
                  --service-name com.amazonaws.eu-west-1.s3 --route-table-ids rtb-0private000000000
                aws ec2 create-vpc-endpoint --vpc-id vpc-0123456789abcdef0 --vpc-endpoint-type Interface \\
                  --service-name com.amazonaws.eu-west-1.secretsmanager \\
                  --subnet-ids subnet-0a000000000000000 subnet-0b000000000000000 \\
                  --security-group-ids sg-0endpoints00000000 --private-dns-enabled
            """, runnable=False),
            ex("Endpoint policy: only our buckets", "advanced", "Traffic through this S3 endpoint can only reach company buckets.", "json", """
                {
                  "Version": "2012-10-17",
                  "Statement": [
                    {
                      "Sid": "OnlyCompanyBuckets",
                      "Effect": "Allow",
                      "Principal": "*",
                      "Action": ["s3:GetObject", "s3:PutObject", "s3:ListBucket"],
                      "Resource": ["arn:aws:s3:::acme-*", "arn:aws:s3:::acme-*/*"]
                    }
                  ]
                }
            """, runnable=False),
        ],
        ["aws ec2 describe-vpc-endpoint-services --query ServiceNames", "aws ec2 create-vpc-endpoint --vpc-endpoint-type Interface", "aws ec2 modify-vpc-endpoint --policy-document file://p.json", "aws ec2 create-vpc-endpoint-service-configuration --network-load-balancer-arns arn", "aws ec2 describe-prefix-lists"],
        ["Interface endpoint security group not allowing 443 from the workloads.", "Private DNS disabled, so SDKs still resolve the public endpoint and go via NAT.", "Gateway endpoints do not work from on-premises or peered VPCs; use an interface endpoint."],
        [
            qa("intermediate", "Gateway vs interface endpoint?", "Gateway endpoints are free route-table targets for S3 and DynamoDB only, usable from within the VPC. Interface endpoints are ENIs with private IPs and security groups for most services, reachable from on-premises and peered networks, billed hourly and per GB."),
            qa("advanced", "How does PrivateLink differ from VPC peering?", "PrivateLink exposes a single service (behind an NLB) to consumers through endpoint ENIs; traffic is one-directional and CIDRs may overlap. Peering connects whole networks bidirectionally and requires non-overlapping CIDRs and route updates."),
            qa("advanced", "How do you prevent data exfiltration to personal S3 buckets from a private VPC?", "Route S3 through a VPC endpoint with an endpoint policy that only allows your organization's buckets (or aws:ResourceOrgID), remove NAT/internet paths for S3, and on your buckets require aws:SourceVpce. This forms a data perimeter in both directions."),
            qa("intermediate", "Why might endpoints reduce cost?", "NAT Gateway charges per GB processed. Heavy traffic to S3, ECR or CloudWatch Logs through a free gateway endpoint or a cheaper interface endpoint avoids NAT data processing charges."),
        ],
        ["vpc", "s3", "iam"],
        chain(
            ("Workload", "private subnet", "Call", "A task in a private subnet calls secretsmanager.eu-west-1.amazonaws.com."),
            ("Private DNS", "resolves to ENI", "Resolve", "Private DNS maps the service name to the endpoint ENI IPs.", "DNS"),
            ("Endpoint ENI", "SG + policy", "Filter", "The endpoint security group and endpoint policy are checked.", "HTTPS"),
            ("PrivateLink", "AWS backbone", "Transit", "Traffic stays on the AWS network to the service.", "allowed"),
            ("Service", "Secrets Manager", "Respond", "The service replies over the same private path.", "request"),
        ),
    ),
    topic(
        "nat-internet-gateway", "Internet Gateway & NAT Gateway", "networking", "basic", "NG",
        "How public subnets reach the internet, and how private subnets get outbound-only access.",
        "The internet gateway is the building's front door to the street. A NAT gateway is the mailroom: staff in back offices can send letters out and get replies, but outsiders cannot walk in to find them.",
        "An internet gateway (IGW) is a horizontally scaled, highly available VPC component that allows traffic between the VPC and the internet for resources with public IPv4 or IPv6 addresses. A subnet is 'public' only because its route table has 0.0.0.0/0 pointing to the IGW. A NAT gateway lives in a public subnet with an Elastic IP and lets instances in private subnets initiate outbound IPv4 connections, translating their private addresses; inbound connections cannot be initiated. NAT gateways are zonal, so for high availability you deploy one per AZ and route each private subnet to the NAT in its own AZ, which also avoids cross-AZ charges. For IPv6, an egress-only internet gateway gives outbound-only access. NAT gateways are billed per hour and per GB processed, which is a common surprise on bills; VPC endpoints remove AWS-service traffic from the NAT path. Private NAT gateways translate between private networks with overlapping or restricted ranges.",
        ["Private app servers downloading OS patches.", "Lambda in a VPC calling a third-party API.", "Exposing only the load balancer publicly.", "Cost tuning by moving S3 and ECR traffic to endpoints."],
        ["Public subnet = route to IGW; private subnet = route to NAT or none.", "One NAT gateway per AZ for resilience.", "NAT gateway scales automatically up to 100 Gbps.", "Use egress-only IGW for IPv6 outbound.", "Data processing charges add up: watch NatGateway-Bytes in Cost Explorer."],
        [
            ex("Wire a private subnet to NAT", "basic", "Create a NAT gateway in the public subnet and route private traffic to it.", "bash", """
                aws ec2 allocate-address --domain vpc
                aws ec2 create-nat-gateway --subnet-id subnet-0public0a00000000 \\
                  --allocation-id eipalloc-0123456789abcdef0
                aws ec2 create-route --route-table-id rtb-0private0a0000000 \\
                  --destination-cidr-block 0.0.0.0/0 --nat-gateway-id nat-0123456789abcdef0
            """, runnable=False),
            ex("Per-AZ NAT in Terraform", "intermediate", "One NAT and route table per AZ.", "hcl", """
                resource "aws_nat_gateway" "this" {
                  for_each      = aws_subnet.public
                  subnet_id     = each.value.id
                  allocation_id = aws_eip.nat[each.key].id
                }

                resource "aws_route" "private_default" {
                  for_each               = aws_route_table.private
                  route_table_id         = each.value.id
                  destination_cidr_block = "0.0.0.0/0"
                  nat_gateway_id         = aws_nat_gateway.this[each.key].id
                }
            """, runnable=False),
        ],
        ["aws ec2 create-internet-gateway · attach-internet-gateway", "aws ec2 create-nat-gateway --subnet-id public --allocation-id eip", "aws ec2 create-route --nat-gateway-id nat-x", "aws ec2 create-egress-only-internet-gateway", "aws ec2 describe-route-tables --filters Name=vpc-id,Values=vpc-x"],
        ["Putting the NAT gateway in a private subnet: it then has no route to the IGW.", "A single NAT for all AZs: an AZ outage breaks outbound for everyone and costs cross-AZ data.", "Expecting a NAT gateway to allow inbound connections."],
        [
            qa("basic", "What makes a subnet public?", "Its route table has a default route (0.0.0.0/0 or ::/0) to an internet gateway. Instances also need a public IP or Elastic IP to be reachable."),
            qa("basic", "Why do private subnets need a NAT gateway?", "Instances without public IPs cannot reach the internet directly. The NAT gateway translates their source addresses to its Elastic IP for outbound connections and returns responses, while blocking unsolicited inbound traffic."),
            qa("intermediate", "How do you make NAT highly available?", "Deploy a NAT gateway in a public subnet in each AZ and give each AZ's private route table a default route to its local NAT. A NAT gateway is redundant within its AZ but not across AZs."),
            qa("intermediate", "NAT gateway vs NAT instance?", "A NAT gateway is managed, scales automatically and is highly available within an AZ. A NAT instance is an EC2 you manage, patch and scale yourself; it is cheaper at tiny scale and supports security groups and port forwarding, but is rarely worth it."),
        ],
        ["vpc", "ec2"],
        chain(
            ("Private EC2", "10.0.2.15", "Outbound", "A private instance opens a connection to a package mirror."),
            ("Route table", "0.0.0.0/0 -> NAT", "Route", "The private route table sends internet-bound traffic to the NAT in the same AZ.", "SYN"),
            ("NAT GW", "Elastic IP", "Translate", "The NAT gateway rewrites the source to its Elastic IP and tracks the flow.", "10.0.2.15"),
            ("IGW", "VPC edge", "Exit", "The public subnet routes to the internet gateway.", "EIP"),
            ("Internet", "mirror", "Reply", "The reply returns via the IGW and NAT to the instance; unsolicited inbound is dropped.", "packets"),
        ),
    ),
    topic(
        "transit-gateway-peering", "Transit Gateway & VPC Peering", "networking", "advanced", "TG",
        "Connect many VPCs and accounts: point-to-point peering or a regional hub-and-spoke router.",
        "Peering is a private footbridge between two buildings. A Transit Gateway is a central train station: every building connects once, and route tables decide which lines can reach which stations.",
        "VPC peering connects two VPCs (same or different accounts or Regions) privately over the AWS backbone. It is non-transitive: if A peers with B and B with C, A cannot reach C, and CIDRs must not overlap; each side updates route tables and security groups. Peering has no hourly fee and no bandwidth bottleneck, so it suits a few VPCs. AWS Transit Gateway (TGW) is a regional, managed router that VPCs, VPNs and Direct Connect gateways attach to. TGW route tables with associations and propagations let you segment traffic, for example prod and dev can both reach shared services but not each other. TGWs can peer across Regions, share across accounts with Resource Access Manager, and centralize egress or inspection through a firewall VPC with appliance mode. TGW charges per attachment-hour and per GB processed. AWS Cloud WAN builds a global network on top with policy-based segments.",
        ["Hub-and-spoke for dozens of VPCs across accounts.", "Shared services VPC (DNS, AD, tooling) reachable from all.", "Centralized egress and inspection with Network Firewall.", "Two VPCs needing simple, cheap connectivity (peering)."],
        ["Peering is non-transitive and needs non-overlapping CIDRs.", "TGW route tables give segmentation between attachments.", "Share a TGW via RAM to other accounts in the org.", "Enable appliance mode on inspection VPC attachments for symmetric routing.", "Plan an IP address strategy (IPAM) early."],
        [
            ex("Peer two VPCs", "intermediate", "Request, accept, then route both ways.", "bash", """
                aws ec2 create-vpc-peering-connection --vpc-id vpc-0aaaa000000000000 \\
                  --peer-vpc-id vpc-0bbbb000000000000 --peer-owner-id 123456789012
                aws ec2 accept-vpc-peering-connection --vpc-peering-connection-id pcx-0123456789abcdef0
                aws ec2 create-route --route-table-id rtb-0aaaa000000000000 \\
                  --destination-cidr-block 10.20.0.0/16 --vpc-peering-connection-id pcx-0123456789abcdef0
            """, runnable=False),
            ex("Segmented Transit Gateway", "advanced", "Prod and dev both reach shared services, never each other.", "hcl", """
                resource "aws_ec2_transit_gateway" "hub" {
                  default_route_table_association = "disable"
                  default_route_table_propagation = "disable"
                }

                resource "aws_ec2_transit_gateway_route_table" "prod" { transit_gateway_id = aws_ec2_transit_gateway.hub.id }
                resource "aws_ec2_transit_gateway_route_table" "dev"  { transit_gateway_id = aws_ec2_transit_gateway.hub.id }

                resource "aws_ec2_transit_gateway_route_table_propagation" "shared_to_prod" {
                  transit_gateway_attachment_id  = aws_ec2_transit_gateway_vpc_attachment.shared.id
                  transit_gateway_route_table_id = aws_ec2_transit_gateway_route_table.prod.id
                }
            """, runnable=False),
        ],
        ["aws ec2 create-vpc-peering-connection", "aws ec2 create-transit-gateway", "aws ec2 create-transit-gateway-vpc-attachment", "aws ec2 search-transit-gateway-routes --transit-gateway-route-table-id tgw-rtb-x --filters Name=type,Values=propagated", "aws ram create-resource-share"],
        ["Overlapping CIDRs across VPCs block peering and complicate TGW routing.", "Forgetting the return route in the spoke VPC's route table.", "Full-mesh peering at scale: n(n-1)/2 connections become unmanageable."],
        [
            qa("intermediate", "Why is VPC peering non-transitive a problem?", "Each pair of VPCs that needs to talk requires its own peering connection, routes and security group rules. With many VPCs this becomes a full mesh; a Transit Gateway solves it with a hub."),
            qa("advanced", "How do you segment environments on a Transit Gateway?", "Disable default association/propagation, create a route table per segment, associate each attachment with its segment table, and propagate only the routes it may reach (for example shared services into both prod and dev tables, but not prod into dev)."),
            qa("advanced", "How do you centralize egress for many VPCs?", "Spokes route 0.0.0.0/0 to the TGW, the TGW routes to an egress VPC containing NAT gateways (and optionally Network Firewall), and the egress VPC routes return traffic for spoke CIDRs back to the TGW. This saves NAT costs and gives one inspection point."),
            qa("intermediate", "When is peering still the better choice?", "For a small number of VPCs with high throughput needs: peering has no hourly or per-GB processing fee (only standard data transfer) and no extra hop."),
        ],
        ["vpc", "global-infra"],
        chain(
            ("VPC A", "prod 10.10/16", "Send", "An instance in prod sends a packet to shared services."),
            ("Attachment", "TGW ENI", "Enter hub", "The VPC route table sends 10.0.0.0/8 to the TGW attachment.", "packet"),
            ("TGW RT", "prod table", "Lookup", "The prod route table has a propagated route to shared, none to dev.", "lookup"),
            ("Shared VPC", "DNS · tools", "Deliver", "The packet reaches the shared services VPC.", "allowed"),
            ("Return", "symmetric path", "Reply", "Replies come back through the TGW using the shared table.", "reply"),
        ),
    ),
    topic(
        "hybrid-connectivity", "Direct Connect & Site-to-Site VPN", "networking", "advanced", "DX",
        "Connecting data centres to AWS: encrypted tunnels over the internet or dedicated private circuits.",
        "A VPN is an armoured van on public motorways: quick to arrange, but stuck in traffic. Direct Connect is your own private rail line into the AWS station: predictable and fast, but it takes weeks to build.",
        "AWS Site-to-Site VPN creates two IPsec tunnels (IKEv2 recommended, AES-256-GCM, SHA-2 and modern Diffie-Hellman groups) between your customer gateway and a virtual private gateway or Transit Gateway, with BGP or static routing; each tunnel offers up to about 1.25 Gbps. It can be set up in minutes and travels over the internet, so latency varies. AWS Direct Connect (DX) provides dedicated (1, 10, 100 Gbps) or hosted connections from a DX location to AWS with consistent latency and lower data transfer out pricing. DX uses virtual interfaces: private VIFs to VPCs (via a virtual private gateway or DX gateway), transit VIFs to Transit Gateways, and public VIFs to AWS public endpoints. DX is not encrypted by default; use MACsec on supported dedicated links or run IPsec VPN over DX. For resilience, AWS recommends two DX connections at separate locations, or DX with VPN backup. Client VPN covers remote users rather than sites.",
        ["Hybrid apps querying on-premises databases with stable latency.", "Large data migrations and backup traffic.", "Quick encrypted connectivity while DX is provisioned.", "Regulated workloads needing private links plus encryption."],
        ["VPN: two tunnels per connection, use both with BGP.", "DX: dedicated or hosted; private, public and transit VIFs.", "DX Gateway connects one DX to VPCs in many Regions.", "Encrypt DX with MACsec or IPsec over DX.", "BGP attributes (AS path, local preference) steer primary and backup paths."],
        [
            ex("Site-to-Site VPN to a Transit Gateway", "intermediate", "Customer gateway with BGP and a VPN attached to the TGW.", "bash", """
                aws ec2 create-customer-gateway --type ipsec.1 --public-ip 198.51.100.10 --bgp-asn 65010
                aws ec2 create-vpn-connection --type ipsec.1 \\
                  --customer-gateway-id cgw-0123456789abcdef0 \\
                  --transit-gateway-id tgw-0123456789abcdef0 \\
                  --options '{"TunnelOptions":[{"IKEVersions":[{"Value":"ikev2"}],"Phase1EncryptionAlgorithms":[{"Value":"AES256-GCM-16"}],"Phase2EncryptionAlgorithms":[{"Value":"AES256-GCM-16"}]},{"IKEVersions":[{"Value":"ikev2"}],"Phase1EncryptionAlgorithms":[{"Value":"AES256-GCM-16"}],"Phase2EncryptionAlgorithms":[{"Value":"AES256-GCM-16"}]}]}'
            """, runnable=False),
            ex("Resilience pattern", "advanced", "Highly resilient hybrid design.", "text", """
                On-prem DC1 --DX 10G (location A)--+
                                                    +--> DX Gateway --> Transit Gateway --> VPCs
                On-prem DC2 --DX 10G (location B)--+
                On-prem      --IPsec VPN (backup, BGP AS-path prepended)--> Transit Gateway
            """, runnable=False),
        ],
        ["aws ec2 create-customer-gateway --bgp-asn 65010", "aws ec2 create-vpn-connection --transit-gateway-id tgw-x", "aws ec2 describe-vpn-connections --query 'VpnConnections[].VgwTelemetry'", "aws directconnect describe-connections", "aws directconnect create-transit-virtual-interface"],
        ["Assuming DX traffic is encrypted; it is not by default.", "Single DX connection with no backup: one fibre cut takes you offline.", "Using only one VPN tunnel; AWS maintenance can take a tunnel down."],
        [
            qa("intermediate", "VPN vs Direct Connect?", "VPN is quick, cheap and encrypted but runs over the internet with variable latency and roughly 1.25 Gbps per tunnel. Direct Connect is a private dedicated link with consistent latency, higher bandwidth and lower egress pricing, but takes weeks to provision and is not encrypted by default."),
            qa("advanced", "How do you encrypt traffic over Direct Connect?", "Use MACsec on supported dedicated connections for layer-2 encryption, or run Site-to-Site VPN (IPsec) over a public or transit VIF on top of DX for end-to-end encryption."),
            qa("advanced", "What is a Direct Connect gateway?", "A global object that lets a private or transit VIF from one DX connection reach VPCs (through VGWs or Transit Gateways) in multiple Regions and accounts."),
            qa("intermediate", "How do you make a VPN-backed DX failover work?", "Advertise the same prefixes over both with BGP and make DX preferred (AWS prefers DX over VPN for the same prefix; you can also use AS-path prepending or local preference on-premises). If DX fails, BGP withdraws routes and traffic shifts to the VPN."),
        ],
        ["vpc", "global-infra"],
        chain(
            ("On-prem", "router BGP 65010", "Advertise", "The on-premises router advertises 192.168.0.0/16 over BGP."),
            ("DX / VPN", "private or IPsec", "Link", "Traffic crosses Direct Connect, or IPsec tunnels as backup.", "BGP"),
            ("DX Gateway", "global", "Aggregate", "A DX gateway connects the VIF to Transit Gateways in several Regions.", "VIF"),
            ("Transit GW", "regional hub", "Route", "The TGW routes on-premises prefixes to the right VPC attachments.", "routes"),
            ("VPC", "workloads", "Reach", "Workloads reach on-premises databases privately.", "traffic"),
        ),
    ),
    topic(
        "route53-routing", "Route 53 Routing Policies", "networking", "intermediate", "RR",
        "DNS that steers users by weight, latency, health, geography or failover.",
        "A receptionist directing callers: send 10% to the new team (weighted), send each caller to the nearest office (latency), skip an office that is closed (health checks), and always route Germans to the Frankfurt office (geolocation).",
        "Route 53 is AWS's authoritative DNS with a 100% availability SLA. Alias records point a name, including the zone apex, at AWS resources (ALB, CloudFront, S3 website, API Gateway) for free queries and automatic IP tracking. Routing policies decide which record answers: simple, weighted (split by weights for canaries or blue/green), latency-based (lowest measured latency Region), failover (primary/secondary with health checks), geolocation (by continent or country), geoproximity (by distance with bias, via traffic flow), multivalue answer (up to eight healthy records) and IP-based (by client CIDR). Health checks probe endpoints, evaluate CloudWatch alarms or combine child checks, and unhealthy records are withdrawn. TTLs control how quickly clients see changes, while alias records use the target's TTL. Private hosted zones serve DNS inside VPCs, Resolver endpoints bridge DNS with on-premises, and DNSSEC signing protects against spoofing.",
        ["Active-passive multi-Region DR with failover records.", "Canary releases with 95/5 weighted records.", "Serving users from the nearest Region.", "Hybrid DNS between VPCs and corporate DNS."],
        ["Alias records are free for AWS targets and work at the apex.", "Health checks + failover = DNS-level DR.", "Low TTLs (60s) before migrations; raise afterwards.", "Geolocation needs a default record for unmatched locations.", "Route 53 ARC adds routing controls and readiness checks for critical failover."],
        [
            ex("Weighted canary", "intermediate", "Send 10% of traffic to the new stack.", "json", """
                {
                  "Changes": [
                    { "Action": "UPSERT", "ResourceRecordSet": {
                        "Name": "api.example.com", "Type": "CNAME", "SetIdentifier": "blue", "Weight": 90, "TTL": 60,
                        "ResourceRecords": [{ "Value": "blue-alb.eu-west-1.elb.amazonaws.com" }] } },
                    { "Action": "UPSERT", "ResourceRecordSet": {
                        "Name": "api.example.com", "Type": "CNAME", "SetIdentifier": "green", "Weight": 10, "TTL": 60,
                        "ResourceRecords": [{ "Value": "green-alb.eu-west-1.elb.amazonaws.com" }] } }
                  ]
                }
            """, runnable=False),
            ex("Failover with health check", "advanced", "Primary in eu-west-1, secondary in eu-central-1.", "yaml", """
                Primary:
                  Type: AWS::Route53::RecordSet
                  Properties:
                    HostedZoneName: example.com.
                    Name: app.example.com.
                    Type: A
                    SetIdentifier: primary
                    Failover: PRIMARY
                    HealthCheckId: !Ref PrimaryHealth
                    AliasTarget: { DNSName: !GetAtt AlbIreland.DNSName, HostedZoneId: !GetAtt AlbIreland.CanonicalHostedZoneID, EvaluateTargetHealth: true }
                Secondary:
                  Type: AWS::Route53::RecordSet
                  Properties:
                    HostedZoneName: example.com.
                    Name: app.example.com.
                    Type: A
                    SetIdentifier: secondary
                    Failover: SECONDARY
                    AliasTarget: { DNSName: !GetAtt AlbFrankfurt.DNSName, HostedZoneId: !GetAtt AlbFrankfurt.CanonicalHostedZoneID, EvaluateTargetHealth: true }
            """, runnable=False),
        ],
        ["aws route53 change-resource-record-sets --hosted-zone-id Z123 --change-batch file://c.json", "aws route53 create-health-check", "aws route53 list-resource-record-sets --hosted-zone-id Z123", "aws route53 test-dns-answer --hosted-zone-id Z123 --record-name a --record-type A", "dig +short api.example.com"],
        ["CNAME at the zone apex is not allowed; use an alias record.", "High TTLs delaying failover far beyond your RTO.", "Geolocation without a default record returns no answer for unmapped countries."],
        [
            qa("basic", "Alias record vs CNAME?", "An alias is a Route 53 extension that maps a name to an AWS resource, works at the zone apex, follows IP changes automatically and is free to query. A CNAME maps to any hostname but cannot be used at the apex and is billed per query."),
            qa("intermediate", "Latency vs geolocation routing?", "Latency routing picks the Region with the lowest measured network latency for the resolver. Geolocation routes by the user's location (country or continent) regardless of latency, which is useful for compliance and localization."),
            qa("intermediate", "How do you do a canary release with DNS?", "Create weighted records with the same name and different set identifiers, starting with a small weight on the new target, use a short TTL, monitor, then increase the weight. Keep in mind clients cache DNS, so it is approximate."),
            qa("advanced", "How does DNS failover work and what limits it?", "Health checks monitor the primary; when unhealthy, Route 53 answers with the secondary record. Recovery time depends on health check interval and failure threshold plus record TTL and client caching, so keep TTLs low and test regularly."),
        ],
        ["cloudfront-route53", "elb-autoscaling", "global-infra"],
        chain(
            ("User", "app.example.com", "Query", "A browser asks its resolver for app.example.com."),
            ("Resolver", "recursive DNS", "Ask Route 53", "The resolver queries Route 53's authoritative name servers.", "query"),
            ("Policy", "failover/weighted", "Choose", "Route 53 applies the routing policy to candidate records.", "lookup"),
            ("Health check", "primary healthy?", "Filter", "Unhealthy records are skipped; healthy ones are answered.", "evaluate"),
            ("Answer", "ALB IPs, TTL 60", "Respond", "The answer is cached for the TTL and the client connects.", "A record"),
        ),
    ),
    topic(
        "api-gateway", "Amazon API Gateway", "integration-ops", "intermediate", "AG",
        "Managed front door for HTTP, REST and WebSocket APIs with auth, throttling and integrations.",
        "A hotel concierge desk: it checks your room key (auth), limits how many requests you can make per minute (throttling), and routes each request to the right department (Lambda, a service, or another hotel).",
        "API Gateway creates HTTP APIs (cheaper, lower latency, JWT/OIDC and Lambda authorizers), REST APIs (richer features: API keys and usage plans, request validation, transformations, caching, WAF, private APIs and resource policies) and WebSocket APIs. Integrations include Lambda proxy, HTTP backends, AWS service actions (for example SQS SendMessage directly) and private resources via VPC links to NLBs or ALBs. Authentication options are IAM (SigV4), Cognito user pools, JWT authorizers, Lambda authorizers and mutual TLS on custom domains. Throttling applies account-level and per-stage or per-route limits with token buckets, returning 429 when exceeded. Stages (dev, prod) and stage variables support deployments, with canary settings on REST APIs. Custom domains use ACM certificates and a TLS security policy; choose TLS 1.2 minimum or newer. Access logs and X-Ray tracing provide observability.",
        ["Serverless REST API backed by Lambda.", "Direct service integration: POST to SQS without a Lambda.", "Private APIs reachable only from VPC endpoints.", "Partner APIs with API keys and usage plans."],
        ["HTTP API for most new Lambda/HTTP proxies; REST API when you need its extra features.", "Integration timeout default 29 s; long work should be async.", "Payload limit 10 MB.", "Use authorizers, never trust client-supplied identity headers.", "Enable access logging with request IDs for tracing."],
        [
            ex("HTTP API with JWT auth (SAM)", "intermediate", "Cognito JWT authorizer on a Lambda route.", "yaml", """
                Resources:
                  Api:
                    Type: AWS::Serverless::HttpApi
                    Properties:
                      Auth:
                        DefaultAuthorizer: Cognito
                        Authorizers:
                          Cognito:
                            IdentitySource: $request.header.Authorization
                            JwtConfiguration:
                              issuer: https://cognito-idp.eu-west-1.amazonaws.com/eu-west-1_EXAMPLE
                              audience: [example-client-id]
                  GetOrder:
                    Type: AWS::Serverless::Function
                    Properties:
                      Runtime: python3.13
                      Handler: app.get_order
                      Events:
                        Get: { Type: HttpApi, Properties: { ApiId: !Ref Api, Path: /orders/{id}, Method: GET } }
            """, runnable=False),
            ex("Lambda proxy handler", "basic", "The event carries path parameters and JWT claims.", "python", """
                import json

                def get_order(event, context):
                    order_id = event["pathParameters"]["id"]
                    user = event["requestContext"]["authorizer"]["jwt"]["claims"]["sub"]
                    return {"statusCode": 200, "headers": {"content-type": "application/json"},
                            "body": json.dumps({"id": order_id, "owner": user})}
            """, runnable=False),
            ex("Throttle a stage", "basic", "Default route throttling for an HTTP API stage.", "bash", """
                aws apigatewayv2 update-stage --api-id a1b2c3d4e5 --stage-name prod \\
                  --default-route-settings ThrottlingBurstLimit=200,ThrottlingRateLimit=100
            """, runnable=False),
        ],
        ["aws apigatewayv2 get-apis", "aws apigatewayv2 create-stage --auto-deploy", "aws apigateway create-usage-plan", "aws apigatewayv2 create-vpc-link", "curl -H 'Authorization: Bearer $TOKEN' https://api.example.com/orders/1"],
        ["Synchronous APIs doing work longer than the 29 s integration timeout.", "Forgetting CORS configuration and blaming the backend.", "Leaving the default execute-api endpoint enabled when you only want the custom domain."],
        [
            qa("basic", "HTTP API vs REST API?", "HTTP APIs are cheaper and faster with JWT authorizers, Lambda and HTTP proxies. REST APIs add API keys and usage plans, request validation and mapping templates, caching, WAF integration, private endpoints and resource policies."),
            qa("intermediate", "How does API Gateway throttling work?", "It uses token-bucket limits with a steady-state rate and burst at account, stage, route and (with usage plans) per-client levels. Requests over the limit get HTTP 429 and clients should retry with backoff."),
            qa("intermediate", "What is a Lambda authorizer?", "A Lambda that receives the request token or parameters and returns an IAM policy (REST) or simple allow/deny response with context (HTTP). Results can be cached by identity source to reduce latency and cost."),
            qa("advanced", "How do you expose a private service in a VPC through API Gateway?", "Create a VPC link to an internal NLB or ALB (HTTP APIs support ALB, NLB and Cloud Map) and use an HTTP integration pointing at it. Traffic flows from API Gateway into your VPC privately."),
        ],
        ["lambda", "messaging", "cloudfront-route53"],
        chain(
            ("Client", "HTTPS + JWT", "Call", "A client calls GET /orders/42 with a bearer token."),
            ("API GW", "custom domain", "Receive", "API Gateway terminates TLS and matches the route.", "request"),
            ("Authorizer", "JWT / Lambda", "Authenticate", "The authorizer validates the token's issuer, audience and expiry.", "token"),
            ("Throttle", "rate + burst", "Limit", "Per-route limits are checked; excess gets 429.", "claims"),
            ("Lambda", "integration", "Handle", "The Lambda integration runs and returns a response.", "event"),
        ),
    ),
    topic(
        "ecs-fargate", "ECS & Fargate", "compute", "intermediate", "FG",
        "Run containers as services on AWS's own orchestrator, with or without managing servers.",
        "ECS is a shipping company that schedules containers onto ships. With Fargate you do not own any ships; you just hand over the containers and pay for the space they occupy.",
        "Amazon ECS is a managed container orchestrator. A task definition describes containers (image, CPU, memory, ports, environment, secrets, logging, IAM task role). A service keeps the desired number of tasks running, replaces unhealthy ones, integrates with ALB/NLB target groups and scales with Application Auto Scaling. Capacity comes from EC2 instances you manage via capacity providers and Auto Scaling groups, or from Fargate, where each task runs in its own micro-VM and you pay per vCPU and GB-second; Fargate Spot offers up to 70% off for interruption-tolerant tasks. With awsvpc networking each task gets its own ENI and security group. The task execution role pulls images and secrets; the task role is what your code uses. Deployments are rolling by default with a deployment circuit breaker for automatic rollback, or blue/green via CodeDeploy. Service Connect and Cloud Map provide service discovery.",
        ["Web services and APIs without managing Kubernetes.", "Scheduled batch jobs on Fargate.", "Queue workers scaling on SQS depth.", "Lift-and-shift of containerized apps."],
        ["Task role (app permissions) vs execution role (pull image, fetch secrets, write logs).", "Fargate: no nodes to patch, per-task isolation.", "awsvpc gives each task an ENI and SG.", "Enable deployment circuit breaker with rollback.", "Use ECS Exec for debugging instead of SSH."],
        [
            ex("Task definition (Fargate)", "intermediate", "Image from ECR, secret injected, logs to CloudWatch.", "json", """
                {
                  "family": "orders",
                  "requiresCompatibilities": ["FARGATE"],
                  "networkMode": "awsvpc",
                  "cpu": "512",
                  "memory": "1024",
                  "runtimePlatform": { "cpuArchitecture": "ARM64", "operatingSystemFamily": "LINUX" },
                  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecution",
                  "taskRoleArn": "arn:aws:iam::123456789012:role/orders-task",
                  "containerDefinitions": [{
                    "name": "api",
                    "image": "123456789012.dkr.ecr.eu-west-1.amazonaws.com/orders:1.4.2",
                    "portMappings": [{ "containerPort": 8080 }],
                    "secrets": [{ "name": "DB_PASSWORD", "valueFrom": "arn:aws:secretsmanager:eu-west-1:123456789012:secret:prod/orders/db" }],
                    "logConfiguration": { "logDriver": "awslogs", "options": { "awslogs-group": "/ecs/orders", "awslogs-region": "eu-west-1", "awslogs-stream-prefix": "api" } }
                  }]
                }
            """, runnable=False),
            ex("Create a service behind an ALB", "intermediate", "Two tasks in private subnets with rollback on failed deploys.", "bash", """
                aws ecs create-service --cluster prod --service-name orders \\
                  --task-definition orders:7 --desired-count 2 --launch-type FARGATE \\
                  --network-configuration 'awsvpcConfiguration={subnets=[subnet-0a000000000000000,subnet-0b000000000000000],securityGroups=[sg-0app0000000000000],assignPublicIp=DISABLED}' \\
                  --load-balancers targetGroupArn=arn:aws:elasticloadbalancing:eu-west-1:123456789012:targetgroup/orders/abc123,containerName=api,containerPort=8080 \\
                  --deployment-configuration 'deploymentCircuitBreaker={enable=true,rollback=true}'
                aws ecs execute-command --cluster prod --task 0123abcd --container api --interactive --command sh
            """, runnable=False),
        ],
        ["aws ecs list-services --cluster prod", "aws ecs update-service --service orders --force-new-deployment", "aws ecs describe-tasks --cluster prod --tasks t", "aws ecs execute-command --interactive --command sh", "aws ecr get-login-password | docker login --username AWS --password-stdin 123456789012.dkr.ecr.eu-west-1.amazonaws.com"],
        ["Mixing up the task role and the execution role, so secrets fail to load or the app lacks permissions.", "Private subnets without NAT or ECR/S3/Logs endpoints: tasks stay in PENDING pulling images.", "Using the latest tag, which makes rollbacks and audits impossible."],
        [
            qa("basic", "ECS on EC2 vs Fargate?", "With EC2 launch type you manage the container instances (patching, scaling, bin-packing) and can use GPUs or special instance types. Fargate is serverless: each task gets isolated compute, you pay per task resources, and there are no nodes to manage."),
            qa("intermediate", "Task role vs task execution role?", "The execution role is used by the ECS agent to pull images from ECR, fetch secrets and write logs. The task role is assumed by your application code to call AWS APIs."),
            qa("intermediate", "How do you scale an ECS service?", "Use Application Auto Scaling with target tracking on CPU, memory or ALB request count per target, or step scaling on custom metrics such as SQS queue depth per task. Capacity providers scale the underlying EC2 capacity if not on Fargate."),
            qa("advanced", "ECS vs EKS: how do you choose?", "ECS is simpler, deeply AWS-integrated and has no control-plane fee, ideal when you do not need Kubernetes. EKS gives the Kubernetes API, ecosystem (Helm, operators, CRDs) and portability, at the cost of more operational complexity."),
        ],
        ["elb-autoscaling", "ec2", "lambda"],
        chain(
            ("Push image", "ECR", "Build", "CI builds the image and pushes an immutable tag to ECR."),
            ("Task def", "revision 7", "Describe", "A new task definition revision references the image and roles.", "image"),
            ("Service", "desired 2", "Schedule", "The service launches tasks on Fargate in private subnets.", "deploy"),
            ("Fargate task", "ENI + SG", "Run", "Each task pulls the image and secrets with the execution role.", "start"),
            ("ALB", "target group", "Serve", "Healthy tasks register in the target group and receive traffic.", "healthy"),
        ),
    ),
    topic(
        "eks", "Amazon EKS", "compute", "advanced", "EK",
        "Managed Kubernetes control plane integrated with IAM, VPC networking and AWS load balancers.",
        "AWS runs the air traffic control tower (Kubernetes control plane) across three AZs; you supply the runways and planes (nodes and pods), or let Fargate or Auto Mode lease them for you.",
        "Amazon EKS runs a highly available Kubernetes control plane (API servers and etcd across AZs) for an hourly fee, and you choose data plane capacity: managed node groups, self-managed nodes, Karpenter for fast just-in-time node provisioning, Fargate profiles, or EKS Auto Mode which manages nodes, networking and add-ons for you. The Amazon VPC CNI gives pods real VPC IP addresses, so plan subnet sizes or use prefix delegation. Access to the cluster API is managed with EKS access entries mapped to IAM principals (replacing the aws-auth ConfigMap). Pods get AWS permissions through EKS Pod Identity or IRSA. The AWS Load Balancer Controller provisions ALBs for Ingress and NLBs for Services, and the EBS/EFS CSI drivers provide persistent storage. Upgrades are per minor version: control plane first, then add-ons and nodes. Security best practices include private API endpoints, envelope encryption of secrets with KMS, and network policies.",
        ["Teams standardised on Kubernetes tooling (Helm, Argo CD).", "Multi-tenant platforms with namespaces and policies.", "Batch and ML workloads with Karpenter and Spot.", "Portable workloads across clouds or on-premises (EKS Anywhere)."],
        ["Control plane managed by AWS; data plane is yours unless Fargate or Auto Mode.", "VPC CNI: pods consume subnet IPs.", "Access entries map IAM to Kubernetes RBAC.", "Pod Identity / IRSA for per-pod AWS permissions.", "Upgrade regularly; versions leave standard support after about 14 months."],
        [
            ex("Create a cluster with eksctl", "intermediate", "Managed node group on Graviton with private networking.", "yaml", """
                apiVersion: eksctl.io/v1alpha5
                kind: ClusterConfig
                metadata: { name: prod, region: eu-west-1, version: "1.33" }
                vpc:
                  clusterEndpoints: { privateAccess: true, publicAccess: false }
                secretsEncryption:
                  keyARN: arn:aws:kms:eu-west-1:123456789012:key/1234abcd-12ab-34cd-56ef-1234567890ab
                managedNodeGroups:
                  - name: general
                    instanceTypes: [m7g.large]
                    minSize: 2
                    maxSize: 6
                    privateNetworking: true
            """, runnable=False),
            ex("Grant a role cluster access and pod permissions", "advanced", "Access entry for admins, Pod Identity for a service account.", "bash", """
                aws eks create-access-entry --cluster-name prod \\
                  --principal-arn arn:aws:iam::123456789012:role/PlatformAdmin
                aws eks associate-access-policy --cluster-name prod \\
                  --principal-arn arn:aws:iam::123456789012:role/PlatformAdmin \\
                  --policy-arn arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy \\
                  --access-scope type=cluster
                aws eks create-pod-identity-association --cluster-name prod --namespace orders \\
                  --service-account orders-sa --role-arn arn:aws:iam::123456789012:role/orders-pod
            """, runnable=False),
        ],
        ["aws eks update-kubeconfig --name prod", "aws eks list-clusters · describe-cluster", "aws eks create-access-entry", "aws eks create-pod-identity-association", "aws eks update-cluster-version --name prod --kubernetes-version 1.33"],
        ["Small subnets exhausted by pod IPs; plan /19 or larger or use prefix delegation.", "Pods using the node instance role for AWS calls, giving every pod the same broad permissions.", "Falling several versions behind and facing forced upgrades and extended support fees."],
        [
            qa("intermediate", "What does AWS manage in EKS and what do you manage?", "AWS manages the control plane: API servers, etcd, scaling and patching across AZs. You manage worker nodes (unless Fargate or Auto Mode), add-on versions, workloads, RBAC, networking policies and upgrades."),
            qa("advanced", "How do pods get AWS permissions in EKS?", "With EKS Pod Identity (an agent DaemonSet vends credentials for a role associated with a namespace/service account) or IRSA (the cluster OIDC provider issues a projected token used with AssumeRoleWithWebIdentity). Both avoid sharing the node role."),
            qa("advanced", "Why does the VPC CNI cause IP exhaustion and how do you fix it?", "Each pod gets a VPC IP from the node's subnet, and nodes pre-allocate IPs per ENI. Fixes include larger subnets, prefix delegation (/28 prefixes per ENI slot), secondary CIDRs with custom networking, or IPv6 clusters."),
            qa("intermediate", "What is Karpenter?", "An open-source node autoscaler that watches unschedulable pods and launches right-sized EC2 instances directly (including Spot) within seconds, then consolidates underused nodes. It replaces fixed node groups with flexible NodePools."),
        ],
        ["ec2", "vpc", "elb-autoscaling", "iam"],
        chain(
            ("kubectl", "IAM identity", "Authenticate", "kubectl uses an IAM token; access entries map it to Kubernetes permissions."),
            ("Control plane", "AWS-managed", "Schedule", "The API server stores the Deployment and the scheduler places pods.", "apply"),
            ("Karpenter", "provision nodes", "Capacity", "If no node fits, Karpenter launches a right-sized EC2 instance.", "pending"),
            ("Pod", "VPC IP", "Run", "The pod gets a VPC IP from the CNI and credentials via Pod Identity.", "scheduled"),
            ("LB Controller", "ALB ingress", "Expose", "The AWS Load Balancer Controller provisions an ALB for the Ingress.", "ingress"),
        ),
    ),
]

# --- Storage & data -------------------------------------------------------------------------------------------------

TOPICS += [
    topic(
        "ebs-volumes", "EBS Volumes & Snapshots", "storage-data", "basic", "EB",
        "Network block storage for EC2: volume types, IOPS, encryption and incremental snapshots.",
        "A USB drive that plugs into one laptop at a time within the same room (AZ). Snapshots are photocopies stored in a fireproof archive (S3) that you can turn into new drives anywhere.",
        "Amazon EBS provides persistent block volumes attached to EC2 instances in the same Availability Zone; they survive instance stop and can be detached and reattached. Volume types: gp3 (general purpose SSD, baseline 3,000 IOPS and 125 MB/s, independently provisioned up to 80,000 IOPS), io2 Block Express (provisioned IOPS, sub-millisecond latency, up to 256,000 IOPS and 99.999% durability), st1 (throughput HDD for big sequential reads) and sc1 (cold HDD). Snapshots are incremental, stored durably in S3-backed storage, and can be copied across Regions and accounts for DR. Fast Snapshot Restore removes first-read latency on restored volumes, and the Recycle Bin protects against accidental deletion. Encryption uses KMS (AES-256) at rest, in transit to the instance and for snapshots; enable encryption by default per Region. Elastic Volumes lets you change size, type and IOPS online. Data Lifecycle Manager or AWS Backup automates snapshot schedules and retention.",
        ["Boot and data volumes for EC2 databases or apps.", "Nightly snapshots copied to a DR Region.", "Increasing IOPS on a busy database without downtime.", "Restoring a volume from a snapshot after corruption."],
        ["Volumes are AZ-scoped; snapshots are Regional.", "gp3 is usually cheaper and better than gp2.", "Enable EBS encryption by default in every Region.", "Snapshots are incremental but each is restorable on its own.", "Multi-Attach exists only for io1/io2 and needs a cluster-aware filesystem."],
        [
            ex("Create, modify and snapshot", "basic", "Encrypted gp3, then raise IOPS online and snapshot.", "bash", """
                aws ec2 enable-ebs-encryption-by-default
                aws ec2 create-volume --availability-zone eu-west-1a --size 200 --volume-type gp3 \\
                  --iops 6000 --throughput 250 --encrypted --kms-key-id alias/ebs
                aws ec2 modify-volume --volume-id vol-0123456789abcdef0 --iops 12000
                aws ec2 create-snapshot --volume-id vol-0123456789abcdef0 --description "pre-upgrade"
            """, runnable=False),
            ex("Copy a snapshot to the DR Region", "intermediate", "Re-encrypt with a key in the destination Region.", "bash", """
                aws ec2 copy-snapshot --region eu-central-1 --source-region eu-west-1 \\
                  --source-snapshot-id snap-0123456789abcdef0 --encrypted --kms-key-id alias/ebs-dr
            """, runnable=False),
            ex("Lifecycle policy", "intermediate", "Daily snapshots of tagged volumes, keep 14.", "json", """
                {
                  "ResourceTypes": ["VOLUME"],
                  "TargetTags": [{ "Key": "backup", "Value": "daily" }],
                  "Schedules": [{
                    "Name": "daily",
                    "CreateRule": { "Interval": 24, "IntervalUnit": "HOURS", "Times": ["03:00"] },
                    "RetainRule": { "Count": 14 },
                    "CopyTags": true
                  }]
                }
            """, runnable=False),
        ],
        ["aws ec2 create-volume --volume-type gp3", "aws ec2 attach-volume --device /dev/sdf", "aws ec2 modify-volume --size 500", "aws ec2 create-snapshot · copy-snapshot", "aws ec2 enable-ebs-encryption-by-default"],
        ["Trying to attach a volume to an instance in another AZ: restore a snapshot there instead.", "Forgotten unattached volumes and old snapshots quietly costing money.", "Growing the volume but not the filesystem (run growpart and resize2fs or xfs_growfs)."],
        [
            qa("basic", "EBS vs instance store?", "EBS is network-attached, persistent, snapshot-able and survives stop/start. Instance store is physically attached NVMe, very fast but ephemeral: data is lost when the instance stops or fails."),
            qa("intermediate", "gp3 vs io2?", "gp3 offers a 3,000 IOPS baseline with IOPS and throughput provisioned independently of size, suiting most workloads. io2 Block Express targets critical databases needing very high, consistent IOPS, sub-ms latency and 99.999% durability."),
            qa("intermediate", "How do EBS snapshots work?", "The first snapshot copies all used blocks; later ones copy only changed blocks, yet each snapshot can restore a full volume. Restored volumes lazily load blocks from S3 unless Fast Snapshot Restore is enabled."),
            qa("advanced", "How do you encrypt an existing unencrypted volume?", "Snapshot it, copy the snapshot with encryption enabled using a KMS key, create a new volume from the encrypted snapshot, then swap it in. You cannot encrypt a volume in place."),
        ],
        ["ec2", "s3"],
        chain(
            ("EC2", "/dev/nvme1n1", "Write", "The instance writes blocks to its attached gp3 volume."),
            ("EBS volume", "AZ eu-west-1a", "Persist", "EBS replicates the volume within the AZ.", "blocks"),
            ("Snapshot", "incremental", "Back up", "A snapshot copies only blocks changed since the last one.", "changed"),
            ("Copy", "DR Region", "Replicate", "The snapshot is copied and re-encrypted in another Region.", "snapshot"),
            ("Restore", "new volume", "Recover", "A new volume is created from the snapshot in any AZ.", "restore"),
        ),
    ),
    topic(
        "efs-fsx", "EFS & FSx File Systems", "storage-data", "intermediate", "FS",
        "Shared file storage: elastic NFS for Linux, and FSx for Windows, Lustre, NetApp ONTAP and OpenZFS.",
        "EBS is a personal drive; EFS is the shared network drive everyone in the office mounts at once. FSx is a set of specialist drives: one for the Windows team, a race car for HPC (Lustre), and an enterprise filer (ONTAP).",
        "Amazon EFS is a fully managed, elastic NFSv4.1 file system that thousands of Linux clients (EC2, ECS, EKS, Lambda) can mount concurrently across AZs. It grows and shrinks automatically and you pay per GB stored; storage classes (Standard, Infrequent Access, Archive) with lifecycle policies cut cost, and One Zone variants trade durability for price. Throughput modes are Elastic (recommended, scales with demand), Provisioned and Bursting. Access points enforce a POSIX user and root directory per application, and mount targets in each AZ have security groups; use TLS in transit via the EFS mount helper and KMS at rest. Amazon FSx offers managed file systems for specific needs: FSx for Windows File Server (SMB, Active Directory, DFS), FSx for Lustre (HPC and ML with S3 data repository integration, hundreds of GB/s), FSx for NetApp ONTAP (multi-protocol NFS/SMB/iSCSI, snapshots, SnapMirror) and FSx for OpenZFS. Choose by protocol, performance and features.",
        ["Shared content directory for a fleet of web servers.", "Persistent volumes shared by EKS pods (EFS CSI driver).", "Windows home directories with AD (FSx for Windows).", "ML training reading S3 datasets at high speed (FSx for Lustre)."],
        ["EFS: NFS, Linux only, multi-AZ, elastic, pay per GB used.", "Use access points per application.", "Mount with TLS: mount -t efs -o tls.", "Lifecycle to IA/Archive for cold files.", "FSx choices map to protocols and workloads."],
        [
            ex("Create and mount EFS", "intermediate", "Encrypted file system, mount target per AZ, TLS mount.", "bash", """
                aws efs create-file-system --encrypted --kms-key-id alias/efs \\
                  --throughput-mode elastic --tags Key=Name,Value=shared-content
                aws efs create-mount-target --file-system-id fs-0123456789abcdef0 \\
                  --subnet-id subnet-0a000000000000000 --security-groups sg-0efs0000000000000
                sudo mount -t efs -o tls,accesspoint=fsap-0123456789abcdef0 fs-0123456789abcdef0:/ /mnt/shared
            """, runnable=False),
            ex("EFS volume in an ECS task", "advanced", "Transit encryption and IAM authorization on the mount.", "json", """
                {
                  "volumes": [{
                    "name": "shared",
                    "efsVolumeConfiguration": {
                      "fileSystemId": "fs-0123456789abcdef0",
                      "transitEncryption": "ENABLED",
                      "authorizationConfig": { "accessPointId": "fsap-0123456789abcdef0", "iam": "ENABLED" }
                    }
                  }]
                }
            """, runnable=False),
        ],
        ["aws efs create-file-system --encrypted --throughput-mode elastic", "aws efs create-access-point", "aws efs put-lifecycle-configuration", "mount -t efs -o tls fs-x:/ /mnt", "aws fsx describe-file-systems"],
        ["Mount target security group missing NFS (2049) from clients.", "Using EFS for latency-sensitive databases; prefer EBS.", "Many small files with metadata-heavy workloads can be slower than expected."],
        [
            qa("basic", "EBS vs EFS vs S3?", "EBS is block storage for one instance in one AZ (databases, boot volumes). EFS is a shared POSIX file system for many clients across AZs. S3 is object storage accessed via API, cheapest at scale and not a mounted file system."),
            qa("intermediate", "When would you choose FSx for Lustre?", "For HPC, ML training or media rendering that needs very high throughput and low latency over large datasets, often linked to S3 so data is lazily loaded and results exported back."),
            qa("intermediate", "What are EFS access points?", "Application-specific entry points that enforce a POSIX user/group and root directory. Combined with IAM authorization they isolate tenants or apps sharing one file system."),
            qa("advanced", "How do you reduce EFS cost?", "Enable lifecycle management to move files not accessed for N days to Infrequent Access or Archive, use One Zone for non-critical data, and use Elastic throughput rather than over-provisioning."),
        ],
        ["ec2", "s3"],
        chain(
            ("Clients", "EC2 · ECS · EKS", "Mount", "Instances and pods mount the file system over NFS with TLS."),
            ("Mount target", "one per AZ", "Connect", "Each AZ has a mount target ENI with a security group.", "NFS 2049"),
            ("Access point", "POSIX + root dir", "Isolate", "The access point enforces the app's user and directory.", "TLS"),
            ("EFS", "multi-AZ storage", "Store", "Data is stored redundantly across AZs and scales elastically.", "files"),
            ("Lifecycle", "IA / Archive", "Tier", "Cold files move to cheaper storage classes automatically.", "cold"),
        ),
    ),
    topic(
        "s3-storage-classes", "S3 Storage Classes & Lifecycle", "storage-data", "basic", "SC",
        "Pay for how often you read data: from Standard to Glacier Deep Archive, moved automatically.",
        "A warehouse with shelves near the door (Standard), shelves at the back (Infrequent Access), and an off-site vault (Glacier) where retrieval takes hours. Lifecycle rules are the forklift that moves boxes as they age.",
        "S3 storage classes trade storage price for access cost and latency. S3 Standard is for frequently accessed data; S3 Intelligent-Tiering automatically moves objects between frequent, infrequent and archive instant access tiers for a small monitoring fee and is a strong default when patterns are unknown. Standard-IA and One Zone-IA are cheaper to store but charge per GB retrieved and have a 30-day minimum and 128 KB minimum billable size. Glacier Instant Retrieval offers millisecond access for data read about once a quarter; Glacier Flexible Retrieval (minutes to hours) and Glacier Deep Archive (hours, cheapest) suit archives and compliance, with 90 and 180-day minimums. S3 Express One Zone provides single-digit-millisecond access in one AZ for performance-critical workloads. Lifecycle rules transition objects between classes and expire objects, old versions and incomplete multipart uploads. S3 Storage Lens and Storage Class Analysis show where savings are.",
        ["Logs that move to IA after 30 days and Deep Archive after a year.", "Unknown access patterns on a data lake (Intelligent-Tiering).", "Compliance archives retained for 7 years.", "Cleaning up incomplete multipart uploads."],
        ["All classes except One Zone and Express One Zone store data across 3+ AZs.", "Minimum storage durations and sizes affect cost for small or short-lived objects.", "Expire noncurrent versions or versioned buckets grow forever.", "Abort incomplete multipart uploads after a few days.", "Restoring from Glacier creates a temporary copy."],
        [
            ex("Lifecycle configuration", "basic", "Tier logs down over time, expire them, and clean up.", "json", """
                {
                  "Rules": [{
                    "ID": "logs-tiering",
                    "Filter": { "Prefix": "logs/" },
                    "Status": "Enabled",
                    "Transitions": [
                      { "Days": 30, "StorageClass": "STANDARD_IA" },
                      { "Days": 90, "StorageClass": "GLACIER_IR" },
                      { "Days": 365, "StorageClass": "DEEP_ARCHIVE" }
                    ],
                    "Expiration": { "Days": 2555 },
                    "NoncurrentVersionExpiration": { "NoncurrentDays": 30 },
                    "AbortIncompleteMultipartUpload": { "DaysAfterInitiation": 7 }
                  }]
                }
            """, runnable=False),
            ex("Apply and restore", "intermediate", "Upload directly to Intelligent-Tiering; restore an archived object.", "bash", """
                aws s3api put-bucket-lifecycle-configuration --bucket acme-logs --lifecycle-configuration file://lifecycle.json
                aws s3 cp report.parquet s3://acme-lake/reports/ --storage-class INTELLIGENT_TIERING
                aws s3api restore-object --bucket acme-logs --key logs/2024/01/app.log.gz \\
                  --restore-request '{"Days":3,"GlacierJobParameters":{"Tier":"Standard"}}'
            """, runnable=False),
        ],
        ["aws s3api put-bucket-lifecycle-configuration", "aws s3 cp f s3://b/ --storage-class STANDARD_IA", "aws s3api restore-object --restore-request", "aws s3api head-object --bucket b --key k (shows Restore)", "S3 Storage Lens · Storage Class Analysis"],
        ["Moving millions of tiny objects to IA or Glacier: per-object transition fees and minimum sizes cost more than they save.", "Reading IA data frequently and paying retrieval fees.", "Expecting Glacier Flexible or Deep Archive objects to be readable instantly."],
        [
            qa("basic", "When would you use Intelligent-Tiering?", "When access patterns are unknown or change over time. It moves objects between tiers automatically based on access, with no retrieval fees, for a small per-object monitoring fee (objects under 128 KB are not monitored)."),
            qa("intermediate", "Standard-IA vs Glacier Instant Retrieval?", "Both give millisecond access. Standard-IA suits data accessed roughly monthly; Glacier Instant Retrieval has cheaper storage but higher retrieval costs and a 90-day minimum, suiting data accessed about once a quarter."),
            qa("intermediate", "What should every lifecycle policy on a versioned bucket include?", "Noncurrent version expiration (or transitions) so old versions do not accumulate forever, expiration of delete markers where appropriate, and aborting incomplete multipart uploads."),
            qa("advanced", "How do you decide whether a lifecycle transition is worth it?", "Compare storage savings against transition request costs, minimum storage duration charges, minimum billable object size and expected retrieval costs. Use Storage Class Analysis to see access patterns per prefix before deciding."),
        ],
        ["s3", "observability-well-architected"],
        chain(
            ("Upload", "STANDARD", "Day 0", "New log objects land in S3 Standard."),
            ("Standard-IA", "day 30", "Cool", "After 30 days the lifecycle rule transitions them to Standard-IA.", "transition"),
            ("Glacier IR", "day 90", "Archive", "After 90 days they move to Glacier Instant Retrieval.", "transition"),
            ("Deep Archive", "day 365", "Deep freeze", "After a year they go to Deep Archive, the cheapest class.", "transition"),
            ("Expire", "day 2555", "Delete", "After seven years the objects are deleted automatically.", "expire"),
        ),
    ),
    topic(
        "s3-replication-versioning", "S3 Versioning, Replication & Object Lock", "storage-data", "intermediate", "RV",
        "Protect objects from overwrites and deletes, copy them across Regions, and make them immutable.",
        "Versioning is a document system that keeps every draft. Replication sends a copy of each new draft to a second office. Object Lock puts certain drafts in a sealed cabinet nobody can open early, not even the boss.",
        "S3 versioning keeps every version of an object; a delete adds a delete marker instead of destroying data, and you can restore any previous version. Once enabled, versioning can only be suspended, not disabled. MFA Delete further protects versioning state and permanent deletes. Replication requires versioning on both buckets: Cross-Region Replication (CRR) and Same-Region Replication (SRR) copy new objects asynchronously, optionally filtered by prefix or tag, with options to change ownership, storage class and KMS key in the destination. Replication Time Control (RTC) gives an SLA of 99.99% of objects in 15 minutes with metrics. Existing objects are copied with S3 Batch Replication. Delete markers are not replicated by default, and versioned deletes are never replicated, which protects against malicious deletion. Object Lock provides WORM storage with retention periods in governance or compliance mode and legal holds, commonly used for backups and regulated records.",
        ["Recover from accidental overwrites or deletes.", "DR copy of critical data in another Region.", "Aggregating logs from many accounts into one bucket (SRR).", "Ransomware-resistant backups with Object Lock compliance mode."],
        ["Versioning is a prerequisite for replication and Object Lock.", "Replication is asynchronous and only for new objects unless you use Batch Replication.", "The replication role needs read on source, write on destination and KMS permissions.", "Compliance mode cannot be shortened or removed by anyone, including root.", "Lifecycle rules are needed to expire noncurrent versions."],
        [
            ex("Enable versioning and CRR", "intermediate", "Replicate to a DR bucket with a different KMS key and storage class.", "json", """
                {
                  "Role": "arn:aws:iam::123456789012:role/s3-replication",
                  "Rules": [{
                    "ID": "to-dr",
                    "Status": "Enabled",
                    "Priority": 1,
                    "Filter": { "Prefix": "" },
                    "DeleteMarkerReplication": { "Status": "Disabled" },
                    "SourceSelectionCriteria": { "SseKmsEncryptedObjects": { "Status": "Enabled" } },
                    "Destination": {
                      "Bucket": "arn:aws:s3:::acme-data-dr",
                      "StorageClass": "STANDARD_IA",
                      "EncryptionConfiguration": { "ReplicaKmsKeyID": "arn:aws:kms:eu-central-1:123456789012:alias/s3-dr" },
                      "ReplicationTime": { "Status": "Enabled", "Time": { "Minutes": 15 } },
                      "Metrics": { "Status": "Enabled", "EventThreshold": { "Minutes": 15 } }
                    }
                  }]
                }
            """, runnable=False),
            ex("Versioning, restore and Object Lock", "advanced", "Restore a previous version; set default compliance retention.", "bash", """
                aws s3api put-bucket-versioning --bucket acme-data --versioning-configuration Status=Enabled
                aws s3api list-object-versions --bucket acme-data --prefix reports/q1.csv
                aws s3api copy-object --bucket acme-data --key reports/q1.csv \\
                  --copy-source "acme-data/reports/q1.csv?versionId=3HL4kqtJlcpXroDTDmJ.rmSpXd3dIbrHY"
                aws s3api put-object-lock-configuration --bucket acme-backups --object-lock-configuration \\
                  '{"ObjectLockEnabled":"Enabled","Rule":{"DefaultRetention":{"Mode":"COMPLIANCE","Days":35}}}'
            """, runnable=False),
        ],
        ["aws s3api put-bucket-versioning --versioning-configuration Status=Enabled", "aws s3api list-object-versions --bucket b", "aws s3api put-bucket-replication --replication-configuration file://r.json", "aws s3api put-object-retention · put-object-legal-hold", "aws s3control create-job (Batch Replication)"],
        ["Assuming replication copies existing objects; it does not without Batch Replication.", "Versioning without lifecycle: storage costs grow with every overwrite.", "Testing Object Lock compliance mode with a long retention in production: you cannot undo it."],
        [
            qa("basic", "What happens when you delete an object in a versioned bucket?", "A simple DELETE adds a delete marker that becomes the current version, so GET returns 404 but older versions remain. Deleting the delete marker restores the object; deleting a specific version ID removes it permanently."),
            qa("intermediate", "What does S3 replication not copy by default?", "Objects that existed before the rule (use Batch Replication), delete markers (unless enabled), deletes of specific versions (never), and objects encrypted with SSE-KMS unless you opt in and grant key permissions. Replicas are not re-replicated unless you configure chaining."),
            qa("advanced", "Governance vs compliance mode in Object Lock?", "In governance mode, users with s3:BypassGovernanceRetention can shorten or remove retention. In compliance mode no one, including the root user, can delete the version or shorten retention until it expires."),
            qa("intermediate", "How do you guarantee replication latency?", "Enable Replication Time Control, which is backed by an SLA of 99.99% of objects replicated within 15 minutes and publishes replication metrics and events for objects that miss the threshold."),
        ],
        ["s3", "global-infra"],
        chain(
            ("PUT", "reports/q1.csv", "Write", "An application overwrites an object in a versioned bucket."),
            ("Versions", "v1, v2 kept", "Keep history", "S3 stores the new version; the old one remains restorable.", "new version"),
            ("Replication", "IAM role + KMS", "Replicate", "The replication rule copies the new version asynchronously.", "async"),
            ("DR bucket", "eu-central-1", "Land", "The replica lands in the DR Region with its own KMS key.", "replica"),
            ("Object Lock", "35-day WORM", "Protect", "Backups are locked in compliance mode so nobody can delete them early.", "locked"),
        ),
    ),
    topic(
        "rds-multi-az", "RDS: Multi-AZ & Read Replicas", "storage-data", "intermediate", "RD",
        "Managed relational databases with synchronous standby for HA and async replicas for read scaling.",
        "Multi-AZ is a co-pilot sitting next to the pilot, ready to take over instantly. Read replicas are trainee pilots in other planes who copy the flight plan slightly later and can answer passengers' questions, but do not fly your plane.",
        "Amazon RDS runs MySQL, PostgreSQL, MariaDB, Oracle, SQL Server and Db2, handling provisioning, patching, backups and failover. Multi-AZ instance deployments keep a synchronous standby in another AZ; on failure, maintenance or instance-type change, RDS fails over by flipping the DNS endpoint, typically within one to two minutes, and the standby serves no reads. Multi-AZ DB clusters (MySQL and PostgreSQL) use two readable standbys with semi-synchronous replication and failovers usually under 35 seconds. Read replicas use asynchronous replication, can live in other Regions, serve read traffic and can be promoted for DR, but may lag. Automated backups with point-in-time restore (up to 35 days) and manual snapshots protect data; encryption at rest uses KMS and must be chosen at creation. RDS Proxy pools connections, which helps Lambda-heavy workloads and shortens failover impact. Use IAM database authentication or Secrets Manager-managed passwords, require TLS, and keep instances in private subnets.",
        ["OLTP application databases with high availability.", "Offloading reporting queries to read replicas.", "Cross-Region DR by promoting a replica.", "Serverless apps behind RDS Proxy."],
        ["Multi-AZ = HA (sync, standby); read replica = scale/DR (async, readable).", "Applications must reconnect using the endpoint DNS after failover.", "Encryption must be enabled at creation; encrypt later via snapshot copy.", "Point-in-time restore creates a new instance.", "Blue/green deployments enable safer major version upgrades."],
        [
            ex("Create a Multi-AZ PostgreSQL instance", "intermediate", "Password managed by Secrets Manager, encrypted, private.", "bash", """
                aws rds create-db-instance --db-instance-identifier orders-db \\
                  --engine postgres --engine-version 17.4 --db-instance-class db.m7g.large \\
                  --allocated-storage 100 --storage-type gp3 --multi-az \\
                  --master-username app_admin --manage-master-user-password \\
                  --storage-encrypted --kms-key-id alias/rds \\
                  --db-subnet-group-name private-db --vpc-security-group-ids sg-0db00000000000000 \\
                  --backup-retention-period 14 --no-publicly-accessible
            """, runnable=False),
            ex("Add a cross-Region read replica", "advanced", "Replica in the DR Region; promote it in a disaster.", "bash", """
                aws rds create-db-instance-read-replica --region eu-central-1 \\
                  --db-instance-identifier orders-db-dr \\
                  --source-db-instance-identifier arn:aws:rds:eu-west-1:123456789012:db:orders-db \\
                  --kms-key-id alias/rds-dr
                aws rds promote-read-replica --region eu-central-1 --db-instance-identifier orders-db-dr
            """, runnable=False),
        ],
        ["aws rds describe-db-instances --query 'DBInstances[].[DBInstanceIdentifier,MultiAZ]'", "aws rds reboot-db-instance --force-failover", "aws rds create-db-instance-read-replica", "aws rds restore-db-instance-to-point-in-time", "aws rds create-blue-green-deployment"],
        ["Sending reads to the Multi-AZ standby: it is not readable in instance deployments.", "Caching database IPs instead of the endpoint DNS name, breaking failover.", "Read-after-write inconsistency when reading from lagging replicas."],
        [
            qa("basic", "Multi-AZ vs read replica?", "Multi-AZ provides high availability with a synchronous standby that takes over automatically; it does not scale reads (for instance deployments). Read replicas use asynchronous replication to scale reads and can be promoted, but may lag and do not fail over automatically."),
            qa("intermediate", "What happens during a Multi-AZ failover?", "RDS detects the failure, promotes the standby and updates the DNS CNAME of the endpoint to point at it. Clients reconnect, usually within one to two minutes; RDS Proxy or short DNS TTLs in drivers reduce the impact."),
            qa("intermediate", "How do you encrypt an existing unencrypted RDS instance?", "Take a snapshot, copy it with encryption and a KMS key, restore a new instance from the encrypted snapshot, then cut over. Encryption cannot be toggled in place."),
            qa("advanced", "Why use RDS Proxy?", "It pools and multiplexes database connections, protecting the database from connection storms (common with Lambda), keeps connections open during failover to cut downtime, and supports IAM authentication with credentials from Secrets Manager."),
        ],
        ["databases", "vpc", "lambda"],
        chain(
            ("App", "orders-db endpoint", "Connect", "The app connects to the RDS endpoint DNS name over TLS."),
            ("Primary", "AZ a", "Write", "Writes go to the primary instance.", "SQL"),
            ("Standby", "AZ b, sync", "Replicate", "Each write is synchronously committed to the standby.", "sync"),
            ("Read replica", "async, readable", "Scale reads", "Reports read from an asynchronous replica.", "async"),
            ("Failover", "DNS flip", "Recover", "If the primary fails, DNS points to the standby within minutes.", "failover"),
        ),
    ),
    topic(
        "aurora", "Amazon Aurora", "storage-data", "advanced", "AU",
        "Cloud-native MySQL and PostgreSQL with a distributed storage layer, fast failover and global replication.",
        "Instead of each chef keeping their own pantry, Aurora gives all chefs one enormous shared pantry copied six times across three buildings. A new chef can start cooking in seconds because the ingredients are already there.",
        "Aurora separates compute from a distributed, self-healing storage volume that keeps six copies of data across three AZs and grows automatically up to 256 TiB. Writes need a quorum of four of six copies and reads three, so it tolerates the loss of an AZ plus one more copy. A cluster has one writer and up to 15 low-lag Aurora Replicas sharing the same storage; failover promotes a replica typically in under 30 seconds. Endpoints include the cluster (writer) endpoint, the reader endpoint (load-balanced across replicas) and custom endpoints. Aurora Serverless v2 scales capacity in fine-grained ACUs within seconds and can scale to zero for idle databases. Aurora Global Database replicates storage to up to ten secondary Regions with typically under one second of lag and supports managed switchover and failover for DR. Other features include fast cloning (copy-on-write), backtrack (MySQL), zero-ETL integration with Redshift, I/O-Optimized pricing and Aurora DSQL for distributed active-active SQL.",
        ["High-throughput OLTP needing fast failover.", "Spiky or dev workloads on Serverless v2.", "Global apps with local reads and Regional DR.", "Fast test environments from database clones."],
        ["Storage: 6 copies in 3 AZs, quorum writes 4/6, reads 3/6.", "Replicas share storage, so replica lag is usually milliseconds.", "Use the reader endpoint for read scaling.", "Global Database RPO about 1 s, RTO about a minute.", "Choose I/O-Optimized when I/O exceeds roughly a quarter of the bill."],
        [
            ex("Aurora PostgreSQL Serverless v2 cluster", "intermediate", "Cluster with a serverless writer that scales between 0.5 and 16 ACUs.", "bash", """
                aws rds create-db-cluster --db-cluster-identifier orders \\
                  --engine aurora-postgresql --engine-version 16.6 \\
                  --serverless-v2-scaling-configuration MinCapacity=0.5,MaxCapacity=16 \\
                  --master-username app_admin --manage-master-user-password \\
                  --storage-encrypted --kms-key-id alias/rds --db-subnet-group-name private-db \\
                  --vpc-security-group-ids sg-0db00000000000000
                aws rds create-db-instance --db-cluster-identifier orders \\
                  --db-instance-identifier orders-writer --db-instance-class db.serverless --engine aurora-postgresql
            """, runnable=False),
            ex("Clone and global database", "advanced", "Copy-on-write clone for testing; add a secondary Region.", "bash", """
                aws rds restore-db-cluster-to-point-in-time --source-db-cluster-identifier orders \\
                  --db-cluster-identifier orders-clone --restore-type copy-on-write --use-latest-restorable-time
                aws rds create-global-cluster --global-cluster-identifier orders-global \\
                  --source-db-cluster-identifier arn:aws:rds:eu-west-1:123456789012:cluster:orders
            """, runnable=False),
        ],
        ["aws rds describe-db-clusters --query 'DBClusters[].Endpoint'", "aws rds failover-db-cluster --db-cluster-identifier c", "aws rds create-db-cluster-endpoint --endpoint-type READER", "aws rds switchover-global-cluster", "aws rds restore-db-cluster-to-point-in-time --restore-type copy-on-write"],
        ["Pointing read traffic at the cluster endpoint instead of the reader endpoint.", "Setting Serverless v2 max ACUs too low, throttling during peaks.", "Assuming Global Database secondaries accept writes (only with write forwarding, and with extra latency)."],
        [
            qa("intermediate", "How does Aurora's storage differ from RDS?", "RDS instances use their own EBS volumes and replicate at the database level. Aurora uses a shared distributed storage volume with six copies across three AZs; replicas read the same storage so they lag milliseconds and failover is faster."),
            qa("advanced", "How does Aurora tolerate failures?", "Writes require 4 of 6 storage copies and reads 3 of 6, so it survives losing an entire AZ (two copies) and still writes, or an AZ plus one copy and still reads. Storage is self-healing in 10 GB segments."),
            qa("intermediate", "When would you use Aurora Serverless v2?", "For variable, unpredictable or intermittent workloads such as SaaS tenants, dev/test or spiky traffic, where capacity should scale within seconds and you want to avoid paying for peak capacity all the time."),
            qa("advanced", "How does Aurora Global Database support DR?", "Storage-level replication to secondary Regions with typically under a second of lag. In a Regional outage you fail over (detach and promote) a secondary in about a minute; planned switchover keeps topology with no data loss."),
        ],
        ["databases", "global-infra"],
        chain(
            ("App", "cluster endpoint", "Write", "The app writes through the cluster (writer) endpoint."),
            ("Writer", "one instance", "Log", "The writer sends redo log records, not pages, to storage.", "INSERT"),
            ("Storage", "6 copies · 3 AZs", "Quorum", "A write commits once 4 of 6 copies acknowledge.", "redo log"),
            ("Replicas", "up to 15", "Read", "Replicas read the same storage with millisecond lag.", "shared"),
            ("Global DB", "other Region", "Replicate", "Storage replicates to a secondary Region in under a second.", "async"),
        ),
    ),
    topic(
        "dynamodb-modeling", "DynamoDB: Keys, GSIs, Capacity & Streams", "storage-data", "advanced", "DY",
        "Single-digit-millisecond key-value at any scale, if you design keys for your access patterns.",
        "A giant filing cabinet with a drawer per partition key and folders sorted by sort key inside. GSIs are extra index cards filed by a different attribute, and Streams is a ticker tape announcing every change.",
        "DynamoDB is a serverless key-value and document database. Every item has a primary key: a partition key alone, or partition key plus sort key, which groups related items so Query can fetch ranges (begins_with, between) efficiently. Data is spread across partitions by the hash of the partition key, so high-cardinality, evenly accessed keys avoid hot partitions. Global secondary indexes provide alternate keys with their own capacity and eventual consistency; local secondary indexes share the partition key and must be created with the table. Capacity is on-demand (pay per request, instant scaling) or provisioned with auto scaling, measured in RCUs and WCUs. Reads are eventually consistent by default, with strongly consistent reads and ACID transactions (TransactWriteItems) available. DynamoDB Streams and Kinesis Data Streams capture item-level changes for Lambda triggers, replication and event-driven designs; TTL deletes expired items for free. Global tables give multi-Region, multi-active replication; point-in-time recovery restores to any second in 35 days.",
        ["Session stores, carts and user profiles at massive scale.", "Single-table designs for microservices with known access patterns.", "Event-driven pipelines from Streams to Lambda.", "Multi-Region active-active apps with global tables."],
        ["Design keys from access patterns first; there are no joins.", "Query by key; avoid Scan in hot paths.", "Item size limit 400 KB.", "Use conditional writes for optimistic locking and idempotency.", "Enable PITR and deletion protection on production tables."],
        [
            ex("Table with a GSI and TTL", "intermediate", "Orders by customer, plus an index by status.", "yaml", """
                OrdersTable:
                  Type: AWS::DynamoDB::Table
                  Properties:
                    BillingMode: PAY_PER_REQUEST
                    AttributeDefinitions:
                      - { AttributeName: pk, AttributeType: S }
                      - { AttributeName: sk, AttributeType: S }
                      - { AttributeName: status, AttributeType: S }
                    KeySchema:
                      - { AttributeName: pk, KeyType: HASH }
                      - { AttributeName: sk, KeyType: RANGE }
                    GlobalSecondaryIndexes:
                      - IndexName: by-status
                        KeySchema: [{ AttributeName: status, KeyType: HASH }, { AttributeName: sk, KeyType: RANGE }]
                        Projection: { ProjectionType: KEYS_ONLY }
                    TimeToLiveSpecification: { AttributeName: expires_at, Enabled: true }
                    StreamSpecification: { StreamViewType: NEW_AND_OLD_IMAGES }
                    PointInTimeRecoverySpecification: { PointInTimeRecoveryEnabled: true }
                    SSESpecification: { SSEEnabled: true, SSEType: KMS }
                    DeletionProtectionEnabled: true
            """, runnable=False),
            ex("Query and conditional write with boto3", "advanced", "Fetch a customer's 2026 orders; create an order only once.", "python", """
                import boto3
                from boto3.dynamodb.conditions import Key

                table = boto3.resource("dynamodb").Table("Orders")
                resp = table.query(KeyConditionExpression=Key("pk").eq("CUST#42") & Key("sk").begins_with("ORDER#2026"))

                table.put_item(
                    Item={"pk": "CUST#42", "sk": "ORDER#2026-10-17#981", "status": "NEW", "total": 4999},
                    ConditionExpression="attribute_not_exists(pk) AND attribute_not_exists(sk)",
                )
            """, runnable=False),
            ex("Stream-triggered Lambda", "intermediate", "React to inserts, e.g. to publish an event.", "python", """
                def handler(event, context):
                    for record in event["Records"]:
                        if record["eventName"] == "INSERT":
                            new = record["dynamodb"]["NewImage"]
                            print("new order", new["sk"]["S"], new["status"]["S"])
            """, runnable=False),
        ],
        ["aws dynamodb query --table-name Orders --key-condition-expression 'pk = :p' --expression-attribute-values '{\":p\":{\"S\":\"CUST#42\"}}'", "aws dynamodb update-table --billing-mode PAY_PER_REQUEST", "aws dynamodb update-time-to-live --time-to-live-specification Enabled=true,AttributeName=expires_at", "aws dynamodb describe-continuous-backups", "aws dynamodb create-table --deletion-protection-enabled"],
        ["Low-cardinality partition keys (status, date) creating hot partitions.", "Using Scan with filters as a query: you pay to read the whole table.", "Forgetting GSIs are eventually consistent and can throttle the base table writes if under-provisioned."],
        [
            qa("intermediate", "Partition key vs sort key?", "The partition key determines which partition stores the item (via hashing) and must be supplied for Query. The sort key orders items within a partition and enables range conditions, so related items (a customer's orders) are fetched in one Query."),
            qa("intermediate", "GSI vs LSI?", "A GSI has a different partition key, its own capacity, can be added any time and is eventually consistent. An LSI keeps the table's partition key with a different sort key, must be created with the table, supports strong consistency and limits each partition key's data to 10 GB."),
            qa("advanced", "How do you avoid hot partitions?", "Choose high-cardinality keys that spread traffic, add write sharding (suffixing keys with a random or calculated shard number) for very hot items, cache hot reads with DAX, and avoid time-based keys that funnel all writes to one partition."),
            qa("advanced", "What are DynamoDB Streams used for?", "They provide an ordered, 24-hour log of item changes per partition. Lambda consumers use them for event-driven processing, materialized views, search indexing, auditing and cross-system replication."),
            qa("basic", "On-demand vs provisioned capacity?", "On-demand charges per request and scales instantly, good for unpredictable traffic. Provisioned sets RCUs/WCUs with auto scaling and reserved capacity, cheaper for steady, predictable load."),
        ],
        ["databases", "lambda", "messaging"],
        chain(
            ("Request", "pk=CUST#42", "Query", "The app queries orders for one customer."),
            ("Router", "hash(pk)", "Locate", "DynamoDB hashes the partition key to find the partition.", "key"),
            ("Partition", "sorted by sk", "Range read", "Items are read in sort-key order with begins_with ORDER#2026.", "hash"),
            ("Stream", "change log", "Capture", "Writes to the table are emitted to DynamoDB Streams.", "items"),
            ("Lambda", "consumer", "React", "A Lambda processes the change, e.g. publishing an OrderCreated event.", "record"),
        ),
    ),
    topic(
        "elasticache", "ElastiCache & MemoryDB", "storage-data", "intermediate", "EL",
        "Managed in-memory Valkey, Redis OSS and Memcached for caching, sessions and real-time data.",
        "A sticky note on your monitor with the answers you look up every day: much faster than walking to the archive room (database), but you must decide when the note is out of date.",
        "Amazon ElastiCache runs Valkey, Redis OSS and Memcached as managed clusters or as ElastiCache Serverless, which scales automatically without capacity planning. It serves microsecond reads for caching database results, sessions, leaderboards, rate limiting, pub/sub and queues. Valkey/Redis clusters support replication with automatic failover across AZs, cluster mode for sharding across node groups, persistence snapshots, encryption at rest with KMS, encryption in transit with TLS, and authentication with RBAC users or IAM. Memcached is simple, multi-threaded and non-persistent, suiting pure cache use. Common patterns are cache-aside (lazy loading: read cache, on miss read DB and populate with a TTL) and write-through (update cache on every write); TTLs and jitter prevent stale data and thundering herds. Amazon MemoryDB is a durable, Redis-compatible primary database using a multi-AZ transaction log, for when you need in-memory speed without losing data.",
        ["Caching expensive database queries or API responses.", "Session storage for stateless web tiers.", "Leaderboards with sorted sets.", "Rate limiting counters with expiry."],
        ["Cache-aside with TTLs is the default pattern.", "Enable Multi-AZ with automatic failover for production.", "Enable in-transit (TLS) and at-rest encryption.", "Valkey is open source and priced lower than Redis OSS on ElastiCache.", "Monitor evictions, CPU and memory; size for the hot set."],
        [
            ex("Cache-aside in Python", "basic", "Read from cache, fall back to the database, populate with a TTL.", "python", """
                import json, os, random
                import redis

                cache = redis.Redis(host=os.environ["CACHE_HOST"], port=6379, ssl=True)

                def get_product(pid: str, db) -> dict:
                    key = f"product:{pid}"
                    hit = cache.get(key)
                    if hit:
                        return json.loads(hit)
                    row = db.fetch_product(pid)
                    cache.set(key, json.dumps(row), ex=300 + random.randint(0, 60))  # TTL with jitter
                    return row
            """, runnable=False),
            ex("Serverless Valkey cache", "intermediate", "No nodes to size; encrypted and in private subnets.", "bash", """
                aws elasticache create-serverless-cache --serverless-cache-name app-cache \\
                  --engine valkey --subnet-ids subnet-0a000000000000000 subnet-0b000000000000000 \\
                  --security-group-ids sg-0cache000000000000 --kms-key-id alias/cache
                aws elasticache describe-serverless-caches --serverless-cache-name app-cache \\
                  --query 'ServerlessCaches[].Endpoint'
            """, runnable=False),
        ],
        ["aws elasticache create-serverless-cache --engine valkey", "aws elasticache create-replication-group --multi-az-enabled --automatic-failover-enabled", "aws elasticache describe-replication-groups", "aws elasticache test-failover", "valkey-cli --tls -h host INFO stats"],
        ["Caching without TTLs and serving stale data forever.", "All keys expiring at once and stampeding the database (add jitter, request coalescing).", "Treating ElastiCache as the source of truth; use MemoryDB if data must be durable."],
        [
            qa("basic", "Valkey/Redis vs Memcached?", "Valkey and Redis support rich data structures, replication, failover, persistence and pub/sub. Memcached is a simple multi-threaded key-value cache with no replication or persistence, fine for pure caching of simple objects."),
            qa("intermediate", "Cache-aside vs write-through?", "Cache-aside loads data into the cache on a miss and relies on TTLs or explicit invalidation; only requested data is cached. Write-through updates the cache on every write, so reads are fresh but you cache data that may never be read."),
            qa("advanced", "How do you prevent a cache stampede?", "Add random jitter to TTLs, use request coalescing or a short lock so only one caller recomputes a key, serve stale while revalidating, and pre-warm hot keys after deploys or failover."),
            qa("intermediate", "ElastiCache vs MemoryDB?", "ElastiCache is a cache: replication is asynchronous and a failover can lose recent writes. MemoryDB writes to a multi-AZ transaction log before acknowledging, so it can be the primary durable database with in-memory reads."),
        ],
        ["databases", "elb-autoscaling"],
        chain(
            ("App", "GET product:42", "Read", "The app first asks the cache for the key."),
            ("Cache", "Valkey", "Miss?", "On a hit, return in under a millisecond. On a miss, continue.", "GET"),
            ("Database", "RDS / Aurora", "Load", "Read the row from the database.", "miss"),
            ("Populate", "SET ex=300", "Store", "Write the value to the cache with a TTL plus jitter.", "row"),
            ("Next read", "cache hit", "Fast path", "Subsequent reads are served from memory until expiry.", "hit"),
        ),
    ),
]

# --- Integration, operations, IaC & analytics -----------------------------------------------------------------------

TOPICS += [
    topic(
        "step-functions", "Step Functions Workflows", "integration-ops", "intermediate", "ST",
        "Visual state machines that orchestrate Lambdas and AWS services with retries, branching and waits.",
        "A project manager with a checklist: do step one, if it fails retry twice, then wait for approval, run three tasks in parallel, and record exactly where things stopped if anything breaks.",
        "AWS Step Functions coordinates distributed work as a state machine defined in Amazon States Language (JSON) or JSONata. States include Task (call Lambda or one of 200+ AWS services directly via SDK integrations), Choice, Parallel, Map (fan out over items, with Distributed Map for millions of S3 objects), Wait, Pass, Succeed and Fail. Each state can declare Retry with exponential backoff and Catch to route errors to compensation logic, which makes saga patterns straightforward. Standard workflows run up to one year with exactly-once execution and full visual history, billed per state transition. Express workflows run up to five minutes at high volume with at-least-once semantics, billed per request and duration, suiting event processing. Integration patterns include request-response, run a job (.sync, waiting for ECS or Glue to finish) and wait for callback with a task token (human approval or external systems). Step Functions removes orchestration code from your Lambdas and gives an auditable timeline of every execution.",
        ["Order processing sagas with compensation on failure.", "ETL pipelines that run Glue jobs and wait for completion.", "Human approval steps via task tokens.", "Processing millions of S3 objects with Distributed Map."],
        ["Prefer direct service integrations over Lambda glue code.", "Retry and Catch on every Task that can fail.", "Standard: long, exactly-once, auditable. Express: short, high-volume, at-least-once.", "Payload limit 256 KB; pass S3 pointers for large data.", "Use idempotent tasks because retries happen."],
        [
            ex("Order saga with retry and compensation", "intermediate", "Charge, then reserve stock; refund if reservation fails.", "json", """
                {
                  "StartAt": "ChargeCard",
                  "States": {
                    "ChargeCard": {
                      "Type": "Task",
                      "Resource": "arn:aws:states:::lambda:invoke",
                      "Parameters": { "FunctionName": "charge", "Payload.$": "$" },
                      "Retry": [{ "ErrorEquals": ["States.TaskFailed"], "IntervalSeconds": 2, "MaxAttempts": 3, "BackoffRate": 2 }],
                      "Next": "ReserveStock"
                    },
                    "ReserveStock": {
                      "Type": "Task",
                      "Resource": "arn:aws:states:::dynamodb:updateItem",
                      "Parameters": {
                        "TableName": "Inventory",
                        "Key": { "sku": { "S.$": "$.sku" } },
                        "UpdateExpression": "SET stock = stock - :one",
                        "ConditionExpression": "stock > :zero",
                        "ExpressionAttributeValues": { ":one": { "N": "1" }, ":zero": { "N": "0" } }
                      },
                      "Catch": [{ "ErrorEquals": ["States.ALL"], "Next": "Refund" }],
                      "End": true
                    },
                    "Refund": {
                      "Type": "Task",
                      "Resource": "arn:aws:states:::lambda:invoke",
                      "Parameters": { "FunctionName": "refund", "Payload.$": "$" },
                      "Next": "OrderFailed"
                    },
                    "OrderFailed": { "Type": "Fail", "Error": "OutOfStock" }
                  }
                }
            """, runnable=False),
            ex("Start and inspect an execution", "basic", "Run with input and view its history.", "bash", """
                aws stepfunctions start-execution \\
                  --state-machine-arn arn:aws:states:eu-west-1:123456789012:stateMachine:orders \\
                  --input '{"orderId":"981","sku":"BOOK-1"}'
                aws stepfunctions get-execution-history \\
                  --execution-arn arn:aws:states:eu-west-1:123456789012:execution:orders:EXAMPLE \\
                  --query 'events[].type'
            """, runnable=False),
        ],
        ["aws stepfunctions create-state-machine --definition file://sm.json --role-arn r", "aws stepfunctions start-execution --input '{}'", "aws stepfunctions list-executions --status-filter FAILED", "aws stepfunctions send-task-success --task-token t --task-output '{}'", "aws stepfunctions test-state"],
        ["Passing large payloads between states and hitting the 256 KB limit.", "Choosing Express for workflows that need exactly-once execution or run longer than 5 minutes.", "No Catch on tasks, so one failure ends the workflow without compensation."],
        [
            qa("basic", "Why use Step Functions instead of chaining Lambdas?", "Chaining Lambdas couples them, duplicates retry logic and hides state. Step Functions centralizes orchestration with built-in retries, error handling, parallelism, waits and a visual audit trail, and can call services without any Lambda."),
            qa("intermediate", "Standard vs Express workflows?", "Standard workflows run up to a year with exactly-once semantics and detailed history, priced per state transition. Express workflows run up to five minutes, support very high rates, are at-least-once and priced per execution and duration."),
            qa("advanced", "How do you implement a human approval step?", "Use the waitForTaskToken integration pattern: a task sends the token (for example via SNS email or an API) and the execution pauses until someone calls SendTaskSuccess or SendTaskFailure with that token, or a heartbeat/timeout fires."),
            qa("advanced", "How do you implement a saga with Step Functions?", "Model each step as a Task with Retry, and add Catch transitions that run compensating actions in reverse order (refund, release stock) before ending in a Fail state, making each task idempotent."),
        ],
        ["lambda", "messaging", "databases"],
        chain(
            ("Event", "order placed", "Start", "An API or EventBridge rule starts an execution with the order as input."),
            ("Charge", "Lambda task", "Step 1", "The charge task runs with automatic retries and backoff.", "input"),
            ("Reserve", "DynamoDB task", "Step 2", "A direct DynamoDB integration decrements stock conditionally.", "charged"),
            ("Catch", "on failure", "Compensate", "If reservation fails, Catch routes to the refund task.", "error"),
            ("History", "visual audit", "Observe", "Every state transition is recorded for debugging.", "events"),
        ),
    ),
    topic(
        "eventbridge", "EventBridge: Buses, Rules, Pipes & Scheduler", "integration-ops", "intermediate", "EV",
        "Serverless event routing between AWS services, your apps and SaaS, with content-based filtering.",
        "A post sorting office: every parcel (event) arrives at one hub, sorting rules read the label and send copies to the right trucks (targets), and a calendar clerk (Scheduler) posts recurring parcels on time.",
        "Amazon EventBridge routes events, JSON documents with source, detail-type and detail, from AWS services, custom applications and SaaS partners onto event buses. Rules match events using event patterns (exact values, prefixes, numeric ranges, anything-but, exists) and deliver them to up to five targets per rule, such as Lambda, Step Functions, SQS, SNS, Kinesis, API destinations and other buses, including cross-account and cross-Region. Input transformers reshape the payload for each target. Delivery retries for up to 24 hours with a dead-letter queue for failures. The schema registry discovers event shapes and generates code bindings, and archive and replay support recovery and testing. EventBridge Pipes connects a source (SQS, Kinesis, DynamoDB Streams, MSK) to a target with optional filtering and enrichment in a point-to-point flow. EventBridge Scheduler runs one-time or recurring invocations of 270+ services at scale with time zones and flexible windows, replacing cron-style rules.",
        ["Decoupled microservices publishing domain events (OrderPlaced).", "Reacting to AWS events, such as an EC2 state change or a GuardDuty finding.", "Cross-account event routing to a central security bus.", "Millions of scheduled reminders with Scheduler."],
        ["Events are matched by content; producers do not know consumers.", "Use custom buses per domain and resource policies for cross-account.", "Configure DLQs and retry policies on targets.", "Pipes for point-to-point stream/queue integrations; rules for fan-out.", "At-least-once delivery: consumers must be idempotent."],
        [
            ex("Publish a domain event", "basic", "Put a custom event onto a domain bus.", "python", """
                import json
                import boto3

                events = boto3.client("events")
                events.put_events(Entries=[{
                    "EventBusName": "orders",
                    "Source": "com.acme.orders",
                    "DetailType": "OrderPlaced",
                    "Detail": json.dumps({"orderId": "981", "total": 4999, "country": "DE"}),
                }])
            """, runnable=False),
            ex("Rule pattern", "intermediate", "Match large German orders only.", "json", """
                {
                  "source": ["com.acme.orders"],
                  "detail-type": ["OrderPlaced"],
                  "detail": {
                    "country": ["DE"],
                    "total": [{ "numeric": [">=", 10000] }]
                  }
                }
            """, runnable=False),
            ex("Scheduler: daily report", "basic", "Invoke a Lambda at 07:00 Berlin time.", "bash", """
                aws scheduler create-schedule --name daily-report \\
                  --schedule-expression "cron(0 7 * * ? *)" --schedule-expression-timezone Europe/Berlin \\
                  --flexible-time-window Mode=OFF \\
                  --target '{"Arn":"arn:aws:lambda:eu-west-1:123456789012:function:report","RoleArn":"arn:aws:iam::123456789012:role/scheduler-invoke"}'
            """, runnable=False),
        ],
        ["aws events put-events --entries file://e.json", "aws events put-rule --event-bus-name orders --event-pattern file://p.json", "aws events put-targets --rule r --targets file://t.json", "aws events test-event-pattern", "aws scheduler create-schedule"],
        ["Patterns that match nothing because of a typo in source or detail-type; use test-event-pattern.", "Infinite loops where a target emits an event that matches its own rule.", "No DLQ: failed deliveries are dropped after retries."],
        [
            qa("intermediate", "EventBridge vs SNS?", "Both fan out. EventBridge offers richer content-based filtering on any field, schema registry, archive/replay, SaaS and AWS service sources and cross-account buses. SNS has higher throughput, lower latency and supports SMS, email and mobile push."),
            qa("intermediate", "What are EventBridge Pipes?", "Point-to-point integrations from a source like SQS, Kinesis or DynamoDB Streams to a target, with optional filtering, enrichment (Lambda, Step Functions, API) and transformation, replacing glue Lambdas that just move data."),
            qa("advanced", "How do you route events across accounts?", "Add a resource policy on the target account's event bus allowing PutEvents from the source account or org, then create a rule in the source account that targets that bus ARN (with a role). Rules in the target account route further."),
            qa("basic", "Why use EventBridge Scheduler instead of scheduled rules?", "Scheduler supports millions of schedules, one-time schedules, time zones, flexible windows, direct targets across many services, and per-schedule retry and DLQ settings."),
        ],
        ["messaging", "lambda", "observability-well-architected"],
        chain(
            ("Producer", "orders service", "Publish", "The orders service puts an OrderPlaced event on its bus."),
            ("Event bus", "orders", "Receive", "The bus accepts the event; producers do not know consumers.", "event"),
            ("Rules", "event patterns", "Match", "Each rule checks the pattern: source, type, country, total.", "match?"),
            ("Targets", "Lambda · SQS · SFN", "Deliver", "Matching rules deliver copies to their targets with retries.", "copies"),
            ("DLQ", "failed deliveries", "Recover", "Events that still fail go to a dead-letter queue for replay.", "failed"),
        ),
    ),
    topic(
        "sns-sqs-fanout", "SNS + SQS Fan-out Pattern", "integration-ops", "intermediate", "FO",
        "Publish once, deliver to many independent queues, each consumed and retried at its own pace.",
        "A newspaper (SNS topic) delivered to many subscribers' letterboxes (SQS queues). Each household reads at its own pace, and if someone is on holiday, their papers pile up in the box instead of being lost.",
        "In the fan-out pattern a producer publishes a message to an SNS topic, and SNS pushes a copy to every subscribed SQS queue (and optionally Lambda, HTTP or email). Each consumer service reads from its own queue, so a slow or failing consumer does not affect the others and messages are buffered durably. Subscription filter policies on message attributes or body let each queue receive only relevant messages. SQS visibility timeout hides a message while a consumer works on it; if the consumer does not delete it in time, it reappears for retry, and after maxReceiveCount it moves to a dead-letter queue. Standard topics and queues are at-least-once with best-effort ordering and nearly unlimited throughput; FIFO topics and queues provide ordering per message group and deduplication with lower throughput. The queue access policy must allow the topic to send messages, and with SSE-KMS both the topic and the queue's KMS keys must permit the services. Raw message delivery removes the SNS envelope.",
        ["OrderPlaced consumed independently by billing, shipping and analytics.", "Decoupling producers from slow downstream systems.", "Ordered processing per customer with FIFO.", "Buffering bursts for Lambda consumers with concurrency limits."],
        ["Each consumer gets its own queue and DLQ.", "Visibility timeout should exceed processing time (about 6x Lambda timeout for event source mappings).", "Filter policies reduce useless deliveries.", "Consumers must be idempotent: duplicates happen.", "Long polling (WaitTimeSeconds=20) cuts empty receives and cost."],
        [
            ex("Wire the fan-out", "intermediate", "Topic, queue, subscription with filter and raw delivery.", "bash", """
                aws sns create-topic --name order-events --attributes KmsMasterKeyId=alias/messaging
                aws sqs create-queue --queue-name shipping \\
                  --attributes '{"KmsMasterKeyId":"alias/messaging","VisibilityTimeout":"180"}'
                aws sns subscribe --topic-arn arn:aws:sns:eu-west-1:123456789012:order-events \\
                  --protocol sqs --notification-endpoint arn:aws:sqs:eu-west-1:123456789012:shipping \\
                  --attributes '{"RawMessageDelivery":"true","FilterPolicy":"{\\"type\\":[\\"OrderPlaced\\"]}"}'
            """, runnable=False),
            ex("Queue policy allowing only the topic", "intermediate", "SQS resource policy scoped with aws:SourceArn.", "json", """
                {
                  "Version": "2012-10-17",
                  "Statement": [
                    {
                      "Effect": "Allow",
                      "Principal": { "Service": "sns.amazonaws.com" },
                      "Action": "sqs:SendMessage",
                      "Resource": "arn:aws:sqs:eu-west-1:123456789012:shipping",
                      "Condition": { "ArnEquals": { "aws:SourceArn": "arn:aws:sns:eu-west-1:123456789012:order-events" } }
                    }
                  ]
                }
            """, runnable=False),
            ex("Idempotent consumer", "advanced", "Process each message once using a conditional write as a dedupe record.", "python", """
                import json
                import boto3

                table = boto3.resource("dynamodb").Table("processed-messages")

                def handler(event, context):
                    failures = []
                    for record in event["Records"]:
                        body = json.loads(record["body"])
                        try:
                            table.put_item(Item={"id": body["orderId"]}, ConditionExpression="attribute_not_exists(id)")
                            ship(body)
                        except table.meta.client.exceptions.ConditionalCheckFailedException:
                            continue  # duplicate delivery
                        except Exception:
                            failures.append({"itemIdentifier": record["messageId"]})
                    return {"batchItemFailures": failures}
            """, runnable=False),
        ],
        ["aws sns publish --topic-arn t --message file://m.json --message-attributes file://a.json", "aws sqs receive-message --queue-url u --wait-time-seconds 20", "aws sqs set-queue-attributes --attributes RedrivePolicy=...", "aws sqs start-message-move-task --source-arn dlq-arn", "aws sns set-subscription-attributes --attribute-name FilterPolicy"],
        ["Missing queue policy, so SNS deliveries silently fail.", "KMS-encrypted queue whose key policy does not allow sns.amazonaws.com to use it.", "Visibility timeout shorter than processing time, causing duplicate processing."],
        [
            qa("basic", "Why put SQS queues behind SNS instead of subscribing services directly?", "Queues buffer messages durably so each consumer can be offline, slow or retried independently, with its own DLQ. Direct push subscriptions lose that buffering and back-pressure."),
            qa("intermediate", "What is visibility timeout?", "After a consumer receives a message, SQS hides it for the visibility timeout. If the consumer deletes it, it is gone; if not, it becomes visible again for another attempt, which is how retries work."),
            qa("intermediate", "How do you get ordering?", "Use an SNS FIFO topic and SQS FIFO queues with a message group ID (such as customer ID); messages in a group are delivered in order and deduplicated by deduplication ID within five minutes. Throughput is lower than standard."),
            qa("advanced", "How do you handle poison messages?", "Configure a redrive policy with maxReceiveCount to move repeatedly failing messages to a DLQ, alarm on DLQ depth, use partial batch responses so one bad message does not fail the whole batch, and redrive after fixing the bug."),
        ],
        ["messaging", "lambda"],
        chain(
            ("Producer", "orders", "Publish", "The orders service publishes OrderPlaced to an SNS topic once."),
            ("SNS topic", "order-events", "Fan out", "SNS evaluates filter policies and copies the message to each subscription.", "publish"),
            ("SQS queues", "billing · shipping", "Buffer", "Each service's queue stores its copy durably.", "copies"),
            ("Consumers", "Lambda / ECS", "Process", "Consumers poll, process idempotently and delete messages.", "poll"),
            ("DLQ", "after 5 tries", "Isolate", "Messages failing repeatedly move to a dead-letter queue.", "poison"),
        ),
    ),
    topic(
        "cost-optimization", "Cost Optimization: Savings Plans, Spot & Rightsizing", "integration-ops", "intermediate", "CO",
        "Pay less for the same outcome: commit for steady load, use Spot for flexible work, delete waste.",
        "A household budget: sign a yearly phone contract for the calls you always make (Savings Plans), take cheap last-minute flights when your dates are flexible (Spot), and stop paying for the gym you never visit (idle resources).",
        "Cost optimization starts with visibility: tag resources (owner, env, cost-center), activate cost allocation tags, and use Cost Explorer, Cost and Usage Reports, Budgets and Cost Anomaly Detection. Then rightsize: Compute Optimizer recommends instance, EBS, Lambda and ECS sizes based on utilization, and Graviton instances often give 20 to 40% better price-performance. Commit for baseline usage: Compute Savings Plans discount EC2, Fargate and Lambda flexibly across families and Regions; EC2 Instance Savings Plans and Reserved Instances discount more for a specific family; database Reserved Instances cover RDS, ElastiCache, OpenSearch and Redshift. Spot Instances offer up to 90% off spare capacity with a two-minute interruption notice, ideal for stateless, batch, CI and containers using diversified instance types and capacity-optimized allocation. Eliminate waste: idle instances, unattached EBS volumes and Elastic IPs, old snapshots, oversized NAT data paths, unused load balancers and logs kept forever. Architect for cost with autoscaling, serverless, S3 lifecycle, VPC endpoints and caching.",
        ["Cutting a compute bill with a Compute Savings Plan for the baseline.", "Running CI and batch on Spot.", "Finding why the bill jumped this month.", "Scheduling dev environments to stop at night."],
        ["Visibility first: tags, Cost Explorer, Budgets, anomaly detection.", "Commit only for the steady baseline, not the peak.", "Spot needs interruption-tolerant design and instance diversification.", "Data transfer (NAT, cross-AZ, egress) is a frequent hidden cost.", "Review Trusted Advisor and Compute Optimizer monthly."],
        [
            ex("Budget with an alert", "basic", "Notify when forecasted spend exceeds 80% of the monthly budget.", "bash", """
                aws budgets create-budget --account-id 123456789012 \\
                  --budget '{"BudgetName":"monthly","BudgetLimit":{"Amount":"5000","Unit":"USD"},"TimeUnit":"MONTHLY","BudgetType":"COST"}' \\
                  --notifications-with-subscribers '[{"Notification":{"NotificationType":"FORECASTED","ComparisonOperator":"GREATER_THAN","Threshold":80},"Subscribers":[{"SubscriptionType":"EMAIL","Address":"finops@example.com"}]}]'
            """, runnable=False),
            ex("Top services last month", "intermediate", "Cost Explorer grouped by service.", "bash", """
                aws ce get-cost-and-usage --time-period Start=2026-09-01,End=2026-10-01 \\
                  --granularity MONTHLY --metrics UnblendedCost \\
                  --group-by Type=DIMENSION,Key=SERVICE \\
                  --query 'ResultsByTime[0].Groups[?Metrics.UnblendedCost.Amount>`100`].[Keys[0],Metrics.UnblendedCost.Amount]'
                aws ce get-savings-plans-purchase-recommendation --savings-plans-type COMPUTE_SP \\
                  --term-in-years ONE_YEAR --payment-option NO_UPFRONT --lookback-period-in-days THIRTY_DAYS
            """, runnable=False),
            ex("Spot-heavy Auto Scaling group", "advanced", "On-demand base of 2, the rest Spot across many instance types.", "json", """
                {
                  "MixedInstancesPolicy": {
                    "InstancesDistribution": {
                      "OnDemandBaseCapacity": 2,
                      "OnDemandPercentageAboveBaseCapacity": 0,
                      "SpotAllocationStrategy": "price-capacity-optimized"
                    },
                    "LaunchTemplate": {
                      "LaunchTemplateSpecification": { "LaunchTemplateName": "web", "Version": "$Latest" },
                      "Overrides": [{ "InstanceType": "m7g.large" }, { "InstanceType": "m6g.large" }, { "InstanceType": "c7g.xlarge" }, { "InstanceType": "r7g.large" }]
                    }
                  }
                }
            """, runnable=False),
        ],
        ["aws ce get-cost-and-usage --group-by Type=DIMENSION,Key=SERVICE", "aws budgets create-budget", "aws compute-optimizer get-ec2-instance-recommendations", "aws ec2 describe-volumes --filters Name=status,Values=available", "aws ce get-anomalies --date-interval Start=...,End=..."],
        ["Buying a 3-year commitment for peak usage that later drops.", "Running stateful singletons on Spot without a fallback.", "Ignoring NAT Gateway data processing and cross-AZ transfer when debugging cost."],
        [
            qa("basic", "Savings Plans vs Reserved Instances?", "Both trade a 1 or 3-year commitment for discounts. Compute Savings Plans commit to a dollar-per-hour spend and apply flexibly across EC2 families, Regions, Fargate and Lambda. Reserved Instances apply to specific instance attributes (and can reserve capacity when zonal)."),
            qa("intermediate", "How do you use Spot safely?", "Run only interruption-tolerant workloads, diversify across many instance types and AZs, use price-capacity-optimized allocation, handle the two-minute interruption notice (drain, checkpoint), and keep an on-demand base for critical capacity."),
            qa("intermediate", "What are common hidden costs?", "NAT Gateway data processing, cross-AZ and internet egress, CloudWatch Logs ingestion and indefinite retention, idle load balancers, unattached EBS volumes, public IPv4 addresses, old snapshots and over-provisioned databases."),
            qa("advanced", "How would you set up cost governance for many accounts?", "Consolidated billing in Organizations, mandatory tagging enforced with tag policies and SCPs, cost categories per team, Budgets and anomaly detection per account, shared Savings Plans at the payer, and monthly reviews with Compute Optimizer and Trusted Advisor."),
        ],
        ["ec2", "elb-autoscaling", "observability-well-architected"],
        chain(
            ("Tag", "owner · env", "See", "Tag everything and activate cost allocation tags."),
            ("Explore", "Cost Explorer", "Find", "Group spend by service, account and tag to find the biggest levers.", "costs"),
            ("Rightsize", "Compute Optimizer", "Shrink", "Downsize idle or oversized resources and move to Graviton.", "findings"),
            ("Commit", "Savings Plans", "Discount", "Cover the steady baseline with a Compute Savings Plan.", "baseline"),
            ("Spot", "flexible work", "Cheapest", "Run batch, CI and stateless tiers on Spot.", "burst"),
            ("Guard", "Budgets · anomaly", "Watch", "Budgets and anomaly detection alert on surprises.", "alerts"),
        ),
    ),
    topic(
        "backup-dr", "Backup & Disaster Recovery Strategies", "integration-ops", "advanced", "DR",
        "From backup-and-restore to multi-site active-active: pick by RTO, RPO and budget.",
        "Fire plans for a restaurant: keep recipes in a safe elsewhere (backup and restore), keep a small kitchen with the oven pilot light on (pilot light), run a smaller second restaurant (warm standby), or run two full restaurants at once (active-active).",
        "Disaster recovery is driven by two targets: RTO (how long you can be down) and RPO (how much data you can lose). AWS describes four strategies. Backup and restore: take backups (AWS Backup, snapshots, S3 replication) to another Region and rebuild infrastructure with IaC when needed; cheapest, with hours of RTO. Pilot light: core data is replicated continuously (Aurora Global Database, DynamoDB global tables, S3 CRR) and infrastructure is defined but scaled to zero or off; minutes to tens of minutes RTO. Warm standby: a scaled-down but fully working copy runs in the DR Region and is scaled up on failover. Multi-site active-active: full capacity serves traffic in two or more Regions with Route 53 or Global Accelerator routing, giving near-zero RTO and RPO at the highest cost and complexity. AWS Backup centralizes backup policies across services and accounts, with cross-Region and cross-account copies and vault lock for immutability. AWS Elastic Disaster Recovery replicates servers at block level for low RPO. Untested DR does not exist: run game days and automate failover runbooks.",
        ["Choosing a DR tier per application based on business impact.", "Ransomware-resilient backups in an isolated account.", "Regional failover for a customer-facing API.", "Compliance requirements for tested recovery."],
        ["Define RTO/RPO per workload before choosing a strategy.", "Cost and complexity rise from backup/restore to active-active.", "Keep backups in a separate account with vault lock.", "IaC is what makes fast rebuilds possible.", "Test failover and failback regularly."],
        [
            ex("AWS Backup plan with cross-Region copy", "intermediate", "Daily backups kept 35 days, copied to a DR vault.", "json", """
                {
                  "BackupPlanName": "prod-daily",
                  "Rules": [{
                    "RuleName": "daily",
                    "TargetBackupVaultName": "prod-vault",
                    "ScheduleExpression": "cron(0 3 * * ? *)",
                    "StartWindowMinutes": 60,
                    "Lifecycle": { "DeleteAfterDays": 35 },
                    "CopyActions": [{
                      "DestinationBackupVaultArn": "arn:aws:backup:eu-central-1:123456789012:backup-vault:dr-vault",
                      "Lifecycle": { "DeleteAfterDays": 35 }
                    }]
                  }]
                }
            """, runnable=False),
            ex("Lock the vault and assign resources", "advanced", "Vault lock makes recovery points undeletable for the retention window.", "bash", """
                aws backup create-backup-plan --backup-plan file://plan.json
                aws backup put-backup-vault-lock-configuration --backup-vault-name prod-vault \\
                  --min-retention-days 7 --max-retention-days 365 --changeable-for-days 3
                aws backup create-backup-selection --backup-plan-id plan-EXAMPLE \\
                  --backup-selection '{"SelectionName":"tagged","IamRoleArn":"arn:aws:iam::123456789012:role/backup","ListOfTags":[{"ConditionType":"STRINGEQUALS","ConditionKey":"backup","ConditionValue":"prod"}]}'
            """, runnable=False),
            ex("Strategy cheat sheet", "basic", "Approximate trade-offs.", "text", """
                Strategy            RPO            RTO              Cost
                Backup & restore    hours          hours to a day   $
                Pilot light         seconds-mins   tens of minutes  $$
                Warm standby        seconds        minutes          $$$
                Active-active       ~zero          ~zero            $$$$
            """, runnable=False),
        ],
        ["aws backup create-backup-plan --backup-plan file://p.json", "aws backup start-restore-job", "aws backup list-recovery-points-by-backup-vault --backup-vault-name v", "aws rds failover-global-cluster", "aws route53 update-health-check · ARC routing controls"],
        ["Backups in the same account and Region as production, deleted along with it.", "Never testing a restore: backups turn out incomplete or too slow to meet RTO.", "DR Region lacking service quotas, AMIs or capacity when you need it."],
        [
            qa("basic", "What are RTO and RPO?", "RTO (recovery time objective) is the maximum acceptable downtime after a disaster. RPO (recovery point objective) is the maximum acceptable data loss measured in time. Together they drive the DR strategy and cost."),
            qa("intermediate", "Pilot light vs warm standby?", "In pilot light only the data layer is live and replicated; compute is off or at zero and must be started and scaled on failover. Warm standby runs a smaller, fully functional copy of the whole stack that can take traffic immediately and is scaled up."),
            qa("advanced", "How do you protect backups from ransomware or a compromised admin?", "Copy backups to a separate, locked-down account and Region, enable AWS Backup Vault Lock in compliance mode (or S3 Object Lock), use a customer managed KMS key with a restrictive policy, and restrict deletion via SCPs."),
            qa("advanced", "What makes active-active hard?", "Data consistency across Regions (write conflicts, replication lag), routing and session affinity, idempotent and Region-aware applications, doubled cost, and testing. Many teams choose active-active for reads and a single write Region."),
        ],
        ["global-infra", "databases", "s3", "cloudfront-route53"],
        chain(
            ("Primary", "eu-west-1", "Normal", "Production serves all traffic from the primary Region."),
            ("Replicate", "Aurora · S3 CRR", "Copy data", "Data replicates continuously to the DR Region.", "data"),
            ("DR Region", "pilot light", "Standby", "Infrastructure is defined in IaC and runs minimal capacity.", "replica"),
            ("Disaster", "health checks fail", "Detect", "Health checks and alarms detect a Regional failure.", "outage"),
            ("Failover", "promote + scale", "Recover", "Promote the database, scale compute and shift DNS to DR.", "failover"),
        ),
    ),
    topic(
        "cloudformation", "CloudFormation", "devops", "intermediate", "CN",
        "AWS-native infrastructure as code: declare stacks in YAML, preview change sets, roll back on failure.",
        "An architect's blueprint handed to a construction firm: you describe the finished building and the firm works out the order of construction, and if something fails halfway it puts everything back the way it was.",
        "AWS CloudFormation provisions resources declared in JSON or YAML templates as stacks. Templates have Parameters, Mappings, Conditions, Resources (the only required section) and Outputs, with intrinsic functions such as !Ref, !GetAtt, !Sub and !ImportValue. CloudFormation determines dependencies, creates resources in order and rolls back automatically on failure. Change sets preview what an update will add, modify or replace before you execute it, and drift detection reveals manual changes. Stack policies and DeletionPolicy/UpdateReplacePolicy (Retain, Snapshot) protect stateful resources. Nested stacks and modules reuse templates; StackSets deploy the same stack to many accounts and Regions, integrated with Organizations. Hooks validate resources before provisioning (proactive controls), and the CloudFormation registry adds third-party and private resource types. Use a service role for deployments and never put secrets in parameters or templates; reference Secrets Manager or SSM dynamically instead.",
        ["Repeatable environments per account and Region.", "Org-wide baselines with StackSets.", "Infrastructure changes through code review and pipelines.", "Base for SAM and CDK, which both synthesize CloudFormation."],
        ["Always review a change set for Replacement before updating stateful resources.", "DeletionPolicy: Retain/Snapshot on databases and buckets.", "Use dynamic references for secrets: {{resolve:secretsmanager:...}}.", "Run cfn-lint and cfn-guard in CI.", "Stack outputs and exports link stacks, but exports cannot change while imported."],
        [
            ex("Versioned, encrypted bucket stack", "basic", "Parameters, a protected resource and an output.", "yaml", """
                AWSTemplateFormatVersion: "2010-09-09"
                Parameters:
                  Env: { Type: String, AllowedValues: [dev, prod] }
                Resources:
                  Data:
                    Type: AWS::S3::Bucket
                    DeletionPolicy: Retain
                    UpdateReplacePolicy: Retain
                    Properties:
                      BucketName: !Sub "acme-data-${Env}-${AWS::AccountId}"
                      VersioningConfiguration: { Status: Enabled }
                      BucketEncryption:
                        ServerSideEncryptionConfiguration:
                          - ServerSideEncryptionByDefault: { SSEAlgorithm: aws:kms, KMSMasterKeyID: alias/app-data }
                            BucketKeyEnabled: true
                      PublicAccessBlockConfiguration:
                        BlockPublicAcls: true
                        BlockPublicPolicy: true
                        IgnorePublicAcls: true
                        RestrictPublicBuckets: true
                Outputs:
                  BucketArn: { Value: !GetAtt Data.Arn, Export: { Name: !Sub "${Env}-data-bucket-arn" } }
            """, runnable=False),
            ex("Deploy via change set", "intermediate", "Preview, then execute; fail on empty change sets is disabled.", "bash", """
                aws cloudformation deploy --stack-name data-prod --template-file bucket.yaml \\
                  --parameter-overrides Env=prod --no-execute-changeset \\
                  --role-arn arn:aws:iam::123456789012:role/cfn-deploy
                aws cloudformation describe-change-set --stack-name data-prod --change-set-name <name> \\
                  --query 'Changes[].ResourceChange.[Action,LogicalResourceId,Replacement]'
                aws cloudformation execute-change-set --stack-name data-prod --change-set-name <name>
            """, runnable=False),
        ],
        ["aws cloudformation deploy --template-file t.yaml --stack-name s", "aws cloudformation create-change-set · describe-change-set", "aws cloudformation detect-stack-drift --stack-name s", "aws cloudformation describe-stack-events --stack-name s", "cfn-lint t.yaml · cfn-guard validate"],
        ["Changing a property that forces replacement (like a DB identifier) and losing data.", "Manual console edits causing drift and failed updates.", "Stacks stuck in UPDATE_ROLLBACK_FAILED; fix the cause and continue-update-rollback."],
        [
            qa("basic", "What is a change set?", "A preview of the changes CloudFormation will make for a stack update: which resources are added, modified or removed, and whether a modification requires replacement. You review it before executing."),
            qa("intermediate", "How do you protect a database from being deleted by a stack update?", "Set DeletionPolicy and UpdateReplacePolicy to Snapshot or Retain, enable deletion protection on the resource, apply a stack policy denying Update:Replace/Delete on it, and review change sets for replacements."),
            qa("intermediate", "What are StackSets?", "A way to deploy the same template to many accounts and Regions from an administrator account, with service-managed permissions through Organizations and automatic deployment to new accounts in target OUs."),
            qa("advanced", "How do you handle secrets in CloudFormation?", "Use dynamic references ({{resolve:secretsmanager:name:SecretString:password}} or ssm-secure) or let services manage them (ManageMasterUserPassword on RDS). Avoid NoEcho parameters with plaintext defaults and never commit secrets to templates."),
        ],
        ["observability-well-architected", "iam", "s3"],
        chain(
            ("Template", "YAML in Git", "Author", "Engineers declare resources in a template reviewed in a pull request."),
            ("Change set", "preview", "Preview", "CloudFormation computes adds, modifications and replacements.", "diff"),
            ("Stack", "ordered create", "Provision", "Resources are created in dependency order using a service role.", "execute"),
            ("Rollback", "on failure", "Protect", "If any resource fails, the stack rolls back to the last good state.", "failure?"),
            ("Drift", "detect", "Verify", "Drift detection compares live resources with the template.", "check"),
        ),
    ),
    topic(
        "cdk", "AWS CDK", "devops", "intermediate", "CD",
        "Define infrastructure in TypeScript or Python with reusable constructs that synthesize CloudFormation.",
        "Instead of drawing every brick on a blueprint, you use prefabricated rooms (constructs): 'add a secure bucket' or 'add a load-balanced Fargate service' and the factory produces the detailed blueprint for you.",
        "The AWS Cloud Development Kit lets you write infrastructure in general-purpose languages (TypeScript, Python, Java, C#, Go). An App contains Stacks, which contain Constructs at three levels: L1 (Cfn* classes mapping one-to-one to CloudFormation), L2 (opinionated resources with sensible defaults and helper methods like bucket.grantRead(role)) and L3 patterns (for example ApplicationLoadBalancedFargateService). cdk synth produces CloudFormation templates and assets; cdk diff shows changes; cdk deploy uploads assets and deploys via CloudFormation. Environments (account and Region) must be bootstrapped once, creating an S3 bucket, ECR repository and deployment roles. Grant methods generate least-privilege IAM policies, and Aspects and cdk-nag can enforce rules across a construct tree. CDK Pipelines builds self-mutating CI/CD pipelines that deploy stages to multiple accounts. Because it compiles to CloudFormation you keep rollbacks, change sets and drift detection.",
        ["Teams preferring code, loops and types over YAML.", "Internal construct libraries encoding company standards.", "Multi-account deployments with CDK Pipelines.", "Serverless apps with assets bundled automatically."],
        ["L1 = raw CFN, L2 = sensible defaults + grants, L3 = patterns.", "cdk diff before every deploy.", "Bootstrap each target account/Region.", "Use grant* methods instead of hand-written IAM policies.", "Keep logical IDs stable; renaming constructs replaces resources."],
        [
            ex("Fargate service with an L3 construct", "intermediate", "ALB, service, task role and logs in a few lines.", "python", """
                from aws_cdk import App, Stack, aws_ec2 as ec2, aws_ecs as ecs, aws_ecs_patterns as patterns, aws_s3 as s3
                from aws_cdk import aws_elasticloadbalancingv2 as elbv2
                from constructs import Construct

                class WebStack(Stack):
                    def __init__(self, scope: Construct, id: str, **kw):
                        super().__init__(scope, id, **kw)
                        vpc = ec2.Vpc(self, "Vpc", max_azs=2)
                        bucket = s3.Bucket(self, "Uploads", enforce_ssl=True,
                                           encryption=s3.BucketEncryption.KMS_MANAGED,
                                           block_public_access=s3.BlockPublicAccess.BLOCK_ALL)
                        svc = patterns.ApplicationLoadBalancedFargateService(
                            self, "Web", vpc=vpc, cpu=512, memory_limit_mib=1024, desired_count=2,
                            task_image_options=patterns.ApplicationLoadBalancedTaskImageOptions(
                                image=ecs.ContainerImage.from_asset("./app"), container_port=8080),
                            ssl_policy=elbv2.SslPolicy.TLS13_RES)
                        bucket.grant_read_write(svc.task_definition.task_role)

                app = App()
                WebStack(app, "web-dev")
                app.synth()
            """, runnable=False),
            ex("CDK workflow", "basic", "Bootstrap once, then diff and deploy.", "bash", """
                npm install -g aws-cdk
                cdk bootstrap aws://123456789012/eu-west-1 --profile dev
                cdk synth
                cdk diff web-dev --profile dev
                cdk deploy web-dev --profile dev --require-approval broadening
            """, runnable=False),
        ],
        ["cdk init app --language python", "cdk bootstrap aws://ACCOUNT/REGION", "cdk synth · cdk diff · cdk deploy", "cdk destroy stack", "cdk-nag · Aspects for policy checks"],
        ["Refactoring construct IDs and unintentionally replacing stateful resources.", "Environment-agnostic stacks that cannot look up VPCs or AZs; set env explicitly.", "Pinning nothing, so a library upgrade changes defaults unexpectedly."],
        [
            qa("basic", "How does CDK relate to CloudFormation?", "CDK code is synthesized into CloudFormation templates and assets, which CloudFormation then deploys. You keep CloudFormation's change sets, rollbacks and drift detection while writing in a programming language."),
            qa("intermediate", "Explain L1, L2 and L3 constructs.", "L1 constructs (CfnBucket) map exactly to CloudFormation resources. L2 constructs (Bucket) add secure defaults and helper methods like grants. L3 patterns combine many resources into an architecture, such as a load-balanced Fargate service."),
            qa("intermediate", "What does cdk bootstrap do?", "It deploys a CDKToolkit stack into an account and Region with an S3 bucket and ECR repository for assets and IAM roles for publishing and deploying, which cdk deploy assumes."),
            qa("advanced", "CDK vs Terraform?", "CDK is AWS-focused, compiles to CloudFormation and lets you use full programming languages and AWS-managed state. Terraform is multi-cloud, uses HCL and its own state file with plan/apply, and has a broad provider ecosystem. Choice often follows team skills and multi-cloud needs."),
        ],
        ["observability-well-architected", "lambda", "elb-autoscaling"],
        chain(
            ("Code", "Python / TS", "Write", "Developers compose constructs in a familiar language."),
            ("Synth", "cdk synth", "Compile", "CDK synthesizes CloudFormation templates and asset bundles.", "constructs"),
            ("Assets", "S3 + ECR", "Publish", "Lambda code and container images upload to bootstrap storage.", "template"),
            ("Diff", "cdk diff", "Review", "Changes and IAM broadening are shown for approval.", "changes"),
            ("Deploy", "CloudFormation", "Apply", "CloudFormation deploys the stack with rollback on failure.", "deploy"),
        ),
    ),
    topic(
        "terraform-aws", "Terraform on AWS", "devops", "intermediate", "TF",
        "HashiCorp Terraform or OpenTofu with the AWS provider: plan, apply, remote state and modules.",
        "A shopping list compared with your pantry: Terraform looks at what you have (state), what the list says (config), and produces exactly what to buy or throw away (plan) before you go to the shop (apply).",
        "Terraform (and the open-source fork OpenTofu) manages AWS resources through the AWS provider using declarative HCL. terraform plan compares configuration, the state file and real infrastructure to show the changes; terraform apply executes them. State maps resources to real IDs and must be stored remotely and securely for teams: an S3 backend with versioning, SSE-KMS and state locking (native S3 lockfiles in recent versions, or DynamoDB historically). Credentials come from the standard AWS chain, ideally an assumed role or OIDC in CI, never hardcoded in providers. Modules package reusable infrastructure (VPC, EKS) with inputs and outputs, and workspaces or separate state per environment isolate blast radius. Data sources read existing resources, and import blocks adopt manually created resources. Policy as code with Sentinel, OPA or Checkov and tflint catch misconfigurations before apply. Lifecycle rules like prevent_destroy and create_before_destroy protect critical resources and enable zero-downtime replacements.",
        ["Multi-cloud or multi-provider infrastructure (AWS plus DNS, monitoring, GitHub).", "Shared module registries for platform teams.", "GitOps-style plan on PR, apply on merge.", "Importing legacy click-ops resources into code."],
        ["Remote state in S3 with encryption, versioning and locking.", "One state per environment/component to limit blast radius.", "Assume roles per account via provider assume_role.", "Pin provider and module versions.", "Never commit state files; they can contain sensitive values."],
        [
            ex("Backend and provider", "basic", "Encrypted, locked remote state; credentials from the assumed role.", "hcl", """
                terraform {
                  required_version = ">= 1.10"
                  required_providers {
                    aws = { source = "hashicorp/aws", version = "~> 6.0" }
                  }
                  backend "s3" {
                    bucket       = "acme-tfstate-123456789012"
                    key          = "prod/network/terraform.tfstate"
                    region       = "eu-west-1"
                    encrypt      = true
                    kms_key_id   = "alias/tfstate"
                    use_lockfile = true
                  }
                }

                provider "aws" {
                  region = "eu-west-1"
                  assume_role { role_arn = "arn:aws:iam::123456789012:role/terraform-deploy" }
                  default_tags { tags = { owner = "platform", env = "prod", managed-by = "terraform" } }
                }
            """, runnable=False),
            ex("Module and protected resource", "intermediate", "Use a community VPC module; protect the database from destroy.", "hcl", """
                module "vpc" {
                  source  = "terraform-aws-modules/vpc/aws"
                  version = "~> 6.0"
                  name    = "prod"
                  cidr    = "10.10.0.0/16"
                  azs             = ["eu-west-1a", "eu-west-1b", "eu-west-1c"]
                  private_subnets = ["10.10.1.0/24", "10.10.2.0/24", "10.10.3.0/24"]
                  public_subnets  = ["10.10.101.0/24", "10.10.102.0/24", "10.10.103.0/24"]
                  enable_nat_gateway = true
                  one_nat_gateway_per_az = true
                }

                resource "aws_db_instance" "orders" {
                  identifier                  = "orders"
                  engine                      = "postgres"
                  instance_class              = "db.m7g.large"
                  allocated_storage           = 100
                  username                    = "app_admin"
                  manage_master_user_password = true
                  storage_encrypted           = true
                  multi_az                    = true
                  deletion_protection         = true
                  lifecycle { prevent_destroy = true }
                }
            """, runnable=False),
            ex("Daily workflow", "basic", "Format, validate, plan to a file, apply that exact plan.", "bash", """
                terraform init
                terraform fmt -check && terraform validate
                terraform plan -out=tfplan
                terraform show -no-color tfplan | less
                terraform apply tfplan
            """, runnable=False),
        ],
        ["terraform init · plan -out=tfplan · apply tfplan", "terraform state list · state show addr", "terraform import / import {} blocks", "terraform plan -refresh-only (detect drift)", "tflint · checkov -d ."],
        ["Local state on a laptop, lost or conflicting between engineers.", "Hardcoding access keys in the provider block; use roles and OIDC.", "One giant state for everything: slow plans and huge blast radius."],
        [
            qa("basic", "What is Terraform state and why does it matter?", "State records which real resources correspond to each resource in your configuration, plus attributes. Terraform uses it to compute plans; losing or corrupting it means Terraform no longer knows what it manages."),
            qa("intermediate", "How do you store state safely on AWS?", "Use the S3 backend with a dedicated bucket that has versioning, SSE-KMS, Block Public Access and restricted IAM, enable state locking (use_lockfile or DynamoDB), and separate state per environment."),
            qa("intermediate", "How should CI authenticate Terraform to AWS?", "Use OIDC federation from the CI provider to assume a deploy role with short-lived credentials, scoped per account and environment. No long-lived access keys in CI secrets."),
            qa("advanced", "Terraform vs CloudFormation?", "Terraform is multi-provider, plan/apply with a self-managed state file and a large module ecosystem. CloudFormation is AWS-native with managed state, automatic rollback, StackSets and day-one support for many services. Both are valid; consistency within an organization matters most."),
        ],
        ["observability-well-architected", "vpc", "iam"],
        chain(
            ("HCL", "config in Git", "Write", "Engineers change HCL in a pull request."),
            ("Plan", "terraform plan", "Compare", "Terraform compares config, state and real resources.", "diff"),
            ("Review", "PR comment", "Approve", "The plan is posted on the PR and reviewed with policy checks.", "plan"),
            ("Apply", "assumed role", "Change", "On merge, CI applies the saved plan using an OIDC-assumed role.", "approved"),
            ("State", "S3 + lock", "Record", "Updated state is written to the encrypted, locked S3 backend.", "state"),
        ),
    ),
    topic(
        "systems-manager", "Systems Manager: Session Manager & Patch Manager", "devops", "basic", "SY",
        "Operate EC2 and on-prem fleets without SSH keys or bastions: shell access, patching, commands and inventory.",
        "A remote facilities team with master keycards: they can open any server room through the front office (no back doors), apply safety updates on a schedule, and every visit is recorded on camera.",
        "AWS Systems Manager (SSM) manages EC2 instances and on-premises servers that run the SSM Agent and have an instance profile (or hybrid activation) allowing them to talk to the SSM service, either through internet egress or VPC interface endpoints. Session Manager gives browser or CLI shell access and port forwarding with IAM-controlled permissions, no inbound ports, no SSH keys and no bastion hosts, with sessions logged to CloudWatch Logs or S3 and encrypted with KMS. Run Command executes documents (scripts) across fleets selected by tags with rate control. Patch Manager applies patch baselines during maintenance windows and reports compliance; Quick Setup and patch policies configure it org-wide. State Manager enforces configuration, Inventory collects software and configuration data, Automation runbooks perform multi-step operations (such as remediation from Config). Parameter Store, OpsCenter, Incident Manager and Fleet Manager complete the toolkit.",
        ["Replacing SSH and bastion hosts with audited sessions.", "Monthly OS patching across thousands of instances.", "Running a hotfix command on every instance with a tag.", "Port forwarding to a private RDS for debugging."],
        ["Instances need the SSM Agent, an instance profile with AmazonSSMManagedInstanceCore and network path to SSM.", "Private subnets: add ssm, ssmmessages and ec2messages endpoints (or NAT).", "Control access with IAM conditions on tags (ssm:resourceTag).", "Log sessions to S3/CloudWatch with KMS encryption.", "Patch baselines + maintenance windows + compliance reporting."],
        [
            ex("Start a session and port-forward", "basic", "Shell to an instance and tunnel to a private database.", "bash", """
                aws ssm start-session --target i-0123456789abcdef0
                aws ssm start-session --target i-0123456789abcdef0 \\
                  --document-name AWS-StartPortForwardingSessionToRemoteHost \\
                  --parameters '{"host":["orders-db.cluster-abc.eu-west-1.rds.amazonaws.com"],"portNumber":["5432"],"localPortNumber":["15432"]}'
            """, runnable=False),
            ex("Patch and run commands by tag", "intermediate", "Install security patches on the web fleet, 10% at a time.", "bash", """
                aws ssm send-command --document-name AWS-RunPatchBaseline \\
                  --targets Key=tag:role,Values=web --parameters Operation=Install \\
                  --max-concurrency 10% --max-errors 1
                aws ssm list-compliance-summaries --filters Key=ComplianceType,Values=Patch,Type=EQUAL
            """, runnable=False),
            ex("IAM: sessions only to dev instances", "intermediate", "Developers can start sessions only on instances tagged env=dev.", "json", """
                {
                  "Version": "2012-10-17",
                  "Statement": [
                    {
                      "Effect": "Allow",
                      "Action": "ssm:StartSession",
                      "Resource": "arn:aws:ec2:eu-west-1:123456789012:instance/*",
                      "Condition": { "StringEquals": { "ssm:resourceTag/env": "dev" } }
                    },
                    {
                      "Effect": "Allow",
                      "Action": ["ssm:TerminateSession", "ssm:ResumeSession"],
                      "Resource": "arn:aws:ssm:*:*:session/${aws:username}-*"
                    }
                  ]
                }
            """, runnable=False),
        ],
        ["aws ssm describe-instance-information", "aws ssm start-session --target i-x", "aws ssm send-command --document-name AWS-RunShellScript --targets Key=tag:role,Values=web", "aws ssm create-maintenance-window", "aws ssm describe-instance-patch-states --instance-ids i-x"],
        ["Instance not showing as managed: missing instance profile, agent or network path to SSM endpoints.", "Granting ssm:StartSession on * to everyone, which is equivalent to root shell on every instance.", "Patching all instances at once without max-concurrency and taking the service down."],
        [
            qa("basic", "Why use Session Manager instead of SSH?", "No inbound ports, bastions or SSH keys to manage; access is controlled and audited through IAM and CloudTrail, sessions can be logged in full, and it works for instances in private subnets."),
            qa("intermediate", "What does an instance need to be managed by SSM?", "The SSM Agent (preinstalled on many AMIs), an IAM instance profile with the AmazonSSMManagedInstanceCore policy, and network access to the SSM endpoints via NAT or VPC interface endpoints (ssm, ssmmessages, ec2messages)."),
            qa("intermediate", "How does Patch Manager work?", "A patch baseline defines which patches are approved (by classification, severity and auto-approval delay). The AWS-RunPatchBaseline document scans or installs them, usually during a maintenance window targeting tagged instances, and compliance is reported to SSM and Security Hub."),
            qa("advanced", "How do you automatically remediate a non-compliant resource?", "Attach an SSM Automation runbook as a remediation action on an AWS Config rule (or trigger it from EventBridge). The runbook runs with an assumed role to fix the resource, for example enabling encryption or closing a security group port."),
        ],
        ["ec2", "iam", "vpc"],
        chain(
            ("Engineer", "ssm start-session", "Request", "An engineer requests a session; IAM checks tag-based permissions."),
            ("SSM", "service", "Broker", "Systems Manager brokers the session; no inbound ports are opened.", "StartSession"),
            ("Endpoint", "ssmmessages", "Channel", "The agent's outbound connection via VPC endpoints carries the session.", "TLS"),
            ("Agent", "on instance", "Shell", "The SSM Agent opens a shell as a restricted user.", "channel"),
            ("Logs", "S3 / CloudWatch", "Audit", "Session activity is logged and encrypted with KMS.", "transcript"),
        ),
    ),
    topic(
        "kinesis", "Kinesis Data Streams & Firehose", "analytics", "advanced", "KI",
        "Real-time streaming: ordered shards for custom consumers, and Firehose for zero-code delivery to S3 and more.",
        "Kinesis Data Streams is a set of conveyor belts (shards) where items keep their order and stay on the belt for a day or more so several workers can inspect them. Firehose is a delivery van that collects items, packs them into boxes and drops them at the warehouse (S3) every few minutes.",
        "Amazon Kinesis Data Streams ingests ordered records into shards; each provisioned shard handles 1 MB/s or 1,000 records/s in and 2 MB/s out, while on-demand mode scales capacity automatically. A record's partition key determines its shard, guaranteeing order per key. Records are retained 24 hours by default and up to 365 days, so multiple consumers can read and replay independently; enhanced fan-out gives each consumer dedicated 2 MB/s per shard with push delivery. Consumers include Lambda (event source mapping with batching, bisect-on-error and parallelization factor), the Kinesis Client Library on ECS/EC2 with DynamoDB checkpointing, and Managed Service for Apache Flink for stateful stream processing. Amazon Data Firehose is fully managed delivery: it buffers by size or time, optionally transforms with Lambda, converts to Parquet, and delivers to S3, Redshift, OpenSearch, Splunk, Snowflake or Iceberg tables, with no shards to manage. Both support server-side encryption with KMS. Amazon MSK is the alternative when you need Kafka APIs.",
        ["Clickstream and IoT telemetry ingestion.", "Real-time fraud detection with Flink.", "Log delivery into an S3 data lake with Firehose.", "Change data capture fan-out to multiple consumers."],
        ["Order is guaranteed per partition key within a shard.", "Hot partition keys throttle a single shard.", "Data Streams: you build consumers; Firehose: managed delivery, near real time (buffered).", "Use enhanced fan-out when many consumers share a stream.", "Lambda consumers: configure bisect-on-error, max retries and an on-failure destination."],
        [
            ex("Produce records with boto3", "intermediate", "Partition by device id so each device's events stay ordered.", "python", """
                import json
                import boto3

                kinesis = boto3.client("kinesis")

                def send(events: list[dict]) -> None:
                    resp = kinesis.put_records(
                        StreamName="telemetry",
                        Records=[{"Data": json.dumps(e).encode(), "PartitionKey": e["device_id"]} for e in events],
                    )
                    if resp["FailedRecordCount"]:
                        failed = [e for e, r in zip(events, resp["Records"]) if "ErrorCode" in r]
                        raise RuntimeError(f"retry {len(failed)} throttled records with backoff")
            """, runnable=False),
            ex("Stream and Firehose to S3", "intermediate", "On-demand stream with KMS; Firehose delivers Parquet-ready batches.", "bash", """
                aws kinesis create-stream --stream-name telemetry --stream-mode-details StreamMode=ON_DEMAND
                aws kinesis start-stream-encryption --stream-name telemetry --encryption-type KMS --key-id alias/streams
                aws firehose create-delivery-stream --delivery-stream-name telemetry-to-s3 \\
                  --delivery-stream-type KinesisStreamAsSource \\
                  --kinesis-stream-source-configuration KinesisStreamARN=arn:aws:kinesis:eu-west-1:123456789012:stream/telemetry,RoleARN=arn:aws:iam::123456789012:role/firehose \\
                  --extended-s3-destination-configuration file://s3-dest.json
            """, runnable=False),
        ],
        ["aws kinesis create-stream --stream-mode-details StreamMode=ON_DEMAND", "aws kinesis put-record --stream-name s --partition-key k --data <base64>", "aws kinesis describe-stream-summary --stream-name s", "aws kinesis register-stream-consumer (enhanced fan-out)", "aws firehose create-delivery-stream"],
        ["Low-cardinality partition keys creating a hot shard and throttling.", "Lambda consumer stuck retrying one bad record and blocking the shard; enable bisect and failure destinations.", "Expecting Firehose to be real-time: it buffers for seconds to minutes."],
        [
            qa("intermediate", "Kinesis Data Streams vs Firehose?", "Data Streams stores ordered records for replay and supports multiple custom consumers with low latency; you manage shards (or use on-demand) and consumers. Firehose is a fully managed, buffered delivery service to destinations like S3 and Redshift with optional transformation, no consumers to write."),
            qa("intermediate", "Kinesis vs SQS?", "Kinesis keeps an ordered, replayable log that multiple consumers read independently, ideal for streaming analytics. SQS is a queue where each message is processed by one consumer and deleted, ideal for task distribution."),
            qa("advanced", "How do you scale a provisioned stream?", "Split hot shards or use UpdateShardCount to increase shards, choose high-cardinality partition keys, or switch to on-demand mode. Consumers scale with shard count; Lambda can use a parallelization factor up to 10 per shard."),
            qa("advanced", "How is ordering guaranteed and when can it break?", "Records with the same partition key go to the same shard and are read in sequence order. Ordering can break with producer retries (out-of-order resubmission), resharding (read parent shards fully before children, which KCL handles) or consumer parallelism across keys."),
        ],
        ["messaging", "lambda", "s3"],
        chain(
            ("Producers", "devices · apps", "Put", "Producers put records with a partition key such as device_id."),
            ("Shards", "ordered per key", "Store", "Records land in a shard by hash of the key and are retained.", "records"),
            ("Consumers", "Lambda · Flink", "Process", "Real-time consumers read in order and checkpoint progress.", "stream"),
            ("Firehose", "buffer 60s", "Batch", "Firehose buffers, transforms and compresses records.", "copy"),
            ("S3 lake", "Parquet", "Land", "Batches land in S3, partitioned by date, for Athena.", "files"),
        ),
    ),
    topic(
        "athena-glue-lake", "Athena, Glue & the S3 Data Lake", "analytics", "intermediate", "AT",
        "Store data once in S3, catalogue it with Glue, query it with SQL in Athena, govern it with Lake Formation.",
        "S3 is a vast library of books, the Glue Data Catalog is the card index telling you which shelf has what, Glue crawlers are librarians cataloguing new arrivals, and Athena is a reading room where you ask questions in SQL and pay only for the pages you read.",
        "A data lake on AWS stores raw and curated data in S3, typically in zones such as raw, clean and curated, in columnar formats like Parquet or table formats like Apache Iceberg. The AWS Glue Data Catalog is a Hive-compatible metastore of databases, tables, schemas and partitions used by Athena, EMR, Redshift Spectrum and Glue jobs. Glue crawlers infer schemas and partitions, and Glue ETL jobs (serverless Spark or Python) transform data, with job bookmarks for incremental processing. Amazon Athena runs serverless SQL (Trino engine) directly on S3 and charges per TB scanned, so partitioning, compression and columnar formats drastically cut cost and time; partition projection avoids managing partitions for predictable layouts. Athena supports Iceberg for ACID updates, time travel and MERGE, CTAS to write optimized tables, and federated queries to other sources. Workgroups enforce per-team limits, result locations and encryption. AWS Lake Formation adds fine-grained permissions (database, table, column, row and cell level) and tag-based access control across the catalog.",
        ["Ad hoc SQL over logs (CloudTrail, ALB, VPC Flow Logs) in S3.", "Central analytics lake shared across accounts.", "Serverless ETL from raw JSON to curated Parquet.", "Fine-grained data access for analysts with Lake Formation."],
        ["Partition by commonly filtered columns (date) and use Parquet + compression.", "Athena bills per data scanned; SELECT only needed columns.", "Use Iceberg tables for updates, deletes and schema evolution.", "Workgroups: query limits, encrypted results, cost control.", "Lake Formation for column/row-level security."],
        [
            ex("Partitioned table with projection", "intermediate", "ALB logs table with date projection, no crawler needed.", "text", """
                CREATE EXTERNAL TABLE alb_logs (
                  type string, time string, elb string, client_ip string, request_url string,
                  elb_status_code int, target_processing_time double
                )
                PARTITIONED BY (day string)
                ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.RegexSerDe'
                WITH SERDEPROPERTIES ('input.regex' = '([^ ]*) ([^ ]*) ([^ ]*) ([^ ]*):[0-9]* .*')
                LOCATION 's3://acme-logs/alb/AWSLogs/123456789012/elasticloadbalancing/eu-west-1/'
                TBLPROPERTIES (
                  'projection.enabled' = 'true',
                  'projection.day.type' = 'date',
                  'projection.day.range' = '2025/01/01,NOW',
                  'projection.day.format' = 'yyyy/MM/dd',
                  'storage.location.template' = 's3://acme-logs/alb/AWSLogs/123456789012/elasticloadbalancing/eu-west-1/${day}'
                );

                SELECT elb_status_code, count(*) AS hits
                FROM alb_logs WHERE day = '2026/10/17' AND elb_status_code >= 500
                GROUP BY 1 ORDER BY hits DESC;
            """, runnable=False),
            ex("CTAS to Parquet / Iceberg", "advanced", "Rewrite raw JSON into a partitioned Iceberg table.", "text", """
                CREATE TABLE curated.orders
                WITH (table_type = 'ICEBERG', format = 'PARQUET',
                      location = 's3://acme-lake/curated/orders/', partitioning = ARRAY['day(order_ts)'])
                AS SELECT order_id, customer_id, total, CAST(order_ts AS timestamp(6)) AS order_ts
                FROM raw.orders_json;
            """, runnable=False),
            ex("Run a query from the CLI", "basic", "Use a workgroup with encrypted results and scan limits.", "bash", """
                aws athena start-query-execution --work-group analysts \\
                  --query-string "SELECT count(*) FROM curated.orders WHERE order_ts > current_date - interval '7' day"
                aws athena get-query-results --query-execution-id 11111111-2222-3333-4444-555555555555
                aws glue start-crawler --name raw-orders
            """, runnable=False),
        ],
        ["aws athena start-query-execution --work-group wg --query-string 'SELECT ...'", "aws glue start-crawler --name c", "aws glue get-tables --database-name raw", "aws glue start-job-run --job-name j", "aws lakeformation grant-permissions"],
        ["Querying unpartitioned JSON and paying to scan terabytes for each query.", "Millions of tiny files; compact into 128 MB to 1 GB files.", "Crawlers changing schemas unexpectedly in production tables."],
        [
            qa("basic", "What is Athena and how is it billed?", "Athena is a serverless SQL engine that queries data in S3 using the Glue Data Catalog. You pay per TB of data scanned (or for provisioned capacity), so reducing scanned data via partitions, columnar formats and compression reduces cost."),
            qa("intermediate", "What does the Glue Data Catalog do?", "It stores metadata (databases, tables, schemas, partitions, locations) for data in S3 and other sources, shared by Athena, Glue ETL, EMR and Redshift Spectrum, acting as the lake's central metastore."),
            qa("intermediate", "How do you make Athena queries faster and cheaper?", "Store data as Parquet or ORC with compression, partition by frequently filtered columns, use partition projection, compact small files, select only needed columns and use CTAS or Iceberg to maintain optimized tables."),
            qa("advanced", "Why use Iceberg tables in a data lake?", "Iceberg adds ACID transactions, row-level updates/deletes (MERGE), schema and partition evolution, time travel and snapshot isolation on top of files in S3, making the lake behave like a warehouse table without rewriting entire partitions."),
        ],
        ["s3", "observability-well-architected"],
        chain(
            ("Ingest", "Firehose · DMS", "Land raw", "Data lands in the S3 raw zone."),
            ("Crawler", "Glue", "Catalogue", "A Glue crawler infers schema and partitions into the Data Catalog.", "files"),
            ("ETL", "Glue Spark", "Transform", "Glue jobs clean data into partitioned Parquet or Iceberg.", "tables"),
            ("Lake Formation", "column/row ACL", "Govern", "Lake Formation grants fine-grained access to curated tables.", "curated"),
            ("Athena", "SQL per TB", "Query", "Analysts query with SQL, scanning only needed partitions and columns.", "SELECT"),
        ),
    ),
]

SCENARIOS = [
    {"level": "advanced", "topic": "iam-roles-sts", "q": "A CI pipeline uses a long-lived IAM user access key stored as a CI secret to deploy to three accounts.", "a": "Replace it with OIDC federation: create an OIDC identity provider in each account (or a central one), a deploy role whose trust policy pins aud and sub to the repository and branch, and assume it with AssumeRoleWithWebIdentity. Delete the user's keys, scope each role to what that pipeline deploys, and review CloudTrail for prior key usage."},
    {"level": "advanced", "topic": "kms-encryption", "q": "After a migration, an application role gets AccessDenied reading objects from an S3 bucket even though its IAM policy allows s3:GetObject.", "a": "The objects are encrypted with SSE-KMS using a customer managed key, and the role lacks kms:Decrypt in its policy or is not allowed by the key policy. Grant kms:Decrypt on the key (optionally with kms:ViaService for S3), check the key policy allows IAM policies or the role directly, and confirm no SCP or bucket policy deny applies."},
    {"level": "intermediate", "topic": "vpc-endpoints-privatelink", "q": "ECS Fargate tasks in private subnets with no NAT gateway are stuck in PENDING with image pull errors.", "a": "Tasks cannot reach ECR. Add interface endpoints for ecr.api and ecr.dkr, an S3 gateway endpoint (image layers are stored in S3), and a CloudWatch Logs endpoint for the log driver, plus Secrets Manager or SSM endpoints if the task uses secrets. Ensure endpoint security groups allow 443 from the tasks and private DNS is enabled."},
    {"level": "advanced", "topic": "dynamodb-modeling", "q": "A DynamoDB table throttles writes at peak although total consumed capacity is well below the table's limit.", "a": "Writes are concentrated on a hot partition key (for example a date or a single tenant). Redesign the key for higher cardinality or add write sharding with a suffix, check that GSIs are not throttling and back-pressuring the table, and use on-demand mode or adaptive capacity while fixing the access pattern."},
    {"level": "advanced", "topic": "backup-dr", "q": "The business asks for an RTO of 15 minutes and RPO of 1 minute for the order platform if eu-west-1 fails, without doubling cost.", "a": "Use warm standby or pilot light with continuous data replication: Aurora Global Database (sub-second RPO), DynamoDB global tables, S3 CRR with RTC, and IaC-defined compute in eu-central-1 running at minimum size. Use Route 53 failover with health checks or ARC routing controls, pre-raise quotas, automate the runbook and run regular game days."},
    {"level": "intermediate", "topic": "cost-optimization", "q": "NAT Gateway is the third-largest line on the bill for a containerized app in private subnets.", "a": "Find which traffic flows through NAT with VPC Flow Logs. Usually it is image pulls from ECR, S3 access and CloudWatch Logs: add an S3 gateway endpoint and interface endpoints for ECR and Logs, keep NAT and workloads in the same AZ to avoid cross-AZ charges, and cache dependencies in images."},
]

TOPICS += [
    topic(
        "cross-account-iam-troubleshooting", "Cross-Account IAM Troubleshooting Lab Guide", "security", "advanced", "IAM", "Trace an AssumeRole failure across both accounts",
        "Two organizations must agree on a visitor: the source account authorizes the request, and the destination role admits the visitor and grants only the needed actions.",
        "Cross-account access is a chain of independent checks. Confirm the source caller with sts:GetCallerIdentity; verify the source identity policy allows sts:AssumeRole on the exact target role; verify the target trust policy names the exact source role/account and matches ExternalId, MFA or OIDC conditions. After assumption succeeds, inspect the target role's identity permissions, session policy, permissions boundary, resource policy, SCP/RCP and explicit denies. For S3, KMS or SQS, check resource-side policies as well. Use CloudTrail's event in the destination account to identify which principal and condition failed.",
        ["Debugging CI/CD deployments into multiple AWS accounts.", "Setting up vendor access with ExternalId.", "Explaining why a role works in one account but fails in another."],
        ["Source side: the caller needs sts:AssumeRole for the exact role ARN.", "Target side: the role trust policy must admit that source principal and satisfy conditions.", "The assumed role's permissions determine what the session can do.", "SCPs and explicit denies can still block a seemingly valid allow.", "Inspect CloudTrail in the account where the denied API request occurred."],
        [
            ex("Source account policy", "intermediate", "The caller can request only the named deployment role.", "json", "{\n  \"Effect\": \"Allow\",\n  \"Action\": \"sts:AssumeRole\",\n  \"Resource\": \"arn:aws:iam::222233334444:role/Deploy\"\n}", runnable=False),
            ex("Destination role trust", "intermediate", "The target role trusts one source role; add an ExternalId condition for a third party.", "json", "{\n  \"Effect\": \"Allow\",\n  \"Principal\": {\"AWS\": \"arn:aws:iam::111122223333:role/ReleaseBot\"},\n  \"Action\": \"sts:AssumeRole\"\n}", runnable=False),
        ],
        ["aws sts get-caller-identity", "aws sts assume-role --role-arn arn:aws:iam::222233334444:role/Deploy --role-session-name release", "aws iam simulate-principal-policy", "aws iam get-role --role-name Deploy", "Review CloudTrail AssumeRole and AccessDenied events in the destination account"],
        ["The role trust policy and source identity policy are different policies in different accounts.", "A successful AssumeRole call does not mean the session has permission to access the final resource.", "A KMS key policy, S3 bucket policy, SCP or explicit Deny may be the final blocker.", "For OIDC, compare issuer, audience and subject claims exactly; repository or branch mismatch is common."],
        [
            qa("advanced", "A source role is allowed to call sts:AssumeRole, but the API returns AccessDenied. What do you check first?", "Confirm the exact source identity with sts:GetCallerIdentity, then compare its role ARN with the destination trust policy Principal and all trust conditions. Also verify the source policy's Resource is the exact destination role ARN and inspect SCPs/explicit denies."),
            qa("advanced", "AssumeRole succeeds, but s3:GetObject still fails. Why?", "The assumed session's permissions may not allow the action, or the bucket policy, KMS key policy, VPC endpoint policy, SCP, boundary or session policy may deny it. Check the failing resource service's CloudTrail event and both identity and resource-side authorization."),
            qa("intermediate", "Why use ExternalId for a third-party role?", "It prevents the confused-deputy problem by requiring the provider to present the customer-specific external identifier in addition to being a trusted principal."),
        ],
        ["iam-roles-sts", "iam-policy-evaluation", "organizations-control-tower", "identity-center"],
        chain(("Source account", "principal + allow", "Authorize the request", "The caller must be allowed to request the exact target role."),
              ("Target account", "trust + conditions", "Admit the principal", "The role trust policy must match the caller and request context."),
              ("Target resource", "session + resource policy", "Authorize the operation", "The assumed role and any resource or organization guardrails decide the final action.")),
    ),
]
SCENARIOS += [
    {"level": "advanced", "topic": "cross-account-iam-troubleshooting", "q": "AssumeRole works from a developer laptop but fails in the CI pipeline. The destination role trusts the source account.", "a": "Trusting the whole account does not remove the source-side permission requirement. Check the actual CI role ARN and its sts:AssumeRole Resource, compare it with the destination trust Principal/conditions, then inspect session tags, external ID, OIDC claims and SCPs. Use CloudTrail in the destination account to see the caller and failed condition."},
    {"level": "advanced", "topic": "cross-account-iam-troubleshooting", "q": "A cross-account deploy role assumes successfully, but the deployment cannot decrypt an artifact with a customer-managed KMS key.", "a": "AssumeRole only establishes the target session. Grant kms:Decrypt to the target role and allow that role in the KMS key policy (or enable IAM policy delegation as designed); then inspect SCPs, key state/region and encryption context conditions."},
]
