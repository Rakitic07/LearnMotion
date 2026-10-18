import { $, esc, highlightCode } from "../util.js";
import { labHero } from "./common.js";

const CHECKS = [
  ["source", "Source identity policy allows sts:AssumeRole on the exact destination role ARN"],
  ["trust", "Destination role trust policy matches the source principal and conditions"],
  ["role", "Assumed role policy allows the requested action on the target resource"],
  ["guardrail", "No SCP, permissions boundary or session policy blocks the request"],
  ["resource", "Target resource policy or KMS key policy admits the role where required"],
];
const CASES = {
  ci: { title: "CI cannot assume a deployment role", symptom: "The CI job receives AccessDenied from sts:AssumeRole before deployment starts.", missing: ["source", "trust"], explanation: "The source CI principal needs sts:AssumeRole on the exact target role ARN, and the target role trust must match the actual CI role plus any ExternalId, MFA or OIDC conditions." },
  trust: { title: "Trust policy names the wrong principal", symptom: "A developer can assume the role, but a workload in another account cannot.", missing: ["trust"], explanation: "Compare the workload's actual principal ARN with the target role's Principal and conditions. Trusting an account is not the same as authorizing every source principal to assume the role." },
  s3: { title: "AssumeRole succeeds, S3 access fails", symptom: "The role session is created successfully, but s3:GetObject returns AccessDenied.", missing: ["role", "resource"], explanation: "AssumeRole is only the identity handoff. The role session needs s3:GetObject on the object ARN, and the bucket policy, KMS key policy, endpoint policy and guardrails must permit the request." },
  scp: { title: "Organization guardrail blocks access", symptom: "Both account policies allow the operation, but the target account still denies it.", missing: ["guardrail"], explanation: "Inspect SCPs on the source and destination account paths, permissions boundaries, session policies and explicit denies. An SCP limits permissions; it does not grant them." },
  oidc: { title: "GitHub OIDC role assumption fails", symptom: "The workflow gets Not authorized to perform sts:AssumeRoleWithWebIdentity.", missing: ["trust"], explanation: "Compare issuer, audience and subject claims with the trust conditions exactly. A repository, branch or environment mismatch is a common cause; confirm the OIDC provider exists in the target account." },
  kms: { title: "Cross-account object cannot be decrypted", symptom: "The target role reads the S3 object metadata but cannot decrypt its SSE-KMS body.", missing: ["role", "resource"], explanation: "The target role needs kms:Decrypt and the KMS key policy must admit that role (or delegate to IAM as intended). Check key region, encryption context and organization guardrails." },
};

export function lab(view) {
  view.innerHTML = `${labHero("IAM", "rose", "Cross-Account IAM Troubleshooting Lab", "Follow the authorization chain across source identity, destination trust, role permissions and resource policies. Toggle the actual layers and find the first missing permission.")}
    <div class="grid two"><section class="panel clay"><label>Failure scenario<select id="iamCase" style="width:100%;margin-top:.4rem">${Object.entries(CASES).map(([id, c]) => `<option value="${id}">${esc(c.title)}</option>`).join("")}</select></label><p id="iamSymptom" class="muted"></p><div id="iamChecks"></div><div class="row" style="margin-top:1rem"><button class="btn primary" id="iamEvaluate">Evaluate access</button><button class="btn" id="iamReset">Reset example</button></div></section><section class="panel clay" id="iamOutput" aria-live="polite"><h3>Authorization decision</h3><p class="muted">Select the policies you believe are correct, then evaluate.</p></section></div>
    <section class="panel clay" style="margin-top:1rem"><h3>Troubleshooting order</h3><ol><li>Run <code>aws sts get-caller-identity</code> to confirm the real caller.</li><li>Check the source identity's <code>sts:AssumeRole</code> permission and exact role ARN.</li><li>Check the target trust principal and conditions.</li><li>After assuming, inspect role session permissions and guardrails.</li><li>For S3, KMS or SQS, inspect the resource policy and the denied CloudTrail event.</li></ol></section>`;
  const select = $("#iamCase", view), checksEl = $("#iamChecks", view);
  function reset() {
    const c = CASES[select.value];
    $("#iamSymptom", view).textContent = c.symptom;
    checksEl.innerHTML = CHECKS.map(([id, label]) => `<label class="check" style="display:flex;gap:.6rem;margin:.55rem 0"><input type="checkbox" value="${id}"><span>${esc(label)}</span></label>`).join("");
    $("#iamOutput", view).innerHTML = `<h3>Authorization decision</h3><p class="muted">Select the policies you believe are correct, then evaluate.</p>`;
  }
  $("#iamEvaluate", view).addEventListener("click", () => {
    const c = CASES[select.value];
    const enabled = new Set(Array.from(checksEl.querySelectorAll("input:checked"), (i) => i.value));
    const firstMissing = CHECKS.find(([id]) => c.missing.includes(id) && !enabled.has(id));
    const output = $("#iamOutput", view);
    if (firstMissing) output.innerHTML = `<span class="pill danger">DENY</span><h3>First failing layer: ${esc(firstMissing[1].split(" ")[0])}</h3><p>${esc(c.explanation)}</p><p class="muted">Check next: <code>${esc(firstMissing[1])}</code></p>`;
    else output.innerHTML = `<span class="pill success">PATH COMPLETE</span><h3>All required layers are present</h3><p>${esc(c.explanation)}</p><p class="muted">In AWS, confirm with policy simulation and the CloudTrail event; this teaching model does not call your account.</p>`;
  });
  $("#iamReset", view).addEventListener("click", reset);
  select.addEventListener("change", reset);
  reset();
}

export function playground(view) {
  view.innerHTML = `<section class="topic-hero clay"><div class="code tint-rose">IAM</div><div><h1>Least-Privilege Policy Builder</h1><div class="muted">Build a small identity policy and review how its action, resource and cross-account trust fit together.</div></div></section>
    <div class="grid two" style="margin-top:1rem"><section class="panel clay"><label>Service action<select id="iamAction"><option value="s3:GetObject">s3:GetObject</option><option value="s3:PutObject">s3:PutObject</option><option value="kms:Decrypt">kms:Decrypt</option><option value="sqs:SendMessage">sqs:SendMessage</option><option value="sts:AssumeRole">sts:AssumeRole</option></select></label><label style="display:block;margin-top:.8rem">Exact resource ARN<input id="iamResource" style="width:100%;font-family:var(--mono)" value="arn:aws:s3:::reports-prod/monthly/*"></label><label class="check" style="display:flex;gap:.6rem;margin-top:.8rem"><input type="checkbox" id="iamCross"> This is a cross-account request</label><div class="row" style="margin-top:1rem"><button class="btn primary" id="iamBuild">Build policy</button></div></section><section class="panel clay"><h3>Identity policy</h3><pre class="code" id="iamJson" style="white-space:pre-wrap"></pre><p id="iamTrustHint" class="muted"></p></section></div>`;
  function draw() {
    const action = $("#iamAction", view).value, resource = $("#iamResource", view).value.trim() || "REPLACE_WITH_EXACT_ARN";
    $("#iamJson", view).innerHTML = highlightCode(JSON.stringify({ Version: "2012-10-17", Statement: [{ Effect: "Allow", Action: action, Resource: resource }] }, null, 2), "json");
    $("#iamTrustHint", view).textContent = action === "sts:AssumeRole" || $("#iamCross", view).checked
      ? "Cross-account access also needs a destination role trust policy that matches the source principal. The destination role then needs its own permissions for the final resource action."
      : "Replace the sample ARN with the narrowest required resource. A permission policy does not override an explicit deny, boundary or SCP.";
  }
  view.querySelectorAll("#iamAction, #iamResource, #iamCross").forEach((el) => el.addEventListener("input", draw));
  view.querySelectorAll("#iamAction, #iamResource, #iamCross").forEach((el) => el.addEventListener("change", draw));
  $("#iamBuild", view).addEventListener("click", draw);
  draw();
}
