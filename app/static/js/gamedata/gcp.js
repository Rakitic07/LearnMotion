export const WORDS = [
  { answer: "PROJECT", term: "Project", clue: "Google Cloud resource, billing and API boundary" },
  { answer: "FOLDER", term: "Folder", clue: "Groups projects under an organization" },
  { answer: "VPC", term: "VPC", clue: "Global Google Cloud virtual network" },
  { answer: "SUBNET", term: "Subnet", clue: "Regional IP range inside a VPC" },
  { answer: "BIGQUERY", term: "BigQuery", clue: "Serverless analytics warehouse" },
  { answer: "PUBSUB", term: "Pub/Sub", clue: "Managed publish/subscribe messaging service" },
  { answer: "GKE", term: "GKE", clue: "Google Kubernetes Engine" },
  { answer: "IAM", term: "IAM", clue: "Identity and access management" },
  { answer: "BUCKET", term: "Bucket", clue: "Cloud Storage object namespace container" },
  { answer: "WORKLOAD", term: "Workload", clue: "Application using a service identity" },
];
export const RUSH = [{ task: "GCP VPC scope", answer: "Global", wrong: ["Regional", "Zonal", "Project-local"] }, { task: "GCP subnet scope", answer: "Regional", wrong: ["Global", "Zonal", "Organization-wide"] }];
export const BUGS = [];
export const META = { rushLabel: "GCP Rush", rushIntro: "Pick the Google Cloud concept.", rushMono: false, bugLabel: "GCP Bug Hunt", bugNoun: "finding" };
