export const WORDS = ["PLAYBOOK", "INVENTORY", "IDEMPOTENT", "HANDLER", "VAULT", "TOWER", "ROLE", "FACTS"].map((answer) => ({ answer, term: answer, clue: `Ansible concept: ${answer}` }));
export const RUSH = [{ task: "Reusable Ansible package", answer: "Role", wrong: ["Handler", "Fact", "Inventory"] }, { task: "Ansible secret encryption", answer: "Vault", wrong: ["Tower", "Facts", "Galaxy"] }];
export const BUGS = [];
export const META = { rushLabel: "Ansible Rush", rushIntro: "Choose the automation concept.", rushMono: true, bugLabel: "Playbook Bug Hunt", bugNoun: "finding" };
