export const WORDS = ["GITOPS", "APPLICATION", "APPSET", "OUTOFSYNC", "RECONCILE", "PROJECT", "PRUNE", "HEALTH"].map((answer) => ({ answer, term: answer, clue: `Argo CD concept: ${answer}` }));
export const RUSH = [{ task: "GitOps desired state", answer: "Git", wrong: ["Live cluster", "Image tag", "Dashboard"] }, { task: "Generated multi-app controller", answer: "ApplicationSet", wrong: ["HelmRelease", "ReplicaSet", "ConfigMap"] }];
export const BUGS = [];
export const META = { rushLabel: "Argo CD Rush", rushIntro: "Choose the GitOps concept.", rushMono: true, bugLabel: "GitOps Bug Hunt", bugNoun: "finding" };
