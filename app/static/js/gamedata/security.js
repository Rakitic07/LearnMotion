export const WORDS = [
  { answer: "THREAT", term: "Threat", clue: "A potential cause of harm to an asset" },
  { answer: "IAM", term: "IAM", clue: "Identity and access management" },
  { answer: "LEASTPRIVILEGE", term: "Least privilege", clue: "Give only the permissions needed" },
  { answer: "MFA", term: "MFA", clue: "Authentication using more than one factor" },
  { answer: "OIDC", term: "OIDC", clue: "Federated identity layer over OAuth 2" },
  { answer: "ENCRYPTION", term: "Encryption", clue: "Protects data confidentiality with keys" },
  { answer: "AUDIT", term: "Audit", clue: "Recorded evidence of who did what" },
  { answer: "SECRET", term: "Secret", clue: "Credential or key that needs controlled access" },
  { answer: "FIREWALL", term: "Firewall", clue: "Filters traffic at a network boundary" },
  { answer: "INJECTION", term: "Injection", clue: "Untrusted input changes a command or query" },
  { answer: "CIPHER", term: "Cipher", clue: "Algorithm used to encrypt and decrypt data" },
  { answer: "PHISHING", term: "Phishing", clue: "Fraudulent message that tricks a recipient" },
];
export const RUSH = [
  { task: "Who may assume a role?", answer: "Trust policy", wrong: ["Permissions policy", "SCP only", "Security group"] },
  { task: "What does an explicit deny do?", answer: "Overrides an allow", wrong: ["Adds permissions", "Applies only to users", "Is ignored by roles"] },
  { task: "Preferred CI cloud credential", answer: "Short-lived OIDC role", wrong: ["Root access key", "Shared user key", "Key in source code"] },
];
export const BUGS = [];
export const META = { rushLabel: "Security Rush", rushIntro: "Choose the control that fits the risk.", rushMono: false, bugLabel: "Threat Hunt", bugNoun: "finding" };
