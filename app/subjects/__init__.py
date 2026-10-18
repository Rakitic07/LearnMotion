"""Registry of learning subjects. Kubernetes keeps its original modules; the rest live next to this file."""

from __future__ import annotations

import json
from functools import lru_cache
from importlib import import_module
from pathlib import Path

from ._beginner_guides import BEGINNER_GUIDES

SUBJECTS = [
    {
        "id": "k8s", "name": "Kubernetes", "short": "K8s", "accent": "#326ce5", "accent2": "#46e0c4",
        "tagline": "Pods, scheduling, autoscaling and a real Kind cluster.",
        "headline": ["Kubernetes,", "animated."],
        "blurb": "Every core concept as an animated diagram, with real-life analogies, YAML from basic to advanced, a scheduler simulator that explains <i>why</i> a pod lands where it does, and a real <b>Kind</b> cluster playground with guided labs.",
        "start": "pods",
        "tabs": {"lab": "Scheduler Lab", "playground": "Kind Playground"},
        "cheat": "kubectl cheat sheet", "rush": "kubectl Rush", "art": ["#326ce5", "#46e0c4", "#8f7dff"],
        "blobs": ["Pod", "HPA", "Node", "CM"],
    },
    {
        "id": "db", "name": "Databases", "short": "DB", "accent": "#10b981", "accent2": "#38bdf8",
        "tagline": "SQL, indexes, transactions, isolation and scaling data.",
        "headline": ["Databases,", "demystified."],
        "blurb": "From your first <b>SELECT</b> to MVCC, isolation anomalies, query plans and sharding. Run real SQL against a seeded shop database and watch two transactions race each other.",
        "start": "relational-model",
        "tabs": {"lab": "Isolation Lab", "playground": "SQL Playground"},
        "cheat": "SQL cheat sheet", "rush": "SQL Rush", "art": ["#10b981", "#38bdf8", "#0f766e"],
        "blobs": ["SQL", "ACID", "Index", "MVCC"],
    },
    {
        "id": "sysdesign", "name": "System Design", "short": "SD", "accent": "#f97316", "accent2": "#ec4899",
        "tagline": "Scale, caching, queues, consistency and interview case studies.",
        "headline": ["System design,", "visualised."],
        "blurb": "Load balancers, caches, queues, consistent hashing and CAP, each as a moving diagram. Stress-test an architecture with live traffic and do back-of-the-envelope maths like in a real interview.",
        "start": "scalability",
        "tabs": {"lab": "Architecture Simulator", "playground": "Capacity Estimator"},
        "cheat": "Numbers & rules of thumb", "rush": "Design Rush", "art": ["#f97316", "#ec4899", "#facc15"],
        "blobs": ["Cache", "CAP", "Queue", "LB"],
    },
    {
        "id": "git", "name": "Git", "short": "Git", "accent": "#f05033", "accent2": "#fbbf24",
        "tagline": "Commits, branches, merge vs rebase, undoing and internals.",
        "headline": ["Git,", "untangled."],
        "blurb": "See the commit graph move as you type <b>git</b> commands. Merge, rebase, reset, revert and cherry-pick in a safe simulator, then solve challenges that mirror real team workflows.",
        "start": "three-trees",
        "tabs": {"lab": "Git Challenges", "playground": "Git Sandbox"},
        "cheat": "git cheat sheet", "rush": "Git Rush", "art": ["#f05033", "#fbbf24", "#a855f7"],
        "blobs": ["Commit", "HEAD", "Branch", "SHA"],
    },
    {
        "id": "python", "name": "Python", "short": "Py", "accent": "#3776ab", "accent2": "#ffd43b",
        "tagline": "Objects, functions, generators, async and the GIL.",
        "headline": ["Python,", "step by step."],
        "blurb": "Names and objects, closures, decorators, generators, asyncio and the GIL. Step through real code line by line and watch every variable and stack frame change.",
        "start": "objects-mutability",
        "tabs": {"lab": "Code Visualizer", "playground": "Python Runner"},
        "cheat": "Python cheat sheet", "rush": "Python Rush", "art": ["#3776ab", "#ffd43b", "#22d3ee"],
        "blobs": ["async", "GIL", "yield", "def"],
    },
    {
        "id": "aws", "name": "AWS", "short": "AWS", "accent": "#ff9900", "accent2": "#a78bfa",
        "tagline": "IAM, VPC, compute, storage, serverless and architecture.",
        "headline": ["AWS,", "without the bill."],
        "blurb": "Regions, IAM, VPCs, EC2, S3, Lambda and friends, explained with flows. Evaluate IAM policies like AWS does and debug VPC reachability without spending a cent.",
        "start": "global-infra",
        "tabs": {"lab": "IAM Policy Evaluator", "playground": "VPC Reachability"},
        "cheat": "AWS CLI cheat sheet", "rush": "AWS Rush", "art": ["#ff9900", "#a78bfa", "#232f3e"],
        "blobs": ["Lambda", "IAM", "EC2", "S3"],
    },
    {
        "id": "linux", "name": "Linux", "short": "Linux", "accent": "#e8a800", "accent2": "#38bdf8",
        "tagline": "Files, permissions, pipes, processes, systemd and the kernel.",
        "headline": ["Linux,", "from the shell up."],
        "blurb": "The filesystem, permissions, pipes, text tools, processes, systemd, networking and what containers really are. Practise in a simulated <b>shell</b> with real files, users and services, and solve hands-on challenges.",
        "start": "filesystem",
        "tabs": {"lab": "Shell Challenges", "playground": "Shell Sandbox"},
        "cheat": "Linux cheat sheet", "rush": "Shell Rush", "art": ["#fcc624", "#263238", "#38bdf8"],
        "blobs": ["bash", "PID", "chmod", "rwx"],
    },
    {
        "id": "java", "name": "Java", "short": "Java", "accent": "#e76f00", "accent2": "#5382a1",
        "tagline": "JVM, collections, streams, records, virtual threads and GC.",
        "headline": ["Java,", "from 8 to 25."],
        "blurb": "From the JVM and collections to records, pattern matching, virtual threads and garbage collectors. Compare the same code across <b>Java 8, 11, 14, 17, 18, 21 and 25</b> side by side, and check the minimum version any snippet needs.",
        "start": "jvm-basics",
        "tabs": {"lab": "Version Explorer", "playground": "Version Checker"},
        "cheat": "Java cheat sheet", "rush": "Java Rush", "art": ["#e76f00", "#5382a1", "#f8b26a"],
        "blobs": ["JVM", "GC", "Stream", "var"],
    },
    {
        "id": "cicd", "name": "CI/CD", "short": "CI/CD", "accent": "#2088ff", "accent2": "#22c55e",
        "tagline": "Pipelines, tests, artifacts, deployments and safe rollbacks.",
        "headline": ["CI/CD,", "shipped safely."],
        "blurb": "From the first commit hook to blue-green and canary releases. Watch a <b>pipeline</b> run stage by stage, break it with flaky tests and slow builds, then fix it with caching, parallelism and automatic rollbacks.",
        "start": "ci-basics",
        "tabs": {"lab": "Pipeline Simulator", "playground": "Pipeline Builder"},
        "cheat": "CI/CD cheat sheet", "rush": "Pipeline Rush", "art": ["#2088ff", "#22c55e", "#a78bfa"],
        "blobs": ["Build", "Test", "Ship", "CD"],
    },
    {
        "id": "dsa", "name": "DSA", "short": "DSA", "accent": "#a855f7", "accent2": "#22d3ee",
        "tagline": "Big-O, data structures, sorting, graphs, DP and interview patterns.",
        "headline": ["Algorithms,", "in motion."],
        "blurb": "Arrays to graphs, every classic <b>sorting</b> algorithm, recursion, dynamic programming and the patterns interviewers love. Watch sorts race bar by bar and run your own solutions in Python.",
        "start": "big-o",
        "tabs": {"lab": "Sorting Visualizer", "playground": "Algorithm Runner"},
        "cheat": "Big-O cheat sheet", "rush": "Big-O Rush", "art": ["#a855f7", "#22d3ee", "#f472b6"],
        "blobs": ["O(n)", "Heap", "Sort", "DP"],
    },
    {
        "id": "qa", "name": "QA & Testing", "short": "QA", "accent": "#14b8a6", "accent2": "#f43f5e",
        "tagline": "Test design, automation, the test pyramid, flaky tests and quality.",
        "headline": ["Quality,", "by design."],
        "blurb": "Unit, integration and end-to-end tests, test design techniques, mocks, flaky tests and quality metrics. Pick test inputs and watch <b>branch coverage</b> and mutation score change, then run real unittest suites.",
        "start": "qa-basics",
        "tabs": {"lab": "Coverage Lab", "playground": "Test Runner"},
        "cheat": "Testing cheat sheet", "rush": "QA Rush", "art": ["#14b8a6", "#f43f5e", "#facc15"],
        "blobs": ["Test", "Mock", "Bug", "E2E"],
    },
    {
        "id": "ds", "name": "Data Science", "short": "DS", "accent": "#f59e0b", "accent2": "#3b82f6",
        "tagline": "Statistics, data wrangling, visualisation and experiments.",
        "headline": ["Data science,", "made visible."],
        "blurb": "Descriptive stats, distributions, hypothesis tests, A/B experiments, cleaning and feature engineering. Drag points to see <b>mean, median and correlation</b> move, and analyse data in a Python notebook.",
        "start": "ds-workflow",
        "tabs": {"lab": "Stats Explorer", "playground": "Data Notebook"},
        "cheat": "Stats cheat sheet", "rush": "Stats Rush", "art": ["#f59e0b", "#3b82f6", "#10b981"],
        "blobs": ["Mean", "p<.05", "SQL", "Plot"],
    },
    {
        "id": "ml", "name": "ML & AI", "short": "AI", "accent": "#ec4899", "accent2": "#8b5cf6",
        "tagline": "Models, training, LLMs, RAG, agents, AGENTS.md and skills.",
        "headline": ["ML & AI,", "neurons to agents."],
        "blurb": "Regression to transformers, training and evaluation, LLMs, prompting, RAG, tool calling and <b>AI agents</b>, including how to write AGENTS.md and SKILL.md files. Train a model live and lint your own agent instructions.",
        "start": "ml-basics",
        "tabs": {"lab": "Training Lab", "playground": "Agent Builder"},
        "cheat": "ML & AI cheat sheet", "rush": "AI Rush", "art": ["#ec4899", "#8b5cf6", "#22d3ee"],
        "blobs": ["LLM", "Loss", "RAG", "MCP"],
    },
    {
        "id": "security", "name": "Security", "short": "Sec", "accent": "#fb7185", "accent2": "#fbbf24",
        "tagline": "Identity, application security, cloud controls and incident response.",
        "headline": ["Security,", "built in."],
        "blurb": "Learn threat modeling, authentication, authorization, secure coding, cloud identity and incident response. Use the IAM troubleshooting simulator to trace cross-account access failures one policy layer at a time.",
        "start": "threat-modeling",
        "tabs": {"lab": "Security Lab", "playground": "IAM Policy Builder"},
        "cheat": "Security review checklist", "rush": "Security Rush", "art": ["#fb7185", "#fbbf24", "#a78bfa"],
        "blobs": ["Threat", "IAM", "TLS", "Least privilege"],
    },
    {
        "id": "networking", "name": "Networking", "short": "Net", "accent": "#38bdf8", "accent2": "#34d399",
        "tagline": "IP addressing, CIDR math, routing, DNS, protocols and cloud networks.",
        "headline": ["Networking,", "made calculable."],
        "blurb": "Build intuition for IPv4 and IPv6, masks, prefixes such as /24, /32 and /64, subnet ranges, routing, DNS, TCP, TLS, NAT and cloud networking. Calculate the ranges yourself in the interactive CIDR simulator.",
        "start": "ip-addressing",
        "tabs": {"lab": "Packet Path Lab", "playground": "CIDR Calculator"},
        "cheat": "Networking cheat sheet", "rush": "Networking Rush", "art": ["#38bdf8", "#34d399", "#8b5cf6"],
        "blobs": ["/24", "DNS", "Route", "TLS"],
    },
    {
        "id": "go", "name": "Go", "short": "Go", "accent": "#00add8", "accent2": "#7dd3fc",
        "tagline": "Go syntax, interfaces, concurrency, testing and production services.",
        "headline": ["Go,", "from zero to service."],
        "blurb": "Learn Go's type system, modules, errors, interfaces, generics, goroutines, channels, context, testing and profiling by building small production-shaped programs.",
        "start": "go-toolchain",
        "tabs": {"lab": "Go Code Lab", "playground": "Go Practice Bench"},
        "cheat": "Go cheat sheet", "rush": "Go Rush", "art": ["#00add8", "#7dd3fc", "#007d9c"],
        "blobs": ["go", "chan", "err", "ctx"],
    },
    {
        "id": "kafka", "name": "Kafka", "short": "Kafka", "accent": "#f59e0b", "accent2": "#fb7185",
        "tagline": "Topics, partitions, consumer groups, delivery guarantees and operations.",
        "headline": ["Kafka,", "event by event."],
        "blurb": "Understand the distributed log, choose partition keys, reason about offsets and rebalances, and design producers and consumers that handle retries, duplicates and schema changes safely.",
        "start": "kafka-log-model",
        "tabs": {"lab": "Kafka Flow Simulator", "playground": "Kafka Config Builder"},
        "cheat": "Kafka operations guide", "rush": "Kafka Rush", "art": ["#f59e0b", "#fb7185", "#334155"],
        "blobs": ["Topic", "Offset", "ISR", "Group"],
    },
    {
        "id": "azure", "name": "Azure", "short": "Azure", "accent": "#0089d6", "accent2": "#38bdf8",
        "tagline": "Azure identity, networking, compute, data, governance and operations.",
        "headline": ["Azure,", "by architecture."],
        "blurb": "Learn Entra ID and RBAC, subscriptions and governance, VNets, private endpoints, compute, AKS, storage, databases, Key Vault and observability with practical decision paths.",
        "start": "azure-resource-hierarchy",
        "tabs": {"lab": "Azure Architecture Lab", "playground": "Azure DevOps Pipeline Builder"},
        "cheat": "Azure services guide", "rush": "Azure Rush", "art": ["#0089d6", "#38bdf8", "#7c3aed"],
        "blobs": ["Entra", "VNet", "AKS", "RBAC"],
    },
    {
        "id": "gcp", "name": "Google Cloud", "short": "GCP", "accent": "#4285f4", "accent2": "#34a853",
        "tagline": "GCP identity, networking, compute, data and operations.",
        "headline": ["Google Cloud,", "by service boundary."],
        "blurb": "Learn organizations and projects, IAM, VPC networking, Compute Engine, GKE, Cloud Run, Cloud Storage, BigQuery, Pub/Sub, Cloud Logging and cost controls with practical troubleshooting paths.",
        "start": "gcp-resource-hierarchy",
        "tabs": {"lab": "GCP Architecture Lab", "playground": "GCP Config Builder"},
        "cheat": "GCP services guide", "rush": "GCP Rush", "art": ["#4285f4", "#34a853", "#fbbc05"],
        "blobs": ["IAM", "VPC", "GKE", "BQ"],
    },
    {
        "id": "nodejs", "name": "Node.js", "short": "Node", "accent": "#68a063", "accent2": "#f0db4f",
        "tagline": "Node.js runtime, async I/O, APIs, packages, testing and operations.",
        "headline": ["Node.js,", "from event loop to API."],
        "blurb": "Understand the event loop, promises, streams, modules, package supply chain and production HTTP services. Practise backpressure, cancellation, tests, profiling and safe deployment.",
        "start": "node-runtime",
        "tabs": {"lab": "Node.js Code Lab", "playground": "Node.js Service Builder"},
        "cheat": "Node.js runtime guide", "rush": "Node.js Rush", "art": ["#68a063", "#f0db4f", "#3c873a"],
        "blobs": ["async", "stream", "npm", "event loop"],
    },
    {
        "id": "observability", "name": "Observability & Monitoring", "short": "Obs", "accent": "#f97316", "accent2": "#38bdf8",
        "tagline": "Prometheus, Grafana, ELK, Logstash, Kibana, Jaeger and OpenTelemetry.",
        "headline": ["Observability & Monitoring", "from signal to answer."],
        "blurb": "Write PromQL queries and alert rules, build Grafana dashboards, parse and route logs with Logstash, search them with Kibana KQL, and trace requests with Jaeger and OpenTelemetry.",
        "start": "obs-signals",
        "tabs": {"lab": "Telemetry Triage Lab", "playground": "Query & Rule Builder"},
        "cheat": "Observability query guide", "rush": "Observability Rush", "art": ["#f97316", "#38bdf8", "#8b5cf6"],
        "blobs": ["p95", "trace", "logs", "SLO"],
    },
    {
        "id": "ansible", "name": "Ansible", "short": "Ansible", "accent": "#ee0000", "accent2": "#7dd3fc",
        "tagline": "Playbooks, inventories, roles, safe automation and Ansible Tower/AWX.",
        "headline": ["Ansible,", "repeatable by design."],
        "blurb": "Write readable YAML playbooks, build reusable roles, manage secrets and inventory, test idempotence, and run governed automation through Ansible Tower / Automation Controller and AWX.",
        "start": "ansible-inventory",
        "tabs": {"lab": "Playbook Run Lab", "playground": "Playbook Builder"},
        "cheat": "Ansible operations guide", "rush": "Ansible Rush", "art": ["#ee0000", "#7dd3fc", "#232f3e"],
        "blobs": ["YAML", "Role", "Facts", "Tower"],
    },
    {
        "id": "artifactory", "name": "Artifactory", "short": "Repo", "accent": "#41bf47", "accent2": "#f59e0b",
        "tagline": "JFrog Artifactory, Nexus, package formats and artifact supply chains.",
        "headline": ["Artifacts,", "promoted with trust."],
        "blurb": "Manage Maven, npm, PyPI, Docker and generic artifacts with repositories, permissions, immutable versions, retention, build metadata and promotion workflows across JFrog Artifactory and Sonatype Nexus.",
        "start": "artifact-repository-model",
        "tabs": {"lab": "Repository Flow Lab", "playground": "Repository Policy Builder"},
        "cheat": "Artifact repository guide", "rush": "Artifact Rush", "art": ["#41bf47", "#f59e0b", "#38bdf8"],
        "blobs": ["OCI", "Maven", "digest", "SBOM"],
    },
    {
        "id": "terraform", "name": "Terraform", "short": "TF", "accent": "#7b42bc", "accent2": "#38bdf8",
        "tagline": "HCL, state, modules, plans, providers and safe infrastructure delivery.",
        "headline": ["Terraform,", "planned carefully."],
        "blurb": "Write HCL, understand providers and dependency graphs, manage remote state and locking, build reusable modules, review plans, and deliver infrastructure through secure CI workflows.",
        "start": "terraform-resource-model",
        "tabs": {"lab": "Plan Review Lab", "playground": "HCL Builder"},
        "cheat": "Terraform command guide", "rush": "Terraform Rush", "art": ["#7b42bc", "#38bdf8", "#f59e0b"],
        "blobs": ["HCL", "Plan", "State", "Module"],
    },
    {
        "id": "helm", "name": "Helm Charts", "short": "Helm", "accent": "#0f1689", "accent2": "#38bdf8",
        "tagline": "Chart structure, templates, values, releases, testing and safe upgrades.",
        "headline": ["Helm charts,", "packaged clearly."],
        "blurb": "Build and lint charts, write maintainable Go templates and schemas, manage values per environment, handle dependencies and secrets, and test, upgrade or roll back releases safely.",
        "start": "helm-chart-structure",
        "tabs": {"lab": "Chart Render Lab", "playground": "Chart Values Builder"},
        "cheat": "Helm command guide", "rush": "Helm Rush", "art": ["#0f1689", "#38bdf8", "#f59e0b"],
        "blobs": ["Chart", "Values", "Release", "OCI"],
    },
    {
        "id": "argocd", "name": "Argo CD", "short": "Argo CD", "accent": "#ef7b4d", "accent2": "#38bdf8",
        "tagline": "GitOps applications, sync, health, drift, RBAC and multi-cluster delivery.",
        "headline": ["Argo CD,", "Git as desired state."],
        "blurb": "Model Applications and ApplicationSets, diagnose OutOfSync and degraded states, tune sync waves and health checks, secure projects and RBAC, and deliver Helm or Kustomize sources across clusters.",
        "start": "argocd-gitops-model",
        "tabs": {"lab": "GitOps Reconcile Lab", "playground": "Application Builder"},
        "cheat": "Argo CD command guide", "rush": "Argo CD Rush", "art": ["#ef7b4d", "#38bdf8", "#8b5cf6"],
        "blobs": ["Git", "Sync", "Drift", "AppSet"],
    },
    {
        "id": "guitar", "domain": "Music & Instruments", "name": "Guitar", "short": "Guitar", "accent": "#e87935", "accent2": "#f3c969",
        "tagline": "Guitar setup, chords, rhythm, technique and songs from first notes onward.",
        "headline": ["Guitar,", "one chord at a time."],
        "blurb": "Learn how the instrument works, tune it, read tabs, build chords, develop rhythm and technique, and bring each skill into songs and performance.",
        "start": "guitar-01", "tabs": {"lab": "Guitar Practice Room", "playground": "Listening Room"},
        "cheat": "Guitar reference", "rush": "Guitar Rush", "art": ["#e87935", "#f3c969", "#8fbc8f"], "blobs": ["E A D", "Chord", "Riff", "♪"],
    },
    {
        "id": "theory", "domain": "Music & Instruments", "name": "Music Theory", "short": "Theory", "accent": "#8b5cf6", "accent2": "#38bdf8",
        "tagline": "Pitch, rhythm, scales, harmony, form and how to listen for them.",
        "headline": ["Music theory,", "heard and understood."],
        "blurb": "Build a practical map of sound: read rhythm, name intervals, understand keys and chords, follow musical form, and connect the terms to what you hear.",
        "start": "theory-01", "tabs": {"lab": "Ear & Theory Lab", "playground": "Listening Room"},
        "cheat": "Theory reference", "rush": "Theory Rush", "art": ["#8b5cf6", "#38bdf8", "#f472b6"], "blobs": ["C D E", "I–V–vi", "♩", "♬"],
    },
    {
        "id": "drums", "domain": "Music & Instruments", "name": "Drums", "short": "Drums", "accent": "#ef4444", "accent2": "#f59e0b",
        "tagline": "Build time, coordination, grooves, fills and ensemble awareness.",
        "headline": ["Drums,", "feel the pulse."],
        "blurb": "Set up safely, develop relaxed technique, read rhythms, coordinate all four limbs, build grooves and play with a band or backing track.",
        "start": "drums-01", "tabs": {"lab": "Drum Practice Room", "playground": "Groove Room"},
        "cheat": "Drum reference", "rush": "Drum Rush", "art": ["#ef4444", "#f59e0b", "#8b5cf6"], "blobs": ["Kick", "Snare", "Hi-hat", "♩"],
    },
    {
        "id": "violin", "domain": "Music & Instruments", "name": "Violin", "short": "Violin", "accent": "#dc5572", "accent2": "#f3bd54",
        "tagline": "Healthy setup, bow control, intonation, reading and expressive playing.",
        "headline": ["Violin,", "from open strings to songs."],
        "blurb": "Set up comfortably, make a clear sound with the bow, find notes in tune, read music, develop technique and prepare pieces for playing with others.",
        "start": "violin-01", "tabs": {"lab": "Violin Practice Room", "playground": "Listening Room"},
        "cheat": "Violin reference", "rush": "Violin Rush", "art": ["#dc5572", "#f3bd54", "#8fbc8f"], "blobs": ["G D A E", "Bow", "Tune", "♪"],
    },
    {
        "id": "piano", "domain": "Music & Instruments", "name": "Piano", "short": "Piano", "accent": "#3979d6", "accent2": "#53c5ad",
        "tagline": "Read the keyboard, coordinate both hands and make harmony come alive.",
        "headline": ["Piano,", "keys to music."],
        "blurb": "Find your way around the keyboard, read both staves, build scales and chords, coordinate hands, shape phrases and learn repertoire with confidence.",
        "start": "piano-01", "tabs": {"lab": "Keyboard Practice Room", "playground": "Listening Room"},
        "cheat": "Piano reference", "rush": "Piano Rush", "art": ["#3979d6", "#53c5ad", "#e9c65a"], "blobs": ["C D E", "Chord", "Scale", "♬"],
    },
    {
        "id": "voice", "domain": "Music & Instruments", "name": "Singing & Voice", "short": "Voice", "accent": "#d946ef", "accent2": "#38bdf8",
        "tagline": "Healthy vocal technique, registers, pitch, reading and expression.",
        "headline": ["Singing & voice,", "with healthy technique."],
        "blurb": "Learn how the voice works, compare chest and head voice, build pitch and breath coordination, read vocal melodies and practise expression without forcing your sound.",
        "start": "voice-01", "tabs": {"lab": "Vocal Practice Room", "playground": "Voice Listening Room"},
        "cheat": "Vocal practice guide", "rush": "Voice Rush", "art": ["#d946ef", "#38bdf8", "#f472b6"], "blobs": ["Breath", "Pitch", "Register", "♪"],
    },
    {
        "id": "react", "name": "React", "short": "React", "accent": "#61dafb", "accent2": "#3178c6",
        "tagline": "Components, JSX, state, effects, forms and production patterns.",
        "headline": ["React,", "one component at a time."],
        "blurb": "Learn component composition, props, JSX, state, effects, forms, routing, accessibility, testing and performance through focused examples and an interactive component builder.",
        "start": "react-ui-model", "tabs": {"lab": "React Foundations Lab", "playground": "Component Builder"},
        "cheat": "React reference", "rush": "React Rush", "art": ["#61dafb", "#3178c6", "#a78bfa"], "blobs": ["JSX", "Props", "State", "Hooks"],
    },
    {
        "id": "sonarqube", "name": "SonarQube", "short": "SonarQube", "accent": "#4b9fd5", "accent2": "#4cc38a",
        "tagline": "Static analysis, quality profiles, gates, issues and CI integration.",
        "headline": ["SonarQube,", "quality made actionable."],
        "blurb": "Understand code analysis, rules, quality profiles, issues, quality gates, coverage, pull-request decoration and safe CI integration with practical builder exercises.",
        "start": "sonar-intro", "tabs": {"lab": "Quality Gate Lab", "playground": "Rule & Gate Builder"},
        "cheat": "SonarQube reference", "rush": "Quality Gate Rush", "art": ["#4b9fd5", "#4cc38a", "#e9c65a"], "blobs": ["Rules", "Gate", "Issues", "CI"],
    },
    {
        "id": "css", "name": "CSS", "short": "CSS", "accent": "#7c5cff", "accent2": "#38bdf8",
        "tagline": "Selectors, layouts, responsive design, visual systems and accessible UI.",
        "headline": ["CSS,", "style with intent."],
        "blurb": "Learn the cascade, selectors, Flexbox, Grid, responsive design, design tokens, effects and accessible states. Preview claymorphism, neumorphism and glassmorphism live.",
        "start": "css-intro", "tabs": {"lab": "CSS Foundations Lab", "playground": "Live Style Studio"},
        "cheat": "CSS reference", "rush": "CSS Rush", "art": ["#7c5cff", "#38bdf8", "#f472b6"], "blobs": ["Grid", "Tokens", "Flex", "CSS"],
    },
    {
        "id": "nginx", "name": "NGINX", "short": "NGINX", "accent": "#009639", "accent2": "#38bdf8",
        "tagline": "HTTP request flow, reverse proxies, load balancing, TLS and operations.",
        "headline": ["NGINX,", "from request to response."],
        "blurb": "Learn how NGINX parses configuration, serves static files, proxies applications, balances upstreams, terminates TLS and exposes useful operational signals.",
        "start": "nginx-01", "tabs": {"lab": "Config Lab", "playground": "Request Flow Lab"},
        "cheat": "NGINX reference", "rush": "NGINX Rush", "art": ["#009639", "#38bdf8", "#a78bfa"], "blobs": ["server", "proxy", "TLS", "upstream"],
    },
    {
        "id": "javascript", "name": "JavaScript", "short": "JS", "accent": "#f7df1e", "accent2": "#38bdf8",
        "tagline": "Modern JavaScript, browser APIs, asynchronous code and production tooling.",
        "headline": ["JavaScript,", "from values to the event loop."],
        "blurb": "Build a sturdy foundation in values, functions, objects, modules, promises, browser events, accessibility, testing and performance with runnable examples.",
        "start": "javascript-01", "tabs": {"lab": "JavaScript Foundations Lab", "playground": "JavaScript Playground"},
        "cheat": "JavaScript reference", "rush": "JavaScript Rush", "art": ["#f7df1e", "#111827", "#38bdf8"], "blobs": ["const", "Promise", "DOM", "ESM"],
    },
]

for _subject in SUBJECTS:
    _subject.setdefault("domain", "Technology & Engineering")
    _subject["beginner"] = BEGINNER_GUIDES.get(_subject["id"], {
        "what": f"{_subject['name']} is a technology used to build and operate software systems.",
        "why": f"Learning {_subject['name']} helps you understand how software is built, delivered and maintained.",
        "example": f"Start with a small {_subject['name']} example, inspect how each part works, and change one thing at a time.",
        "start": "Begin with the basic building blocks, then practise small examples before combining them into larger workflows.",
    })

_BY_ID = {s["id"]: s for s in SUBJECTS}


def subject(subject_id: str) -> dict | None:
    return _BY_ID.get(subject_id)


@lru_cache(maxsize=None)
def module(subject_id: str):
    if subject_id == "k8s":
        return import_module("app.topics")
    return import_module(f"app.subjects.{subject_id}")


def content(subject_id: str) -> dict:
    mod = module(subject_id)
    return {"subject": _BY_ID[subject_id], "categories": mod.CATEGORIES, "topics": mod.TOPICS, "scenarios": mod.SCENARIOS}


def _build_summaries() -> list[dict]:
    out = []
    for s in SUBJECTS:
        mod = module(s["id"])
        questions = sum(len(t["interview"]) for t in mod.TOPICS) + len(mod.SCENARIOS)
        out.append({**s, "topics": len(mod.TOPICS), "questions": questions,
                    "levels": sorted({t["level"] for t in mod.TOPICS}, key=["basic", "intermediate", "advanced"].index)})
    return out


@lru_cache(maxsize=1)
def summaries() -> list[dict]:
    """Return build-generated subject counts without importing every lesson at runtime."""
    manifest = Path(__file__).with_name("_summary_manifest.json")
    try:
        return json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        # Keep development usable if the generated manifest was removed.
        return _build_summaries()


def search_index() -> list[dict]:
    """One compact row per topic across all subjects, for the global search palette."""
    rows = []
    for s in SUBJECTS:
        mod = module(s["id"])
        cats = {c["id"]: c["title"] for c in mod.CATEGORIES}
        for t in mod.TOPICS:
            examples = t.get("examples", [])
            example_terms = [f"{e.get('title', '')} {e.get('description', '')}" for e in examples if isinstance(e, dict)]
            interview_terms = [f"{q.get('q', '')} {q.get('a', '')[:180]}" for q in t.get("interview", [])]
            terms = " ".join([
                t.get("what", "")[:520], t.get("analogy", "")[:180],
                *t.get("use_cases", [])[:3], *t.get("key_points", [])[:7],
                *t.get("commands", [])[:4], *example_terms[:4], *interview_terms[:4],
            ])
            rows.append({"sid": s["id"], "subject": s["name"], "id": t["id"], "title": t["title"], "tagline": t.get("tagline", ""),
                         "category": cats.get(t["category"], t["category"]), "level": t["level"], "terms": terms[:1800]})
    return rows
