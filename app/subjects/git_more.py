"""More git topics, appended to the core module."""

from ._dsl import chain, ex, qa, topic

CATEGORIES = [
    {"id": "history", "title": "History & Search", "color": "peach", "blurb": "Log, blame, tags and patches."},
    {"id": "scale", "title": "Large Repos", "color": "slate", "blurb": "Worktrees, submodules, LFS and partial clones."},
    {"id": "automation", "title": "Hooks & Security", "color": "mint", "blurb": "Hooks, signing, CI and secrets."},
]

TOPICS = [
    topic(
        "init-clone", "init & clone", "basics", "basic", "IC",
        "Start a repository from scratch or copy one with its full history.",
        "git init is buying an empty notebook; git clone is photocopying a colleague's notebook, every page and every bookmark included.",
        "git init creates a .git directory containing the object database, refs, HEAD and a local config, turning the current directory into a repository. The initial branch name comes from init.defaultBranch (commonly set to main). git clone contacts a remote, negotiates which objects are needed, downloads them as a packfile, and writes every remote branch as a remote-tracking ref under refs/remotes/origin/. It then registers the remote as origin and checks out the remote's default branch. git init --bare and git clone --bare create repositories without a working tree, which is what servers host. git clone --mirror additionally copies every ref (including notes and pull refs) and is used for backups and migrations. Options like --depth and --filter reduce what is downloaded for very large repositories.",
        ["Starting a new project locally before pushing it to a hosting service.", "Getting a full copy of an existing project to contribute.", "Creating a bare repository on a server or a mirror for backup."],
        [
            "A clone is a complete repository: full history works offline.",
            "origin is just a conventional name for the remote you cloned from.",
            "Bare repos have no working tree and are the right target for pushes.",
            "Set init.defaultBranch once globally to control the first branch name.",
            "Prefer SSH keys or a credential helper over embedding credentials in URLs.",
        ],
        [
            ex("New repo from scratch", "basic", "Initialise, commit and connect a remote.", "bash", """
                git config --global init.defaultBranch main
                mkdir demo && cd demo
                git init
                echo "# demo" > README.md
                git add README.md
                git commit -m "chore: initial commit"
                git remote add origin git@github.com:example/demo.git
                git push -u origin main
            """, runnable=False),
            ex("Clone variants", "intermediate", "Normal, into a named directory, single branch, and a mirror.", "bash", """
                git clone https://github.com/example/app.git
                git clone git@github.com:example/app.git my-app
                git clone --branch release/2.x --single-branch https://github.com/example/app.git
                git clone --mirror https://github.com/example/app.git app-backup.git
            """, runnable=False),
        ],
        ["git init", "git init --bare repo.git", "git clone <url> [dir]", "git clone --branch <b> --single-branch <url>", "git clone --mirror <url>", "git remote -v"],
        ["Running git init inside an existing repo's subfolder creates a nested repository that the parent will not track properly.", "Credentials embedded in a clone URL end up in .git/config in plain text.", "--single-branch clones only fetch that branch later too, until you widen the fetch refspec."],
        [
            qa("basic", "What does git init actually create?", "A .git directory containing objects/ (the object database), refs/ (branches and tags), HEAD (pointing to the unborn default branch), config and hooks samples. No commits exist until the first git commit."),
            qa("basic", "What does git clone set up besides copying files?", "It copies all objects, creates remote-tracking refs (origin/main etc.), adds the origin remote with a default fetch refspec, creates a local branch for the default branch with upstream tracking, and checks it out."),
            qa("intermediate", "What is a bare repository and when do you use one?", "A repository with no working tree, just the contents of .git. Servers and shared central repos are bare so pushes never conflict with a checked-out working copy."),
            qa("intermediate", "clone --bare vs clone --mirror?", "Both create bare repos. --mirror also copies all refs (not just branches and tags) and configures fetch so a later git remote update overwrites refs exactly, which makes it suitable for backups and migrations."),
        ],
        ["three-trees", "remotes", "internals"],
        chain(
            ("Remote repo", "objects + refs", "The remote", "The server holds a bare repository: objects and refs, no working tree."),
            ("Negotiation", "want / have", "Negotiate", "The client asks for the refs it wants; with an empty repo it has nothing, so it needs everything.", "ls-refs"),
            ("Packfile", "compressed objs", "Transfer", "The server streams one packfile containing every needed object, delta-compressed.", "pack"),
            ("Local .git", "origin/* refs", "Write refs", "Objects are stored and remote branches become remote-tracking refs under refs/remotes/origin/.", "refs"),
            ("Working tree", "main checked out", "Checkout", "A local main is created tracking origin/main and its tree is written to disk.", "checkout"),
        ),
    ),
    topic(
        "config-aliases", "Config Levels & Aliases", "basics", "basic", "CF",
        "System, global, local and conditional config, plus aliases that save keystrokes.",
        "House rules, family rules and your own room's rules: the most specific rule wins when they disagree.",
        "Git reads configuration from several files in order: system (--system, usually /etc/gitconfig), global (--global, ~/.gitconfig or ~/.config/git/config), local (--local, .git/config) and optionally per-worktree (--worktree). Later, more specific levels override earlier ones, and command-line -c options override everything. git config --list --show-origin --show-scope shows where each value comes from, which is the fastest way to debug surprising behaviour. includeIf lets you load a different file based on the repository path or remote URL, for example a work email for repos under ~/work/. Aliases are config entries under alias.*; a value starting with ! runs as a shell command. Useful settings include pull.rebase, push.autoSetupRemote, rerere.enabled, fetch.prune and core.editor. Keep secrets out of config files and use a credential helper backed by the OS keychain instead.",
        ["Setting your name and email once for every repo.", "Using a different identity or signing key for work repositories.", "Creating short aliases for long log or status commands."],
        [
            "Precedence: system < global < local < worktree < command-line -c.",
            "--show-origin reveals which file set a value.",
            "includeIf \"gitdir:~/work/\" switches identity per directory tree.",
            "Aliases starting with ! run in a shell from the repo root.",
            "Credential helpers (osxkeychain, manager, libsecret) keep tokens out of config.",
        ],
        [
            ex("Identity and sensible defaults", "basic", "Global settings most teams recommend.", "bash", """
                git config --global user.name "Ada Lovelace"
                git config --global user.email "ada@example.com"
                git config --global pull.rebase true
                git config --global push.autoSetupRemote true
                git config --global fetch.prune true
                git config --global rerere.enabled true
                git config --list --show-origin --show-scope
            """, runnable=False),
            ex("Conditional work identity", "intermediate", "Use a different email for repos under ~/work.", "bash", """
                # ~/.gitconfig
                [includeIf "gitdir:~/work/"]
                    path = ~/.gitconfig-work

                # ~/.gitconfig-work
                [user]
                    email = ada@company.example
            """, runnable=False),
            ex("Aliases", "basic", "Short names for frequent commands.", "bash", """
                git config --global alias.st "status -sb"
                git config --global alias.lg "log --oneline --graph --decorate --all"
                git config --global alias.undo "reset --soft HEAD~1"
                git config --global alias.root "!pwd"
                git lg
            """, runnable=False),
        ],
        ["git config --global user.email <e>", "git config --list --show-origin", "git config --get <key>", "git config --unset <key>", "git config --global alias.<name> \"<cmd>\""],
        ["A local .git/config value silently overrides your global setting.", "includeIf gitdir patterns need a trailing slash to match subdirectories.", "Shell aliases (!) run from the top of the repository, not the current directory."],
        [
            qa("basic", "What are Git's config levels and their precedence?", "System (all users), global (your user), local (one repo) and worktree (one worktree). More specific levels override broader ones, and git -c key=value on the command line overrides them all."),
            qa("basic", "How do you find out why a setting has a particular value?", "Run git config --show-origin --show-scope --get-all <key> or --list. It prints the file and scope for each value, so you can see which level wins."),
            qa("intermediate", "How do you use a different email for work repositories automatically?", "Add an [includeIf \"gitdir:~/work/\"] section to the global config that includes a second file setting user.email (and optionally a signing key). It applies to every repo under that path."),
            qa("intermediate", "What is the difference between a normal alias and one starting with !?", "A normal alias expands to Git arguments (alias.st = status -sb). A ! alias runs an arbitrary shell command, which allows pipes and multiple git commands, and it runs from the repository root."),
        ],
        ["three-trees", "workflows"],
        chain(
            ("System", "/etc/gitconfig", "System level", "Machine-wide defaults for all users, rarely edited."),
            ("Global", "~/.gitconfig", "Global level", "Your identity, aliases and preferences; overrides system.", "override"),
            ("Local", ".git/config", "Local level", "Per-repository remotes, branches and overrides; wins over global.", "override"),
            ("Command -c", "git -c k=v", "One-off override", "git -c sets a value for a single command and beats every file.", "override"),
        ),
    ),
    topic(
        "gitignore-attributes", ".gitignore & .gitattributes", "basics", "basic", "GA",
        "Keep junk out of the repo and tell Git how to treat each kind of file.",
        "A bouncer list at the door (.gitignore) and care labels sewn into clothes (.gitattributes): one decides what gets in, the other how it is washed.",
        ".gitignore lists patterns for untracked files Git should not offer to add, such as build output, dependency folders, editor files and local environment files. Patterns are relative to the .gitignore's directory; a leading / anchors to that directory, a trailing / matches only directories, ** matches across directories and ! re-includes a path. Ignore rules never affect files that are already tracked; you must git rm --cached them first. Personal patterns belong in .git/info/exclude or a global core.excludesFile rather than the shared .gitignore. .gitattributes assigns attributes to paths: line-ending normalisation (text=auto, eol=lf), binary handling, custom diff drivers, merge strategies such as merge=ours, export-ignore for git archive, and filter=lfs for Git LFS. git check-ignore -v and git check-attr explain which rule applied to a path.",
        ["Excluding node_modules, build directories and .env files.", "Normalising line endings across Windows, macOS and Linux contributors.", "Marking generated or binary files so diffs and merges behave sensibly."],
        [
            ".gitignore only applies to untracked files.",
            "git check-ignore -v <path> shows the exact rule and file that matched.",
            "* text=auto plus explicit eol rules prevents CRLF churn.",
            "A parent directory that is ignored cannot be re-included with !.",
            "Commit .gitattributes so everyone gets the same behaviour.",
        ],
        [
            ex("A typical .gitignore", "basic", "Common patterns with anchors, directories and negation.", "bash", """
                cat > .gitignore <<'EOF'
                # dependencies and builds
                node_modules/
                /dist/
                *.log
                # local environment (keep the template)
                .env
                .env.*
                !.env.example
                EOF
                git check-ignore -v .env.local
            """, runnable=False),
            ex("Stop tracking an already committed file", "basic", "Ignore rules do nothing until the file leaves the index.", "bash", """
                echo "config/local.yml" >> .gitignore
                git rm --cached config/local.yml
                git commit -m "chore: stop tracking local config"
            """, runnable=False),
            ex("A .gitattributes file", "intermediate", "Line endings, binaries, generated files and LFS.", "bash", """
                cat > .gitattributes <<'EOF'
                * text=auto
                *.sh text eol=lf
                *.bat text eol=crlf
                *.png binary
                package-lock.json -diff linguist-generated
                *.psd filter=lfs diff=lfs merge=lfs -text
                docs/internal/ export-ignore
                EOF
                git add --renormalize .
            """, runnable=False),
        ],
        ["git check-ignore -v <path>", "git rm --cached <path>", "git status --ignored", "git check-attr -a <path>", "git add --renormalize ."],
        ["Adding a committed secret to .gitignore does not remove it from history.", "Ignoring a directory with dir/ means !dir/keep.txt cannot re-include files inside it; use dir/* instead.", "Changing eol attributes on an existing repo needs git add --renormalize or every file appears modified."],
        [
            qa("basic", "Why is a file still tracked after you added it to .gitignore?", "Ignore rules only apply to untracked files. Remove it from the index with git rm --cached <file> and commit; the file stays on disk and is ignored from then on."),
            qa("basic", "Where should personal ignore patterns go?", "In .git/info/exclude (this repo only) or the file named by core.excludesFile (all repos). The shared .gitignore should hold project-wide patterns only."),
            qa("intermediate", "What does * text=auto do in .gitattributes?", "It lets Git detect text files and normalise their line endings to LF in the repository, converting to the platform's native ending on checkout unless eol is set explicitly. This prevents whole-file diffs caused by CRLF/LF differences."),
            qa("intermediate", "Name three uses of .gitattributes beyond line endings.", "Marking files binary or -diff, assigning custom diff or merge drivers (e.g. merge=ours for generated files), export-ignore for git archive, and filter=lfs to store large files via Git LFS."),
        ],
        ["three-trees", "internals"],
        chain(
            ("New file", "untracked", "Untracked path", "A new file appears in the working tree."),
            ("Ignore rules", ".gitignore", "Ignore check", "Git checks .gitignore files, info/exclude and the global excludes file.", "match?"),
            ("Attributes", ".gitattributes", "Attributes", "For files that are added, attributes decide text/eol, diff and merge handling.", "attrs"),
            ("Index", "normalised blob", "Stored", "The normalised content is staged as a blob in the index.", "git add"),
        ),
    ),
    topic(
        "status-diff", "status & diff in Depth", "basics", "basic", "SD",
        "Read every column of git status and compare any two snapshots precisely.",
        "A before-and-after photo with red and green highlights, and the ability to choose which two photos to compare.",
        "git status compares HEAD, the index and the working tree; git status -sb prints a two-column code where the first column is the index versus HEAD and the second is the working tree versus the index (for example M_ staged, _M unstaged, ?? untracked). git diff with no arguments shows unstaged changes, git diff --staged shows what will be committed, and git diff HEAD shows both together. git diff A B compares two commits, and git diff A...B compares B with the merge base of A and B, which is exactly what a pull request shows. --stat, --name-only and --name-status summarise; -w ignores whitespace, --word-diff highlights changed words and --color-moved marks moved blocks. Different algorithms such as --histogram or --patience can produce more readable diffs for reordered code. git difftool opens an external visual diff tool.",
        ["Reviewing exactly what will be committed before committing.", "Seeing what a feature branch changes relative to main.", "Hiding whitespace noise when reviewing reformatted code."],
        [
            "status -s columns: left = staged, right = unstaged.",
            "diff (unstaged), diff --staged (staged), diff HEAD (both).",
            "A..B in diff means A B; A...B means merge-base(A,B) to B.",
            "--stat and --name-status give a quick overview.",
            "-w and --color-moved make refactors readable.",
        ],
        [
            ex("Three ways to diff", "basic", "Unstaged, staged and everything since the last commit.", "bash", """
                git status -sb
                # ## main...origin/main [ahead 1]
                # M  app.py      <- staged
                #  M utils.py    <- modified, not staged
                # ?? notes.txt   <- untracked
                git diff
                git diff --staged
                git diff HEAD
            """, runnable=False),
            ex("What a PR changes", "intermediate", "Three dots compare against the merge base.", "bash", """
                git fetch origin
                git diff --stat origin/main...feature/login
                git diff origin/main...feature/login -- src/
                git diff -w --color-moved origin/main...HEAD
            """, runnable=False),
        ],
        ["git status -sb", "git diff --staged", "git diff A...B", "git diff --stat · --name-status", "git diff -w --word-diff", "git difftool"],
        ["git diff shows nothing for new untracked files; stage them or use git add -N.", "Two dots and three dots mean different things in diff and in log.", "Whitespace-only changes can hide in a large diff unless you review with and without -w."],
        [
            qa("basic", "What do the two columns in git status -s mean?", "The first column is the index compared with HEAD (staged changes) and the second is the working tree compared with the index (unstaged changes). ?? marks untracked files."),
            qa("basic", "How do you see what will go into the next commit?", "git diff --staged (alias --cached) compares the index with HEAD, which is exactly the content of the next commit."),
            qa("intermediate", "What is the difference between git diff main..feature and main...feature?", "Two dots compares the two tips directly, so changes made on main also show up (inverted). Three dots compares feature against the merge base, showing only what the feature branch introduced, like a pull request view."),
            qa("intermediate", "How would you review a commit that mixes reformatting with logic changes?", "Use git diff -w (or --ignore-all-space) to hide whitespace, --color-moved to highlight moved blocks and --word-diff for small changes. Better still, ask for the formatting to be split into a separate commit."),
        ],
        ["three-trees", "merging"],
        chain(
            ("Working tree", "files on disk", "Edits", "Your files differ from the index: git diff shows this."),
            ("Index", "staged snapshot", "Staged", "git diff --staged compares the index with HEAD.", "diff"),
            ("HEAD", "last commit", "HEAD", "git diff HEAD compares the working tree straight with the last commit.", "--staged"),
            ("Merge base", "common ancestor", "A...B", "git diff A...B starts from the merge base, showing only B's work.", "A...B"),
        ),
    ),
    topic(
        "staging-hunks", "Staging Hunks (add -p)", "basics", "intermediate", "SH",
        "Split messy work into clean, focused commits one hunk at a time.",
        "Sorting a mixed pile of laundry into separate loads instead of throwing everything in one machine.",
        "git add -p (patch mode) walks through each hunk of your unstaged changes and asks what to do: y stages it, n skips it, s splits it into smaller hunks, e opens it in an editor so you can stage individual lines, and q quits. This lets you turn an afternoon of mixed work into several atomic commits, each doing one thing. New files are not shown in patch mode until you mark them with git add -N (intent to add), which adds an empty entry to the index. The same interface exists in reverse: git restore -p --staged unstages hunks, git restore -p discards working-tree hunks, git stash -p stashes only selected hunks and git commit -p stages and commits in one go. Always finish with git diff --staged to confirm the commit contains exactly what you intended. GUI tools and IDEs offer the same line-level staging if you prefer a visual approach.",
        ["Separating a bug fix from an unrelated refactor made in the same file.", "Leaving debug prints out of a commit.", "Building a reviewable series of small commits."],
        [
            "y/n/s/e/q: stage, skip, split, edit, quit.",
            "git add -N makes new files visible to patch mode.",
            "restore -p --staged unstages hunks; restore -p discards them.",
            "stash -p and commit -p share the same interface.",
            "Verify with git diff --staged before committing.",
        ],
        [
            ex("Two commits from one file", "intermediate", "Stage the fix, commit it, then commit the refactor.", "bash", """
                git add -p src/orders.py
                # Stage this hunk [y,n,q,a,d,s,e,?]? y   (the null check fix)
                # Stage this hunk [y,n,q,a,d,s,e,?]? n   (the rename refactor)
                git diff --staged
                git commit -m "fix(orders): guard against missing customer"
                git add src/orders.py
                git commit -m "refactor(orders): rename helper for clarity"
            """, runnable=False),
            ex("Patch mode for new files and undo", "intermediate", "Intent-to-add, then unstage a hunk by mistake.", "bash", """
                git add -N src/new_module.py
                git add -p src/new_module.py
                git restore -p --staged src/new_module.py
                git stash push -p -m "debug logging"
            """, runnable=False),
        ],
        ["git add -p [path]", "git add -N <new-file>", "git restore -p --staged", "git restore -p", "git stash push -p", "git commit -p"],
        ["Staging part of a file means the committed version was never run or tested as a whole; run tests on the staged state if it matters.", "e (edit) mode fails if you break the hunk header; delete lines with - or turn - into space instead of editing context.", "git restore -p without --staged throws away working-tree changes permanently."],
        [
            qa("basic", "What does git add -p do?", "It presents each change hunk interactively and lets you stage, skip, split or edit it, so a commit can contain only part of a file's changes."),
            qa("intermediate", "Why doesn't a new file show up in git add -p?", "Patch mode works on differences between the index and working tree, and an untracked file has no index entry. git add -N records an empty intent-to-add entry so the whole file appears as hunks."),
            qa("intermediate", "How do you unstage just one hunk?", "git restore -p --staged <file> (or the older git reset -p). It walks staged hunks and lets you remove selected ones from the index without touching the working tree."),
            qa("advanced", "What is a risk of committing partial files, and how do you mitigate it?", "The committed snapshot may never have been built or tested because the working tree contains extra changes. Mitigate by stashing unstaged changes with git stash --keep-index, running tests, then popping the stash."),
        ],
        ["three-trees", "stash-cherry-pick", "interactive-rebase"],
        chain(
            ("Mixed edits", "fix + refactor", "Messy working tree", "One file contains a bug fix and an unrelated rename."),
            ("Hunk review", "y / n / s / e", "Patch mode", "git add -p shows each hunk; you answer y for the fix and n for the rename.", "add -p"),
            ("Index", "fix only", "Partial stage", "Only the fix hunks are in the index; diff --staged confirms it.", "y"),
            ("Commit 1", "fix(orders)", "First commit", "Commit the fix alone.", "commit"),
            ("Commit 2", "refactor", "Second commit", "Stage and commit the remaining rename as its own commit.", "commit"),
        ),
    ),
    topic(
        "commit-messages", "Commit Messages & Conventional Commits", "basics", "basic", "CM",
        "Write messages that explain why, and structure them so tools can read them.",
        "A commit message is a note to a future teammate at 2 a.m. during an outage. Make it the note you would want to find.",
        "A good commit message has a short summary line (about 50 characters, imperative mood such as 'Add retry to payment client'), a blank line, and a body wrapped near 72 columns that explains why the change was needed and any trade-offs. The diff already shows what changed; the message should capture intent and context. Conventional Commits adds a machine-readable prefix: type(scope): summary, where type is feat, fix, docs, refactor, perf, test, build, ci or chore. A ! after the type or a BREAKING CHANGE: footer marks an incompatible change. Tools use these to generate changelogs and decide semantic version bumps automatically (fix -> patch, feat -> minor, breaking -> major). Trailers at the end, like Co-authored-by:, Signed-off-by: (added by git commit -s for a DCO) and Refs: #123, are parsed by Git and hosting platforms. commitlint in a commit-msg hook or CI can enforce the format.",
        ["Generating release notes automatically.", "Making git log and git blame useful during incidents.", "Enforcing a consistent style across a large team."],
        [
            "Summary: imperative, short, no trailing period.",
            "Body explains why, not what.",
            "feat -> minor, fix -> patch, ! or BREAKING CHANGE -> major.",
            "Trailers: Co-authored-by, Signed-off-by, Refs.",
            "Enforce with a commit-msg hook or a CI check.",
        ],
        [
            ex("A well-formed message", "basic", "Summary, body and trailers.", "bash", """
                git commit -F - <<'EOF'
                fix(payments): retry idempotent charge on timeout

                The provider occasionally times out after accepting a charge.
                Retrying with the same idempotency key is safe and avoids
                customers seeing a failed checkout for a successful payment.

                Refs: #482
                Co-authored-by: Grace Hopper <grace@example.com>
                EOF
            """, runnable=False),
            ex("Breaking change and DCO sign-off", "intermediate", "Mark incompatibility and sign off.", "bash", """
                git commit -s -m "feat(api)!: remove deprecated v1 endpoints" -m "BREAKING CHANGE: clients must use /v2."
                git log -1 --format=%B
                git interpret-trailers --parse < .git/COMMIT_EDITMSG
            """, runnable=False),
        ],
        ["git commit (opens editor)", "git commit -m \"type(scope): summary\"", "git commit -s", "git commit --amend", "git log --format=%B -1"],
        ["Messages like 'fix stuff' or 'wip' make history useless for blame and bisect.", "Squash merges discard individual messages unless the PR title follows the convention.", "Signed-off-by is a DCO statement, not a cryptographic signature."],
        [
            qa("basic", "What makes a good commit message?", "A concise imperative summary line, a blank line, then a body explaining why the change was made and any context the diff cannot show. One logical change per commit."),
            qa("basic", "What is Conventional Commits?", "A specification for messages of the form type(scope): description, with types like feat and fix and a BREAKING CHANGE marker. It makes history machine-readable for changelogs and semantic versioning."),
            qa("intermediate", "How do Conventional Commits map to semantic versions?", "fix triggers a patch bump, feat a minor bump, and any commit with ! or a BREAKING CHANGE footer a major bump. Tools such as semantic-release or release-please compute the next version from commits since the last tag."),
            qa("intermediate", "What is the difference between Signed-off-by and a signed commit?", "Signed-off-by is a text trailer certifying the Developer Certificate of Origin. A signed commit carries a cryptographic SSH or GPG signature that proves who created it and that it was not altered."),
        ],
        ["three-trees", "interactive-rebase", "workflows"],
        chain(
            ("Change", "one logical fix", "Atomic change", "Stage a single focused change."),
            ("Message", "type(scope): msg", "Write message", "Summary line plus a body that explains why.", "commit"),
            ("Lint", "commit-msg hook", "Validate", "commitlint checks the format locally or in CI.", "check"),
            ("Changelog", "grouped by type", "Release notes", "Tools group feat and fix commits into a changelog.", "parse"),
            ("Version", "semver bump", "Bump", "Breaking -> major, feat -> minor, fix -> patch.", "tag"),
        ),
    ),
    topic(
        "log-search", "log & History Search", "history", "intermediate", "LS",
        "Filter history by author, date, message, path or the code that changed.",
        "A library catalogue: you can search by author, date and title, and pickaxe lets you search inside the pages for when a sentence first appeared.",
        "git log walks the commit graph from the given refs and prints commits in reverse chronological order. Filters narrow it down: --author, --since/--until, --grep for message text, and -- <path> for commits touching a path (add --follow to track renames of a single file). Range syntax selects sets: main..feature shows commits on feature not on main, and A...B shows commits on either side but not both. The pickaxe -S'text' finds commits that changed the number of occurrences of a string (added or removed it), while -G'regex' finds commits whose diff lines match a regex. git log -L :funcname:file or -L 10,20:file shows the evolution of a function or line range. --first-parent follows only the mainline of merges, --merges/--no-merges filter by type, and -p shows patches. git shortlog -sn summarises by author and git grep searches file contents at any revision.",
        ["Finding when a config key or function was introduced or removed.", "Listing what will be released: commits since the last tag.", "Tracing the history of one function during debugging."],
        [
            "main..feature = reachable from feature but not main.",
            "-S counts occurrences; -G matches changed lines by regex.",
            "-L :func:file follows a function over time.",
            "--first-parent gives a clean mainline view of merge-based history.",
            "git grep <pattern> <rev> searches a whole snapshot quickly.",
        ],
        [
            ex("Pickaxe and line history", "intermediate", "When was this string added or removed?", "bash", """
                git log -S"MAX_RETRIES" --oneline
                git log -G"timeout\\s*=" -p -- config/
                git log -L :charge_card:src/payments.py
                git log --follow --oneline -- docs/guide.md
            """, runnable=False),
            ex("Filters and ranges", "intermediate", "What is in this release, by whom?", "bash", """
                git log --oneline v2.3.0..main
                git log --oneline --no-merges --author="ada" --since="2 weeks ago"
                git log --first-parent --oneline main
                git shortlog -sn v2.3.0..main
                git grep -n "feature_flag" v2.3.0 -- src/
            """, runnable=False),
        ],
        ["git log --oneline --graph --all", "git log -S<string> · -G<regex>", "git log -L :func:file", "git log A..B · A...B", "git log --grep=<text> --author=<a>", "git shortlog -sn"],
        ["-S does not report commits that only move a string around (occurrence count unchanged); use -G for that.", "--follow works for a single file path only.", "Dates filter by committer date by default, which rebases change."],
        [
            qa("intermediate", "What is the pickaxe in git log?", "git log -S<string> finds commits where the number of occurrences of the string changed, i.e. where it was introduced or removed. -G<regex> is broader and matches any added or removed line matching the regex."),
            qa("intermediate", "How do you list commits on a feature branch that are not in main?", "git log main..feature (or git log feature ^main). Two dots in log mean reachable from the right side but not from the left."),
            qa("intermediate", "How do you see the history of a single function?", "git log -L :function_name:path/to/file, which uses the language's funcname patterns to track the function's line range and shows each change to it. -L start,end:file works for explicit ranges."),
            qa("advanced", "Why use --first-parent?", "In a merge-based workflow the first parent of each merge on main is the previous mainline commit. Following only first parents shows one entry per merged feature, which is the readable release history and is also useful with bisect."),
        ],
        ["bisect-reflog", "internals", "merging"],
        chain(
            ("Refs", "main, v2.3.0", "Starting points", "log starts from the refs you name and excludes those prefixed with ^ or before .."),
            ("Graph walk", "parents", "Walk", "Git walks parent pointers through the commit graph.", "walk"),
            ("Filters", "author, -S, path", "Filter", "Each commit is tested against author, date, message, path and pickaxe filters.", "test"),
            ("Output", "--oneline / -p", "Format", "Matching commits are printed with the chosen format.", "print"),
        ),
    ),
    topic(
        "blame", "blame & Annotate", "history", "intermediate", "BL",
        "Find the commit that last touched each line, then read why it changed.",
        "Asking who last repainted each brick in a wall: useful, as long as you then read the work order rather than blaming the painter.",
        "git blame <file> annotates every line with the commit, author and date that last modified it. -L limits it to a line range or function, -w ignores whitespace changes, and -M / -C detect lines moved within a file or copied from other files so the original commit is found instead of the refactor. Large formatting commits pollute blame; list their hashes in a .git-blame-ignore-revs file and set blame.ignoreRevsFile so blame looks past them (GitHub honours the same file). Blame shows the last change, not the original author, so the next step is git show <commit> or git log -L to read the context and linked issue. git blame <rev> -- <file> blames an older version, which helps you step further back. IDEs show the same information inline.",
        ["Finding the commit and PR that introduced a puzzling line.", "Identifying who to ask about a piece of code.", "Skipping a mass reformat to see meaningful history."],
        [
            "blame shows the last change per line, not the original author.",
            "-w, -M and -C reduce noise from whitespace and moved code.",
            ".git-blame-ignore-revs hides formatting-only commits.",
            "Follow up with git show or git log -L.",
            "Use it to find context, not to assign fault.",
        ],
        [
            ex("Targeted blame", "intermediate", "A range, ignoring whitespace and following moves.", "bash", """
                git blame -L 40,60 src/payments.py
                git blame -w -M -C src/payments.py
                git blame -L :charge_card src/payments.py
                git show 3f2a9c1
            """, runnable=False),
            ex("Ignore a formatting commit", "intermediate", "Keep blame useful after running a formatter.", "bash", """
                echo "9b1d7e0c4a5f2e3d1c0b9a8f7e6d5c4b3a2f1e0d  # black reformat" >> .git-blame-ignore-revs
                git config blame.ignoreRevsFile .git-blame-ignore-revs
                git blame src/payments.py
            """, runnable=False),
        ],
        ["git blame <file>", "git blame -L <start>,<end> <file>", "git blame -w -M -C <file>", "git config blame.ignoreRevsFile .git-blame-ignore-revs", "git blame <rev> -- <file>"],
        ["A reformat or file move makes blame point at the wrong commit unless you use -M/-C or ignore revs.", "The person shown may only have moved the code; read the commit before drawing conclusions.", "Squash merges collapse many authors into one commit."],
        [
            qa("basic", "What does git blame show?", "For each line, the commit that last changed it, with author and timestamp. It is a starting point for finding the commit and discussion behind a line."),
            qa("intermediate", "How do you stop a mass reformat from dominating blame?", "Put the formatting commit hashes in .git-blame-ignore-revs and set blame.ignoreRevsFile to it (or pass --ignore-rev). Blame then attributes lines to the previous meaningful change."),
            qa("intermediate", "What do -M and -C do?", "-M detects lines moved within the same file and -C detects lines moved or copied from other files in the same commit. Blame then reports the commit where the code was originally written rather than where it was moved."),
            qa("intermediate", "Blame points at a refactor commit. How do you look further back?", "Run git blame <commit>^ -- <file> to blame the version before that commit, or use git log -L on the line range to see every change in sequence."),
        ],
        ["bisect-reflog", "three-trees"],
        chain(
            ("File", "src/payments.py", "Pick a file", "Choose the file and optionally a line range."),
            ("Annotate", "line -> commit", "Blame", "Git walks history to find the last commit that touched each line.", "blame"),
            ("Skip noise", "ignore-revs, -w", "Filter", "Formatting commits and whitespace changes are skipped.", "skip"),
            ("Commit", "git show", "Read context", "Open the commit to read its message, diff and linked issue.", "show"),
        ),
    ),
    topic(
        "tags", "Tags: Lightweight, Annotated & Signed", "history", "basic", "TG",
        "Name important commits, usually releases, with fixed labels.",
        "A branch is a bookmark you keep moving; a tag is an engraved plaque bolted to one page.",
        "A tag is a ref under refs/tags/ that names a commit and, by convention, never moves. A lightweight tag is just a ref pointing straight at a commit. An annotated tag (git tag -a) is a real tag object with a tagger, date and message, and the ref points to that object. A signed tag (git tag -s) is an annotated tag with a GPG or SSH signature, verified with git tag -v. git describe uses annotated tags to produce names like v2.3.0-14-g3f2a9c1 for builds. Tags are not pushed by default: push them with git push origin v2.3.0, or use --follow-tags to push annotated tags reachable from pushed commits. Deleting a tag remotely uses git push origin --delete v2.3.0. Moving a published tag breaks everyone who already fetched it, so cut a new version instead.",
        ["Marking release versions for builds and deployments.", "Providing a verifiable signed release point.", "Generating version strings with git describe."],
        [
            "Lightweight = ref only; annotated = tag object with metadata.",
            "Prefer annotated tags for releases; they work with describe and --follow-tags.",
            "Tags must be pushed explicitly.",
            "Never move a published tag; release a new version.",
            "git tag -v verifies a signed tag.",
        ],
        [
            ex("Create and push release tags", "basic", "Annotated tag on the release commit.", "bash", """
                git tag -a v2.3.0 -m "Release 2.3.0"
                git tag -n
                git push origin v2.3.0
                git push --follow-tags
                git describe --tags
            """, runnable=False),
            ex("Signed tags and cleanup", "intermediate", "Sign, verify, and delete a mistaken tag.", "bash", """
                git tag -s v2.3.1 -m "Release 2.3.1"
                git tag -v v2.3.1
                git tag -d v2.3.1-rc
                git push origin --delete v2.3.1-rc
                git ls-remote --tags origin
            """, runnable=False),
        ],
        ["git tag -a v1.0.0 -m \"msg\"", "git tag -s v1.0.0", "git push origin <tag> · --follow-tags", "git tag -d <tag>", "git describe --tags"],
        ["git push without --tags or --follow-tags leaves your tags local only.", "Re-tagging the same name after people fetched it leaves them on the old commit; Git will not overwrite existing tags on fetch without --force.", "Lightweight tags are ignored by git describe unless you pass --tags."],
        [
            qa("basic", "Lightweight vs annotated tag?", "A lightweight tag is just a ref to a commit. An annotated tag is a stored object with tagger, date, message and optional signature; use annotated tags for releases."),
            qa("basic", "Why didn't your tag appear on the remote after git push?", "Tags are not pushed with branches by default. Push it explicitly (git push origin v1.0.0) or use git push --follow-tags for annotated tags reachable from pushed commits."),
            qa("intermediate", "What does git describe output?", "The nearest annotated tag, the number of commits since it, and an abbreviated hash, e.g. v2.3.0-14-g3f2a9c1. Build systems use it as a version string."),
            qa("intermediate", "You tagged the wrong commit and already pushed. What do you do?", "If anyone may have fetched it, publish a new version instead of moving the tag. If it truly was not consumed, delete it locally and remotely, recreate it, and tell anyone who fetched it to delete their local copy."),
        ],
        ["branches", "internals", "workflows"],
        chain(
            ("Commit", "release-ready", "Release commit", "main is green and ready to ship."),
            ("Tag object", "v2.3.0 + msg", "Annotate", "git tag -a creates a tag object with tagger and message.", "tag -a"),
            ("Signature", "SSH or GPG", "Sign", "git tag -s adds a signature anyone can verify.", "sign"),
            ("Remote", "refs/tags/v2.3.0", "Publish", "git push origin v2.3.0 publishes it; CI can build from it.", "push"),
        ),
    ),
    topic(
        "format-patch", "Patches: format-patch, am & apply", "history", "advanced", "FM",
        "Exchange commits as email-ready patch files and apply them with authorship intact.",
        "Mailing someone a recipe card with your name on it, instead of shouting the ingredient changes across the room.",
        "git format-patch turns commits into numbered .patch files in mbox format, each containing the author, date, message and diff. git am applies such patches as real commits, preserving the original author and message, and can use --3way to fall back to a three-way merge when context has drifted. git apply applies a plain diff to the working tree (and optionally the index) without creating a commit; --check tests whether it applies cleanly. git diff > fix.diff is quick but loses authorship and messages, so prefer format-patch for commits. Projects like the Linux kernel and Git itself accept patches by email via git send-email. git range-diff compares two versions of a patch series, which reviewers use to see what changed between v1 and v2. Patches are also handy for moving work between air-gapped machines or unrelated repositories.",
        ["Contributing to mailing-list based projects.", "Moving commits between repositories that share no remote.", "Sharing a fix with someone who cannot pull from you."],
        [
            "format-patch keeps author, date and message; diff does not.",
            "git am creates commits; git apply only changes files.",
            "git apply --check and git am --3way handle drift.",
            "git am --abort / --continue mirror rebase.",
            "range-diff compares revisions of a patch series.",
        ],
        [
            ex("Export and apply a series", "advanced", "Three commits as patches, applied elsewhere.", "bash", """
                git format-patch origin/main..feature -o outgoing/
                # outgoing/0001-fix-parse-empty-header.patch ...
                cd ../other-repo
                git am --3way ../app/outgoing/*.patch
                git log --oneline -3
            """, runnable=False),
            ex("Plain diffs and series comparison", "advanced", "Apply a diff without committing; compare series versions.", "bash", """
                git diff > hotfix.diff
                git apply --check hotfix.diff
                git apply --index hotfix.diff
                git range-diff main feature-v1 feature-v2
            """, runnable=False),
        ],
        ["git format-patch -3 · A..B", "git am --3way *.patch", "git am --abort · --continue", "git apply --check file.diff", "git range-diff A B C", "git send-email"],
        ["git apply refuses partial application by default; use --reject or --3way to see what failed.", "Line-ending or whitespace changes in transit (email clients) corrupt patches.", "Applying a plain diff loses the original author; use git am with format-patch output."],
        [
            qa("intermediate", "git apply vs git am?", "git apply applies a diff to the working tree (and index with --index) without making a commit. git am reads mbox patches from format-patch and creates commits with the original author, date and message."),
            qa("intermediate", "Why prefer format-patch over git diff for sharing commits?", "format-patch includes the commit metadata and message and produces one file per commit, so the receiver reproduces the exact series with git am. A plain diff is anonymous and collapses everything into one change."),
            qa("advanced", "A patch no longer applies cleanly. What can you do?", "Use git am --3way so Git uses the blob ids in the patch to do a three-way merge, then resolve conflicts and git am --continue. Alternatively git apply --reject writes .rej files for the failed hunks."),
            qa("advanced", "What is git range-diff for?", "It compares two ranges of commits, pairing up corresponding commits and showing the diff between their diffs. Reviewers use it to see exactly what changed between version 1 and version 2 of a rebased patch series."),
        ],
        ["stash-cherry-pick", "remotes", "workflows"],
        chain(
            ("Commits", "feature branch", "Series", "Three commits on a feature branch."),
            ("Patch files", "0001-*.patch", "Export", "git format-patch writes one mbox file per commit.", "format-patch"),
            ("Transport", "email / file", "Send", "Send by email (send-email) or copy the files.", "send"),
            ("git am", "3-way fallback", "Apply", "git am applies each patch, using a three-way merge if needed.", "am"),
            ("Commits", "same author/msg", "Result", "Equivalent commits with original authorship exist in the target repo.", "commit"),
        ),
    ),
]

TOPICS += [
    topic(
        "refs-refspecs", "Refs & Refspecs", "internals", "advanced", "RF",
        "Branches, tags and remote branches are all refs; refspecs map them between repos.",
        "Refs are name tags on parcels in a warehouse; a refspec is the shipping rule saying which tagged parcels go to which shelf in the other warehouse.",
        "A ref is a name that resolves to an object id: refs/heads/* are local branches, refs/tags/* tags, refs/remotes/<remote>/* remote-tracking branches, and refs/notes/* or refs/stash hold other data. HEAD is a symbolic ref that usually points to another ref. Refs live as loose files under .git/refs or in .git/packed-refs (newer Git versions can also use the reftable backend). A refspec has the form [+]<src>:<dst>; the default fetch refspec +refs/heads/*:refs/remotes/origin/* copies every remote branch into your remote-tracking namespace, and the leading + allows non-fast-forward updates. Push refspecs work the other way: git push origin feature:refs/heads/review/feature pushes a local branch under a different name, and git push origin :old deletes old. Hosting platforms expose extra refs such as GitHub's refs/pull/<n>/head, which you can fetch with a custom refspec. Plumbing commands show-ref, update-ref and symbolic-ref read and write refs safely.",
        ["Fetching pull request heads locally for review.", "Pushing to a differently named branch or to Gerrit's refs/for/main.", "Narrowing fetches to only the branches you need."],
        [
            "Ref namespaces: heads, tags, remotes, notes, stash.",
            "HEAD is a symbolic ref; detached HEAD holds a raw id.",
            "Refspec: [+]src:dst; + permits non-fast-forward updates.",
            "An empty source in a push refspec deletes the destination.",
            "Use update-ref rather than editing ref files by hand.",
        ],
        [
            ex("Inspect refs", "advanced", "See every ref and what HEAD points to.", "bash", """
                git show-ref --heads --tags
                git symbolic-ref HEAD
                git rev-parse origin/main
                cat .git/packed-refs | head
                git for-each-ref --sort=-committerdate --format="%(refname:short) %(committerdate:relative)" refs/heads
            """, runnable=False),
            ex("Custom refspecs", "advanced", "Fetch PR heads and push under another name.", "bash", """
                git fetch origin "+refs/pull/*/head:refs/remotes/origin/pr/*"
                git switch --detach origin/pr/482
                git config --add remote.origin.fetch "+refs/pull/*/head:refs/remotes/origin/pr/*"
                git push origin HEAD:refs/heads/review/payments-retry
                git push origin :refs/heads/old-experiment
            """, runnable=False),
        ],
        ["git show-ref", "git for-each-ref refs/heads", "git symbolic-ref HEAD", "git update-ref refs/heads/x <sha>", "git fetch origin \"+src:dst\"", "git push origin src:dst"],
        ["Hand-editing ref files bypasses the reflog and locking.", "A + on a fetch refspec silently overwrites a remote-tracking ref after a force-push, which is intended but surprising.", "A branch and a tag with the same name make short names ambiguous."],
        [
            qa("intermediate", "What is a ref?", "A human-readable name stored under .git/refs (or packed-refs) that resolves to an object id, usually a commit. Branches, tags, remote-tracking branches and the stash are all refs in different namespaces."),
            qa("advanced", "Explain the refspec +refs/heads/*:refs/remotes/origin/*.", "On fetch, every branch on the remote (source) is written to a matching remote-tracking ref locally (destination). The + allows updating them even when the remote history was rewritten (non-fast-forward)."),
            qa("advanced", "How do you push a local branch to a remote branch with a different name?", "git push origin local-name:remote-name, for example git push origin HEAD:refs/heads/review/x. Fully qualified destinations avoid ambiguity with tags."),
            qa("advanced", "How do you delete a remote branch using a refspec?", "Push an empty source: git push origin :branch-name. The friendlier form git push origin --delete branch-name does the same thing."),
        ],
        ["internals", "remotes", "branches"],
        chain(
            ("Remote refs", "refs/heads/*", "Source", "The remote advertises its branches as refs/heads/*."),
            ("Refspec", "+src:dst", "Mapping rule", "The fetch refspec maps each source ref to a destination pattern.", "match"),
            ("Tracking refs", "refs/remotes/o/*", "Destination", "Local remote-tracking refs are created or updated.", "update"),
            ("HEAD", "-> refs/heads/main", "Symbolic ref", "Your HEAD still points to your own local branch, unchanged.", "resolve"),
        ),
    ),
    topic(
        "fetch-vs-pull", "fetch vs pull", "collab", "basic", "FP",
        "fetch downloads; pull downloads and then integrates into your branch.",
        "fetch is checking the mailbox and reading the letters; pull is reading them and immediately rewriting your plans to match.",
        "git fetch contacts a remote, downloads new objects and updates remote-tracking refs such as origin/main, but never touches your local branches or working tree. That makes it always safe: you can then inspect what arrived with git log HEAD..origin/main or git diff HEAD...origin/main. git pull is git fetch followed by integrating the upstream branch into the current branch, either with a merge (the historical default) or a rebase if pull.rebase is true or you pass --rebase. Modern Git warns when your branch and upstream have diverged and no strategy is configured; pull.ff=only refuses anything but a fast-forward. git fetch --prune removes remote-tracking refs for branches deleted on the remote, and fetch.prune=true makes that automatic. git fetch --all updates every remote. Fetching often and integrating deliberately keeps surprises small.",
        ["Checking what teammates pushed before integrating.", "Updating many remote-tracking branches without switching.", "Keeping local main current with a fast-forward-only pull."],
        [
            "fetch updates origin/* only; it is always safe.",
            "pull = fetch + merge (or rebase).",
            "pull.ff=only or pull.rebase=true makes behaviour explicit.",
            "--prune removes stale remote-tracking refs.",
            "Inspect with git log HEAD..@{u} before integrating.",
        ],
        [
            ex("Fetch, inspect, integrate", "basic", "See incoming commits before merging them.", "bash", """
                git fetch origin
                git status -sb
                git log --oneline HEAD..origin/main
                git diff HEAD...origin/main --stat
                git merge --ff-only origin/main
            """, runnable=False),
            ex("Configure pull behaviour", "basic", "Choose one integration strategy explicitly.", "bash", """
                git config --global pull.ff only
                # or: git config --global pull.rebase true
                git config --global fetch.prune true
                git pull
                git fetch --all --prune
            """, runnable=False),
        ],
        ["git fetch [remote]", "git fetch --all --prune", "git pull --ff-only", "git pull --rebase", "git log HEAD..@{u}"],
        ["Running pull on a branch with local commits can create unexpected merge commits.", "Stale origin/* branches linger without --prune.", "pull applies to the current branch only; other local branches stay behind their upstreams."],
        [
            qa("basic", "What is the difference between git fetch and git pull?", "fetch downloads objects and updates remote-tracking refs without changing your branches or files. pull runs fetch and then merges or rebases the upstream branch into the current branch."),
            qa("basic", "Why is fetch considered safe?", "It only writes new objects and updates refs under refs/remotes, so your local branches, index and working tree are untouched. You decide afterwards how to integrate."),
            qa("intermediate", "How do you see what a pull would bring in before doing it?", "git fetch, then git log HEAD..@{u} for incoming commits and git diff HEAD...@{u} for the changes. @{u} is the configured upstream of the current branch."),
            qa("intermediate", "What does pull.ff=only do?", "It makes git pull succeed only if it can fast-forward. If your branch has diverged it stops, so you choose to rebase or merge consciously instead of creating accidental merge commits."),
        ],
        ["remotes", "merging", "rebase"],
        chain(
            ("Remote", "new commits", "Remote moved", "A teammate pushed commits to origin/main."),
            ("Fetch", "objects + refs", "git fetch", "Objects download and origin/main moves; your main is untouched.", "fetch"),
            ("Inspect", "HEAD..origin/main", "Review", "Look at incoming commits and diffs before integrating.", "log"),
            ("Integrate", "merge or rebase", "git pull's 2nd half", "Merge, rebase or fast-forward your branch onto origin/main.", "merge"),
        ),
    ),
    topic(
        "pull-rebase", "pull --rebase", "collab", "intermediate", "PL",
        "Replay your unpushed commits on top of upstream instead of adding merge bubbles.",
        "Arriving late to a queue: instead of forming a parallel queue and merging later, you simply step in behind the last person.",
        "git pull --rebase fetches and then rebases your local commits that are not yet upstream onto the new upstream tip. The result is linear history without the small 'Merge branch main of origin' commits that plain pull creates when two people commit on the same branch. Set it as the default with pull.rebase=true, or per branch with branch.<name>.rebase. Git uses the reflog of the upstream ref (fork-point) so that if upstream itself was rebased, commits you already had are not replayed twice. --autostash (or rebase.autoStash=true) stashes uncommitted changes before the rebase and restores them after. pull.rebase=merges also preserves local merge commits by rebuilding them with --rebase-merges. Because only your unpushed commits are rewritten, it is consistent with the golden rule of rebasing. If a conflict occurs, resolve it, git add, and git rebase --continue, or git rebase --abort to return to where you started.",
        ["Committing directly on a shared branch with teammates.", "Keeping a feature branch in sync with main before review.", "Avoiding noisy merge bubbles in history."],
        [
            "Rewrites only local, unpushed commits.",
            "pull.rebase=true makes it the default.",
            "rebase.autoStash handles a dirty working tree.",
            "Conflicts are resolved per commit, then --continue.",
            "Fork-point detection copes with upstream rewrites.",
        ],
        [
            ex("Pull with rebase", "intermediate", "Local commits are replayed on the new upstream tip.", "bash", """
                git config --global pull.rebase true
                git config --global rebase.autoStash true
                git pull
                # Successfully rebased and updated refs/heads/main.
                git log --oneline --graph -5
            """, runnable=False),
            ex("Handling a conflict mid-rebase", "intermediate", "Resolve, continue or abort.", "bash", """
                git pull --rebase
                # CONFLICT (content): Merge conflict in app/settings.py
                git status
                git add app/settings.py
                git rebase --continue
                # or bail out entirely:
                git rebase --abort
            """, runnable=False),
        ],
        ["git pull --rebase", "git config pull.rebase true", "git config rebase.autoStash true", "git rebase --continue · --abort", "git pull --rebase=merges"],
        ["Rebasing a branch that others have pulled from still rewrites shared history.", "During a rebase, 'ours' is the upstream and 'theirs' is your commit, the reverse of merge.", "Long-running local branches can hit the same conflict in several commits; enable rerere."],
        [
            qa("basic", "What does git pull --rebase do?", "It fetches, then rebases your local commits that are not on the upstream branch on top of the updated upstream, giving linear history without a merge commit."),
            qa("intermediate", "Why is pull --rebase considered safe even though rebase rewrites history?", "It only rewrites your local commits that have not been pushed yet. Nobody else has them, so the golden rule (do not rewrite shared commits) is respected."),
            qa("intermediate", "What does rebase.autoStash do?", "Before rebasing it stashes uncommitted changes, runs the rebase, then reapplies the stash. Without it, rebase refuses to start on a dirty working tree."),
            qa("advanced", "During a pull --rebase conflict, what do --ours and --theirs refer to?", "Rebase replays your commits onto upstream, so 'ours' is the upstream base being built on and 'theirs' is the commit of yours being replayed. This is the reverse of a normal merge."),
        ],
        ["rebase", "remotes", "merging"],
        chain(
            ("Local commits", "L1, L2 unpushed", "Diverged", "You have L1 and L2; upstream gained U1."),
            ("Fetch", "origin/main = U1", "Fetch", "pull first fetches the new upstream tip.", "fetch"),
            ("Set aside", "L1, L2 saved", "Detach", "Your local commits are set aside as patches.", "save"),
            ("Replay", "L1', L2' on U1", "Rebase", "Each commit is re-applied on top of U1 with a new id.", "replay"),
            ("Linear", "no merge bubble", "Result", "History is linear and ready to push as a fast-forward.", "push"),
        ),
    ),
    topic(
        "force-with-lease", "push Options & --force-with-lease", "collab", "intermediate", "FL",
        "Push safely after a rewrite, and know the push flags that matter.",
        "--force is bulldozing a shared garden bed; --force-with-lease first checks that nobody planted anything since you last looked.",
        "git push sends commits and updates remote refs, and by default refuses non-fast-forward updates so you cannot discard others' work. After a rebase or amend you must force, but plain --force overwrites whatever is on the remote. --force-with-lease only succeeds if the remote ref still points where your remote-tracking ref says it did; if someone pushed in the meantime, the push is rejected. Its weakness is a background fetch (from an IDE) that silently advances origin/branch; --force-if-includes (Git 2.30+) adds a check that the remote tip is actually in your local reflog. Other useful options: -u sets upstream, --delete removes a remote branch, --follow-tags pushes annotated tags, --dry-run shows what would happen, --atomic makes multi-ref pushes all-or-nothing, and -o/--push-option passes server-side options (GitLab uses these to open merge requests or skip CI). Protected branches on the server should reject force pushes to main entirely.",
        ["Updating your own PR branch after an interactive rebase.", "Publishing a new branch with upstream tracking.", "Pushing a release branch and tag atomically."],
        [
            "Default push rejects non-fast-forward updates.",
            "--force-with-lease compares against your origin/<branch>.",
            "Add --force-if-includes to defeat background fetches.",
            "--atomic: all refs update or none do.",
            "Never force-push shared branches like main.",
        ],
        [
            ex("Safe force-push after rebase", "intermediate", "Lease-protected update of your own branch.", "bash", """
                git rebase -i origin/main
                git push --force-with-lease --force-if-includes
                # ! [rejected] feature -> feature (stale info)  <- someone pushed; fetch and look first
                git config --global alias.pushf "push --force-with-lease --force-if-includes"
            """, runnable=False),
            ex("Everyday push options", "basic", "Upstream, dry run, delete, atomic and push options.", "bash", """
                git push -u origin feature/login
                git push --dry-run
                git push origin --delete feature/old
                git push --atomic origin main v2.3.0
                git push -o merge_request.create -o ci.skip origin feature/login
            """, runnable=False),
        ],
        ["git push -u origin <branch>", "git push --force-with-lease", "git push --force-if-includes", "git push --atomic origin a b", "git push origin --delete <b>", "git push -o <option>"],
        ["--force-with-lease without an explicit expected value is defeated if something fetched in the background.", "git push --force with push.default=matching once forced every branch; be explicit about the branch.", "Force-pushing a PR branch hides previous review context on some platforms."],
        [
            qa("basic", "Why does git push reject your push with 'non-fast-forward'?", "The remote branch has commits your local branch does not contain, so updating it would discard them. Fetch and integrate (merge or rebase) first, then push."),
            qa("intermediate", "--force vs --force-with-lease?", "--force overwrites the remote ref unconditionally. --force-with-lease only overwrites it if it still equals the value you last fetched, so it refuses when someone else pushed in the meantime."),
            qa("advanced", "How can --force-with-lease still lose work, and what fixes it?", "If a tool fetches in the background, origin/branch already includes the teammate's commit and the lease check passes. --force-if-includes also verifies that the remote tip is reachable from your local reflog, or you can pass an explicit expected sha with --force-with-lease=branch:sha."),
            qa("intermediate", "What does git push --atomic guarantee?", "When pushing several refs, the server either updates all of them or none, so a branch and its release tag cannot end up half-published. The server must support the atomic capability."),
        ],
        ["rebase", "remotes", "interactive-rebase"],
        chain(
            ("Local", "rewritten branch", "After rebase", "Your branch has new commit ids after a rebase."),
            ("Lease check", "remote = expected?", "Compare", "Git asks the server to update only if the ref equals your origin/feature.", "expect"),
            ("Includes check", "in local reflog?", "Extra check", "--force-if-includes confirms you actually integrated that remote tip.", "verify"),
            ("Remote", "updated / rejected", "Outcome", "The ref is updated, or the push is rejected as stale.", "push"),
        ),
    ),
    topic(
        "upstream-tracking", "Upstream Tracking Branches", "collab", "basic", "UT",
        "Link a local branch to a remote branch so push, pull and status just work.",
        "A buddy system: each local branch knows exactly which remote branch it is paired with and can tell you how far apart you are.",
        "An upstream (tracking) relationship is stored in config as branch.<name>.remote and branch.<name>.merge. With it, plain git pull and git push know where to go, and git status reports 'ahead 2, behind 1' compared with the remote-tracking branch. git push -u origin feature sets the upstream while pushing, git branch -u origin/feature sets it for an existing branch, and git switch feature automatically creates a tracking branch if exactly one remote has a branch of that name. push.autoSetupRemote=true (Git 2.37+) makes the first git push create the upstream automatically. The shorthands @{u} (upstream) and @{push} (where push would go) work in any revision expression, such as git log @{u}.. for unpushed commits. git branch -vv lists every branch with its upstream and ahead/behind counts, and shows [gone] when the remote branch has been deleted. push.default=simple (the default) pushes the current branch to its upstream of the same name.",
        ["Seeing how far your branch is from the remote at a glance.", "Using plain git push and git pull without arguments.", "Cleaning up local branches whose remote was deleted."],
        [
            "Stored as branch.<name>.remote and branch.<name>.merge.",
            "git push -u or push.autoSetupRemote sets it the first time.",
            "@{u} and @{push} are usable revision shorthands.",
            "git branch -vv shows ahead/behind and [gone].",
            "Ahead/behind is relative to your last fetch.",
        ],
        [
            ex("Set and inspect upstream", "basic", "Several ways to link a branch.", "bash", """
                git push -u origin feature/login
                git branch -u origin/main main
                git config --global push.autoSetupRemote true
                git branch -vv
                git status -sb
            """, runnable=False),
            ex("Use @{u}", "intermediate", "Unpushed and incoming commits, plus cleanup of gone branches.", "bash", """
                git fetch --prune
                git log --oneline @{u}..        # commits you have not pushed
                git log --oneline ..@{u}        # commits you have not pulled
                git rev-list --left-right --count @{u}...HEAD
                git branch -vv | grep ': gone]'
            """, runnable=False),
        ],
        ["git push -u origin <branch>", "git branch -u origin/<branch>", "git branch -vv", "git log @{u}..", "git branch --unset-upstream"],
        ["Ahead/behind counts are stale until you fetch.", "A branch tracking the wrong remote branch pushes to the wrong place; check git branch -vv.", "Creating a branch from origin/main with --no-track leaves no upstream."],
        [
            qa("basic", "What is an upstream branch?", "The remote-tracking branch a local branch is linked to, stored in branch.<name>.remote and .merge. It is the default target for pull and push and the reference for ahead/behind counts."),
            qa("basic", "How do you set the upstream for a new branch?", "git push -u origin <branch> on the first push, or git branch -u origin/<branch> afterwards. With push.autoSetupRemote=true a plain git push does it automatically."),
            qa("intermediate", "How do you list commits you have not pushed yet?", "git log @{u}.. shows commits reachable from HEAD but not from the upstream. git log ..@{u} shows the reverse: commits on upstream you have not integrated."),
            qa("intermediate", "What does [gone] mean in git branch -vv?", "The branch's upstream remote-tracking ref no longer exists, usually because the remote branch was deleted (for example after a merged PR) and you fetched with --prune. The local branch can usually be deleted."),
        ],
        ["remotes", "branches"],
        chain(
            ("Local branch", "feature", "Local", "You created feature locally."),
            ("Push -u", "sets upstream", "Link", "git push -u origin feature writes branch.feature.remote and merge.", "push -u"),
            ("Tracking ref", "origin/feature", "Remote-tracking", "origin/feature mirrors the remote branch after each fetch.", "fetch"),
            ("Status", "ahead 2, behind 1", "Compare", "git status and branch -vv compare feature with origin/feature.", "@{u}"),
        ),
    ),
    topic(
        "merge-strategies", "Merge Strategies: ort, ours & -X", "branching", "advanced", "MS",
        "Choose how Git combines histories, and know -s ours from -X ours.",
        "Strategies are different referees for the same match: the standard one weighs both sides fairly, while 'ours' declares the home team the winner before kickoff.",
        "A merge strategy is the algorithm git merge uses to combine trees. ort (the default since Git 2.34, replacing recursive) performs a three-way merge with good rename detection, and when there are multiple merge bases it first merges them into a virtual base. octopus is used automatically when merging more than two branches and refuses if there are conflicts. resolve is an older simpler three-way strategy. The ours strategy (-s ours) records a merge but keeps the current tree exactly, discarding the other side's changes entirely; it is used to mark a branch as merged without taking its content. That is different from the strategy option -X ours, which runs a normal ort merge but resolves only conflicting hunks in favour of our side; -X theirs does the opposite, and there is no -s theirs. Other -X options include ignore-space-change, renormalize, patience/histogram diff and find-renames=<n>. subtree merges another project into a subdirectory.",
        ["Marking an old release branch as merged without taking its changes.", "Resolving trivial conflicts in generated files automatically.", "Merging several topic branches at once with octopus."],
        [
            "ort is the default two-head strategy.",
            "-s ours keeps our tree completely; -X ours only wins conflicts.",
            "There is no -s theirs.",
            "octopus merges 3+ heads only if conflict-free.",
            "-X ignore-space-change tames whitespace conflicts.",
        ],
        [
            ex("-X ours vs -s ours", "advanced", "Same branch, very different results.", "bash", """
                git merge -X ours feature        # normal merge; conflicts resolved toward HEAD
                git merge -s ours legacy-2.x     # merge commit, but tree == HEAD (legacy changes dropped)
                git diff HEAD^1 HEAD --stat      # empty after -s ours
            """, runnable=False),
            ex("Other strategies and options", "advanced", "Octopus, whitespace and rename tuning.", "bash", """
                git merge topic-a topic-b topic-c          # octopus
                git merge -X ignore-space-change feature
                git merge -X find-renames=40% feature
                git merge -s ort -X diff-algorithm=histogram feature
            """, runnable=False),
        ],
        ["git merge -s ort <b>", "git merge -X ours|theirs <b>", "git merge -s ours <b>", "git merge a b c (octopus)", "git merge -X ignore-space-change <b>"],
        ["-X theirs silently drops our side of every conflicting hunk; review the result.", "-s ours throws away all of the other branch's changes, not just conflicts.", "Octopus merges are hard to bisect and revert; use them only for independent topics."],
        [
            qa("intermediate", "What is Git's default merge strategy today?", "ort (Ostensibly Recursive's Twin), the default since Git 2.34. It is a faster rewrite of recursive with better rename handling and creates a virtual merge base when there are several merge bases."),
            qa("advanced", "Difference between git merge -s ours and git merge -X ours?", "-s ours creates a merge commit whose tree is identical to the current branch, ignoring the other branch completely. -X ours performs a normal merge and only uses our version for hunks that actually conflict."),
            qa("advanced", "Why is there no -s theirs and how do you emulate it?", "It would discard your branch's work wholesale and was removed as dangerous. You can emulate it by merging with -s ours from the other branch's perspective, or by git merge --no-commit then git read-tree -m -u <theirs> before committing."),
            qa("advanced", "When does Git use the octopus strategy?", "Automatically when you merge more than two heads in one command. It produces a single merge commit with many parents but aborts if any conflict needs manual resolution."),
        ],
        ["merging", "internals"],
        chain(
            ("Two heads", "HEAD + feature", "Inputs", "You merge feature into the current branch."),
            ("Merge base", "virtual if many", "Base", "ort finds the merge base, building a virtual one if there are several.", "base"),
            ("Strategy", "ort / ours", "Algorithm", "The chosen strategy decides how trees are combined.", "-s"),
            ("Options", "-X ours/theirs", "Tie-breaks", "Strategy options settle conflicting hunks or tune diffing.", "-X"),
            ("Merge commit", "2+ parents", "Result", "A merge commit records the combined tree.", "commit"),
        ),
    ),
    topic(
        "conflicts-rerere", "Conflict Resolution & rerere", "branching", "intermediate", "RR",
        "Read conflict markers with the base shown, pick sides per file, and let Git reuse fixes.",
        "A diplomat who keeps a notebook: once two countries agreed on a border, the same agreement is applied automatically next time the dispute comes up.",
        "When a merge, rebase, cherry-pick or stash pop conflicts, Git writes markers into the file and leaves stage 1 (base), 2 (ours) and 3 (theirs) versions in the index. Setting merge.conflictStyle=zdiff3 adds the base section between ||||||| markers, which makes it far easier to see what each side actually changed. You can take a whole file from one side with git checkout --ours/--theirs <file> (or git restore --ours), compare with git diff (combined diff) or git diff --base/--ours/--theirs, and open a visual tool with git mergetool. After editing, git add marks the file resolved and you continue the operation. rerere (reuse recorded resolution), enabled with rerere.enabled=true, records the conflict preimage and your resolution in .git/rr-cache and automatically reapplies it when the same conflict appears again, for example when re-running a rebase or repeatedly merging main into a long branch. git rerere forget <path> discards a bad recorded resolution. git ls-files -u lists unresolved paths.",
        ["Repeatedly rebasing a long-lived branch onto main.", "Resolving a conflict where you need to see the original code.", "Taking a generated file wholesale from one side."],
        [
            "Index stages: 1 base, 2 ours, 3 theirs.",
            "zdiff3 shows the common ancestor inside the markers.",
            "checkout --ours/--theirs takes a whole file from one side.",
            "rerere records and replays resolutions.",
            "In a rebase, ours and theirs are swapped.",
        ],
        [
            ex("Resolve with base context", "intermediate", "zdiff3 markers and per-side checkout.", "bash", """
                git config --global merge.conflictStyle zdiff3
                git merge feature
                # <<<<<<< HEAD
                # timeout: 45
                # ||||||| base
                # timeout: 30
                # =======
                # timeout: 60
                # >>>>>>> feature
                git checkout --theirs package-lock.json
                git add config.yml package-lock.json
                git commit
            """, runnable=False),
            ex("Enable rerere", "intermediate", "Record once, reuse on every rerun.", "bash", """
                git config --global rerere.enabled true
                git config --global rerere.autoUpdate true
                git rebase main            # resolve conflict once
                git rebase --abort
                git rebase main            # Resolved 'config.yml' using previous resolution.
                git rerere forget config.yml
            """, runnable=False),
        ],
        ["git config merge.conflictStyle zdiff3", "git checkout --ours|--theirs <f>", "git mergetool", "git ls-files -u", "git config rerere.enabled true", "git rerere forget <path>"],
        ["rerere can faithfully replay a wrong resolution; review and use rerere forget.", "Taking --theirs during a rebase takes your own commit, not upstream.", "Lock files and generated files should be regenerated, not hand-merged."],
        [
            qa("basic", "How do you resolve a merge conflict?", "Edit the conflicted files to the desired content, removing the markers, then git add each one and complete the operation with git commit (merge) or git rebase --continue. git merge --abort backs out entirely."),
            qa("intermediate", "What does merge.conflictStyle=zdiff3 change?", "Conflict markers include the merge base version between ||||||| and =======, so you can see what each side changed relative to the original rather than guessing from two final versions."),
            qa("intermediate", "What is git rerere?", "Reuse recorded resolution: when enabled, Git records each conflict and how you resolved it, and automatically applies the same resolution when that identical conflict appears again."),
            qa("advanced", "What are index stages during a conflict?", "A conflicted path has up to three index entries: stage 1 is the merge base, stage 2 is ours and stage 3 is theirs. git show :1:path, :2:path and :3:path print them, and git add collapses them back to stage 0."),
        ],
        ["merging", "rebase"],
        chain(
            ("Conflict", "same lines edited", "Collision", "Both sides changed the same region of config.yml."),
            ("Markers", "ours|base|theirs", "Inspect", "zdiff3 markers show ours, the base and theirs together.", "write"),
            ("Resolve", "edit + git add", "Fix", "Edit to the right result and git add to mark it resolved.", "add"),
            ("rr-cache", "recorded fix", "Record", "rerere stores the preimage and your resolution.", "record"),
            ("Next time", "auto-applied", "Replay", "The same conflict later is resolved automatically.", "reuse"),
        ),
    ),
    topic(
        "ff-vs-noff", "Fast-forward vs --no-ff", "branching", "basic", "FF",
        "Move the pointer, or always record a merge commit: a team history choice.",
        "Fast-forward is sliding a bookmark further along the same chapter; --no-ff is inserting a divider page that says 'feature X ended here'.",
        "If the branch you are merging is strictly ahead of the current branch, Git can fast-forward: it simply moves the current branch pointer to the other tip, creating no new commit and leaving perfectly linear history. --no-ff forces a merge commit even when a fast-forward is possible, so the feature's commits stay grouped under a merge whose first parent is the previous mainline. That makes git log --first-parent read like a list of features and lets you revert an entire feature with git revert -m 1 <merge>. --ff-only does the opposite: it refuses to merge unless a fast-forward is possible, which is a common safety setting for updating local main. merge.ff=false or merge.ff=only in config sets the default. Hosting platforms expose the same choice as 'create a merge commit', 'rebase and merge' and 'squash and merge'. Pick one convention per repository and apply it consistently.",
        ["Recording feature boundaries in main.", "Keeping local main a pure mirror of origin/main.", "Producing linear history after rebasing feature branches."],
        [
            "Fast-forward creates no commit; just moves the ref.",
            "--no-ff always creates a merge commit.",
            "--ff-only refuses anything but a fast-forward.",
            "--first-parent log works best with --no-ff merges.",
            "Reverting a --no-ff feature is one revert -m 1.",
        ],
        [
            ex("Same branch, two outcomes", "basic", "Fast-forward vs forced merge commit.", "bash", """
                git switch main
                git merge feature/a            # Fast-forward
                git merge --no-ff feature/b    # Merge made by the 'ort' strategy.
                git log --oneline --graph -6
            """, runnable=False),
            ex("Configure defaults", "basic", "Safe local updates and explicit feature merges.", "bash", """
                git config --global pull.ff only
                git config branch.main.mergeoptions "--no-ff"
                git merge --ff-only origin/main
            """, runnable=False),
        ],
        ["git merge <b> (ff if possible)", "git merge --no-ff <b>", "git merge --ff-only <b>", "git config merge.ff false|only", "git log --first-parent"],
        ["Fast-forward merges lose the information that commits came from one feature.", "--no-ff on trivial one-commit fixes clutters history.", "--ff-only pull fails after any local commit; that is the point, but surprises newcomers."],
        [
            qa("basic", "When can Git fast-forward?", "When the current branch's tip is an ancestor of the branch being merged, so there are no divergent commits. Git simply moves the branch pointer forward."),
            qa("basic", "What does --no-ff do?", "It creates a merge commit even if a fast-forward is possible, preserving the fact that a group of commits was developed on a separate branch."),
            qa("intermediate", "Why would a team prefer --no-ff merges?", "Mainline history via --first-parent then shows one entry per feature, and the whole feature can be reverted with one git revert -m 1 <merge>. It also records when and by whom a feature was integrated."),
            qa("intermediate", "What is --ff-only useful for?", "Updating a local branch that should exactly mirror its upstream, such as main. If you accidentally committed locally the merge stops instead of creating a merge commit."),
        ],
        ["merging", "rebase", "workflows"],
        chain(
            ("main", "at c2", "Start", "main points at c2; feature is c3 and c4 on top of c2."),
            ("Fast-forward", "main -> c4", "Default", "Plain merge just moves main to c4; history stays linear.", "ff"),
            ("--no-ff", "merge commit M", "Forced merge", "--no-ff creates M with parents c2 and c4.", "no-ff"),
            ("First-parent", "one entry/feature", "Readable mainline", "log --first-parent shows M as one feature step.", "log"),
        ),
    ),
    topic(
        "squash-merge", "Squash Merges", "branching", "intermediate", "SQ",
        "Collapse a branch into one commit on main, and know what is lost.",
        "Publishing a book chapter without the drafts: readers get one clean chapter, but the editing history stays in your notebook.",
        "git merge --squash feature applies the combined changes of feature to the index and working tree without creating a merge commit or recording the branch as a parent; you then git commit to create one new ordinary commit. Hosting platforms offer the same as 'Squash and merge', usually using the PR title as the commit message. The result is a tidy mainline with one commit per PR that is easy to revert and bisect. The trade-off is that Git no longer knows the branch was merged: git branch -d refuses to delete it, and any branch built on top of the original feature commits will see conflicts or duplicate changes when it is later rebased or merged. Use git rebase --onto main <old-feature-tip> stacked-branch to move a stacked branch onto the squashed result. Individual commit messages and authorship are collapsed, though platforms add Co-authored-by trailers. Squashing is a good fit for small PRs with messy intermediate commits, and a poor fit for large changes where the individual steps matter.",
        ["One commit per PR on main for simple history.", "Hiding 'fix typo' and 'address review' commits.", "Making each change trivially revertible."],
        [
            "--squash stages changes; you still run git commit.",
            "No parent link: branch is not considered merged.",
            "Stacked branches need rebase --onto afterwards.",
            "PR title becomes the commit message: make it meaningful.",
            "Delete the source branch after squashing.",
        ],
        [
            ex("Local squash merge", "intermediate", "One new commit containing the whole feature.", "bash", """
                git switch main
                git merge --squash feature/login
                git commit -m "feat(auth): add login form and session handling (#214)"
                git branch -D feature/login     # -d refuses: not merged by ancestry
            """, runnable=False),
            ex("Rescue a stacked branch", "advanced", "Move the branch that was built on the squashed feature.", "bash", """
                # feature/b was based on feature/a, which got squash-merged into main
                git fetch origin
                git rebase --onto origin/main feature/a feature/b
                git push --force-with-lease
            """, runnable=False),
        ],
        ["git merge --squash <b>", "git commit", "git branch -D <b>", "git rebase --onto main <old-base> <b>", "git cherry main <b>"],
        ["Continuing to work on a branch after it was squash-merged causes repeated conflicts.", "git branch --merged does not list squash-merged branches.", "Large squashed commits are hard to review and bisect within."],
        [
            qa("basic", "What does git merge --squash do?", "It applies all changes from the other branch to the index and working tree as if merged, but does not create a merge commit or record the parent. You commit the result as a single new commit."),
            qa("intermediate", "Why does git branch -d refuse to delete a squash-merged branch?", "-d only deletes branches whose tip is reachable from the current branch or upstream. A squash creates a new unrelated commit, so the original commits are not ancestors of main."),
            qa("intermediate", "Squash merge vs rebase and merge?", "Squash produces one commit containing all changes. Rebase and merge replays each commit individually onto main, keeping every commit and message but still producing linear history."),
            qa("advanced", "How do you fix a branch that was based on a feature branch that got squash-merged?", "Rebase only the commits unique to the stacked branch onto main: git rebase --onto main <old-feature-tip> <stacked-branch>. That skips the original feature commits, whose changes already exist in the squash commit."),
        ],
        ["merging", "interactive-rebase", "rebase"],
        chain(
            ("Feature", "5 small commits", "Messy branch", "A PR has five commits including fixups."),
            ("--squash", "changes staged", "Squash", "git merge --squash applies all changes to the index.", "squash"),
            ("Commit", "one commit S", "Single commit", "git commit records S on main with the PR title.", "commit"),
            ("No parent", "branch unmerged", "Side effect", "main has no link to feature's commits; delete the branch.", "orphan"),
        ),
    ),
    topic(
        "revert-deep", "Revert in Depth", "fixing", "intermediate", "RV",
        "Undo published commits by adding new inverse commits, including merges and ranges.",
        "Publishing a correction notice in tomorrow's newspaper rather than recalling every copy already delivered.",
        "git revert <commit> computes the inverse of a commit's changes and records them as a new commit, leaving history intact. Because nothing is rewritten, it is the right tool for undoing changes on shared branches. You can revert several commits at once (git revert A..B reverts each commit in the range, newest first) and combine them with --no-commit to produce a single revert commit. Reverting a merge commit requires -m <parent-number>, usually -m 1 to keep the mainline and undo what the merged branch brought in. The catch: after reverting a merge, Git still considers the branch merged, so merging it again brings in only newer commits; to reintroduce the feature you must revert the revert. Conflicts during revert are resolved like any other, then git revert --continue (or --abort). Many teams use revert as the first response to a bad deploy because it is fast, auditable and safe.",
        ["Rolling back a bad change already deployed from main.", "Undoing a whole merged feature.", "Backing out a range of commits as one change."],
        [
            "Revert adds a new commit; it never rewrites history.",
            "Merge commits need -m 1 (mainline parent).",
            "Re-merging after reverting a merge needs revert-of-revert.",
            "--no-commit combines several reverts into one.",
            "Use revert on shared branches; reset only on private ones.",
        ],
        [
            ex("Revert a commit and a range", "intermediate", "Single commit, then a range combined into one.", "bash", """
                git revert 3f2a9c1
                git revert --no-commit HEAD~3..HEAD
                git commit -m "revert: back out checkout redesign (3 commits)"
                git revert --abort        # if a conflict is too messy
            """, runnable=False),
            ex("Revert a merge, then restore it", "advanced", "Undo a feature merge and later bring it back.", "bash", """
                git log --oneline --merges -3
                git revert -m 1 a1b2c3d             # undo feature merge
                # ... feature is fixed on its branch ...
                git revert <sha-of-the-revert>      # reintroduce original changes
                git merge feature/payments          # bring in the new fixes
            """, runnable=False),
        ],
        ["git revert <sha>", "git revert -m 1 <merge-sha>", "git revert --no-commit A..B", "git revert --continue · --abort", "git revert <revert-sha>"],
        ["Forgetting -m on a merge commit makes revert fail with 'is a merge but no -m option was given'.", "Merging a reverted branch again without reverting the revert silently omits the original changes.", "Reverting a commit that later commits depend on can conflict; revert dependents first."],
        [
            qa("basic", "git revert vs git reset?", "revert creates a new commit that undoes a previous one and is safe on shared branches. reset moves the branch pointer backward, rewriting history, which is only safe on commits nobody else has."),
            qa("intermediate", "How do you revert a merge commit?", "git revert -m 1 <merge> undoes the changes the merge introduced relative to its first parent (the mainline). The number selects which parent's side is kept."),
            qa("advanced", "You reverted a merged feature, fixed it, and re-merged, but the original changes are missing. Why?", "The original commits are still ancestors of main, so Git considers them merged and only brings in the new fix commits. You must first revert the revert commit to reapply the original changes, then merge the fixes."),
            qa("intermediate", "How do you revert several commits as a single commit?", "git revert --no-commit <oldest>^..<newest> (or A..B) applies all inverses to the index without committing, then one git commit records them together."),
        ],
        ["undoing", "merging", "bisect-reflog"],
        chain(
            ("Bad commit", "B on main", "Problem", "Commit B is on main and already deployed."),
            ("Inverse diff", "-B", "Compute", "git revert computes the opposite of B's changes.", "invert"),
            ("Revert commit", "R = -B", "Record", "A new commit R is added on top; history is untouched.", "commit"),
            ("Push", "fast-forward", "Share", "R pushes as a normal fast-forward and can be deployed.", "push"),
            ("Re-apply", "revert R", "Later", "To bring B back, revert R.", "revert"),
        ),
    ),
]

TOPICS += [
    topic(
        "reset-modes", "reset: --soft, --mixed, --hard, --keep", "fixing", "intermediate", "RS",
        "Move the branch pointer and decide how much of the index and working tree follows.",
        "Rewinding a film: --soft rewinds the counter only, --mixed also clears the editing desk, --hard also burns the scenes you shot since.",
        "git reset <commit> moves the current branch (and HEAD) to another commit; the mode decides what else changes. --soft moves only the branch, so the undone commits' changes stay staged, which is perfect for recombining commits. --mixed (the default) also resets the index to the target, leaving changes in the working tree as unstaged edits. --hard also overwrites the working tree, discarding uncommitted changes to tracked files permanently. --keep is a safer alternative to --hard: it moves the branch and updates files but refuses if a file with local changes would be overwritten. With a path, git reset <path> only unstages that path (git restore --staged is the modern equivalent). After a reset, ORIG_HEAD and the reflog hold the previous position, so committed work can be recovered with git reset --hard ORIG_HEAD or HEAD@{1}. Because reset rewrites a branch, use it on local or private commits; use revert for anything shared.",
        ["Squashing the last few commits into one with --soft.", "Unstaging everything with a plain reset.", "Throwing away a failed experiment with --hard or --keep."],
        [
            "--soft: branch only. --mixed: + index. --hard: + working tree.",
            "--keep moves but protects uncommitted local edits.",
            "git reset <path> only unstages; it does not move HEAD.",
            "ORIG_HEAD and reflog undo a reset of committed work.",
            "Uncommitted changes discarded by --hard are not in the reflog.",
        ],
        [
            ex("The three classic modes", "intermediate", "Same target, three different results.", "bash", """
                git reset --soft HEAD~2    # last two commits' changes now staged
                git commit -m "feat: combined change"
                git reset HEAD~1           # --mixed: changes unstaged in working tree
                git reset --hard HEAD~1    # changes gone from working tree too
                git reset --hard ORIG_HEAD # undo the previous reset
            """, runnable=False),
            ex("Safer variants", "intermediate", "Unstage a path and move with --keep.", "bash", """
                git reset config.yml          # unstage just this file
                git reset --keep origin/main  # move branch, keep unrelated local edits
                git reflog -5
            """, runnable=False),
        ],
        ["git reset --soft <rev>", "git reset [--mixed] <rev>", "git reset --hard <rev>", "git reset --keep <rev>", "git reset <path>", "git reset --hard ORIG_HEAD"],
        ["git reset --hard deletes uncommitted changes with no undo; stash first if unsure.", "Resetting a pushed branch forces everyone else to recover.", "Untracked files survive --hard; use git clean to remove them."],
        [
            qa("basic", "What are the three main reset modes?", "--soft moves the branch pointer only, --mixed (default) also resets the index, and --hard also resets the working tree. Each step discards more state."),
            qa("intermediate", "How do you combine the last three commits into one with reset?", "git reset --soft HEAD~3 moves the branch back while keeping all their changes staged, then a single git commit records them together."),
            qa("intermediate", "You ran git reset --hard HEAD~2 by mistake. How do you recover?", "The commits still exist. git reset --hard ORIG_HEAD or git reset --hard HEAD@{1} (from git reflog) moves the branch back to where it was."),
            qa("advanced", "What does git reset --keep do differently from --hard?", "It updates files that differ between HEAD and the target but aborts if any of those files has uncommitted changes, so local edits are never silently discarded. Files you edited that are the same in both commits are kept."),
        ],
        ["undoing", "three-trees", "bisect-reflog"],
        chain(
            ("HEAD/branch", "moves to target", "--soft", "Only the branch pointer moves; index and files stay."),
            ("Index", "reset to target", "--mixed", "The index is also reset; changes become unstaged.", "mixed"),
            ("Working tree", "overwritten", "--hard", "Files are overwritten; uncommitted edits are lost.", "hard"),
            ("ORIG_HEAD", "old position", "Safety net", "ORIG_HEAD and the reflog remember where you were.", "undo"),
        ),
    ),
    topic(
        "restore-switch", "restore & switch", "fixing", "basic", "RW",
        "The clear, single-purpose replacements for the overloaded git checkout.",
        "checkout was a Swiss Army knife where the corkscrew sometimes opened by accident; switch and restore are two separate, clearly labelled tools.",
        "Git 2.23 split git checkout into two commands. git switch changes branches: git switch main, git switch -c feature to create, git switch - to go back, git switch --detach <commit> to inspect an old commit, and -C to reset an existing branch. It refuses to switch if local changes would be overwritten, unless you pass --discard-changes or --merge. git restore changes files: git restore <path> copies the index version over the working tree (discarding unstaged edits), git restore --staged <path> copies HEAD into the index (unstaging), and --source=<rev> restores from any commit. Combining --staged --worktree resets both. git restore -p works hunk by hunk. Because each command does one job, it is harder to lose work by mistyping a branch name that happens to match a file. checkout still works and remains common in scripts and older documentation.",
        ["Discarding edits to one file.", "Unstaging a file staged by mistake.", "Bringing back a deleted file from an older commit."],
        [
            "switch is for branches; restore is for files.",
            "restore <f>: index -> working tree.",
            "restore --staged <f>: HEAD -> index.",
            "--source=<rev> restores from any commit.",
            "git switch - returns to the previous branch.",
        ],
        [
            ex("Switching branches", "basic", "Create, go back, and inspect an old commit.", "bash", """
                git switch -c feature/search
                git switch main
                git switch -
                git switch --detach v2.3.0
                git switch -c hotfix/2.3.1
            """, runnable=False),
            ex("Restoring files", "basic", "Discard, unstage and recover from history.", "bash", """
                git restore src/app.py                     # discard unstaged edits
                git restore --staged src/app.py            # unstage
                git restore --source=HEAD~3 -- docs/api.md # old version of a file
                git restore --source=main --staged --worktree config.yml
            """, runnable=False),
        ],
        ["git switch <branch>", "git switch -c <new>", "git switch -", "git restore <path>", "git restore --staged <path>", "git restore --source=<rev> <path>"],
        ["git restore <path> discards working-tree changes permanently.", "--source restores into the working tree only unless you add --staged.", "switch refuses with a dirty tree that conflicts; stash or commit first."],
        [
            qa("basic", "Why were switch and restore introduced?", "checkout did two unrelated jobs, switching branches and overwriting files, which confused users and could destroy work. switch handles branches and restore handles files with clearer options."),
            qa("basic", "How do you unstage a file without losing your edits?", "git restore --staged <file>. It copies the HEAD version into the index and leaves the working tree untouched."),
            qa("intermediate", "How do you get a file back as it was three commits ago?", "git restore --source=HEAD~3 -- <file> writes that version to the working tree; add --staged to also stage it. The older form is git checkout HEAD~3 -- <file>."),
            qa("intermediate", "What does git switch --detach do?", "It checks out a commit without moving any branch, giving a detached HEAD for inspection or testing. Create a branch with git switch -c if you want to keep commits made there."),
        ],
        ["branches", "undoing", "three-trees"],
        chain(
            ("HEAD", "last commit", "Source", "HEAD holds the committed version."),
            ("Index", "restore --staged", "Unstage", "restore --staged copies HEAD into the index.", "--staged"),
            ("Working tree", "restore <file>", "Discard", "restore copies the index version over your edits.", "restore"),
            ("Branch", "switch <name>", "Switch", "switch moves HEAD to another branch and updates all three.", "switch"),
        ),
    ),
    topic(
        "clean", "git clean", "fixing", "basic", "CL",
        "Remove untracked files and directories, carefully, after a dry run.",
        "Sweeping the workshop floor: everything not on the inventory list goes in the bin, so look at the pile before you sweep.",
        "git clean deletes untracked files from the working tree, which is useful after a build that left artefacts behind or to get back to a pristine checkout. It is deliberately hard to run by accident: clean.requireForce defaults to true, so you must pass -f (or -n for a dry run, or -i for interactive). -d also removes untracked directories, -x also removes ignored files such as build output and .env files, and -X removes only ignored files, keeping other untracked files. -e <pattern> adds extra exclusions. Combined with git reset --hard, git clean -fdx returns a repository to exactly the committed state. Deleted untracked files never entered Git, so they cannot be recovered from the reflog or objects. Always run git clean -n (or -nd, -ndx) first and read the list.",
        ["Removing build artefacts before a clean build.", "Resetting a CI workspace or a messy checkout.", "Deleting stray generated files after switching branches."],
        [
            "-n dry run, -f force, -i interactive.",
            "-d includes directories.",
            "-x includes ignored files; -X only ignored files.",
            "Untracked files deleted by clean are unrecoverable.",
            "reset --hard + clean -fdx = pristine checkout.",
        ],
        [
            ex("Dry run first", "basic", "Look before deleting.", "bash", """
                git clean -nd
                # Would remove build/
                # Would remove scratch.txt
                git clean -fd
            """, runnable=False),
            ex("Pristine checkout", "intermediate", "Remove ignored output but keep local env files.", "bash", """
                git clean -ndX
                git clean -fdx -e .env -e .env.local
                git reset --hard
                git clean -i
            """, runnable=False),
        ],
        ["git clean -n", "git clean -fd", "git clean -fdx", "git clean -fdX", "git clean -i", "git clean -fd -e <pattern>"],
        ["-x deletes ignored files like .env and local databases that are often not backed up.", "Nested repositories are skipped unless you pass -f twice.", "No undo: files never committed are not in Git."],
        [
            qa("basic", "What does git clean do?", "It removes untracked files from the working tree. By default it needs -f to actually delete anything; -n shows what would be removed."),
            qa("basic", "Difference between -x and -X?", "-x removes untracked files including ignored ones. -X removes only ignored files (like build output), leaving other untracked files alone."),
            qa("intermediate", "How do you get a working copy back to exactly the last commit?", "git reset --hard to restore tracked files and the index, then git clean -fdx to remove all untracked and ignored files and directories. Dry run the clean first."),
            qa("intermediate", "Can you recover files deleted by git clean?", "Not through Git: they were never stored as objects, so neither reflog nor fsck can find them. Only OS backups, editor local history or the trash (if the tool used it) can help."),
        ],
        ["undoing", "three-trees"],
        chain(
            ("Working tree", "tracked + extras", "Messy tree", "Build output and scratch files are lying around."),
            ("Dry run", "git clean -n", "Preview", "List what would be removed.", "-n"),
            ("Select", "-d / -x / -X", "Scope", "Choose directories, ignored files or only ignored files.", "flags"),
            ("Delete", "git clean -f", "Remove", "Files are deleted permanently.", "-f"),
        ),
    ),
    topic(
        "amend-fixup", "amend, fixup & autosquash", "fixing", "intermediate", "AF",
        "Fix the last commit, or mark fixes for older commits and fold them in automatically.",
        "Sticky notes on earlier pages saying 'insert this here', which a single pass of the editor then folds into the right pages.",
        "git commit --amend replaces the last commit with a new one containing the current index and, optionally, a new message; --no-edit keeps the message and --reset-author updates authorship. For older commits, git commit --fixup=<sha> creates a commit titled 'fixup! <original subject>', and --squash=<sha> creates 'squash! ...' whose message is combined. git rebase -i --autosquash <base> then reorders those commits next to their targets and marks them fixup or squash, so the fix is folded into the right commit automatically; rebase.autoSquash=true makes this the default. --fixup=amend:<sha> also replaces the target's message and --fixup=reword:<sha> changes only the message. This workflow keeps a PR's commit series clean while addressing review comments. Like any rewrite, amend and autosquash change commit ids, so force-push with --force-with-lease and avoid rewriting shared branches.",
        ["Adding a forgotten file to the last commit.", "Addressing review feedback in the commit it belongs to.", "Fixing a typo in a commit message."],
        [
            "--amend replaces the last commit (new id).",
            "--fixup=<sha> targets any earlier commit.",
            "rebase -i --autosquash folds fixups in.",
            "--fixup=reword:<sha> changes only the message.",
            "Force-push with lease after rewriting.",
        ],
        [
            ex("Amend the last commit", "basic", "Add a forgotten file, keep the message.", "bash", """
                git add tests/test_login.py
                git commit --amend --no-edit
                git commit --amend -m "feat(auth): add login with rate limiting"
                git push --force-with-lease
            """, runnable=False),
            ex("Fixup an older commit", "intermediate", "Mark a fix for commit 3f2a9c1 and autosquash.", "bash", """
                git log --oneline -4
                git add src/session.py
                git commit --fixup=3f2a9c1
                git rebase -i --autosquash origin/main
                git config --global rebase.autoSquash true
            """, runnable=False),
        ],
        ["git commit --amend [--no-edit]", "git commit --fixup=<sha>", "git commit --squash=<sha>", "git rebase -i --autosquash <base>", "git commit --fixup=reword:<sha>"],
        ["Amending a pushed commit requires a force-push and breaks others who pulled it.", "--amend with an accidentally staged file sneaks it into the commit.", "Autosquash matches by subject line; renaming the target breaks matching (use the sha form)."],
        [
            qa("basic", "What does git commit --amend do?", "It creates a new commit that replaces the current tip, combining the previous commit's content with whatever is staged and optionally a new message. The old commit remains reachable only via reflog."),
            qa("intermediate", "How do you fix a commit that is three commits back?", "Stage the fix, run git commit --fixup=<sha-of-target>, then git rebase -i --autosquash <base>. Git moves the fixup next to its target and folds it in."),
            qa("intermediate", "Difference between --fixup and --squash?", "fixup! commits are folded in and their message is discarded. squash! commits are folded in too, but the editor opens so you can combine the messages."),
            qa("intermediate", "Is amending safe after pushing?", "It rewrites the commit id, so the remote branch must be force-pushed. It is fine on your own PR branch (use --force-with-lease) but not on shared branches others have built on."),
        ],
        ["interactive-rebase", "undoing", "rebase"],
        chain(
            ("Series", "A, B, C", "PR commits", "Your PR has commits A, B and C."),
            ("Review", "fix belongs in A", "Feedback", "A reviewer finds a bug introduced in A."),
            ("Fixup", "fixup! A", "Mark", "git commit --fixup=A creates a marked commit.", "--fixup"),
            ("Autosquash", "A', B', C'", "Fold", "rebase -i --autosquash folds the fix into A.", "rebase"),
            ("Push", "with lease", "Update PR", "Force-push with lease to update the PR.", "push"),
        ),
    ),
    topic(
        "recover-lost-work", "Recovering Lost Work", "fixing", "advanced", "LW",
        "Find commits, stashes and staged files that seem gone, using reflog and fsck.",
        "Git is a hoarder with a diary: almost nothing committed is thrown away immediately, and the diary says where you put it.",
        "Most 'lost' work in Git is still in the object database. The reflog records every position of HEAD and each branch, so commits lost to a bad reset, rebase or branch deletion can be found with git reflog (or git reflog show <branch>) and restored with git branch rescue <sha> or git reset --hard <sha>. ORIG_HEAD points to where HEAD was before the last reset, merge or rebase. A dropped or cleared stash is a dangling commit: git fsck --no-reflogs --unreachable (or --lost-found) lists unreachable commits, and stash commits are recognisable by their 'WIP on' messages. Files that were staged but never committed exist as dangling blobs, which git fsck --lost-found writes to .git/lost-found/other. Unreachable objects survive until garbage collection prunes them, governed by gc.reflogExpire (90 days), gc.reflogExpireUnreachable (30 days) and gc.pruneExpire (2 weeks). Changes that were never staged or committed are not in Git at all; only editor local history or backups can help. When something goes wrong, stop and avoid running git gc until you have recovered.",
        ["Undoing a git reset --hard of committed work.", "Recovering a deleted branch.", "Finding a dropped stash or an accidentally removed staged file."],
        [
            "reflog: every HEAD and branch movement, local only.",
            "Create a branch at a found sha to keep it safe.",
            "fsck --unreachable/--lost-found finds dangling objects.",
            "Staged content survives as blobs; unstaged edits do not.",
            "gc eventually prunes unreachable objects.",
        ],
        [
            ex("Recover commits and branches", "advanced", "Reflog after a bad reset or branch delete.", "bash", """
                git reflog -10
                # 7c1e2a4 HEAD@{1}: commit: add payment retries
                # a9d0f31 HEAD@{0}: reset: moving to HEAD~3
                git branch rescue 7c1e2a4
                git reflog show feature/old
                git branch feature/old feature/old@{1}
            """, runnable=False),
            ex("Find a dropped stash or staged file", "advanced", "Dangling commits and blobs via fsck.", "bash", """
                git fsck --no-reflogs --unreachable | grep commit
                git log --oneline --no-walk $(git fsck --no-reflogs --unreachable | awk '/commit/ {print $3}')
                git stash apply 5d3c2b1
                git fsck --lost-found
                ls .git/lost-found/other/
            """, runnable=False),
        ],
        ["git reflog [branch]", "git branch rescue <sha>", "git reset --hard HEAD@{n}", "git fsck --unreachable --no-reflogs", "git fsck --lost-found"],
        ["Running git gc --prune=now after an accident can destroy recoverable objects.", "The reflog is local: a fresh clone has none of your history of movements.", "Unstaged edits destroyed by reset --hard or restore are not recoverable from Git."],
        [
            qa("intermediate", "You deleted a branch with unmerged commits. How do you get it back?", "git reflog (or the sha printed when you deleted it) shows the branch tip; git branch <name> <sha> recreates it. The commits remain until gc prunes unreachable objects."),
            qa("advanced", "How do you recover a stash you dropped?", "A dropped stash is a dangling commit. git fsck --no-reflogs --unreachable lists unreachable commits; find the one with a 'WIP on' message and git stash apply <sha> or branch from it."),
            qa("advanced", "Can you recover a file that was staged but never committed, then reset away?", "Yes, usually: git add stored it as a blob. git fsck --lost-found writes dangling blobs to .git/lost-found/other, where you can find the content by inspecting the files."),
            qa("intermediate", "How long does Git keep unreachable commits?", "Until gc prunes them: reflog entries for unreachable commits expire after 30 days by default (90 for reachable), and loose unreachable objects older than gc.pruneExpire (2 weeks) are removed. Recover promptly and avoid manual gc."),
        ],
        ["bisect-reflog", "undoing", "internals"],
        chain(
            ("Accident", "reset / drop", "Something vanished", "A reset, rebase or stash drop hid your work."),
            ("Reflog", "HEAD@{n}", "Look back", "git reflog lists where HEAD and branches have been.", "reflog"),
            ("fsck", "dangling objects", "Dig deeper", "For stashes and staged files, fsck finds unreachable objects.", "fsck"),
            ("Rescue", "git branch x <sha>", "Anchor it", "Create a branch at the sha so gc cannot prune it.", "branch"),
        ),
    ),
    topic(
        "worktrees", "Worktrees", "scale", "intermediate", "WT",
        "Check out several branches at once from one repository, without stashing.",
        "One kitchen pantry (object store) feeding several cooking stations, each working on a different dish at the same time.",
        "git worktree add <path> <branch> creates an additional working directory linked to the same repository. All worktrees share the object database, refs and config, but each has its own HEAD, index and working files, so you can build a hotfix in one directory while a long feature build runs in another. This is cheaper than a second clone (no duplicate objects) and safer than stashing half-finished work. A branch can be checked out in only one worktree at a time, which prevents two directories from fighting over the same branch tip. git worktree list shows them, git worktree remove deletes one cleanly, and git worktree prune cleans up metadata for directories deleted by hand. git worktree lock prevents pruning of a worktree on removable media. Per-worktree configuration is possible with extensions.worktreeConfig. Worktrees are also popular for running AI agents or parallel test runs on separate branches.",
        ["Urgent hotfix while a feature is half done.", "Reviewing a PR without disturbing your current branch.", "Running long builds or tests on another branch in parallel."],
        [
            "Shared objects and refs; separate HEAD, index and files.",
            "One branch can be checked out in one worktree only.",
            "remove and prune keep metadata tidy.",
            "Much cheaper than a second clone.",
            "Each worktree needs its own dependencies installed.",
        ],
        [
            ex("Hotfix in a second worktree", "intermediate", "No stash needed.", "bash", """
                git worktree add -b hotfix/2.3.1 ../app-hotfix origin/main
                cd ../app-hotfix
                git commit -am "fix: null pointer in invoice export"
                git push -u origin hotfix/2.3.1
                cd ../app
                git worktree remove ../app-hotfix
            """, runnable=False),
            ex("Review a PR side by side", "intermediate", "Detached worktree at a remote branch.", "bash", """
                git fetch origin
                git worktree add --detach ../review origin/feature/search
                git worktree list
                git worktree prune
            """, runnable=False),
        ],
        ["git worktree add <path> <branch>", "git worktree add -b <new> <path> <base>", "git worktree list", "git worktree remove <path>", "git worktree prune", "git worktree lock <path>"],
        ["fatal: 'main' is already checked out at ... means another worktree has that branch.", "Deleting a worktree directory manually leaves stale metadata until git worktree prune.", "Untracked build outputs and node_modules are not shared between worktrees."],
        [
            qa("basic", "What is a git worktree?", "An extra working directory attached to the same repository, with its own HEAD, index and files but sharing objects and refs. It lets you have several branches checked out simultaneously."),
            qa("intermediate", "Worktree vs a second clone?", "A worktree shares the object database and refs, so it is created instantly, uses little disk and sees new commits and branches immediately. A second clone duplicates objects and needs its own fetches."),
            qa("intermediate", "Why can't the same branch be checked out in two worktrees?", "Committing in one would move the branch under the other, leaving its index and files inconsistent with HEAD. Git prevents it; use a new branch or --detach instead."),
            qa("intermediate", "How do you clean up a worktree you deleted with rm -rf?", "Run git worktree prune, which removes administrative data in .git/worktrees for directories that no longer exist. git worktree remove is the clean way to delete one in the first place."),
        ],
        ["branches", "stash-cherry-pick", "internals"],
        chain(
            ("Repository", "objects + refs", "Shared store", "One .git directory holds all objects and refs."),
            ("Worktree A", "feature (main dir)", "Primary", "Your main directory has feature checked out.", "HEAD"),
            ("Worktree B", "hotfix (../app-hf)", "Add", "git worktree add creates a second directory on hotfix.", "add"),
            ("Commit", "visible to both", "Shared refs", "A commit in B is instantly visible from A.", "commit"),
            ("Remove", "worktree remove", "Clean up", "Remove B when done; objects stay in the repo.", "remove"),
        ),
    ),
    topic(
        "submodules", "Submodules", "scale", "advanced", "SM",
        "Embed another repository at a pinned commit inside your repository.",
        "A bookshelf with a reserved slot labelled 'volume 3, second printing': the slot records exactly which edition belongs there, not the book itself.",
        "A submodule is a nested Git repository whose exact commit is recorded in the parent as a special tree entry (a gitlink, mode 160000), with its URL and path stored in .gitmodules. Cloning the parent does not fetch submodule contents unless you use git clone --recurse-submodules or later run git submodule update --init --recursive. Inside a submodule you are usually on a detached HEAD at the pinned commit; to update it, enter it, check out the desired commit (or run git submodule update --remote to follow a branch configured in .gitmodules), then commit the new gitlink in the parent. submodule.recurse=true makes checkout, pull and switch update submodules automatically, and git submodule foreach runs a command in each one. Submodules give precise pinning and keep histories separate, but add friction: forgetting to update or push a submodule commit leaves others with a broken reference. Removing one takes git submodule deinit, git rm and cleaning .git/modules. Only add submodules from trusted URLs because their content and hooks are fetched into your checkout.",
        ["Vendoring a shared library pinned to an exact version.", "Including a large independent project, such as firmware or a theme.", "Sharing common configuration across several repositories."],
        [
            "Parent stores a gitlink (commit id) plus .gitmodules.",
            "Clone with --recurse-submodules or update --init.",
            "Submodules sit on a detached HEAD by default.",
            "Update = move submodule, then commit the gitlink in parent.",
            "Push submodule commits before pushing the parent.",
        ],
        [
            ex("Add and clone", "advanced", "Add a submodule and fetch it on clone.", "bash", """
                git submodule add https://github.com/example/ui-kit.git vendor/ui-kit
                git commit -m "build: add ui-kit submodule"
                git clone --recurse-submodules https://github.com/example/app.git
                git submodule update --init --recursive
                git config --global submodule.recurse true
            """, runnable=False),
            ex("Update to a newer version", "advanced", "Move the pin, then commit it in the parent.", "bash", """
                git submodule update --remote vendor/ui-kit
                git diff --submodule
                git add vendor/ui-kit
                git commit -m "build: bump ui-kit to 4.2.0"
                git push --recurse-submodules=check
                git submodule foreach "git status -s"
            """, runnable=False),
        ],
        ["git submodule add <url> <path>", "git clone --recurse-submodules <url>", "git submodule update --init --recursive", "git submodule update --remote", "git submodule foreach <cmd>", "git submodule deinit <path>"],
        ["Pushing the parent before the submodule commit leaves teammates with 'reference is not a tree'.", "Commits made on a submodule's detached HEAD are easy to lose; create a branch first.", "Empty submodule directories after clone mean update --init was not run."],
        [
            qa("intermediate", "How does Git store a submodule in the parent repository?", "As a gitlink entry in the tree with mode 160000 pointing to a specific commit id of the submodule, plus its path and URL in .gitmodules. The submodule's files are not stored in the parent."),
            qa("intermediate", "Why are submodule directories empty after cloning?", "Plain clone does not fetch submodules. Run git submodule update --init --recursive, or clone with --recurse-submodules next time."),
            qa("advanced", "How do you update a submodule to a newer upstream version?", "Inside it, fetch and check out the desired commit, or run git submodule update --remote. Then in the parent git add <path> and commit, which records the new gitlink."),
            qa("advanced", "When would you choose subtree over submodules?", "When consumers should get everything with a normal clone and you rarely push changes back. Subtree copies the code into the parent history, avoiding the extra commands and detached-HEAD pitfalls of submodules at the cost of a bigger history."),
        ],
        ["internals", "remotes", "workflows"],
        chain(
            ("Parent repo", "app", "Parent", "Your repository wants to include ui-kit."),
            ("gitlink", "160000 <sha>", "Pin", "The parent tree records the exact submodule commit.", "add"),
            (".gitmodules", "path + url", "Locate", ".gitmodules says where to clone it from.", "config"),
            ("Submodule", "detached @ sha", "Checkout", "update --init clones and checks out that commit.", "update"),
            ("Bump", "commit new gitlink", "Update", "Move the submodule, then commit the new pin in the parent.", "commit"),
        ),
    ),
    topic(
        "subtrees", "Subtrees", "scale", "advanced", "ST",
        "Merge another project's history into a subdirectory, no extra commands for consumers.",
        "Instead of a reserved slot pointing to another book, you photocopy the chapters into your own book, while still able to sync with the original author.",
        "A subtree embeds another repository's content directly in a subdirectory of your repository, as ordinary files and commits. git subtree add --prefix=vendor/lib <url> <branch> --squash fetches the project and merges it under that prefix, optionally squashing its history into one commit. git subtree pull --prefix=... updates it later, and git subtree push or git subtree split extracts the commits that touched the prefix so you can contribute changes upstream. Because the code is just part of the parent repository, cloning, branching and CI need no special handling, unlike submodules. The trade-offs are a larger repository, merges of upstream history into yours, and the need to remember the prefix and remote for each pull. git subtree ships in Git's contrib directory and is installed by most packages. The underlying idea, a subtree merge (git merge -s subtree or -X subtree=<path>), is also available directly.",
        ["Vendoring a library that you occasionally patch.", "Extracting a directory into its own repository with split.", "Combining small repositories into a monorepo."],
        [
            "Code lives in the parent as normal files.",
            "add / pull / push / split with --prefix.",
            "--squash keeps upstream history out of yours.",
            "No extra steps for people who clone.",
            "split can extract a directory's history into a new repo.",
        ],
        [
            ex("Add and update a subtree", "advanced", "Vendor a library under vendor/parser.", "bash", """
                git remote add parser https://github.com/example/parser.git
                git subtree add --prefix=vendor/parser parser main --squash
                git subtree pull --prefix=vendor/parser parser main --squash
            """, runnable=False),
            ex("Contribute back or extract", "advanced", "Split commits under a prefix into a branch.", "bash", """
                git subtree push --prefix=vendor/parser parser fix/unicode
                git subtree split --prefix=services/billing -b billing-only
                git push git@github.com:example/billing.git billing-only:main
            """, runnable=False),
        ],
        ["git subtree add --prefix=<dir> <repo> <ref> --squash", "git subtree pull --prefix=<dir> <repo> <ref> --squash", "git subtree push --prefix=<dir> <repo> <ref>", "git subtree split --prefix=<dir> -b <branch>"],
        ["Mixing commits that touch the subtree and the parent makes split output messy.", "Forgetting --squash on pull after adding with --squash causes confusing merges.", "Large upstream histories bloat the parent repo without --squash."],
        [
            qa("intermediate", "What is a Git subtree?", "A way to include another repository's content in a subdirectory of yours as ordinary tracked files, with commands to pull upstream updates and push or split local changes back."),
            qa("intermediate", "Subtree vs submodule: main difference?", "A submodule stores only a pointer to a commit in another repo and needs extra commands to fetch. A subtree copies the content into your history, so clones just work but the repository grows."),
            qa("advanced", "What does git subtree split do?", "It walks history and synthesises a new line of commits containing only changes under the given prefix, rewritten as if that directory were the root. You can push that branch to a new repository."),
            qa("advanced", "What does --squash do in git subtree add/pull?", "It merges upstream changes as a single squashed commit instead of importing the full upstream history, keeping your log small while still recording which upstream commit was included."),
        ],
        ["merging", "remotes", "workflows"],
        chain(
            ("Upstream", "parser repo", "External project", "A library lives in its own repository."),
            ("subtree add", "--prefix=vendor/", "Import", "Its content is merged into vendor/parser.", "add"),
            ("Parent repo", "normal files", "Use", "Teammates clone and build with no extra steps.", "clone"),
            ("subtree pull", "upstream updates", "Update", "Pull upstream changes into the prefix later.", "pull"),
            ("split / push", "changes upstream", "Contribute", "Extract prefix commits and push them back.", "push"),
        ),
    ),
    topic(
        "sparse-partial", "Sparse Checkout & Partial Clone", "scale", "advanced", "SP",
        "Download and check out only the parts of a huge repository you actually need.",
        "A streaming service instead of buying every DVD: you get the catalogue immediately and episodes download only when you press play.",
        "Partial clone reduces what is downloaded: git clone --filter=blob:none (blobless) fetches all commits and trees but downloads file contents only when they are needed, for example on checkout; --filter=tree:0 (treeless) also defers trees. The server becomes a promisor remote that Git contacts on demand, so some commands like blame on old history trigger downloads. Sparse checkout reduces what is written to disk: git sparse-checkout set <dirs> limits the working tree to those directories, and cone mode (the default) matches whole directories, which is much faster than arbitrary patterns. Combining them, git clone --filter=blob:none --sparse <url> followed by git sparse-checkout set services/api gives a fast, small checkout of one area of a monorepo. git sparse-checkout add, list and disable adjust it later. Sparse index support keeps git status fast even with millions of files. Scalar, bundled with Git, configures these features plus background maintenance for very large repositories.",
        ["Working on one service inside a large monorepo.", "Reducing clone time and disk usage on developer laptops.", "Speeding up CI jobs that need only part of the tree."],
        [
            "Partial clone (--filter) limits downloaded objects.",
            "Sparse checkout limits files written to disk.",
            "Blobless clones fetch file contents on demand.",
            "Cone mode matches directories and is fast.",
            "Scalar sets up both plus maintenance.",
        ],
        [
            ex("Blobless sparse clone of a monorepo", "advanced", "Only services/api and shared libs.", "bash", """
                git clone --filter=blob:none --sparse https://github.com/example/monorepo.git
                cd monorepo
                git sparse-checkout set services/api libs/common
                git sparse-checkout add tools/lint
                git sparse-checkout list
            """, runnable=False),
            ex("Inspect and undo", "advanced", "See the filter and widen the checkout.", "bash", """
                git config remote.origin.partialclonefilter
                git sparse-checkout disable
                scalar clone https://github.com/example/monorepo.git
            """, runnable=False),
        ],
        ["git clone --filter=blob:none <url>", "git clone --filter=blob:none --sparse <url>", "git sparse-checkout set <dirs>", "git sparse-checkout add <dir>", "git sparse-checkout disable", "scalar clone <url>"],
        ["Commands that need old blobs (blame, log -p) trigger many on-demand fetches and need network access.", "Treeless clones are poor for daily development because many commands need trees.", "Tools that scan the whole repo may misbehave with files missing from the working tree."],
        [
            qa("intermediate", "Sparse checkout vs partial clone?", "Sparse checkout controls which files appear in the working tree. Partial clone controls which objects are downloaded from the server. They are independent but often combined."),
            qa("advanced", "What is a blobless clone?", "git clone --filter=blob:none downloads all commits and trees but no file contents up front; blobs are fetched lazily when a command needs them. It keeps full history available while greatly reducing clone size."),
            qa("advanced", "What is cone mode in sparse checkout?", "A restricted pattern mode where you list directories and Git includes them recursively plus top-level files. Matching by directory prefix is much faster than gitignore-style patterns and enables the sparse index."),
            qa("advanced", "Why might a partial clone be slow for git blame?", "Blame needs old versions of the file, which were not downloaded. Git fetches each missing blob from the promisor remote on demand, which can mean many round trips."),
        ],
        ["internals", "remotes", "workflows"],
        chain(
            ("Monorepo", "huge server repo", "Too big", "The full repo is many gigabytes."),
            ("Partial clone", "--filter=blob:none", "Fetch less", "Commits and trees arrive; file contents are deferred.", "filter"),
            ("Sparse set", "services/api", "Check out less", "sparse-checkout set limits the working tree.", "sparse"),
            ("On demand", "promisor fetch", "Lazy fetch", "Needed blobs download automatically from the promisor remote.", "fetch"),
        ),
    ),
    topic(
        "shallow-clones", "Shallow Clones", "scale", "intermediate", "SL",
        "Fetch only recent history, mainly for CI and quick throwaway checkouts.",
        "Reading only the last few pages of a diary: quick, but you cannot answer questions about what happened earlier.",
        "git clone --depth <n> fetches only the latest n commits of each requested branch, cutting off history at a shallow boundary recorded in .git/shallow. It implies --single-branch unless you pass --no-single-branch. --shallow-since=<date> and --shallow-exclude=<ref> choose the cut-off by date or ref instead. Later, git fetch --deepen=<n> extends history and git fetch --unshallow converts it into a full clone. Shallow clones are popular in CI because they download very little, and many CI systems default to a depth of 1. The cost is that anything needing older history breaks or misleads: merge-base computations against main, git describe without reachable tags, blame, bisect and some changelog tools. Pushing from a shallow clone usually works, but the server may reject or slow down some operations. For developer machines a blobless partial clone is usually a better compromise, since it keeps full commit history.",
        ["Fast CI checkouts that only build the tip.", "Quickly grabbing source code for one release.", "Reducing bandwidth on constrained environments."],
        [
            "--depth 1 fetches only the tip commit.",
            "Implies --single-branch by default.",
            "--deepen and --unshallow extend history.",
            "describe, merge-base and blame can fail.",
            "Prefer --filter=blob:none for daily development.",
        ],
        [
            ex("Shallow CI checkout", "intermediate", "Tip only, then deepen when needed.", "bash", """
                git clone --depth 1 --branch main https://github.com/example/app.git
                git rev-parse --is-shallow-repository
                git fetch --deepen=50
                git fetch --unshallow
            """, runnable=False),
            ex("Fix describe and diff in CI", "intermediate", "Fetch tags and the base branch for comparisons.", "bash", """
                git fetch --depth=1 origin main
                git fetch --shallow-since="2026-01-01" origin main
                git fetch --tags --unshallow
                git describe --tags
            """, runnable=False),
        ],
        ["git clone --depth 1 <url>", "git clone --shallow-since=<date> <url>", "git fetch --deepen=<n>", "git fetch --unshallow", "git rev-parse --is-shallow-repository"],
        ["CI diffs against origin/main fail with 'no merge base' in shallow clones.", "git describe fails when the tag is beyond the shallow boundary.", "Only one branch is fetched; other remote branches seem missing."],
        [
            qa("basic", "What is a shallow clone?", "A clone created with --depth (or --shallow-since) that contains only recent commits. Older history is cut off at a boundary recorded in .git/shallow."),
            qa("intermediate", "Why does git describe fail in CI?", "CI often clones with depth 1, so the nearest tag is not in the local history. Fetch tags and enough history (or unshallow) before running describe."),
            qa("intermediate", "How do you turn a shallow clone into a full one?", "git fetch --unshallow downloads the remaining history. git fetch --deepen=<n> adds a fixed number of commits instead."),
            qa("advanced", "Shallow clone vs blobless partial clone for developers?", "Shallow clones lack history, breaking merge-base, blame and bisect. Blobless clones keep all commits and trees and only defer file contents, so history commands work at the cost of on-demand downloads."),
        ],
        ["remotes", "internals"],
        chain(
            ("Full history", "10,000 commits", "Server", "The remote has years of history."),
            ("--depth 1", "tip only", "Shallow clone", "Only the latest commit and its tree are fetched.", "clone"),
            ("Boundary", ".git/shallow", "Cut-off", "Parents beyond the boundary are unknown locally.", "graft"),
            ("Deepen", "--unshallow", "Extend", "Fetch more history when a command needs it.", "fetch"),
        ),
    ),
]

TOPICS += [
    topic(
        "git-lfs", "Git LFS", "scale", "intermediate", "LF",
        "Store large binaries outside Git history, with small pointer files in the repo.",
        "A coat check: the repository keeps only the numbered ticket, and the heavy coat is stored in a separate room until you ask for it.",
        "Git LFS (Large File Storage) is an extension that replaces large files such as videos, design files, datasets and model weights with small text pointer files containing a SHA-256 oid and the size. The real content is uploaded to an LFS server (usually provided by the hosting platform) on push and downloaded on checkout via Git's clean and smudge filters. git lfs install sets up the filters once per user, and git lfs track \"*.psd\" writes the matching rule into .gitattributes, which must be committed. Because history only contains pointers, clones stay small and Git's packfiles avoid repeated multi-megabyte binary deltas. Files committed before tracking remain as normal blobs; git lfs migrate import --include=\"*.zip\" --everything rewrites history to convert them, which requires a coordinated force-push. git lfs ls-files shows which files are managed, GIT_LFS_SKIP_SMUDGE=1 clones pointers without downloading content, and git lfs lock supports exclusive editing of unmergeable files. Hosting providers apply storage and bandwidth quotas, so track only what needs it.",
        ["Game assets, design files and videos in a project repo.", "Machine-learning model weights next to code.", "Avoiding repository bloat from frequently changing binaries."],
        [
            "Repo stores pointer files; content lives on the LFS server.",
            "git lfs track writes .gitattributes; commit it.",
            "Existing history needs git lfs migrate to convert.",
            "Clean/smudge filters run on add and checkout.",
            "Watch hosting storage and bandwidth quotas.",
        ],
        [
            ex("Track large files", "intermediate", "Set up LFS for design assets.", "bash", """
                git lfs install
                git lfs track "*.psd" "*.mp4"
                git add .gitattributes assets/hero.psd
                git commit -m "build: store design assets in LFS"
                git lfs ls-files
                git push
            """, runnable=False),
            ex("Migrate and partial download", "advanced", "Convert history and clone pointers only.", "bash", """
                git lfs migrate info --everything
                git lfs migrate import --include="*.zip" --everything
                git push --force-with-lease --all
                GIT_LFS_SKIP_SMUDGE=1 git clone https://github.com/example/game.git
                git lfs pull --include="levels/level1/**"
            """, runnable=False),
        ],
        ["git lfs install", "git lfs track \"*.ext\"", "git lfs ls-files", "git lfs pull · fetch", "git lfs migrate import --include=<glob>", "git lfs lock <file>"],
        ["Cloning without LFS installed leaves pointer text files in place of real content.", "Tracking a pattern after files were committed does not move existing history into LFS.", "CI jobs may download gigabytes on every run unless LFS content is cached or skipped."],
        [
            qa("basic", "What problem does Git LFS solve?", "Git keeps every version of every file in history, so large changing binaries bloat clones permanently. LFS stores the content externally and keeps only small pointers in history."),
            qa("intermediate", "What is stored in the repository for an LFS file?", "A small pointer file with the LFS spec version, the SHA-256 oid of the content and its size. The actual bytes live on the LFS server and are fetched by the smudge filter."),
            qa("intermediate", "You started tracking *.zip with LFS but the repo is still huge. Why?", "Tracking only affects new commits; old zips remain as regular blobs in history. git lfs migrate import --include=\"*.zip\" --everything rewrites history to move them, followed by a coordinated force-push."),
            qa("advanced", "Why might a teammate see text pointer files instead of images?", "Git LFS is not installed or its filters are not configured on their machine, or LFS content was skipped. Running git lfs install and git lfs pull fetches and checks out the real files."),
        ],
        ["internals", "three-trees"],
        chain(
            ("Big file", "hero.psd 200MB", "Large binary", "A designer adds a 200 MB file."),
            ("Clean filter", "upload content", "git add", "The LFS clean filter stores content and stages a pointer.", "clean"),
            ("Pointer", "oid sha256 + size", "Commit", "History stores only a tiny pointer file.", "commit"),
            ("LFS server", "object storage", "git push", "Content uploads to the LFS store.", "upload"),
            ("Smudge", "fetch on checkout", "Checkout", "Others get the real file via the smudge filter.", "smudge"),
        ),
    ),
    topic(
        "hooks", "Git Hooks (Client & Server)", "automation", "intermediate", "HK",
        "Scripts Git runs at key moments: before commits, before pushes, and on the server.",
        "Tripwires along a path: step on one and a script runs, possibly stopping you before you reach the next stage.",
        "Hooks are executables that Git runs at specific points, stored in .git/hooks or in a directory set by core.hooksPath. Client-side hooks include pre-commit (inspect staged changes), prepare-commit-msg and commit-msg (edit or validate the message), post-commit, post-checkout, post-merge, pre-rebase and pre-push (run before data is sent). A pre-* hook that exits non-zero aborts the operation. Server-side hooks run on the receiving repository: pre-receive can reject an entire push, update runs once per ref, and post-receive triggers notifications or deployments. Hooks are not copied by git clone for security reasons, so teams share them by committing a hooks directory and setting core.hooksPath, or through a manager like pre-commit or Husky. Client hooks can be bypassed with --no-verify, so anything that must be enforced belongs in server hooks, branch protection or CI. Keep hooks fast, since slow hooks get disabled.",
        ["Running linters and formatters before each commit.", "Validating commit message format.", "Rejecting pushes to protected refs or triggering deployments on the server."],
        [
            "pre-* hooks can abort by exiting non-zero.",
            "Hooks are not cloned; share via core.hooksPath or a manager.",
            "--no-verify skips client hooks.",
            "pre-receive and update enforce policy server-side.",
            "Hooks receive arguments and stdin describing the operation.",
        ],
        [
            ex("A simple pre-push hook", "intermediate", "Run tests before pushing; shared via core.hooksPath.", "bash", """
                mkdir -p .githooks
                cat > .githooks/pre-push <<'EOF'
                #!/usr/bin/env sh
                set -e
                echo "running tests before push..."
                make test
                EOF
                chmod +x .githooks/pre-push
                git config core.hooksPath .githooks
            """, runnable=False),
            ex("Server-side pre-receive policy", "advanced", "Reject force pushes to main.", "bash", """
                #!/usr/bin/env bash
                zero=0000000000000000000000000000000000000000
                while read old new ref; do
                  if [ "$ref" = "refs/heads/main" ] && [ "$old" != "$zero" ]; then
                    if ! git merge-base --is-ancestor "$old" "$new"; then
                      echo "rejected: non-fast-forward push to main" >&2
                      exit 1
                    fi
                  fi
                done
            """, runnable=False),
        ],
        ["ls .git/hooks", "git config core.hooksPath .githooks", "chmod +x .githooks/<hook>", "git commit --no-verify", "git push --no-verify"],
        ["A hook without the executable bit is silently ignored.", "Hooks that mutate files in pre-commit must re-stage them or the commit misses the fix.", "Never rely on client hooks for security; anyone can skip them."],
        [
            qa("basic", "What is a Git hook?", "An executable script Git runs automatically at certain events such as before a commit or after a push is received. Exiting non-zero from a pre-* hook cancels the operation."),
            qa("intermediate", "Why aren't hooks included when you clone a repo?", "Automatically running scripts from a cloned repository would let anyone execute code on your machine. Teams share hooks explicitly with core.hooksPath or a hook manager that each developer installs."),
            qa("intermediate", "pre-commit vs pre-push: which to use for what?", "pre-commit should be fast checks on staged files like formatting and linting. pre-push suits slower checks such as unit tests, since it runs less often."),
            qa("advanced", "How do you enforce a rule developers cannot bypass?", "Enforce it on the server: a pre-receive or update hook, branch protection rules, or required CI status checks. Client-side hooks can always be skipped with --no-verify."),
        ],
        ["workflows", "three-trees"],
        chain(
            ("git commit", "staged files", "Trigger", "You run git commit."),
            ("pre-commit", "lint / format", "Check", "The hook inspects staged files; non-zero exit aborts.", "hook"),
            ("commit-msg", "validate message", "Message", "commit-msg validates the message format.", "msg"),
            ("pre-push", "run tests", "Before push", "pre-push runs tests before anything is sent.", "push"),
            ("pre-receive", "server policy", "Server", "The server can still reject the push.", "receive"),
        ),
    ),
    topic(
        "pre-commit", "The pre-commit Framework", "automation", "intermediate", "PC",
        "Declare versioned hooks in one YAML file and run the same checks locally and in CI.",
        "A shared checklist pinned to the wall with exact tool versions, so everyone's pre-flight inspection is identical.",
        "pre-commit is a popular multi-language framework for managing Git hooks. A .pre-commit-config.yaml lists repositories of hooks, each pinned to a rev (tag or commit), and the hook ids to run, such as trailing-whitespace, end-of-file-fixer, check-added-large-files, detect-private-key, ruff, black or gitleaks for secret detection. pre-commit install writes a small .git/hooks/pre-commit shim; each tool is installed into an isolated, cached environment the first time. By default hooks run only on staged files, keeping commits fast, while pre-commit run --all-files checks the whole repository, which is exactly what CI should run so the check cannot be bypassed. pre-commit autoupdate bumps pinned revisions, and stages: lets a hook run at commit-msg or pre-push instead. Hooks that modify files fail the commit so you can review and re-stage the fixes. Similar tools exist in other ecosystems, such as Husky with lint-staged for JavaScript and Lefthook.",
        ["Consistent formatting and linting across a team.", "Blocking private keys and secrets before they reach history.", "Running identical checks locally and in CI."],
        [
            "Config lives in .pre-commit-config.yaml with pinned revs.",
            "pre-commit install sets up the Git hook shim.",
            "run --all-files in CI makes checks unskippable.",
            "Fixer hooks fail the commit; re-stage and commit again.",
            "autoupdate keeps hook versions current.",
        ],
        [
            ex("A starter config", "intermediate", "Basic hygiene, Python linting and secret scanning.", "bash", """
                cat > .pre-commit-config.yaml <<'EOF'
                repos:
                  - repo: https://github.com/pre-commit/pre-commit-hooks
                    rev: v5.0.0
                    hooks:
                      - id: trailing-whitespace
                      - id: end-of-file-fixer
                      - id: check-added-large-files
                      - id: detect-private-key
                  - repo: https://github.com/astral-sh/ruff-pre-commit
                    rev: v0.6.9
                    hooks:
                      - id: ruff
                      - id: ruff-format
                  - repo: https://github.com/gitleaks/gitleaks
                    rev: v8.21.2
                    hooks:
                      - id: gitleaks
                EOF
                pre-commit install
                pre-commit run --all-files
            """, runnable=False),
            ex("Run in CI and update", "intermediate", "Same checks on every push.", "bash", """
                pip install pre-commit
                pre-commit run --all-files --show-diff-on-failure
                pre-commit autoupdate
                pre-commit install --hook-type commit-msg
            """, runnable=False),
        ],
        ["pre-commit install", "pre-commit run --all-files", "pre-commit run <hook-id>", "pre-commit autoupdate", "SKIP=<hook-id> git commit"],
        ["Unpinned or floating revs make results change unexpectedly; pin and autoupdate deliberately.", "Developers who never ran pre-commit install get no local checks; CI must run it too.", "Heavy hooks on every commit encourage --no-verify; move slow ones to pre-push or CI."],
        [
            qa("basic", "What does the pre-commit framework provide over raw hooks?", "A declarative, versioned config shared in the repo, automatic installation of each tool in an isolated environment, and running only on staged files. Everyone gets identical checks."),
            qa("intermediate", "Why run pre-commit in CI as well?", "Local hooks are opt-in and can be skipped with --no-verify. Running pre-commit run --all-files in CI makes the checks mandatory before merge."),
            qa("intermediate", "A hook reformatted files and the commit failed. What now?", "That is intended: review the changes, git add the fixed files and commit again. The hook fails so modifications are never committed without you seeing them."),
            qa("intermediate", "How can pre-commit help prevent leaked credentials?", "Hooks like detect-private-key and gitleaks scan staged changes for key blocks and token patterns and block the commit. Combine them with server-side secret scanning and push protection."),
        ],
        ["workflows", "three-trees"],
        chain(
            ("Config", "pre-commit.yaml", "Declare", "The repo declares hooks with pinned versions."),
            ("Install", "hook shim", "Set up", "pre-commit install adds the Git hook.", "install"),
            ("Commit", "staged files only", "Run", "On commit, hooks run on staged files.", "commit"),
            ("Fix / block", "fail on issues", "Result", "Problems or auto-fixes stop the commit for review.", "check"),
            ("CI", "--all-files", "Enforce", "CI runs all hooks on every file.", "ci"),
        ),
    ),
    topic(
        "signing-commits", "Signing Commits & Tags (SSH / GPG)", "automation", "advanced", "SG",
        "Prove that commits and tags really came from you, with SSH or GPG signatures.",
        "Anyone can write your name on an envelope; a wax seal from your own signet ring is what proves the letter is really yours.",
        "Git's author and committer fields are free text, so anyone can create commits that claim to be from you. Signing attaches a cryptographic signature to the commit or tag object that others can verify. Since Git 2.34 you can sign with an SSH key: set gpg.format=ssh, user.signingkey to your public key file (an ed25519 key is a good choice, ideally a hardware-backed ed25519-sk key), and commit.gpgsign=true and tag.gpgSign=true to sign everything. Verification uses an allowed signers file (gpg.ssh.allowedSignersFile) mapping emails to keys. GPG signing works the same way with gpg.format=openpgp and a modern key such as ed25519 or RSA 4096. git log --show-signature, git verify-commit and git verify-tag check signatures, and hosting platforms show a Verified badge when the key is registered and the email matches. A signature proves who created the object and that it has not been altered, not that the code is good. Keep private keys out of repositories, protect them with a passphrase or hardware token, and branch protection can require signed commits on main.",
        ["Meeting supply-chain requirements for signed releases.", "Requiring signed commits on protected branches.", "Preventing impersonation via forged author fields."],
        [
            "Author fields are unverified text; signatures are proof.",
            "SSH signing: gpg.format=ssh with an ed25519 key.",
            "commit.gpgsign=true signs every commit.",
            "Verify with git log --show-signature or verify-commit.",
            "Rebasing or amending re-signs with your key.",
        ],
        [
            ex("Sign with an SSH key", "advanced", "Generate an ed25519 key and sign everything.", "bash", """
                ssh-keygen -t ed25519 -C "ada@example.com" -f ~/.ssh/id_ed25519_signing
                git config --global gpg.format ssh
                git config --global user.signingkey ~/.ssh/id_ed25519_signing.pub
                git config --global commit.gpgsign true
                git config --global tag.gpgSign true
                echo "ada@example.com $(cat ~/.ssh/id_ed25519_signing.pub)" >> ~/.config/git/allowed_signers
                git config --global gpg.ssh.allowedSignersFile ~/.config/git/allowed_signers
                git commit -m "feat: signed commit"
                git log --show-signature -1
            """, runnable=False),
            ex("GPG alternative and verification", "advanced", "Modern GPG key and verify commands.", "bash", """
                gpg --quick-generate-key "Ada Lovelace <ada@example.com>" ed25519 sign 2y
                gpg --list-secret-keys --keyid-format=long
                git config --global gpg.format openpgp
                git config --global user.signingkey <KEY-ID-PLACEHOLDER>
                git verify-commit HEAD
                git tag -s v2.4.0 -m "Release 2.4.0" && git verify-tag v2.4.0
            """, runnable=False),
        ],
        ["git config gpg.format ssh", "git config user.signingkey <pubkey>", "git config commit.gpgsign true", "git commit -S", "git log --show-signature", "git verify-commit · verify-tag"],
        ["The commit email must match a verified email on your hosting account or the badge shows Unverified.", "Squash or rebase merges done by the platform are signed by the platform, not by you.", "Losing the private key means old signatures still verify but you must register a new key for new commits."],
        [
            qa("intermediate", "Why sign commits when Git already records the author?", "Author and committer fields are plain text that anyone can set to any name. A signature cryptographically proves the commit was created by the holder of a specific key and has not been modified."),
            qa("intermediate", "How do you sign commits with an SSH key?", "Set gpg.format=ssh, user.signingkey to the public key path, and commit.gpgsign=true (or use git commit -S). For local verification configure gpg.ssh.allowedSignersFile mapping emails to keys."),
            qa("advanced", "What does a signature on a commit actually cover?", "It signs the commit object: tree id, parent ids, author, committer and message. Since the tree id transitively covers every file, the signature protects the full snapshot and its ancestry links."),
            qa("advanced", "What key types would you recommend for signing?", "An SSH ed25519 key, ideally hardware-backed (ed25519-sk on a security key), or a GPG key using ed25519 or RSA 4096. Protect it with a passphrase or hardware, and never store private keys in a repository."),
        ],
        ["internals", "workflows"],
        chain(
            ("Commit object", "tree + parents", "Create", "Git builds the commit object."),
            ("Private key", "ed25519 (SSH)", "Sign", "Your private key signs the commit contents.", "sign"),
            ("Signature", "in commit header", "Embed", "The signature is stored in the commit object.", "gpgsig"),
            ("Verify", "allowed signers", "Check", "Others verify against your registered public key.", "verify"),
            ("Verified", "badge / policy", "Trust", "Platforms show Verified and can require it on main.", "enforce"),
        ),
    ),
    topic(
        "secrets-history", "Secrets in History", "automation", "advanced", "SE",
        "A committed secret is leaked: rotate it first, then purge history and prevent repeats.",
        "Posting your house key in a public photo album: deleting the photo later does not help much, because someone may already have copied the key. Change the lock first.",
        "Once a credential is committed and pushed, assume it is compromised: clones, forks, CI caches and automated scanners may already have it. The first step is always to revoke or rotate the credential at its provider and check access logs. Removing it in a new commit is not enough because every earlier commit still contains it. To purge it, rewrite history with git filter-repo (the tool recommended by the Git project; git filter-branch is deprecated), for example --invert-paths --path config/secrets.env to drop a file or --replace-text with a list of strings to redact. Then force-push all rewritten branches and tags, ask collaborators to re-clone rather than merge old history back, and ask the hosting provider to purge cached views and pull request refs if needed. Forks and existing clones keep the old commits, which is why rotation matters more than rewriting. Prevent recurrences with .gitignore for env files, pre-commit secret scanners such as gitleaks, server-side secret scanning with push protection, and secrets loaded from a vault or environment at runtime instead of source code.",
        ["Responding to an API key accidentally pushed to a public repo.", "Removing a large or sensitive file from all history.", "Setting up guardrails so it does not happen again."],
        [
            "Rotate or revoke the credential first; rewriting is secondary.",
            "git filter-repo replaces filter-branch.",
            "Force-push every rewritten branch and tag.",
            "Collaborators must re-clone; forks keep old copies.",
            "Prevent with gitleaks, push protection and a secrets manager.",
        ],
        [
            ex("Purge a file from all history", "advanced", "After rotating the credential.", "bash", """
                # 1. Rotate/revoke the credential at the provider FIRST.
                git clone --mirror https://github.com/example/app.git app-clean.git
                cd app-clean.git
                git filter-repo --invert-paths --path config/secrets.env
                git push --force --mirror origin
            """, runnable=False),
            ex("Redact a string everywhere", "advanced", "Replace a leaked value with a placeholder.", "bash", """
                echo "EXAMPLE-ONLY-not-a-real-secret==>REDACTED" > replacements.txt
                git filter-repo --replace-text replacements.txt
                git log -S"EXAMPLE-ONLY-not-a-real-secret" --all --oneline   # should print nothing
                echo ".env" >> .gitignore
                gitleaks detect --source . --redact
            """, runnable=False),
        ],
        ["git filter-repo --invert-paths --path <file>", "git filter-repo --replace-text <file>", "git push --force --mirror", "git log -S<value> --all", "gitleaks detect --redact"],
        ["Rewriting history without rotating leaves a valid credential in every existing clone and fork.", "A teammate merging their old branch reintroduces the purged commits.", "filter-repo removes the origin remote by design; re-add it deliberately before pushing."],
        [
            qa("basic", "You pushed an API key to a public repo. What is the first thing you do?", "Revoke or rotate the key at the provider immediately and review its usage logs. Bots scan public repos within minutes, so cleanup of history comes after the credential is invalidated."),
            qa("intermediate", "Why isn't deleting the file in a new commit enough?", "Previous commits still contain the file and anyone can check them out or search them with git log -S. The secret remains in every clone, fork and cached copy."),
            qa("advanced", "How do you remove a secret from Git history?", "Use git filter-repo (--invert-paths --path <file> or --replace-text) on a fresh mirror clone, force-push all refs, ask collaborators to re-clone, and request the host purge cached data. BFG Repo-Cleaner is an alternative; filter-branch is deprecated."),
            qa("intermediate", "How do you prevent secrets from being committed?", "Keep secrets in a vault or environment variables, ignore env files, run a secret scanner (gitleaks, detect-secrets) as a pre-commit hook and in CI, and enable server-side secret scanning with push protection."),
        ],
        ["three-trees", "undoing", "interactive-rebase"],
        chain(
            ("Leak", "key in commit", "Detected", "A credential was pushed in a commit."),
            ("Rotate", "revoke at provider", "Contain", "Invalidate the credential first; check access logs.", "revoke"),
            ("filter-repo", "rewrite history", "Purge", "Remove or redact it from every commit.", "rewrite"),
            ("Force-push", "all refs", "Publish", "Push rewritten branches and tags; teammates re-clone.", "push"),
            ("Prevent", "scanners + vault", "Guardrails", "Add gitleaks, push protection and a secrets manager.", "guard"),
        ),
    ),
    topic(
        "pr-code-review", "Pull Requests, Code Review & Protected Branches", "collab", "intermediate", "CR",
        "Gate changes to main behind reviews and checks the platform enforces.",
        "A bank vault with two-person rule: nobody, not even the manager, opens it alone, and the alarm system (CI) must be green first.",
        "A pull request (merge request on GitLab) proposes merging a branch and becomes the place for discussion, review and automated checks. Protected branch rules on the hosting platform enforce policy on main: require pull requests, a minimum number of approvals, approval from CODEOWNERS for the paths touched, passing required status checks, an up-to-date branch or a merge queue, linear history or signed commits, and no force pushes or deletions. CODEOWNERS files map paths to responsible teams so the right reviewers are requested automatically. A merge queue tests each PR against the latest main plus the PRs ahead of it, preventing 'green PR, red main' races. Good PRs are small, focused and described with context, testing notes and links to issues; draft PRs signal work in progress. Reviewers look for correctness, tests, security and clarity rather than style that a linter could catch. The platform's merge button then applies the team's chosen method: merge commit, squash or rebase.",
        ["Requiring at least one approval and green CI before merging.", "Routing reviews to owners of sensitive directories.", "Preventing force pushes and direct commits to main."],
        [
            "Protect main: PRs required, no force push, no deletion.",
            "Required status checks must pass before merge.",
            "CODEOWNERS auto-requests the right reviewers.",
            "Merge queues prevent semantic merge races.",
            "Small PRs get faster, better reviews.",
        ],
        [
            ex("Typical PR workflow", "basic", "Branch, push, open a PR, update after review.", "bash", """
                git switch -c feat/search-filters
                git commit -am "feat(search): add date filters"
                git push -u origin feat/search-filters
                gh pr create --fill --draft
                git commit --fixup=HEAD
                git rebase -i --autosquash origin/main
                git push --force-with-lease
                gh pr ready
            """, runnable=False),
            ex("CODEOWNERS", "intermediate", "Route reviews by path.", "bash", """
                cat > .github/CODEOWNERS <<'EOF'
                *                @example/maintainers
                /infra/          @example/platform-team
                /src/payments/   @example/payments-team
                *.sql            @example/dba
                EOF
                git add .github/CODEOWNERS
                git commit -m "chore: add CODEOWNERS"
            """, runnable=False),
        ],
        ["gh pr create --fill", "gh pr checkout <n>", "gh pr review --approve", "gh pr merge --squash", "git fetch origin pull/<n>/head:pr-<n>"],
        ["Admins bypassing protection rules undermines the whole policy; include administrators.", "Requiring 'up to date with main' without a merge queue causes endless rebase loops on busy repos.", "Huge PRs get rubber-stamped instead of reviewed."],
        [
            qa("basic", "What is a protected branch?", "A branch with platform-enforced rules, such as requiring pull requests, approvals and passing checks, and blocking force pushes and deletion. It prevents unreviewed or broken changes from reaching main."),
            qa("intermediate", "What does a CODEOWNERS file do?", "It maps file patterns to users or teams. When a PR touches matching paths those owners are requested as reviewers, and branch protection can require their approval."),
            qa("intermediate", "What problem does a merge queue solve?", "Two PRs can each pass CI against an old main but break when combined. A merge queue tests each PR on top of the latest main plus queued PRs and merges only if that combination passes."),
            qa("intermediate", "What makes a pull request easy to review?", "A single focused change, a clear description of why and how it was tested, a reasonable size, tidy commits, and passing automated checks so reviewers can focus on design and correctness."),
        ],
        ["workflows", "remotes", "interactive-rebase"],
        chain(
            ("Branch", "feat/search", "Work", "Develop on a short-lived branch."),
            ("Pull request", "description + diff", "Propose", "Push and open a PR for discussion.", "push"),
            ("CI checks", "required, green", "Verify", "Required status checks run automatically.", "ci"),
            ("Review", "CODEOWNERS approve", "Approve", "Owners review and approve.", "review"),
            ("Protected main", "merge queue", "Merge", "The merge queue merges it into protected main.", "merge"),
        ),
    ),
    topic(
        "trunk-based", "Trunk-Based Development", "collab", "intermediate", "TB",
        "Integrate into main at least daily, hide unfinished work behind feature flags.",
        "A relay where runners hand off the baton every lap instead of each running a marathon alone and trying to sync up at the end.",
        "Trunk-based development means all developers integrate small changes into a single shared branch (trunk, usually main) very frequently, at least once a day, either by direct commits in small teams or through short-lived branches and pull requests that live a day or two. Because branches never drift far, merge conflicts stay small and continuous integration actually means integrating continuously. Unfinished features are merged behind feature flags or developed with branch by abstraction, so main is always releasable. It depends on a fast, reliable automated test suite, code review that keeps up, and the discipline to keep main green; a broken main is fixed or reverted immediately. Releases are cut from main directly (continuous delivery) or from short-lived release branches created from main, with fixes landed on main first and cherry-picked. It contrasts with GitFlow's long-lived develop and feature branches, which suit scheduled releases but delay integration. Research such as the DORA reports associates trunk-based practices with higher delivery performance.",
        ["Teams doing continuous delivery to production.", "Reducing painful merges from long-lived feature branches.", "Large engineering organisations working in a monorepo."],
        [
            "Branches live hours or a day or two, not weeks.",
            "Feature flags decouple deploy from release.",
            "main must always be green and releasable.",
            "Fix forward or revert immediately when main breaks.",
            "Release branches, if any, are cut from main and short-lived.",
        ],
        [
            ex("A day on trunk", "intermediate", "Small branch, quick PR, flag-guarded feature.", "bash", """
                git switch main && git pull --ff-only
                git switch -c tb/flag-new-checkout
                git commit -am "feat(checkout): new flow behind NEW_CHECKOUT flag (off)"
                git push -u origin tb/flag-new-checkout
                gh pr create --fill
                # merged the same day; enable the flag gradually in production
            """, runnable=False),
            ex("Release from trunk", "intermediate", "Cut a release branch and land fixes on main first.", "bash", """
                git switch -c release/2.4 origin/main
                git push -u origin release/2.4
                # fix lands on main as a1b2c3d, then:
                git switch release/2.4
                git cherry-pick -x a1b2c3d
                git tag -a v2.4.1 -m "Release 2.4.1"
            """, runnable=False),
        ],
        ["git pull --ff-only", "git switch -c <short-branch>", "git push -u origin <branch>", "git revert <sha> (keep main green)", "git cherry-pick -x <sha>"],
        ["Feature flags left in the code forever become technical debt; remove them after rollout.", "Without fast CI, frequent merges just break main more often.", "Long-lived 'trunk-based' branches are just feature branches with a new name."],
        [
            qa("basic", "What is trunk-based development?", "A branching model where everyone integrates small changes into one main branch very frequently, using at most short-lived branches. main is kept always releasable."),
            qa("intermediate", "How do you merge unfinished features into main safely?", "Hide them behind feature flags (off by default) or use branch by abstraction, so the code is integrated and tested but not exposed to users until it is ready."),
            qa("intermediate", "Trunk-based development vs GitFlow?", "GitFlow uses long-lived develop and feature branches plus release and hotfix branches, suited to scheduled versioned releases. Trunk-based keeps one main line with short branches, enabling continuous integration and delivery but requiring strong automation."),
            qa("advanced", "What prerequisites does trunk-based development need?", "A fast and reliable automated test suite, required CI checks, quick code reviews, feature flag infrastructure, and a culture of fixing or reverting a broken main immediately."),
        ],
        ["workflows", "merging", "rebase"],
        chain(
            ("main", "always green", "Trunk", "Everyone integrates into main."),
            ("Short branch", "hours to a day", "Small change", "A tiny branch or direct commit.", "branch"),
            ("CI + review", "fast checks", "Validate", "Automated tests and a quick review.", "pr"),
            ("Merge", "behind a flag", "Integrate", "Merge the same day, feature flag off.", "merge"),
            ("Release", "flag on / deploy", "Ship", "Deploy main and turn the flag on gradually.", "deploy"),
        ),
    ),
    topic(
        "release-semver", "Release Branching, SemVer & Cherry-pick Ranges", "collab", "intermediate", "RL",
        "Version releases meaningfully, stabilise them on release branches and backport fixes.",
        "A publisher prints edition 2.3 from a frozen manuscript; corrections go into the master copy first, and only the urgent ones are pasted into the printed edition.",
        "Semantic Versioning uses MAJOR.MINOR.PATCH: bump MAJOR for incompatible API changes, MINOR for backwards-compatible features and PATCH for backwards-compatible fixes, with optional pre-release labels (2.4.0-rc.1) and build metadata (+build.7). A release branch such as release/2.3 is cut from main when a version enters stabilisation; only fixes land there while main continues with new work. The safest rule is 'fix on main first, then backport': cherry-pick the fix onto each supported release branch with git cherry-pick -x, which appends '(cherry picked from commit ...)' for traceability. Ranges can be backported with git cherry-pick A^..B (inclusive of A) or A..B (exclusive). Each release is marked with an annotated or signed tag (v2.3.1) that CI builds and publishes. Tools like release-please or semantic-release derive version bumps and changelogs from Conventional Commits. Long-lived support branches multiply backport work, so keep the number of supported versions small.",
        ["Maintaining 2.x while 3.0 is developed on main.", "Shipping a patch release with one urgent fix.", "Automating versions and changelogs from commit messages."],
        [
            "MAJOR breaking, MINOR features, PATCH fixes.",
            "Release branches stabilise; main keeps moving.",
            "Fix on main first, then cherry-pick -x to release branches.",
            "A^..B includes A; A..B excludes it.",
            "Tag every release; never move a published tag.",
        ],
        [
            ex("Cut a release and patch it", "intermediate", "Release branch, backport and tag.", "bash", """
                git switch -c release/2.3 v2.3.0
                git push -u origin release/2.3
                git cherry-pick -x 7c1e2a4
                git tag -a v2.3.1 -m "Release 2.3.1"
                git push origin release/2.3 v2.3.1
            """, runnable=False),
            ex("Backport a range", "advanced", "Pick several consecutive fixes, inclusive of the first.", "bash", """
                git log --oneline main -6
                git switch release/2.3
                git cherry-pick -x a1b2c3d^..f4e5d6c
                # on conflict: resolve, git add, git cherry-pick --continue
                git cherry-pick --abort
                git cherry -v release/2.3 main
            """, runnable=False),
        ],
        ["git switch -c release/X.Y <tag|main>", "git cherry-pick -x <sha>", "git cherry-pick A^..B", "git tag -a vX.Y.Z -m \"msg\"", "git cherry -v <upstream> <head>"],
        ["Fixing only on the release branch means the bug reappears in the next major version.", "Cherry-picks create new commits; Git does not know they are the same change, which can cause conflicts later.", "Marking a breaking change as MINOR breaks consumers who trust SemVer ranges."],
        [
            qa("basic", "What do the three numbers in SemVer mean?", "MAJOR changes break compatibility, MINOR adds backwards-compatible functionality and PATCH contains backwards-compatible bug fixes. 1.4.2 -> 2.0.0 signals consumers must review breaking changes."),
            qa("intermediate", "Why fix on main first and then backport?", "It guarantees the fix exists in every future release. Fixing only on a release branch risks the bug resurfacing when the next version is cut from main."),
            qa("intermediate", "What does cherry-pick -x add?", "A line '(cherry picked from commit <sha>)' in the new commit's message, linking the backport to the original commit for traceability."),
            qa("advanced", "How do you cherry-pick a range including its first commit?", "git cherry-pick A^..B, because A..B excludes A. Commits are applied oldest first, and you resolve conflicts with --continue or stop with --abort."),
        ],
        ["stash-cherry-pick", "workflows", "branches"],
        chain(
            ("main", "3.0 in progress", "Mainline", "New features continue on main."),
            ("release/2.3", "from v2.3.0", "Cut branch", "A release branch is created for stabilisation.", "branch"),
            ("Fix on main", "commit 7c1e2a4", "Fix first", "The bug is fixed on main.", "fix"),
            ("Cherry-pick", "-x to release", "Backport", "The fix is cherry-picked onto release/2.3.", "pick"),
            ("Tag v2.3.1", "build + publish", "Release", "Tag the patch release; CI publishes it.", "tag"),
        ),
    ),
    topic(
        "packfiles-gc", "Packfiles, gc & Maintenance", "internals", "advanced", "PK",
        "How Git compresses objects into packs, prunes garbage and stays fast over time.",
        "Moving from a desk covered in loose notes to a filing cabinet where similar documents are stored as one original plus small amendments.",
        "New objects are first written as loose files under .git/objects/xx/, each zlib-compressed and named by its object id (SHA-1 by default; repositories can be created with --object-format=sha256 as part of Git's SHA-256 transition). Periodically Git packs objects into a packfile (.pack) with an index (.idx); inside a pack, objects can be stored as deltas against similar objects, so many versions of a file cost little more than one. Packing also happens during fetch and push, since objects travel as packs. git gc packs loose objects, consolidates packs, packs refs into packed-refs, expires old reflog entries and prunes unreachable objects older than gc.pruneExpire. It runs automatically (gc --auto) when there are too many loose objects or packs. git maintenance start schedules background tasks instead: prefetch, commit-graph (speeds up history walks), loose-objects and incremental-repack with a multi-pack-index. git count-objects -vH reports repository size and git verify-pack -v shows delta chains.",
        ["Understanding why a repository is large.", "Keeping big repositories fast with background maintenance.", "Diagnosing slow log or status on huge histories."],
        [
            "Loose objects: one zlib file each; packs: many objects with deltas.",
            "gc packs, prunes unreachable objects and expires reflogs.",
            "commit-graph files make history traversal much faster.",
            "git maintenance start replaces manual gc for big repos.",
            "Object ids are SHA-1 by default; SHA-256 format exists.",
        ],
        [
            ex("Inspect storage", "advanced", "Sizes, packs and delta chains.", "bash", """
                git count-objects -vH
                ls .git/objects/pack/
                git verify-pack -v .git/objects/pack/pack-*.idx | sort -k3 -n | tail -5
                git rev-parse --show-object-format
            """, runnable=False),
            ex("Maintenance", "advanced", "Manual gc versus scheduled maintenance.", "bash", """
                git gc
                git commit-graph write --reachable
                git maintenance start
                git maintenance run --task=incremental-repack
                git config --get-regexp maintenance
            """, runnable=False),
        ],
        ["git count-objects -vH", "git gc", "git gc --aggressive (rarely)", "git maintenance start", "git commit-graph write --reachable", "git verify-pack -v <idx>"],
        ["git gc --prune=now removes the safety window for recovering lost work.", "--aggressive is slow and rarely helps; prefer normal gc or maintenance.", "Deleting a large file in a new commit does not shrink the repo; history still holds it."],
        [
            qa("intermediate", "What is a packfile?", "A single file storing many objects compressed together, where objects can be stored as deltas against similar objects. An accompanying .idx file maps object ids to offsets for fast lookup."),
            qa("intermediate", "What does git gc do?", "It packs loose objects and refs, consolidates packfiles, expires old reflog entries, and prunes unreachable objects older than the prune expiry. Git runs it automatically when thresholds are exceeded."),
            qa("advanced", "Why does storing many versions of a large text file not grow the repo linearly?", "In packfiles Git delta-compresses objects: similar blobs are stored as a base plus a delta of differences. Recent versions are typically stored whole and older ones as deltas."),
            qa("advanced", "What hash does Git use for object ids, and is it changing?", "SHA-1 by default, hardened with collision detection. Git also supports a SHA-256 object format (git init --object-format=sha256) as part of an ongoing transition, though interoperability with hosting services is still limited."),
        ],
        ["internals", "bisect-reflog"],
        chain(
            ("New objects", "loose, zlib", "Write", "Each new object is written as a loose zlib file."),
            ("Too many", "gc --auto", "Threshold", "Past a threshold, automatic gc kicks in.", "count"),
            ("Packfile", ".pack + .idx", "Pack", "Objects are packed together with delta compression.", "pack"),
            ("Prune", "unreachable old", "Clean", "Expired reflog entries and old unreachable objects go.", "prune"),
            ("Maintenance", "commit-graph etc.", "Stay fast", "Background tasks keep packs and graphs optimised.", "schedule"),
        ),
    ),
]

SCENARIOS = [
    {
        "level": "intermediate", "topic": "secrets-history",
        "q": "A developer pushed a cloud access key to a public repository an hour ago and then pushed a commit deleting the file. What do you do?",
        "a": "Treat the key as compromised: revoke or rotate it at the provider immediately and review its access logs, because the deletion commit leaves it in history and scanners find keys within minutes. Then purge it with git filter-repo on a mirror clone, force-push all refs, have collaborators re-clone, and ask the host to purge cached views. Finally add gitleaks as a pre-commit hook and enable push protection and server-side secret scanning.",
    },
    {
        "level": "intermediate", "topic": "recover-lost-work",
        "q": "After an interactive rebase went wrong, a teammate ran git reset --hard and now two days of commits are missing. Can you recover them?",
        "a": "Yes, very likely. Run git reflog to find the entry just before the rebase started (or use ORIG_HEAD), then git branch rescue <sha> to anchor it and inspect it. Avoid running git gc in the meantime. Only uncommitted, unstaged edits would be unrecoverable.",
    },
    {
        "level": "advanced", "topic": "force-with-lease",
        "q": "You force-pushed your rebased PR branch with --force-with-lease, yet a colleague's commit on that branch disappeared. How could that happen and how do you prevent it?",
        "a": "Your IDE likely fetched in the background, so origin/branch already pointed at the colleague's commit and the lease check passed. Recover their commit from their clone or the server's reflog and re-apply it. Prevent it with --force-if-includes (or an explicit --force-with-lease=branch:<sha>), and agree who owns rebasing shared PR branches.",
    },
    {
        "level": "intermediate", "topic": "squash-merge",
        "q": "Your PR B was branched from PR A. A was squash-merged into main and now rebasing B onto main produces conflicts in every file A touched. What is going on?",
        "a": "The squash commit has different ids from A's original commits, so Git tries to replay A's commits again on top of a main that already contains their changes. Rebase only B's own commits: git rebase --onto origin/main <old-tip-of-A> B, then push with --force-with-lease.",
    },
    {
        "level": "advanced", "topic": "sparse-partial",
        "q": "Cloning the company monorepo takes 40 minutes and 30 GB, but you only work on services/api. How do you make this practical without losing history?",
        "a": "Use a blobless partial clone with sparse checkout: git clone --filter=blob:none --sparse <url>, then git sparse-checkout set services/api libs/common. You keep full commit history for log and bisect while downloading file contents only for checked-out paths. Enable git maintenance start or use scalar clone to keep it fast.",
    },
    {
        "level": "intermediate", "topic": "revert-deep",
        "q": "A merged feature broke production, so you reverted its merge commit. A week later the fixed feature is merged again, but most of its code is missing. Why, and how do you fix it?",
        "a": "The original feature commits are still ancestors of main, so the second merge only brought in the new fix commits while the earlier revert kept the original changes removed. Revert the revert commit to reapply the original changes, then keep the fix merge on top, and verify the combined result in CI.",
    },
]
