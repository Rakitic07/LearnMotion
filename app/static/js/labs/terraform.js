import { esc, highlightCode } from "../util.js";

const STEPS = [
  { title: "Validate", cmd: "terraform validate", lines: ["Success! The configuration is valid.", "No errors found."], state: "Configuration checked" },
  { title: "Plan", cmd: "terraform plan -out=tfplan", lines: ["Refreshing state...", "# aws_instance.web will be created", "+ resource \"aws_instance\" \"web\" {", "    + instance_type = \"t3.micro\"", "    + ami           = \"ami-0abc123\"", "  }", "Plan: 1 to add, 0 to change, 0 to destroy."], state: "Plan: 1 resource to add" },
  { title: "Verify plan", cmd: "terraform show tfplan", lines: ["# Review the exact saved plan", "+ aws_instance.web", "  instance_type = \"t3.micro\"", "No unexpected deletes or replacements."], state: "Plan reviewed" },
  { title: "Apply", cmd: "terraform apply tfplan", lines: ["aws_instance.web: Creating...", "aws_instance.web: Still creating... [10s elapsed]", "aws_instance.web: Creation complete [id=i-0abc123]", "Apply complete! Resources: 1 added, 0 changed, 0 destroyed."], state: "Resource created" },
  { title: "Verify state", cmd: "terraform state list", lines: ["aws_instance.web", "", "$ terraform output instance_id", "\"i-0abc123\""], state: "State contains aws_instance.web" },
  { title: "Destroy", cmd: "terraform destroy", lines: ["# aws_instance.web will be destroyed", "Plan: 0 to add, 0 to change, 1 to destroy.", "aws_instance.web: Destroying...", "aws_instance.web: Destruction complete", "Destroy complete! Resources: 1 destroyed."], state: "Resource removed" },
];

export function lab(view) {
  view.innerHTML = `<section class="topic-hero clay"><div class="code tint-lilac">TF</div><div><h1>Terraform Command Lifecycle</h1><div class="muted">Step through validate → plan → verify → apply → verify state → destroy. This is a safe visual simulation; it does not run Terraform or create infrastructure.</div></div></section>
    <div class="tf-lifecycle-layout"><section class="panel clay tf-lifecycle-card"><div class="row tf-command-bar"><button class="btn primary" type="button" id="tfRunAll">▶ Run full lifecycle</button><button class="btn" type="button" id="tfReset">Reset</button><span class="pill neutral" id="tfStatus">Ready · no real resources changed</span></div>
      <div class="tf-stages" id="tfStages">${STEPS.map((step, i) => `<button type="button" class="tf-stage" data-tf-step="${i}"><span>${String(i + 1).padStart(2, "0")}</span><b>${step.title}</b><small>${step.cmd}</small></button>`).join("")}</div>
      <div class="tf-resource-map"><div class="tf-resource-node" data-resource="config">main.tf<span>configuration</span></div><i>→</i><div class="tf-resource-node" data-resource="plan">tfplan<span>saved plan</span></div><i>→</i><div class="tf-resource-node" data-resource="cloud">Cloud resource<span>provider API</span></div><i>→</i><div class="tf-resource-node" data-resource="state">terraform.tfstate<span>recorded state</span></div></div>
      <div class="tf-terminal" aria-live="polite"><div class="tf-terminal-title"><span></span><span></span><span></span><b>Terraform demo terminal</b></div><pre id="tfLog">Choose a command above to see example output.</pre></div>
      <p class="muted tf-safety-note">Always review the saved plan and target workspace before applying. <code>terraform destroy</code> removes managed infrastructure after confirmation.</p></section></div>`;
  const log = view.querySelector("#tfLog"), status = view.querySelector("#tfStatus"); let runId = 0;
  const renderLog = (lines) => { log.innerHTML = lines.map((line) => `<span class="${line.startsWith("+") || line.includes("will be created") ? "tf-add" : line.includes("destroy") ? "tf-remove" : line.startsWith("$") ? "tf-command" : ""}">${esc(line || " ")}</span>`).join("\n"); };
  const mark = (index) => {
    view.querySelectorAll(".tf-stage").forEach((el, i) => { el.classList.toggle("active", i === index); el.classList.toggle("complete", i < index); });
    view.querySelectorAll("[data-resource]").forEach((node) => node.classList.toggle("reached", node.dataset.resource === "config" || (index >= 1 && node.dataset.resource === "plan") || (index >= 3 && index < 5 && ["cloud", "state"].includes(node.dataset.resource))));
    view.querySelector('[data-resource="cloud"]').classList.toggle("removed", index === 5);
  };
  const runStep = async (index, id = runId) => {
    const step = STEPS[index]; if (!step) return;
    mark(index); status.textContent = `Running example: ${step.title}`;
    const lines = [`$ ${step.cmd}`]; renderLog(lines);
    for (const line of step.lines) { await new Promise((resolve) => setTimeout(resolve, 250)); if (id !== runId) return; lines.push(line); renderLog(lines); }
    status.textContent = step.state;
  };
  view.querySelectorAll("[data-tf-step]").forEach((button) => button.addEventListener("click", () => { runId++; runStep(Number(button.dataset.tfStep)); }));
  view.querySelector("#tfRunAll").addEventListener("click", async () => { const id = ++runId; for (let i = 0; i < STEPS.length; i++) { await runStep(i, id); if (id !== runId) return; } status.textContent = "Lifecycle complete · demo only"; });
  view.querySelector("#tfReset").addEventListener("click", () => { runId++; log.textContent = "Choose a command above to see example output."; status.textContent = "Ready · no real resources changed"; view.querySelectorAll(".tf-stage, .tf-resource-node").forEach((el) => el.classList.remove("active", "complete", "reached", "removed")); });
}

export function playground(view) {
  view.innerHTML = `<section class="topic-hero clay"><div class="code tint-lilac">TF</div><div><h1>Interactive HCL Generator</h1><div class="muted">Choose a resource, edit its settings, inspect highlighted HCL and preview the plan Terraform would produce.</div></div></section>
    <div class="grid two" style="margin-top:1rem"><section class="panel clay tf-builder-controls">
      <label>Resource type<select id="tfType"><option value="instance">AWS instance</option><option value="bucket">S3 bucket</option><option value="network">Security group</option></select></label>
      <label>Resource name<input id="tfName" value="web" maxlength="32"></label><label>Region<input id="tfRegion" value="us-east-1" maxlength="24"></label>
      <label>Instance type<select id="tfSize"><option>t3.micro</option><option>t3.small</option><option>t3.medium</option></select></label>
      <label class="check"><input id="tfEncrypt" type="checkbox" checked> Enable encryption / secure defaults</label>
      <label>Environment<select id="tfEnv"><option>dev</option><option>staging</option><option>production</option></select></label>
      <button type="button" class="btn primary" id="tfShowPlan">▶ Preview plan</button>
    </section><section class="panel clay"><div class="row"><h3 style="margin:0">Generated HCL</h3><button type="button" class="btn small" id="tfCopy">Copy</button></div><pre class="code tf-code" id="tfCode"></pre></section></div>
    <section class="panel clay tf-plan-preview" id="tfPlanPreview" hidden><h3>Plan preview</h3><p id="tfPlanText"></p><div class="tf-plan-graph" id="tfPlanGraph"></div><p class="muted">This local preview illustrates Terraform's plan concept; it does not query a provider or create infrastructure.</p></section>`;
  const $ = (q) => view.querySelector(q);
  const draw = () => {
    const type = $("#tfType").value, name = $("#tfName").value.trim().replace(/[^\w-]/g, "_") || "example", region = $("#tfRegion").value.trim().replace(/[^\w-]/g, "") || "us-east-1", size = $("#tfSize").value, env = $("#tfEnv").value, encrypted = $("#tfEncrypt").checked;
    let code;
    if (type === "instance") code = `provider "aws" {\n  region = "${region}"\n}\n\nresource "aws_instance" "${name}" {\n  ami           = "ami-0abc123"\n  instance_type = "${size}"\n\n  root_block_device {\n    encrypted = ${encrypted}\n  }\n\n  tags = {\n    Name        = "${name}"\n    Environment = "${env}"\n  }\n}`;
    else if (type === "bucket") code = `resource "aws_s3_bucket" "${name}" {\n  bucket = "${name}-${env}-example"\n}\n${encrypted ? `\nresource "aws_s3_bucket_server_side_encryption_configuration" "${name}" {\n  bucket = aws_s3_bucket.${name}.id\n\n  rule {\n    apply_server_side_encryption_by_default {\n      sse_algorithm = "AES256"\n    }\n  }\n}` : ""}`;
    else code = `resource "aws_security_group" "${name}" {\n  name         = "${name}-${env}"\n  description  = "Scoped application access"\n\n  ingress {\n    from_port   = 443\n    to_port     = 443\n    protocol    = "tcp"\n    cidr_blocks = ["10.0.0.0/8"]\n  }\n\n  egress {\n    from_port   = 0\n    to_port     = 0\n    protocol    = "-1"\n    cidr_blocks = ["0.0.0.0/0"]\n  }\n}`;
    $("#tfCode").innerHTML = highlightCode(code, "hcl"); $("#tfCode").dataset.raw = code;
  };
  view.querySelectorAll("#tfType, #tfName, #tfRegion, #tfSize, #tfEncrypt, #tfEnv").forEach((el) => { el.addEventListener("input", draw); el.addEventListener("change", draw); });
  $("#tfCopy").addEventListener("click", async () => { await navigator.clipboard?.writeText($("#tfCode").dataset.raw); $("#tfCopy").textContent = "Copied"; setTimeout(() => { if ($("#tfCopy")) $("#tfCopy").textContent = "Copy"; }, 1200); });
  $("#tfShowPlan").addEventListener("click", () => {
    const name = $("#tfName").value.trim().replace(/[^\w-]/g, "_") || "example"; const resource = $("#tfType").value === "instance" ? "aws_instance" : $("#tfType").value === "bucket" ? "aws_s3_bucket" : "aws_security_group";
    $("#tfPlanPreview").hidden = false; $("#tfPlanText").textContent = `Plan: 1 to add, 0 to change, 0 to destroy. Resource ${resource}.${name} will be created.`;
    $("#tfPlanGraph").innerHTML = `<span class="tf-resource-node reached">HCL config</span><i>→</i><span class="tf-resource-node reached">${esc(resource)}.${esc(name)} <b>+ create</b></span><i>→</i><span class="tf-resource-node">State file</span>`;
  });
  draw();
}
