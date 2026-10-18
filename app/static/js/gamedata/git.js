export const WORDS = [
  { answer: "COMMIT", term: "Commit", clue: "Snapshot of the project plus author, message and parent pointers" },
  { answer: "BRANCH", term: "Branch", clue: "A movable name that points at a commit" },
  { answer: "HEAD", term: "HEAD", clue: "Pointer to what you have checked out, usually a branch" },
  { answer: "DETACHED", term: "Detached HEAD", clue: "State where HEAD points straight at a commit, not a branch" },
  { answer: "INDEX", term: "Index", clue: "Staging area: what the next commit will contain" },
  { answer: "STAGE", term: "Stage", clue: "git add puts changes here before a commit" },
  { answer: "MERGE", term: "Merge", clue: "Joins histories, possibly with a commit that has two parents" },
  { answer: "FASTFORWARD", term: "Fast-forward", clue: "Merge that just moves the branch pointer, no new commit" },
  { answer: "REBASE", term: "Rebase", clue: "Replays your commits on top of another base, creating new hashes" },
  { answer: "SQUASH", term: "Squash", clue: "Combine several commits into one" },
  { answer: "CHERRYPICK", term: "Cherry-pick", clue: "Copy one commit onto the current branch" },
  { answer: "REVERT", term: "Revert", clue: "New commit that undoes an earlier one without rewriting history" },
  { answer: "RESET", term: "Reset", clue: "Moves the current branch to another commit (soft, mixed or hard)" },
  { answer: "REFLOG", term: "Reflog", clue: "Local diary of where HEAD has been; rescues lost commits" },
  { answer: "STASH", term: "Stash", clue: "Shelves uncommitted changes so you can switch tasks" },
  { answer: "TAG", term: "Tag", clue: "Fixed name for a commit, typically a release like v1.2.0" },
  { answer: "REMOTE", term: "Remote", clue: "Another copy of the repository, such as origin" },
  { answer: "ORIGIN", term: "origin", clue: "Default name of the remote you cloned from" },
  { answer: "FETCH", term: "Fetch", clue: "Downloads new commits but does not change your branches" },
  { answer: "PULL", term: "Pull", clue: "Fetch followed by merge (or rebase)" },
  { answer: "PUSH", term: "Push", clue: "Uploads your commits and moves the remote branch" },
  { answer: "UPSTREAM", term: "Upstream", clue: "The remote branch your local branch tracks" },
  { answer: "CONFLICT", term: "Merge conflict", clue: "Both sides changed the same lines; you decide the result" },
  { answer: "BLOB", term: "Blob", clue: "Object that stores a file's content" },
  { answer: "TREE", term: "Tree", clue: "Object that lists names, modes and hashes: a directory" },
  { answer: "SHA", term: "SHA", clue: "Hash that names every git object" },
  { answer: "BISECT", term: "Bisect", clue: "Binary search through history to find the commit that broke things" },
  { answer: "BLAME", term: "Blame", clue: "Shows which commit last touched each line" },
  { answer: "AMEND", term: "Amend", clue: "Replace the last commit with a fixed one" },
  { answer: "FORK", term: "Fork", clue: "Server-side copy of someone else's repository" },
  { answer: "GITIGNORE", term: ".gitignore", clue: "File listing paths git should not track" },
  { answer: "TRUNK", term: "Trunk-based development", clue: "Everyone integrates small changes into main at least daily" },
  { answer: "WORKTREE", term: "Worktree", clue: "Extra checkout of the same repo in another folder" },
];

export const RUSH = [
  { task: "Create a branch and switch to it", answer: "git switch -c feature", wrong: ["git branch -s feature", "git checkout feature --new", "git new feature"] },
  { task: "Undo the last commit but keep its changes staged", answer: "git reset --soft HEAD~1", wrong: ["git reset --hard HEAD~1", "git revert HEAD --soft", "git undo"] },
  { task: "Undo a pushed commit safely", answer: "git revert <sha>", wrong: ["git reset --hard <sha>^ && git push -f", "git rm <sha>", "git checkout <sha>^"] },
  { task: "Fix the message of the last (unpushed) commit", answer: 'git commit --amend -m "new msg"', wrong: ['git rename HEAD "new msg"', 'git message --edit', 'git rebase --msg "new msg"'] },
  { task: "Bring one commit from main to release", answer: "git cherry-pick <sha>", wrong: ["git merge <sha> --only", "git pull <sha>", "git copy <sha>"] },
  { task: "Shelve uncommitted work temporarily", answer: "git stash", wrong: ["git shelve", "git commit --temp", "git save"] },
  { task: "See where HEAD has been, to recover lost work", answer: "git reflog", wrong: ["git log --lost", "git history", "git fsck --undo"] },
  { task: "Download remote commits without touching your branches", answer: "git fetch", wrong: ["git pull", "git clone", "git sync"] },
  { task: "Rewrite your feature branch on top of the latest main", answer: "git rebase main", wrong: ["git merge --rebase main", "git reset main", "git pull --squash"] },
  { task: "Squash the last 3 commits interactively", answer: "git rebase -i HEAD~3", wrong: ["git squash 3", "git merge --squash HEAD~3", "git commit --squash=3"] },
  { task: "Force push, but refuse if someone else pushed meanwhile", answer: "git push --force-with-lease", wrong: ["git push --force", "git push --safe", "git push -u"] },
  { task: "Find the commit that introduced a bug", answer: "git bisect start / bad / good", wrong: ["git blame --bug", "git log --find-bug", "git grep -bug"] },
  { task: "Who last changed each line of a file?", answer: "git blame file.py", wrong: ["git who file.py", "git log --lines file.py", "git show --author file.py"] },
  { task: "Discard local changes to one file", answer: "git restore file.py", wrong: ["git reset file.py --hard", "git remove file.py", "git clean file.py"] },
  { task: "Unstage a file but keep the edits", answer: "git restore --staged file.py", wrong: ["git rm file.py", "git reset --hard file.py", "git unadd file.py"] },
  { task: "Compact one-line history of all branches", answer: "git log --oneline --graph --all", wrong: ["git history --all", "git show --tree", "git branch --log"] },
  { task: "Merge but always create a merge commit", answer: "git merge --no-ff feature", wrong: ["git merge --ff-only feature", "git merge --squash feature", "git merge -f feature"] },
  { task: "Mark release v1.0 on the current commit", answer: 'git tag -a v1.0 -m "v1.0"', wrong: ["git release v1.0", "git branch v1.0 --tag", "git mark v1.0"] },
];

export const BUGS = [
  {
    symptom: "Teammates' history broke after this cleanup on the shared main branch.",
    lang: "bash",
    code: `git switch main
git pull
git rebase -i HEAD~5
git push --force origin main`,
    bug: [2, 3],
    why: "Rewriting commits that others already pulled forces everyone to repair their clones. On shared branches undo with git revert, and only rebase private branches (push with --force-with-lease).",
  },
  {
    symptom: "The 'oops' commit is still on GitHub even though this was meant to undo it.",
    lang: "bash",
    code: `git log --oneline -1   # a1b2c3d oops (already pushed)
git reset --hard HEAD~1
git pull
git push`,
    bug: [2],
    why: "After resetting, git pull merges the pushed oops commit straight back in. For pushed commits use git revert HEAD and push the new commit.",
  },
  {
    symptom: "The AWS access key from .env is now visible in the repository history.",
    lang: "bash",
    code: `echo "AWS_SECRET_ACCESS_KEY=..." > .env
git add .
git commit -m "add config"
echo ".env" >> .gitignore`,
    bug: [1],
    why: "git add . staged .env before it was ignored, and .gitignore never untracks files. Add ignores first, never commit secrets, and rotate any key that was committed (rewriting history is not enough).",
  },
  {
    symptom: "The feature commits vanished after switching back to main.",
    lang: "bash",
    code: `git checkout a1b2c3d
git commit -m "try new parser"
git commit -m "parser works"
git switch main`,
    bug: [0],
    why: "Checking out a commit detaches HEAD, so the new commits belong to no branch. Use git switch -c parser a1b2c3d, or rescue them with git reflog and git branch parser <sha>.",
  },
  {
    symptom: "Stashed work is gone after the hotfix.",
    lang: "bash",
    code: `git stash
git switch -c hotfix main
git commit -am "fix crash"
git switch feature
git stash drop`,
    bug: [4],
    why: "git stash drop deletes the stash without applying it. Use git stash pop (apply and drop) or git stash apply. A dropped stash can still be found with git fsck --lost-found.",
  },
  {
    symptom: "The release branch now contains half-finished features.",
    lang: "bash",
    code: `git switch release
git merge main
git tag v2.1.1
git push --follow-tags`,
    bug: [1],
    why: "Merging main brings every commit on main into release. For a patch release, cherry-pick only the fix commits onto release.",
  },
];

export const META = {
  rushLabel: "Git Rush",
  rushIntro: "Pick the git command that does the job.",
  rushMono: true,
  bugLabel: "Git Bug Hunt",
  bugNoun: "symptom",
};
