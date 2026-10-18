import { $, esc, highlightCode } from "../util.js";
import { scenarioLab } from "./catalog.js";

export function lab(view, content) {
  scenarioLab(view, "AZ", "sky", "Azure Architecture Lab", "Resolve common Azure failures across identity, RBAC, private networking, DNS and policy.", content);
}

export function playground(view) {
  view.innerHTML = `<section class="topic-hero clay"><div class="code tint-sky">AZDO</div><div><h1>Azure DevOps Pipeline Builder</h1><div class="muted">Choose a stack, stages and deployment environment to generate Azure Pipelines YAML. Preview a sample run without connecting to Azure.</div></div></section>
    <div class="grid two" style="margin-top:1rem"><section class="panel clay azdo-controls">
      <label>Application stack<select id="azdoStack"><option value="node">Node.js</option><option value="dotnet">.NET</option><option value="python">Python</option></select></label>
      <label>Agent image<select id="azdoAgent"><option>ubuntu-latest</option><option>windows-latest</option><option>macOS-latest</option></select></label>
      <label>Trigger branch<input id="azdoBranch" value="main" maxlength="40"></label>
      <label>Deploy environment<select id="azdoEnvironment"><option>dev</option><option>staging</option><option>production</option></select></label>
      <fieldset class="azdo-stage-options"><legend>Pipeline stages</legend>${[["build", "Build"], ["test", "Test"], ["security", "Security scan"], ["deploy", "Deploy"]].map(([id, label], i) => `<label class="check"><input type="checkbox" data-azdo-stage="${id}" ${i < 3 ? "checked" : ""}> ${label}</label>`).join("")}</fieldset>
      <label class="check"><input id="azdoApproval" type="checkbox" checked> Require approval before production deploy</label>
      <button type="button" class="btn primary" id="azdoRun">▶ Preview pipeline run</button>
    </section><section class="panel clay"><div class="row"><h3 style="margin:0">Stage flow</h3><span class="pill neutral" id="azdoRunStatus">Ready</span></div><div id="azdoFlow" class="azdo-flow"></div><pre id="azdoRunLog" class="azdo-run-log">Select stages and preview a run.</pre></section></div>
    <section class="panel clay azdo-yaml-panel"><div class="row"><div><h3 style="margin:0">azure-pipelines.yml</h3><span class="muted">Generated from your selections</span></div><button type="button" class="btn small" id="azdoCopy">Copy YAML</button></div><pre id="azdoYaml" class="code azdo-yaml"></pre></section>`;
  const $ = (q) => view.querySelector(q); let runId = 0;
  const selectedStages = () => [...view.querySelectorAll("[data-azdo-stage]:checked")].map((el) => el.dataset.azdoStage);
  const buildYaml = () => {
    const stack = $("#azdoStack").value, agent = $("#azdoAgent").value, branch = $("#azdoBranch").value.trim().replace(/[^\w./-]/g, "") || "main", env = $("#azdoEnvironment").value, stages = selectedStages();
    const snippets = {
      node: { build: ["      - task: NodeTool@0", "        inputs:", "          versionSpec: '22.x'", "      - script: npm ci && npm run build", "        displayName: Build"], test: ["      - script: npm test -- --ci", "        displayName: Run tests"], security: ["      - script: npm audit --audit-level=high", "        displayName: Dependency audit"] },
      dotnet: { build: ["      - task: UseDotNet@2", "        inputs:", "          packageType: sdk", "          version: '8.x'", "      - script: dotnet build --configuration Release"], test: ["      - script: dotnet test --configuration Release", "        displayName: Run tests"], security: ["      - script: dotnet list package --vulnerable", "        displayName: Check vulnerable packages"] },
      python: { build: ["      - task: UsePythonVersion@0", "        inputs:", "          versionSpec: '3.12'", "      - script: python -m pip install -r requirements.txt"], test: ["      - script: python -m pytest", "        displayName: Run tests"], security: ["      - script: pip-audit", "        displayName: Audit dependencies"] },
    }[stack];
    const names = { build: "Build", test: "Test", security: "SecurityScan", deploy: "Deploy" };
    const lines = [`trigger:`, `  branches:`, `    include:`, `      - ${branch}`, `pool:`, `  vmImage: ${agent}`, `stages:`];
    stages.forEach((stage) => {
      lines.push(`  - stage: ${names[stage]}`, `    displayName: ${stage === "security" ? "Security scan" : names[stage]}`, `    jobs:`);
      if (stage === "deploy") {
        if (env === "production" && $("#azdoApproval").checked) lines.push(`      # Configure a pre-deployment approval check on this environment in Azure DevOps.`);
        lines.push(`    - deployment: Deploy`, `      environment: ${env}`, `      strategy:`, `        runOnce:`, `          deploy:`, `            steps:`, `            - task: AzureCLI@2`, `              inputs:`, `                azureSubscription: $(AZURE_SERVICE_CONNECTION)`, `                scriptType: bash`, `                scriptLocation: inlineScript`, `                inlineScript: |`, `                  echo "Deploy to ${env}"`);
      } else lines.push(`    - job: ${names[stage]}`, `      steps:`, ...snippets[stage]);
    });
    return { yaml: lines.join("\n"), stages, env };
  };
  const draw = () => {
    const { yaml, stages } = buildYaml(); $("#azdoYaml").innerHTML = highlightCode(yaml, "yaml"); $("#azdoYaml").dataset.raw = yaml;
    $("#azdoFlow").innerHTML = stages.length ? stages.map((s, i) => `<div class="azdo-stage" data-run-stage="${s}"><span>${i + 1}</span><b>${s === "security" ? "Security" : s[0].toUpperCase() + s.slice(1)}</b><small>${s === "deploy" ? $("#azdoEnvironment").value : "Azure Pipeline"}</small></div>`).join(`<i aria-hidden="true">→</i>`) : `<p class="muted">Select at least one stage.</p>`;
  };
  view.querySelectorAll("#azdoStack, #azdoAgent, #azdoBranch, #azdoEnvironment, #azdoApproval, [data-azdo-stage]").forEach((el) => { el.addEventListener("input", draw); el.addEventListener("change", draw); });
  $("#azdoCopy").addEventListener("click", async () => { await navigator.clipboard?.writeText($("#azdoYaml").dataset.raw); $("#azdoCopy").textContent = "Copied"; setTimeout(() => { if ($("#azdoCopy")) $("#azdoCopy").textContent = "Copy YAML"; }, 1200); });
  $("#azdoRun").addEventListener("click", async () => {
    const id = ++runId; const { stages, env } = buildYaml(); const log = $("#azdoRunLog"); log.textContent = "Queueing sample run…"; $("#azdoRunStatus").textContent = "Running";
    for (let i = 0; i < stages.length; i++) {
      await new Promise((resolve) => setTimeout(resolve, 650)); if (id !== runId) return;
      view.querySelectorAll("[data-run-stage]").forEach((el, j) => { el.classList.toggle("running", j === i); el.classList.toggle("passed", j < i); });
      log.textContent += `\n${stages[i].toUpperCase()} · ${stages[i] === "deploy" ? `deploy to ${env}` : "completed successfully"}`;
    }
    view.querySelectorAll("[data-run-stage]").forEach((el) => el.classList.remove("running"));
    $("#azdoRunStatus").textContent = stages.length ? "Sample run passed" : "No stages";
  });
  draw();
}
