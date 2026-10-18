export const WORDS = ["PROVIDER", "RESOURCE", "STATE", "BACKEND", "MODULE", "PLAN", "DRIFT", "LOCKING"].map((answer) => ({ answer, term: answer, clue: `Terraform concept: ${answer}` }));
export const RUSH = [{ task: "Review proposed infrastructure changes", answer: "Plan", wrong: ["Apply", "Import", "Destroy"] }, { task: "Prevent concurrent state writes", answer: "Locking", wrong: ["Refresh", "Output", "Workspace"] }];
export const BUGS = [];
export const META = { rushLabel: "Terraform Rush", rushIntro: "Choose the infrastructure-as-code concept.", rushMono: true, bugLabel: "Terraform Bug Hunt", bugNoun: "finding" };
