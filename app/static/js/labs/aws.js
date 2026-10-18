import { $, $$, esc } from "../util.js";
import { labHero, takeHandoff } from "./common.js";

// ===================================================================== IAM evaluator
const arr = (v) => (v === undefined ? [] : Array.isArray(v) ? v : [v]);
const globRe = (pattern, ci) => new RegExp(`^${pattern.replace(/[.+^${}()|[\]\\]/g, "\\$&").replace(/\*/g, ".*").replace(/\?/g, ".")}$`, ci ? "i" : "");
const glob = (pattern, value, ci = false) => globRe(pattern, ci).test(value);

function ipToInt(ip) {
  const p = ip.split(".").map(Number);
  return p.length === 4 && p.every((n) => n >= 0 && n <= 255) ? ((p[0] << 24) | (p[1] << 16) | (p[2] << 8) | p[3]) >>> 0 : null;
}
function inCidr(ip, cidr) {
  const [net, bits = "32"] = cidr.split("/");
  const a = ipToInt(ip), b = ipToInt(net);
  if (a === null || b === null) return false;
  const mask = +bits === 0 ? 0 : (~0 << (32 - +bits)) >>> 0;
  return (a & mask) === (b & mask);
}

const OPS = {
  StringEquals: (a, b) => a === b,
  StringNotEquals: (a, b) => a === b,
  StringEqualsIgnoreCase: (a, b) => a.toLowerCase() === b.toLowerCase(),
  StringLike: (a, b) => glob(b, a),
  StringNotLike: (a, b) => glob(b, a),
  ArnEquals: (a, b) => a === b,
  ArnLike: (a, b) => glob(b, a),
  ArnNotLike: (a, b) => glob(b, a),
  Bool: (a, b) => String(a).toLowerCase() === String(b).toLowerCase(),
  NumericEquals: (a, b) => +a === +b,
  NumericNotEquals: (a, b) => +a === +b,
  NumericLessThan: (a, b) => +a < +b,
  NumericLessThanEquals: (a, b) => +a <= +b,
  NumericGreaterThan: (a, b) => +a > +b,
  NumericGreaterThanEquals: (a, b) => +a >= +b,
  IpAddress: (a, b) => inCidr(a, b),
  NotIpAddress: (a, b) => inCidr(a, b),
};
const NEGATED = new Set(["StringNotEquals", "StringNotLike", "ArnNotLike", "NumericNotEquals", "NotIpAddress"]);

function substitute(s, ctx) {
  return String(s).replace(/\$\{([^}]+)\}/g, (_, k) => ctx[k] ?? `\${${k}}`);
}

function evalCondition(cond, ctx) {
  for (const [rawOp, block] of Object.entries(cond || {})) {
    const ifExists = rawOp.endsWith("IfExists");
    const op = rawOp.replace(/IfExists$/, "");
    const fn = OPS[op];
    for (const [key, want] of Object.entries(block)) {
      if (op === "Null") {
        const missing = !(key in ctx);
        if (missing !== (String(want) === "true")) return `${key} is ${missing ? "missing" : "present"}`;
        continue;
      }
      if (!fn) return `operator ${rawOp} is not supported by this lab`;
      const have = ctx[key];
      if (have === undefined) {
        if (ifExists || NEGATED.has(op)) continue;
        return `context key ${key} is missing`;
      }
      const values = arr(want).map((w) => substitute(w, ctx));
      const any = values.some((w) => fn(String(have), String(w)));
      const pass = NEGATED.has(op) ? !any : any;
      if (!pass) return `${rawOp} ${key}: request has "${have}", policy wants ${NEGATED.has(op) ? "none of" : "one of"} ${JSON.stringify(values)}`;
    }
  }
  return null;
}

function principalMatches(p, who) {
  if (p === "*") return true;
  if (!p || typeof p !== "object") return false;
  return arr(p.AWS).some((a) => a === "*" || a === who || (a.endsWith(":root") && who.startsWith(a.replace(/root$/, ""))));
}

function evalPolicy(doc, req, ctx, { resourcePolicy = false } = {}) {
  const out = [];
  arr(doc?.Statement).forEach((st, i) => {
    const sid = st.Sid || `#${i + 1}`;
    const why = [];
    if (st.Action && !arr(st.Action).some((a) => glob(a, req.action, true))) why.push(`action ${req.action} not in Action`);
    if (st.NotAction && arr(st.NotAction).some((a) => glob(a, req.action, true))) why.push(`action ${req.action} is in NotAction`);
    if (st.Resource && !arr(st.Resource).some((r) => glob(substitute(r, ctx), req.resource))) why.push("resource not in Resource");
    if (st.NotResource && arr(st.NotResource).some((r) => glob(substitute(r, ctx), req.resource))) why.push("resource is in NotResource");
    if (resourcePolicy && !principalMatches(st.Principal, req.principal)) why.push("principal not in Principal");
    if (!why.length && st.Condition) {
      const c = evalCondition(st.Condition, ctx);
      if (c) why.push(`condition failed: ${c}`);
    }
    out.push({ sid, effect: st.Effect, applies: !why.length, why });
  });
  return out;
}

const parseDoc = (txt, name) => {
  if (!txt.trim()) return null;
  try {
    return JSON.parse(txt);
  } catch (e) {
    throw new Error(`${name}: invalid JSON (${e.message})`);
  }
};

export function evaluate({ identity, resource, boundary, scp }, req) {
  const user = req.principal.split("/").pop();
  const ctx = { "aws:username": user, "aws:PrincipalArn": req.principal, ...req.context };
  const sets = [
    ["SCP", scp, {}],
    ["Resource policy", resource, { resourcePolicy: true }],
    ["Permissions boundary", boundary, {}],
    ["Identity policy", identity, {}],
  ].filter(([, d]) => d).map(([name, doc, o]) => ({ name, rows: evalPolicy(doc, req, ctx, o) }));
  const find = (name, eff) => sets.find((s) => s.name === name)?.rows.some((r) => r.applies && r.effect === eff);
  const has = (name) => sets.some((s) => s.name === name);
  const anyDeny = sets.find((s) => s.rows.some((r) => r.applies && r.effect === "Deny"));
  let decision, reason, step;
  if (anyDeny) [decision, reason, step] = ["Deny", `Explicit deny in the ${anyDeny.name}. An explicit deny always wins.`, 1];
  else if (has("SCP") && !find("SCP", "Allow")) [decision, reason, step] = ["Deny", "The organisation's SCP does not allow this action, so nobody in the account can do it.", 2];
  else if (find("Resource policy", "Allow")) [decision, reason, step] = ["Allow", "The resource policy allows this principal (same account: that is enough on its own).", 3];
  else if (has("Permissions boundary") && !find("Permissions boundary", "Allow")) [decision, reason, step] = ["Deny", "The permissions boundary does not allow it. A boundary caps what identity policies can grant.", 4];
  else if (find("Identity policy", "Allow")) [decision, reason, step] = ["Allow", "An identity policy allows it and nothing denies it.", 5];
  else [decision, reason, step] = ["Deny", "Implicit deny: no policy allows it. Everything is denied by default.", 5];
  return { decision, reason, step, sets, ctx };
}

const P = (statements) => JSON.stringify({ Version: "2012-10-17", Statement: statements }, null, 2);
const IAM_PRESETS = [
  {
    label: "Read-only S3",
    identity: P([{ Sid: "ReadReports", Effect: "Allow", Action: ["s3:GetObject", "s3:ListBucket"], Resource: ["arn:aws:s3:::acme-reports", "arn:aws:s3:::acme-reports/*"] }]),
    req: { action: "s3:PutObject", resource: "arn:aws:s3:::acme-reports/q3.csv", context: "" },
    note: "Try s3:GetObject, then s3:PutObject. Nothing allows the write, so it is implicitly denied.",
  },
  {
    label: "Explicit deny wins",
    identity: P([{ Sid: "AllS3", Effect: "Allow", Action: "s3:*", Resource: "*" }, { Sid: "NoDeletes", Effect: "Deny", Action: "s3:DeleteObject", Resource: "arn:aws:s3:::prod-*/*" }]),
    req: { action: "s3:DeleteObject", resource: "arn:aws:s3:::prod-data/users.json", context: "" },
    note: "s3:* allows it, but the Deny matches, and a Deny always wins. Change the bucket to dev-data to see it allowed.",
  },
  {
    label: "MFA required",
    identity: P([{ Sid: "StopWithMfa", Effect: "Allow", Action: ["ec2:StopInstances", "ec2:TerminateInstances"], Resource: "*", Condition: { Bool: { "aws:MultiFactorAuthPresent": "true" } } }]),
    req: { action: "ec2:TerminateInstances", resource: "arn:aws:ec2:eu-west-1:123456789012:instance/i-0abc", context: "aws:MultiFactorAuthPresent=false" },
    note: "Flip the context key to true and evaluate again.",
  },
  {
    label: "Home folders (${aws:username})",
    identity: P([{ Sid: "OwnFolder", Effect: "Allow", Action: ["s3:GetObject", "s3:PutObject"], Resource: "arn:aws:s3:::acme-home/home/${aws:username}/*" }]),
    req: { action: "s3:GetObject", resource: "arn:aws:s3:::acme-home/home/bob/notes.txt", context: "" },
    note: "The principal is alice. Policy variables make one policy work for every user. Change bob to alice.",
  },
  {
    label: "Office IPs only",
    identity: P([{ Sid: "Work", Effect: "Allow", Action: "dynamodb:*", Resource: "*" }, { Sid: "OfficeOnly", Effect: "Deny", Action: "*", Resource: "*", Condition: { NotIpAddress: { "aws:SourceIp": ["203.0.113.0/24"] } } }]),
    req: { action: "dynamodb:Scan", resource: "arn:aws:dynamodb:eu-west-1:123456789012:table/orders", context: "aws:SourceIp=198.51.100.7" },
    note: "Change the IP to 203.0.113.40 (inside the office range).",
  },
  {
    label: "Boundary caps an admin",
    identity: P([{ Sid: "Admin", Effect: "Allow", Action: "*", Resource: "*" }]),
    boundary: P([{ Sid: "OnlyDataServices", Effect: "Allow", Action: ["s3:*", "dynamodb:*", "cloudwatch:*"], Resource: "*" }]),
    req: { action: "iam:CreateUser", resource: "arn:aws:iam::123456789012:user/eve", context: "" },
    note: "The identity policy says everything, the boundary says only data services: the effective permission is the intersection.",
  },
  {
    label: "SCP region guardrail",
    identity: P([{ Sid: "Ec2", Effect: "Allow", Action: "ec2:*", Resource: "*" }]),
    scp: P([{ Sid: "AllowAll", Effect: "Allow", Action: "*", Resource: "*" }, { Sid: "EuOnly", Effect: "Deny", NotAction: ["iam:*", "sts:*", "cloudfront:*"], Resource: "*", Condition: { StringNotEquals: { "aws:RequestedRegion": ["eu-west-1", "eu-central-1"] } } }]),
    req: { action: "ec2:RunInstances", resource: "arn:aws:ec2:us-east-1:123456789012:instance/*", context: "aws:RequestedRegion=us-east-1" },
    note: "Organisations use SCPs as guardrails. Switch the region to eu-west-1.",
  },
  {
    label: "Bucket policy grants",
    identity: P([]),
    resource: P([{ Sid: "AnalyticsRead", Effect: "Allow", Principal: { AWS: "arn:aws:iam::123456789012:user/alice" }, Action: "s3:GetObject", Resource: "arn:aws:s3:::acme-analytics/*" }]),
    req: { action: "s3:GetObject", resource: "arn:aws:s3:::acme-analytics/daily.parquet", context: "" },
    note: "No identity policy at all, yet allowed: in the same account a resource policy can grant access by itself.",
  },
];

export function lab(view) {
  const docs = { identity: "", resource: "", boundary: "", scp: "" };
  let tab = "identity";
  const TABS = [["identity", "Identity policy"], ["resource", "Resource policy"], ["boundary", "Permissions boundary"], ["scp", "SCP"]];

  view.innerHTML = `
    ${labHero("IAM", "lemon", "IAM Policy Evaluator", "Paste policies, describe a request and see the decision exactly as AWS reaches it: explicit deny → SCP → resource policy → permissions boundary → identity policy → implicit deny, with a trace for every statement.")}
    <div class="filters"><span class="muted">Presets:</span>${IAM_PRESETS.map((p, i) => `<button class="btn small" data-preset="${i}">${esc(p.label)}</button>`).join("")}</div>
    <div class="lab-grid halves">
      <div class="panel clay">
        <div class="tabs" id="polTabs">${TABS.map(([k, l]) => `<button data-t="${k}">${l}<span class="dot-on" data-on="${k}"></span></button>`).join("")}</div>
        <textarea id="pol" class="code code-editor" spellcheck="false" rows="16" placeholder="Leave empty if this policy type does not apply."></textarea>
        <p class="muted" id="presetNote" style="font-size:.85rem"></p>
      </div>
      <div class="panel clay iam-req">
        <h3>Request</h3>
        <label>Principal<input type="text" id="who" value="arn:aws:iam::123456789012:user/alice"></label>
        <label>Action<input type="text" id="act" placeholder="s3:GetObject"></label>
        <label>Resource ARN<input type="text" id="res"></label>
        <label>Context keys <span class="muted">(one key=value per line)</span><textarea id="ctx" class="code short" rows="3" placeholder="aws:SourceIp=203.0.113.10"></textarea></label>
        <button class="btn primary" id="evalBtn">Evaluate</button>
        <div id="decision"></div>
      </div>
    </div>
    <div class="panel clay" id="trace" style="margin-top:1.2rem"></div>`;

  const ta = $("#pol");
  const drawTabs = () => {
    $$("#polTabs button").forEach((b) => b.classList.toggle("active", b.dataset.t === tab));
    $$("[data-on]").forEach((d) => d.classList.toggle("on", !!docs[d.dataset.on].trim()));
    ta.value = docs[tab];
  };
  ta.addEventListener("input", () => {
    docs[tab] = ta.value;
    $$("[data-on]").forEach((d) => d.classList.toggle("on", !!docs[d.dataset.on].trim()));
  });
  $("#polTabs").onclick = (e) => {
    const t = e.target.closest("[data-t]")?.dataset.t;
    if (t) { tab = t; drawTabs(); }
  };
  const loadPreset = (p) => {
    Object.assign(docs, { identity: p.identity || "", resource: p.resource || "", boundary: p.boundary || "", scp: p.scp || "" });
    tab = "identity";
    $("#act").value = p.req.action;
    $("#res").value = p.req.resource;
    $("#ctx").value = p.req.context;
    $("#presetNote").textContent = p.note || "";
    drawTabs();
    run();
  };
  const run = () => {
    let r;
    try {
      const parsed = Object.fromEntries(Object.entries(docs).map(([k, v]) => [k, parseDoc(v, TABS.find((t) => t[0] === k)[1])]));
      const context = Object.fromEntries($("#ctx").value.split("\n").map((l) => l.trim()).filter(Boolean).map((l) => {
        const i = l.indexOf("=");
        return i < 0 ? [l, ""] : [l.slice(0, i).trim(), l.slice(i + 1).trim()];
      }));
      r = evaluate(parsed, { principal: $("#who").value.trim(), action: $("#act").value.trim(), resource: $("#res").value.trim(), context });
    } catch (e) {
      $("#decision").innerHTML = `<div class="run-error">${esc(e.message)}</div>`;
      $("#trace").innerHTML = "";
      return;
    }
    const allow = r.decision === "Allow";
    $("#decision").innerHTML = `<div class="iam-decision ${allow ? "allow" : "deny"}"><b>${r.decision.toUpperCase()}</b><span>${esc(r.reason)}</span></div>`;
    const ladder = ["Any explicit Deny?", "SCP allows?", "Resource policy allows?", "Boundary allows?", "Identity policy allows?"];
    $("#trace").innerHTML = `
      <h3>Evaluation order</h3>
      <ol class="iam-ladder">${ladder.map((l, i) => `<li class="${i + 1 < r.step ? "passed" : i + 1 === r.step ? (allow ? "allow" : "deny") : "skipped"}">${esc(l)}</li>`).join("")}</ol>
      <h3>Statements</h3>
      ${r.sets.length ? r.sets.map((s) => `<div class="iam-set"><b>${esc(s.name)}</b>${s.rows.length ? s.rows.map((row) => `
        <div class="iam-row ${row.applies ? (row.effect === "Deny" ? "deny" : "allow") : "skip"}">
          <span class="pill ${row.applies ? (row.effect === "Deny" ? "bad" : "ok") : "neutral"}">${esc(row.effect)}</span>
          <code>${esc(row.sid)}</code>
          <span>${row.applies ? "matches this request" : esc(row.why.join("; "))}</span>
        </div>`).join("") : `<div class="muted">no statements</div>`}</div>`).join("") : `<div class="muted">No policies at all: implicit deny.</div>`}
      <p class="muted" style="font-size:.78rem">Variables available: ${Object.keys(r.ctx).map((k) => `<code>\${${esc(k)}}</code>`).join(" ")}. Simplified model: same-account requests, no session policies or cross-account trust.</p>`;
  };
  $("#evalBtn").onclick = run;
  ["#act", "#res", "#who"].forEach((s) => $(s).addEventListener("keydown", (e) => e.key === "Enter" && run()));
  view.addEventListener("click", (e) => {
    const i = e.target.closest("[data-preset]")?.dataset.preset;
    if (i !== undefined) loadPreset(IAM_PRESETS[+i]);
  });
  const handed = takeHandoff("iam-policy");
  if (handed) {
    loadPreset({ identity: handed, req: { action: "s3:GetObject", resource: "arn:aws:s3:::example-bucket/file.txt", context: "" }, note: "Policy loaded from the lesson. Adjust the request to probe it." });
  } else loadPreset(IAM_PRESETS[0]);
}

// ===================================================================== VPC reachability
const VPC_TOGGLES = [
  ["igw", "Internet gateway attached to the VPC"],
  ["pubRoute", "Public route table: 0.0.0.0/0 → IGW"],
  ["webIp", "Web server has a public IP"],
  ["webSg", "Web SG: allow 443 from 0.0.0.0/0"],
  ["nacl", "Public subnet NACL: allow 443 in, ephemeral ports out"],
  ["appSg", "App SG: allow 8080 from web SG"],
  ["dbSg", "DB SG: allow 5432 from app SG"],
  ["nat", "NAT gateway in the public subnet"],
  ["privRoute", "Private route table: 0.0.0.0/0 → NAT"],
  ["s3ep", "S3 gateway endpoint on the private route table"],
  ["dbWide", "DB SG: allow 5432 from 10.0.0.0/16 (too wide)"],
  ["appPublic", "Private route table → IGW and app SG open to the world (misconfig)"],
  ["peerLink", "Peering / Transit Gateway connection is active"],
  ["peerRoutes", "Both VPC route tables include the peer CIDR route"],
  ["peerSg", "Remote DB SG allows traffic from the app SG"],
];
const VPC_PRESETS = {
  good: { label: "Correct 3-tier", igw: 1, pubRoute: 1, webIp: 1, webSg: 1, nacl: 1, appSg: 1, dbSg: 1, nat: 1, privRoute: 1, s3ep: 1, dbWide: 0, appPublic: 0 },
  noroute: { label: "Forgot the IGW route", igw: 1, pubRoute: 0, webIp: 1, webSg: 1, nacl: 1, appSg: 1, dbSg: 1, nat: 1, privRoute: 1, s3ep: 0, dbWide: 0, appPublic: 0 },
  nonat: { label: "No NAT", igw: 1, pubRoute: 1, webIp: 1, webSg: 1, nacl: 1, appSg: 1, dbSg: 1, nat: 0, privRoute: 0, s3ep: 0, dbWide: 0, appPublic: 0 },
  open: { label: "Too open", igw: 1, pubRoute: 1, webIp: 1, webSg: 1, nacl: 1, appSg: 1, dbSg: 1, nat: 1, privRoute: 1, s3ep: 0, dbWide: 1, appPublic: 1 },
};
Object.values(VPC_PRESETS).forEach((p) => { p.peerLink ??= 1; p.peerRoutes ??= 1; p.peerSg ??= 1; });
VPC_PRESETS.peerroute = { ...VPC_PRESETS.good, label: "Cross-VPC route missing", peerRoutes: 0 };
const SPOTS = {
  internet: [8, 12], igw: [30, 12], web: [30, 42], nat: [48, 42], app: [30, 78], db: [62, 78], s3: [90, 30], ep: [80, 62], peerNet: [88, 55], peerDb: [88, 82],
};
const CHECKS = [
  { id: "in-web", label: "Internet → web :443", want: true, hops: (t) => [
    ["internet", "Client sends to the web server's public IP", t.webIp, "the instance has no public IP, so there is nothing to reach"],
    ["igw", "Internet gateway translates public ↔ private IP", t.igw, "no internet gateway is attached"],
    ["web", "Public subnet route back to the internet", t.pubRoute, "no 0.0.0.0/0 → IGW route: replies cannot leave"],
    ["web", "NACL allows 443 in and ephemeral ports out (stateless)", t.nacl, "the NACL blocks it; remember NACLs need the return ports too"],
    ["web", "Security group allows 443 (stateful)", t.webSg, "the web SG does not allow 443 inbound"],
  ] },
  { id: "web-app", label: "Web → app :8080", want: true, hops: (t) => [
    ["web", "VPC local route 10.0.0.0/16 (always present)", true, ""],
    ["app", "App SG allows 8080 from the web SG", t.appSg, "the app SG does not reference the web SG"],
  ] },
  { id: "app-db", label: "App → database :5432", want: true, hops: (t) => [
    ["app", "VPC local route", true, ""],
    ["db", "DB SG allows 5432 from the app SG", t.dbSg || t.dbWide, "the DB SG does not allow the app"],
  ] },
  { id: "app-out", label: "App → internet (OS updates)", want: true, hops: (t) => [
    ["app", "Private route 0.0.0.0/0 → NAT", t.privRoute || t.appPublic, "the private route table has no default route"],
    ...(t.appPublic && !t.privRoute ? [["igw", "Direct to IGW (the subnet is effectively public!)", t.igw, "no internet gateway"]] : [
      ["nat", "NAT gateway exists in the public subnet", t.nat, "there is no NAT gateway"],
      ["igw", "NAT's subnet routes to the IGW", t.pubRoute && t.igw, "the public subnet has no IGW route, so NAT has no way out"],
    ]),
    ["internet", "Reaches the package mirror", true, ""],
  ] },
  { id: "app-s3", label: "App → S3", want: true, hops: (t) => t.s3ep ? [
    ["app", "Prefix-list route to the S3 gateway endpoint", true, ""],
    ["ep", "Gateway endpoint: private, free, no NAT data charges", true, ""],
    ["s3", "Bucket reached", true, ""],
  ] : [
    ["app", "No endpoint: default route → NAT", t.privRoute, "no default route and no S3 endpoint"],
    ["nat", "Through the NAT gateway (paid per GB)", t.nat, "no NAT gateway"],
    ["igw", "Out via the IGW to S3's public endpoint", t.pubRoute && t.igw, "the public subnet has no IGW route"],
    ["s3", "Bucket reached", true, ""],
  ] },
  { id: "in-app", label: "Internet → app :8080 (should fail)", want: false, hops: (t) => [
    ["internet", "Attacker targets the app server", true, ""],
    ["igw", "Internet gateway", t.igw, "no IGW"],
    ["app", "Private subnet routes to the IGW and has a public IP", t.appPublic, "private subnet has no IGW route (good: it is truly private)"],
    ["app", "App SG allows 8080 from anywhere", t.appPublic, "app SG only allows the web SG"],
  ] },
  { id: "web-db", label: "Web → database (should fail)", want: false, hops: (t) => [
    ["web", "VPC local route", true, ""],
    ["db", "DB SG allows the web tier", t.dbWide, "DB SG only allows the app SG (least privilege)"],
  ] },
  { id: "cross-vpc", label: "App → peer VPC database :5432", want: true, hops: (t) => [
    ["app", "Source route table sends the peer CIDR to peering / Transit Gateway", t.peerRoutes, "add the remote VPC CIDR route to the source route table"],
    ["peerNet", "Peering or Transit Gateway connection is active", t.peerLink, "accept the peering connection or attach both VPCs to the Transit Gateway"],
    ["peerDb", "Remote route table sends return traffic to the source VPC", t.peerRoutes, "add the reciprocal route in the remote VPC route table"],
    ["peerDb", "Remote DB SG allows 5432 from the app SG", t.peerSg, "allow the app SG (or a narrow source CIDR) on the database port"],
  ] },
];

function vpcPlayground(view) {
  let t = { ...VPC_PRESETS.good };
  let active = CHECKS[0].id;
  let anim;

  view.innerHTML = `
    ${labHero("VPC", "sky", "VPC Reachability", "A classic three-tier VPC. Toggle gateways, routes, security groups and NACLs, then trace a packet hop by hop to see where it gets through and where it is dropped.")}
    <div class="filters"><span class="muted">Presets:</span>${Object.entries(VPC_PRESETS).map(([k, p]) => `<button class="btn small" data-preset="${k}">${esc(p.label)}</button>`).join("")}</div>
    <div class="lab-grid side-left">
      <aside class="panel clay vpc-toggles">${VPC_TOGGLES.map(([k, l]) => `<label class="check"><input type="checkbox" data-k="${k}"> ${esc(l)}</label>`).join("")}</aside>
      <div class="lab-main">
        <div class="panel clay vpc-stage" id="vpc"></div>
        <div class="vpc-checks" id="checks"></div>
        <div class="panel clay" id="hops"></div>
      </div>
    </div>`;

  const results = () => CHECKS.map((c) => {
    const hops = c.hops(t);
    const fail = hops.findIndex(([, , ok]) => !ok);
    return { ...c, list: hops, fail, reach: fail < 0 };
  });

  const drawStage = () => {
    const on = (k) => !!t[k];
    const box = (id, label, sub, show = true) => show ? `<div class="vpc-node" data-spot="${id}" style="left:${SPOTS[id][0]}%;top:${SPOTS[id][1]}%"><b>${label}</b><span>${sub}</span></div>` : "";
    $("#vpc").innerHTML = `
      <div class="vpc-box"><span class="vpc-tag">VPC 10.0.0.0/16</span></div>
      <div class="subnet pub"><span class="vpc-tag">Public subnet 10.0.1.0/24 ${on("pubRoute") ? "· 0/0 → IGW" : "· no IGW route"}</span></div>
      <div class="subnet priv"><span class="vpc-tag">Private subnet 10.0.2.0/24 ${on("privRoute") ? "· 0/0 → NAT" : on("appPublic") ? "· 0/0 → IGW (!)" : "· local only"}</span></div>
      ${box("internet", "Internet", "0.0.0.0/0")}
      ${box("igw", "IGW", on("igw") ? "attached" : "missing", true)}
      ${box("web", "Web EC2", on("webIp") ? "10.0.1.10 · 54.x.x.x" : "10.0.1.10")}
      ${box("nat", "NAT GW", on("nat") ? "elastic IP" : "none")}
      ${box("app", "App EC2", "10.0.2.20")}
      ${box("db", "RDS", "10.0.2.30")}
      ${box("s3", "S3", "regional service")}
      ${box("ep", "S3 endpoint", "gateway", on("s3ep"))}
      ${box("peerNet", "Peering / TGW", on("peerLink") ? "connected" : "disconnected")}
      ${box("peerDb", "Peer VPC DB", "10.1.2.30")}
      <span class="vpc-packet" id="pkt"></span>`;
    $$(".vpc-node").forEach((n) => {
      const id = n.dataset.spot;
      n.classList.toggle("off", (id === "igw" && !on("igw")) || (id === "nat" && !on("nat")));
    });
  };

  const animate = (r) => {
    anim?.cancel();
    const pkt = $("#pkt");
    const pts = r.list.slice(0, r.fail < 0 ? r.list.length : r.fail + 1).map(([s]) => SPOTS[s]);
    if (!pts.length || matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    pkt.className = `vpc-packet ${r.reach ? "ok" : "bad"}`;
    anim = pkt.animate(pts.map(([x, y]) => ({ left: `${x}%`, top: `${y}%` })).concat(r.fail >= 0 ? [{ left: `${pts.at(-1)[0]}%`, top: `${pts.at(-1)[1]}%`, transform: "translate(-50%,-50%) scale(1.8)", opacity: 0 }] : []), { duration: 700 * Math.max(pts.length, 2), fill: "forwards", easing: "ease-in-out" });
  };

  const draw = () => {
    $$("[data-k]").forEach((i) => (i.checked = !!t[i.dataset.k]));
    drawStage();
    const all = results();
    $("#checks").innerHTML = all.map((r) => {
      const good = r.reach === r.want;
      return `<button class="vpc-check ${r.id === active ? "active" : ""} ${good ? "good" : "bad"}" data-check="${r.id}">
        <b>${esc(r.label)}</b><span class="pill ${r.reach ? "ok" : "bad"}">${r.reach ? "reachable" : "blocked"}</span><small>${good ? "as intended" : r.want ? "should work" : "security risk!"}</small></button>`;
    }).join("");
    const r = all.find((x) => x.id === active);
    $("#hops").innerHTML = `<h3>${esc(r.label)}</h3><ol class="hop-list">${r.list.map(([spot, text, ok, why], i) => `
      <li class="${r.fail >= 0 && i > r.fail ? "skipped" : ok ? "ok" : "bad"}"><b>${esc(text)}</b>${!ok && i === r.fail ? `<span>Dropped: ${esc(why)}</span>` : ""}</li>`).join("")}</ol>
      <p class="muted" style="font-size:.8rem;margin-bottom:0">${r.reach === r.want ? "This matches the intended design." : r.want ? "This path should work. Fix the hop marked in red." : "This should be blocked! Least privilege: keep private tiers private."}</p>`;
    animate(r);
  };

  view.addEventListener("change", (e) => {
    const k = e.target.dataset.k;
    if (!k) return;
    t[k] = e.target.checked ? 1 : 0;
    draw();
  });
  view.addEventListener("click", (e) => {
    const p = e.target.closest("[data-preset]")?.dataset.preset;
    const c = e.target.closest("[data-check]")?.dataset.check;
    if (p) t = { ...VPC_PRESETS[p] };
    else if (c) active = c;
    else return;
    draw();
  });
  draw();
  return () => anim?.cancel();
}

const EKS_TOGGLES = [
  ["endpoint", "Admin network can reach the EKS API endpoint"],
  ["accessEntry", "IAM principal has an EKS access entry"],
  ["rbac", "Kubernetes RBAC grants the requested action"],
  ["capacity", "Managed node group / Karpenter has capacity"],
  ["podIps", "Private subnets have free pod IPs"],
  ["cni", "Amazon VPC CNI is healthy"],
  ["podIdentity", "Pod Identity agent and association are ready"],
  ["s3Policy", "Pod role allows s3:GetObject"],
  ["igw", "Public subnets route to an Internet Gateway"],
  ["albController", "AWS Load Balancer Controller is installed"],
  ["targetSg", "Target security group allows traffic from the ALB"],
  ["dbSg", "Database SG allows 5432 from the app SG"],
];
const EKS_PRESETS = {
  healthy: { label: "Healthy cluster", endpoint: 1, accessEntry: 1, rbac: 1, capacity: 1, podIps: 1, cni: 1, podIdentity: 1, s3Policy: 1, igw: 1, albController: 1, targetSg: 1, dbSg: 1 },
  noAccess: { label: "IAM has no cluster access", endpoint: 1, accessEntry: 0, rbac: 1, capacity: 1, podIps: 1, cni: 1, podIdentity: 1, s3Policy: 1, igw: 1, albController: 1, targetSg: 1, dbSg: 1 },
  noIps: { label: "Pods stuck: subnet IPs exhausted", endpoint: 1, accessEntry: 1, rbac: 1, capacity: 1, podIps: 0, cni: 1, podIdentity: 1, s3Policy: 1, igw: 1, albController: 1, targetSg: 1, dbSg: 1 },
  noPodRole: { label: "Pod cannot read S3", endpoint: 1, accessEntry: 1, rbac: 1, capacity: 1, podIps: 1, cni: 1, podIdentity: 0, s3Policy: 1, igw: 1, albController: 1, targetSg: 1, dbSg: 1 },
  noIngress: { label: "Ingress has no working ALB", endpoint: 1, accessEntry: 1, rbac: 1, capacity: 1, podIps: 1, cni: 1, podIdentity: 1, s3Policy: 1, igw: 0, albController: 1, targetSg: 1, dbSg: 1 },
};
const EKS_CHECKS = [
  { id: "admin", label: "kubectl → EKS API", want: true, hops: (t) => [
    ["admin", "Admin CLI obtains an IAM identity", true, "configure AWS CLI credentials or an assumed role"],
    ["api", "Network can reach the cluster endpoint", t.endpoint, "check public/private endpoint access and the admin network or VPN"],
    ["entry", "EKS access entry maps IAM to Kubernetes access", t.accessEntry, "create an access entry for the IAM principal"],
    ["rbac", "Kubernetes RBAC allows the requested action", t.rbac, "associate an access policy or bind a least-privilege Kubernetes role"],
  ] },
  { id: "schedule", label: "Deployment → running pod", want: true, hops: (t) => [
    ["deploy", "Deployment creates a pod", true, "apply a valid Deployment manifest"],
    ["capacity", "Scheduler finds node capacity", t.capacity, "scale a managed node group or let Karpenter provision a node"],
    ["ips", "Subnet has an available VPC address for the pod", t.podIps, "expand subnet CIDRs, add a secondary CIDR, or enable prefix delegation"],
    ["cni", "VPC CNI assigns the pod IP", t.cni, "check the aws-node DaemonSet, IAM permissions and CNI logs"],
  ] },
  { id: "s3", label: "Pod → S3 with its own role", want: true, hops: (t) => [
    ["pod", "Pod runs with a Kubernetes service account", true, "set serviceAccountName on the workload"],
    ["identity", "Pod Identity agent and association provide temporary credentials", t.podIdentity, "install the agent and map the namespace/service account to an IAM role"],
    ["policy", "Role policy allows s3:GetObject", t.s3Policy, "grant only the required bucket and object actions"],
    ["s3", "Request reaches the S3 endpoint", true, "add an S3 gateway endpoint for private subnet traffic, or route through NAT"],
  ] },
  { id: "ingress", label: "Internet → ALB → pod", want: true, hops: (t) => [
    ["internet", "Client sends HTTPS request", true, "the client can reach the public internet"],
    ["igw", "Public subnet route reaches the Internet Gateway", t.igw, "use public subnets with a default route to an attached IGW"],
    ["controller", "AWS Load Balancer Controller reconciles the Ingress", t.albController, "install the controller and grant its IAM role the required permissions"],
    ["sg", "Target security group allows traffic from the ALB security group", t.targetSg, "allow the app port from the ALB SG; avoid opening it to the world"],
    ["pod", "Healthy pod is registered in the target group", t.capacity && t.podIps && t.cni, "make sure nodes, pod IP capacity and readiness probes are healthy"],
  ] },
  { id: "database", label: "App pod → RDS :5432", want: true, hops: (t) => [
    ["pod", "App pod has a VPC CNI address", t.cni && t.podIps, "restore VPC CNI health and free subnet IP capacity"],
    ["route", "VPC local route connects the private subnets", true, "keep the app and database subnets in routed VPC address space"],
    ["db", "RDS SG allows 5432 from the app workload SG", t.dbSg, "allow the database port from the app security group only"],
    ["rds", "Connection reaches the RDS endpoint", true, "check DNS resolution and the database listener"],
  ] },
];

function eksPlayground(view) {
  let t = { ...EKS_PRESETS.healthy };
  let active = EKS_CHECKS[0].id;
  view.innerHTML = `
    ${labHero("EKS", "lilac", "Amazon EKS Simulator", "Trace cluster access, pod scheduling, AWS identity and network traffic. Toggle access entries, subnet IP capacity, the VPC CNI, load balancer routing and security groups to find the first broken hop.")}
    <div class="filters"><span class="muted">Scenarios:</span>${Object.entries(EKS_PRESETS).map(([k, p]) => `<button class="btn small" data-eks-preset="${k}">${esc(p.label)}</button>`).join("")}</div>
    <div class="lab-grid side-left">
      <aside class="panel clay vpc-toggles"><h3>Cluster & network settings</h3>${EKS_TOGGLES.map(([k, l]) => `<label class="check"><input type="checkbox" data-eks-k="${k}"> ${esc(l)}</label>`).join("")}</aside>
      <div class="lab-main"><div class="panel clay"><h3>Choose a path</h3><div class="vpc-checks" id="eksChecks"></div></div>
        <div class="panel clay"><h3 id="eksPathTitle">Path trace</h3><div class="eks-path" id="eksPath"></div></div>
        <div class="panel clay" id="eksHops"></div>
      </div>
    </div>`;

  const getResults = () => EKS_CHECKS.map((c) => {
    const hops = c.hops(t);
    const fail = hops.findIndex(([, , ok]) => !ok);
    return { ...c, list: hops, fail, reach: fail < 0 };
  });
  const draw = () => {
    $$(`[data-eks-k]`, view).forEach((i) => { i.checked = !!t[i.dataset.eksK]; });
    const all = getResults();
    $("#eksChecks", view).innerHTML = all.map((r) => {
      const good = r.reach === r.want;
      return `<button class="vpc-check ${r.id === active ? "active" : ""} ${good ? "good" : "bad"}" data-eks-check="${r.id}">
        <b>${esc(r.label)}</b><span class="pill ${r.reach ? "ok" : "bad"}">${r.reach ? "reachable" : "blocked"}</span><small>${good ? "as intended" : r.want ? "should work" : "blocked as expected"}</small></button>`;
    }).join("");
    const r = all.find((x) => x.id === active);
    $("#eksPathTitle", view).textContent = r.label;
    $("#eksPath", view).innerHTML = r.list.map(([id, label], i) => {
      const state = r.fail >= 0 && i > r.fail ? "waiting" : i === r.fail ? "failed" : "passed";
      return `${i ? `<span class="eks-path-arrow" aria-hidden="true">→</span>` : ""}<div class="eks-path-node ${state}"><b>${esc(label)}</b><span>${esc(id.toUpperCase())}</span></div>`;
    }).join("");
    $("#eksHops", view).innerHTML = `<h3>${esc(r.label)}</h3><ol class="hop-list">${r.list.map(([id, text, ok, why], i) => `
      <li class="${r.fail >= 0 && i > r.fail ? "skipped" : ok ? "ok" : "bad"}"><b>${esc(text)}</b>${!ok && i === r.fail ? `<span>Fix: ${esc(why)}</span>` : ""}</li>`).join("")}</ol>
      <p class="muted" style="font-size:.8rem;margin-bottom:0">${r.reach === r.want ? "This path works as configured." : "The first broken dependency is marked in red. Fix it, then trace the path again."}</p>`;
  };
  view.addEventListener("change", (e) => {
    const k = e.target.dataset.eksK;
    if (!k) return;
    t[k] = e.target.checked ? 1 : 0;
    draw();
  });
  view.addEventListener("click", (e) => {
    const preset = e.target.closest("[data-eks-preset]")?.dataset.eksPreset;
    const check = e.target.closest("[data-eks-check]")?.dataset.eksCheck;
    if (preset && EKS_PRESETS[preset]) t = { ...EKS_PRESETS[preset] };
    else if (check) active = check;
    else return;
    draw();
  });
  draw();
}

export function playground(view) {
  let mode = "network";
  let cleanup = () => {};
  const draw = () => {
    cleanup();
    view.innerHTML = `<div class="filters aws-sim-modes" role="group" aria-label="AWS simulator">
      <b>Simulator:</b>
      <button type="button" class="btn small ${mode === "network" ? "active" : ""}" data-aws-mode="network">VPC Networking</button>
      <button type="button" class="btn small ${mode === "eks" ? "active" : ""}" data-aws-mode="eks">EKS & Kubernetes</button>
    </div><div id="awsSimMount"></div>`;
    const mount = $("#awsSimMount", view);
    cleanup = mode === "eks" ? (eksPlayground(mount) || (() => {})) : vpcPlayground(mount);
  };
  const onClick = (e) => {
    const next = e.target.closest("[data-aws-mode]")?.dataset.awsMode;
    if (!next || next === mode) return;
    mode = next;
    draw();
  };
  view.addEventListener("click", onClick);
  draw();
  return () => { cleanup(); view.removeEventListener("click", onClick); };
}
