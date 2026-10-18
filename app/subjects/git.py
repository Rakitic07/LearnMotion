"""Git: from the three trees to internals. Runnable bash examples use only commands the in-browser simulator supports."""

from ._dsl import ex, flow, node, pkt, qa, step

CATEGORIES = [
    {"id": "basics", "title": "Basics", "color": "sky", "blurb": "Snapshots, staging and history."},
    {"id": "branching", "title": "Branching", "color": "mint", "blurb": "Branches, merges and rebases."},
    {"id": "fixing", "title": "Fixing Mistakes", "color": "rose", "blurb": "Undo safely, find bugs."},
    {"id": "collab", "title": "Collaboration", "color": "lemon", "blurb": "Remotes and team workflows."},
    {"id": "internals", "title": "Internals", "color": "lilac", "blurb": "Objects, refs and the DAG."},
]

_C = lambda id, label, x, y, tint="sky", sub="", hidden=False: node(id, label, x, y, tint, sub, "round", hidden)
_R = lambda id, label, x, y, tint="lemon", hidden=False: node(id, label, x, y, tint, "", "pill", hidden)

TOPICS = [
    {
        "id": "three-trees", "title": "Working Tree, Index & Commits", "category": "basics", "level": "basic", "code": "3T",
        "tagline": "Edit, stage, commit: the three places your changes live.",
        "analogy": "Packing for a trip: clothes on the bed (working tree), clothes in the suitcase (staging area), and the photo you take of the closed suitcase (commit).",
        "what": "Git tracks snapshots, not diffs. Your working tree is the files on disk. The index (staging area) is the proposed next snapshot. A commit permanently records the index as a snapshot with a message, author and parent pointer. git add moves changes into the index, git commit records it, git status and git diff show differences between the three. HEAD points at the current commit (usually via a branch).",
        "use_cases": ["Committing only part of your changes (git add -p).", "Reviewing what will go into a commit (git diff --staged).", "Writing atomic commits that are easy to revert."],
        "key_points": [
            "git diff: working tree vs index. git diff --staged: index vs HEAD.",
            "Commits are immutable; 'changing' one creates a new commit.",
            "Good commits are small, focused and explain why.",
            ".gitignore keeps build output and secrets out of the repo.",
        ],
        "examples": [
            ex("First commits", "basic", "Make two commits and inspect history.", "bash", """
                git commit -m "add README"
                git commit -m "add app skeleton"
                git log --oneline
            """),
            ex("Stage selectively", "intermediate", "Review hunks and stage only what belongs together.", "bash", """
                git status
                git add -p src/app.py
                git diff --staged
                git commit -m "fix: handle empty input"
            """, runnable=False),
            ex("Ignore files", "basic", "Never commit environment files or build output.", "bash", """
                cat >> .gitignore <<'EOF'
                .env
                node_modules/
                dist/
                EOF
                git rm --cached .env   # stop tracking a file that was committed by mistake
            """, runnable=False),
        ],
        "commands": ["git status", "git add <file> · git add -p", "git diff · git diff --staged", "git commit -m \"msg\"", "git log --oneline --graph --all"],
        "gotchas": ["Committed a secret? Removing it in a new commit leaves it in history: rotate it and rewrite history.", "git add . can stage files you didn't mean to.", "Huge binary files bloat the repo forever (use Git LFS)."],
        "interview": [
            qa("basic", "What is the staging area for?", "It lets you compose the next commit deliberately: stage some changes, keep others in progress, and review exactly what will be committed."),
            qa("basic", "Does Git store diffs or snapshots?", "Snapshots: each commit points to a tree of the full project state. Unchanged files are shared by hash, and packfiles delta-compress storage."),
            qa("intermediate", "git diff vs git diff --staged?", "git diff compares working tree with the index (unstaged changes). --staged compares the index with HEAD (what will be committed)."),
            qa("intermediate", "You committed a password. What now?", "Treat it as leaked: rotate the credential first. Then remove it from history (git filter-repo or BFG), force-push, and ask collaborators to re-clone. Add the file to .gitignore."),
        ],
        "related": ["branches", "internals"],
        "flow": flow(
            [node("wt", "Working tree", 15, 50, "sky", "app.py (modified)"), node("ix", "Index", 50, 50, "lemon", "staged snapshot"), node("repo", "Repository", 85, 50, "lilac", "commits", "db"),
             _C("c1", "a1f3", 70, 85, "mint"), _C("c2", "b7e2", 85, 85, "mint", "", True)],
            [("wt", "ix"), ("ix", "repo"), ("c1", "c2")],
            [
                step("Edit files", "You change app.py. Only the working tree differs.", ["wt"], set={"wt": {"sub": "app.py (modified)"}}),
                step("Stage", "<b>git add app.py</b> copies that version into the index.", ["ix"], [pkt("wt", "ix", "git add")], {"ix": {"sub": "app.py staged"}}),
                step("Commit", "<b>git commit</b> turns the index into a snapshot with a parent pointer.", ["repo", "c2"], [pkt("ix", "repo", "git commit")], {"c2": {"hidden": False}}),
                step("Clean state", "Working tree, index and HEAD all match: git status says nothing to commit.", ["c2"], set={"wt": {"sub": "clean"}, "ix": {"sub": "= HEAD"}}),
            ],
        ),
    },
    {
        "id": "branches", "title": "Branches & HEAD", "category": "branching", "level": "basic", "code": "BR",
        "tagline": "Branches are cheap movable pointers; HEAD says where you are.",
        "analogy": "Bookmarks in a choose-your-own-adventure book. Creating a bookmark is free; reading on moves the bookmark you are holding.",
        "what": "A branch is just a file containing a commit hash. Committing moves the current branch forward. HEAD normally points to a branch (symbolic ref); checking out a commit directly gives a detached HEAD. git switch -c creates and switches. Because branches are pointers, creating them is instant, and history is a directed acyclic graph of commits.",
        "use_cases": ["One branch per feature or fix.", "Trying an experiment without risk.", "Release branches for hotfixes."],
        "key_points": [
            "git switch (branches) and git restore (files) replace the overloaded git checkout.",
            "Detached HEAD commits are lost unless you create a branch for them.",
            "Delete merged branches: git branch -d; -D forces.",
            "Short-lived branches reduce merge pain.",
        ],
        "examples": [
            ex("Create and switch", "basic", "Branch off main and commit on the feature branch.", "bash", """
                git commit -m "init"
                git switch -c feature/login
                git commit -m "login form"
                git commit -m "login api"
                git switch main
                git log --oneline --all
            """),
            ex("Detached HEAD", "intermediate", "Check out an old commit, then save work with a branch.", "bash", """
                git commit -m "v1"
                git commit -m "v2"
                git checkout HEAD~1
                git commit -m "experiment"
                git switch -c experiment
                git log --oneline --all
            """),
        ],
        "commands": ["git branch · git branch -a", "git switch -c <name>", "git switch <name>", "git branch -d <name>", "git log --oneline --graph --all"],
        "gotchas": ["Working on main by accident: create a branch at HEAD and reset main.", "Switching branches with uncommitted changes carries them along (or refuses).", "Branch names are case sensitive on Linux, not on macOS defaults."],
        "interview": [
            qa("basic", "What is a branch in Git?", "A movable pointer (ref) to a commit. New commits on the branch advance the pointer; creating a branch writes one small file."),
            qa("basic", "What is HEAD?", "A reference to what you have checked out, usually a branch name (refs/heads/main). The next commit's parent is HEAD's commit."),
            qa("intermediate", "What is a detached HEAD and is it dangerous?", "HEAD points directly at a commit, not a branch. Commits made there are reachable only from HEAD; switching away makes them garbage unless you create a branch (or find them via reflog)."),
            qa("intermediate", "git checkout vs git switch?", "checkout does both branch switching and file restoring. switch only changes branches and restore only restores files, which is clearer and safer."),
        ],
        "related": ["three-trees", "merging"],
        "flow": flow(
            [_C("c1", "c1", 15, 55), _C("c2", "c2", 35, 55), _C("c3", "c3", 55, 30, "mint", "", True), _C("c4", "c4", 75, 30, "mint", "", True),
             _R("main", "main", 35, 82), _R("feat", "feature", 55, 10, "lilac", True), _R("head", "HEAD", 15, 82, "rose")],
            [("c1", "c2"), ("c2", "c3"), ("c3", "c4")],
            [
                step("main points to c2", "HEAD → main → c2.", ["c2", "main", "head"], set={"head": {"x": 35, "y": 95}}),
                step("Create a branch", "<b>git switch -c feature</b> adds a pointer at the same commit and moves HEAD to it.", ["feat"], set={"feat": {"hidden": False, "x": 35, "y": 30}, "head": {"x": 50, "y": 18}}),
                step("Commit moves the branch", "Two commits advance <b>feature</b>; main stays at c2.", ["c3", "c4", "feat"], [pkt("c2", "c3"), pkt("c3", "c4")], {"c3": {"hidden": False}, "c4": {"hidden": False}, "feat": {"x": 75, "y": 10}, "head": {"x": 90, "y": 10}}),
                step("Switch back", "<b>git switch main</b> moves HEAD and rewrites the working tree to c2.", ["main", "head"], set={"head": {"x": 35, "y": 95}}),
            ],
        ),
    },
    {
        "id": "merging", "title": "Merging & Conflicts", "category": "branching", "level": "intermediate", "code": "MG",
        "tagline": "Fast-forward vs three-way merges and how to resolve conflicts.",
        "analogy": "Two editors revise copies of the same chapter. If only one changed it, take that copy (fast-forward). If both did, combine them line by line, and talk when they edited the same sentence (conflict).",
        "what": "git merge integrates another branch. If the current branch has no new commits, Git fast-forwards the pointer. Otherwise it performs a three-way merge using the merge base (common ancestor), creating a merge commit with two parents. A conflict happens when both sides changed the same lines; Git writes conflict markers and you edit, add and commit. --no-ff forces a merge commit to keep feature boundaries visible.",
        "use_cases": ["Integrating a finished feature into main.", "Pulling main into a long-lived branch.", "Preserving the history of a release."],
        "key_points": [
            "Merge base = best common ancestor of the two tips.",
            "Merge commits preserve true history; they never rewrite.",
            "git merge --abort returns to the pre-merge state.",
            "rerere can remember conflict resolutions.",
        ],
        "examples": [
            ex("Fast-forward", "basic", "main has no new commits, so the pointer just moves.", "bash", """
                git commit -m "init"
                git switch -c fix
                git commit -m "fix typo"
                git switch main
                git merge fix
                git log --oneline --all
            """),
            ex("Three-way merge", "intermediate", "Both branches moved; a merge commit with two parents is created.", "bash", """
                git commit -m "init"
                git switch -c feature
                git commit -m "feature work"
                git switch main
                git commit -m "hotfix on main"
                git merge feature
                git log --oneline --all
            """),
            ex("Resolving a conflict", "intermediate", "Edit the markers, then stage and commit.", "bash", """
                git merge feature
                # CONFLICT (content): Merge conflict in config.yml
                # <<<<<<< HEAD
                # timeout: 30
                # =======
                # timeout: 60
                # >>>>>>> feature
                git add config.yml
                git commit            # or: git merge --abort
            """, runnable=False),
        ],
        "commands": ["git merge <branch>", "git merge --no-ff <branch>", "git merge --abort", "git merge-base A B", "git config rerere.enabled true"],
        "gotchas": ["Resolving conflicts by blindly taking 'ours' and dropping a teammate's fix.", "Committing conflict markers.", "Huge long-lived branches turn every merge into a conflict festival."],
        "interview": [
            qa("basic", "Fast-forward vs three-way merge?", "Fast-forward moves the pointer when the target is directly ahead, so no new commit is created. Three-way merge combines divergent histories using the merge base and creates a merge commit with two parents."),
            qa("intermediate", "How does Git detect a merge conflict?", "It compares both tips against the merge base; if both sides changed the same region differently, it cannot choose automatically and marks a conflict."),
            qa("intermediate", "Why use --no-ff?", "To always record a merge commit, keeping a visible group of commits per feature and making it possible to revert the whole feature with one revert -m 1."),
            qa("advanced", "How do you revert a merge commit?", "git revert -m 1 <merge> keeps the first parent's side. Note that re-merging the same branch later requires reverting the revert."),
        ],
        "related": ["rebase", "branches"],
        "flow": flow(
            [_C("b", "base", 12, 55), _C("m1", "m1", 40, 75), _C("f1", "f1", 40, 30, "mint"), _C("f2", "f2", 62, 30, "mint"),
             _C("mc", "merge", 82, 60, "lilac", "2 parents", True), _R("main", "main", 40, 93), _R("feat", "feature", 62, 10, "mint")],
            [("b", "m1"), ("b", "f1"), ("f1", "f2"), ("m1", "mc"), ("f2", "mc")],
            [
                step("Divergent history", "main has m1, feature has f1 and f2. Their common ancestor is <b>base</b>.", ["b", "m1", "f1", "f2"]),
                step("Find the merge base", "Git compares each tip with the merge base to see who changed what.", ["b"], [pkt("m1", "b", "diff"), pkt("f2", "b", "diff")]),
                step("Create the merge commit", "<b>git merge feature</b> writes a commit with parents m1 and f2.", ["mc", "main"], [pkt("m1", "mc"), pkt("f2", "mc")], {"mc": {"hidden": False}, "main": {"x": 82, "y": 85}}),
                step("Conflicts", "If both changed the same lines, Git stops and asks you to edit the markers, then git add + commit.", ["mc"], set={"mc": {"sub": "CONFLICT?", "tint": "rose"}}),
            ],
        ),
    },
    {
        "id": "rebase", "title": "Rebase", "category": "branching", "level": "intermediate", "code": "RB",
        "tagline": "Replay commits on a new base for a linear history, and the golden rule.",
        "analogy": "Re-recording your song's verses on top of the band's newest backing track, instead of mixing two different tracks together.",
        "what": "git rebase main takes the commits on your branch that are not in main and replays them, one by one, on top of main's tip. The result is a linear history with new commit ids (the old ones are abandoned). Conflicts are resolved per commit (git rebase --continue). The golden rule: never rebase commits that others have already based work on (shared/pushed branches), unless everyone agrees and you use --force-with-lease.",
        "use_cases": ["Updating a feature branch with the latest main before review.", "Keeping a clean linear history.", "Moving a branch to a different base (--onto)."],
        "key_points": [
            "Rebased commits get new hashes: they are copies.",
            "git pull --rebase avoids needless merge commits.",
            "--force-with-lease refuses to overwrite remote work you have not seen.",
            "Rebase vs merge is a team convention; be consistent.",
        ],
        "examples": [
            ex("Rebase a feature on main", "intermediate", "Feature commits are replayed after main's new commit.", "bash", """
                git commit -m "init"
                git switch -c feature
                git commit -m "feature A"
                git commit -m "feature B"
                git switch main
                git commit -m "main moved"
                git switch feature
                git rebase main
                git log --oneline --all
            """),
            ex("Rebase then fast-forward", "intermediate", "After rebasing, merging into main is a fast-forward.", "bash", """
                git commit -m "init"
                git switch -c feature
                git commit -m "work"
                git switch main
                git commit -m "other work"
                git switch feature
                git rebase main
                git switch main
                git merge feature
                git log --oneline
            """),
            ex("Safe force push", "advanced", "After rebasing your own pushed branch.", "bash", """
                git fetch origin
                git rebase origin/main
                git push --force-with-lease origin feature
            """, runnable=False),
        ],
        "commands": ["git rebase main", "git rebase --continue · --abort · --skip", "git pull --rebase", "git rebase --onto new-base old-base branch", "git push --force-with-lease"],
        "gotchas": ["Rebasing a shared branch forces everyone else to recover.", "Using --force instead of --force-with-lease and erasing a teammate's push.", "Resolving the same conflict repeatedly in a long rebase (enable rerere)."],
        "interview": [
            qa("intermediate", "Merge vs rebase?", "Merge preserves history exactly and adds merge commits; safe for shared branches. Rebase rewrites your commits onto a new base for linear history; great for local/feature branches, dangerous for shared ones."),
            qa("intermediate", "What is the golden rule of rebasing?", "Do not rebase commits that exist outside your repository and that others may have built on, because their history would diverge from yours."),
            qa("advanced", "What does git rebase --onto do?", "git rebase --onto X A B replays commits in A..B onto X. Useful to move a branch that was started from the wrong base."),
            qa("advanced", "--force vs --force-with-lease?", "--force overwrites the remote branch unconditionally. --force-with-lease only pushes if the remote still points where you last saw it, protecting others' new commits."),
        ],
        "related": ["merging", "interactive-rebase"],
        "flow": flow(
            [_C("b", "base", 10, 60), _C("m1", "m1", 32, 60), _C("a", "A", 32, 25, "mint"), _C("bb", "B", 54, 25, "mint"),
             _C("a2", "A'", 56, 60, "lilac", "", True), _C("b2", "B'", 78, 60, "lilac", "", True), _R("feat", "feature", 54, 8, "mint"), _R("main", "main", 32, 85)],
            [("b", "m1"), ("b", "a"), ("a", "bb"), ("m1", "a2"), ("a2", "b2")],
            [
                step("Diverged", "feature (A, B) started from base; main has a new commit m1.", ["a", "bb", "m1"]),
                step("Replay A", "<b>git rebase main</b> re-applies A's change on m1, creating a new commit A'.", ["a2"], [pkt("a", "a2", "replay")], {"a2": {"hidden": False}}),
                step("Replay B", "B is replayed on A'. New hashes: these are copies.", ["b2"], [pkt("bb", "b2", "replay")], {"b2": {"hidden": False}}),
                step("Move the branch", "feature now points to B'. The old A and B become unreachable (reflog keeps them).", ["b2", "feat"], set={"feat": {"x": 78, "y": 85}, "a": {"tint": "slate"}, "bb": {"tint": "slate"}}),
            ],
        ),
    },
    {
        "id": "undoing", "title": "Undoing: restore, reset, revert", "category": "fixing", "level": "intermediate", "code": "UN",
        "tagline": "Pick the right undo: discard edits, move branches or add an inverse commit.",
        "analogy": "Writing in a notebook: an eraser for this page (restore), tearing out the last pages (reset), or writing a new note saying 'ignore the previous entry' (revert).",
        "what": "git restore discards working tree changes or unstages files. git reset moves the current branch pointer: --soft keeps changes staged, --mixed (default) keeps them unstaged, --hard discards them. git revert creates a new commit that undoes a previous one, safe for shared history. git commit --amend replaces the last commit. Rule of thumb: rewrite only unpublished history; revert published history.",
        "use_cases": ["Throwing away experimental edits.", "Squashing the last 3 commits into one (reset --soft).", "Undoing a bad commit already on main (revert)."],
        "key_points": [
            "reset --hard loses uncommitted work permanently.",
            "Reset commits are recoverable via reflog for a while.",
            "revert keeps history honest and is push-friendly.",
            "amend changes the commit hash.",
        ],
        "examples": [
            ex("reset --soft to squash", "intermediate", "Combine the last two commits into one.", "bash", """
                git commit -m "init"
                git commit -m "wip 1"
                git commit -m "wip 2"
                git reset --soft HEAD~2
                git commit -m "feature done"
                git log --oneline
            """),
            ex("revert a shared commit", "intermediate", "Add an inverse commit instead of rewriting history.", "bash", """
                git commit -m "init"
                git commit -m "bad change"
                git commit -m "good change"
                git revert HEAD~1
                git log --oneline
            """),
            ex("reset --hard", "advanced", "Move main back and drop the last commit.", "bash", """
                git commit -m "init"
                git commit -m "oops"
                git reset --hard HEAD~1
                git log --oneline --all
            """),
        ],
        "commands": ["git restore <file> · git restore --staged <file>", "git reset --soft | --mixed | --hard <commit>", "git revert <commit>", "git commit --amend", "git clean -fd (untracked files)"],
        "gotchas": ["reset --hard with uncommitted work: that work is gone (not in reflog).", "Amending or resetting already-pushed commits breaks collaborators.", "Reverting a merge without -m."],
        "interview": [
            qa("intermediate", "reset --soft vs --mixed vs --hard?", "All move the branch pointer. --soft keeps index and working tree (changes staged). --mixed resets the index (changes unstaged). --hard resets index and working tree (changes discarded)."),
            qa("intermediate", "reset vs revert?", "reset rewrites history by moving the branch back; for local work. revert adds a new commit that undoes changes; safe on shared branches."),
            qa("basic", "How do you unstage a file?", "git restore --staged <file> (or git reset <file>)."),
            qa("advanced", "You ran git reset --hard and lost commits. Recover?", "git reflog shows where HEAD was; git reset --hard <hash> or git branch rescue <hash>. Uncommitted changes, however, are not recoverable this way."),
        ],
        "related": ["bisect-reflog", "interactive-rebase"],
        "flow": flow(
            [_C("c1", "c1", 12, 50), _C("c2", "c2", 36, 50), _C("c3", "c3", 60, 50, "rose", "bad"), _C("rv", "revert c3", 84, 50, "mint", "", True), _R("main", "main", 60, 82)],
            [("c1", "c2"), ("c2", "c3"), ("c3", "rv")],
            [
                step("A bad commit", "c3 introduced a bug; main points to it.", ["c3", "main"]),
                step("Local only? reset", "<b>git reset --hard HEAD~1</b> moves main back to c2. c3 is orphaned (reflog remembers).", ["c2", "main"], set={"main": {"x": 36}, "c3": {"tint": "slate"}}),
                step("Already pushed? revert", "Instead, keep c3 and add <b>revert c3</b>, an inverse commit. History stays shareable.", ["rv", "main"], [pkt("c3", "rv")], {"main": {"x": 84}, "c3": {"tint": "rose"}, "rv": {"hidden": False}}),
            ],
        ),
    },
    {
        "id": "remotes", "title": "Remotes: fetch, pull, push", "category": "collab", "level": "basic", "code": "RM",
        "tagline": "origin, remote-tracking branches and upstreams.",
        "analogy": "A shared Google Drive folder (remote) and your laptop copy. fetch downloads news without touching your files; pull downloads and merges; push uploads your changes.",
        "what": "A remote is a named URL (origin). git fetch downloads objects and updates remote-tracking branches (origin/main) without changing your branches. git pull = fetch + merge (or rebase). git push uploads commits and moves the remote branch, rejected if it is not a fast-forward. An upstream links a local branch to a remote one (git push -u). Forks add a second remote (upstream) to sync from.",
        "use_cases": ["Sharing branches for code review.", "Syncing a fork with the original repo.", "Checking what teammates pushed before merging."],
        "key_points": [
            "origin/main is your last-known view of the remote, updated only by fetch.",
            "Rejected push: fetch, integrate, push again.",
            "pull.rebase=true keeps history linear.",
            "Use SSH keys or credential managers; never put tokens in remote URLs.",
        ],
        "examples": [
            ex("Clone, branch and push", "basic", "Publish a feature branch and set its upstream.", "bash", """
                git clone git@github.com:acme/shop.git
                cd shop
                git switch -c feature/cart
                git commit -am "cart badge"
                git push -u origin feature/cart
            """, runnable=False),
            ex("Fetch before you merge", "intermediate", "See what changed remotely without touching your branch.", "bash", """
                git fetch origin
                git log --oneline main..origin/main
                git pull --rebase
            """, runnable=False),
            ex("Sync a fork", "intermediate", "Add the original repository as 'upstream'.", "bash", """
                git remote add upstream https://github.com/original/project.git
                git fetch upstream
                git rebase upstream/main
                git push --force-with-lease origin main
            """, runnable=False),
        ],
        "commands": ["git remote -v", "git fetch [--prune]", "git pull [--rebase]", "git push -u origin <branch>", "git branch -vv (tracking info)"],
        "gotchas": ["Embedding access tokens in remote URLs (they end up in shell history and .git/config).", "git pull creating noisy merge commits on every sync.", "Pushing to the wrong remote or branch: check git branch -vv."],
        "interview": [
            qa("basic", "fetch vs pull?", "fetch downloads remote commits and updates origin/* refs only. pull also integrates them into your current branch (merge by default, or rebase)."),
            qa("intermediate", "Why was my push rejected?", "The remote branch has commits you don't have, so your push isn't a fast-forward. Fetch, rebase or merge, then push."),
            qa("intermediate", "What is a remote-tracking branch?", "A read-only local ref like origin/main recording where the remote's branch was at your last fetch."),
            qa("basic", "How do you keep a fork up to date?", "Add the original as upstream, fetch it, rebase or merge upstream/main into your main, and push to your fork."),
        ],
        "related": ["workflows", "rebase"],
        "flow": flow(
            [node("remote", "origin (GitHub)", 80, 20, "lilac", "main @ r2", "db"), node("om", "origin/main", 50, 20, "lemon", "@ r1", "pill"), node("local", "main (local)", 20, 20, "sky", "@ r1", "pill"),
             node("wt", "Working tree", 20, 75, "mint")],
            [("remote", "om"), ("om", "local"), ("local", "wt")],
            [
                step("Someone pushed", "The remote main moved to r2. Your view (origin/main) still says r1.", ["remote", "om"]),
                step("git fetch", "Downloads r2 and updates origin/main. Your main and files are untouched.", ["om"], [pkt("remote", "om", "objects")], {"om": {"sub": "@ r2"}}),
                step("Integrate", "<b>git merge origin/main</b> (or pull) moves your main and updates files.", ["local", "wt"], [pkt("om", "local", "ff"), pkt("local", "wt", "checkout")], {"local": {"sub": "@ r2"}}),
                step("git push", "Your new commit r3 uploads; the remote fast-forwards.", ["remote"], [pkt("local", "remote", "r3")], {"remote": {"sub": "main @ r3"}, "local": {"sub": "@ r3"}, "om": {"sub": "@ r3"}}),
            ],
        ),
    },
    {
        "id": "stash-cherry-pick", "title": "Stash, Cherry-pick & Tags", "category": "fixing", "level": "intermediate", "code": "SC",
        "tagline": "Park unfinished work, copy single commits, and mark releases.",
        "analogy": "Stash is a drawer for half-done homework; cherry-pick is photocopying one page from a friend's notebook; a tag is a permanent sticky note saying 'v1.0 was here'.",
        "what": "git stash saves uncommitted changes and cleans the working tree so you can switch tasks; git stash pop reapplies them. git cherry-pick <commit> applies one commit's change onto the current branch as a new commit, useful for backporting fixes. Tags name specific commits: lightweight tags are pointers, annotated tags (git tag -a) are objects with a message and tagger, used for releases.",
        "use_cases": ["Urgent bug interrupts half-done work (stash).", "Backport a fix from main to release/1.4 (cherry-pick).", "Mark v2.3.0 for a deployment (annotated tag)."],
        "key_points": [
            "git stash -u includes untracked files.",
            "Cherry-picked commits get new hashes; duplicates may conflict later.",
            "Tags are not pushed by default: git push --tags or push the tag name.",
            "Prefer annotated tags (or signed) for releases.",
        ],
        "examples": [
            ex("Backport with cherry-pick", "intermediate", "Copy a fix from main to the release branch.", "bash", """
                git commit -m "v1"
                git branch release
                git commit -m "new feature"
                git commit -m "fix crash"
                git switch release
                git cherry-pick main
                git tag v1.0.1
                git log --oneline --all
            """),
            ex("Stash for an interruption", "basic", "Park work, fix something, come back.", "bash", """
                git stash push -m "half-done search"
                git switch -c hotfix main
                # ...fix, commit, push...
                git switch feature/search
                git stash pop
            """, runnable=False),
        ],
        "commands": ["git stash push -m msg [-u]", "git stash list · pop · apply · drop", "git cherry-pick <commit> [-x]", "git tag -a v1.2.0 -m \"release\"", "git push origin v1.2.0"],
        "gotchas": ["Forgotten stashes pile up; name them.", "Cherry-picking many commits instead of merging a branch.", "Moving a tag that others already fetched."],
        "interview": [
            qa("intermediate", "When would you use cherry-pick?", "To apply a specific commit elsewhere, typically backporting a hotfix to a release branch, without merging everything else."),
            qa("basic", "What does git stash do?", "Saves your uncommitted changes onto a stack and reverts the working tree to HEAD, so you can switch branches; pop or apply restores them."),
            qa("intermediate", "Lightweight vs annotated tags?", "Lightweight: just a ref to a commit. Annotated: a full object with tagger, date, message and optional signature, recommended for releases."),
            qa("advanced", "What does cherry-pick -x add?", "A line '(cherry picked from commit ...)' in the message, recording provenance for later auditing."),
        ],
        "related": ["undoing", "workflows"],
        "flow": flow(
            [_C("v1", "v1", 12, 50), _C("f", "feature", 40, 25), _C("fix", "fix", 66, 25, "mint", "crash fix"), _C("fix2", "fix'", 40, 78, "lilac", "copy", True),
             _R("main", "main", 66, 6), _R("rel", "release", 12, 90), _R("tag", "v1.0.1", 66, 90, "peach", True)],
            [("v1", "f"), ("f", "fix"), ("v1", "fix2")],
            [
                step("Fix on main", "The crash fix landed on main after a feature that is not ready for release.", ["fix"]),
                step("Cherry-pick", "On release: <b>git cherry-pick main</b> applies just the fix as a new commit.", ["fix2"], [pkt("fix", "fix2", "copy")], {"fix2": {"hidden": False}, "rel": {"x": 40, "y": 95}}),
                step("Tag the release", "<b>git tag v1.0.1</b> names the exact commit you deploy.", ["tag"], [pkt("tag", "fix2")], {"tag": {"hidden": False, "x": 66, "y": 78}}),
            ],
        ),
    },
    {
        "id": "interactive-rebase", "title": "Interactive Rebase & Clean History", "category": "fixing", "level": "advanced", "code": "IR",
        "tagline": "Squash, reword, reorder and fixup commits before sharing.",
        "analogy": "Editing a draft before publishing: merge tiny paragraphs, fix headings, reorder sections, and drop the notes to yourself.",
        "what": "git rebase -i <base> opens a todo list of commits. Change pick to reword, edit, squash, fixup or drop, or reorder lines. Git replays commits accordingly. git commit --fixup <hash> plus git rebase -i --autosquash automates fixups. Clean, atomic commits make review, bisect and revert easier.",
        "use_cases": ["Turning 'wip', 'fix', 'fix again' into one meaningful commit.", "Splitting a commit that does two things (edit + reset).", "Removing an accidental debug commit."],
        "key_points": [
            "Only on commits not yet shared (or on your own PR branch with a lease).",
            "squash keeps messages to combine; fixup discards the fixup's message.",
            "git rebase --abort if it goes wrong; reflog as a safety net.",
            "Many teams squash-merge PRs instead.",
        ],
        "examples": [
            ex("Todo list", "advanced", "Squash fixups into the main commit and reword it.", "bash", """
                git rebase -i HEAD~4
                # reword a1b2c3 add search endpoint
                # fixup  d4e5f6 fix typo
                # fixup  0718aa address review
                # drop   9f8e7d debug logging
            """, runnable=False),
            ex("Autosquash", "advanced", "Mark fixups as you go; fold them in later.", "bash", """
                git commit --fixup a1b2c3
                git rebase -i --autosquash main
            """, runnable=False),
        ],
        "commands": ["git rebase -i HEAD~n", "pick · reword · edit · squash · fixup · drop", "git commit --fixup <hash>", "git rebase -i --autosquash <base>", "git config --global rebase.autoSquash true"],
        "gotchas": ["Rewriting commits on a branch a teammate also pushes to.", "Squashing everything into one giant commit that is impossible to review or revert partially.", "Forgetting commit signing is re-done after a rebase."],
        "interview": [
            qa("advanced", "squash vs fixup?", "Both merge a commit into the previous one. squash lets you combine the messages; fixup discards the fixup commit's message."),
            qa("advanced", "How do you split a commit?", "Mark it 'edit' in rebase -i, then git reset HEAD~ to unstage, add and commit in pieces, and git rebase --continue."),
            qa("intermediate", "Squash merge vs rebase merge for PRs?", "Squash merge creates one commit per PR (clean main, loses granular history). Rebase merge keeps each commit linearly, which is valuable if commits are already clean."),
            qa("intermediate", "Why care about clean history?", "Easier code review, meaningful blame, effective bisect, and safe reverts of a single logical change."),
        ],
        "related": ["rebase", "undoing"],
        "flow": flow(
            [_C("a", "add search", 12, 40, "mint"), _C("b", "fix typo", 34, 40, "rose"), _C("c", "review", 56, 40, "rose"), _C("d", "debug log", 78, 40, "slate"),
             _C("s", "add search ✓", 34, 82, "lilac", "1 clean commit", True)],
            [("a", "b"), ("b", "c"), ("c", "d")],
            [
                step("Messy branch", "Four commits, two are fixups and one is debug noise.", ["a", "b", "c", "d"]),
                step("Fixup", "Mark 'fix typo' and 'review' as <b>fixup</b>: folded into 'add search'.", ["b", "c"], [pkt("b", "a"), pkt("c", "a")]),
                step("Drop", "Mark 'debug log' as <b>drop</b>.", ["d"], set={"d": {"sub": "dropped"}}),
                step("Result", "One clean commit ready for review.", ["s"], set={"s": {"hidden": False}, "a": {"tint": "slate"}, "b": {"tint": "slate"}, "c": {"tint": "slate"}}),
            ],
        ),
    },
    {
        "id": "internals", "title": "Git Internals: Objects & Refs", "category": "internals", "level": "advanced", "code": "GI",
        "tagline": "Blobs, trees, commits, tags: a content-addressed DAG.",
        "analogy": "A warehouse where every box is labelled by a fingerprint of its contents. Identical content always gets the same label, and boxes list the labels of other boxes inside.",
        "what": "Git is a content-addressable store. A blob holds file contents; a tree lists names → blob/tree hashes with modes; a commit points to a tree plus parents, author, committer and message; an annotated tag points to an object with metadata. Objects are identified by SHA-1 (SHA-256 is supported in newer repos) of their content. Refs (branches, tags) are files in .git/refs or packed-refs pointing to hashes. Packfiles compress objects with deltas.",
        "use_cases": ["Understanding why identical files cost no extra space.", "Debugging a corrupted repo.", "Explaining why rewriting history changes all descendant hashes."],
        "key_points": [
            "Changing any byte changes the hash, and every descendant commit hash.",
            "Branches are 41-byte files; that's why they are cheap.",
            "git gc packs loose objects; unreachable objects are pruned after expiry.",
            "Git's object ids use SHA-1 with collision detection; repos can opt into SHA-256.",
        ],
        "examples": [
            ex("Peek into objects", "advanced", "Inspect the commit, its tree and a blob.", "bash", """
                git cat-file -t HEAD          # commit
                git cat-file -p HEAD          # tree <hash>, parent <hash>, author ...
                git cat-file -p HEAD^{tree}   # 100644 blob <hash>  README.md
                git rev-parse HEAD:README.md
                cat .git/refs/heads/main
            """, runnable=False),
            ex("Hash an object yourself", "advanced", "Git hashes 'blob <size>\\0<content>'.", "bash", """
                echo 'hello' | git hash-object --stdin
                printf 'blob 6\\0hello\\n' | sha1sum
            """, runnable=False),
        ],
        "commands": ["git cat-file -t | -p <obj>", "git ls-tree HEAD", "git rev-parse <ref>", "git hash-object -w <file>", "git count-objects -v · git gc"],
        "gotchas": ["Editing files inside .git by hand.", "Assuming deleted history is gone: forks, clones and caches may keep it.", "Shallow clones break some history commands."],
        "interview": [
            qa("advanced", "What are Git's four object types?", "Blob (file content), tree (directory listing), commit (tree + parents + metadata), and annotated tag (a named, signed pointer to an object)."),
            qa("advanced", "Why does changing an old commit change all later hashes?", "Each commit's hash includes its parent's hash, so a change propagates down the chain, like a Merkle tree."),
            qa("intermediate", "Why are branches so cheap in Git?", "A branch is a tiny file storing a commit hash. Creating one does not copy any files."),
            qa("advanced", "What does git gc do?", "Packs loose objects into packfiles with delta compression, packs refs, and prunes unreachable objects older than the grace period."),
        ],
        "related": ["three-trees", "bisect-reflog"],
        "flow": flow(
            [_R("ref", "refs/heads/main", 10, 15), node("commit", "commit 9c1e", 38, 15, "lilac", "tree, parent, author"), node("tree", "tree 4b82", 38, 55, "sky", "README.md, src/"),
             node("blob", "blob e69d", 68, 40, "mint", "README contents"), node("sub", "tree 1f0a", 68, 75, "sky", "src/"), node("blob2", "blob 77aa", 92, 75, "mint", "app.py"), node("parent", "commit 51b0", 68, 10, "lilac", "previous")],
            [("ref", "commit"), ("commit", "tree"), ("commit", "parent"), ("tree", "blob"), ("tree", "sub"), ("sub", "blob2")],
            [
                step("Ref → commit", "The branch file contains one hash: commit 9c1e.", ["ref", "commit"], [pkt("ref", "commit", "9c1e")]),
                step("Commit → tree + parent", "The commit records the root tree and its parent commit.", ["tree", "parent"], [pkt("commit", "tree"), pkt("commit", "parent")]),
                step("Trees → blobs", "Trees map names to blobs (file contents) and sub-trees.", ["blob", "sub", "blob2"], [pkt("tree", "blob"), pkt("tree", "sub"), pkt("sub", "blob2")]),
                step("Content addressing", "Change app.py: new blob, new src tree, new root tree, new commit. Unchanged README blob is reused.", ["blob2", "blob"], set={"blob2": {"label": "blob 0d3c", "tint": "lemon"}, "blob": {"sub": "reused"}}),
            ],
        ),
    },
    {
        "id": "workflows", "title": "Team Workflows & Pull Requests", "category": "collab", "level": "intermediate", "code": "WF",
        "tagline": "Trunk-based, GitHub flow, Git flow, PR reviews and protected branches.",
        "analogy": "A newspaper: reporters write drafts (branches), editors review them (pull requests), and only approved stories reach the printing press (main).",
        "what": "A workflow is a team agreement on branching and integration. Trunk-based development: tiny short-lived branches merged to main daily, feature flags hide unfinished work, enabling continuous delivery. GitHub flow: branch → PR → review + CI → merge → deploy. Git flow: develop, release and hotfix branches for scheduled releases (heavier). Protected branches require reviews and green checks; CODEOWNERS route reviews; conventional commits and semantic versioning automate changelogs.",
        "use_cases": ["Choosing a branching model for a new team.", "Setting branch protection rules.", "Automating releases from commit messages."],
        "key_points": [
            "Small PRs are reviewed faster and better.",
            "CI must pass before merge; main is always deployable.",
            "Feature flags decouple deploy from release.",
            "Signed commits/tags strengthen supply-chain trust.",
        ],
        "examples": [
            ex("GitHub flow with the gh CLI", "basic", "Branch, push and open a PR.", "bash", """
                git switch -c feat/search-filters
                git commit -am "feat(search): add price filter"
                git push -u origin feat/search-filters
                gh pr create --fill --base main
                gh pr checks --watch
            """, runnable=False),
            ex("CODEOWNERS", "intermediate", "Route reviews automatically.", "text", """
                # .github/CODEOWNERS
                /infra/        @acme/platform
                /payments/     @acme/payments @lead-dev
                *.sql          @acme/dba
            """, runnable=False),
        ],
        "commands": ["Branch protection: required reviews + status checks", "Conventional commits: feat:, fix:, chore:, BREAKING CHANGE:", "Semantic versioning MAJOR.MINOR.PATCH", "gh pr create · gh pr review · gh pr merge --squash"],
        "gotchas": ["Long-lived feature branches drifting for weeks.", "Merging with red CI 'just this once'.", "Mega PRs that nobody can review properly."],
        "interview": [
            qa("intermediate", "Trunk-based development vs Git flow?", "Trunk-based: everyone integrates small changes into main frequently, behind feature flags; enables CI/CD. Git flow: develop/release/hotfix branches for versioned, scheduled releases; more ceremony and merge overhead."),
            qa("intermediate", "What makes a good pull request?", "Small and focused, clear description of why, tests, green CI, screenshots for UI, and linked issue. Reviewers can understand it in minutes."),
            qa("basic", "What are protected branches?", "Branch rules that block direct pushes and force pushes and require reviews and passing checks before merging."),
            qa("advanced", "How do you release from a trunk-based repo?", "Tag commits on main (often automated from conventional commits), deploy continuously, use feature flags for incomplete work, and cut short-lived release branches only if you must patch old versions."),
        ],
        "related": ["remotes", "interactive-rebase"],
        "flow": flow(
            [node("dev", "Developer", 8, 50, "slate"), node("br", "feature branch", 30, 50, "mint", "small change", "pill"), node("pr", "Pull request", 52, 50, "lilac", "review"),
             node("ci", "CI checks", 52, 15, "lemon", "tests, lint"), node("main", "main", 76, 50, "sky", "protected", "pill"), node("deploy", "Deploy", 94, 50, "peach", "", "round")],
            [("dev", "br"), ("br", "pr"), ("pr", "ci"), ("pr", "main"), ("main", "deploy")],
            [
                step("Branch", "Create a short-lived branch for one change.", ["br"], [pkt("dev", "br", "commit")]),
                step("Open a PR", "Push and open a pull request with context.", ["pr"], [pkt("br", "pr", "push")]),
                step("Checks and review", "CI runs; CODEOWNERS review. Protected main blocks merge until both pass.", ["ci", "pr"], [pkt("pr", "ci", "run"), pkt("ci", "pr", "✓", "mint")]),
                step("Merge and ship", "Squash merge into main, which deploys automatically.", ["main", "deploy"], [pkt("pr", "main", "merge"), pkt("main", "deploy", "release")]),
            ],
        ),
    },
    {
        "id": "bisect-reflog", "title": "Bisect, Reflog & Blame", "category": "fixing", "level": "advanced", "code": "BS",
        "tagline": "Binary-search the commit that broke things and recover anything.",
        "analogy": "Finding which of 100 light bulbs on a string is broken by testing the middle, then the middle of the bad half, and so on. Seven tests instead of a hundred.",
        "what": "git bisect performs a binary search between a known good and a known bad commit: you (or a script via git bisect run) mark each checkout good or bad until Git names the first bad commit, in log₂(n) steps. git reflog records where HEAD and branches pointed over time, even after resets and rebases, so 'lost' commits can be recovered. git blame shows the last commit to touch each line (use -w and -C to ignore whitespace and moves); git log -S finds when a string appeared.",
        "use_cases": ["A test that passed last week now fails: which commit?", "Recovering a branch deleted by mistake.", "Finding why a line was written."],
        "key_points": [
            "1,000 commits need only ~10 bisect steps.",
            "git bisect run <script> automates the search (exit 0 = good).",
            "Reflog is local and expires (default 90 days for reachable entries).",
            "git log -S 'text' (pickaxe) searches content changes.",
        ],
        "examples": [
            ex("Automated bisect", "advanced", "Let a test script drive the search.", "bash", """
                git bisect start
                git bisect bad HEAD
                git bisect good v2.3.0
                git bisect run pytest tests/test_checkout.py -x -q
                git bisect reset
            """, runnable=False),
            ex("Rescue with reflog", "advanced", "Undo an accidental hard reset.", "bash", """
                git reset --hard HEAD~3          # oops
                git reflog                       # a1b2c3 HEAD@{1}: commit: payment retries
                git branch rescue HEAD@{1}
            """, runnable=False),
            ex("Who and when", "intermediate", "Blame ignoring whitespace, and find when a string was introduced.", "bash", """
                git blame -w -C src/payment.py
                git log -S "retry_limit" --oneline
            """, runnable=False),
        ],
        "commands": ["git bisect start · good · bad · run · reset", "git reflog [branch]", "git branch rescue <hash>", "git blame -w -C <file>", "git log -S 'text' / -G 'regex'"],
        "gotchas": ["Untestable commits during bisect: use git bisect skip.", "Reflog doesn't exist on a fresh clone: it's local history.", "Blame shows the last formatter commit unless you use .git-blame-ignore-revs."],
        "interview": [
            qa("advanced", "How does git bisect work?", "Binary search over history: mark one good and one bad commit, Git checks out the midpoint, you mark it, and the range halves each step until the first bad commit is found in about log₂(n) steps."),
            qa("intermediate", "What is the reflog?", "A local log of every position HEAD and each branch has had, including after reset, rebase and amend. It lets you recover commits that are no longer referenced."),
            qa("advanced", "A teammate force-pushed and your commits vanished from the remote. Recover?", "Your local reflog still has them: find the hash with git reflog or origin/branch's reflog, create a branch at it and push it back."),
            qa("intermediate", "How do you find when a function was removed?", "git log -S 'function_name' -p shows commits that added or removed that string."),
        ],
        "related": ["undoing", "internals"],
        "flow": flow(
            [_C("g", "v2.3 ✓", 8, 50, "mint", "good"), _C("c2", "c2", 22, 50), _C("c3", "c3", 36, 50), _C("c4", "c4", 50, 50), _C("c5", "c5", 64, 50), _C("c6", "c6", 78, 50), _C("b", "HEAD ✗", 92, 50, "rose", "bad")],
            [("g", "c2"), ("c2", "c3"), ("c3", "c4"), ("c4", "c5"), ("c5", "c6"), ("c6", "b")],
            [
                step("Good and bad", "v2.3 passes, HEAD fails. 6 commits to search.", ["g", "b"]),
                step("Test the middle", "Bisect checks out c4: tests pass, so the bug is later.", ["c4"], set={"c4": {"tint": "mint", "sub": "good"}, "c2": {"tint": "slate"}, "c3": {"tint": "slate"}}),
                step("Halve again", "c5 fails: the bug is in c5 or earlier, after c4.", ["c5"], set={"c5": {"tint": "rose", "sub": "bad"}, "c6": {"tint": "slate"}}),
                step("Found", "c5 is the first bad commit, found in 2 tests instead of 6.", ["c5"], set={"c5": {"label": "c5 ← first bad"}}),
            ],
        ),
    },
]

SCENARIOS = [
    {"level": "intermediate", "topic": "undoing", "q": "You pushed a commit that breaks production to main. Teammates have already pulled.", "a": "Do not reset or force-push shared history. git revert <commit> (or -m 1 for a merge), push, and deploy; then fix forward properly on a branch."},
    {"level": "advanced", "topic": "bisect-reflog", "q": "A performance regression appeared somewhere in the last 400 commits.", "a": "Write a script that exits non-zero when the benchmark is too slow, then git bisect start, mark HEAD bad and the last fast tag good, and git bisect run the script. About 9 steps find the culprit."},
    {"level": "advanced", "topic": "three-trees", "q": "An API key was committed three weeks ago and pushed to GitHub.", "a": "Revoke and rotate the key immediately (assume it's compromised). Then purge it from history with git filter-repo, force-push, invalidate caches/forks where possible, add the path to .gitignore, and enable secret scanning / pre-commit hooks."},
    {"level": "intermediate", "topic": "rebase", "q": "After rebasing your feature branch, git push is rejected.", "a": "Rebase rewrote commits, so the remote branch is no longer an ancestor. If it's your own branch, git push --force-with-lease; if others use it, coordinate or merge instead."},
    {"level": "basic", "topic": "branches", "q": "You made three commits on main locally that should have been on a feature branch.", "a": "git branch feature (pointer at your commits), git reset --hard origin/main to move main back, git switch feature. Nothing is lost."},
]

from .git_more import CATEGORIES as _MORE_CATEGORIES, SCENARIOS as _MORE_SCENARIOS, TOPICS as _MORE_TOPICS

CATEGORIES += _MORE_CATEGORIES
TOPICS += _MORE_TOPICS
SCENARIOS += _MORE_SCENARIOS
