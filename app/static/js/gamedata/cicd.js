export const WORDS = [
  { answer: "PIPELINE", term: "Pipeline", clue: "Automated sequence of stages that takes a commit from source to production" },
  { answer: "WORKFLOW", term: "Workflow", clue: "GitHub Actions YAML file under .github/workflows that defines jobs" },
  { answer: "RUNNER", term: "Runner", clue: "Machine or container that executes CI jobs" },
  { answer: "ARTIFACT", term: "Artifact", clue: "Build output such as an image or jar that later stages reuse" },
  { answer: "REGISTRY", term: "Registry", clue: "Server that stores and serves container images" },
  { answer: "DIGEST", term: "Image digest", clue: "Immutable sha256 identifier of an image, safer to deploy than a tag" },
  { answer: "CACHE", term: "Cache", clue: "Saved dependencies or layers restored to make the next run faster" },
  { answer: "MATRIX", term: "Matrix", clue: "Strategy that fans one job out over versions, platforms or shards" },
  { answer: "SHARD", term: "Test shard", clue: "One slice of a test suite run in parallel with the others" },
  { answer: "FLAKY", term: "Flaky test", clue: "Test that passes and fails on the same code" },
  { answer: "LINTER", term: "Linter", clue: "Static checker that catches style issues and simple bugs before tests" },
  { answer: "CANARY", term: "Canary release", clue: "Send a small slice of traffic to the new version and watch its metrics" },
  { answer: "BLUEGREEN", term: "Blue-green deployment", clue: "Two full environments; switch the router from one to the other" },
  { answer: "ROLLBACK", term: "Rollback", clue: "Returning production to the last known good version" },
  { answer: "ROLLINGUPDATE", term: "Rolling update", clue: "Replace instances in batches while the service stays up" },
  { answer: "FEATUREFLAG", term: "Feature flag", clue: "Runtime switch that decouples deploying code from releasing it" },
  { answer: "TRUNKBASED", term: "Trunk-based development", clue: "Everyone merges small changes to main at least daily" },
  { answer: "MERGEQUEUE", term: "Merge queue", clue: "Tests each PR on top of the latest main before merging it" },
  { answer: "GITOPS", term: "GitOps", clue: "Cluster state is declared in Git and an agent syncs it" },
  { answer: "DRIFT", term: "Configuration drift", clue: "Live environment no longer matches what is declared in code" },
  { answer: "OIDC", term: "OIDC federation", clue: "Lets a CI job swap a signed token for short-lived cloud credentials" },
  { answer: "SECRETS", term: "Secrets", clue: "Encrypted values injected at runtime, never committed to the repo" },
  { answer: "PERMISSIONS", term: "permissions:", clue: "Workflow key that scopes what the GITHUB_TOKEN may do" },
  { answer: "CONCURRENCY", term: "concurrency:", clue: "Workflow key that stops two runs for the same group overlapping" },
  { answer: "ENVIRONMENT", term: "Environment", clue: "Deploy target with its own secrets and protection rules such as reviewers" },
  { answer: "APPROVAL", term: "Manual approval", clue: "Human gate before a production deploy" },
  { answer: "SBOM", term: "SBOM", clue: "Software bill of materials listing every component in a build" },
  { answer: "PROVENANCE", term: "Provenance", clue: "Signed record of how, where and from what source an artifact was built" },
  { answer: "COSIGN", term: "Cosign", clue: "Sigstore tool for signing and verifying container images" },
  { answer: "HERMETIC", term: "Hermetic build", clue: "Build that depends only on declared, pinned inputs, not the network" },
  { answer: "SMOKETEST", term: "Smoke test", clue: "Quick check right after a deploy that the basics respond" },
  { answer: "LEADTIME", term: "Lead time for changes", clue: "DORA metric: time from commit to running in production" },
  { answer: "MTTR", term: "MTTR", clue: "Mean time to restore service after a failure" },
  { answer: "DORA", term: "DORA metrics", clue: "Four key measures: deploy frequency, lead time, change failure rate, restore time" },
];

export const RUSH = [
  { task: "npm install takes 2 minutes on every run", answer: "Cache dependencies keyed on the lockfile hash", wrong: ["Add a bigger runner", "Run npm install twice", "Skip installing in CI"] },
  { task: "The unit suite takes 20 minutes on one runner", answer: "Shard it across parallel jobs with a matrix", wrong: ["Delete the slowest tests", "Run it only on Fridays", "Increase the job timeout"] },
  { task: "A test fails one run in ten on unchanged code", answer: "Quarantine and fix the flaky test", wrong: ["Retry the whole pipeline until green", "Lower the coverage target", "Mark the pipeline optional"] },
  { task: "CI needs to deploy to AWS without stored keys", answer: "OIDC federation to assume an IAM role", wrong: ["Commit an access key to the repo", "Paste keys into the workflow env", "Use the root account"] },
  { task: "Default GITHUB_TOKEN scope for a build job", answer: "permissions: contents: read", wrong: ["permissions: write-all", "No permissions block at all", "contents: write everywhere"] },
  { task: "Two pushes deploy at once and race each other", answer: "A concurrency group for the deploy", wrong: ["Add sleep 60 before deploying", "Disable branch protection", "Deploy from laptops instead"] },
  { task: "Release to 5% of users and watch error rates", answer: "Canary deployment", wrong: ["Big-bang deploy", "Recreate strategy", "Nightly cron deploy"] },
  { task: "Switch all traffic instantly and back just as fast", answer: "Blue-green deployment", wrong: ["Rolling update with one pod", "Rebuild the image in prod", "Edit files on the server"] },
  { task: "Ship code dark and turn it on later", answer: "Feature flag", wrong: ["Long-lived feature branch", "Comment the code out", "Separate repository"] },
  { task: "Make sure prod runs exactly the image that was tested", answer: "Promote the same artifact by digest", wrong: ["Rebuild from source for each environment", "Deploy the latest tag", "Copy files with scp"] },
  { task: "Third-party action reference that cannot change underneath you", answer: "Pin to a full commit SHA", wrong: ["@main", "@latest", "No version at all"] },
  { task: "Untrusted fork PRs must not see repository secrets", answer: "Use pull_request, not pull_request_target with a PR checkout", wrong: ["Echo secrets only in fork builds", "Give forks write-all", "Disable tests for forks"] },
  { task: "Docker rebuilds every layer after a one-line code change", answer: "Copy the lockfile and install before copying source", wrong: ["Use FROM latest", "Add more RUN lines", "Disable BuildKit"] },
  { task: "A secret appears in the build log", answer: "Rotate it immediately and stop printing it", wrong: ["Delete the log and move on", "Make the repo private", "Base64 it next time"] },
  { task: "Cluster state should follow what is in Git", answer: "GitOps controller such as Argo CD or Flux", wrong: ["kubectl apply from a laptop", "Manual edits in the console", "A wiki page of commands"] },
  { task: "Main breaks because PRs were tested on an old base", answer: "Merge queue", wrong: ["Force-push to main", "Skip CI on small PRs", "Squash commits"] },
  { task: "Know exactly which packages are in an image", answer: "Generate an SBOM", wrong: ["Read the Dockerfile", "Trust the base image name", "Count the layers"] },
  { task: "DORA metric for how often deploys cause incidents", answer: "Change failure rate", wrong: ["Lead time", "Code coverage", "Lines of code"] },
  { task: "Cheap checks that should run first", answer: "Lint and type checks", wrong: ["End-to-end tests", "Load tests", "Production deploy"] },
  { task: "Require a human before production", answer: "Environment protection rule with required reviewers", wrong: ["A comment in the YAML", "A Slack message", "if: false on the job"] },
];

export const BUGS = [
  {
    symptom: "A commit with failing unit tests was still deployed to production.",
    lang: "yaml",
    code: `jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci && npm test
  deploy:
    needs: [lint]
    runs-on: ubuntu-latest
    steps:
      - run: ./deploy.sh production`,
    bug: [7],
    why: "deploy only needs lint, so it starts in parallel with test and does not care if tests fail. Make it needs: [lint, test] so the deploy is gated on passing tests.",
  },
  {
    symptom: "A pull request from a fork exfiltrated the repository's deploy token.",
    lang: "yaml",
    code: `on: pull_request_target
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: \${{ github.event.pull_request.head.sha }}
      - run: npm ci && npm test
        env:
          DEPLOY_TOKEN: \${{ secrets.DEPLOY_TOKEN }}`,
    bug: [0, 7],
    why: "pull_request_target runs with the base repo's secrets, and checking out the PR head then runs the attacker's code with them. Use pull_request for untrusted code and keep secrets out of test jobs.",
  },
  {
    symptom: "CI keeps using old dependencies even after package-lock.json changed.",
    lang: "yaml",
    code: `steps:
  - uses: actions/checkout@v4
  - uses: actions/cache@v4
    with:
      path: ~/.npm
      key: npm-cache
  - run: npm ci
  - run: npm test`,
    bug: [5],
    why: "A constant cache key never changes, so the first cache saved is restored forever. Key it on the lockfile: npm-${{ hashFiles('**/package-lock.json') }}, with a restore-keys prefix as fallback.",
  },
  {
    symptom: "A compromised lint tool pushed commits and created releases in the repo.",
    lang: "yaml",
    code: `name: ci
on: [push, pull_request]
permissions: write-all
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npx some-linter .`,
    bug: [2],
    why: "write-all hands every job a token that can push code, create releases and edit workflows. Default to permissions: contents: read and grant extra scopes only to the job that needs them.",
  },
  {
    symptom: "Every one-line code change makes the image rebuild reinstall all dependencies (4 minutes).",
    lang: "dockerfile",
    code: `FROM node:20-alpine
WORKDIR /app
COPY . .
RUN npm ci --omit=dev
EXPOSE 3000
USER node
CMD ["node", "server.js"]`,
    bug: [2],
    why: "Copying the whole source before npm ci means any file change invalidates the install layer. Copy package.json and package-lock.json first, run npm ci, then COPY the rest.",
  },
  {
    symptom: "Anyone who pulls the image can read the private registry token.",
    lang: "dockerfile",
    code: `FROM node:20-alpine
ARG NPM_TOKEN
WORKDIR /app
COPY package*.json ./
RUN echo "//registry.npmjs.org/:_authToken=$NPM_TOKEN" > .npmrc && npm ci
COPY . .
CMD ["node", "server.js"]`,
    bug: [1, 4],
    why: "Build args and files written in a RUN are baked into image layers and history. Use a BuildKit secret mount (RUN --mount=type=secret,id=npmrc,target=/app/.npmrc npm ci) so the token never lands in a layer.",
  },
  {
    symptom: "Builds with failing tests are green and get deployed.",
    lang: "groovy",
    code: `pipeline {
  agent any
  stages {
    stage('Test') {
      steps { sh 'npm ci && npm test || true' }
    }
    stage('Deploy') {
      steps { sh './deploy.sh production' }
    }
  }
}`,
    bug: [4],
    why: "|| true swallows the non-zero exit code, so Jenkins thinks the tests passed. Remove it; publish test reports in a post { always { ... } } block if you need them on failure.",
  },
  {
    symptom: "The deploy token shows up in the Jenkins process list and build log.",
    lang: "groovy",
    code: `stage('Deploy') {
  steps {
    withCredentials([string(credentialsId: 'deploy-token', variable: 'TOKEN')]) {
      sh "echo using \${TOKEN} && ./deploy.sh --token \${TOKEN}"
    }
  }
}`,
    bug: [3],
    why: "Double quotes make Groovy interpolate the secret into the command string before the shell runs, and echo prints it. Use single quotes so the shell reads $TOKEN from the environment, and never echo it.",
  },
];

export const META = {
  rushLabel: "Pipeline Rush",
  rushIntro: "Pick the fix a seasoned platform engineer would ship.",
  rushMono: false,
  bugLabel: "Pipeline Bug Hunt",
  bugNoun: "symptom",
};
