"""cicd subject content."""

from ._dsl import chain, ex, qa, topic

CATEGORIES = [
    {"id": "foundations", "title": "Foundations", "color": "sky", "blurb": "What CI/CD is, branching, trunk-based work and pipelines as code."},
    {"id": "build-test", "title": "Build & Test", "color": "mint", "blurb": "Reproducible builds, caching, matrices, test stages and container images."},
    {"id": "pipelines", "title": "Pipeline Platforms", "color": "lilac", "blurb": "GitHub Actions, GitLab CI, Jenkins, Azure DevOps and CircleCI."},
    {"id": "artifacts-release", "title": "Artifacts & Release", "color": "lemon", "blurb": "Registries, versioning, changelogs, IaC, GitOps and promotion."},
    {"id": "deployment", "title": "Deployment Strategies", "color": "peach", "blurb": "Rolling, blue-green, canary, flags, migrations and gates."},
    {"id": "operations", "title": "Operations", "color": "slate", "blurb": "Rollback, DORA metrics, observability, cost and incidents."},
    {"id": "security", "title": "Supply-Chain Security", "color": "rose", "blurb": "Secrets, OIDC, SLSA, SBOMs, signing, scanning and runner hardening."},
]

_BATCH_1 = [
    topic(
        "ci-basics", "What CI/CD Really Means", "foundations", "basic", "CI",
        "Every change is built, tested and made releasable automatically, many times a day.",
        "A restaurant kitchen where every dish is tasted before it leaves the pass. Small plates go out constantly, so a bad one is caught at once instead of after a whole banquet has been cooked.",
        "Continuous Integration (CI) means every developer merges small changes into a shared mainline frequently, and each merge triggers an automated build and test run that tells the team within minutes whether the mainline still works. Continuous Delivery (CD) extends this so every green build produces a versioned, deployable artifact that could go to production at the push of a button. Continuous Deployment goes one step further and releases every green build to production automatically. The pipeline is the executable definition of this process: a sequence of stages (checkout, build, test, package, scan, deploy) run by a CI server or hosted service on every push or pull request. The value is fast feedback and small batch size: a failing test points at a change made an hour ago by one person, not a month of tangled work. CI/CD is a practice as much as a tool; a Jenkins server with a nightly build and week-long feature branches is not continuous integration. Good pipelines are versioned with the code, deterministic, fast (ideally under ten minutes for the main feedback loop) and treat a red mainline as the team's top priority.",
        ["Giving every pull request an automatic build and test result before review.", "Producing one immutable artifact per commit that later stages deploy.", "Releasing to production many times a day with low risk.", "Replacing manual release checklists with repeatable automation."],
        [
            "CI = integrate small changes often and verify each one automatically.",
            "Continuous delivery = always releasable; continuous deployment = always released.",
            "The pipeline is code stored in the repository and reviewed like code.",
            "Fast feedback (minutes) and a green mainline matter more than tool choice.",
            "Build once, then promote the same artifact through environments.",
        ],
        [
            ex("Minimal CI workflow (GitHub Actions)", "basic", "Build and test on every push and pull request with least-privilege permissions.", "yaml", """
                name: ci
                on:
                  push:
                    branches: [main]
                  pull_request:

                permissions:
                  contents: read

                concurrency:
                  group: ci-${{ github.ref }}
                  cancel-in-progress: true

                jobs:
                  test:
                    runs-on: ubuntu-latest
                    timeout-minutes: 15
                    steps:
                      - uses: actions/checkout@v4
                      - uses: actions/setup-python@v5
                        with:
                          python-version: "3.13"
                          cache: pip
                      - run: pip install -r requirements.txt
                      - run: pytest -q
            """, runnable=False),
            ex("Same idea in GitLab CI", "basic", "Two stages; the test job only runs if build succeeds.", "yaml", """
                stages: [build, test]

                build:
                  stage: build
                  image: python:3.13-slim
                  script:
                    - pip install build
                    - python -m build
                  artifacts:
                    paths: [dist/]

                test:
                  stage: test
                  image: python:3.13-slim
                  script:
                    - pip install -r requirements.txt
                    - pytest -q
            """, runnable=False),
        ],
        ["git push -> pipeline runs", "gh run list · gh run view --log-failed", "gh workflow run ci.yml", "gitlab-ci-lint (CI Lint page)", "Keep main green: fix or revert first"],
        ["A pipeline that takes an hour stops being feedback; people batch changes to avoid it.", "Long-lived feature branches defeat CI even if a CI server runs on them.", "Rebuilding the artifact per environment means production runs something that was never tested."],
        [
            qa("basic", "What is continuous integration?", "It is the practice of merging small changes into a shared mainline frequently, at least daily, with every merge verified by an automated build and test run. The goal is to detect integration problems within minutes while the change is small and fresh in the author's mind."),
            qa("basic", "What is the difference between continuous delivery and continuous deployment?", "With continuous delivery every passing build produces an artifact that is ready to deploy, but a human decides when to release. With continuous deployment every passing build goes to production automatically without a manual step."),
            qa("intermediate", "What makes a good CI pipeline?", "It is defined as code in the repository, fast enough to give feedback in minutes, deterministic so the same commit gives the same result, and it fails loudly. It builds one artifact per commit that later stages promote, and the team treats a red mainline as an urgent fix."),
            qa("intermediate", "Is running Jenkins nightly builds CI?", "Not really. CI is about integrating frequently with fast feedback on each change; a nightly build on long-lived branches finds problems a day or more late, mixed with many other changes."),
            qa("advanced", "How do you introduce CI/CD to a team that releases monthly?", "Start by automating the build and unit tests on every pull request and making the mainline protected. Then shrink batch size: trunk-based work with feature flags, an artifact per commit, automated deployment to a staging environment, and finally more frequent production releases while tracking DORA metrics to show progress."),
        ],
        ["ci-vs-cd", "trunk-based-dev", "pipeline-as-code", "gha-workflows"],
        chain(
            ("Commit", "small change", "Developer pushes", "A developer pushes a small change or opens a pull request against <b>main</b>."),
            ("Build", "compile, package", "Build", "The CI service checks out the commit and builds it in a clean environment.", "push"),
            ("Test", "unit, integration", "Verify", "Automated tests run; any failure turns the check red and blocks the merge.", "build"),
            ("Artifact", "immutable, tagged", "Package", "A green build publishes one immutable artifact tagged with the commit SHA.", "pass"),
            ("Deploy", "stage then prod", "Release", "The same artifact is deployed to staging and then production, manually or automatically.", "artifact"),
        ),
    ),
    topic(
        "ci-vs-cd", "CI vs Continuous Delivery vs Deployment", "foundations", "basic", "CD",
        "Three practices that build on each other: integrate, be releasable, release automatically.",
        "Integration is checking every ingredient as it arrives; delivery is having the meal plated and ready on the counter; deployment is the waiter carrying every finished plate straight to the table without asking.",
        "Continuous Integration covers the developer side: merge often, build and test every change, keep the mainline green. Continuous Delivery adds the release side: every change that passes the pipeline is packaged, deployed to production-like environments and proven releasable, so releasing is a business decision that takes minutes. Continuous Deployment removes the final manual approval: every change that passes all automated checks is deployed to production. Moving from delivery to deployment requires high confidence in automated tests, progressive rollout (canary or feature flags), good monitoring and fast rollback, because no human looks at each release. Many regulated organisations stop at continuous delivery with an approval gate, which is fine as long as the gate is quick and the artifact is the same one that was tested. The distinction matters in interviews and in planning: a team can have excellent CI and still release quarterly if deployment is manual and risky. Measuring lead time for changes and deployment frequency shows where on the spectrum a team really sits.",
        ["Explaining to stakeholders why a manual release gate still counts as continuous delivery.", "Planning the steps from nightly builds to continuous deployment.", "Choosing where approval gates belong in a regulated environment."],
        [
            "CI ends with a tested build; delivery ends with a releasable artifact; deployment ends in production.",
            "Continuous delivery keeps a manual release decision; continuous deployment removes it.",
            "Continuous deployment needs strong tests, progressive rollout and automated rollback.",
            "Feature flags decouple deploying code from releasing features to users.",
        ],
        [
            ex("Delivery: build, deploy to staging, manual prod approval", "intermediate", "The production job targets an environment that requires reviewers.", "yaml", """
                name: delivery
                on:
                  push:
                    branches: [main]
                permissions:
                  contents: read
                  id-token: write
                jobs:
                  build:
                    runs-on: ubuntu-latest
                    outputs:
                      tag: ${{ steps.meta.outputs.tag }}
                    steps:
                      - uses: actions/checkout@v4
                      - id: meta
                        run: echo "tag=${GITHUB_SHA::12}" >> "$GITHUB_OUTPUT"
                      - run: make build push TAG=${{ steps.meta.outputs.tag }}
                  staging:
                    needs: build
                    runs-on: ubuntu-latest
                    environment: staging
                    steps:
                      - run: ./deploy.sh staging ${{ needs.build.outputs.tag }}
                  production:
                    needs: [build, staging]
                    runs-on: ubuntu-latest
                    environment: production   # required reviewers configured here
                    steps:
                      - run: ./deploy.sh production ${{ needs.build.outputs.tag }}
            """, runnable=False),
            ex("Deployment: no human gate, automated canary instead", "advanced", "Production rollout is automatic but guarded by metric analysis.", "yaml", """
                production:
                  needs: [build, staging]
                  runs-on: ubuntu-latest
                  environment: production       # no required reviewers
                  steps:
                    - run: kubectl argo rollouts set image web web=registry.example.com/web:${{ needs.build.outputs.tag }}
                    - run: kubectl argo rollouts status web --timeout 15m
            """, runnable=False),
        ],
        ["CI: build + test every merge", "Delivery: releasable artifact + 1-click deploy", "Deployment: auto-release on green", "Measure: lead time, deploy frequency"],
        ["Calling a pipeline continuous delivery when the release still needs a week of manual QA.", "Removing the approval gate before tests and monitoring are trustworthy.", "Rebuilding for production after approval, so the approved artifact is not the one deployed."],
        [
            qa("basic", "Define CI, continuous delivery and continuous deployment in one line each.", "CI: every change is merged often and verified by an automated build and tests. Continuous delivery: every passing change is packaged and proven deployable, released on demand. Continuous deployment: every passing change is released to production automatically."),
            qa("intermediate", "Can a regulated company do continuous deployment?", "Sometimes, if controls are automated: required reviews on merge, signed artifacts, audit logs and automated checks can satisfy separation-of-duties requirements. Many stay with continuous delivery and a fast approval gate, which still gives most of the benefit."),
            qa("intermediate", "What do you need before turning on continuous deployment?", "Reliable automated tests with low flakiness, progressive rollout such as canary or feature flags, good monitoring with alerts tied to releases, and fast rollback. Without these, removing the human gate just moves risk into production."),
            qa("advanced", "How do feature flags change the CD conversation?", "They separate deploy from release: code ships dark to production continuously, and the business turns features on for cohorts later. This lets teams practise continuous deployment for code while keeping product control over exposure."),
        ],
        ["ci-basics", "feature-flags", "approvals-gates", "dora-metrics"],
        chain(
            ("Integrate", "merge + test", "Continuous integration", "Small changes merge to main and the pipeline builds and tests each one."),
            ("Package", "immutable artifact", "Releasable build", "A passing commit produces a versioned artifact stored in a registry.", "green"),
            ("Stage", "prod-like env", "Prove it", "The artifact deploys to staging where integration and smoke tests run.", "artifact"),
            ("Gate?", "manual or none", "Delivery vs deployment", "Continuous delivery waits for a human approval; continuous deployment proceeds automatically.", "verified"),
            ("Production", "progressive", "Release", "The same artifact rolls out to production, ideally behind a canary or flag.", "approve"),
        ),
    ),
    topic(
        "trunk-based-dev", "Trunk-Based Development", "foundations", "intermediate", "TB",
        "Everyone integrates into one main branch at least daily, with short-lived branches and flags.",
        "A shared document everyone edits in small sentences throughout the day, instead of each person writing a chapter in private and trying to paste them together at the end of the month.",
        "Trunk-based development is a branching model where all developers integrate into a single branch (trunk or main) frequently, either by committing directly or through short-lived feature branches that live for hours or a day or two. It is the branching model that makes continuous integration real, because integration happens constantly rather than at the end of a long branch. Unfinished work is hidden behind feature flags or built using branch-by-abstraction, so main is always releasable even while features are half done. Releases are cut from trunk, either by deploying trunk directly or by creating a short release branch for hotfixes only; fixes go to trunk first and are cherry-picked. Compared with GitFlow, there are no long-lived develop or feature branches, so merge conflicts are smaller and the cost of integration is paid in small instalments. The DORA research links trunk-based development with higher delivery performance. It requires discipline: fast CI, good test coverage, small pull requests and a culture of fixing a broken main immediately.",
        ["Moving a team off GitFlow to reduce merge pain.", "Enabling continuous deployment from main.", "Coordinating many teams in a monorepo without integration weeks."],
        [
            "Branches live hours to a couple of days, never weeks.",
            "Incomplete features ship dark behind feature flags.",
            "Branch by abstraction lets large refactors land incrementally.",
            "Release branches, if any, receive cherry-picked fixes from trunk only.",
            "Requires fast CI and a rule that a red main is fixed or reverted at once.",
        ],
        [
            ex("Short-lived branch workflow", "basic", "Branch, commit small, rebase on main and merge the same day.", "bash", """
                git switch -c feat/search-filter
                # ... small change behind a flag ...
                git commit -am "feat(search): add price filter behind search.price_filter flag"
                git fetch origin && git rebase origin/main
                git push -u origin feat/search-filter
                gh pr create --fill --base main
                gh pr merge --squash --auto
            """, runnable=False),
            ex("Release branch for hotfixes only", "intermediate", "Fix lands on main first and is cherry-picked to the release line.", "bash", """
                git switch main && git pull
                git commit -am "fix(cart): handle empty coupon"
                FIX=$(git rev-parse HEAD)
                git switch release/2026.10
                git cherry-pick -x "$FIX"
                git push origin release/2026.10
            """, runnable=False),
        ],
        ["git rebase origin/main", "gh pr merge --squash --auto", "git cherry-pick -x <sha>", "Flags: ship dark, release later"],
        ["Short-lived branches that quietly grow to two weeks bring back merge hell.", "Fixing on the release branch first and forgetting trunk causes regressions in the next release.", "Without feature flags, teams hold changes back and branches get long again."],
        [
            qa("basic", "What is trunk-based development?", "A model where everyone integrates into one main branch at least daily, using very short-lived branches or direct commits. Main is kept releasable at all times."),
            qa("intermediate", "How do you ship unfinished features with trunk-based development?", "Put them behind feature flags that default off, or use branch by abstraction where a new implementation sits behind an interface until it is ready. The code is merged and deployed but not exposed to users."),
            qa("intermediate", "Trunk-based development vs GitFlow?", "GitFlow uses long-lived develop, feature and release branches with merges at milestones, which delays integration. Trunk-based keeps one long-lived branch and integrates continuously, which suits CI/CD and frequent releases."),
            qa("advanced", "How do you handle a hotfix when releases are cut from trunk?", "Fix on trunk first with a test, then cherry-pick the commit to the release branch and ship a patch release. This guarantees the next release from trunk also contains the fix."),
        ],
        ["branching-pr-checks", "feature-flags", "ci-basics"],
        chain(
            ("Branch", "hours, not weeks", "Short branch", "Create a short-lived branch off main for one small change."),
            ("Flag", "default off", "Hide work", "Unfinished behaviour is wrapped in a feature flag so main stays releasable.", "code"),
            ("PR + CI", "fast checks", "Verify", "A small pull request runs CI in minutes and gets a quick review.", "push"),
            ("Merge", "squash to main", "Integrate", "The change merges the same day; everyone rebases onto the new main.", "green"),
            ("Release", "from trunk", "Ship", "Main deploys continuously; the flag is turned on when the feature is ready.", "deploy"),
        ),
    ),
    topic(
        "branching-pr-checks", "Branch Protection & Pull Request Checks", "foundations", "basic", "BP",
        "Required status checks and reviews stop unverified code from reaching main.",
        "The bouncer at the club door with a checklist: ticket scanned, ID checked, dress code met. Nobody gets in on charm alone, not even the owner's friends.",
        "Branch protection (GitHub rulesets, GitLab protected branches, Bitbucket branch permissions) enforces rules on important branches such as main and release/*. Typical rules: changes only through pull requests, at least one approving review, CODEOWNERS approval for sensitive paths, required status checks that must pass, linear history, signed commits and no force pushes or deletions. Required checks are the bridge between CI and the repository: the PR cannot merge until named jobs (build, unit-tests, lint, security-scan) report success on the latest commit. A merge queue goes further by testing the PR combined with everything ahead of it in the queue, so two individually green PRs cannot break main together. PR checks should be fast and focused; slower suites can run after merge or nightly, but anything that protects main from breakage belongs before merge. Administrators should not bypass rules casually, because a bypass is exactly how an untested change or a compromised account ships code.",
        ["Requiring CI and review before anything merges to main.", "Forcing security team approval on changes to infrastructure code via CODEOWNERS.", "Using a merge queue in a busy repository to keep main green."],
        [
            "Required status checks must name the exact job names the pipeline reports.",
            "CODEOWNERS routes reviews for paths to the right team automatically.",
            "Merge queues test PRs against the latest main plus queued changes.",
            "Disable force pushes and require PRs even for admins on main.",
            "Dismiss stale approvals when new commits are pushed.",
        ],
        [
            ex("CODEOWNERS", "basic", "Require platform and security reviews on sensitive paths.", "bash", """
                # .github/CODEOWNERS
                *                    @acme/app-team
                /infra/              @acme/platform-team
                /.github/workflows/  @acme/platform-team @acme/security-team
                /db/migrations/      @acme/dba-team
            """, runnable=False),
            ex("Workflow that supports a merge queue", "intermediate", "Run the same required checks for PRs and merge_group events.", "yaml", """
                name: pr-checks
                on:
                  pull_request:
                  merge_group:
                permissions:
                  contents: read
                jobs:
                  lint:
                    runs-on: ubuntu-latest
                    steps:
                      - uses: actions/checkout@v4
                      - run: make lint
                  unit-tests:
                    runs-on: ubuntu-latest
                    steps:
                      - uses: actions/checkout@v4
                      - run: make test
            """, runnable=False),
            ex("Inspect protection with the GitHub CLI", "intermediate", "Read the current rules for main.", "bash", """
                gh api repos/acme/shop/branches/main/protection --jq '.required_status_checks.contexts'
                gh api repos/acme/shop/rulesets --jq '.[].name'
                gh pr checks 123 --watch
            """, runnable=False),
        ],
        ["gh pr checks <n> --watch", "gh api repos/O/R/branches/main/protection", ".github/CODEOWNERS", "on: merge_group (merge queue)"],
        ["Renaming a job silently breaks required checks: the PR waits forever for a check that no longer exists.", "Workflows with path filters can skip a required check and block merges; use a always-reporting job instead.", "Letting admins bypass protection undermines audit and supply-chain guarantees."],
        [
            qa("basic", "What is a required status check?", "A CI job name that must report success on the PR's latest commit before branch protection allows the merge. It ties the repository's merge button to the pipeline result."),
            qa("intermediate", "What problem does a merge queue solve?", "Two PRs can each pass against an older main but break when combined. A merge queue builds each PR on top of main plus PRs ahead of it and only merges if that combined state passes."),
            qa("intermediate", "What is CODEOWNERS used for?", "It maps paths to owning users or teams; GitHub and GitLab automatically request their review and can require their approval before merging changes to those paths."),
            qa("advanced", "A required check is skipped by a path filter and the PR is stuck. How do you fix it?", "Skipped workflows do not report, so the required check never appears. Either remove the path filter and decide inside the job whether to do work, or add a small always-running gate job that depends on the conditional jobs and is the one marked required."),
        ],
        ["trunk-based-dev", "monorepo-pipelines", "gha-workflows"],
        chain(
            ("Open PR", "feature -> main", "Propose change", "A developer opens a pull request; protection rules apply to the target branch."),
            ("Checks", "lint, tests, scan", "Required checks", "CI reports each required job back to the PR as a status check.", "trigger"),
            ("Review", "CODEOWNERS", "Approval", "Owners of the touched paths are auto-requested and must approve.", "status"),
            ("Queue", "test with main", "Merge queue", "The PR is rebuilt on top of current main and queued PRs.", "approved"),
            ("Merge", "main stays green", "Land", "Only when combined checks pass does the change land on main.", "pass"),
        ),
    ),
    topic(
        "pipeline-as-code", "Pipeline as Code & Testing Pipelines", "foundations", "intermediate", "PC",
        "Pipelines live in the repo as reviewed, linted and tested code.",
        "A recipe written down and kept with the ingredients, instead of living in the head chef's memory. Anyone can read it, suggest changes, and see who changed the salt last Tuesday.",
        "Pipeline as code means the CI/CD definition is stored in the repository next to the application (.github/workflows/*.yml, .gitlab-ci.yml, Jenkinsfile, azure-pipelines.yml) instead of being clicked together in a UI. This gives version history, code review, branching and rollback for the pipeline itself, and lets a change to code and to its pipeline land in the same commit. Because the pipeline is code, it deserves the same quality gates: schema validation and linting (actionlint, GitLab CI Lint API, Jenkins declarative linter), shell linting of embedded scripts with shellcheck, and policy checks such as 'every workflow declares permissions' or 'actions are pinned'. Logic should be kept in scripts or make targets that can run locally, with the YAML acting as thin orchestration; that makes behaviour testable outside the CI service. Tools such as act (GitHub Actions locally) or gitlab-ci-local help debug, though they are not perfect replicas. Shared logic moves into reusable workflows, composite actions or Jenkins shared libraries, which are versioned and tested on their own.",
        ["Reviewing pipeline changes in the same PR as the code they build.", "Blocking workflows that request write-all permissions.", "Debugging a workflow locally before pushing dozens of trial commits."],
        [
            "Keep YAML thin: call make or scripts that also run on a laptop.",
            "Lint workflows (actionlint, CI Lint, Jenkins linter) in CI itself.",
            "Shellcheck every inline script block.",
            "Version shared pipeline libraries and test them like any library.",
        ],
        [
            ex("Lint workflows in CI", "intermediate", "actionlint checks syntax, expressions and embedded shell.", "yaml", """
                name: workflow-lint
                on:
                  pull_request:
                    paths: [".github/workflows/**"]
                permissions:
                  contents: read
                jobs:
                  actionlint:
                    runs-on: ubuntu-latest
                    steps:
                      - uses: actions/checkout@v4
                      - name: Run actionlint
                        run: |
                          bash <(curl -sSfL https://raw.githubusercontent.com/rhysd/actionlint/main/scripts/download-actionlint.bash)
                          ./actionlint -color
            """, runnable=False),
            ex("Run pipelines locally", "basic", "Debug faster with local runners and validation endpoints.", "bash", """
                act pull_request -j unit-tests          # GitHub Actions locally (Docker)
                gitlab-ci-local test                     # GitLab CI locally
                curl --header "PRIVATE-TOKEN: $GITLAB_TOKEN" --data-urlencode "content@.gitlab-ci.yml" "https://gitlab.example.com/api/v4/projects/42/ci/lint"
                shellcheck scripts/*.sh
            """, runnable=False),
            ex("Policy check with conftest", "advanced", "Fail if any workflow lacks a top-level permissions block.", "bash", """
                # policy/workflows.rego
                # package main
                # deny[msg] { not input.permissions; msg := "workflow must declare permissions" }
                conftest test --policy policy/ .github/workflows/*.yml
            """, runnable=False),
        ],
        ["actionlint", "act -j <job>", "gitlab-ci-local <job>", "shellcheck scripts/*.sh", "conftest test .github/workflows"],
        ["Large inline bash in YAML is hard to test and hides quoting bugs.", "act uses different runner images, so a green local run is not proof.", "Pipeline edits from forks can exfiltrate secrets if pull_request_target is misused."],
        [
            qa("basic", "What is pipeline as code?", "Defining the CI/CD pipeline in a file stored in the repository, so it is versioned, reviewed and changed together with the application code."),
            qa("intermediate", "How do you test a pipeline definition?", "Lint it for schema and expression errors, shellcheck inline scripts, run policy checks such as required permissions, and keep logic in scripts with their own tests. Local runners such as act help with debugging."),
            qa("intermediate", "Why keep YAML thin?", "CI YAML is hard to unit test and vendor-specific. Putting logic into make targets or scripts makes it runnable locally, portable across CI systems and testable with normal tools."),
            qa("advanced", "How would you govern pipelines across 300 repositories?", "Provide versioned reusable workflows or templates, enforce them with required workflows or rulesets, and run policy-as-code checks (permissions declared, actions pinned, no secrets in pull_request_target) in an org-wide scanner. Track adoption and roll out template versions gradually."),
        ],
        ["gha-reusable", "jenkins-shared-libs", "ci-basics"],
        chain(
            ("Edit YAML", "in the repo", "Change pipeline", "A pipeline change is made in a branch, next to the code it builds."),
            ("Lint", "actionlint", "Static checks", "Schema, expressions and inline shell are validated automatically.", "diff"),
            ("Policy", "conftest/OPA", "Guardrails", "Rules such as declared permissions and pinned actions are enforced.", "ok"),
            ("Review", "CODEOWNERS", "Peer review", "Platform owners review pipeline changes like any other code.", "pass"),
            ("Run", "real pipeline", "Execute", "Merged, the new pipeline definition runs on the next commit.", "merge"),
        ),
    ),
    topic(
        "monorepo-pipelines", "Monorepo Pipelines & Path Filters", "foundations", "advanced", "MR",
        "Build and test only what a change affects, without missing dependents.",
        "A large office building where a plumbing repair on floor 3 should not trigger a fire drill for all forty floors, but should alert floor 2 whose ceiling shares the pipes.",
        "In a monorepo many services and libraries share one repository, so naively running every build and test on every commit becomes slow and expensive. The goal is affected-only builds: determine which projects changed and which projects depend on them, then run only those pipelines. Simple setups use path filters (GitHub Actions on.paths, dorny/paths-filter, GitLab rules:changes) per service directory. More robust setups use a build graph from a tool such as Bazel, Nx, Turborepo, Pants or Gradle that knows dependencies, so a change in libs/auth also tests every service that imports it. Remote caching lets unchanged targets reuse previous results, often making most of a build a cache hit. Required checks need care: if path filters skip workflows, branch protection may wait forever, so use a single always-running aggregator job. Ownership is handled with CODEOWNERS per directory, and release/versioning can be per package (changesets, release-please manifest mode).",
        ["Running only the payments service tests when only payments changed.", "Re-testing every consumer when a shared library changes.", "Cutting CI minutes in a 200-project repository with remote caching."],
        [
            "Path filters are simple but miss dependency edges; build graphs do not.",
            "Compare against the merge base, not just the previous commit.",
            "Use one always-on aggregator job as the required check.",
            "Remote build caches turn unchanged targets into instant hits.",
            "Changes to shared tooling or root config should trigger everything.",
        ],
        [
            ex("Dynamic matrix from changed paths", "advanced", "Detect changed services, then fan out a matrix; a gate job is the required check.", "yaml", """
                name: monorepo
                on: [pull_request]
                permissions:
                  contents: read
                  pull-requests: read
                jobs:
                  changes:
                    runs-on: ubuntu-latest
                    outputs:
                      services: ${{ steps.filter.outputs.changes }}
                    steps:
                      - uses: actions/checkout@v4
                      - id: filter
                        uses: dorny/paths-filter@v3
                        with:
                          filters: |
                            api: ['services/api/**', 'libs/auth/**']
                            web: ['services/web/**', 'libs/ui/**']
                            worker: ['services/worker/**', 'libs/auth/**']
                  test:
                    needs: changes
                    if: needs.changes.outputs.services != '[]'
                    runs-on: ubuntu-latest
                    strategy:
                      matrix:
                        service: ${{ fromJSON(needs.changes.outputs.services) }}
                    steps:
                      - uses: actions/checkout@v4
                      - run: make -C services/${{ matrix.service }} test
                  ci-ok:
                    if: always()
                    needs: [changes, test]
                    runs-on: ubuntu-latest
                    steps:
                      - run: |
                          if [ "${{ contains(needs.*.result, 'failure') || contains(needs.*.result, 'cancelled') }}" = "true" ]; then exit 1; fi
            """, runnable=False),
            ex("GitLab rules:changes per service", "intermediate", "Jobs run only when their directory or shared libs change.", "yaml", """
                api-test:
                  stage: test
                  script: [make -C services/api test]
                  rules:
                    - changes:
                        paths: [services/api/**/*, libs/auth/**/*]
                        compare_to: refs/heads/main
            """, runnable=False),
            ex("Graph-aware affected builds", "advanced", "Let the build tool compute affected targets.", "bash", """
                npx nx affected -t test --base=origin/main --head=HEAD
                npx turbo run test --filter='...[origin/main]'
                bazel test $(bazel query "rdeps(//..., set($(git diff --name-only origin/main...HEAD | xargs -I{} bazel query {} 2>/dev/null)))")
            """, runnable=False),
        ],
        ["git diff --name-only origin/main...HEAD", "nx affected -t test", "turbo run test --filter=...[origin/main]", "rules: changes: compare_to", "on: pull_request: paths:"],
        ["Path filters ignore transitive dependencies, so a library change can ship untested consumers.", "Skipped workflows never report status and block required checks.", "Diffing against HEAD~1 misses earlier commits in a multi-commit PR."],
        [
            qa("intermediate", "How do you avoid running all tests in a monorepo on every change?", "Compute which projects changed relative to the merge base and which projects depend on them, then run only those. Path filters do this crudely; build tools like Bazel, Nx or Turborepo use a dependency graph and remote caching."),
            qa("intermediate", "Why diff against the merge base?", "A PR can contain many commits and main may have moved. git diff origin/main...HEAD compares against the common ancestor, giving exactly the PR's changes."),
            qa("advanced", "How do required checks work with conditional jobs?", "Mark a single aggregator job as required, run it with if: always(), and have it fail when any needed job failed or was cancelled. Skipped jobs then do not block merges, and failures still do."),
            qa("advanced", "When should a monorepo change trigger a full build?", "When shared root inputs change: toolchain versions, lockfiles, root build config, CI templates or base images. These affect every project, so a filter should map them to all targets."),
        ],
        ["build-systems", "build-matrix", "branching-pr-checks", "cost-speed"],
        chain(
            ("Diff", "vs merge base", "Find changes", "List files changed between the PR head and its merge base with main."),
            ("Graph", "deps + rdeps", "Affected set", "Map files to projects and add every project that depends on them.", "files"),
            ("Matrix", "one job each", "Fan out", "A dynamic matrix starts a job per affected project.", "projects"),
            ("Cache", "remote hits", "Reuse", "Unchanged targets are served from the remote build cache.", "targets"),
            ("Gate", "ci-ok job", "Aggregate", "One always-running job reports a single required status.", "results"),
        ),
    ),
    topic(
        "build-systems", "Build Systems & Reproducible Builds", "build-test", "intermediate", "BS",
        "Same source plus same inputs must produce the same artifact, bit for bit if possible.",
        "Baking from a recipe with weighed ingredients and a thermostat-controlled oven: any baker, any day, gets the same loaf. 'A handful of flour and a hot oven' gives a different loaf every time.",
        "A build system turns source into artifacts: Make, Maven, Gradle, npm/pnpm, Cargo, Go, Bazel and others. In CI the build must be hermetic and deterministic: it should depend only on declared inputs (source, locked dependencies, a pinned toolchain) and not on whatever happens to be installed on the runner or the current time. A reproducible build goes further: independent rebuilds of the same commit produce byte-identical outputs, which lets anyone verify a published binary matches its source and is a key part of supply-chain integrity. Sources of non-determinism include timestamps embedded in archives, file ordering, absolute paths, locale, random seeds, and floating dependency versions; fixes include SOURCE_DATE_EPOCH, sorted inputs, path trimming (go build -trimpath) and lockfiles. Toolchains should be pinned (.tool-versions, setup-* actions with exact versions, toolchain containers). Incremental and cached builds depend on correct input tracking; if the build system does not know an input, caching produces stale or wrong results. The output should be one immutable artifact identified by version and SHA-256 digest.",
        ["Verifying a release binary matches its tagged source.", "Eliminating 'works on my machine' differences between laptops and CI.", "Enabling safe remote build caching."],
        [
            "Pin toolchains and lock dependencies; never build against 'latest'.",
            "Set SOURCE_DATE_EPOCH so archives do not embed the current time.",
            "Identify artifacts by SHA-256 digest, not just by name.",
            "Hermetic builds declare every input; undeclared inputs break caching.",
        ],
        [
            ex("Deterministic Go build", "intermediate", "Trim paths, fix timestamps and print the artifact digest.", "bash", """
                export SOURCE_DATE_EPOCH=$(git log -1 --format=%ct)
                export CGO_ENABLED=0
                go build -trimpath -ldflags "-s -w -buildid= -X main.version=$(git describe --tags)" -o dist/app ./cmd/app
                sha256sum dist/app
                # rebuild elsewhere and compare: identical digest means reproducible
            """, runnable=False),
            ex("Pinned toolchain in CI", "basic", "Exact versions for Node and pnpm with frozen lockfile.", "yaml", """
                jobs:
                  build:
                    runs-on: ubuntu-24.04
                    permissions:
                      contents: read
                    steps:
                      - uses: actions/checkout@v4
                      - uses: pnpm/action-setup@v4
                        with:
                          version: 9.12.0
                      - uses: actions/setup-node@v4
                        with:
                          node-version: 22.11.0
                          cache: pnpm
                      - run: pnpm install --frozen-lockfile
                      - run: pnpm build
            """, runnable=False),
        ],
        ["export SOURCE_DATE_EPOCH=$(git log -1 --format=%ct)", "go build -trimpath", "npm ci · pnpm install --frozen-lockfile", "sha256sum dist/*", "diffoscope a.tar b.tar"],
        ["ubuntu-latest moves; pin the runner image when reproducibility matters.", "npm install (not npm ci) can rewrite the lockfile in CI.", "Embedding build time or hostname in the binary breaks reproducibility."],
        [
            qa("basic", "What is a reproducible build?", "A build where the same source, dependencies and toolchain always produce byte-identical output, so anyone can rebuild and compare digests to verify an artifact."),
            qa("intermediate", "Name common causes of non-deterministic builds.", "Embedded timestamps, filesystem ordering, absolute build paths, unpinned dependency versions, toolchain differences, locale and random seeds."),
            qa("intermediate", "What does hermetic mean for a build?", "The build only uses inputs it declares, such as source files, locked dependencies and a pinned toolchain, and nothing from the host environment or network that is not declared."),
            qa("advanced", "Why do reproducible builds matter for supply-chain security?", "If independent builders produce the same digest from the same source, a compromised build server cannot silently inject code without the mismatch being detected. It strengthens provenance claims such as SLSA."),
        ],
        ["dependency-caching", "supply-chain-slsa", "artifacts-registries"],
        chain(
            ("Source", "git commit", "Inputs", "The build starts from an exact commit SHA."),
            ("Toolchain", "pinned version", "Fixed tools", "Compiler and package manager versions are pinned, often in a container.", "sha"),
            ("Deps", "lockfile", "Locked deps", "Dependencies install from a lockfile with integrity hashes.", "tools"),
            ("Build", "no timestamps", "Deterministic", "SOURCE_DATE_EPOCH, trimmed paths and sorted inputs remove variation.", "deps"),
            ("Digest", "sha256", "Identify", "The artifact is recorded by SHA-256 digest for verification.", "artifact"),
        ),
    ),
    topic(
        "dependency-caching", "Dependency & Build Caching", "build-test", "intermediate", "DC",
        "Restore downloaded packages and build outputs keyed by lockfile hash.",
        "Keeping a pantry stocked instead of driving to the market before every meal. You only shop again when the shopping list (lockfile) changes.",
        "CI runners usually start clean, so without caching every run re-downloads dependencies and recompiles everything. Dependency caches store package manager directories (~/.npm, ~/.cache/pip, ~/.m2, ~/.gradle, Go module cache) and restore them on the next run. The cache key should include the OS, toolchain version and a hash of the lockfile, so a dependency change produces a new key; restore-keys provide a fallback to the most recent partial match. Build caches (Gradle build cache, Bazel remote cache, ccache, Turborepo, Docker BuildKit layer cache) go further and reuse compiled outputs. Caches are an optimisation, never a source of truth: a pipeline must still succeed with an empty cache, and caching node_modules directly across OS or Node versions is risky. On GitHub, caches are scoped by branch, with PRs able to read from the base branch, and are evicted when the repository exceeds its quota. Caches can be poisoned if untrusted PR jobs can write entries that trusted main jobs later read, so be careful with scoping and never cache secrets.",
        ["Cutting a 6-minute npm install to 30 seconds.", "Sharing a Gradle build cache between CI and developer machines.", "Reusing Docker layers across pipeline runs."],
        [
            "Key = OS + tool version + hashFiles(lockfile); restore-keys for fallbacks.",
            "Cache the package manager store, not necessarily node_modules.",
            "Pipelines must pass with a cold cache; cache is an optimisation.",
            "Untrusted jobs writing caches that trusted jobs read is a poisoning risk.",
            "Measure hit rates; a cache that always misses is just upload time.",
        ],
        [
            ex("actions/cache with a lockfile key", "basic", "Cache pip downloads keyed by Python version and requirements hash.", "yaml", """
                - uses: actions/setup-python@v5
                  id: py
                  with:
                    python-version: "3.13"
                - uses: actions/cache@v4
                  with:
                    path: ~/.cache/pip
                    key: pip-${{ runner.os }}-${{ steps.py.outputs.python-version }}-${{ hashFiles('requirements*.txt') }}
                    restore-keys: |
                      pip-${{ runner.os }}-${{ steps.py.outputs.python-version }}-
                - run: pip install -r requirements.txt
            """, runnable=False),
            ex("GitLab cache with key files", "intermediate", "Per-lockfile cache with pull-only policy for test jobs.", "yaml", """
                default:
                  image: node:22
                  cache:
                    key:
                      files: [pnpm-lock.yaml]
                    paths: [.pnpm-store/]
                    policy: pull
                install:
                  stage: build
                  cache:
                    key:
                      files: [pnpm-lock.yaml]
                    paths: [.pnpm-store/]
                    policy: pull-push
                  script:
                    - corepack enable
                    - pnpm config set store-dir .pnpm-store
                    - pnpm install --frozen-lockfile
            """, runnable=False),
            ex("Gradle remote build cache", "advanced", "CI pushes to the cache; laptops only read.", "bash", """
                # settings.gradle.kts
                # buildCache { remote<HttpBuildCache> { url = uri("https://cache.example.com/cache/"); isPush = System.getenv("CI") != null } }
                ./gradlew build --build-cache --scan
            """, runnable=False),
        ],
        ["key: ${{ hashFiles('**/package-lock.json') }}", "restore-keys: prefix-", "gh cache list · gh cache delete <key>", "cache: policy: pull", "./gradlew build --build-cache"],
        ["Caching node_modules across Node versions can load incompatible native modules.", "Overly broad restore-keys can restore stale dependencies that mask lockfile issues.", "Fork PRs writing cache entries can poison builds on main."],
        [
            qa("basic", "How should a CI cache key be built?", "From things that change the cached content: OS, tool version and a hash of the lockfile. When any of these change the key changes and a fresh cache is created."),
            qa("intermediate", "What are restore-keys?", "Prefix fallbacks used when the exact key misses. The most recent cache matching the prefix is restored, so most packages are present and only the delta is downloaded."),
            qa("intermediate", "Dependency cache vs build cache?", "A dependency cache stores downloaded packages so installs are fast. A build cache stores outputs of compilation or test tasks keyed by their inputs so unchanged work is skipped entirely."),
            qa("advanced", "What is cache poisoning in CI and how do you prevent it?", "An untrusted job, such as a fork PR, writes a malicious entry under a key that a trusted job on main later restores. Prevent it by scoping caches per branch, letting only trusted branches write shared caches and never executing cached content without integrity checks."),
        ],
        ["build-systems", "container-builds", "cost-speed"],
        chain(
            ("Hash", "lockfile", "Compute key", "The job hashes the lockfile and combines it with OS and tool version."),
            ("Restore", "exact or prefix", "Lookup", "The cache service returns the exact key or the newest prefix match.", "key"),
            ("Install", "only the delta", "Install deps", "The package manager fetches only what the restored cache lacks.", "cache"),
            ("Build", "tests run", "Work", "The build and tests run on the warm environment.", "deps"),
            ("Save", "on miss only", "Store", "On an exact-key miss the updated cache is uploaded for next time.", "new"),
        ),
    ),
]

_BATCH_2 = [
    topic(
        "build-matrix", "Build Matrices", "build-test", "basic", "BM",
        "One job definition fans out across versions, platforms and configurations.",
        "A tailor checking one suit pattern on every body size at once, rather than sewing one size, waiting, then trying the next.",
        "A build matrix expands a single job template into many parallel jobs, one per combination of variables such as operating system, language version, database version or feature set. GitHub Actions uses strategy.matrix with include and exclude, GitLab uses parallel:matrix, Jenkins declarative pipelines have a matrix directive, and CircleCI has matrix parameters. Matrices are ideal for libraries that must support several runtimes (Python 3.11 to 3.13, Node 20 and 22) and for cross-platform binaries (Linux, macOS, Windows, arm64). The combinatorial explosion is the main risk: three OSes times four versions times two databases is 24 jobs, so trim with exclude, run the full matrix nightly and a reduced one on PRs. fail-fast controls whether one failure cancels the rest; turning it off gives a complete picture of which combinations are broken. max-parallel limits concurrency to protect shared resources or budget. Dynamic matrices built from a JSON output of an earlier job allow matrices driven by changed services or a config file.",
        ["Testing a library on every supported Python version.", "Building release binaries for linux/amd64, linux/arm64, darwin and windows.", "Running integration tests against PostgreSQL 15, 16 and 17."],
        [
            "Each matrix cell is an independent job with its own runner.",
            "include adds or extends combinations; exclude removes them.",
            "fail-fast: false shows every failing combination instead of the first.",
            "Dynamic matrices come from fromJSON(needs.job.outputs.x).",
            "Run the full matrix on main or nightly, a slim one on PRs.",
        ],
        [
            ex("OS and version matrix", "basic", "Six combinations with one exclusion and an extra experimental cell.", "yaml", """
                jobs:
                  test:
                    runs-on: ${{ matrix.os }}
                    permissions:
                      contents: read
                    strategy:
                      fail-fast: false
                      max-parallel: 6
                      matrix:
                        os: [ubuntu-24.04, macos-14, windows-2022]
                        python: ["3.12", "3.13"]
                        exclude:
                          - os: windows-2022
                            python: "3.12"
                        include:
                          - os: ubuntu-24.04
                            python: "3.14"
                            experimental: true
                    continue-on-error: ${{ matrix.experimental == true }}
                    steps:
                      - uses: actions/checkout@v4
                      - uses: actions/setup-python@v5
                        with:
                          python-version: ${{ matrix.python }}
                      - run: pip install -e .[test] && pytest -q
            """, runnable=False),
            ex("GitLab parallel matrix", "intermediate", "Test against several database versions as services.", "yaml", """
                integration:
                  stage: test
                  image: python:3.13
                  parallel:
                    matrix:
                      - PG_VERSION: ["15", "16", "17"]
                  services:
                    - name: postgres:${PG_VERSION}
                      alias: db
                  variables:
                    POSTGRES_PASSWORD: EXAMPLE-ONLY-not-a-real-secret
                    DATABASE_URL: postgresql://postgres@db:5432/postgres
                  script:
                    - pip install -r requirements.txt
                    - pytest tests/integration -q
            """, runnable=False),
        ],
        ["strategy.matrix · include · exclude", "fail-fast: false", "max-parallel: N", "parallel: matrix: (GitLab)", "fromJSON(needs.x.outputs.list)"],
        ["Matrix size multiplies cost; 3x4x2 is already 24 runners.", "Required checks must list each matrix job name, which changes when the matrix changes; use an aggregator job.", "Shared external resources (one test DB) break when cells run in parallel."],
        [
            qa("basic", "What is a build matrix?", "A way to run the same job across several combinations of parameters, such as OS and language version, in parallel from one definition."),
            qa("intermediate", "What does fail-fast do?", "When true (the GitHub default), the first failing cell cancels the rest of the matrix. Setting it to false lets every combination finish so you see the full set of failures."),
            qa("intermediate", "How do you keep a matrix affordable?", "Exclude combinations that add little value, run a reduced matrix on pull requests and the full one on main or nightly, cap max-parallel and cache dependencies per cell."),
            qa("advanced", "How do you build a matrix dynamically?", "An earlier job computes a JSON array, for example changed services, and exposes it as an output. The matrix job uses matrix: ${{ fromJSON(needs.detect.outputs.list) }} and is skipped when the list is empty."),
        ],
        ["test-sharding", "monorepo-pipelines", "gha-workflows"],
        chain(
            ("Template", "one job def", "Define", "One job lists matrix axes such as os and python."),
            ("Expand", "axes x values", "Combine", "The CI service computes every combination, applying include and exclude.", "axes"),
            ("Fan out", "parallel jobs", "Run cells", "Each combination gets its own runner and runs in parallel.", "cells"),
            ("Report", "per-cell status", "Collect", "Each cell reports pass or fail; an aggregator job summarises.", "results"),
        ),
    ),
    topic(
        "test-sharding", "Parallelism & Test Sharding", "build-test", "intermediate", "SH",
        "Split a long test suite across N runners so wall-clock time drops by roughly N.",
        "Ten checkout lanes instead of one. The shopping is the same, but the queue disappears, as long as you send shoppers to lanes evenly.",
        "When a test suite takes 40 minutes, parallelism is usually the fastest lever. Within one machine, runners like pytest-xdist, Jest workers or JUnit parallel execution use multiple CPU cores. Across machines, sharding splits the test files into N groups and runs each on its own CI job, then merges results. Naive splitting by file count is uneven because some files take minutes; timing-based splitting uses historical durations (JUnit XML reports) to balance shards so they finish together. CircleCI has tests split --split-by=timings, GitLab has parallel: N with CI_NODE_INDEX and CI_NODE_TOTAL, Playwright and Jest support --shard=i/n, and Knapsack-style tools rebalance dynamically. Tests must be isolated for sharding to work: no shared database rows, ports or files between tests, and no order dependencies. Each shard uploads JUnit XML and coverage files, and a final job merges them so reports and coverage gates remain accurate. Remember the fixed overhead per shard (checkout, install, container start); past a certain N, adding shards adds cost without saving time.",
        ["Bringing a 45-minute end-to-end suite under 10 minutes.", "Balancing Playwright tests across 8 runners.", "Merging coverage from parallel shards into one report."],
        [
            "Split by historical timing, not file count, for even shards.",
            "Tests must be isolated: unique DB schemas, ports and temp dirs.",
            "Merge JUnit XML and coverage in a final job.",
            "Per-shard setup overhead sets a floor on useful parallelism.",
        ],
        [
            ex("Playwright sharding with merged report", "intermediate", "Four shards, each uploads a blob report; a final job merges them.", "yaml", """
                jobs:
                  e2e:
                    runs-on: ubuntu-latest
                    permissions:
                      contents: read
                    strategy:
                      fail-fast: false
                      matrix:
                        shard: [1, 2, 3, 4]
                    steps:
                      - uses: actions/checkout@v4
                      - uses: actions/setup-node@v4
                        with:
                          node-version: 22
                          cache: npm
                      - run: npm ci && npx playwright install --with-deps chromium
                      - run: npx playwright test --shard=${{ matrix.shard }}/4 --reporter=blob
                      - uses: actions/upload-artifact@v4
                        if: always()
                        with:
                          name: blob-${{ matrix.shard }}
                          path: blob-report
                  report:
                    needs: e2e
                    if: always()
                    runs-on: ubuntu-latest
                    steps:
                      - uses: actions/checkout@v4
                      - uses: actions/download-artifact@v4
                        with:
                          pattern: blob-*
                          path: all-blobs
                          merge-multiple: true
                      - run: npx playwright merge-reports --reporter html ./all-blobs
            """, runnable=False),
            ex("GitLab parallel with pytest-split", "advanced", "Timing-based split using stored durations.", "yaml", """
                unit:
                  stage: test
                  parallel: 6
                  script:
                    - pip install -r requirements.txt pytest-split pytest-xdist
                    - pytest -n auto --splits $CI_NODE_TOTAL --group $CI_NODE_INDEX --durations-path .test_durations --junitxml=report.xml
                  artifacts:
                    when: always
                    reports:
                      junit: report.xml
            """, runnable=False),
        ],
        ["pytest -n auto (xdist)", "npx playwright test --shard=2/4", "jest --shard=1/3", "circleci tests split --split-by=timings", "parallel: N · $CI_NODE_INDEX"],
        ["Hidden shared state (same DB row, same port) causes failures only when sharded.", "One slow test file caps the speedup no matter how many shards.", "Forgetting to merge coverage makes the coverage gate fail or lie."],
        [
            qa("basic", "What is test sharding?", "Splitting a test suite into groups that run on separate machines in parallel, then combining their results."),
            qa("intermediate", "Why split by timing instead of by count?", "Test files vary widely in duration. Using recorded timings balances shards so they finish at about the same time, which minimises the wall-clock time of the slowest shard."),
            qa("intermediate", "What breaks when you parallelise tests?", "Tests that share state such as database rows, files, ports or global caches, and tests that depend on running in a particular order. They must be made independent first."),
            qa("advanced", "How do you choose the number of shards?", "Measure per-shard fixed overhead (checkout, install, container start) and total test time. Increase shards while the wall-clock time keeps dropping meaningfully; once overhead dominates, more shards only add cost."),
        ],
        ["build-matrix", "test-stages", "flaky-tests", "cost-speed"],
        chain(
            ("Timings", "past JUnit XML", "Collect durations", "Durations from previous runs are loaded for each test file."),
            ("Split", "balance N groups", "Partition", "Files are assigned to N shards so each has similar total time.", "times"),
            ("Run", "N runners", "Parallel shards", "Each shard runs on its own runner with isolated resources.", "groups"),
            ("Upload", "xml + coverage", "Artifacts", "Every shard uploads test reports and coverage, even on failure.", "reports"),
            ("Merge", "one report", "Combine", "A final job merges reports and enforces the coverage gate.", "files"),
        ),
    ),
    topic(
        "test-stages", "Test Stages: Unit, Integration, E2E", "build-test", "basic", "TS",
        "Order tests from fast and narrow to slow and broad, failing as early as possible.",
        "Checking a car on the production line: each bolt is torqued as it is fitted (unit), the engine is run on a test bench (integration), and finally someone drives the finished car round the track (end-to-end).",
        "A pipeline arranges tests in stages following the test pyramid: many fast unit tests, fewer integration tests and a small number of end-to-end tests. Static checks (lint, type checks, formatting) and unit tests run first because they take seconds to minutes and catch most mistakes. Integration tests exercise real dependencies such as a database, message broker or HTTP API, often via service containers or Testcontainers. Contract tests (Pact) verify that services agree on API shapes without deploying everything together. End-to-end tests drive the system through its UI or public API in a deployed environment and are the slowest and most brittle, so they focus on critical user journeys. After deployment, smoke tests and synthetic checks confirm the environment is healthy. Ordering by cost gives fast failure: there is no point running a 20-minute browser suite if the code does not compile. Independent stages can still run in parallel; the ordering is a dependency graph rather than a strict line.",
        ["Designing a PR pipeline that fails in under 3 minutes for most mistakes.", "Running integration tests against a real PostgreSQL service container.", "Keeping a small, stable E2E suite for checkout and login."],
        [
            "Pyramid: many unit, fewer integration, few E2E.",
            "Run cheapest checks first for fast failure.",
            "Service containers or Testcontainers give real dependencies in CI.",
            "Contract tests replace many brittle cross-service E2E tests.",
            "Post-deploy smoke tests verify the environment, not the code logic.",
        ],
        [
            ex("Staged pipeline with a service container", "intermediate", "Lint and unit first; integration uses PostgreSQL; E2E runs after deploy to preview.", "yaml", """
                jobs:
                  lint-unit:
                    runs-on: ubuntu-latest
                    permissions:
                      contents: read
                    steps:
                      - uses: actions/checkout@v4
                      - run: make lint typecheck unit
                  integration:
                    needs: lint-unit
                    runs-on: ubuntu-latest
                    services:
                      postgres:
                        image: postgres:17
                        env:
                          POSTGRES_PASSWORD: ${{ secrets.CI_DB_PASSWORD }}
                        ports: ["5432:5432"]
                        options: >-
                          --health-cmd "pg_isready -U postgres"
                          --health-interval 5s --health-retries 10
                    env:
                      PGHOST: localhost
                      PGUSER: postgres
                      PGPASSWORD: ${{ secrets.CI_DB_PASSWORD }}
                    steps:
                      - uses: actions/checkout@v4
                      - run: make integration
                  e2e:
                    needs: integration
                    runs-on: ubuntu-latest
                    steps:
                      - uses: actions/checkout@v4
                      - run: make deploy-preview e2e BASE_URL=https://pr-${{ github.event.number }}.preview.example.com
            """, runnable=False),
            ex("Post-deploy smoke test", "basic", "Fail the deployment if critical endpoints do not respond.", "bash", """
                set -euo pipefail
                BASE=https://staging.example.com
                curl -fsS --retry 5 --retry-delay 3 "$BASE/healthz"
                curl -fsS "$BASE/api/v1/products?limit=1" | jq -e '.items | length == 1'
            """, runnable=False),
        ],
        ["make lint unit", "pytest -m 'not integration'", "services: postgres:", "npx playwright test", "curl -fsS $BASE/healthz"],
        ["An inverted pyramid (mostly E2E) makes pipelines slow and flaky.", "Integration tests against shared staging databases interfere with each other.", "Mocking everything in 'integration' tests means nothing real is integrated."],
        [
            qa("basic", "Describe the test pyramid.", "A wide base of fast, isolated unit tests, a middle layer of integration tests with real dependencies, and a narrow top of slow end-to-end tests. It balances confidence against speed and maintenance cost."),
            qa("intermediate", "Why run unit tests before integration tests?", "They are cheaper and catch most bugs, so failing fast saves runner time and gives developers feedback sooner."),
            qa("intermediate", "What are contract tests?", "Tests where a consumer records the requests and responses it expects from a provider, and the provider verifies it satisfies that contract in its own pipeline. They catch API breaks without full multi-service E2E environments."),
            qa("advanced", "How do you keep E2E tests valuable rather than painful?", "Limit them to critical journeys, run them against isolated preview environments, make them deterministic with seeded data and explicit waits, shard them, and quarantine flaky ones quickly with an owner to fix."),
        ],
        ["test-sharding", "flaky-tests", "ci-basics"],
        chain(
            ("Static", "lint, types", "Static checks", "Formatting, lint and type checks fail in seconds."),
            ("Unit", "fast, isolated", "Unit tests", "Thousands of isolated tests verify logic in a minute or two.", "ok"),
            ("Integration", "real DB, broker", "Integration", "Tests hit real dependencies via service containers.", "ok"),
            ("E2E", "user journeys", "End-to-end", "A few browser or API journeys run against a preview environment.", "ok"),
            ("Smoke", "after deploy", "Smoke", "Health checks confirm the deployed environment is serving.", "deployed"),
        ),
    ),
    topic(
        "flaky-tests", "Flaky Tests & Quarantine", "build-test", "intermediate", "FT",
        "Tests that pass and fail on the same code erode trust; detect, quarantine, fix.",
        "A smoke alarm that goes off at random. After a week everyone ignores it, including the one time there really is a fire.",
        "A flaky test is one that can both pass and fail without any code change. Common causes are timing assumptions (sleep instead of waiting for a condition), test order dependence, shared state, real network calls, time zones and clocks, random data without fixed seeds, resource limits on runners and race conditions in the code itself. Flakiness is corrosive: developers start rerunning pipelines until green, real failures get dismissed, and CI loses its authority. Detection uses history: a test that failed and then passed on retry for the same commit is flaky, and CI analytics (GitHub, GitLab, BuildPulse, Datadog CI Visibility, Gradle Develocity) can flag them. Quarantine moves a known-flaky test out of the blocking path (a marker, a skip list, a non-blocking job) while a ticket with an owner and deadline tracks the fix; quarantine without follow-up becomes a graveyard of deleted coverage. Automatic retries can mask flakiness and should be limited, reported and never used as the fix. Some flakes are real bugs, such as race conditions, so investigate before assuming the test is wrong.",
        ["Identifying the top 10 flaky tests by failure rate.", "Unblocking a team while an intermittently failing test is fixed.", "Catching a production race condition that first showed up as a flaky test."],
        [
            "Same commit, different results = flaky.",
            "Replace sleeps with waits on conditions; freeze time; seed randomness.",
            "Quarantine with an owner and a deadline, not forever.",
            "Retries hide signal; record every retry as a flake event.",
            "Some flakes are real concurrency bugs in production code.",
        ],
        [
            ex("Quarantine marker in pytest", "intermediate", "Quarantined tests run in a separate non-blocking job.", "yaml", """
                # pytest.ini: markers = quarantine: known flaky, tracked in issue tracker
                jobs:
                  tests:
                    runs-on: ubuntu-latest
                    permissions:
                      contents: read
                    steps:
                      - uses: actions/checkout@v4
                      - run: pip install -r requirements.txt
                      - run: pytest -m "not quarantine" --junitxml=report.xml
                  quarantined:
                    runs-on: ubuntu-latest
                    continue-on-error: true
                    steps:
                      - uses: actions/checkout@v4
                      - run: pip install -r requirements.txt
                      - run: pytest -m quarantine --count=5 -p no:randomly
            """, runnable=False),
            ex("Reproduce a flake locally", "basic", "Run a test many times, in random order, to surface flakiness.", "bash", """
                pip install pytest-repeat pytest-randomly
                pytest tests/test_checkout.py::test_coupon -x --count=200
                pytest -p randomly --randomly-seed=12345 tests/
                npx playwright test checkout.spec.ts --repeat-each=50 --workers=4
            """, runnable=False),
        ],
        ["pytest --count=200 (pytest-repeat)", "pytest -p randomly --randomly-seed=N", "playwright test --repeat-each=50", "pytest -m 'not quarantine'", "Track: flake rate per test"],
        ["Blanket retries (retry: 2 on everything) hide new flakes and real bugs.", "Quarantined tests without owners are effectively deleted.", "Fixing a flake by increasing a sleep just moves the threshold."],
        [
            qa("basic", "What is a flaky test?", "A test that produces different results on the same code, passing sometimes and failing other times, usually because of timing, shared state, ordering or external dependencies."),
            qa("intermediate", "How do you detect flaky tests?", "Track test results per commit over time; a test that fails then passes on retry for the same commit is flaky. CI analytics tools compute failure rates, and stress runs (repeat 100 times, randomised order) reproduce them."),
            qa("intermediate", "What is test quarantine?", "Moving a known-flaky test out of the blocking pipeline into a non-blocking job or skip list, with a tracked owner and deadline to fix it, so it stops blocking others but is not forgotten."),
            qa("advanced", "Should CI automatically retry failed tests?", "A single retry can be acceptable for known infrastructure noise if every retry is recorded and reported as a flake. Unlimited or silent retries hide real regressions and race conditions, so the long-term fix is always to make the test deterministic."),
        ],
        ["test-stages", "test-sharding", "pipeline-observability"],
        chain(
            ("Fail", "same commit", "Intermittent", "A test fails, then passes on rerun with no code change."),
            ("Detect", "flake rate", "Identify", "CI analytics flags the test by its pass-fail history.", "history"),
            ("Quarantine", "non-blocking", "Isolate", "The test moves to a non-blocking job with an owner ticket.", "flaky"),
            ("Reproduce", "repeat, shuffle", "Root cause", "Stress runs expose timing, ordering or shared-state issues.", "ticket"),
            ("Fix", "back to blocking", "Restore", "A deterministic fix lands and the test rejoins the gate.", "fix"),
        ),
    ),
    topic(
        "container-builds", "Container Image Builds in CI", "build-test", "intermediate", "CB",
        "Multi-stage Dockerfiles, good layer ordering and BuildKit caches give small, fast, safe images.",
        "Packing a suitcase: heavy items that never change go at the bottom, the things you swap daily on top, and you leave the tools you used to pack at home.",
        "Container images are the most common deployable artifact in modern CD. A multi-stage Dockerfile uses a full SDK image to compile and a minimal runtime image (distroless, alpine, chiseled or slim) for the final stage, so compilers and build secrets never ship. Layer ordering determines cache efficiency: copy dependency manifests and install dependencies before copying source, so a code change does not invalidate the dependency layer. BuildKit (docker buildx) adds parallel stages, cache mounts (RUN --mount=type=cache) for package managers, secret mounts that do not persist in layers, and remote cache export to a registry or the GitHub Actions cache. Base images should be pinned by digest and updated deliberately by a bot such as Renovate or Dependabot. Images should run as a non-root user, include only what is needed, and be tagged with the commit SHA (not only latest) and referenced by digest when deployed. In CI, build once, scan (Trivy, Grype), generate an SBOM, sign (cosign) and push; multi-architecture images are built with buildx and QEMU or native arm runners.",
        ["Shrinking a 1.2 GB Node image to 150 MB.", "Cutting image build time from 8 minutes to 1 with registry cache.", "Publishing amd64 and arm64 images from one pipeline."],
        [
            "Multi-stage: build in SDK image, run in minimal image.",
            "Copy lockfiles and install deps before copying source.",
            "Use --mount=type=secret for build-time credentials; never ARG or ENV.",
            "Pin base images by digest; tag outputs with the commit SHA.",
            "Run as non-root and keep the final image minimal.",
        ],
        [
            ex("Multi-stage Dockerfile with cache mounts", "intermediate", "Go build with BuildKit cache, distroless non-root runtime.", "dockerfile", """
                # syntax=docker/dockerfile:1.7
                FROM golang:1.23 AS build
                WORKDIR /src
                COPY go.mod go.sum ./
                RUN --mount=type=cache,target=/go/pkg/mod go mod download
                COPY . .
                RUN --mount=type=cache,target=/go/pkg/mod --mount=type=cache,target=/root/.cache/go-build CGO_ENABLED=0 go build -trimpath -o /out/app ./cmd/app

                FROM gcr.io/distroless/static-debian12:nonroot
                COPY --from=build /out/app /app
                USER nonroot:nonroot
                EXPOSE 8080
                ENTRYPOINT ["/app"]
            """, runnable=False),
            ex("Build and push with buildx and registry cache", "advanced", "Multi-arch build to GHCR using GITHUB_TOKEN with packages: write.", "yaml", """
                jobs:
                  image:
                    runs-on: ubuntu-latest
                    permissions:
                      contents: read
                      packages: write
                    steps:
                      - uses: actions/checkout@v4
                      - uses: docker/setup-qemu-action@v3
                      - uses: docker/setup-buildx-action@v3
                      - uses: docker/login-action@v3
                        with:
                          registry: ghcr.io
                          username: ${{ github.actor }}
                          password: ${{ secrets.GITHUB_TOKEN }}
                      - uses: docker/build-push-action@v6
                        with:
                          context: .
                          platforms: linux/amd64,linux/arm64
                          push: true
                          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
                          cache-from: type=registry,ref=ghcr.io/${{ github.repository }}:buildcache
                          cache-to: type=registry,ref=ghcr.io/${{ github.repository }}:buildcache,mode=max
                          provenance: mode=max
                          sbom: true
            """, runnable=False),
            ex("Build-time secret without leaking it into layers", "advanced", "The secret is mounted only for one RUN step.", "bash", """
                # Dockerfile: RUN --mount=type=secret,id=npmrc,target=/root/.npmrc npm ci
                docker buildx build --secret id=npmrc,src=$HOME/.npmrc -t app:dev .
                docker history app:dev          # no secret in any layer
            """, runnable=False),
        ],
        ["docker buildx build --platform linux/amd64,linux/arm64", "--cache-from/--cache-to type=registry", "RUN --mount=type=cache,target=...", "--secret id=x,src=file", "docker buildx imagetools inspect img"],
        ["COPY . . before installing deps busts the cache on every code change.", "ARG or ENV for tokens bakes them into image history.", "Using :latest in deployments makes rollbacks and audits ambiguous.", "Missing .dockerignore sends .git and node_modules into the build context."],
        [
            qa("basic", "Why use a multi-stage Dockerfile?", "To compile in a full SDK image and copy only the result into a small runtime image. The final image is smaller, has fewer vulnerabilities and contains no build tools or intermediate secrets."),
            qa("intermediate", "How does layer ordering affect build time?", "Each instruction creates a cached layer, and a change invalidates that layer and everything after it. Copying lockfiles and installing dependencies before copying source keeps the expensive dependency layer cached across code changes."),
            qa("intermediate", "How do you pass a private registry token to a build safely?", "Use a BuildKit secret mount (RUN --mount=type=secret) supplied with --secret at build time. It is available only during that step and never stored in a layer, unlike ARG or ENV."),
            qa("advanced", "How do you get fast image builds on ephemeral CI runners?", "Use BuildKit with a remote cache exported to a registry or the GitHub Actions cache (cache-to mode=max), cache mounts for package managers, good layer ordering and a tight .dockerignore. Native arm runners avoid slow QEMU emulation for multi-arch builds."),
        ],
        ["artifacts-registries", "signing-cosign", "sbom", "dependency-caching"],
        chain(
            ("Context", ".dockerignore", "Send context", "Only needed files are sent to BuildKit."),
            ("Deps layer", "lockfile first", "Cached deps", "Dependencies install in an early layer that rarely changes.", "files"),
            ("Build stage", "SDK image", "Compile", "Source is compiled with cache mounts in the build stage.", "deps"),
            ("Runtime", "distroless", "Final stage", "Only the binary is copied into a minimal non-root image.", "binary"),
            ("Push", "tag = SHA", "Publish", "The image is scanned, signed and pushed, then referenced by digest.", "image"),
        ),
    ),
    topic(
        "mobile-ci", "Mobile CI/CD", "build-test", "advanced", "MO",
        "Build, sign, test and ship iOS and Android apps through store pipelines.",
        "Shipping a product through customs: the goods (app) must be packed to spec, sealed with an approved stamp (code signing), inspected (store review) and released country by country (staged rollout).",
        "Mobile pipelines differ from web pipelines in three ways: builds need special hosts (macOS for iOS/Xcode), artifacts must be code-signed with platform certificates and provisioning profiles, and releases go through app stores with review and staged rollouts rather than instant deploys. Fastlane is the common automation layer: lanes for building, running unit and UI tests, managing signing (match stores certificates encrypted in a private repo or cloud bucket) and uploading to TestFlight or Google Play internal tracks. Android builds use Gradle with a release keystore whose password comes from CI secrets; iOS builds use xcodebuild or Fastlane gym with an App Store Connect API key, ideally short-lived. UI tests run on emulators/simulators or device farms (Firebase Test Lab, AWS Device Farm, BrowserStack). Because users update slowly and you cannot roll back an installed binary, mobile CD relies heavily on feature flags, remote config, phased rollout percentages and forced-update mechanisms. Build numbers must increase monotonically, commonly derived from the CI run number.",
        ["Uploading every main build to TestFlight and Play internal testing.", "Managing iOS signing for a team without sharing certificates by hand.", "Running UI tests on a device farm before a store release."],
        [
            "iOS needs macOS runners; Android builds run on Linux.",
            "Signing material lives in a secret store, never in the repo unencrypted.",
            "Fastlane lanes standardise build, test, sign and upload.",
            "You cannot roll back installed apps: use flags and phased rollouts.",
            "Build numbers must strictly increase per store upload.",
        ],
        [
            ex("Android release build", "advanced", "Keystore decoded from a secret; upload to Play internal track via Fastlane.", "yaml", """
                jobs:
                  android:
                    runs-on: ubuntu-latest
                    permissions:
                      contents: read
                    environment: play-internal
                    steps:
                      - uses: actions/checkout@v4
                      - uses: actions/setup-java@v4
                        with:
                          distribution: temurin
                          java-version: "21"
                          cache: gradle
                      - name: Restore keystore
                        run: echo "${{ secrets.ANDROID_KEYSTORE_B64 }}" | base64 -d > release.jks
                      - run: ./gradlew bundleRelease -PversionCode=${{ github.run_number }}
                        env:
                          KEYSTORE_PATH: release.jks
                          KEYSTORE_PASSWORD: ${{ secrets.ANDROID_KEYSTORE_PASSWORD }}
                      - run: bundle exec fastlane android internal
                        env:
                          PLAY_JSON_KEY: ${{ secrets.PLAY_SERVICE_ACCOUNT_JSON }}
                      - if: always()
                        run: rm -f release.jks
            """, runnable=False),
            ex("Fastlane lanes for iOS", "advanced", "Fastfile (Ruby DSL) using match and an App Store Connect API key from env.", "bash", """
                # fastlane/Fastfile
                # lane :beta do
                #   app_store_connect_api_key(key_id: ENV["ASC_KEY_ID"], issuer_id: ENV["ASC_ISSUER_ID"], key_content: ENV["ASC_KEY_P8"])
                #   match(type: "appstore", readonly: true)
                #   increment_build_number(build_number: ENV["GITHUB_RUN_NUMBER"])
                #   build_app(scheme: "Shop")
                #   upload_to_testflight(skip_waiting_for_build_processing: true)
                # end
                bundle exec fastlane ios beta
            """, runnable=False),
        ],
        ["fastlane ios beta · fastlane android internal", "fastlane match appstore --readonly", "./gradlew bundleRelease", "xcodebuild test -scheme App -destination 'platform=iOS Simulator,name=iPhone 16'", "gcloud firebase test android run"],
        ["macOS runners cost several times more per minute than Linux; keep iOS jobs lean.", "Expired provisioning profiles or certificates break release builds suddenly.", "Reusing a build number makes the store reject the upload."],
        [
            qa("intermediate", "What makes mobile CI/CD different from web CD?", "Builds need platform-specific hosts and code signing, releases pass through store review, and shipped binaries cannot be rolled back on users' devices. Teams rely on flags, remote config and phased rollouts for safety."),
            qa("intermediate", "What does fastlane match do?", "It stores signing certificates and provisioning profiles encrypted in a private git repository or bucket, and syncs them onto CI and developer machines so the whole team uses the same signing identity without manual sharing."),
            qa("advanced", "How do you roll back a bad mobile release?", "You cannot uninstall it, so halt the phased rollout, disable the faulty feature through a flag or remote config, and ship a fixed build with a higher build number. A forced-update screen handles severe cases."),
            qa("advanced", "How should store credentials be handled in CI?", "Use App Store Connect API keys and Play service accounts with minimum roles, stored in CI secrets bound to a protected environment. Decode keystores only for the job, delete them afterwards and rotate keys on staff changes."),
        ],
        ["feature-flags", "secrets-in-ci", "signing-cosign"],
        chain(
            ("Build", "macOS / Linux", "Compile", "Gradle or Xcode builds the app with a CI-derived build number."),
            ("Test", "sim + devices", "Verify", "Unit and UI tests run on simulators and a device farm.", "app"),
            ("Sign", "match/keystore", "Code sign", "Release signing material is pulled from secrets for this job only.", "tested"),
            ("Upload", "TestFlight/Play", "Distribute", "The signed bundle goes to beta tracks for internal testers.", "signed"),
            ("Rollout", "phased %", "Release", "Store release starts at a small percentage and expands if healthy.", "approved"),
        ),
    ),
    topic(
        "ml-pipelines", "ML Pipelines (MLOps) Overview", "build-test", "advanced", "ML",
        "CI/CD for models adds data, training, evaluation and model registries to the code pipeline.",
        "A bakery where the recipe (code) is only half the story: the flour (data) changes every delivery, so each batch is test-baked and tasted against the last before it reaches the shop window.",
        "Machine learning systems change when code changes and also when data changes, so MLOps extends CI/CD with data and model stages. CI still lints and unit-tests feature code and training code, and adds data validation (schema, ranges, null rates) with tools like Great Expectations or TFX Data Validation. Continuous training (CT) pipelines, orchestrated by Kubeflow Pipelines, Airflow, SageMaker Pipelines, Vertex AI or MLflow Projects, pull a versioned dataset (DVC, lakeFS, Delta), train, and log parameters, metrics and artifacts to an experiment tracker. An evaluation gate compares the candidate against the current production model on a held-out set and fairness or slice metrics; only a better model is registered in a model registry with a version and stage. Deployment uses familiar strategies: shadow mode, canary or A/B tests on live traffic, with monitoring for latency, prediction drift and data drift. Everything should be reproducible: code commit, data version, environment image and random seeds recorded with the model. Retraining can be triggered by schedule, new data arrival or drift alerts.",
        ["Retraining a recommendation model weekly with an automated quality gate.", "Promoting a fraud model only if precision at a fixed recall improves.", "Running a new model in shadow mode before it serves real decisions."],
        [
            "Version data, code, environment and model together.",
            "Data validation is a pipeline stage like unit tests.",
            "Evaluation gates compare candidate vs production on fixed holdout data.",
            "Model registry tracks versions, stages and lineage.",
            "Monitor data drift and prediction drift after deploy.",
        ],
        [
            ex("Training workflow with an evaluation gate", "advanced", "Train on a versioned dataset; register only if metrics beat production.", "yaml", """
                name: train
                on:
                  schedule:
                    - cron: "0 3 * * 1"
                  workflow_dispatch:
                permissions:
                  contents: read
                  id-token: write
                jobs:
                  train:
                    runs-on: [self-hosted, gpu]
                    timeout-minutes: 180
                    steps:
                      - uses: actions/checkout@v4
                      - run: pip install -r requirements.lock
                      - run: dvc pull data/train.parquet data/holdout.parquet
                      - run: python -m pipeline.validate_data data/train.parquet
                      - run: python -m pipeline.train --seed 42 --out model/
                      - run: python -m pipeline.evaluate --candidate model/ --baseline models:/fraud/Production --min-gain 0.005
                      - run: python -m pipeline.register --model model/ --name fraud --stage Staging
            """, runnable=False),
            ex("Data and model versioning commands", "intermediate", "DVC for data, MLflow for runs and registry.", "bash", """
                dvc add data/train.parquet && git add data/train.parquet.dvc && git commit -m "data: october snapshot"
                dvc push
                mlflow run . -P epochs=20 -P seed=42
                mlflow models serve -m "models:/fraud/Staging" -p 5001
            """, runnable=False),
        ],
        ["dvc pull · dvc push · dvc repro", "mlflow run . -P seed=42", "models:/name/Production", "great_expectations checkpoint run", "Shadow -> canary -> full"],
        ["Comparing against a different holdout set each time makes the gate meaningless.", "Training-serving skew: features computed differently online and offline.", "Not recording data version makes a model impossible to reproduce."],
        [
            qa("intermediate", "How is MLOps CI/CD different from normal CI/CD?", "Besides code, the pipeline must validate and version data, train models, evaluate them against a baseline and manage model versions in a registry. Behaviour can change without code changes when data shifts, so monitoring for drift and retraining are part of the loop."),
            qa("intermediate", "What is a model registry?", "A catalogue of trained model versions with metadata, lineage (code commit, data version, metrics) and lifecycle stages such as Staging and Production. Deployment pulls a specific registered version."),
            qa("advanced", "What is training-serving skew and how do you prevent it?", "It is a mismatch between how features are computed in training and in production, which silently degrades accuracy. Share feature code or use a feature store, and test with production-like inputs."),
            qa("advanced", "How do you safely deploy a new model?", "Pass an offline evaluation gate, then run it in shadow mode to compare predictions on real traffic without affecting users, then canary or A/B test with business and latency metrics, with automatic rollback to the previous registered version."),
        ],
        ["dark-launch-shadow", "canary", "build-systems"],
        chain(
            ("Data", "versioned", "Validate data", "A versioned dataset is pulled and checked for schema and drift."),
            ("Train", "seeded run", "Train", "Training runs with logged parameters, seed and environment.", "dataset"),
            ("Evaluate", "vs production", "Gate", "Candidate metrics must beat the production model on holdout data.", "model"),
            ("Register", "model registry", "Version", "The model is registered with lineage and moved to Staging.", "pass"),
            ("Serve", "shadow, canary", "Deploy", "Shadow and canary traffic confirm it before full rollout.", "version"),
            ("Monitor", "drift alerts", "Watch", "Drift and quality metrics can trigger retraining.", "live"),
        ),
    ),
    topic(
        "gha-workflows", "GitHub Actions: Workflows, Jobs, Steps", "pipelines", "basic", "GA",
        "Events trigger workflows; workflows contain jobs on runners; jobs run steps.",
        "A theatre production: an event (curtain call) starts the show (workflow); each act (job) gets its own stage crew and set (runner); inside an act, lines are delivered in order (steps).",
        "GitHub Actions workflows are YAML files in .github/workflows triggered by events: push, pull_request, schedule, workflow_dispatch (manual with inputs), release, workflow_call and many more, with filters on branches, tags and paths. A workflow contains jobs, which run in parallel by default on separate runners (GitHub-hosted ubuntu, windows, macos, or self-hosted) and can depend on each other with needs. Each job is a list of steps that either run shell commands (run:) or use an action (uses: owner/repo@ref), sharing the job's filesystem. Data moves between steps via GITHUB_OUTPUT and environment files, between jobs via job outputs, and between workflows or runs via artifacts. Contexts and expressions (${{ github.sha }}, ${{ secrets.X }}, if: conditions) make behaviour dynamic. The GITHUB_TOKEN is issued per run and should be scoped down with permissions: at workflow or job level. Third-party actions run with the job's privileges, so pin them to a full commit SHA or at least a trusted version tag, and keep timeouts and concurrency groups explicit.",
        ["Running CI on pull requests and deployments on pushes to main.", "A manual release workflow with typed inputs.", "Nightly scheduled dependency audits."],
        [
            "Workflow -> jobs (parallel, separate runners) -> steps (sequential, same runner).",
            "needs: creates job dependencies; outputs pass small values between jobs.",
            "permissions: should be least privilege, default contents: read.",
            "Pin third-party actions to a commit SHA for supply-chain safety.",
            "Expressions untrusted input (PR titles) must not be interpolated into run: scripts.",
        ],
        [
            ex("Jobs, needs and outputs", "basic", "Build computes a version, deploy consumes it.", "yaml", """
                name: build-deploy
                on:
                  push:
                    branches: [main]
                  workflow_dispatch:
                    inputs:
                      dry_run:
                        type: boolean
                        default: true
                permissions:
                  contents: read
                jobs:
                  build:
                    runs-on: ubuntu-latest
                    timeout-minutes: 10
                    outputs:
                      version: ${{ steps.v.outputs.version }}
                    steps:
                      - uses: actions/checkout@v4
                      - id: v
                        run: echo "version=1.4.${{ github.run_number }}" >> "$GITHUB_OUTPUT"
                      - run: make build VERSION=${{ steps.v.outputs.version }}
                      - uses: actions/upload-artifact@v4
                        with:
                          name: dist
                          path: dist/
                  deploy:
                    needs: build
                    if: ${{ !inputs.dry_run }}
                    runs-on: ubuntu-latest
                    steps:
                      - uses: actions/download-artifact@v4
                        with:
                          name: dist
                      - run: echo "Deploying ${{ needs.build.outputs.version }}"
            """, runnable=False),
            ex("Avoid script injection", "intermediate", "Pass untrusted context through env, never inline into the script.", "yaml", """
                on: [pull_request]
                permissions:
                  contents: read
                jobs:
                  title-check:
                    runs-on: ubuntu-latest
                    steps:
                      - name: Check PR title
                        env:
                          TITLE: ${{ github.event.pull_request.title }}
                        run: |
                          if ! printf '%s' "$TITLE" | grep -Eq '^(feat|fix|chore|docs)(\\(.+\\))?: '; then
                            echo "::error::PR title must follow Conventional Commits"; exit 1
                          fi
            """, runnable=False),
            ex("Inspect runs with gh", "basic", "Trigger, watch and debug from the terminal.", "bash", """
                gh workflow list
                gh workflow run build-deploy.yml -f dry_run=false
                gh run watch
                gh run view --log-failed
                gh run rerun --failed
            """, runnable=False),
        ],
        ["gh workflow run x.yml -f key=val", "gh run view --log-failed", "echo k=v >> $GITHUB_OUTPUT", "needs: · outputs: · if:", "permissions: contents: read"],
        ["Interpolating ${{ github.event.* }} into run: allows shell injection from PR titles or branch names.", "Jobs do not share files; use artifacts to pass build output.", "Default GITHUB_TOKEN permissions may be write-all in older repos; set permissions explicitly.", "Scheduled workflows are disabled after 60 days of repo inactivity."],
        [
            qa("basic", "What is the hierarchy in GitHub Actions?", "An event triggers a workflow; a workflow has one or more jobs, each running on its own runner; each job runs ordered steps that execute commands or actions in the same environment."),
            qa("basic", "How do you pass data between jobs?", "Small values via job outputs (written to GITHUB_OUTPUT in a step and declared under outputs), consumed with needs.<job>.outputs.<name>. Files go through upload-artifact and download-artifact."),
            qa("intermediate", "Why set permissions in a workflow?", "The GITHUB_TOKEN gets whatever permissions are configured; declaring the minimum, such as contents: read, limits damage if a step or third-party action is compromised."),
            qa("intermediate", "What is script injection in GitHub Actions?", "When attacker-controlled context such as a PR title is placed directly in a run: script via ${{ }}, it is substituted before the shell runs and can execute commands. Pass such values through env variables and quote them."),
            qa("advanced", "Why pin actions to a commit SHA?", "Tags like v4 are mutable and can be moved to malicious code if the action's repository is compromised. A full commit SHA is immutable; Dependabot or Renovate can keep SHA pins updated."),
        ],
        ["gha-reusable", "gha-concurrency", "gha-environments", "runner-security"],
        chain(
            ("Event", "push, PR, cron", "Trigger", "An event matching on: filters starts a workflow run."),
            ("Workflow", ".github/workflows", "Plan jobs", "GitHub reads the YAML and builds the job dependency graph.", "event"),
            ("Job", "fresh runner", "Assign runner", "Each ready job gets a runner and a scoped GITHUB_TOKEN.", "job"),
            ("Steps", "run / uses", "Execute", "Steps run in order, sharing the workspace and env files.", "token"),
            ("Result", "checks, artifacts", "Report", "Status checks, logs and artifacts are attached to the commit.", "status"),
        ),
    ),
]

_BATCH_3 = [
    topic(
        "gha-reusable", "Reusable Workflows & Composite Actions", "pipelines", "intermediate", "RW",
        "Share pipeline logic as versioned building blocks instead of copy-pasted YAML.",
        "Franchise kitchens: head office publishes a standard recipe card (reusable workflow) and a pre-mixed spice blend (composite action). Each branch uses them as is, and an update reaches everyone through a new card version.",
        "GitHub Actions offers two reuse mechanisms. A reusable workflow is a whole workflow with on: workflow_call, typed inputs, secrets and outputs; a caller invokes it as a job with uses: org/repo/.github/workflows/build.yml@v2. It can contain multiple jobs, its own runners, environments and permissions, which makes it ideal for standardised build-and-deploy pipelines owned by a platform team. A composite action is an action.yml with runs: using: composite that bundles several steps; it runs inside the caller's job and runner, sharing the workspace, so it suits small step sequences such as 'set up toolchain and cache'. JavaScript and Docker actions are the other action types for custom logic. Secrets are not inherited automatically by reusable workflows: pass them explicitly or use secrets: inherit within the same organisation. Reusable workflows can nest a few levels deep, and the caller's permissions cap what the called workflow can get. Version shared components with tags or SHAs, keep a changelog and test them in their own repository before consumers upgrade.",
        ["One golden build-scan-push workflow used by 200 service repos.", "A composite action that installs a toolchain and configures caching.", "Org-wide deployment workflow with consistent environments and approvals."],
        [
            "Reusable workflow = jobs-level reuse via on: workflow_call.",
            "Composite action = steps-level reuse inside the caller's job.",
            "Secrets must be passed explicitly or with secrets: inherit.",
            "Caller permissions are the ceiling for the called workflow.",
            "Version by tag or SHA; consumers upgrade deliberately.",
        ],
        [
            ex("Reusable workflow (called side)", "intermediate", "Typed inputs, a required secret and an output.", "yaml", """
                # acme/pipelines/.github/workflows/build-image.yml
                name: build-image
                on:
                  workflow_call:
                    inputs:
                      image:
                        type: string
                        required: true
                      context:
                        type: string
                        default: "."
                    outputs:
                      digest:
                        value: ${{ jobs.build.outputs.digest }}
                permissions:
                  contents: read
                  packages: write
                jobs:
                  build:
                    runs-on: ubuntu-latest
                    outputs:
                      digest: ${{ steps.push.outputs.digest }}
                    steps:
                      - uses: actions/checkout@v4
                      - uses: docker/setup-buildx-action@v3
                      - uses: docker/login-action@v3
                        with:
                          registry: ghcr.io
                          username: ${{ github.actor }}
                          password: ${{ secrets.GITHUB_TOKEN }}
                      - id: push
                        uses: docker/build-push-action@v6
                        with:
                          context: ${{ inputs.context }}
                          push: true
                          tags: ghcr.io/${{ inputs.image }}:${{ github.sha }}
            """, runnable=False),
            ex("Caller workflow", "intermediate", "Uses the shared workflow pinned to a tag and consumes its output.", "yaml", """
                name: ci
                on:
                  push:
                    branches: [main]
                permissions:
                  contents: read
                  packages: write
                jobs:
                  image:
                    uses: acme/pipelines/.github/workflows/build-image.yml@v2.3.0
                    with:
                      image: acme/checkout-api
                  report:
                    needs: image
                    runs-on: ubuntu-latest
                    steps:
                      - run: echo "pushed digest ${{ needs.image.outputs.digest }}"
            """, runnable=False),
            ex("Composite action", "basic", "Bundle setup steps; shell must be declared for run steps.", "yaml", """
                # .github/actions/setup-node-pnpm/action.yml
                name: setup-node-pnpm
                description: Install Node and pnpm with caching
                inputs:
                  node-version:
                    default: "22"
                runs:
                  using: composite
                  steps:
                    - uses: pnpm/action-setup@v4
                      with:
                        version: 9
                    - uses: actions/setup-node@v4
                      with:
                        node-version: ${{ inputs.node-version }}
                        cache: pnpm
                    - run: pnpm install --frozen-lockfile
                      shell: bash
            """, runnable=False),
        ],
        ["on: workflow_call: inputs/secrets/outputs", "jobs.x.uses: org/repo/.github/workflows/f.yml@ref", "secrets: inherit", "runs: using: composite", "uses: ./.github/actions/name"],
        ["Composite run steps need an explicit shell: or the action fails to load.", "Forgetting to pass secrets leaves them empty in the called workflow without an obvious error.", "Pinning shared workflows to @main means every consumer changes when main changes."],
        [
            qa("basic", "Reusable workflow vs composite action?", "A reusable workflow is called as a job and can contain multiple jobs with their own runners and environments. A composite action is a bundle of steps that runs within the caller's job on the caller's runner."),
            qa("intermediate", "How do secrets reach a reusable workflow?", "They must be declared under on.workflow_call.secrets and passed by the caller, or the caller can use secrets: inherit to pass all its secrets when both are in the same organisation or enterprise."),
            qa("intermediate", "How do permissions work across a workflow_call?", "The called workflow's GITHUB_TOKEN permissions can only be the same as or lower than the caller's. If the caller grants contents: read, the called workflow cannot elevate to write."),
            qa("advanced", "How would you roll out a change to a reusable workflow used by hundreds of repos?", "Release it as a new version tag, test it in canary repositories, then let Renovate or Dependabot open upgrade PRs to consumers. Avoid moving tags consumers rely on, and keep a changelog of breaking input changes."),
        ],
        ["gha-workflows", "pipeline-as-code", "jenkins-shared-libs"],
        chain(
            ("Author", "platform team", "Publish", "The platform team writes a workflow_call workflow and tags v2.3.0."),
            ("Call", "uses: ...@v2.3.0", "Consume", "A service repo calls it as a job with inputs.", "tag"),
            ("Pass", "inputs, secrets", "Wire up", "Inputs and explicitly passed secrets flow into the called jobs.", "inputs"),
            ("Run", "called jobs", "Execute", "The shared jobs run with permissions capped by the caller.", "secrets"),
            ("Outputs", "digest etc.", "Return", "Outputs flow back to later jobs in the caller.", "digest"),
        ),
    ),
    topic(
        "gha-concurrency", "Triggers, Concurrency & Timeouts", "pipelines", "intermediate", "CO",
        "Control when workflows run and stop overlapping runs from racing each other.",
        "A single-lane bridge with a traffic light. Only one convoy crosses at a time; a newer convoy can either wait its turn or send the older one back if it is out of date.",
        "Trigger design decides how much CI you pay for and how safe it is. Filter push and pull_request by branches, tags and paths; use workflow_dispatch for manual runs with inputs, schedule for cron jobs, and workflow_run or repository_dispatch to chain workflows. pull_request runs untrusted fork code with a read-only token and no secrets, while pull_request_target runs in the base repository context with secrets, so it must never check out and execute PR code. The concurrency key groups runs: only one run or job in a group executes at a time, and cancel-in-progress: true cancels older in-flight runs when a newer one starts. For PR CI, a group like ci-${{ github.ref }} with cancellation saves minutes when developers push repeatedly. For deployments, use a group per environment without cancellation so a deploy is never killed halfway and deploys run in order. timeout-minutes on jobs and steps caps stuck runs (the default is six hours). Combined, these settings give fast feedback, predictable deploy ordering and controlled cost.",
        ["Cancelling superseded PR builds when a developer pushes again.", "Guaranteeing only one production deploy runs at a time.", "Running a nightly job and a manual job with inputs."],
        [
            "cancel-in-progress: true for CI; false for deploys.",
            "Group by github.ref for PRs, by environment name for deploys.",
            "pull_request_target has secrets; never run PR code in it.",
            "Set timeout-minutes; the default six hours wastes money.",
            "paths and branches filters cut unnecessary runs.",
        ],
        [
            ex("PR CI that cancels superseded runs", "basic", "Newer pushes to the same PR cancel older runs.", "yaml", """
                name: ci
                on:
                  pull_request:
                    paths-ignore: ["docs/**", "**.md"]
                permissions:
                  contents: read
                concurrency:
                  group: ci-${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
                  cancel-in-progress: true
                jobs:
                  test:
                    runs-on: ubuntu-latest
                    timeout-minutes: 15
                    steps:
                      - uses: actions/checkout@v4
                      - run: make test
            """, runnable=False),
            ex("Serialised production deploys", "intermediate", "One deploy at a time per environment, never cancelled mid-flight.", "yaml", """
                name: deploy
                on:
                  push:
                    branches: [main]
                permissions:
                  contents: read
                  id-token: write
                jobs:
                  production:
                    runs-on: ubuntu-latest
                    environment: production
                    timeout-minutes: 30
                    concurrency:
                      group: deploy-production
                      cancel-in-progress: false
                    steps:
                      - uses: actions/checkout@v4
                      - run: ./scripts/deploy.sh production "${GITHUB_SHA}"
            """, runnable=False),
            ex("Schedule and manual dispatch", "basic", "Nightly run plus a manual trigger with a choice input.", "yaml", """
                on:
                  schedule:
                    - cron: "30 1 * * *"
                  workflow_dispatch:
                    inputs:
                      suite:
                        type: choice
                        options: [smoke, full]
                        default: smoke
            """, runnable=False),
        ],
        ["concurrency: group · cancel-in-progress", "timeout-minutes: 15", "on: pull_request: paths-ignore:", "on: workflow_dispatch: inputs:", "gh run cancel <id>"],
        ["cancel-in-progress on a deploy group can leave infrastructure half-migrated.", "pull_request_target plus checkout of the PR head is a classic secret-exfiltration hole.", "Cron times are UTC and may be delayed under load; do not rely on exact timing."],
        [
            qa("basic", "What does the concurrency key do?", "It groups runs or jobs so only one in the group executes at a time. With cancel-in-progress: true, a new run cancels the older in-progress one; otherwise the new one waits."),
            qa("intermediate", "Why not cancel in-progress deployments?", "Killing a deploy midway can leave partial migrations or a half-rolled-out service. Deploys should queue per environment and complete in order."),
            qa("intermediate", "pull_request vs pull_request_target?", "pull_request runs the PR's merge commit with no secrets and a read-only token for forks. pull_request_target runs the base branch workflow with secrets and write token, so it is only safe for actions like labelling that never execute PR code."),
            qa("advanced", "A deploy workflow ran twice and the older commit finished last, rolling production back. How do you prevent it?", "Use a concurrency group per environment with cancel-in-progress: false so deploys serialise in order, and make the deploy script refuse to deploy a commit older than what is currently live, for example by comparing to the recorded deployed SHA."),
        ],
        ["gha-workflows", "gha-environments", "cost-speed"],
        chain(
            ("Push", "new commit", "New run", "A developer pushes again to the same pull request."),
            ("Group", "ci-<PR number>", "Match group", "The new run computes its concurrency group key.", "run"),
            ("Cancel", "older run", "Supersede", "With cancel-in-progress, the older run in the group is cancelled.", "key"),
            ("Run", "latest only", "Execute", "Only the latest commit consumes runner minutes, within its timeout.", "slot"),
        ),
    ),
    topic(
        "gha-environments", "Environments, Protection Rules & Deployments", "pipelines", "intermediate", "EN",
        "Environments scope secrets and add reviewers, wait timers and branch rules to deploy jobs.",
        "A bank vault room: the key (secret) is kept inside the room, not handed to anyone in the lobby. To enter you need the right badge (branch), a manager's signature (reviewer) and sometimes a time lock.",
        "A GitHub environment (dev, staging, production) is a named deployment target attached to a job with environment: name. Environments hold their own secrets and variables, so production credentials are only available to jobs that target production and pass its rules. Protection rules include required reviewers (up to six people or teams, optionally preventing self-review), a wait timer, deployment branch and tag policies (only main or v* tags may deploy), and custom deployment protection rules from apps that check external systems such as change management or monitoring. When a job targets a protected environment, it pauses until approved, and the deployment is recorded with its commit, actor and status in the repository's deployment history. OIDC tokens include the environment in the subject claim (repo:org/repo:environment:production), which lets cloud trust policies grant production roles only to production jobs. GitLab has a similar concept with protected environments and deployment approvals, and Azure DevOps uses environments with checks.",
        ["Requiring a release manager to approve production deploys.", "Keeping production database credentials away from PR jobs.", "Restricting production deploys to the main branch and release tags."],
        [
            "Environment secrets are only exposed to jobs targeting that environment.",
            "Required reviewers pause the job until approval.",
            "Deployment branch policies block deploys from feature branches.",
            "OIDC subject includes environment: use it in cloud trust policies.",
        ],
        [
            ex("Promote through environments", "intermediate", "Same artifact; production gated by the environment's rules.", "yaml", """
                name: release
                on:
                  push:
                    tags: ["v*"]
                permissions:
                  contents: read
                  id-token: write
                jobs:
                  staging:
                    runs-on: ubuntu-latest
                    environment:
                      name: staging
                      url: https://staging.example.com
                    steps:
                      - uses: actions/checkout@v4
                      - uses: aws-actions/configure-aws-credentials@v4
                        with:
                          role-to-assume: ${{ vars.DEPLOY_ROLE_ARN }}
                          aws-region: eu-west-1
                      - run: ./deploy.sh staging "${GITHUB_REF_NAME}"
                  production:
                    needs: staging
                    runs-on: ubuntu-latest
                    environment:
                      name: production
                      url: https://www.example.com
                    steps:
                      - uses: actions/checkout@v4
                      - uses: aws-actions/configure-aws-credentials@v4
                        with:
                          role-to-assume: ${{ vars.DEPLOY_ROLE_ARN }}
                          aws-region: eu-west-1
                      - run: ./deploy.sh production "${GITHUB_REF_NAME}"
            """, runnable=False),
            ex("Configure an environment via API", "advanced", "Reviewers, wait timer and branch policy.", "bash", """
                gh api -X PUT repos/acme/shop/environments/production --input - <<'JSON'
                {"wait_timer": 5,
                 "prevent_self_review": true,
                 "reviewers": [{"type": "Team", "id": 123456}],
                 "deployment_branch_policy": {"protected_branches": false, "custom_branch_policies": true}}
                JSON
                gh api -X POST repos/acme/shop/environments/production/deployment-branch-policies -f name='v*' -f type=tag
            """, runnable=False),
        ],
        ["environment: name: production", "gh api repos/O/R/environments", "vars.NAME (environment variables)", "secrets.NAME (environment secrets)", "sub: repo:O/R:environment:production"],
        ["Putting production secrets at repo level makes them available to every workflow.", "Required reviewers who rubber-stamp make the gate theatre; give them context (diff, change summary).", "Environments are not enforced on reusable workflow callers unless the job declares environment."],
        [
            qa("basic", "What is a GitHub environment?", "A named deployment target with its own secrets, variables and protection rules. Jobs that declare environment: name must satisfy those rules before running."),
            qa("intermediate", "How do environments improve secret security?", "Secrets stored on an environment are only injected into jobs that target it and pass its protection rules, so PR jobs and other workflows never see production credentials."),
            qa("intermediate", "What protection rules exist?", "Required reviewers, wait timers, deployment branch or tag policies and custom deployment protection rules provided by GitHub Apps that can query external systems."),
            qa("advanced", "How do environments interact with OIDC to the cloud?", "The OIDC token's sub claim contains environment:production when the job targets that environment. The cloud role's trust policy can require that exact subject so only approved production jobs can assume the production role."),
        ],
        ["approvals-gates", "oidc-federation", "env-promotion"],
        chain(
            ("Job", "env: production", "Target", "A deploy job declares the production environment."),
            ("Rules", "branch policy", "Check rules", "GitHub verifies the ref is allowed to deploy to production.", "request"),
            ("Approve", "reviewers", "Human gate", "Required reviewers approve; a wait timer may apply.", "pending"),
            ("Secrets", "env-scoped", "Unlock", "Environment secrets and the environment OIDC claim become available.", "approved"),
            ("Deploy", "recorded", "Run and log", "The job deploys and the deployment is recorded in history.", "creds"),
        ),
    ),
    topic(
        "gitlab-ci", "GitLab CI: Stages, Rules & needs DAG", "pipelines", "intermediate", "GL",
        "A .gitlab-ci.yml of jobs in stages, filtered by rules and sped up with needs.",
        "An assembly line with stations (stages). By default every item waits until the whole station finishes, but with needs a part can skip ahead as soon as the one part it depends on is ready.",
        "GitLab CI is configured in .gitlab-ci.yml at the repository root. Jobs are assigned to stages (build, test, deploy by default); all jobs in a stage run in parallel and the next stage starts only when the previous one succeeds. rules decide whether a job is added to a pipeline, using if expressions on predefined variables ($CI_PIPELINE_SOURCE, $CI_COMMIT_BRANCH, $CI_COMMIT_TAG), changes for paths and exists for files; workflow:rules control whether a pipeline is created at all, which avoids duplicate branch and merge request pipelines. The needs keyword turns stage order into a directed acyclic graph: a job starts as soon as the jobs it needs finish, and it only downloads their artifacts, which can cut pipeline time dramatically. Jobs run on GitLab Runners (shared or self-hosted, with Docker, Kubernetes or shell executors) selected by tags. Reuse comes from include (local, project, remote and CI/CD component catalog), extends and YAML anchors. Variables can be protected (only on protected branches) and masked, and environments plus deployment approvals gate production.",
        ["Merge request pipelines that skip deploy jobs.", "Fanning out build jobs per service and starting tests as each build finishes.", "Sharing templates across projects with include: project."],
        [
            "Stages run in order; jobs inside a stage run in parallel.",
            "rules replace only/except; first matching rule wins.",
            "workflow:rules decide if a pipeline exists at all.",
            "needs creates a DAG and limits artifact downloads.",
            "Protected and masked variables limit secret exposure.",
        ],
        [
            ex("Rules, workflow and needs", "intermediate", "MR and main pipelines only; tests start as soon as their build is done.", "yaml", """
                workflow:
                  rules:
                    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
                    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
                    - if: $CI_COMMIT_TAG

                stages: [build, test, deploy]

                default:
                  image: node:22
                  interruptible: true

                build-api:
                  stage: build
                  script: [make -C api build]
                  artifacts:
                    paths: [api/dist/]

                build-web:
                  stage: build
                  script: [make -C web build]
                  artifacts:
                    paths: [web/dist/]

                test-api:
                  stage: test
                  needs: [build-api]
                  script: [make -C api test]

                test-web:
                  stage: test
                  needs: [build-web]
                  script: [make -C web test]

                deploy-prod:
                  stage: deploy
                  needs: [test-api, test-web]
                  environment:
                    name: production
                    url: https://www.example.com
                  rules:
                    - if: $CI_COMMIT_TAG =~ /^v[0-9]+/
                      when: manual
                  interruptible: false
                  script: [./deploy.sh production "$CI_COMMIT_TAG"]
            """, runnable=False),
            ex("Includes and extends", "advanced", "Shared templates from another project, pinned to a ref.", "yaml", """
                include:
                  - project: acme/ci-templates
                    ref: v3.1.0
                    file: /templates/docker-build.yml
                  - component: $CI_SERVER_FQDN/acme/components/sast@1.4.0

                .test-base:
                  stage: test
                  image: python:3.13
                  before_script: [pip install -r requirements.txt]

                unit:
                  extends: .test-base
                  script: [pytest -q tests/unit]
            """, runnable=False),
        ],
        ["rules: - if: $CI_PIPELINE_SOURCE == 'merge_request_event'", "needs: [job]", "include: project/ref/file", "extends: .template", "interruptible: true"],
        ["Without workflow:rules, pushes to an MR branch can create duplicate branch and MR pipelines.", "A job with needs: [] starts immediately, even before earlier stages.", "Unprotected variables are exposed to pipelines on any branch, including untrusted ones."],
        [
            qa("basic", "How do stages work in GitLab CI?", "Stages define an ordered list; all jobs in one stage run in parallel and the next stage starts only after every job in the previous stage succeeds, unless needs is used."),
            qa("intermediate", "What do rules do and how are they evaluated?", "They decide if a job is included and with what when value. Rules are evaluated in order and the first match applies; if none match, the job is excluded."),
            qa("intermediate", "What does needs give you?", "A DAG: a job starts as soon as the specific jobs it needs complete, regardless of stage, and only fetches their artifacts. This shortens pipelines with independent parallel paths."),
            qa("advanced", "How do you avoid duplicate pipelines for merge requests?", "Use workflow:rules that create pipelines for merge_request_event, the default branch and tags, and skip branch pipelines when an MR is open (for example with $CI_OPEN_MERGE_REQUESTS checks)."),
            qa("advanced", "How should secrets be protected in GitLab CI?", "Store them as masked and protected CI/CD variables, scoped to environments, so they appear only in pipelines on protected branches or tags. Prefer OIDC id_tokens to cloud providers over static keys."),
        ],
        ["gha-workflows", "jenkins-declarative", "monorepo-pipelines"],
        chain(
            ("Push/MR", "event", "Trigger", "A push or merge request event reaches GitLab."),
            ("Workflow", "workflow:rules", "Create?", "workflow:rules decide whether a pipeline is created at all.", "event"),
            ("Rules", "per job", "Select jobs", "Each job's rules decide if it joins this pipeline.", "pipeline"),
            ("DAG", "needs", "Schedule", "Jobs start as soon as the jobs they need have finished.", "jobs"),
            ("Runner", "tags, executor", "Execute", "Matching runners run jobs in Docker, Kubernetes or shell executors.", "ready"),
            ("Deploy", "environment", "Release", "Deploy jobs record environments and can require manual approval.", "artifacts"),
        ),
    ),
    topic(
        "jenkins-declarative", "Jenkins Declarative Pipelines & Agents", "pipelines", "intermediate", "JK",
        "A Jenkinsfile describing stages, agents, post actions and credentials binding.",
        "A conductor's score: each section (stage) is written down, which musicians (agents) play it, and what happens at the end whether the concert went well or not (post).",
        "Jenkins is a self-hosted automation server with a large plugin ecosystem. Modern Jenkins jobs are defined in a Jenkinsfile using declarative pipeline syntax: a pipeline block with an agent, options, environment, stages, steps and post sections. Agents choose where work runs: any, a label for a node pool, docker for a container image, or kubernetes to launch an ephemeral pod per build via the Kubernetes plugin, which is the recommended way to avoid long-lived, dirty build machines. when conditions skip stages by branch, tag or changeset; parallel runs stages concurrently; input pauses for approvals; options add timeouts, retries and disableConcurrentBuilds. Credentials are stored in Jenkins (or an external vault) and exposed with withCredentials or credentials() in environment, which masks them in logs. Multibranch pipelines and organisation folders discover branches and pull requests automatically. Operating Jenkins is the main cost: controller upgrades, plugin compatibility and security patches, backups, and making sure builds never run on the controller itself.",
        ["Enterprises with existing Jenkins estates and on-premise requirements.", "Ephemeral Kubernetes pod agents per build.", "Multibranch pipelines building every PR automatically."],
        [
            "Declarative syntax: pipeline, agent, stages, steps, post.",
            "Run builds on agents, never on the controller (0 executors).",
            "Kubernetes or Docker agents give clean, ephemeral environments.",
            "withCredentials masks secrets; avoid echoing or string-interpolating them.",
            "Keep plugins minimal and updated; they are the main attack surface.",
        ],
        [
            ex("Declarative Jenkinsfile with Kubernetes agent", "intermediate", "Parallel tests, credentials binding, post actions and a manual gate.", "groovy", """
                pipeline {
                  agent {
                    kubernetes {
                      yaml '''
                        apiVersion: v1
                        kind: Pod
                        spec:
                          containers:
                          - name: build
                            image: maven:3.9-eclipse-temurin-21
                            command: ["sleep"]
                            args: ["infinity"]
                      '''
                      defaultContainer 'build'
                    }
                  }
                  options {
                    timeout(time: 30, unit: 'MINUTES')
                    disableConcurrentBuilds()
                    buildDiscarder(logRotator(numToKeepStr: '30'))
                  }
                  stages {
                    stage('Build') {
                      steps { sh 'mvn -B -DskipTests package' }
                    }
                    stage('Test') {
                      parallel {
                        stage('Unit') { steps { sh 'mvn -B test' } }
                        stage('Integration') { steps { sh 'mvn -B verify -Pintegration' } }
                      }
                    }
                    stage('Publish') {
                      when { branch 'main' }
                      steps {
                        withCredentials([usernamePassword(credentialsId: 'nexus-ci', usernameVariable: 'NEXUS_USER', passwordVariable: 'NEXUS_PASS')]) {
                          sh 'mvn -B deploy -s ci-settings.xml'
                        }
                      }
                    }
                    stage('Approve prod') {
                      when { branch 'main' }
                      steps { input message: 'Deploy to production?', submitter: 'release-managers' }
                    }
                  }
                  post {
                    always { junit '**/target/surefire-reports/*.xml' }
                    failure { echo "Build failed: ${env.BUILD_URL}" }
                  }
                }
            """, runnable=False),
            ex("Lint and operate Jenkins", "basic", "Validate a Jenkinsfile and manage the controller via CLI.", "bash", """
                curl -X POST -F "jenkinsfile=<Jenkinsfile" "$JENKINS_URL/pipeline-model-converter/validate" --user "$JENKINS_USER:$JENKINS_API_TOKEN"
                java -jar jenkins-cli.jar -s "$JENKINS_URL" -auth @creds.txt list-plugins
                java -jar jenkins-cli.jar -s "$JENKINS_URL" -auth @creds.txt build my-pipeline -s -v
            """, runnable=False),
        ],
        ["Jenkinsfile: pipeline { agent stages post }", "when { branch 'main' }", "withCredentials([...]) { sh '...' }", "parallel { stage(...) }", "options { timeout(...) }"],
        ["Using double quotes around secret variables in sh lets Groovy interpolate and leak them; use single quotes.", "Running builds on the controller exposes its secrets and config to build scripts.", "Plugin sprawl makes upgrades risky; each plugin is code with controller privileges."],
        [
            qa("basic", "Declarative vs scripted pipeline?", "Declarative uses a structured pipeline block with fixed sections and validation, which is easier to read and lint. Scripted is free-form Groovy with more flexibility but more room for mistakes."),
            qa("intermediate", "What is an agent in Jenkins?", "The executor environment where stages run: a labelled node, a Docker container or a Kubernetes pod. Using ephemeral agents gives clean, isolated builds."),
            qa("intermediate", "How do you use credentials safely in a Jenkinsfile?", "Store them in the Jenkins credentials store or an external vault and bind them with withCredentials, which masks them in logs. Reference them inside single-quoted sh strings so the shell, not Groovy, expands them."),
            qa("advanced", "How do you secure a Jenkins controller?", "Set controller executors to zero, require authentication with a matrix or role-based authorisation, keep core and plugins patched, restrict script approval, use agents in isolated networks and back up JENKINS_HOME. Prefer short-lived cloud credentials over long-lived keys in the credential store."),
        ],
        ["jenkins-shared-libs", "gitlab-ci", "runner-security"],
        chain(
            ("SCM", "Jenkinsfile", "Discover", "A multibranch job detects a new commit and reads the Jenkinsfile."),
            ("Agent", "k8s pod", "Provision", "Jenkins launches an ephemeral pod agent for this build.", "build"),
            ("Stages", "build, test", "Run stages", "Stages run in order, with parallel blocks fanning out.", "pod"),
            ("Creds", "withCredentials", "Bind secrets", "Credentials are bound only within the steps that need them.", "stage"),
            ("Post", "always/failure", "Finish", "Post blocks publish reports and notify, then the pod is deleted.", "result"),
        ),
    ),
    topic(
        "jenkins-shared-libs", "Jenkins Shared Libraries", "pipelines", "advanced", "JL",
        "Versioned Groovy libraries that turn long Jenkinsfiles into one-line standard pipelines.",
        "A company style guide with ready-made templates. Each team writes 'use the standard report template, version 3' instead of re-designing the cover page every time.",
        "Shared libraries let organisations centralise pipeline logic in a separate Git repository with a defined structure: vars/ holds global variables and custom steps (vars/buildService.groovy exposes a buildService step), src/ holds Groovy classes in packages, and resources/ holds non-Groovy files such as templates loaded with libraryResource. Libraries are configured globally or per folder and loaded with @Library('acme-lib@v4.2.0') _ at the top of a Jenkinsfile, which lets each repository pin a version. A common pattern is a full pipeline template: the service Jenkinsfile becomes standardPipeline(language: 'java', deploy: true), and the library defines stages, agents, scanning and deployment. Global trusted libraries run outside the Groovy sandbox, so changes to them need strict review and branch protection; untrusted (folder-level) libraries run in the sandbox. Libraries should have unit tests with JenkinsPipelineUnit and integration tests against a test Jenkins instance before being tagged. Versioning matters: loading the default branch implicitly means every pipeline changes the moment someone merges.",
        ["Standardising build, scan and deploy across 400 microservices.", "Exposing a deployToK8s step with built-in safety checks.", "Upgrading every pipeline's scanning tool by bumping one library version."],
        [
            "vars/*.groovy = custom steps; src/ = classes; resources/ = files.",
            "Load with @Library('name@version') _ and pin versions.",
            "Global trusted libraries bypass the sandbox; protect them tightly.",
            "Test with JenkinsPipelineUnit before tagging a release.",
        ],
        [
            ex("Custom step in vars/", "advanced", "A standard pipeline exposed as one step.", "groovy", """
                // vars/standardPipeline.groovy
                def call(Map cfg = [:]) {
                  pipeline {
                    agent { label cfg.get('agent', 'linux-docker') }
                    options { timeout(time: cfg.get('timeoutMinutes', 30), unit: 'MINUTES') }
                    stages {
                      stage('Build') { steps { sh "make build" } }
                      stage('Test') { steps { sh "make test" } }
                      stage('Scan') { steps { sh "trivy fs --exit-code 1 --severity HIGH,CRITICAL ." } }
                      stage('Deploy') {
                        when { allOf { branch 'main'; expression { cfg.get('deploy', false) } } }
                        steps { deployToK8s(namespace: cfg.namespace, image: "registry.example.com/${cfg.name}:${env.GIT_COMMIT}") }
                      }
                    }
                    post { always { junit allowEmptyResults: true, testResults: '**/reports/*.xml' } }
                  }
                }
            """, runnable=False),
            ex("Consumer Jenkinsfile", "basic", "The service repo pins the library version.", "groovy", """
                @Library('acme-pipeline-lib@v4.2.0') _

                standardPipeline(
                  name: 'checkout-api',
                  namespace: 'shop',
                  deploy: true,
                  timeoutMinutes: 20
                )
            """, runnable=False),
        ],
        ["@Library('lib@v4.2.0') _", "vars/stepName.groovy -> stepName()", "libraryResource 'templates/x.yaml'", "JenkinsPipelineUnit tests", "Folder-level (sandboxed) vs global (trusted)"],
        ["@Library('lib') _ without a version follows the default branch and can break all pipelines at once.", "Trusted global libraries can run arbitrary code on the controller.", "Heavy logic in Groovy CPS can hit serialisation errors; keep complex work in shell or containers."],
        [
            qa("basic", "What is a Jenkins shared library?", "A separate Git repository of Groovy code (custom steps, classes and resources) that Jenkinsfiles load with @Library to reuse common pipeline logic."),
            qa("intermediate", "What goes in vars/, src/ and resources/?", "vars/ contains global variables and custom steps callable from pipelines; src/ contains Groovy classes in a package structure; resources/ contains files like templates read with libraryResource."),
            qa("intermediate", "Why pin library versions?", "Without a version, every pipeline uses the latest default branch, so a bad merge breaks all builds simultaneously. Pinned versions let teams upgrade deliberately and roll back."),
            qa("advanced", "What is the security difference between global and folder libraries?", "Global libraries configured by admins are trusted and run outside the Groovy sandbox with full controller access, so they need strict code review. Folder-level libraries run in the sandbox and are limited to approved methods."),
        ],
        ["jenkins-declarative", "gha-reusable", "pipeline-as-code"],
        chain(
            ("Library", "vars, src", "Author", "The platform team writes custom steps in the library repo."),
            ("Test", "PipelineUnit", "Verify", "Unit tests exercise the steps before a release.", "code"),
            ("Tag", "v4.2.0", "Release", "A version tag is created for consumers to pin.", "pass"),
            ("Load", "@Library", "Consume", "Each Jenkinsfile loads the pinned version and calls the step.", "tag"),
            ("Run", "standard stages", "Execute", "The standard pipeline runs with the service's parameters.", "steps"),
        ),
    ),
    topic(
        "azure-circleci", "Azure DevOps Pipelines & CircleCI Overview", "pipelines", "basic", "AZ",
        "Two other mainstream CI/CD platforms and how their concepts map to GitHub and GitLab.",
        "Different car brands with the same controls in slightly different places. Once you can drive one, you look for where the indicator stalk is and drive off.",
        "Azure DevOps Pipelines uses azure-pipelines.yml with a hierarchy of stages, jobs and steps (script, task or template). Agents come from Microsoft-hosted pools or self-hosted agent pools; deployment jobs target environments that can have approvals and checks (business hours, Azure Monitor alerts, required templates). Service connections hold credentials to Azure, Kubernetes or other clouds, and workload identity federation lets them use OIDC instead of client secrets. Templates (extends and include) enable reuse and can be enforced by required-template checks. CircleCI uses .circleci/config.yml with jobs, workflows that orchestrate jobs, executors (docker, machine, macos) and orbs, which are versioned packages of reusable config. CircleCI features include test splitting by timing, resource classes for sizing, contexts that hold secrets shared across projects with security-group restrictions, and OIDC tokens for cloud auth. Concept mapping helps when switching: workflows (CircleCI) are like GitHub workflows; orbs and Azure templates are like reusable workflows; contexts and variable groups are like environment or org secrets; Azure environments with checks are like GitHub environments with protection rules.",
        ["Organisations standardised on Microsoft tooling and Azure.", "Teams wanting fast Docker-based CI with test splitting.", "Migrating pipelines between platforms using concept mapping."],
        [
            "Azure: stages -> jobs -> steps; tasks and templates for reuse.",
            "Azure service connections can use workload identity federation (OIDC).",
            "CircleCI: workflows orchestrate jobs; orbs package reusable config.",
            "CircleCI contexts scope shared secrets with security groups.",
            "Concepts map closely across platforms; YAML syntax differs.",
        ],
        [
            ex("Azure Pipelines with a deployment job", "intermediate", "Build stage and a deployment to an environment with checks.", "yaml", """
                trigger:
                  branches:
                    include: [main]
                pool:
                  vmImage: ubuntu-latest
                stages:
                  - stage: Build
                    jobs:
                      - job: build
                        steps:
                          - script: make build test
                          - publish: dist
                            artifact: app
                  - stage: Production
                    dependsOn: Build
                    jobs:
                      - deployment: deploy
                        environment: production
                        strategy:
                          runOnce:
                            deploy:
                              steps:
                                - download: current
                                  artifact: app
                                - task: AzureCLI@2
                                  inputs:
                                    azureSubscription: prod-federated-connection
                                    scriptType: bash
                                    scriptLocation: inlineScript
                                    inlineScript: ./deploy.sh production
            """, runnable=False),
            ex("CircleCI with an orb, test splitting and a context", "intermediate", "Parallel tests split by timing; deploy uses a restricted context.", "yaml", """
                version: 2.1
                orbs:
                  node: circleci/node@6.1.0
                jobs:
                  test:
                    docker:
                      - image: cimg/node:22.11
                    parallelism: 4
                    steps:
                      - checkout
                      - node/install-packages
                      - run: |
                          TESTS=$(circleci tests glob "test/**/*.spec.js" | circleci tests split --split-by=timings)
                          npx jest $TESTS --ci --reporters=default --reporters=jest-junit
                      - store_test_results:
                          path: reports
                  deploy:
                    docker:
                      - image: cimg/base:current
                    steps:
                      - checkout
                      - run: ./deploy.sh production
                workflows:
                  main:
                    jobs:
                      - test
                      - deploy:
                          requires: [test]
                          context: prod-deploy
                          filters:
                            branches:
                              only: main
            """, runnable=False),
        ],
        ["az pipelines run --name app-ci", "az pipelines runs list", "circleci config validate", "circleci tests split --split-by=timings", "orbs: name: ns/orb@x.y.z"],
        ["Azure classic (UI) release pipelines are harder to review than YAML; migrate to YAML.", "Unrestricted CircleCI contexts expose production secrets to any project's jobs.", "Orbs from unknown publishers run arbitrary code; pin versions and prefer certified orbs."],
        [
            qa("basic", "What is the structure of an Azure Pipelines YAML?", "Stages contain jobs, jobs contain steps, and steps are scripts or tasks. Deployment jobs target environments that can have approvals and checks."),
            qa("intermediate", "What are CircleCI orbs?", "Versioned, shareable packages of CircleCI configuration (jobs, commands, executors) that projects import to avoid duplicating setup like language installs or cloud deploys."),
            qa("intermediate", "How do Azure service connections avoid long-lived secrets?", "They can use workload identity federation, where Azure DevOps presents an OIDC token that Microsoft Entra ID trusts, instead of storing a client secret."),
            qa("advanced", "How would you migrate from CircleCI to GitHub Actions?", "Map workflows to workflows, jobs to jobs, orbs to actions or reusable workflows, contexts to environments or org secrets and parallelism to matrices or sharding. Keep build logic in scripts so only orchestration changes, run both systems in parallel briefly and compare results and timings."),
        ],
        ["gha-workflows", "gitlab-ci", "test-sharding"],
        chain(
            ("Trigger", "push / PR", "Start", "A commit triggers the platform's pipeline definition."),
            ("Stages", "build, deploy", "Structure", "Stages or workflows order jobs and their dependencies.", "event"),
            ("Agents", "pools, executors", "Run jobs", "Hosted or self-hosted agents run each job.", "jobs"),
            ("Checks", "env approvals", "Gate", "Environment checks or restricted contexts guard production.", "build"),
            ("Deploy", "federated auth", "Release", "Deployment uses OIDC-based service connections where possible.", "approved"),
        ),
    ),
    topic(
        "artifacts-registries", "Artifacts & Registries", "artifacts-release", "basic", "AR",
        "Store build outputs once, immutably, with digests and retention, then promote them.",
        "A sealed, labelled crate in a warehouse. Every shop that needs the product gets that exact crate by its barcode, not a fresh copy assembled again by someone else.",
        "An artifact is anything a build produces that later stages consume: container images, JARs, wheels, npm packages, Helm charts, binaries, test reports and SBOMs. CI systems have short-lived workflow artifacts for passing files between jobs, but releasable artifacts belong in a registry or repository manager: OCI registries (GHCR, ECR, Artifact Registry, ACR, Harbor), language repositories (Maven/Nexus/Artifactory, PyPI, npm) and generic stores (S3 with versioning). Artifacts should be immutable: a version or tag, once published, never changes, and consumers reference container images by SHA-256 digest (image@sha256:...) so they get exactly what was tested. Registries enforce this with tag immutability settings. Build-once-deploy-many means the same artifact is promoted from dev to staging to production by changing tags, copying between repositories or updating GitOps manifests, never by rebuilding. Retention and cleanup policies keep storage costs in check without deleting anything still deployed. Access control should allow CI to push only to its own repositories, and deployment systems to pull only, with signatures and attestations stored alongside the artifact.",
        ["Publishing images to ECR with immutable tags.", "Passing build outputs between jobs with workflow artifacts.", "Promoting a Helm chart from a staging repo to a production repo."],
        [
            "Workflow artifacts are temporary; registries are the system of record.",
            "Reference images by digest for exactly-what-was-tested deploys.",
            "Enable tag immutability for release tags.",
            "Retention policies must not delete artifacts that are still running.",
            "Store signatures, SBOMs and provenance next to the artifact.",
        ],
        [
            ex("Immutable ECR repository and lifecycle policy", "intermediate", "Terraform: immutable tags, scan on push, expire untagged images.", "hcl", """
                resource "aws_ecr_repository" "api" {
                  name                 = "shop/api"
                  image_tag_mutability = "IMMUTABLE"
                  image_scanning_configuration {
                    scan_on_push = true
                  }
                  encryption_configuration {
                    encryption_type = "KMS"
                  }
                }

                resource "aws_ecr_lifecycle_policy" "api" {
                  repository = aws_ecr_repository.api.name
                  policy = jsonencode({
                    rules = [{
                      rulePriority = 1
                      description  = "expire untagged after 14 days"
                      selection = {
                        tagStatus   = "untagged"
                        countType   = "sinceImagePushed"
                        countUnit   = "days"
                        countNumber = 14
                      }
                      action = { type = "expire" }
                    }]
                  })
                }
            """, runnable=False),
            ex("Resolve and deploy by digest", "basic", "Find the digest of a tag and deploy that exact image.", "bash", """
                DIGEST=$(crane digest ghcr.io/acme/api:1.8.2)
                echo "ghcr.io/acme/api@${DIGEST}"
                kubectl set image deploy/api api="ghcr.io/acme/api@${DIGEST}"
                crane copy ghcr.io/acme/api@${DIGEST} 123456789012.dkr.ecr.eu-west-1.amazonaws.com/shop/api:1.8.2
            """, runnable=False),
        ],
        ["crane digest img:tag", "docker buildx imagetools inspect img", "image@sha256:<digest>", "actions/upload-artifact · download-artifact", "oras push reg/repo:tag file"],
        ["Mutable tags like latest or main make it impossible to know what is running.", "Workflow artifacts expire (default 90 days on GitHub); do not treat them as releases.", "Aggressive cleanup policies can delete an image a cluster still needs to pull during a reschedule."],
        [
            qa("basic", "What is an artifact in CI/CD?", "Any output of the build that later stages or users consume, such as a container image, package, binary or report. Release artifacts are stored in a registry with a version."),
            qa("intermediate", "Why deploy by digest instead of tag?", "Tags can be moved to point at other content; a SHA-256 digest identifies exact bytes. Deploying by digest guarantees production runs exactly the image that was tested and signed."),
            qa("intermediate", "Workflow artifacts vs registry artifacts?", "Workflow artifacts are temporary files for passing data between jobs or debugging and expire. Registry artifacts are durable, versioned, access-controlled releases that deployments pull."),
            qa("advanced", "How do you design artifact promotion?", "Build once, publish to a registry with an immutable version and digest, sign and attach SBOM and provenance. Promote by copying the same digest to a production repository or updating a GitOps manifest after gates pass, never by rebuilding."),
        ],
        ["env-promotion", "container-builds", "signing-cosign", "semver-release"],
        chain(
            ("Build", "one artifact", "Produce", "The pipeline builds the artifact once per commit."),
            ("Push", "registry", "Publish", "The artifact is pushed with an immutable version tag.", "image"),
            ("Digest", "sha256", "Pin identity", "The SHA-256 digest is recorded as the true identity.", "tag"),
            ("Attach", "sig, SBOM", "Evidence", "Signatures, SBOM and provenance are stored alongside.", "digest"),
            ("Promote", "same digest", "Deploy", "Environments deploy the same digest after each gate.", "verified"),
        ),
    ),
]

_BATCH_4 = [
    topic(
        "semver-release", "Semantic Versioning & Release Automation", "artifacts-release", "intermediate", "SV",
        "MAJOR.MINOR.PATCH computed from commit history, tagged and published by the pipeline.",
        "House numbering with a promise: a new street name (major) means you must update your address book, a new house on the street (minor) is extra choice, and a repainted door (patch) changes nothing for visitors.",
        "Semantic Versioning (SemVer 2.0.0) encodes compatibility in MAJOR.MINOR.PATCH: increment MAJOR for breaking changes, MINOR for backwards-compatible features and PATCH for backwards-compatible fixes, with optional pre-release (1.4.0-rc.1) and build metadata (+sha.abc123). Version 0.y.z signals an unstable API where anything may change. Release automation removes humans from deciding and typing versions: tools such as semantic-release, release-please, changesets, GitVersion or cargo-release inspect commits since the last tag (often using Conventional Commits like feat:, fix:, feat!:) and compute the next version, update manifests, create a git tag and a release, and publish packages. release-please opens a 'release PR' that accumulates changes and bumps versions when merged, giving a human checkpoint without manual edits. Applications deployed continuously sometimes use CalVer (2026.10.3) or build numbers instead, since compatibility promises matter most for libraries and APIs. Tags should be protected and created only by the release workflow, and published artifacts should be immutable.",
        ["Publishing a library to npm or PyPI with correct versions automatically.", "Generating release PRs for a monorepo with per-package versions.", "Tagging container images with both SemVer and commit SHA."],
        [
            "Breaking -> MAJOR, feature -> MINOR, fix -> PATCH.",
            "Conventional Commits let tools compute the next version.",
            "release-please uses a release PR; semantic-release releases on merge.",
            "Tags are protected and created only by automation.",
            "Pre-releases (-rc.1) let consumers opt in to testing.",
        ],
        [
            ex("release-please workflow", "intermediate", "Maintains a release PR; on merge creates the tag and GitHub release.", "yaml", """
                name: release-please
                on:
                  push:
                    branches: [main]
                permissions:
                  contents: write
                  pull-requests: write
                jobs:
                  release:
                    runs-on: ubuntu-latest
                    outputs:
                      created: ${{ steps.rp.outputs.release_created }}
                      tag: ${{ steps.rp.outputs.tag_name }}
                    steps:
                      - id: rp
                        uses: googleapis/release-please-action@v4
                        with:
                          release-type: node
                  publish:
                    needs: release
                    if: needs.release.outputs.created == 'true'
                    runs-on: ubuntu-latest
                    permissions:
                      contents: read
                      id-token: write
                    steps:
                      - uses: actions/checkout@v4
                        with:
                          ref: ${{ needs.release.outputs.tag }}
                      - uses: actions/setup-node@v4
                        with:
                          node-version: 22
                          registry-url: https://registry.npmjs.org
                      - run: npm ci && npm publish --provenance --access public
                        env:
                          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
            """, runnable=False),
            ex("Compute versions from commits", "basic", "How commit types map to bumps.", "bash", """
                git describe --tags --abbrev=0            # last release, e.g. v1.4.2
                git log v1.4.2..HEAD --oneline
                # fix(api): handle null       -> 1.4.3
                # feat(api): add filter       -> 1.5.0
                # feat(api)!: drop v1 routes  -> 2.0.0
                npx semantic-release --dry-run
            """, runnable=False),
        ],
        ["git describe --tags --abbrev=0", "npx semantic-release --dry-run", "release-please-action@v4", "npx changeset version", "gh release create v1.5.0 --generate-notes"],
        ["Squash-merging with a non-conventional PR title loses the version signal.", "Letting humans push tags bypasses the release pipeline and its checks.", "Deleting and re-creating a tag with different content breaks consumers' caches and trust."],
        [
            qa("basic", "Explain semantic versioning.", "A version MAJOR.MINOR.PATCH where MAJOR increases for incompatible API changes, MINOR for backwards-compatible features and PATCH for backwards-compatible bug fixes."),
            qa("intermediate", "How can a pipeline decide the next version automatically?", "By parsing commit messages since the last tag using Conventional Commits: fix gives a patch, feat a minor and a ! or BREAKING CHANGE footer a major. Tools like semantic-release and release-please do this and create tags and releases."),
            qa("intermediate", "release-please vs semantic-release?", "release-please keeps an open release PR that shows the upcoming version and changelog and releases when it is merged. semantic-release releases directly on each qualifying push to the release branch."),
            qa("advanced", "Should a continuously deployed web app use SemVer?", "Often not strictly; there is no external API consumer to protect, so CalVer or build numbers plus the commit SHA are simpler. SemVer remains valuable for libraries, SDKs and public APIs where compatibility promises matter."),
        ],
        ["changelogs", "artifacts-registries", "trunk-based-dev"],
        chain(
            ("Commits", "feat, fix, !", "History", "Conventional commits accumulate on main since the last tag."),
            ("Compute", "next version", "Decide bump", "The release tool maps commit types to a major, minor or patch bump.", "log"),
            ("Release PR", "version + notes", "Review", "A release PR shows the new version and changelog for approval.", "1.5.0"),
            ("Tag", "v1.5.0", "Tag", "Merging creates a protected tag and a release.", "merge"),
            ("Publish", "registry", "Distribute", "The tagged build publishes packages and images.", "tag"),
        ),
    ),
    topic(
        "changelogs", "Changelogs & Conventional Commits", "artifacts-release", "basic", "CL",
        "Human-readable release notes generated from structured commit and PR history.",
        "A ship's log: every notable event is written down with a category and time, so anyone boarding later can see what changed on the voyage without interviewing the crew.",
        "A changelog tells users and operators what changed between versions: new features, fixes, deprecations, breaking changes and security fixes. Keep a Changelog proposes a CHANGELOG.md with an Unreleased section and versioned sections grouped by Added, Changed, Deprecated, Removed, Fixed and Security. Writing it by hand is error-prone, so most teams generate it from structured history. Conventional Commits defines a commit format, type(scope): description, with types like feat, fix, docs, refactor, perf, chore and a ! or BREAKING CHANGE footer for breaking changes; commitlint enforces it in CI or a git hook, and with squash merges the PR title becomes the commit, so linting PR titles is enough. Generators (release-please, semantic-release, git-cliff, conventional-changelog, changesets) group commits by type and link PRs and issues. GitHub's generated release notes use PR labels and a .github/release.yml config. A changelog entry should describe impact for the reader ('Checkout no longer double-charges on retry'), not implementation detail, and breaking changes should include migration steps.",
        ["Auto-generating release notes for each tag.", "Telling on-call engineers what went out in today's deploy.", "Enforcing commit format so versioning and notes are automatic."],
        [
            "Format: type(scope)!: description, plus optional body and footers.",
            "Lint PR titles when using squash merges.",
            "Group notes by Added, Changed, Fixed, Security, Breaking.",
            "Write for the reader's impact; include migration steps for breaks.",
        ],
        [
            ex("Lint PR titles", "basic", "Fail PRs whose titles are not Conventional Commits.", "yaml", """
                name: pr-title
                on:
                  pull_request:
                    types: [opened, edited, synchronize]
                permissions:
                  pull-requests: read
                jobs:
                  lint:
                    runs-on: ubuntu-latest
                    steps:
                      - uses: amannn/action-semantic-pull-request@v5
                        env:
                          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
                        with:
                          types: |
                            feat
                            fix
                            perf
                            refactor
                            docs
                            chore
                          requireScope: false
            """, runnable=False),
            ex("Generated release notes config", "intermediate", ".github/release.yml groups PRs by label.", "yaml", """
                changelog:
                  exclude:
                    labels: [skip-changelog]
                  categories:
                    - title: Breaking changes
                      labels: [breaking]
                    - title: Features
                      labels: [feature]
                    - title: Bug fixes
                      labels: [bug]
                    - title: Security
                      labels: [security]
                    - title: Other
                      labels: ["*"]
            """, runnable=False),
            ex("git-cliff locally", "basic", "Generate the unreleased section from commits.", "bash", """
                git cliff --unreleased --tag v1.5.0 --prepend CHANGELOG.md
                npx commitlint --from origin/main --to HEAD
                gh release create v1.5.0 --generate-notes
            """, runnable=False),
        ],
        ["feat(api): add search filter", "fix!: drop legacy token format", "npx commitlint --from origin/main", "git cliff --unreleased", "gh release create vX --generate-notes"],
        ["Commit messages like 'wip' or 'fix stuff' produce useless notes.", "Breaking changes without a migration section cause painful upgrades.", "Generated notes still need a human skim for clarity on major releases."],
        [
            qa("basic", "What is Conventional Commits?", "A commit message convention, type(scope): description, with types like feat and fix and a ! or BREAKING CHANGE footer for breaking changes, which tools use to generate changelogs and versions."),
            qa("intermediate", "How do you enforce commit conventions with squash merges?", "Lint the PR title, since it becomes the squash commit message, with a PR-title check action or commitlint in CI."),
            qa("intermediate", "What should a good changelog entry contain?", "The user-visible impact in plain language, a link to the PR or issue, and for breaking changes clear migration steps and the version where the old behaviour was deprecated."),
            qa("advanced", "How do changelogs help incident response?", "They give on-call engineers a quick list of what changed in a deploy, with links to PRs and owners, which speeds up correlating an incident with a change and deciding what to roll back or flag off."),
        ],
        ["semver-release", "incident-postmortem", "branching-pr-checks"],
        chain(
            ("PR title", "type(scope):", "Structure", "Each PR title follows Conventional Commits and is linted."),
            ("Squash", "one commit", "History", "Squash merge makes the title the commit message on main.", "title"),
            ("Group", "feat, fix, !", "Categorise", "The generator groups commits since the last tag by type.", "commits"),
            ("Notes", "CHANGELOG.md", "Write notes", "A release section with links is prepended to the changelog.", "groups"),
        ),
    ),
    topic(
        "iac-in-ci", "Infrastructure as Code in CI (Terraform plan/apply)", "artifacts-release", "advanced", "IC",
        "Plan on pull request, review the diff, apply exactly that plan after merge.",
        "An architect's change drawing: before anyone knocks down a wall, the drawing shows exactly what will change, gets signed off, and the builders work from that signed drawing, not from a new one made on the day.",
        "Treating infrastructure like application code means changes to Terraform, OpenTofu, Pulumi or CloudFormation go through pull requests and pipelines rather than laptops. The standard Terraform flow: on a PR, run fmt -check, validate, tflint and security scanners (Checkov, Trivy config, tfsec) and terraform plan, then post the plan summary as a PR comment for review. After merge (or on approval), apply the saved plan file so what is applied is exactly what was reviewed; if state changed in between, the saved plan is rejected as stale and must be regenerated. Remote state with locking (S3 with native lockfile or DynamoDB, GCS, Terraform Cloud) prevents concurrent applies, and pipelines should serialise per state with a concurrency group. Credentials come from OIDC federation: a read-only plan role for PRs and a separate apply role limited to the protected branch and environment. Drift detection runs plan on a schedule and alerts when the real world no longer matches code. Tools like Atlantis, Terraform Cloud, Spacelift or env0 package this workflow.",
        ["Reviewing infrastructure changes with a plan comment on every PR.", "Applying production changes only from main with approval.", "Nightly drift detection on all workspaces."],
        [
            "PR: fmt, validate, lint, scan, plan; post plan to PR.",
            "Apply the saved plan file, not a fresh plan.",
            "Remote state with locking; one apply per state at a time.",
            "Separate read-only plan role and privileged apply role via OIDC.",
            "Scheduled plan with -detailed-exitcode detects drift.",
        ],
        [
            ex("Terraform plan on PR, apply on main", "advanced", "OIDC roles, saved plan artifact and serialised apply.", "yaml", """
                name: terraform
                on:
                  pull_request:
                    paths: ["infra/**"]
                  push:
                    branches: [main]
                    paths: ["infra/**"]
                permissions:
                  contents: read
                  id-token: write
                  pull-requests: write
                concurrency:
                  group: terraform-prod
                  cancel-in-progress: false
                defaults:
                  run:
                    working-directory: infra
                jobs:
                  plan:
                    runs-on: ubuntu-latest
                    steps:
                      - uses: actions/checkout@v4
                      - uses: hashicorp/setup-terraform@v3
                        with:
                          terraform_version: 1.9.8
                      - uses: aws-actions/configure-aws-credentials@v4
                        with:
                          role-to-assume: arn:aws:iam::123456789012:role/tf-plan-readonly
                          aws-region: eu-west-1
                      - run: terraform fmt -check -recursive
                      - run: terraform init -input=false
                      - run: terraform validate
                      - run: terraform plan -input=false -out=tfplan
                      - uses: actions/upload-artifact@v4
                        with:
                          name: tfplan
                          path: infra/tfplan
                  apply:
                    if: github.event_name == 'push'
                    needs: plan
                    runs-on: ubuntu-latest
                    environment: production
                    steps:
                      - uses: actions/checkout@v4
                      - uses: hashicorp/setup-terraform@v3
                        with:
                          terraform_version: 1.9.8
                      - uses: aws-actions/configure-aws-credentials@v4
                        with:
                          role-to-assume: arn:aws:iam::123456789012:role/tf-apply-prod
                          aws-region: eu-west-1
                      - uses: actions/download-artifact@v4
                        with:
                          name: tfplan
                          path: infra
                      - run: terraform init -input=false
                      - run: terraform apply -input=false tfplan
            """, runnable=False),
            ex("Remote state with locking", "intermediate", "S3 backend with native lockfile and encryption.", "hcl", """
                terraform {
                  required_version = ">= 1.9"
                  backend "s3" {
                    bucket       = "acme-tfstate-prod"
                    key          = "network/terraform.tfstate"
                    region       = "eu-west-1"
                    encrypt      = true
                    use_lockfile = true
                  }
                  required_providers {
                    aws = {
                      source  = "hashicorp/aws"
                      version = "~> 5.70"
                    }
                  }
                }
            """, runnable=False),
            ex("Drift detection", "intermediate", "Exit code 2 means changes are pending, i.e. drift.", "bash", """
                terraform plan -input=false -detailed-exitcode -lock=false
                case $? in
                  0) echo "no drift" ;;
                  2) echo "drift detected"; exit 1 ;;
                  *) echo "plan failed"; exit 1 ;;
                esac
            """, runnable=False),
        ],
        ["terraform fmt -check -recursive", "terraform plan -out=tfplan", "terraform apply tfplan", "terraform plan -detailed-exitcode", "checkov -d infra/ · tflint"],
        ["Applying a fresh plan after approval can apply changes nobody reviewed.", "Plan files contain sensitive values; restrict artifact access and retention.", "Running plan for PRs from forks with an apply-capable role is a privilege escalation.", "Two pipelines applying the same state without locking corrupt it."],
        [
            qa("basic", "What does terraform plan do in a CI pipeline?", "It computes the difference between the code and real infrastructure and shows what will be created, changed or destroyed, so reviewers can approve the change before it is applied."),
            qa("intermediate", "Why apply a saved plan file?", "It guarantees the apply executes exactly the reviewed changes. If state changed since the plan, Terraform rejects the stale plan instead of silently applying something different."),
            qa("intermediate", "How should cloud credentials work for Terraform pipelines?", "Use OIDC federation with two roles: a read-only role for plans on PRs and a privileged apply role that only trusts the protected branch and production environment. No static access keys are stored."),
            qa("advanced", "How do you detect and handle drift?", "Run terraform plan -detailed-exitcode on a schedule; exit code 2 indicates differences. Alert the owner, investigate whether the manual change should be codified or reverted, and restrict console write access to reduce future drift."),
        ],
        ["gitops", "oidc-federation", "approvals-gates"],
        chain(
            ("PR", "infra/** change", "Propose", "An engineer edits Terraform and opens a pull request."),
            ("Checks", "fmt, lint, scan", "Static", "Formatting, validation, tflint and policy scanners run.", "diff"),
            ("Plan", "read-only role", "Plan", "terraform plan runs with a read-only OIDC role and is posted to the PR.", "ok"),
            ("Approve", "review + env", "Gate", "Reviewers approve the plan; merge triggers apply behind an environment.", "plan"),
            ("Apply", "saved tfplan", "Apply", "The apply role applies the saved plan under a state lock.", "approved"),
        ),
    ),
    topic(
        "gitops", "GitOps with Argo CD & Flux", "artifacts-release", "intermediate", "GO",
        "Git holds desired state; an in-cluster agent pulls and reconciles it continuously.",
        "A thermostat. You set the temperature you want on the dial (Git), and the heating system keeps checking the room and correcting it. Nobody walks in and fiddles with the radiators directly.",
        "GitOps applies Git-based workflows to deployment: the desired state of a system (Kubernetes manifests, Helm values, Kustomize overlays) lives in a Git repository, and an agent running in the cluster, such as Argo CD or Flux, continuously compares live state to Git and reconciles differences. This is a pull model: CI builds and publishes an image, then updates the image tag or digest in the config repo (directly or through a PR), and the agent applies it. The cluster does not need to expose credentials to CI, and every change is an auditable, revertible commit; rollback is git revert. Drift from manual kubectl edits is detected and optionally self-healed. Argo CD models deployments as Applications (and ApplicationSets for many clusters or environments) with sync policies, sync waves and health checks, and a UI. Flux uses controllers (source, kustomize, helm, image automation) configured through CRDs such as GitRepository, Kustomization and HelmRelease. Secrets need special handling (Sealed Secrets, SOPS, External Secrets Operator) because plain secrets must not be committed. Separating application code repos from environment config repos keeps promotion and access control clear.",
        ["Deploying to many Kubernetes clusters from one config repo.", "Auditable production changes where every deploy is a commit.", "Self-healing drift caused by manual hotfixes."],
        [
            "Desired state in Git; agent pulls and reconciles.",
            "CI's job ends at publishing an image and updating config.",
            "Rollback = git revert of the config change.",
            "selfHeal and prune keep live state matching Git.",
            "Use Sealed Secrets, SOPS or External Secrets; never plain secrets in Git.",
        ],
        [
            ex("Argo CD Application with automated sync", "intermediate", "Points at an overlay; prunes deleted resources and self-heals drift.", "yaml", """
                apiVersion: argoproj.io/v1alpha1
                kind: Application
                metadata:
                  name: checkout-prod
                  namespace: argocd
                spec:
                  project: shop
                  source:
                    repoURL: https://github.com/acme/shop-config.git
                    targetRevision: main
                    path: apps/checkout/overlays/prod
                  destination:
                    server: https://kubernetes.default.svc
                    namespace: checkout
                  syncPolicy:
                    automated:
                      prune: true
                      selfHeal: true
                    syncOptions:
                      - CreateNamespace=true
                    retry:
                      limit: 3
                      backoff:
                        duration: 10s
                        factor: 2
            """, runnable=False),
            ex("CI updates the config repo by digest", "intermediate", "Open a PR in the config repo bumping the image digest.", "bash", """
                DIGEST=$(crane digest ghcr.io/acme/checkout:${GITHUB_SHA})
                git clone https://github.com/acme/shop-config.git && cd shop-config
                git switch -c bump/checkout-${GITHUB_SHA::7}
                (cd apps/checkout/overlays/staging && kustomize edit set image checkout=ghcr.io/acme/checkout@${DIGEST})
                git commit -am "chore(checkout): staging -> ${GITHUB_SHA::7}"
                git push -u origin HEAD && gh pr create --fill
            """, runnable=False),
            ex("Flux Kustomization", "advanced", "Reconcile every 5 minutes with health checks and SOPS decryption.", "yaml", """
                apiVersion: kustomize.toolkit.fluxcd.io/v1
                kind: Kustomization
                metadata:
                  name: checkout
                  namespace: flux-system
                spec:
                  interval: 5m
                  path: ./apps/checkout/overlays/prod
                  prune: true
                  sourceRef:
                    kind: GitRepository
                    name: shop-config
                  decryption:
                    provider: sops
                    secretRef:
                      name: sops-age
                  healthChecks:
                    - apiVersion: apps/v1
                      kind: Deployment
                      name: checkout
                      namespace: checkout
            """, runnable=False),
        ],
        ["argocd app sync checkout-prod", "argocd app diff checkout-prod", "argocd app history · rollback", "flux reconcile kustomization checkout --with-source", "flux get kustomizations"],
        ["selfHeal reverts manual hotfixes; emergency changes must go through Git too.", "Using image tags like latest in Git defeats auditability; pin digests.", "CI with cluster-admin kubeconfig alongside GitOps reintroduces the push model's risks."],
        [
            qa("basic", "What is GitOps?", "An operating model where Git is the single source of truth for desired system state and an automated agent continuously reconciles the live environment to match it."),
            qa("intermediate", "Push-based CD vs GitOps pull-based?", "In push CD the pipeline holds cluster credentials and runs kubectl or helm. In GitOps an in-cluster agent pulls from Git, so CI never needs cluster credentials, drift is detected and every change is a commit."),
            qa("intermediate", "How do you roll back with GitOps?", "Revert the commit in the config repository; the agent reconciles the cluster back to the previous state. Argo CD can also roll back to a previous sync, but Git should be updated to match."),
            qa("advanced", "How do you manage secrets in GitOps?", "Never commit plain secrets. Commit encrypted secrets with Sealed Secrets or SOPS, or commit references with External Secrets Operator that pulls values from a cloud secret manager at runtime."),
            qa("advanced", "How do you promote between environments with GitOps?", "Keep per-environment overlays or folders. A promotion is a PR that changes the image digest in the next environment's overlay, gated by review and automated checks; tools like Kargo or Argo CD Image Updater can automate the PRs."),
        ],
        ["env-promotion", "iac-in-ci", "rollback-rollforward", "progressive-delivery"],
        chain(
            ("CI", "build + push", "Publish image", "CI builds, scans and pushes an image, getting its digest."),
            ("Config PR", "bump digest", "Change desired", "CI opens a PR to the config repo with the new digest.", "digest"),
            ("Merge", "reviewed", "Approve", "The PR is reviewed and merged; Git now holds the new desired state.", "PR"),
            ("Reconcile", "Argo CD / Flux", "Pull and apply", "The in-cluster agent detects the change and syncs it.", "commit"),
            ("Healthy", "health checks", "Verify", "The agent reports health; drift is corrected continuously.", "sync"),
        ),
    ),
    topic(
        "env-promotion", "Environment Promotion (dev, stage, prod)", "artifacts-release", "intermediate", "EP",
        "Build once, then move the same artifact forward through environments as gates pass.",
        "A theatre play moving from rehearsal to preview night to opening night with the same cast and script. You do not recast the lead for opening night and hope it goes well.",
        "Environment promotion is the path an artifact takes from first deploy to production: commonly dev or preview, then staging (production-like), then production, sometimes with a canary ring or several regions. The core rule is build once, deploy many: the artifact built and tested at the start is the one that reaches production, identified by digest, with only configuration differing between environments. Configuration comes from per-environment values (Helm values files, Kustomize overlays, parameter stores) and secrets from per-environment secret stores, never baked into the artifact. Each promotion is gated by evidence: tests passed in the previous environment, scans clean, approvals or change tickets where required, and health metrics stable for a soak period. Environments should be as similar as practical, especially staging to production (same IaC modules, same versions, smaller scale). Ephemeral preview environments per pull request give fast feedback without contention for a shared dev. Promotion can be pipeline-driven (sequential jobs with environment gates) or GitOps-driven (PRs that bump the digest in each environment's overlay).",
        ["Moving a release from staging to production with the same image digest.", "Spinning up a preview environment per pull request.", "Rolling out to regions in waves after each soak period."],
        [
            "Build once; promote the same digest.",
            "Config and secrets are per environment and external to the artifact.",
            "Each gate requires evidence from the previous environment.",
            "Staging must be production-like in topology and versions.",
            "Preview environments per PR reduce shared-environment contention.",
        ],
        [
            ex("Kustomize overlays per environment", "basic", "Base manifests with environment-specific patches and image digests.", "bash", """
                # apps/checkout/
                #   base/            deployment.yaml service.yaml kustomization.yaml
                #   overlays/dev/    kustomization.yaml (replicas 1, image digest A)
                #   overlays/staging kustomization.yaml (replicas 2, image digest A)
                #   overlays/prod/   kustomization.yaml (replicas 6, image digest previous)
                kustomize build apps/checkout/overlays/prod | kubectl diff -f -
                # promote: copy the staging digest into prod
                DIGEST=$(yq '.images[0].digest' apps/checkout/overlays/staging/kustomization.yaml)
                yq -i ".images[0].digest = \\"$DIGEST\\"" apps/checkout/overlays/prod/kustomization.yaml
            """, runnable=False),
            ex("Sequential promotion with soak", "intermediate", "Staging deploy, smoke tests and a soak check before production.", "yaml", """
                jobs:
                  staging:
                    runs-on: ubuntu-latest
                    environment: staging
                    permissions:
                      contents: read
                      id-token: write
                    steps:
                      - uses: actions/checkout@v4
                      - run: ./deploy.sh staging "${{ needs.build.outputs.digest }}"
                      - run: ./smoke.sh https://staging.example.com
                      - run: ./check-slo.sh --env staging --window 30m --max-error-rate 0.5
                  production:
                    needs: staging
                    runs-on: ubuntu-latest
                    environment: production
                    permissions:
                      contents: read
                      id-token: write
                    steps:
                      - uses: actions/checkout@v4
                      - run: ./deploy.sh production "${{ needs.build.outputs.digest }}"
            """, runnable=False),
        ],
        ["kustomize build overlays/prod", "helm upgrade -f values-prod.yaml", "Promote digest, not rebuild", "Preview env per PR", "Soak: watch SLOs before next ring"],
        ["Rebuilding per environment produces untested binaries.", "Environment-specific code paths (if env == 'prod') make staging prove nothing.", "A staging environment that drifts from production (different DB version) hides bugs."],
        [
            qa("basic", "What does build once, deploy many mean?", "The artifact is built a single time, then the same artifact (same digest) is deployed to each environment, with only external configuration changing."),
            qa("intermediate", "How do you handle configuration differences between environments?", "Keep config outside the artifact: environment variables, Helm values or Kustomize overlays, and secret managers per environment. The code reads config at runtime."),
            qa("intermediate", "What gates should exist between staging and production?", "Automated tests and smoke checks passing in staging, security scans clean, a soak period with healthy SLO metrics, and an approval or change record if required by policy."),
            qa("advanced", "How do preview environments fit into promotion?", "Each PR gets a short-lived environment built from its artifact, used for review and E2E tests, and destroyed on merge. They catch issues before staging and avoid teams blocking each other on a single shared dev environment."),
        ],
        ["artifacts-registries", "gitops", "approvals-gates", "gha-environments"],
        chain(
            ("Build", "digest A", "Build once", "CI builds and publishes one artifact, digest A."),
            ("Dev", "preview/dev", "First deploy", "Digest A deploys to dev or a PR preview environment.", "A"),
            ("Staging", "prod-like", "Validate", "Digest A deploys to staging; smoke and E2E tests run.", "A"),
            ("Soak", "SLO check", "Evidence", "Metrics are watched for a soak window before promotion.", "healthy"),
            ("Prod", "same digest", "Release", "Digest A, unchanged, is promoted to production.", "A"),
        ),
    ),
    topic(
        "rolling-deploy", "Rolling Deployments", "deployment", "basic", "RD",
        "Replace instances a few at a time while the service keeps serving.",
        "Replacing the tyres of a bus one at a time while it stays parked at the stop and still takes passengers. It never has zero wheels, but for a while it rides on a mix of old and new.",
        "A rolling deployment gradually replaces old instances with new ones in batches, so capacity stays available and there is no separate environment to pay for. Kubernetes Deployments do this by default with the RollingUpdate strategy: maxSurge controls how many extra pods may be created above the desired count and maxUnavailable how many may be down at once. Readiness probes are essential: a new pod only receives traffic once ready, and the rollout pauses if new pods never become ready; minReadySeconds and progressDeadlineSeconds tune how long to wait. Cloud equivalents include ECS rolling updates with deployment circuit breakers, Auto Scaling Group instance refresh and VM scale set rolling upgrades. During the rollout old and new versions serve traffic simultaneously, so the change must be backwards compatible with the database schema, message formats and APIs. Rollback means rolling back to the previous ReplicaSet or task definition, which also takes time proportional to fleet size. Rolling updates are a good default, but they give limited control over blast radius compared with canary releases.",
        ["Default deployments for stateless Kubernetes services.", "ECS service updates with automatic rollback on failure.", "Updating a VM fleet without a maintenance window."],
        [
            "maxSurge = extra pods allowed; maxUnavailable = pods allowed down.",
            "Readiness probes gate traffic to new pods.",
            "Old and new versions run together: stay backwards compatible.",
            "progressDeadlineSeconds marks a stuck rollout as failed.",
            "kubectl rollout undo returns to the previous ReplicaSet.",
        ],
        [
            ex("Zero-downtime rolling update", "basic", "Never drop below desired capacity; gate on readiness.", "yaml", """
                apiVersion: apps/v1
                kind: Deployment
                metadata:
                  name: api
                spec:
                  replicas: 6
                  minReadySeconds: 10
                  progressDeadlineSeconds: 300
                  strategy:
                    type: RollingUpdate
                    rollingUpdate:
                      maxSurge: 2
                      maxUnavailable: 0
                  selector:
                    matchLabels: {app: api}
                  template:
                    metadata:
                      labels: {app: api}
                    spec:
                      containers:
                        - name: api
                          image: ghcr.io/acme/api@sha256:EXAMPLE-DIGEST
                          readinessProbe:
                            httpGet: {path: /ready, port: 8080}
                            periodSeconds: 5
                            failureThreshold: 3
                          lifecycle:
                            preStop:
                              exec: {command: ["sleep", "10"]}
            """, runnable=False),
            ex("Watch and undo a rollout", "basic", "CI waits for success and rolls back on failure.", "bash", """
                kubectl set image deploy/api api=ghcr.io/acme/api@${DIGEST}
                if ! kubectl rollout status deploy/api --timeout=5m; then
                  kubectl rollout undo deploy/api
                  exit 1
                fi
                kubectl rollout history deploy/api
            """, runnable=False),
        ],
        ["kubectl rollout status deploy/x --timeout=5m", "kubectl rollout undo deploy/x", "kubectl rollout history deploy/x", "maxSurge / maxUnavailable", "aws ecs update-service --force-new-deployment"],
        ["No readiness probe means pods receive traffic before they can serve.", "maxUnavailable > 0 with small replica counts can cut capacity sharply.", "Without preStop delay, in-flight requests are dropped when old pods terminate."],
        [
            qa("basic", "How does a rolling deployment work?", "Instances are replaced in batches: new ones start, pass readiness checks and take traffic, then old ones are terminated, until all are on the new version."),
            qa("intermediate", "What do maxSurge and maxUnavailable control?", "maxSurge is how many extra pods above the desired count can exist during the update; maxUnavailable is how many of the desired pods may be unavailable. maxUnavailable: 0 with maxSurge > 0 keeps full capacity."),
            qa("intermediate", "What is a downside of rolling deployments?", "Both versions serve traffic at the same time for the duration, so changes must be backward compatible, and every user may hit the new version quickly with limited blast-radius control."),
            qa("advanced", "A rolling update hangs at 3 of 6 new pods. What do you check?", "kubectl rollout status and describe on the new pods: failing readiness probes, image pull errors, resource quota or insufficient node capacity for the surge. progressDeadlineSeconds will mark it failed; roll back with kubectl rollout undo while investigating."),
        ],
        ["blue-green", "canary", "rollback-rollforward"],
        chain(
            ("v1 x6", "all old", "Start", "Six v1 pods serve traffic."),
            ("Surge", "+2 v2 pods", "Add new", "Two v2 pods start; maxSurge allows the extra capacity.", "update"),
            ("Ready", "probe passes", "Gate", "v2 pods pass readiness and join the Service endpoints.", "v2"),
            ("Retire", "-2 v1 pods", "Remove old", "Two v1 pods drain and terminate; the cycle repeats.", "ready"),
            ("v2 x6", "all new", "Complete", "All pods run v2; the old ReplicaSet is kept for rollback.", "done"),
        ),
    ),
    topic(
        "blue-green", "Blue-Green Deployments", "deployment", "intermediate", "BG",
        "Run a full new environment beside the old one and switch traffic in one move.",
        "Two identical stages in a theatre. The next show is fully set up on the dark stage while the current show runs; at the interval the audience is simply turned to face the new stage, and turned back if the lights fail.",
        "In a blue-green deployment two complete environments exist: blue serves production traffic and green receives the new version. Green is deployed, warmed up and tested in isolation (smoke tests, synthetic checks, even internal users through a test hostname). The cut-over switches all traffic at once by changing a load balancer target group, a Kubernetes Service selector, a DNS record or an API gateway stage. Rollback is equally fast: switch back to blue, which is still running. The costs are double capacity during the deployment and harder handling of state: both environments usually share a database, so schema changes must work for both versions (expand/contract), and in-flight sessions and long connections need draining. DNS-based switching is slow and uneven due to caching, so load balancer or service-mesh switching is preferred. Blue-green suits systems that need instant rollback and can afford the duplicate capacity; it is supported natively by AWS CodeDeploy for ECS and Lambda, Argo Rollouts (BlueGreen strategy with preview service), and Azure slots.",
        ["Releasing a payment service where rollback must take seconds.", "ECS deployments via CodeDeploy with test listeners.", "App Service deployment slots with swap."],
        [
            "Two full environments; switch traffic atomically.",
            "Test green on a preview endpoint before switching.",
            "Instant rollback by switching back to blue.",
            "Shared database requires backward-compatible migrations.",
            "Prefer LB or mesh switching over DNS TTL-based switching.",
        ],
        [
            ex("Argo Rollouts blue-green", "intermediate", "Preview service for testing; manual promotion; old ReplicaSet kept briefly.", "yaml", """
                apiVersion: argoproj.io/v1alpha1
                kind: Rollout
                metadata:
                  name: payments
                spec:
                  replicas: 4
                  selector:
                    matchLabels: {app: payments}
                  template:
                    metadata:
                      labels: {app: payments}
                    spec:
                      containers:
                        - name: payments
                          image: ghcr.io/acme/payments@sha256:EXAMPLE-DIGEST
                  strategy:
                    blueGreen:
                      activeService: payments-active
                      previewService: payments-preview
                      autoPromotionEnabled: false
                      prePromotionAnalysis:
                        templates:
                          - templateName: smoke-tests
                      scaleDownDelaySeconds: 600
            """, runnable=False),
            ex("Kubernetes Service selector switch", "basic", "Flip the Service to the green version label; flip back to roll back.", "bash", """
                kubectl apply -f payments-green.yaml       # Deployment with version: green
                kubectl rollout status deploy/payments-green
                ./smoke.sh https://payments-preview.internal.example.com
                kubectl patch service payments -p '{"spec":{"selector":{"app":"payments","version":"green"}}}'
                # rollback:
                kubectl patch service payments -p '{"spec":{"selector":{"app":"payments","version":"blue"}}}'
            """, runnable=False),
        ],
        ["kubectl argo rollouts promote payments", "kubectl argo rollouts undo payments", "kubectl patch svc x -p selector", "aws deploy create-deployment (ECS blue/green)", "az webapp deployment slot swap"],
        ["Running a destructive migration at cut-over makes switching back to blue impossible.", "DNS switching leaves some clients on blue for the TTL or longer.", "Background workers in both colours can double-process jobs; scale workers carefully."],
        [
            qa("basic", "What is a blue-green deployment?", "Running two identical production environments, deploying the new version to the idle one, testing it, then switching all traffic to it at once while keeping the old one ready for instant rollback."),
            qa("intermediate", "What are the downsides of blue-green?", "Double infrastructure during deployment, and shared state is tricky: the database must support both versions, sessions must survive the switch, and background jobs must not run twice."),
            qa("intermediate", "Blue-green vs rolling?", "Rolling replaces instances gradually in one environment with mixed versions for a while. Blue-green switches all traffic at once between two full environments, giving instant rollback at the cost of extra capacity."),
            qa("advanced", "How do you handle database migrations with blue-green?", "Use expand/contract: before the switch, apply only additive changes that both versions tolerate; after green is stable and blue is retired, apply the contract migration that removes old columns or tables."),
        ],
        ["rolling-deploy", "canary", "db-migrations"],
        chain(
            ("Blue live", "100% traffic", "Current", "Blue runs v1 and serves all production traffic."),
            ("Green up", "deploy v2", "Prepare", "Green is deployed with v2 and warmed up.", "v2"),
            ("Test", "preview URL", "Verify", "Smoke and synthetic tests hit green via the preview endpoint.", "probe"),
            ("Switch", "LB / selector", "Cut over", "The load balancer or Service selector moves 100% to green.", "pass"),
            ("Standby", "blue kept", "Rollback ready", "Blue stays up for a while so switching back is instant.", "live"),
        ),
    ),
    topic(
        "canary", "Canary Releases", "deployment", "intermediate", "CN",
        "Send a small slice of real traffic to the new version and expand only if metrics stay healthy.",
        "Miners carried a canary underground: if the air turned bad, the small bird showed it first, long before the whole crew was affected.",
        "A canary release exposes the new version to a small percentage of traffic (for example 1 percent, then 5, 25, 50, 100) while the rest stays on the stable version. At each step the canary's error rate, latency and business metrics are compared with the stable baseline; if they degrade, traffic shifts back and the canary is removed, so only a small fraction of users were affected. Traffic splitting can be done by replica ratios (crude), by load balancers with weighted target groups, by service meshes (Istio, Linkerd), by ingress controllers (NGINX canary annotations, Gateway API weights) or by CDN edge rules. Sticky routing by user or cookie keeps a user on one version to avoid flapping experiences. Canary analysis needs enough traffic to be statistically meaningful: 1 percent of a quiet service may be three requests. Tools like Argo Rollouts, Flagger, Spinnaker with Kayenta and AWS CodeDeploy automate the steps and analysis. Canaries limit blast radius in production, which no pre-production test can fully replicate.",
        ["Rolling out a new recommendation service version to 5 percent of users first.", "Catching a memory leak that only appears under real traffic.", "Automating rollback when error rate exceeds the baseline."],
        [
            "Small traffic slice, compare against stable baseline, expand stepwise.",
            "Weighted routing via mesh, ingress, LB or CDN.",
            "Analysis needs enough traffic and time per step.",
            "Sticky sessions keep users on one version.",
            "Automatic rollback on metric breach limits blast radius.",
        ],
        [
            ex("Argo Rollouts canary steps", "intermediate", "Weighted steps with pauses and background analysis.", "yaml", """
                apiVersion: argoproj.io/v1alpha1
                kind: Rollout
                metadata:
                  name: web
                spec:
                  replicas: 10
                  selector:
                    matchLabels: {app: web}
                  template:
                    metadata:
                      labels: {app: web}
                    spec:
                      containers:
                        - name: web
                          image: ghcr.io/acme/web@sha256:EXAMPLE-DIGEST
                  strategy:
                    canary:
                      canaryService: web-canary
                      stableService: web-stable
                      trafficRouting:
                        nginx:
                          stableIngress: web
                      analysis:
                        templates:
                          - templateName: error-rate
                        startingStep: 1
                      steps:
                        - setWeight: 5
                        - pause: {duration: 10m}
                        - setWeight: 25
                        - pause: {duration: 10m}
                        - setWeight: 50
                        - pause: {duration: 15m}
            """, runnable=False),
            ex("Operate a canary", "basic", "Watch, promote or abort from the CLI.", "bash", """
                kubectl argo rollouts get rollout web --watch
                kubectl argo rollouts promote web          # skip current pause
                kubectl argo rollouts abort web            # shift all traffic back to stable
                kubectl argo rollouts retry rollout web
            """, runnable=False),
        ],
        ["kubectl argo rollouts get rollout x --watch", "kubectl argo rollouts abort x", "setWeight / pause steps", "nginx.ingress.kubernetes.io/canary-weight", "Compare canary vs baseline, not vs history"],
        ["Too little traffic at the canary step makes analysis noise, not signal.", "Comparing canary to last week instead of to the concurrent baseline confuses seasonality with regressions.", "Canary by replica count gives coarse percentages and no stickiness."],
        [
            qa("basic", "What is a canary release?", "Releasing a new version to a small subset of traffic or users first, monitoring it against the stable version, and gradually increasing exposure if it stays healthy."),
            qa("intermediate", "How is traffic split for a canary?", "Through weighted routing in a service mesh, ingress controller, load balancer or CDN, or crudely by the ratio of canary to stable replicas. Header or cookie rules can target specific users."),
            qa("intermediate", "Canary vs blue-green?", "Blue-green switches all traffic at once with instant rollback; canary shifts traffic gradually, limiting blast radius and allowing metric comparison at each step, but takes longer and needs good traffic routing and observability."),
            qa("advanced", "What metrics make a good canary analysis?", "Request error rate and latency percentiles compared with the stable baseline running at the same time, saturation such as CPU and memory, and key business metrics like checkout success. Use enough samples per step and conservative thresholds tied to SLOs."),
        ],
        ["progressive-delivery", "blue-green", "feature-flags", "rollback-rollforward"],
        chain(
            ("Stable", "100% v1", "Baseline", "All traffic is on the stable version."),
            ("5%", "canary v2", "First slice", "Routing sends 5 percent of requests to the canary.", "5%"),
            ("Analyse", "vs baseline", "Compare", "Error rate and latency of canary and stable are compared.", "metrics"),
            ("Expand", "25 -> 50%", "Step up", "If healthy, weight increases step by step with pauses.", "pass"),
            ("Promote", "100% v2", "Complete", "Canary becomes stable; on failure it aborts back to v1.", "healthy"),
        ),
    ),
]

_BATCH_5 = [
    topic(
        "feature-flags", "Feature Flags", "deployment", "intermediate", "FF",
        "Runtime switches that separate deploying code from releasing behaviour.",
        "Light switches wired in during construction. The electrician installs everything (deploy), and the owner decides later which rooms to light and for whom (release).",
        "A feature flag (toggle) is a runtime conditional whose value comes from configuration or a flag service (LaunchDarkly, Unleash, Flagsmith, OpenFeature-compatible providers, or a simple config store). Code for a new feature can be merged and deployed with the flag off, then enabled for internal users, a percentage of customers, a region or specific accounts, and turned off instantly if it misbehaves, without a redeploy. Common flag types are release flags (temporary, for rollout), experiment flags (A/B tests), ops flags or kill switches (disable an expensive feature under load) and permission flags (entitlements). Flags enable trunk-based development and continuous deployment because unfinished work can live safely on main. They also create debt: every flag doubles code paths, so release flags need owners, expiry dates and removal tickets, and tests should cover both states for critical flags. Flag evaluation should be fast and resilient, using local caching and safe defaults if the flag service is unreachable. Flag changes are production changes and should be audited and visible next to deploy markers on dashboards.",
        ["Merging half-built features to main safely.", "Turning on a feature for 1 percent of users, then 10, then everyone.", "A kill switch that disables a heavy recommendation call during an incident."],
        [
            "Deploy is technical; release is a business decision controlled by flags.",
            "Types: release, experiment, ops/kill switch, permission.",
            "Every release flag needs an owner and removal date.",
            "Safe defaults when the flag service is unreachable.",
            "Audit flag changes like deploys.",
        ],
        [
            ex("OpenFeature-style evaluation config", "intermediate", "Flag definition with percentage rollout and targeting (flagd JSON).", "json", """
                {
                  "$schema": "https://flagd.dev/schema/v0/flags.json",
                  "flags": {
                    "checkout.new-pricing": {
                      "state": "ENABLED",
                      "variants": {"on": true, "off": false},
                      "defaultVariant": "off",
                      "targeting": {
                        "if": [
                          {"ends_with": [{"var": "email"}, "@acme.example"]}, "on",
                          {"fractional": [{"var": "userId"}, ["on", 10], ["off", 90]]}
                        ]
                      }
                    }
                  }
                }
            """, runnable=False),
            ex("Flag hygiene in CI", "advanced", "Fail the build when release flags pass their expiry date.", "bash", """
                # flags.yaml lists: name, type, owner, expires
                python scripts/check_flags.py flags.yaml --today "$(date -u +%F)"
                # also: grep the codebase for flags not present in flags.yaml
                rg -o "isEnabled\\(\\"([a-z0-9.-]+)\\"" -r '$1' src/ | sort -u > used.txt
                yq '.flags[].name' flags.yaml | sort -u > declared.txt
                comm -23 used.txt declared.txt
            """, runnable=False),
        ],
        ["flag on for: internal -> 1% -> 10% -> 100%", "Kill switch: ops flag default on, off under load", "Expiry date + owner per release flag", "Test both flag states for critical paths", "Show flag changes on dashboards"],
        ["Stale flags accumulate into untestable combinations.", "Evaluating flags with a network call per request adds latency and a new failure mode.", "Reusing an old flag name for a new feature can silently enable code for the wrong users."],
        [
            qa("basic", "What is a feature flag?", "A runtime switch that turns behaviour on or off without redeploying, letting code be deployed dark and released gradually or to selected users."),
            qa("intermediate", "How do feature flags support continuous deployment?", "Unfinished or risky features merge and deploy with the flag off, so main stays releasable and every commit can ship. Release becomes a controlled flag change rather than a deploy."),
            qa("intermediate", "What are the risks of feature flags?", "Technical debt from stale flags, combinatorial testing complexity, a dependency on the flag service, and unaudited production changes. Mitigate with ownership, expiry, safe defaults, local caching and audit logs."),
            qa("advanced", "Feature flag rollout vs canary deployment?", "A canary routes a fraction of traffic to a new binary and is managed by the deploy system. A flag rollout runs one binary and exposes a feature to a fraction of users, controlled at the application level, with user-level targeting and instant toggling. They complement each other."),
        ],
        ["trunk-based-dev", "dark-launch-shadow", "canary", "progressive-delivery"],
        chain(
            ("Merge", "flag off", "Ship dark", "Code merges to main with the flag defaulting off."),
            ("Deploy", "no exposure", "Deploy", "The new code deploys everywhere but is not active.", "build"),
            ("Internal", "staff only", "Dogfood", "The flag is enabled for internal users first.", "deployed"),
            ("Ramp", "1 -> 10 -> 100%", "Gradual release", "Exposure increases while metrics are watched.", "on"),
            ("Remove", "delete flag", "Clean up", "Once fully on and stable, the flag and old path are deleted.", "100%"),
        ),
    ),
    topic(
        "dark-launch-shadow", "Dark Launches & Shadow Traffic", "deployment", "advanced", "DL",
        "Run new code on real production traffic without users seeing its results.",
        "A trainee pilot flying the same route in a simulator synced to the real plane's inputs. Every decision is recorded and compared, but passengers only ever feel the captain's hands.",
        "A dark launch deploys a new feature or service to production and exercises it with real traffic or data, but hides the outcome from users. A common form is shadow (mirrored) traffic: a proxy or service mesh copies incoming requests to the new version asynchronously, discards its responses for users and records them for comparison with the live version. Istio supports this with mirror and mirrorPercentage, Envoy with request_mirror_policies, and NGINX with the mirror directive. Another form is calling the new code path in the background behind a flag (for example computing new search results and logging differences), sometimes called a diff test or Scientist-style experiment. Dark launches reveal performance under real load, real data edge cases and correctness differences before any user depends on the new system, which is valuable for rewrites, migrations and ML models. The big danger is side effects: mirrored requests must not charge cards, send emails or write to the production database, so shadow services need stubbed or isolated downstreams and idempotency. Mirroring also adds load to shared dependencies and should be capacity-planned.",
        ["Validating a rewritten pricing service against the old one on live requests.", "Load-testing a new database with real query patterns.", "Running a new ML model in shadow mode before it makes decisions."],
        [
            "Users see only the live version's responses.",
            "Mirror via mesh, Envoy or NGINX; compare outputs offline.",
            "Shadow writes must go to isolated stores; stub payments and emails.",
            "Start with a small mirror percentage; watch shared dependencies.",
            "Great for rewrites, migrations and models.",
        ],
        [
            ex("Istio traffic mirroring", "advanced", "All traffic served by v1; 20 percent mirrored to v2.", "yaml", """
                apiVersion: networking.istio.io/v1
                kind: VirtualService
                metadata:
                  name: pricing
                spec:
                  hosts: [pricing]
                  http:
                    - route:
                        - destination:
                            host: pricing
                            subset: v1
                          weight: 100
                      mirror:
                        host: pricing
                        subset: v2
                      mirrorPercentage:
                        value: 20.0
            """, runnable=False),
            ex("Compare shadow vs live results", "intermediate", "Offline diff of logged responses keyed by request id.", "bash", """
                # both versions log {request_id, status, body_sha256}
                jq -r '[.request_id, .status, .body_sha256] | @tsv' live.jsonl | sort > live.tsv
                jq -r '[.request_id, .status, .body_sha256] | @tsv' shadow.jsonl | sort > shadow.tsv
                join -t $'\\t' live.tsv shadow.tsv | awk -F'\\t' '$2!=$4 || $3!=$5' | wc -l
            """, runnable=False),
        ],
        ["Istio: mirror + mirrorPercentage", "NGINX: mirror /shadow;", "Envoy: request_mirror_policies", "Compare by request id and SHA-256 of body", "Shadow mode: isolated writes"],
        ["Mirrored POSTs that hit real payment or email providers cause real side effects.", "Mirroring doubles load on shared databases and caches.", "Mirrored requests are fire-and-forget; shadow latency is not seen by users but must still be measured."],
        [
            qa("basic", "What is a dark launch?", "Deploying a feature to production and exercising it with real traffic or data while hiding its results from users, to validate behaviour and performance before release."),
            qa("intermediate", "How does shadow traffic work?", "A proxy or mesh duplicates live requests to the new version asynchronously. Users get the live version's response; the shadow's responses are recorded and compared."),
            qa("intermediate", "What is the main risk with traffic mirroring?", "Side effects: the shadow may write data, charge payments or send notifications. Shadow deployments must use isolated stores or stubs, and mirroring should be limited to safe or idempotent operations."),
            qa("advanced", "Shadow vs canary for a rewritten service?", "Shadow lets you compare correctness and performance on real traffic without user impact, so it comes first for risky rewrites. Once differences are understood and fixed, a canary exposes real users gradually."),
        ],
        ["canary", "feature-flags", "ml-pipelines"],
        chain(
            ("Request", "live user", "Incoming", "A user request arrives at the mesh or proxy."),
            ("Serve v1", "response to user", "Live path", "The live version handles the request and responds.", "req"),
            ("Mirror", "copy to v2", "Shadow path", "A copy is sent asynchronously to the shadow version.", "copy"),
            ("Discard", "isolated writes", "No impact", "Shadow responses are discarded for users; writes go to isolated stores.", "resp"),
            ("Compare", "diff results", "Analyse", "Logged outputs and latencies are compared offline.", "logs"),
        ),
    ),
    topic(
        "db-migrations", "Database Migrations in CD (Expand/Contract)", "deployment", "advanced", "DB",
        "Change schemas in backwards-compatible steps so old and new code both keep working.",
        "Widening a road: you build the new lane first, let traffic use both, move everyone across, and only then remove the old lane. You never dig up the only lane while cars are on it.",
        "Application deploys are easy to roll back; schema changes are not, and during rolling, blue-green or canary deployments old and new code run against the same database at the same time. The expand/contract (parallel change) pattern makes every step compatible with both versions. Expand: add new tables or nullable columns, new indexes (built concurrently), and code that writes to both old and new structures. Migrate: backfill existing data in batches, then switch reads to the new structure. Contract: once no running version uses the old structure, drop it in a later release. Renaming a column directly, adding a NOT NULL column without a default, or changing a type in place are classic outage causes because the old code or locks break immediately. Migrations should be versioned (Flyway, Liquibase, Alembic, Rails, Prisma, Atlas) and run as a dedicated pipeline step or Kubernetes Job before the app rollout, with a single runner holding a lock. Lock behaviour matters: on large PostgreSQL tables use CREATE INDEX CONCURRENTLY, set lock_timeout, and avoid long transactions. Test migrations against a production-sized copy and make sure they are idempotent and observable.",
        ["Renaming a column with zero downtime.", "Adding a required field to a 500-million-row table.", "Running migrations as a gated step before a canary rollout."],
        [
            "Every migration must work with both the old and the new app version.",
            "Expand -> migrate/backfill -> switch reads -> contract later.",
            "Run migrations once, with a lock, before the app rollout.",
            "Use CONCURRENTLY and lock_timeout on big PostgreSQL tables.",
            "Roll forward data changes; rollback of schema is rarely safe.",
        ],
        [
            ex("Zero-downtime column rename in three releases", "advanced", "Expand, backfill, then contract (PostgreSQL).", "sql", """
                -- Release 1 (expand): new column, app writes both
                ALTER TABLE customers ADD COLUMN email_address text;
                CREATE INDEX CONCURRENTLY idx_customers_email_address ON customers (email_address);

                -- Backfill in batches (job, not in the deploy transaction)
                UPDATE customers SET email_address = email
                 WHERE id IN (SELECT id FROM customers WHERE email_address IS NULL LIMIT 10000);

                -- Release 2: app reads email_address, still writes both
                ALTER TABLE customers ADD CONSTRAINT email_address_nn CHECK (email_address IS NOT NULL) NOT VALID;
                ALTER TABLE customers VALIDATE CONSTRAINT email_address_nn;

                -- Release 3 (contract): nothing reads email any more
                ALTER TABLE customers DROP COLUMN email;
            """, runnable=False),
            ex("Migration step before rollout", "intermediate", "Run migrations once with a short lock timeout, then deploy.", "yaml", """
                jobs:
                  migrate:
                    runs-on: ubuntu-latest
                    environment: production
                    permissions:
                      contents: read
                      id-token: write
                    concurrency:
                      group: db-migrate-production
                      cancel-in-progress: false
                    steps:
                      - uses: actions/checkout@v4
                      - run: ./scripts/get-db-creds.sh production   # short-lived creds via OIDC + secrets manager
                      - run: PGOPTIONS='-c lock_timeout=5s -c statement_timeout=15min' flyway -configFiles=flyway-prod.conf migrate
                  deploy:
                    needs: migrate
                    runs-on: ubuntu-latest
                    environment: production
                    steps:
                      - run: ./deploy.sh production "${{ github.sha }}"
            """, runnable=False),
        ],
        ["flyway migrate · flyway info", "alembic upgrade head", "CREATE INDEX CONCURRENTLY", "SET lock_timeout = '5s'", "ADD CONSTRAINT ... NOT VALID; VALIDATE CONSTRAINT"],
        ["ALTER TABLE ... RENAME COLUMN breaks every running old pod instantly.", "Adding a NOT NULL column with a volatile default can rewrite and lock a huge table.", "Running migrations from every app pod at startup causes races; run once.", "Down migrations that drop data are not real rollbacks."],
        [
            qa("basic", "Why are database migrations hard in continuous delivery?", "During a deploy, old and new application versions run against the same database, and schema changes are hard to undo. A change that breaks the old version causes an outage mid-rollout."),
            qa("intermediate", "Explain expand/contract.", "First expand the schema with additive, backward-compatible changes and dual writes; then backfill and switch reads to the new structure; finally, once no code uses the old structure, contract by removing it in a later release."),
            qa("intermediate", "Where should migrations run in a pipeline?", "As a dedicated, serialised step or Kubernetes Job before the application rollout, run once with a migration lock, not from every pod at startup."),
            qa("advanced", "How do you add an index to a huge PostgreSQL table without downtime?", "Use CREATE INDEX CONCURRENTLY outside a transaction, set lock_timeout so it fails fast instead of queueing behind long locks, monitor progress with pg_stat_progress_create_index, and drop and retry if it ends up invalid."),
            qa("advanced", "How do you roll back a bad release that included a migration?", "Because the migration was additive (expand), roll back only the application; the old code ignores the new column. Destructive changes are only in contract releases, which ship after the new code has proven stable."),
        ],
        ["blue-green", "rollback-rollforward", "approvals-gates"],
        chain(
            ("Expand", "add, nullable", "Additive", "Add new columns or tables that old code safely ignores."),
            ("Dual write", "new code", "Write both", "New app version writes to old and new structures.", "schema"),
            ("Backfill", "batches", "Migrate data", "A background job copies existing rows in small batches.", "writes"),
            ("Switch", "read new", "Cut reads", "A later release reads from the new structure only.", "data"),
            ("Contract", "drop old", "Clean up", "Once no version uses it, the old column is dropped.", "safe"),
        ),
    ),
    topic(
        "approvals-gates", "Approvals, Gates & Change Management", "deployment", "intermediate", "AG",
        "Automated quality gates by default, human approvals where risk or policy requires.",
        "Airport security: most checks are machines (scanners, gates) that work in seconds for everyone, and a human officer steps in only for the cases that genuinely need judgement.",
        "Gates are conditions a change must satisfy before moving to the next stage. Automated gates include passing tests, coverage thresholds, static analysis and vulnerability policies (no critical CVEs), license checks, signed artifact verification, policy-as-code (OPA, Kyverno), successful staging smoke tests and healthy SLO metrics. Manual gates are approvals by a person or team: GitHub environment reviewers, GitLab deployment approvals, Azure environment checks, Jenkins input steps or a change ticket in ServiceNow. Separation of duties (the author cannot approve their own production deploy) and audit trails satisfy many compliance regimes such as SOC 2 and PCI DSS. Gates should be fast and meaningful; a manual approval that takes two days or that reviewers click without reading adds delay without safety. Prefer moving manual checks into automation over time, and use change windows or freeze periods sparingly, because large batches after a freeze are riskier than steady small changes. DORA research found heavyweight external change approval boards correlate with worse delivery performance and no stability gain, while peer review and automated checks work better.",
        ["A security gate that blocks images with critical vulnerabilities.", "Separation of duties for production deploys under SOC 2.", "Automatic change records created by the pipeline."],
        [
            "Automate gates first: tests, scans, policy, SLOs.",
            "Human approval for genuine judgement or regulatory need.",
            "Separation of duties: no self-approval of production deploys.",
            "Every gate decision should be logged for audit.",
            "Change advisory boards slow delivery without improving stability.",
        ],
        [
            ex("Policy gate on vulnerabilities and signatures", "intermediate", "Fail the job if the image has critical CVEs or an invalid signature.", "yaml", """
                jobs:
                  gate:
                    runs-on: ubuntu-latest
                    permissions:
                      contents: read
                    steps:
                      - uses: aquasecurity/trivy-action@0.28.0
                        with:
                          image-ref: ghcr.io/acme/api@${{ needs.build.outputs.digest }}
                          severity: CRITICAL
                          exit-code: "1"
                          ignore-unfixed: true
                      - uses: sigstore/cosign-installer@v3
                      - run: |
                          cosign verify ghcr.io/acme/api@${{ needs.build.outputs.digest }} \\
                            --certificate-identity-regexp '^https://github.com/acme/api/.github/workflows/release.yml@refs/heads/main$' \\
                            --certificate-oidc-issuer https://token.actions.githubusercontent.com
            """, runnable=False),
            ex("Jenkins approval with timeout", "basic", "Restricted submitters, auto-abort after 4 hours.", "groovy", """
                stage('Approve production') {
                  when { branch 'main' }
                  steps {
                    timeout(time: 4, unit: 'HOURS') {
                      input message: "Deploy ${env.GIT_COMMIT.take(7)} to production?", submitter: 'release-managers', ok: 'Deploy'
                    }
                  }
                }
            """, runnable=False),
        ],
        ["environment reviewers + prevent_self_review", "trivy image --severity CRITICAL --exit-code 1", "cosign verify --certificate-identity ...", "conftest test manifests/", "input submitter: 'team'"],
        ["Approvers with no context approve blindly; show diff, risk and test evidence.", "A freeze creates a huge batch afterwards, which is riskier than steady deploys.", "Gates that can be skipped with a label or admin override are not gates."],
        [
            qa("basic", "What is a quality gate?", "A condition a change must meet to progress in the pipeline, such as passing tests, a coverage threshold or no critical vulnerabilities."),
            qa("intermediate", "When is a manual approval appropriate?", "When a decision needs human judgement or is required by regulation, such as production releases in a regulated system. It should be fast, informed by evidence and performed by someone other than the author."),
            qa("intermediate", "How do automated gates support compliance?", "They enforce policy consistently and log every decision with the commit, artifact digest, actor and evidence, giving auditors a better trail than manual checklists."),
            qa("advanced", "What does DORA research say about change approval boards?", "Heavyweight external approval processes were associated with lower delivery performance and no improvement in change failure rate. Lightweight peer review plus automated checks gave better outcomes."),
        ],
        ["gha-environments", "env-promotion", "security-scanning", "signing-cosign"],
        chain(
            ("Tests", "green", "Quality", "All required tests and coverage thresholds pass."),
            ("Scans", "CVEs, policy", "Security", "Vulnerability and policy checks pass for the exact digest.", "pass"),
            ("Verify", "signature", "Integrity", "The artifact signature and provenance are verified.", "clean"),
            ("Approve", "not the author", "Human gate", "An authorised reviewer approves with evidence attached.", "signed"),
            ("Record", "audit log", "Change record", "The decision, actor and digest are logged automatically.", "approved"),
        ),
    ),
    topic(
        "progressive-delivery", "Progressive Delivery with Metric Analysis", "deployment", "advanced", "PD",
        "Automate canary steps with queries against real metrics and auto-rollback.",
        "An autopilot that climbs in steps, checking instruments at each altitude. If any gauge goes into the red, it levels off and descends back to safety without waiting for the captain.",
        "Progressive delivery combines gradual exposure (canary, blue-green, flags) with automated analysis so that promotion and rollback decisions are made by the system based on metrics. Argo Rollouts uses AnalysisTemplates that run Prometheus, Datadog, CloudWatch, New Relic or web queries during steps, with successCondition and failureLimit; a failed analysis aborts the rollout and shifts traffic back to stable. Flagger does the same for Istio, Linkerd, Contour, NGINX and Gateway API using metric templates and webhooks for load tests or acceptance tests. Spinnaker with Kayenta performs statistical comparisons between canary and baseline clusters. Good analysis queries compare the canary with the stable version at the same time, use SLO-aligned signals (error ratio, p99 latency, saturation) and include business metrics where possible. Inconclusive results, such as no data because of low traffic, should be treated carefully, often as a failure or pause. Analysis can also run before promotion (pre-promotion) and after full rollout (post-promotion) to catch slow-burn regressions like memory leaks.",
        ["Fully automatic canary promotion and rollback for a high-traffic API.", "Gating promotion on a Prometheus error-ratio query.", "Running a load test webhook at each canary step."],
        [
            "Analysis queries decide promote vs abort, not people watching graphs.",
            "Compare canary against concurrent stable baseline.",
            "Use SLO-aligned metrics with conservative thresholds.",
            "Treat no data as a failure or inconclusive, not as success.",
            "Abort shifts traffic back automatically.",
        ],
        [
            ex("Argo Rollouts AnalysisTemplate (Prometheus)", "advanced", "Canary 5xx ratio must stay under 1 percent; three failures abort.", "yaml", """
                apiVersion: argoproj.io/v1alpha1
                kind: AnalysisTemplate
                metadata:
                  name: error-rate
                spec:
                  args:
                    - name: service
                  metrics:
                    - name: error-ratio
                      interval: 1m
                      count: 10
                      failureLimit: 3
                      successCondition: len(result) > 0 && result[0] < 0.01
                      provider:
                        prometheus:
                          address: http://prometheus.monitoring:9090
                          query: |
                            sum(rate(http_requests_total{service="{{args.service}}",role="canary",code=~"5.."}[2m]))
                            /
                            sum(rate(http_requests_total{service="{{args.service}}",role="canary"}[2m]))
            """, runnable=False),
            ex("Flagger canary with webhook load test", "advanced", "Istio-based canary with metric thresholds.", "yaml", """
                apiVersion: flagger.app/v1beta1
                kind: Canary
                metadata:
                  name: api
                  namespace: shop
                spec:
                  targetRef:
                    apiVersion: apps/v1
                    kind: Deployment
                    name: api
                  service:
                    port: 8080
                  analysis:
                    interval: 1m
                    threshold: 5
                    maxWeight: 50
                    stepWeight: 10
                    metrics:
                      - name: request-success-rate
                        thresholdRange: {min: 99}
                        interval: 1m
                      - name: request-duration
                        thresholdRange: {max: 500}
                        interval: 1m
                    webhooks:
                      - name: load-test
                        url: http://flagger-loadtester.test/
                        metadata:
                          cmd: "hey -z 1m -q 10 -c 2 http://api-canary.shop:8080/"
            """, runnable=False),
        ],
        ["kubectl argo rollouts get rollout x", "kubectl get analysisrun", "kubectl describe canary api -n shop", "successCondition / failureLimit", "Flagger: stepWeight, maxWeight, threshold"],
        ["A query that returns nothing at low traffic can pass the canary by accident.", "Thresholds copied from another service ignore its normal error baseline.", "Only checking technical metrics misses business regressions like falling conversion."],
        [
            qa("basic", "What is progressive delivery?", "Releasing changes gradually to increasing audiences while automated analysis of metrics decides whether to continue, pause or roll back."),
            qa("intermediate", "How does Argo Rollouts decide to abort a canary?", "An AnalysisRun executes metric queries at intervals; if results fail the successCondition more times than failureLimit, the analysis fails and the rollout aborts, routing all traffic back to stable."),
            qa("intermediate", "What metrics should a canary analysis use?", "SLO-aligned signals such as error ratio and latency percentiles for the canary compared with stable, plus saturation and, ideally, key business metrics."),
            qa("advanced", "How do you handle low-traffic services in automated canary analysis?", "Use longer steps or synthetic load to gather enough samples, require a minimum request count in the query, treat empty results as failure or inconclusive, and consider header-based routing of test traffic instead of percentages."),
        ],
        ["canary", "feature-flags", "rollback-rollforward", "pipeline-observability"],
        chain(
            ("Deploy", "canary pods", "Start", "The rollout creates canary pods next to stable."),
            ("Shift", "setWeight 10", "Route", "Traffic routing sends 10 percent to the canary.", "pods"),
            ("Query", "Prometheus", "Analyse", "Analysis queries error ratio and latency for canary vs stable.", "10%"),
            ("Decide", "pass / fail", "Evaluate", "Results are checked against successCondition and failureLimit.", "metrics"),
            ("Promote", "or abort", "Act", "Pass promotes to the next step; fail aborts and returns traffic.", "verdict"),
        ),
    ),
    topic(
        "rollback-rollforward", "Rollback & Roll-Forward", "operations", "intermediate", "RB",
        "Restore service fast by going back to a known-good version or forward with a fix.",
        "A GPS that has taken a wrong turn can either do a U-turn to the last known road (rollback) or take the next exit that leads to the destination anyway (roll-forward). The right choice depends on traffic and how far you have gone.",
        "When a release causes problems, the priority is to restore service, then find the root cause. Rollback redeploys the previous known-good artifact: kubectl rollout undo, Argo Rollouts abort, switching back in blue-green, git revert in GitOps, or redeploying the previous digest from the pipeline. It is usually fastest when the change is stateless. Roll-forward ships a new fix through the pipeline, which is appropriate when rollback is unsafe (a migration already changed data, an external API contract moved on, mobile clients updated) or when the fix is tiny and the pipeline is fast. Feature flags offer a third option: disable the feature without any deploy. To make rollback reliable, keep previous artifacts available by digest, keep schema changes backwards compatible (expand/contract), make deploys idempotent and practice rollbacks regularly so they are routine. Decide in advance who can trigger a rollback and make it a one-command or one-click action, ideally automated by progressive delivery when metrics breach thresholds. Time to restore service is one of the DORA metrics, and rollback capability is a major driver of it.",
        ["Undoing a deploy that doubled error rates within two minutes.", "Rolling forward when a migration already transformed data.", "Disabling a broken feature with a flag instead of redeploying."],
        [
            "Restore first, investigate second.",
            "Rollback = previous digest; roll-forward = new fix via pipeline.",
            "Flags allow instant disable with no deploy.",
            "Backwards-compatible schema changes keep rollback possible.",
            "Practise rollbacks so they are boring and fast.",
        ],
        [
            ex("Rollback options by platform", "basic", "Kubernetes, Argo Rollouts, ECS and GitOps.", "bash", """
                kubectl rollout undo deploy/api                       # previous ReplicaSet
                kubectl rollout undo deploy/api --to-revision=41
                kubectl argo rollouts abort web && kubectl argo rollouts undo web
                aws ecs update-service --cluster prod --service api --task-definition api:118
                git revert --no-edit 3f2c1ab && git push            # GitOps: agent reconciles back
                helm rollback api 41 -n shop
            """, runnable=False),
            ex("One-click rollback workflow", "intermediate", "Redeploy a previous digest chosen by the operator.", "yaml", """
                name: rollback
                on:
                  workflow_dispatch:
                    inputs:
                      digest:
                        description: "sha256 digest of the known-good image"
                        required: true
                permissions:
                  contents: read
                  id-token: write
                concurrency:
                  group: deploy-production
                  cancel-in-progress: false
                jobs:
                  rollback:
                    runs-on: ubuntu-latest
                    environment: production
                    steps:
                      - uses: actions/checkout@v4
                      - name: Validate digest format
                        env:
                          DIGEST: ${{ inputs.digest }}
                        run: printf '%s' "$DIGEST" | grep -Eq '^sha256:[a-f0-9]{64}$'
                      - name: Deploy previous image
                        env:
                          DIGEST: ${{ inputs.digest }}
                        run: ./deploy.sh production "ghcr.io/acme/api@${DIGEST}"
            """, runnable=False),
        ],
        ["kubectl rollout undo deploy/x", "helm rollback rel REV", "kubectl argo rollouts abort x", "git revert <sha> (GitOps)", "Flag off = zero-deploy rollback"],
        ["Rollback after a destructive migration can make things worse; check data compatibility first.", "Rolling back the app but not its config or feature flag state leaves a mismatched system.", "Image retention policies that delete old digests make rollback impossible."],
        [
            qa("basic", "What is the difference between rollback and roll-forward?", "Rollback returns to the previous known-good version. Roll-forward fixes the problem by deploying a new version that contains a fix."),
            qa("intermediate", "When would you roll forward instead of rolling back?", "When rollback is unsafe or impossible, for example after a non-reversible data migration, when clients already depend on the new contract, or for mobile apps; or when the fix is trivial and the pipeline is fast enough."),
            qa("intermediate", "How do you make rollbacks reliable?", "Keep previous artifacts addressable by digest, make schema changes backwards compatible, keep deploys idempotent, automate rollback as a single action and practise it regularly."),
            qa("advanced", "How does rollback work in GitOps when selfHeal is on?", "Rolling back in the cluster directly is reverted by the agent, so roll back in Git with git revert of the config change. The agent then reconciles to the previous desired state, keeping Git as the source of truth."),
        ],
        ["incident-postmortem", "db-migrations", "progressive-delivery", "dora-metrics"],
        chain(
            ("Detect", "alert fires", "Notice", "An alert or canary analysis shows the new version is unhealthy."),
            ("Decide", "back or forward", "Choose", "On-call decides: rollback, roll-forward or disable a flag.", "alert"),
            ("Restore", "previous digest", "Act", "The known-good digest is redeployed or traffic is switched back.", "decision"),
            ("Verify", "metrics recover", "Confirm", "Dashboards confirm errors and latency return to baseline.", "deployed"),
            ("Follow up", "postmortem", "Learn", "The incident is reviewed and the real fix goes through the pipeline.", "stable"),
        ),
    ),
    topic(
        "dora-metrics", "DORA Metrics", "operations", "intermediate", "DM",
        "Deployment frequency, lead time, change failure rate and time to restore.",
        "A car's dashboard for delivery: speedometer (deploy frequency), journey time (lead time), how often you break down (change failure rate) and how fast roadside assistance gets you moving (time to restore).",
        "The DORA (DevOps Research and Assessment) programme identified four key metrics that predict software delivery performance. Deployment frequency is how often an organisation deploys to production. Lead time for changes is the time from a commit (or merge) to that change running in production. Change failure rate is the percentage of deployments that cause a failure in production requiring remediation such as a rollback, hotfix or incident. Time to restore service (failed deployment recovery time in newer reports) is how long it takes to recover from such a failure. The first two measure throughput and the last two measure stability; DORA's finding is that high performers are good at both, and they reinforce each other through small batches and automation. Newer reports also discuss reliability as a fifth dimension and rework rate. Data comes from version control, CI/CD and incident systems: deploy events with commit SHAs, commit timestamps and incidents linked to deployments. Metrics should be used to improve systems and spot bottlenecks, not to rank teams or individuals, because gaming them is easy.",
        ["Showing the effect of moving from weekly to daily releases.", "Finding that lead time is dominated by waiting for review.", "Tracking whether a new testing strategy lowers change failure rate."],
        [
            "Throughput: deployment frequency, lead time for changes.",
            "Stability: change failure rate, time to restore.",
            "Elite teams excel at both; speed and stability are not a trade-off.",
            "Compute from deploy events, commits and incidents linked by SHA.",
            "Use for improvement, not for ranking people.",
        ],
        [
            ex("Record a deployment event", "intermediate", "Emit a structured deploy event the metrics system can join with commits and incidents.", "yaml", """
                - name: Record deployment
                  if: success()
                  env:
                    DEPLOY_API: ${{ vars.DEPLOY_EVENTS_URL }}
                    TOKEN: ${{ secrets.DEPLOY_EVENTS_TOKEN }}
                  run: |
                    curl -fsS -X POST "$DEPLOY_API" -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -d "{\\"service\\":\\"api\\",\\"env\\":\\"production\\",\\"sha\\":\\"${GITHUB_SHA}\\",\\"finished_at\\":\\"$(date -u +%FT%TZ)\\"}"
            """, runnable=False),
            ex("Lead time for a release from git", "basic", "Hours from each commit to the deploy time of the release that contained it.", "bash", """
                DEPLOYED_AT=$(date -u -d '2026-10-17T10:00:00Z' +%s)
                git log --format='%H %ct' v1.4.2..v1.5.0 | while read sha ts; do
                  echo "$sha $(( (DEPLOYED_AT - ts) / 3600 ))h"
                done | sort -k2 -n | awk '{a[NR]=$2} END {print "median lead time:", a[int((NR+1)/2)]}'
            """, runnable=False),
        ],
        ["Deploy frequency = deploys / day", "Lead time = deploy_time - commit_time (median)", "CFR = failed deploys / total deploys", "Time to restore = resolved - started", "Join on commit SHA"],
        ["Counting deploys to staging inflates deployment frequency.", "Using averages hides long tails; use medians and percentiles.", "Teams pressured on metrics may split deploys or avoid declaring incidents."],
        [
            qa("basic", "What are the four DORA metrics?", "Deployment frequency, lead time for changes, change failure rate and time to restore service."),
            qa("intermediate", "How do you measure lead time for changes?", "For each change, take the time from commit (or merge) to when the deployment containing it finished in production, then report the median over a period. This needs deploy events that record the commit SHA."),
            qa("intermediate", "What counts as a change failure?", "A production deployment that results in degraded service requiring remediation, such as a rollback, hotfix, patch or incident. It is measured as a percentage of production deployments."),
            qa("advanced", "Do speed and stability trade off?", "DORA's research shows they do not: high performers have both higher throughput and better stability, because small, frequent, automated changes are easier to test, review and roll back."),
            qa("advanced", "How would you avoid DORA metrics being gamed?", "Use them at team or system level for improvement, not for individual performance, combine them with qualitative feedback, define failure and deploy consistently, and look at trends rather than targets."),
        ],
        ["pipeline-observability", "rollback-rollforward", "ci-vs-cd"],
        chain(
            ("Commit", "timestamp", "Change starts", "A commit is created; its timestamp starts the lead-time clock."),
            ("Deploy", "event + SHA", "Deploy event", "The pipeline records a production deploy event with commit SHAs.", "sha"),
            ("Incident", "linked deploy", "Failures", "Incidents are linked to the deploy that caused them.", "event"),
            ("Compute", "4 metrics", "Aggregate", "Frequency, lead time, failure rate and restore time are calculated.", "data"),
            ("Improve", "find bottleneck", "Act", "Teams use trends to target the slowest or riskiest step.", "trends"),
        ),
    ),
    topic(
        "pipeline-observability", "Pipeline Observability", "operations", "intermediate", "PO",
        "Measure pipeline duration, failure causes, queue time and flakiness like a production system.",
        "Fitting a factory line with sensors. Instead of guessing why orders are late, you can see which machine jams, how long items wait between stations, and which part fails most often.",
        "Pipelines are production systems for developers, and they need monitoring. Useful signals include end-to-end duration (p50, p95), queue time waiting for a runner, per-job and per-step duration, success rate by workflow and branch, failure categories (test failure, infrastructure, timeout, dependency download), flaky test rates, cache hit rates and cost per run. Sources are CI APIs and webhooks (GitHub workflow_run and workflow_job events, GitLab pipeline events, Jenkins metrics plugins), JUnit reports and OpenTelemetry: the CI/CD semantic conventions and tools like otel-cli, the Jenkins OpenTelemetry plugin or GitLab and GitHub exporters can emit each pipeline as a trace with jobs and steps as spans. Vendor products (Datadog CI Visibility, Honeycomb, Grafana, Buildkite Test Analytics, Gradle Develocity) provide dashboards. Deployment markers (annotations) should also flow into production dashboards so that every graph shows when a deploy happened, linking pipeline observability with service observability. Alert on main being red, rising queue times and success-rate drops, and review the slowest steps regularly.",
        ["Finding that 40 percent of pipeline time is waiting for runners.", "Tracing a slow job to a single dependency download step.", "Annotating Grafana dashboards with deploy markers."],
        [
            "Track duration p50/p95, queue time, success rate and cost.",
            "Classify failures: tests, infra, timeouts, flakes.",
            "Model pipelines as traces with OpenTelemetry.",
            "Send deploy markers to production dashboards.",
            "Alert when main is red or queue time spikes.",
        ],
        [
            ex("Pipeline as a trace with otel-cli", "advanced", "Wrap steps in spans exported over OTLP.", "bash", """
                export OTEL_EXPORTER_OTLP_ENDPOINT=https://otel-collector.example.com:4317
                export OTEL_SERVICE_NAME=ci-api
                otel-cli exec --name "install deps" -- npm ci
                otel-cli exec --name "unit tests" --attrs "ci.job=unit,git.sha=${GITHUB_SHA}" -- npm test
                otel-cli exec --name "docker build" -- docker buildx build -t api:ci .
            """, runnable=False),
            ex("Deploy annotation in Grafana", "intermediate", "Add a marker after a successful deploy.", "yaml", """
                - name: Annotate dashboards
                  if: success()
                  env:
                    GRAFANA_URL: ${{ vars.GRAFANA_URL }}
                    GRAFANA_TOKEN: ${{ secrets.GRAFANA_ANNOTATION_TOKEN }}
                  run: |
                    curl -fsS -X POST "$GRAFANA_URL/api/annotations" -H "Authorization: Bearer $GRAFANA_TOKEN" -H 'Content-Type: application/json' -d "{\\"tags\\":[\\"deploy\\",\\"api\\",\\"production\\"],\\"text\\":\\"api ${GITHUB_SHA::7} by ${GITHUB_ACTOR}\\"}"
            """, runnable=False),
            ex("Query run history", "basic", "Duration and conclusion of recent runs via gh.", "bash", """
                gh run list -w ci.yml -L 50 --json databaseId,conclusion,createdAt,updatedAt --jq '.[] | [.databaseId, .conclusion, .createdAt, .updatedAt] | @tsv'
                gh api repos/acme/api/actions/runs/123456/timing --jq '.run_duration_ms'
            """, runnable=False),
        ],
        ["gh run list --json conclusion,createdAt", "gh api .../actions/runs/ID/timing", "otel-cli exec --name step -- cmd", "Grafana /api/annotations", "Metrics: p95 duration, queue time, success %"],
        ["Only measuring total duration hides that most time is spent queued.", "Lumping all failures together hides that infrastructure, not code, causes most reds.", "Deploy events without commit SHAs cannot be correlated with incidents."],
        [
            qa("basic", "Why monitor CI/CD pipelines?", "Pipelines are critical to developer productivity and delivery. Monitoring duration, failures and queue time shows bottlenecks, flaky tests and infrastructure issues that slow everyone down."),
            qa("intermediate", "Which pipeline metrics matter most?", "End-to-end duration percentiles, queue time, success rate of main, failure categories, flaky test rate, cache hit rate and cost per run."),
            qa("intermediate", "What is a deployment marker?", "An annotation recorded on production dashboards at the time of a deploy, with service, version and author, so changes in metrics can be correlated with releases."),
            qa("advanced", "How can OpenTelemetry be applied to CI?", "Each pipeline run becomes a trace and each job and step a span with attributes like repository, branch and SHA. This lets you analyse critical paths, slow steps and failure hotspots with normal tracing tools."),
        ],
        ["dora-metrics", "flaky-tests", "cost-speed"],
        chain(
            ("Emit", "events, spans", "Collect", "CI emits webhooks, JUnit reports and OpenTelemetry spans."),
            ("Store", "metrics backend", "Ingest", "Events land in a metrics or tracing backend.", "events"),
            ("Dashboard", "p95, queue, %", "Visualise", "Dashboards show duration, queue time and success rate by workflow.", "data"),
            ("Alert", "main red", "Notify", "Alerts fire when main breaks or queue times spike.", "trend"),
            ("Fix", "slowest step", "Improve", "Teams target the biggest time or failure contributor.", "insight"),
        ),
    ),
    topic(
        "cost-speed", "Pipeline Cost & Speed Optimisation", "operations", "advanced", "CS",
        "Fast feedback for less money: cache, parallelise, skip, right-size and fail early.",
        "Running a delivery fleet: you do not send a lorry for every envelope, you keep vans fuelled and ready, send only what changed, and pick the right vehicle for each load.",
        "Pipeline speed directly affects developer productivity, and pipeline cost grows with every repository, matrix cell and minute. The biggest levers are usually: avoiding work (path filters, affected-only builds in monorepos, skipping docs-only changes, cancelling superseded runs), reusing work (dependency caches, remote build caches, Docker layer caches, prebuilt toolchain images), parallelising (job DAGs with needs, test sharding, matrices) and failing fast (lint and unit tests before slow suites). Right-sizing runners matters: a larger runner that halves duration can cost the same or less, and arm64 runners are often cheaper; macOS minutes are much more expensive than Linux. Self-hosted or autoscaling runners (Actions Runner Controller, GitLab runner autoscaling on spot instances) can cut cost at scale but add operational and security work. Timeouts prevent runaway jobs, and artifact retention settings control storage costs. Measure before optimising: look at the critical path, queue time and the most frequent and longest jobs, then fix the top items and watch the trend.",
        ["Cutting PR feedback from 25 to 8 minutes.", "Reducing a monthly CI bill by a third with caching and cancellations.", "Moving heavy builds to autoscaled spot runners."],
        [
            "Avoid work: path filters, affected builds, cancel superseded runs.",
            "Reuse work: caches for deps, builds and images.",
            "Parallelise along the critical path; fail fast first.",
            "Right-size runners; bigger can be cheaper per result.",
            "Set timeouts and artifact retention.",
        ],
        [
            ex("Speed-focused PR workflow", "intermediate", "Cancel old runs, skip docs, fast checks first, larger runner for the heavy job.", "yaml", """
                name: pr
                on:
                  pull_request:
                    paths-ignore: ["docs/**", "*.md"]
                permissions:
                  contents: read
                concurrency:
                  group: pr-${{ github.event.pull_request.number }}
                  cancel-in-progress: true
                jobs:
                  quick:
                    runs-on: ubuntu-latest
                    timeout-minutes: 5
                    steps:
                      - uses: actions/checkout@v4
                      - uses: actions/setup-node@v4
                        with: {node-version: 22, cache: npm}
                      - run: npm ci --prefer-offline && npm run lint && npm run test:unit
                  heavy:
                    needs: quick
                    runs-on: ubuntu-latest-8-cores
                    timeout-minutes: 20
                    strategy:
                      matrix:
                        shard: [1, 2, 3]
                    steps:
                      - uses: actions/checkout@v4
                      - uses: actions/setup-node@v4
                        with: {node-version: 22, cache: npm}
                      - run: npm ci --prefer-offline
                      - run: npx playwright test --shard=${{ matrix.shard }}/3
                      - uses: actions/upload-artifact@v4
                        if: failure()
                        with:
                          name: traces-${{ matrix.shard }}
                          path: test-results/
                          retention-days: 3
            """, runnable=False),
            ex("Find the expensive jobs", "basic", "Summarise billable time by workflow.", "bash", """
                gh api repos/acme/api/actions/workflows --jq '.workflows[] | [.id, .name] | @tsv'
                gh api repos/acme/api/actions/runs/123456/timing --jq '.billable'
                gh cache list --sort size_in_bytes --limit 10
            """, runnable=False),
        ],
        ["concurrency cancel-in-progress", "paths-ignore: docs/**", "timeout-minutes", "retention-days: 3", "Larger / arm64 runners"],
        ["Optimising a job that is not on the critical path does not shorten the pipeline.", "Caches that cost more to upload than they save make things slower.", "Spot runners without retry handling turn evictions into random failures."],
        [
            qa("basic", "What are the quickest wins for a slow pipeline?", "Cancel superseded runs, cache dependencies, run fast checks first, skip irrelevant changes with path filters and parallelise independent jobs."),
            qa("intermediate", "Can a bigger runner save money?", "Yes. If an 8-core runner finishes in a quarter of the time of a 2-core runner at four times the per-minute price, the cost is the same and feedback is faster; with better CPU utilisation it can be cheaper."),
            qa("intermediate", "What is the critical path of a pipeline?", "The longest chain of dependent jobs from start to finish. Only shortening jobs on it reduces total wall-clock time."),
            qa("advanced", "How would you reduce CI cost by 30 percent across an organisation?", "Measure billable minutes by repo and workflow, then target the top consumers with cancellation of superseded runs, affected-only builds, caching, right-sized or arm runners, shorter artifact retention and autoscaled spot-based self-hosted runners where security allows."),
        ],
        ["dependency-caching", "test-sharding", "monorepo-pipelines", "pipeline-observability"],
        chain(
            ("Measure", "p95, minutes", "Baseline", "Collect duration, queue time and billable minutes per workflow."),
            ("Avoid", "filters, cancel", "Skip work", "Skip irrelevant changes and cancel superseded runs.", "data"),
            ("Reuse", "caches", "Cache", "Cache dependencies, build outputs and image layers.", "less"),
            ("Parallel", "DAG, shards", "Parallelise", "Shorten the critical path with needs and sharding.", "faster"),
            ("Right-size", "runner types", "Tune", "Pick runner sizes and architectures by cost per result.", "cheaper"),
        ),
    ),
]

_BATCH_6 = [
    topic(
        "incident-postmortem", "Incident Response & Postmortems for Bad Deploys", "operations", "intermediate", "IP",
        "Detect, mitigate, communicate, then learn blamelessly and fix the pipeline gap.",
        "A fire brigade drill: put the fire out first, keep the neighbours informed, then walk through the building afterwards to see why it started and which alarm should have rung earlier.",
        "When a deployment causes an incident, response follows a predictable shape. Detection comes from alerts on SLOs, canary analysis or user reports; the deploy marker on dashboards often points at the culprit immediately. An incident commander coordinates, a communications lead updates status pages and stakeholders, and responders focus on mitigation first: rollback, flag off, scale up or failover, rather than debugging in production. A deploy freeze for the affected service avoids confounding changes while the incident is open. After recovery, a blameless postmortem reconstructs the timeline (deploy time, detection time, mitigation time), identifies contributing factors and asks why the pipeline let the change through: missing test, ineffective canary metric, migration not backwards compatible, alert too slow. Action items are specific, owned and tracked: add a contract test, add a canary metric, make migrations a separate step, shorten rollback time. Blameless does not mean no accountability; it means focusing on system improvements rather than individual fault, because people make reasonable decisions with the information and tools they have.",
        ["Handling a release that broke checkout for 10 percent of users.", "Writing a postmortem that leads to new canary metrics.", "Defining when on-call may roll back without asking."],
        [
            "Mitigate first (rollback, flag off), diagnose second.",
            "Roles: incident commander, comms, responders, scribe.",
            "Deploy markers and changelogs speed up correlation.",
            "Blameless postmortem with timeline and contributing factors.",
            "Action items close the pipeline gap that let the change through.",
        ],
        [
            ex("Freeze deploys for a service during an incident", "intermediate", "A repository variable checked by the deploy workflow.", "yaml", """
                jobs:
                  deploy:
                    runs-on: ubuntu-latest
                    environment: production
                    permissions:
                      contents: read
                    steps:
                      - name: Respect incident freeze
                        if: vars.DEPLOY_FREEZE == 'true'
                        run: |
                          echo "::error::Deploys frozen during an active incident (see incident channel)"
                          exit 1
                      - uses: actions/checkout@v4
                      - run: ./deploy.sh production "${GITHUB_SHA}"
            """, runnable=False),
            ex("First five minutes on a bad deploy", "basic", "What changed, roll back, freeze, confirm.", "bash", """
                gh run list -w deploy.yml -L 5                      # what deployed and when
                kubectl argo rollouts get rollout checkout          # current version and step
                kubectl argo rollouts abort checkout                # or: kubectl rollout undo deploy/checkout
                gh variable set DEPLOY_FREEZE --body true           # stop further deploys
                # watch error-rate dashboard until it returns to baseline, then post an update
            """, runnable=False),
            ex("Postmortem skeleton", "basic", "Sections of a blameless review.", "bash", """
                # Summary: impact, duration, customers affected
                # Timeline (UTC): 10:02 deploy v1.8.3 | 10:06 alert | 10:09 rollback | 10:14 recovered
                # Contributing factors: migration renamed column; canary lacked checkout-success metric
                # What went well / what was hard
                # Action items: [owner, due] add checkout metric to AnalysisTemplate; lint migrations for RENAME
            """, runnable=False),
        ],
        ["Mitigate: rollback / flag off", "gh variable set DEPLOY_FREEZE --body true", "Timeline: deploy, detect, mitigate, resolve", "Blameless: systems, not people", "Track action items to done"],
        ["Debugging in production while users suffer instead of rolling back first.", "Postmortems without owned action items repeat the same incident.", "Blame-focused reviews make people hide information next time."],
        [
            qa("basic", "What is the first priority when a deploy causes an incident?", "Restore service, usually by rolling back, disabling the feature flag or failing over, before investigating root cause."),
            qa("intermediate", "What is a blameless postmortem?", "A review of an incident that reconstructs what happened and why, focusing on system and process factors rather than individual blame, and produces concrete improvement actions."),
            qa("intermediate", "Which timestamps matter in a deploy incident timeline?", "When the change was deployed, when the problem began, when it was detected, when mitigation started and when service was restored. Their gaps show detection and recovery weaknesses."),
            qa("advanced", "How should a postmortem change the CI/CD pipeline?", "Ask which automated check could have caught the change earlier or limited its blast radius, then add it: a test, a migration lint, a canary metric, a faster rollback path or an alert. Track these as owned action items."),
        ],
        ["rollback-rollforward", "dora-metrics", "changelogs"],
        chain(
            ("Detect", "SLO alert", "Alert", "An SLO alert fires shortly after a deploy marker."),
            ("Mitigate", "rollback, flag", "Restore", "On-call rolls back or flips a flag; deploys are frozen.", "page"),
            ("Communicate", "status page", "Inform", "Stakeholders get regular updates until resolved.", "stable"),
            ("Review", "blameless", "Postmortem", "The team builds a timeline and contributing factors.", "resolved"),
            ("Improve", "action items", "Close gaps", "Owned actions add the missing test, metric or guardrail.", "actions"),
        ),
    ),
    topic(
        "secrets-in-ci", "Secrets in CI: Storage, Masking & Scope", "security", "intermediate", "SE",
        "Keep credentials out of code, scope them tightly, mask them in logs and prefer short-lived ones.",
        "Hotel key cards: each guest gets a card that opens only their room, only for their stay, and the front desk can cancel it instantly. Nobody gets a permanent master key taped under the reception desk.",
        "CI pipelines need credentials to pull dependencies, push artifacts and deploy, which makes them attractive targets. Secrets must never be committed to repositories, baked into images or printed in logs. CI platforms provide encrypted secret stores (GitHub repository, environment and organisation secrets; GitLab masked and protected variables; Jenkins credentials; Azure variable groups backed by Key Vault) that inject values at runtime and mask exact matches in logs. Masking is a last line of defence: transformed values (base64, URL-encoded, split strings) are not masked, so code should avoid echoing secrets at all. Scope is critical: environment-scoped secrets only reach deploy jobs that pass protection rules, protected variables only reach protected branches, and fork pull requests do not receive secrets. Better still is avoiding static secrets entirely with OIDC federation to cloud providers and dynamic secrets from Vault or cloud secret managers. Secret scanning (GitHub push protection, gitleaks, trufflehog) blocks accidental commits, and any leaked secret must be revoked and rotated immediately, because deleting the commit does not remove copies.",
        ["Keeping production deploy credentials available only to approved production jobs.", "Blocking a commit that contains a cloud key with push protection.", "Replacing static registry passwords with short-lived tokens."],
        [
            "Never in code, images or logs; inject at runtime only.",
            "Scope by environment and protected branch; forks get none.",
            "Masking only hides exact matches; do not echo or transform secrets.",
            "Prefer OIDC and dynamic secrets over long-lived keys.",
            "Leaked means revoke and rotate, not just delete the commit.",
        ],
        [
            ex("Environment-scoped secret, never echoed", "intermediate", "Secret passed through env to a tool that reads it; mask derived values.", "yaml", """
                jobs:
                  publish:
                    runs-on: ubuntu-latest
                    environment: release
                    permissions:
                      contents: read
                    steps:
                      - uses: actions/checkout@v4
                      - name: Configure registry auth
                        env:
                          REGISTRY_TOKEN: ${{ secrets.REGISTRY_TOKEN }}
                        run: |
                          AUTH=$(printf 'ci:%s' "$REGISTRY_TOKEN" | base64 -w0)
                          echo "::add-mask::$AUTH"
                          printf '{"auths":{"registry.example.com":{"auth":"%s"}}}' "$AUTH" > "$RUNNER_TEMP/config.json"
                      - run: DOCKER_CONFIG="$RUNNER_TEMP" docker push registry.example.com/app:${{ github.sha }}
            """, runnable=False),
            ex("Secret scanning in CI and pre-commit", "basic", "Scan history and block new leaks.", "bash", """
                gitleaks detect --source . --redact --exit-code 1
                gitleaks protect --staged --redact            # pre-commit hook
                trufflehog git file://. --only-verified --fail
                # placeholder values used in docs and tests:
                # API_TOKEN=EXAMPLE-ONLY-not-a-real-secret
            """, runnable=False),
            ex("GitLab protected and masked variable usage", "intermediate", "Variable only available on protected branches; file type for credentials.", "yaml", """
                deploy:
                  stage: deploy
                  rules:
                    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
                  environment: production
                  script:
                    - test -n "$DEPLOY_KUBECONFIG"   # File-type, protected, masked variable
                    - kubectl --kubeconfig "$DEPLOY_KUBECONFIG" apply -k overlays/prod
            """, runnable=False),
        ],
        ["${{ secrets.NAME }} (never echo)", "echo '::add-mask::value'", "gitleaks detect --redact", "gh secret set NAME --env production", "Rotate on any leak"],
        ["set -x in scripts prints expanded commands, including secrets passed as arguments.", "Base64 or JSON-encoded secrets are not masked automatically.", "Secrets passed as CLI arguments are visible in process listings on shared runners.", "pull_request_target with checkout of fork code can expose secrets."],
        [
            qa("basic", "Where should CI secrets be stored?", "In the CI platform's encrypted secret store or an external secret manager, scoped to the environments and branches that need them, and injected at runtime. Never in the repository or in images."),
            qa("intermediate", "Is log masking enough to protect secrets?", "No. It only redacts exact matches of registered values; encoded or partial values leak, and malicious steps can exfiltrate secrets over the network. Avoid printing secrets, limit scope and prefer short-lived credentials."),
            qa("intermediate", "Why do fork pull requests not get secrets?", "Fork PR code is untrusted and could print or send secrets anywhere. GitHub and GitLab withhold secrets and give a read-only token to such runs."),
            qa("advanced", "A secret was committed and pushed. What do you do?", "Revoke and rotate it immediately at the provider, check its audit logs for misuse, then remove it from history if needed and add scanning or push protection to prevent recurrence. Rewriting history alone is insufficient because clones, forks and caches keep copies."),
        ],
        ["oidc-federation", "gha-environments", "runner-security"],
        chain(
            ("Store", "encrypted", "Secret store", "The secret lives encrypted in the CI store or a secret manager."),
            ("Scope", "env, branch", "Restrict", "It is bound to an environment or protected branch.", "secret"),
            ("Inject", "runtime env", "Use", "Only the approved job receives it as an environment variable.", "allowed"),
            ("Mask", "log redaction", "Hide", "Logs redact exact values; scripts never echo them.", "value"),
            ("Rotate", "short-lived", "Expire", "Values are rotated regularly or replaced with OIDC tokens.", "expiry"),
        ),
    ),
    topic(
        "oidc-federation", "OIDC Federation from CI to Cloud", "security", "advanced", "OI",
        "Exchange a short-lived CI identity token for cloud credentials; store no keys at all.",
        "A visitor badge printed at reception after checking your ID, valid only for one floor and only until 6 pm. You never carry a permanent key, so there is nothing to lose or copy.",
        "OpenID Connect federation lets a CI job prove its identity to a cloud provider without stored credentials. The CI platform acts as an identity provider: GitHub Actions issues a signed JWT (when the job has permissions: id-token: write) with claims such as iss (https://token.actions.githubusercontent.com), aud, sub (repo:acme/api:ref:refs/heads/main or repo:acme/api:environment:production), repository, ref, workflow and job_workflow_ref. The cloud is configured to trust that issuer: an AWS IAM OIDC provider plus a role whose trust policy conditions match sub and aud; a GCP Workload Identity Pool and provider with an attribute condition; or an Azure federated identity credential on an app registration or managed identity. The job exchanges the token (AssumeRoleWithWebIdentity, STS token exchange) for credentials valid for minutes to an hour. Security depends on tight trust conditions: always match the exact repository and, for production, the environment or protected ref; a wildcard like repo:acme/* lets any repository in the organisation assume the role. GitLab (id_tokens), CircleCI, Azure DevOps, Buildkite and Jenkins (via plugins) support the same pattern.",
        ["Deploying to AWS from GitHub Actions without access keys.", "Separate plan and apply roles for Terraform tied to branch and environment.", "Pushing to Google Artifact Registry from GitLab CI."],
        [
            "Job requests a signed OIDC token; cloud exchanges it for short-lived creds.",
            "Trust policy must pin aud and an exact sub (repo plus ref or environment).",
            "Never use wildcards across repositories for privileged roles.",
            "permissions: id-token: write is required in GitHub Actions.",
            "Removes long-lived keys from CI entirely.",
        ],
        [
            ex("AWS role trust policy for one repo and environment", "advanced", "Only production-environment jobs in acme/api can assume this role.", "json", """
                {
                  "Version": "2012-10-17",
                  "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"Federated": "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com"},
                    "Action": "sts:AssumeRoleWithWebIdentity",
                    "Condition": {
                      "StringEquals": {
                        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
                        "token.actions.githubusercontent.com:sub": "repo:acme/api:environment:production"
                      }
                    }
                  }]
                }
            """, runnable=False),
            ex("Workflow assuming the role", "intermediate", "No access keys anywhere; credentials last one hour.", "yaml", """
                name: deploy
                on:
                  push:
                    branches: [main]
                permissions:
                  contents: read
                  id-token: write
                jobs:
                  deploy:
                    runs-on: ubuntu-latest
                    environment: production
                    steps:
                      - uses: actions/checkout@v4
                      - uses: aws-actions/configure-aws-credentials@v4
                        with:
                          role-to-assume: arn:aws:iam::123456789012:role/gha-api-prod-deploy
                          aws-region: eu-west-1
                          role-session-name: gha-${{ github.run_id }}
                          role-duration-seconds: 3600
                      - run: aws sts get-caller-identity
                      - run: ./deploy.sh production
            """, runnable=False),
            ex("GCP Workload Identity Federation with Terraform", "advanced", "Provider restricted to one repository via attribute condition.", "hcl", """
                resource "google_iam_workload_identity_pool" "ci" {
                  workload_identity_pool_id = "github-ci"
                }

                resource "google_iam_workload_identity_pool_provider" "github" {
                  workload_identity_pool_id          = google_iam_workload_identity_pool.ci.workload_identity_pool_id
                  workload_identity_pool_provider_id = "github"
                  attribute_mapping = {
                    "google.subject"       = "assertion.sub"
                    "attribute.repository" = "assertion.repository"
                    "attribute.ref"        = "assertion.ref"
                  }
                  attribute_condition = "assertion.repository == 'acme/api' && assertion.ref == 'refs/heads/main'"
                  oidc {
                    issuer_uri = "https://token.actions.githubusercontent.com"
                  }
                }

                resource "google_service_account_iam_member" "deployer" {
                  service_account_id = google_service_account.deployer.name
                  role               = "roles/iam.workloadIdentityUser"
                  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.ci.name}/attribute.repository/acme/api"
                }
            """, runnable=False),
        ],
        ["permissions: id-token: write", "aws-actions/configure-aws-credentials role-to-assume", "google-github-actions/auth workload_identity_provider", "azure/login with client-id (federated)", "sub: repo:ORG/REPO:environment:ENV"],
        ["A trust condition of repo:acme/* lets every repo in the org assume the role.", "Matching only aud without sub lets any GitHub repository in the world assume it.", "Pull request jobs can request tokens too; restrict privileged roles to protected refs or environments."],
        [
            qa("basic", "What problem does OIDC federation solve in CI?", "It removes long-lived cloud credentials from CI. Jobs get short-lived credentials by presenting a signed identity token that the cloud trusts, so there are no static keys to leak or rotate."),
            qa("intermediate", "Which claims should a trust policy check?", "The issuer via the configured provider, the audience (aud), and the subject (sub) pinned to the exact repository plus a protected branch, tag or environment. Additional claims like job_workflow_ref can restrict to specific reusable workflows."),
            qa("intermediate", "What GitHub Actions setting is required?", "The job or workflow must grant permissions: id-token: write so the runner can request an OIDC token from GitHub's token endpoint."),
            qa("advanced", "How would an attacker abuse a weak OIDC trust policy?", "If the subject condition uses wildcards or is missing, any repository or branch matching it, including a fork-created branch or an unrelated repo in the org, can request a token and assume the role. They could then deploy or read data with that role's permissions."),
        ],
        ["secrets-in-ci", "gha-environments", "iac-in-ci"],
        chain(
            ("Request", "id-token: write", "Ask for token", "The job asks GitHub's OIDC endpoint for a signed JWT."),
            ("JWT", "sub, aud, repo", "Identity token", "The token states which repo, ref and environment the job runs for.", "claims"),
            ("Exchange", "STS / WIF", "Present", "The job presents the JWT to the cloud's token service.", "jwt"),
            ("Verify", "trust policy", "Check claims", "The cloud verifies the signature and matches aud and sub conditions.", "jwt"),
            ("Creds", "1 hour", "Short-lived", "Temporary credentials are returned; they expire automatically.", "creds"),
        ),
    ),
    topic(
        "supply-chain-slsa", "Supply-Chain Security & SLSA Provenance", "security", "advanced", "SL",
        "Prove where an artifact came from and that its build was not tampered with.",
        "A food traceability label: which farm, which batch, which factory, which inspector. If something is contaminated, you can trace it, and fake products without a verifiable label are refused at the shop door.",
        "Software supply-chain attacks target the path from source to production: compromised dependencies, malicious build steps, stolen credentials, tampered artifacts in registries. SLSA (Supply-chain Levels for Software Artifacts) is a framework of incremental requirements, with the v1.0 build track defining levels: Build L1 requires provenance describing how the artifact was built; L2 requires a hosted build platform that signs the provenance; L3 requires a hardened build platform where builds are isolated from each other and signing keys are inaccessible to the build's user-defined steps. Provenance is an in-toto attestation stating the artifact digest (subject), the builder identity, the source repository and commit, and the build parameters. Consumers verify provenance at deploy time, for example with slsa-verifier, cosign verify-attestation, gh attestation verify or a Kubernetes admission policy (Kyverno, Sigstore policy-controller), and reject artifacts built from unexpected repositories or workflows. SLSA complements other controls: SBOMs list contents, signing proves integrity and identity, dependency pinning and scanning reduce risky inputs, and branch protection and two-person review protect the source.",
        ["Generating signed provenance for every release image.", "Rejecting images not built by the official release workflow.", "Meeting customer or regulatory supply-chain requirements."],
        [
            "Threats span source, build, dependencies and distribution.",
            "SLSA build levels: L1 provenance, L2 signed hosted, L3 hardened isolated.",
            "Provenance = in-toto attestation binding digest to source and builder.",
            "Verify provenance at deploy or admission time, not just generate it.",
            "Combine with SBOMs, signing, pinning and review.",
        ],
        [
            ex("GitHub artifact attestations for an image", "advanced", "Generate signed build provenance bound to the image digest.", "yaml", """
                jobs:
                  release:
                    runs-on: ubuntu-latest
                    permissions:
                      contents: read
                      packages: write
                      id-token: write
                      attestations: write
                    steps:
                      - uses: actions/checkout@v4
                      - uses: docker/login-action@v3
                        with:
                          registry: ghcr.io
                          username: ${{ github.actor }}
                          password: ${{ secrets.GITHUB_TOKEN }}
                      - id: push
                        uses: docker/build-push-action@v6
                        with:
                          push: true
                          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
                      - uses: actions/attest-build-provenance@v2
                        with:
                          subject-name: ghcr.io/${{ github.repository }}
                          subject-digest: ${{ steps.push.outputs.digest }}
                          push-to-registry: true
            """, runnable=False),
            ex("Verify provenance before deploy", "intermediate", "Accept only artifacts built by the expected repo and workflow.", "bash", """
                gh attestation verify oci://ghcr.io/acme/api@sha256:EXAMPLE-DIGEST --repo acme/api --signer-workflow acme/api/.github/workflows/release.yml
                slsa-verifier verify-image ghcr.io/acme/api@sha256:EXAMPLE-DIGEST --source-uri github.com/acme/api --source-tag v1.5.0
            """, runnable=False),
        ],
        ["actions/attest-build-provenance", "gh attestation verify oci://img --repo O/R", "slsa-verifier verify-image", "cosign verify-attestation --type slsaprovenance", "in-toto subject = artifact sha256"],
        ["Generating provenance that nobody verifies adds no protection.", "Provenance from a build where user steps can access the signing key is not L3.", "Verifying signature but not the builder identity accepts artifacts signed by anyone with a valid certificate."],
        [
            qa("basic", "What is SLSA?", "Supply-chain Levels for Software Artifacts, a framework of incremental security requirements for how software is built and how its provenance is generated and verified."),
            qa("intermediate", "What is build provenance?", "A signed attestation that records the artifact digest, the build platform and workflow that produced it, the source repository and commit, and build parameters, allowing consumers to verify where it came from."),
            qa("intermediate", "What distinguishes SLSA Build L3?", "A hardened build platform where runs are isolated from one another and the provenance signing material is not accessible to user-defined build steps, so a malicious build step cannot forge provenance."),
            qa("advanced", "How do you enforce provenance in Kubernetes?", "Use an admission controller such as Kyverno verifyImages or Sigstore policy-controller with a policy requiring a valid attestation whose subject matches the image digest and whose builder and source match expected values. Unverified images are rejected at deploy time."),
        ],
        ["signing-cosign", "sbom", "build-systems", "dependency-pinning"],
        chain(
            ("Source", "reviewed commit", "Trusted source", "A reviewed commit on a protected branch starts the release."),
            ("Build", "hosted, isolated", "Trusted build", "An isolated hosted runner builds the artifact.", "sha"),
            ("Attest", "in-toto", "Provenance", "The platform signs provenance binding digest, source and workflow.", "digest"),
            ("Publish", "registry", "Store", "Artifact and attestation are pushed together.", "attestation"),
            ("Verify", "admission", "Enforce", "Deploy-time policy accepts only artifacts with matching provenance.", "pull"),
        ),
    ),
    topic(
        "sbom", "Software Bill of Materials (SBOM)", "security", "intermediate", "SB",
        "A machine-readable inventory of every component inside an artifact.",
        "The ingredient list on a food package. When a recall is announced for a particular batch of peanuts, you can check every product's label in seconds instead of opening every box.",
        "An SBOM lists the components (libraries, packages, OS packages) that make up a piece of software, with names, versions, package URLs (purl), licenses, hashes and dependency relationships. The two main formats are SPDX (an ISO standard, strong on licensing) and CycloneDX (OWASP, strong on security use cases including VEX). In CI, tools such as Syft, Trivy, cdxgen, BuildKit (--sbom) or language plugins generate an SBOM from the built artifact, ideally the final container image rather than just the source tree, because the image contains OS packages and transitive dependencies. The SBOM is stored alongside the artifact, often as a signed attestation in the registry, and ingested into systems like Dependency-Track or a vulnerability management platform. When a new CVE is published (Log4Shell is the classic example), the organisation queries its SBOMs to find every affected artifact and deployment within minutes. VEX documents complement SBOMs by stating whether a listed vulnerable component is actually exploitable in that product. SBOMs are increasingly required by regulation and customers, such as US federal procurement and the EU Cyber Resilience Act.",
        ["Finding every service that ships a vulnerable library version within an hour.", "Providing customers with SBOMs for compliance.", "License compliance checks on all dependencies."],
        [
            "Formats: SPDX and CycloneDX; identify packages by purl.",
            "Generate from the final artifact, not only the source manifest.",
            "Attach SBOMs to artifacts as signed attestations.",
            "Feed SBOMs to Dependency-Track or a vuln platform for continuous matching.",
            "VEX states whether a known vulnerability is actually exploitable.",
        ],
        [
            ex("Generate, attest and scan an SBOM", "intermediate", "Syft for CycloneDX, cosign attestation, Grype scan of the SBOM.", "bash", """
                IMG=ghcr.io/acme/api@sha256:EXAMPLE-DIGEST
                syft "$IMG" -o cyclonedx-json > sbom.cdx.json
                cosign attest --yes --type cyclonedx --predicate sbom.cdx.json "$IMG"
                grype sbom:sbom.cdx.json --fail-on high
                jq -r '.components[] | select(.name=="log4j-core") | "\\(.name) \\(.version)"' sbom.cdx.json
            """, runnable=False),
            ex("SBOM in a GitHub workflow", "intermediate", "Generate an SPDX SBOM for the pushed image and upload it.", "yaml", """
                - uses: anchore/sbom-action@v0
                  with:
                    image: ghcr.io/${{ github.repository }}@${{ steps.push.outputs.digest }}
                    format: spdx-json
                    output-file: sbom.spdx.json
                - uses: actions/attest-sbom@v2
                  with:
                    subject-name: ghcr.io/${{ github.repository }}
                    subject-digest: ${{ steps.push.outputs.digest }}
                    sbom-path: sbom.spdx.json
                    push-to-registry: true
            """, runnable=False),
        ],
        ["syft IMG -o cyclonedx-json", "trivy image --format spdx-json IMG", "grype sbom:sbom.json", "cosign attest --type cyclonedx", "docker buildx build --sbom=true"],
        ["SBOMs from source manifests miss OS packages and vendored code in the image.", "An SBOM that is generated but never stored or queried has no value.", "Unsigned SBOMs can be swapped; attach them as signed attestations."],
        [
            qa("basic", "What is an SBOM?", "A machine-readable list of all components in a piece of software, with versions, identifiers, licenses and relationships, used for vulnerability and license management."),
            qa("intermediate", "SPDX vs CycloneDX?", "Both are standard SBOM formats. SPDX is an ISO standard with deep licensing support; CycloneDX from OWASP focuses on security use cases and supports VEX and services. Most tools can produce both."),
            qa("intermediate", "Why generate the SBOM from the container image?", "The image includes OS packages, transitive dependencies and anything copied in during the build, which source manifests do not show. The SBOM should describe what actually runs."),
            qa("advanced", "How do SBOMs help during a zero-day like Log4Shell?", "With SBOMs for every artifact ingested into a central system, you can query which images contain the affected package and version, map them to running deployments and prioritise patches in minutes rather than scanning everything from scratch."),
        ],
        ["supply-chain-slsa", "security-scanning", "signing-cosign"],
        chain(
            ("Build", "final image", "Artifact", "The pipeline builds the final container image."),
            ("Generate", "syft / trivy", "Inventory", "An SBOM lists every package, version and purl in the image.", "image"),
            ("Attest", "signed", "Bind", "The SBOM is attached as a signed attestation to the digest.", "sbom"),
            ("Ingest", "Dependency-Track", "Catalogue", "SBOMs are ingested centrally and matched to new CVEs.", "attested"),
            ("Respond", "query affected", "Act", "When a CVE appears, affected artifacts are found instantly.", "alert"),
        ),
    ),
    topic(
        "signing-cosign", "Artifact Signing with Sigstore & cosign", "security", "advanced", "SG",
        "Sign images by digest with keyless OIDC identities and verify them before deploy.",
        "A wax seal pressed with a ring that proves who sent the letter. Sigstore is like a notary who issues a one-day ring after checking your ID and records every seal in a public ledger.",
        "Signing proves that an artifact was produced by a specific identity and has not been altered. Sigstore provides the tooling: cosign signs and verifies container images and other OCI artifacts, Fulcio is a certificate authority that issues short-lived certificates bound to an OIDC identity (a person's email or a CI workflow identity), and Rekor is a transparency log that records signatures so they can be audited. In keyless signing, a CI job uses its OIDC token to get a certificate valid for about ten minutes, signs the image digest, and the signature, certificate and Rekor entry are stored with the image; there is no long-lived private key to protect. Verification checks the signature, the certificate chain, the transparency log inclusion and, critically, the identity: certificate-identity (for GitHub, the workflow path and ref) and certificate-oidc-issuer. Key-based signing with a KMS-held ECDSA P-256 key is also supported for air-gapped or policy reasons. Always sign and verify digests, not tags. Enforcement happens at admission with Sigstore policy-controller, Kyverno or Connaisseur, so unsigned or wrongly signed images never run.",
        ["Signing every release image in CI without managing keys.", "Blocking unsigned images in production clusters.", "Verifying third-party images come from the expected publisher."],
        [
            "Keyless: OIDC identity -> Fulcio short-lived cert -> sign -> Rekor log.",
            "Verify both the signature and the signer identity and issuer.",
            "Sign and reference digests, never mutable tags.",
            "KMS-backed ECDSA P-256 keys for key-based signing.",
            "Enforce verification at admission time.",
        ],
        [
            ex("Keyless signing in GitHub Actions", "advanced", "Sign the pushed digest using the workflow's OIDC identity.", "yaml", """
                jobs:
                  sign:
                    needs: build
                    runs-on: ubuntu-latest
                    permissions:
                      contents: read
                      packages: write
                      id-token: write
                    steps:
                      - uses: sigstore/cosign-installer@v3
                      - uses: docker/login-action@v3
                        with:
                          registry: ghcr.io
                          username: ${{ github.actor }}
                          password: ${{ secrets.GITHUB_TOKEN }}
                      - run: cosign sign --yes "ghcr.io/${{ github.repository }}@${{ needs.build.outputs.digest }}"
            """, runnable=False),
            ex("Verify identity and issuer", "intermediate", "Accept only signatures from the release workflow on main.", "bash", """
                cosign verify ghcr.io/acme/api@sha256:EXAMPLE-DIGEST --certificate-identity "https://github.com/acme/api/.github/workflows/release.yml@refs/heads/main" --certificate-oidc-issuer "https://token.actions.githubusercontent.com" | jq '.[0].critical.image'
                cosign tree ghcr.io/acme/api@sha256:EXAMPLE-DIGEST
            """, runnable=False),
            ex("Kyverno policy requiring signatures", "advanced", "Reject pods whose images are not signed by the expected workflow.", "yaml", """
                apiVersion: kyverno.io/v1
                kind: ClusterPolicy
                metadata:
                  name: require-signed-images
                spec:
                  validationFailureAction: Enforce
                  webhookTimeoutSeconds: 15
                  rules:
                    - name: verify-acme-images
                      match:
                        any:
                          - resources:
                              kinds: [Pod]
                      verifyImages:
                        - imageReferences: ["ghcr.io/acme/*"]
                          mutateDigest: true
                          attestors:
                            - entries:
                                - keyless:
                                    issuer: https://token.actions.githubusercontent.com
                                    subject: "https://github.com/acme/*/.github/workflows/release.yml@refs/heads/main"
                                    rekor:
                                      url: https://rekor.sigstore.dev
            """, runnable=False),
        ],
        ["cosign sign --yes img@sha256:...", "cosign verify --certificate-identity ... --certificate-oidc-issuer ...", "cosign tree img", "cosign generate-key-pair --kms awskms:///alias/cosign", "Kyverno verifyImages / policy-controller"],
        ["Signing by tag can sign a different image than intended if the tag moved.", "cosign verify without identity flags is rejected for keyless; loose regexps accept any repo.", "Admission webhooks with failurePolicy Ignore let unsigned images through during outages."],
        [
            qa("basic", "Why sign container images?", "To let consumers verify the image was produced by a trusted identity and has not been modified since signing, preventing tampered or rogue images from being deployed."),
            qa("intermediate", "What is keyless signing in Sigstore?", "The signer authenticates with OIDC, Fulcio issues a short-lived certificate tied to that identity, cosign signs the digest, and the event is logged in Rekor. No long-lived private key exists to steal."),
            qa("intermediate", "What must a verifier check?", "The signature over the exact digest, the certificate chain to Fulcio, inclusion in the Rekor log, and that the certificate identity and OIDC issuer match the expected signer, such as a specific workflow on main."),
            qa("advanced", "How do you enforce signatures in Kubernetes?", "Deploy an admission controller (Sigstore policy-controller or Kyverno verifyImages) with policies that require valid signatures from expected identities for matching image references, rewrite tags to digests and fail closed."),
        ],
        ["supply-chain-slsa", "sbom", "artifacts-registries", "oidc-federation"],
        chain(
            ("OIDC", "workflow identity", "Authenticate", "The CI job obtains an OIDC token for its workflow identity."),
            ("Fulcio", "10-min cert", "Certificate", "Fulcio issues a short-lived certificate bound to that identity.", "token"),
            ("Sign", "image digest", "Sign", "cosign signs the image digest and pushes the signature.", "cert"),
            ("Rekor", "transparency", "Log", "The signature is recorded in the public transparency log.", "sig"),
            ("Verify", "admission", "Enforce", "The cluster verifies identity, issuer and log entry before running.", "entry"),
        ),
    ),
    topic(
        "dependency-pinning", "Dependency Pinning, Lockfiles & Update Bots", "security", "intermediate", "DP",
        "Pin exact versions and hashes, then update deliberately through automated PRs.",
        "Ordering parts by exact catalogue number and batch, not 'any bolt about this size'. When the supplier changes the bolt, you get a notice and test it before it goes into the car.",
        "Floating dependencies (^1.2.0, latest, unpinned base images, actions@main) mean a build can change without any change in your repository, which breaks reproducibility and opens the door to supply-chain attacks such as hijacked maintainer accounts, typosquatting and dependency confusion. Pinning fixes inputs: lockfiles (package-lock.json, pnpm-lock.yaml, poetry.lock, uv.lock, Cargo.lock, go.sum) record exact resolved versions with integrity hashes (SHA-512 or SHA-256), and CI must install from them strictly (npm ci, pnpm install --frozen-lockfile, pip install --require-hashes, uv sync --locked). Container base images are pinned by digest, and GitHub Actions by full commit SHA. Pinning without updating creates a different risk, stale vulnerable dependencies, so update bots (Dependabot, Renovate) open PRs with changelogs, grouped and scheduled, which CI tests like any change; automerge can be enabled for low-risk patch updates with good test coverage. Private package names should be reserved or scoped, and registries configured so internal names cannot resolve from public registries. Minimum release age settings reduce exposure to freshly published malicious versions.",
        ["Locking Python dependencies with hashes for reproducible installs.", "Pinning GitHub Actions to commit SHAs with Renovate keeping them fresh.", "Preventing dependency confusion for internal package names."],
        [
            "Lockfiles with integrity hashes; install strictly in CI.",
            "Pin base images by digest and actions by commit SHA.",
            "Update bots turn upgrades into small tested PRs.",
            "Scope or reserve internal package names to stop dependency confusion.",
            "Consider a minimum release age before adopting new versions.",
        ],
        [
            ex("Renovate config", "intermediate", "Group minor updates, pin action digests, automerge safe patches.", "json", """
                {
                  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
                  "extends": ["config:recommended", "helpers:pinGitHubActionDigests", "docker:pinDigests"],
                  "schedule": ["before 6am on monday"],
                  "minimumReleaseAge": "3 days",
                  "packageRules": [
                    {"matchUpdateTypes": ["minor", "patch"], "groupName": "non-major dependencies"},
                    {"matchUpdateTypes": ["patch"], "matchCurrentVersion": "!/^0/", "automerge": true},
                    {"matchUpdateTypes": ["major"], "dependencyDashboardApproval": true}
                  ]
                }
            """, runnable=False),
            ex("Strict installs with hashes", "basic", "Fail if anything differs from the lockfile.", "bash", """
                npm ci
                pnpm install --frozen-lockfile
                uv pip compile requirements.in --generate-hashes -o requirements.txt
                pip install --require-hashes -r requirements.txt
                go mod verify
            """, runnable=False),
            ex("Dependabot for actions and Docker", "basic", "Weekly update PRs for ecosystems the bot should watch.", "yaml", """
                version: 2
                updates:
                  - package-ecosystem: github-actions
                    directory: /
                    schedule: {interval: weekly}
                  - package-ecosystem: docker
                    directory: /
                    schedule: {interval: weekly}
                  - package-ecosystem: npm
                    directory: /
                    schedule: {interval: weekly}
                    groups:
                      minor-and-patch:
                        update-types: [minor, patch]
            """, runnable=False),
        ],
        ["npm ci · pnpm install --frozen-lockfile", "pip install --require-hashes -r req.txt", "FROM image@sha256:<digest>", "uses: owner/action@<full-sha> # vX.Y.Z", "renovate: minimumReleaseAge"],
        ["Pinning but never updating leaves known CVEs in production.", "npm install in CI can rewrite the lockfile and pull new versions.", "Automerging major updates without tests is a fast path to outages.", "Internal package names without scopes can be hijacked from public registries."],
        [
            qa("basic", "Why use lockfiles?", "They record the exact resolved versions and integrity hashes of all direct and transitive dependencies so every install, locally and in CI, gets identical packages."),
            qa("intermediate", "What is dependency confusion?", "An attack where a public package is published with the same name as an internal one, and a misconfigured resolver picks the public version. Prevent it with scoped names, registry configuration that pins internal names to the private registry, and reserved public names."),
            qa("intermediate", "Why pin GitHub Actions to a SHA?", "Version tags are mutable and can be repointed to malicious code if the action repository is compromised. A full commit SHA is immutable; bots keep the pins updated with the version shown in a comment."),
            qa("advanced", "How do you balance pinning with staying patched?", "Pin everything for reproducibility, then automate updates with Renovate or Dependabot on a schedule, group low-risk updates, automerge patches when tests are strong, require review for majors and use a minimum release age to avoid brand-new malicious releases."),
        ],
        ["security-scanning", "build-systems", "supply-chain-slsa"],
        chain(
            ("Resolve", "lockfile", "Pin", "Dependencies resolve once and are recorded with hashes."),
            ("Install", "strict mode", "Verify", "CI installs strictly from the lockfile and checks hashes.", "lock"),
            ("Bot", "Renovate PR", "Propose update", "An update bot opens a PR for a new version with release notes.", "new"),
            ("Test", "full CI", "Validate", "The update runs through the normal pipeline and scans.", "PR"),
            ("Merge", "auto or review", "Adopt", "Safe patches automerge; majors get human review.", "green"),
        ),
    ),
    topic(
        "security-scanning", "SCA, SAST & DAST in Pipelines", "security", "intermediate", "SC",
        "Automated scanners for vulnerable dependencies, insecure code and running-app weaknesses.",
        "Three inspectors for a new building: one checks the materials delivered (SCA), one reviews the blueprints for design flaws (SAST), and one walks around the finished building trying doors and windows (DAST).",
        "Security scanning in CI shifts detection earlier and makes it continuous. Software Composition Analysis (SCA) matches dependencies and their versions against vulnerability databases (OSV, GitHub Advisory, NVD) using tools like Dependabot alerts, Trivy, Grype, OSV-Scanner, Snyk or npm audit, and also checks licenses. Static Application Security Testing (SAST) analyses source code for insecure patterns such as injection, unsafe deserialisation and hardcoded credentials with CodeQL, Semgrep, SonarQube or language linters like Bandit and gosec. Secret scanning finds leaked credentials. Infrastructure-as-code and container config scanning (Checkov, Trivy config, kube-linter) find misconfigurations. Dynamic Application Security Testing (DAST) attacks a running application, usually a preview or staging deployment, with tools such as OWASP ZAP or Burp, finding issues like missing security headers, injection and auth flaws that static tools miss. Results should be uploaded in SARIF to a central view (GitHub code scanning) and triaged. Gate policy is a balance: block on new critical and high findings with fixes available, report the rest, and avoid noisy rules that teach developers to ignore the scanner.",
        ["Blocking a PR that introduces a dependency with a critical CVE.", "Finding SQL injection patterns with CodeQL before merge.", "Running a ZAP baseline scan against every preview environment."],
        [
            "SCA: known-vulnerable dependencies and licenses.",
            "SAST: insecure code patterns in source.",
            "DAST: attacks the running app; needs a deployed environment.",
            "Upload SARIF for a central, triaged view.",
            "Gate on new, fixable critical/high findings to keep signal high.",
        ],
        [
            ex("CodeQL, Semgrep and Trivy in one workflow", "intermediate", "SARIF uploaded to code scanning; Trivy fails on fixable criticals.", "yaml", """
                name: security
                on:
                  pull_request:
                  push:
                    branches: [main]
                permissions:
                  contents: read
                  security-events: write
                jobs:
                  codeql:
                    runs-on: ubuntu-latest
                    steps:
                      - uses: actions/checkout@v4
                      - uses: github/codeql-action/init@v3
                        with:
                          languages: python, javascript
                      - uses: github/codeql-action/analyze@v3
                  semgrep:
                    runs-on: ubuntu-latest
                    container: semgrep/semgrep
                    steps:
                      - uses: actions/checkout@v4
                      - run: semgrep scan --config p/default --sarif --output semgrep.sarif --error
                      - uses: github/codeql-action/upload-sarif@v3
                        if: always()
                        with:
                          sarif_file: semgrep.sarif
                  sca:
                    runs-on: ubuntu-latest
                    steps:
                      - uses: actions/checkout@v4
                      - uses: aquasecurity/trivy-action@0.28.0
                        with:
                          scan-type: fs
                          severity: CRITICAL,HIGH
                          ignore-unfixed: true
                          exit-code: "1"
            """, runnable=False),
            ex("ZAP baseline against a preview environment", "intermediate", "Passive DAST scan; fails on warnings configured as failures.", "bash", """
                docker run --rm -v "$PWD:/zap/wrk" ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t "https://pr-482.preview.example.com" -c zap-rules.conf -r zap-report.html -I
                osv-scanner scan source -r .
                npm audit --audit-level=high
            """, runnable=False),
        ],
        ["trivy fs --severity CRITICAL,HIGH --exit-code 1 .", "semgrep scan --config p/default --error", "osv-scanner scan source -r .", "zap-baseline.py -t URL", "upload-sarif (security-events: write)"],
        ["Failing on every finding, including unfixable ones, leads teams to disable scanners.", "DAST against production without coordination can trigger alarms or modify data.", "SAST without triage produces thousands of ignored alerts."],
        [
            qa("basic", "What is the difference between SAST, DAST and SCA?", "SAST analyses source code for insecure patterns without running it; DAST tests a running application from the outside; SCA identifies third-party components and their known vulnerabilities and licenses."),
            qa("intermediate", "Where does each scan fit in the pipeline?", "SAST, SCA and secret scanning run on every PR because they only need source. Image scanning runs after the build. DAST runs against a deployed preview or staging environment."),
            qa("intermediate", "What is SARIF?", "Static Analysis Results Interchange Format, a JSON standard for scanner results. Uploading SARIF lets platforms like GitHub show findings in a single code-scanning view with deduplication and triage."),
            qa("advanced", "How do you set a gating policy that developers respect?", "Block only on new findings above a severity threshold with a fix available, report the rest, tune or suppress noisy rules with justification, and give fast feedback with clear remediation guidance. Track exceptions with expiry dates."),
        ],
        ["dependency-pinning", "sbom", "approvals-gates", "container-builds"],
        chain(
            ("Source", "PR opened", "Code", "A pull request triggers source-level scans."),
            ("SAST", "CodeQL/Semgrep", "Code patterns", "Static analysis looks for insecure code patterns.", "code"),
            ("SCA", "deps, licenses", "Components", "Dependencies are matched against vulnerability databases.", "deps"),
            ("Image", "Trivy", "Container", "The built image is scanned for OS and library CVEs.", "image"),
            ("DAST", "preview env", "Running app", "ZAP probes the deployed preview environment.", "url"),
            ("Triage", "SARIF view", "Decide", "Findings are gated, triaged or accepted with expiry.", "sarif"),
        ),
    ),
    topic(
        "runner-security", "Self-Hosted Runner Security", "security", "advanced", "RS",
        "Ephemeral, isolated, least-privilege runners; never run untrusted code on persistent ones.",
        "Lending out a workshop. If every visitor uses the same bench and leaves tools behind, the next visitor can tamper with them. A fresh, locked workshop per visitor, cleaned afterwards, is the safe version.",
        "Self-hosted runners give access to private networks, special hardware (GPUs, arm, macOS) and cheaper compute, but they execute arbitrary code from workflows, which makes them a high-value target. On a persistent runner, one malicious or compromised job can install backdoors, steal credentials from the filesystem or environment, poison caches and tamper with later builds. The strongest mitigation is ephemeral runners: one job per fresh VM or container, destroyed afterwards, using --ephemeral registration, Actions Runner Controller (ARC) on Kubernetes, GitLab autoscaling runners or cloud autoscalers. Never attach self-hosted runners to public repositories where fork pull requests can run code. Isolate runner groups by trust level and restrict which repositories and workflows can use them; production-deploy runners should be separate from general build runners. Run jobs as non-root, avoid privileged containers and mounting the Docker socket, use rootless or remote BuildKit for image builds, restrict network egress to required endpoints and block the cloud instance metadata service or require IMDSv2 with hop limit 1. Give the runner's own cloud identity minimal permissions, patch base images regularly and ship runner logs to a central SIEM.",
        ["Running builds inside a private VPC that hosted runners cannot reach.", "GPU runners for ML training jobs.", "Hardening a runner fleet after a cache poisoning incident."],
        [
            "Ephemeral: one job per fresh VM or pod, then destroy.",
            "Never use self-hosted runners for public repos or fork PRs.",
            "Separate runner groups by trust; restrict repos and workflows.",
            "No Docker socket mounts or privileged mode; rootless builds.",
            "Restrict egress and instance metadata; minimal runner identity.",
        ],
        [
            ex("Actions Runner Controller scale set (ephemeral pods)", "advanced", "Helm values for a runner scale set with non-root containers.", "yaml", """
                # helm install arc-runners oci://ghcr.io/actions/actions-runner-controller-charts/gha-runner-scale-set -f values.yaml
                githubConfigUrl: https://github.com/acme
                githubConfigSecret: arc-github-app      # GitHub App credentials stored as a Kubernetes Secret
                runnerGroup: build-untrusted
                minRunners: 0
                maxRunners: 40
                template:
                  spec:
                    securityContext:
                      runAsNonRoot: true
                      runAsUser: 1001
                      seccompProfile:
                        type: RuntimeDefault
                    containers:
                      - name: runner
                        image: ghcr.io/actions/actions-runner:2.320.0   # pin; Renovate bumps it
                        command: ["/home/runner/run.sh"]
                        securityContext:
                          allowPrivilegeEscalation: false
                          capabilities:
                            drop: [ALL]
                        resources:
                          limits: {cpu: "4", memory: 8Gi}
            """, runnable=False),
            ex("Restrict runner egress with a NetworkPolicy", "advanced", "Allow DNS and HTTPS to the internet but block the metadata endpoint and cluster ranges.", "yaml", """
                apiVersion: networking.k8s.io/v1
                kind: NetworkPolicy
                metadata:
                  name: runner-egress
                  namespace: arc-runners
                spec:
                  podSelector: {}
                  policyTypes: [Egress]
                  egress:
                    - to:
                        - namespaceSelector: {}
                          podSelector:
                            matchLabels: {k8s-app: kube-dns}
                      ports:
                        - {protocol: UDP, port: 53}
                    - to:
                        - ipBlock:
                            cidr: 0.0.0.0/0
                            except: [169.254.169.254/32, 10.0.0.0/8]
                      ports:
                        - {protocol: TCP, port: 443}
            """, runnable=False),
            ex("Register an ephemeral VM runner", "intermediate", "Runner exits after one job; the VM is then destroyed.", "bash", """
                REG_TOKEN=$(gh api -X POST orgs/acme/actions/runners/registration-token --jq .token)
                ./config.sh --url https://github.com/acme --token "$REG_TOKEN" --ephemeral --unattended --runnergroup build-untrusted --labels linux,x64,ephemeral
                ./run.sh
                # after exit: cloud autoscaler terminates the instance
            """, runnable=False),
        ],
        ["./config.sh --ephemeral", "ARC: gha-runner-scale-set", "Runner groups: restrict repos/workflows", "IMDSv2 + hop limit 1", "No -v /var/run/docker.sock"],
        ["Persistent runners let one job tamper with the next job's workspace, caches or toolchain.", "Mounting the Docker socket gives jobs root on the host.", "Runner instance roles with broad cloud permissions turn any job into a cloud admin.", "Public repos with self-hosted runners let anyone run code inside your network via a fork PR."],
        [
            qa("basic", "Why are self-hosted runners risky?", "They execute code from workflows on machines you own, often inside your network with access to credentials. A malicious job can persist on the machine, steal secrets or tamper with later builds."),
            qa("intermediate", "What is an ephemeral runner?", "A runner registered for a single job that is destroyed afterwards, so no state, malware or credentials carry over between jobs. ARC and autoscaling runners create them on demand."),
            qa("intermediate", "Why should self-hosted runners not be used on public repositories?", "Anyone can open a fork pull request whose workflow code may run on the runner, giving an outsider code execution inside your infrastructure."),
            qa("advanced", "How would you design a secure runner fleet?", "Ephemeral VMs or pods per job, separate runner groups for untrusted builds and production deploys with repository and workflow restrictions, non-root and non-privileged execution, rootless image builds, egress allow-lists, blocked metadata service, minimal runner identity using OIDC for cloud access, patched images and centralised logs."),
        ],
        ["secrets-in-ci", "gha-workflows", "jenkins-declarative", "cost-speed"],
        chain(
            ("Queue", "job requested", "Demand", "A job requests a runner label from a restricted group."),
            ("Provision", "fresh VM/pod", "Ephemeral", "The autoscaler starts a clean runner just for this job.", "job"),
            ("Isolate", "non-root, egress", "Sandbox", "The job runs non-root with restricted network and no host socket.", "runner"),
            ("Run", "one job", "Execute", "Exactly one job runs, using OIDC for cloud access.", "isolated"),
            ("Destroy", "wipe all", "Tear down", "The runner is deleted, leaving no state for the next job.", "done"),
        ),
    ),
]

TOPICS = _BATCH_1 + _BATCH_2 + _BATCH_3 + _BATCH_4 + _BATCH_5 + _BATCH_6

SCENARIOS = [
    {
        "level": "intermediate", "topic": "branching-pr-checks",
        "q": "PRs that only touch docs/ are stuck forever with 'Expected - Waiting for status to be reported' on the required unit-tests check. What is happening and how do you fix it?",
        "a": "The CI workflow has paths-ignore for docs/**, so it never runs on those PRs and the required check is never reported. Branch protection waits for a status that will not come. Fix it by making the required check a small always-running gate job (for example ci-ok with if: always() that inspects needs results), or by removing the workflow-level path filter and deciding inside the job whether real work is needed, so a status is always reported.",
    },
    {
        "level": "advanced", "topic": "gha-concurrency",
        "q": "Two merges landed a minute apart. Both deploy workflows ran, the older commit finished last and production ended up on the older version. How do you prevent this?",
        "a": "Deploys were not serialised. Add a concurrency group per environment (group: deploy-production, cancel-in-progress: false) so runs queue in order instead of racing, and do not cancel in-flight deploys. As a second guard, have the deploy script compare the commit being deployed with the currently deployed SHA and refuse to go backwards unless invoked by the explicit rollback workflow.",
    },
    {
        "level": "advanced", "topic": "secrets-in-ci",
        "q": "A security scan finds that a workflow triggered by pull_request_target checks out the PR head and runs npm install. Why is this critical and what is the fix?",
        "a": "pull_request_target runs in the base repository context with secrets and a write-capable token, and npm install executes lifecycle scripts from the attacker's package.json, so any fork PR can exfiltrate secrets or push code. Switch to the pull_request trigger for building untrusted code (no secrets, read-only token). If privileged follow-up is needed, such as commenting results, use a separate workflow_run job that only consumes artifacts as data and never executes PR code, and set minimal permissions.",
    },
    {
        "level": "intermediate", "topic": "dependency-caching",
        "q": "After a Node upgrade from 20 to 22, CI fails with 'invalid ELF header' errors from a native module, but a cache-less rerun passes. What went wrong?",
        "a": "The cache key did not include the Node version, so a node_modules directory built with native binaries for Node 20 was restored on Node 22. Include the runtime version and OS in the key, prefer caching the package manager store (~/.npm, pnpm store) over node_modules, and run npm ci so native modules are rebuilt against the current runtime. Clear the stale cache entries with gh cache delete.",
    },
    {
        "level": "advanced", "topic": "db-migrations",
        "q": "During a rolling deploy, error rates spike: old pods log 'column \"email\" does not exist'. The release renamed customers.email to email_address. How do you recover and prevent it?",
        "a": "The rename broke old pods still running during the rollout. Immediately add the old column back (or a compatible view) or roll forward quickly; rolling the app back alone does not help because the schema already changed. In future use expand/contract: add email_address, dual-write, backfill, switch reads in a later release, and only drop email once no running version uses it. Add a migration linter in CI that flags RENAME and DROP in the same release as code changes.",
    },
    {
        "level": "advanced", "topic": "oidc-federation",
        "q": "An audit shows the production deploy IAM role trusts sub 'repo:acme/*'. Why is that dangerous and what should the condition be?",
        "a": "Any workflow in any repository of the organisation, on any branch including unreviewed ones, can request a token and assume the production role. Restrict the trust policy with StringEquals on aud sts.amazonaws.com and sub repo:acme/api:environment:production (or a protected ref), so only jobs in the right repository that passed the production environment's protection rules can assume it. Consider also checking job_workflow_ref to require a specific reusable deploy workflow.",
    },
    {
        "level": "intermediate", "topic": "flaky-tests",
        "q": "The team's habit is to click 'Re-run failed jobs' until CI goes green. Main has had three real regressions slip through this month. What do you change?",
        "a": "Reruns have hidden real failures among flaky ones. Start tracking test outcomes per commit to identify flaky tests by rerun-pass history, quarantine the worst offenders into a non-blocking job with owners and deadlines, and fix root causes such as sleeps, shared state and ordering. Limit automatic retries, record every retry as a flake signal, and make main red a stop-the-line event so real failures get investigated.",
    },
    {
        "level": "advanced", "topic": "progressive-delivery",
        "q": "An Argo Rollouts canary for a low-traffic internal API promoted to 100 percent even though the new version returned 500s for a key endpoint. The analysis showed 'Successful'. Why?",
        "a": "At 5 to 25 percent weight the canary received almost no requests, so the Prometheus error-ratio query returned no data or a ratio computed from a handful of requests, and the successCondition did not treat an empty result as a failure. Require a minimum request count in the query, make len(result) == 0 a failure or inconclusive, lengthen steps or add synthetic load through a webhook, and include endpoint-level metrics for critical routes.",
    },
]

from ._catalog import build_lessons

TOPICS += build_lessons([
    ("sonarqube-quality-gates", "SonarQube: Static Analysis & Quality Gates", "security", "intermediate", "SonarQube analyzes source for bugs, vulnerabilities, code smells and coverage, then a quality gate can pass or fail the pipeline. Run analysis on pull requests and default branch with a pinned scanner and a narrowly scoped project token.", "sonar-scanner -Dsonar.projectKey=payments -Dsonar.sources=src", "A quality gate is a release policy: choose actionable thresholds, review findings and avoid treating raw coverage as a quality score.", "A SonarQube stage is green, but new code has no analysis results. What do you inspect?", "Check that the scanner ran on the expected commit/branch, the project key and server URL match, report upload completed, and the quality gate waited for the compute task result." , ["ci-basics", "supply-chain-security"]),
    ("artifactories-nexus", "Artifact Repositories: JFrog Artifactory & Nexus", "artifacts-release", "intermediate", "Artifactory and Sonatype Nexus store and proxy build artifacts, container images and package dependencies. Use immutable versions, provenance, retention, replication and scoped publish/pull identities so builds can be reproduced and releases promoted safely.", "Publish immutable package once → promote the same digest through dev, staging and production", "Do not rebuild separately for production; promote the tested artifact by digest and retain metadata that links it to source and build.", "Why promote the same artifact rather than rebuilding for each environment?", "A rebuild can change dependencies or bytes. Promoting the exact tested digest preserves provenance and lets teams verify what passed in earlier stages.", ["cicd-artifacts", "supply-chain-security"]),
    ("ansible-tower", "Ansible & Ansible Tower / Automation Controller", "operations", "intermediate", "Ansible describes configuration and orchestration in YAML playbooks. Ansible Tower (now Automation Controller in Ansible Automation Platform) adds inventory, credentials, RBAC, job templates, schedules and workflow approvals for managed execution.", "ansible-playbook -i inventory/prod site.yml --check --diff", "Keep playbooks idempotent, protect vault credentials, constrain inventory and record job output; check mode is useful but is not a perfect dry run.", "What does Tower/Automation Controller add around Ansible playbooks?", "Central inventory, credential handling, role-based access, job templates, schedules, approval workflows and job history, so teams can run governed automation without distributing SSH keys to every operator.", ["ansible-idempotency", "pipeline-approval"]),
    ("helm-argocd-delivery", "Helm Charts & Argo CD GitOps Delivery", "artifacts-release", "intermediate", "Helm packages Kubernetes resources as versioned charts with values per environment. Argo CD continuously compares the desired Git state with the cluster, reports drift and syncs changes according to policy. Keep chart versions, values and promotion history reviewable.", "helm lint chart && helm template payments chart -f values-staging.yaml", "A chart render is not a live-cluster validation; validate rendered manifests, policy and health, and decide how drift and secret data are handled.", "How do Helm and Argo CD fit together?", "Helm renders a versioned set of Kubernetes manifests from a chart and values; Argo CD can use Helm as a source renderer while Git remains the declared desired state and Argo controls reconciliation.", ["progressive-delivery", "gitops"]),
], "CI", "A deployment pipeline is a chain of artifacts, policies and observable decisions.")
