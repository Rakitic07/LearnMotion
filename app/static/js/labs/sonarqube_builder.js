import { esc, highlightCode } from "../util.js";

export function playground(view) {
  view.innerHTML = `<section class="topic-hero clay"><div class="code tint-sky">SON</div><div><h1>Rule &amp; Quality Gate Builder</h1><div class="muted">Adjust new-code measures and see whether a pull request passes your gate.</div></div></section>
    <div class="grid two" style="margin-top:1rem"><section class="panel clay sonar-controls">
      <label>Analysis language<select id="sonarProfile"><option>JavaScript / TypeScript</option><option>Java</option><option>Python</option><option>CSS</option></select></label>
      <label>New-code coverage <b id="sonarCoverageValue">82%</b><input id="sonarCoverage" type="range" min="0" max="100" value="82"></label>
      <label>Coverage minimum <b id="sonarMinValue">80%</b><input id="sonarMin" type="range" min="0" max="100" value="80"></label>
      <label>New blocker issues <b id="sonarBlockersValue">0</b><input id="sonarBlockers" type="range" min="0" max="10" value="0"></label>
      <label>New vulnerabilities <b id="sonarVulnsValue">0</b><input id="sonarVulns" type="range" min="0" max="5" value="0"></label>
      <label class="check"><input id="sonarHotspot" type="checkbox"> Unreviewed security hotspots exist</label>
      <fieldset class="sonar-rule-list"><legend>Example JavaScript / TypeScript rules</legend>${[["javascript:S3776", "Cognitive complexity"], ["javascript:S6544", "Promise misuse"], ["javascript:S5852", "Risky regular expression"]].map(([id, label], i) => `<label class="check"><input type="checkbox" data-sonar-rule="${id}" ${i < 2 ? "checked" : ""}> ${label} <code>${id}</code></label>`).join("")}<small class="muted">Use rules for your language when editing its quality profile in SonarQube.</small></fieldset>
    </section><section class="panel clay"><div class="row"><h3 style="margin:0">Pull request result</h3><span id="sonarResult" class="pill ok">PASSED</span></div><ul class="sonar-conditions" id="sonarConditions"></ul><div class="sonar-quality-meter"><div id="sonarMeter"></div></div><p class="muted" id="sonarAdvice"></p></section></div>
    <section class="panel clay" style="margin-top:1rem"><div class="row"><h3 style="margin:0">Pipeline configuration</h3><button type="button" class="btn small" id="sonarCopy">Copy</button></div><pre class="code sonar-code" id="sonarCode"></pre></section>`;
  const $ = (q) => view.querySelector(q);
  const draw = () => {
    const coverage = +$("#sonarCoverage").value, minimum = +$("#sonarMin").value, blockers = +$("#sonarBlockers").value, vulns = +$("#sonarVulns").value, hotspot = $("#sonarHotspot").checked;
    $("#sonarCoverageValue").textContent = `${coverage}%`; $("#sonarMinValue").textContent = `${minimum}%`; $("#sonarBlockersValue").textContent = blockers; $("#sonarVulnsValue").textContent = vulns;
    const checks = [[`New-code coverage ≥ ${minimum}%`, coverage >= minimum], ["No new blocker issues", blockers === 0], ["No new vulnerabilities", vulns === 0], ["Security hotspots reviewed", !hotspot]];
    const passed = checks.every(([, ok]) => ok); $("#sonarResult").textContent = passed ? "PASSED" : "FAILED"; $("#sonarResult").className = `pill ${passed ? "ok" : "danger"}`;
    $("#sonarConditions").innerHTML = checks.map(([label, ok]) => `<li class="${ok ? "sonar-pass" : "sonar-fail"}"><b>${ok ? "✓" : "×"}</b> ${esc(label)}</li>`).join("");
    $("#sonarMeter").style.width = `${coverage}%`; $("#sonarAdvice").textContent = passed ? "This change meets the configured new-code gate. Review findings and build status before merge." : "The gate blocks promotion. Inspect the failing condition, fix the source or review the hotspot, then rerun analysis.";
    const rules = [...view.querySelectorAll("[data-sonar-rule]:checked")].map((el) => `  - ${el.dataset.sonarRule}`).join("\n") || "  - (no custom rules selected)";
    const profile = $("#sonarProfile").value;
    const coverageProperty = profile.includes("JavaScript") ? "sonar.javascript.lcov.reportPaths=coverage/lcov.info" : profile === "Java" ? "sonar.coverage.jacoco.xmlReportPaths=target/site/jacoco/jacoco.xml" : profile === "Python" ? "sonar.python.coverage.reportPaths=coverage.xml" : "# Add the coverage report path for your CSS coverage tool";
    const config = `# sonar-project.properties\nsonar.projectKey=payments-api\nsonar.sources=src\nsonar.tests=tests\n${coverageProperty}\n\n# Quality gate policy (configure this gate in SonarQube)\n# New-code coverage minimum: ${minimum}%\n# New blocker issues maximum: 0\n# New vulnerabilities maximum: 0\n# Security hotspots: review all\n\n# Selected quality profile: ${profile}\n# Rules enabled in this lesson builder:\n${rules.split("\n").map((line) => `# ${line.trim()}`).join("\n")}\n\n# CI analysis command\nsonar-scanner`;
    $("#sonarCode").innerHTML = highlightCode(config, "properties");
  };
  view.querySelectorAll("#sonarProfile, #sonarCoverage, #sonarMin, #sonarBlockers, #sonarVulns, #sonarHotspot, [data-sonar-rule]").forEach((el) => { el.addEventListener("input", draw); el.addEventListener("change", draw); });
  $("#sonarCopy").addEventListener("click", async () => { await navigator.clipboard?.writeText($("#sonarCode").textContent); $("#sonarCopy").textContent = "Copied"; setTimeout(() => { if ($("#sonarCopy")) $("#sonarCopy").textContent = "Copy"; }, 1200); });
  draw();
}
