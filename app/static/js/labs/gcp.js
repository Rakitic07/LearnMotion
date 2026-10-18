import { $, esc } from "../util.js";
import { scenarioLab } from "./catalog.js";

export function lab(view, content) {
  scenarioLab(view, "GCP", "sky", "GCP Architecture Lab", "Trace failures through project IAM, Shared VPC, workload identity, service permissions and Cloud Audit Logs.", content);
}

export function playground(view) {
  view.innerHTML = `<section class="topic-hero clay"><div class="code tint-sky">GCP</div><div><h1>GCP Config Builder</h1><div class="muted">Choose a workload and generate a least-privilege service boundary to review.</div></div></section><div class="grid two" style="margin-top:1rem"><section class="panel clay"><label>Workload<select id="gcpWork"><option value="run">Cloud Run API</option><option value="gke">GKE service</option><option value="batch">Batch data processor</option></select></label><label>Resource scope<input id="gcpResource" style="width:100%;font-family:var(--mono)" value="projects/demo-prod/buckets/reports-prod"></label><label class="check" style="display:flex;gap:.6rem;margin-top:.8rem"><input type="checkbox" id="gcpFederation" checked> Use workload identity / federation</label><label class="check" style="display:flex;gap:.6rem;margin-top:.5rem"><input type="checkbox" id="gcpPrivate" checked> Keep data path private</label></section><section class="panel clay"><h3>Suggested boundary</h3><div id="gcpPath"></div><h3>Review checks</h3><ul id="gcpChecks"></ul></section></div>`;
  const draw = () => {
    const work = $("#gcpWork", view).value, resource = $("#gcpResource", view).value.trim() || "REPLACE_WITH_RESOURCE", federation = $("#gcpFederation", view).checked, priv = $("#gcpPrivate", view).checked;
    const workload = work === "run" ? "Cloud Run runtime service account" : work === "gke" ? "GKE Kubernetes service account → Workload Identity" : "Cloud Batch job service account";
    $("#gcpPath", view).innerHTML = ["Organization / folder guardrails", "Project: demo-prod", workload, `Resource scope: ${resource}`].map((x, i) => `<div class="pill neutral" style="margin:.25rem">${i ? "↓ " : ""}${esc(x)}</div>`).join("");
    $("#gcpChecks", view).innerHTML = [federation ? "Use short-lived workload identity; do not download a service-account key." : "Replace long-lived keys with workload identity federation where supported.", priv ? "Check VPC path, private access, DNS and firewall from the actual workload." : "Review public exposure and egress; scope public access only where required.", "Grant the narrowest predefined or custom role at the resource scope.", "Inspect Cloud Audit Logs for the exact principal, permission and denied resource.", "Set quotas, budgets and an owner for the project."].map((x) => `<li>${esc(x)}</li>`).join("");
  };
  view.querySelectorAll("#gcpWork, #gcpResource, #gcpFederation, #gcpPrivate").forEach((el) => { el.addEventListener("input", draw); el.addEventListener("change", draw); });
  draw();
}
