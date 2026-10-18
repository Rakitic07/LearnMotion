export const WORDS = ["CHART", "VALUES", "RELEASE", "TEMPLATE", "ROLLBACK", "HOOK", "REPOSITORY", "SCHEMA"].map((answer) => ({ answer, term: answer, clue: `Helm concept: ${answer}` }));
export const RUSH = [{ task: "Packaged Kubernetes application", answer: "Chart", wrong: ["Release", "Namespace", "ReplicaSet"] }, { task: "Per-environment configuration", answer: "Values", wrong: ["Hooks", "History", "Manifest"] }];
export const BUGS = [];
export const META = { rushLabel: "Helm Rush", rushIntro: "Choose the chart concept.", rushMono: true, bugLabel: "Helm Bug Hunt", bugNoun: "finding" };
