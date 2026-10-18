export const WORDS = ["ARTIFACT", "DIGEST", "PROVENANCE", "SBOM", "REPOSITORY", "PROMOTION", "NEXUS", "IMMUTABLE"].map((answer) => ({ answer, term: answer, clue: `Artifact supply-chain concept: ${answer}` }));
export const RUSH = [{ task: "Immutable container identifier", answer: "Digest", wrong: ["Latest", "Branch", "Workspace"] }, { task: "Component inventory format", answer: "SBOM", wrong: ["RBAC", "OCI", "HCL"] }];
export const BUGS = [];
export const META = { rushLabel: "Artifact Rush", rushIntro: "Choose the repository concept.", rushMono: true, bugLabel: "Artifact Bug Hunt", bugNoun: "finding" };
