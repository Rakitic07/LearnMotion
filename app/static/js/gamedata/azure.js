export const WORDS = [
  { answer: "TENANT", term: "Tenant", clue: "Microsoft Entra identity directory boundary" },
  { answer: "SUBSCRIPTION", term: "Subscription", clue: "Azure resource management and billing scope" },
  { answer: "RBAC", term: "RBAC", clue: "Role-based authorization assignments" },
  { answer: "VNET", term: "VNet", clue: "Private virtual network in Azure" },
  { answer: "AKS", term: "AKS", clue: "Managed Kubernetes service on Azure" },
  { answer: "KEYVAULT", term: "Key Vault", clue: "Stores keys, secrets and certificates" },
  { answer: "PRIVATEENDPOINT", term: "Private endpoint", clue: "Private IP path to a supported Azure service" },
  { answer: "POLICY", term: "Policy", clue: "Governance guardrail that can audit or deny" },
  { answer: "IDENTITY", term: "Identity", clue: "Principal used to authenticate a workload or person" },
  { answer: "MONITOR", term: "Monitor", clue: "Azure service for metrics, logs and alerts" },
];
export const RUSH = [
  { task: "Azure workload without a stored secret", answer: "Managed identity", wrong: ["Shared key", "Root certificate", "Public IP"] },
  { task: "Authorization assignment parts", answer: "Principal, role, scope", wrong: ["VNet, subnet, route", "Tenant, DNS, port", "Policy, metric, tag"] },
  { task: "Azure policy deny bypassed by Contributor?", answer: "No", wrong: ["Always", "Only in production", "Only with a tag"] },
];
export const BUGS = [];
export const META = { rushLabel: "Azure Rush", rushIntro: "Choose the Azure control or service.", rushMono: false, bugLabel: "Azure Bug Hunt", bugNoun: "finding" };
