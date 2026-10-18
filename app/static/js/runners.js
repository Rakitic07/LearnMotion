import { api, esc } from "./util.js";
import { track } from "./account.js";

export const runSql = (sql, explain = false) => {
  track("run_code", { detail: explain ? "sql explain" : "sql" });
  return api("/api/sql/run", { sql, explain });
};
export const runPython = (code, { trace = false, stdin = "" } = {}) => {
  track("run_code", { detail: trace ? "python trace" : "python" });
  return api("/api/python/run", { code, trace, stdin });
};

function planTree(plan) {
  const depth = new Map([[0, -1]]);
  return `<div class="plan">${plan.map((p) => {
    const d = (depth.get(p.parent) ?? -1) + 1;
    depth.set(p.id, d);
    const kind = /SCAN/.test(p.detail) ? "scan" : /SEARCH|INDEX/.test(p.detail) ? "seek" : "other";
    return `<div class="plan-row ${kind}" style="--d:${d}"><span class="pill ${kind === "scan" ? "warn" : kind === "seek" ? "ok" : "neutral"}">${kind === "scan" ? "scan" : kind === "seek" ? "index" : "step"}</span> ${esc(p.detail)}</div>`;
  }).join("")}</div>`;
}

export function sqlResultHtml(r) {
  if (!r) return "";
  const blocks = (r.results || []).map((res, i) => {
    const head = `<div class="res-head"><span class="pill neutral">#${i + 1}</span><code>${esc(res.sql.length > 90 ? res.sql.slice(0, 90) + "…" : res.sql)}</code></div>`;
    if (res.columns) {
      if (res.columns.length === 4 && res.columns[3] === "detail" && res.sql.toUpperCase().startsWith("EXPLAIN")) {
        return head + planTree(res.rows.map(([id, parent, , detail]) => ({ id, parent, detail })));
      }
      const table = `<div class="res-table"><table><thead><tr>${res.columns.map((c) => `<th>${esc(c)}</th>`).join("")}</tr></thead><tbody>${
        res.rows.length ? res.rows.map((row) => `<tr>${row.map((v) => `<td class="${v === null ? "null" : typeof v === "number" ? "num" : ""}">${v === null ? "NULL" : esc(v)}</td>`).join("")}</tr>`).join("") : `<tr><td colspan="${res.columns.length}" class="muted">0 rows</td></tr>`
      }</tbody></table></div>`;
      const meta = `<div class="muted res-meta">${res.rows.length} row${res.rows.length === 1 ? "" : "s"}${res.truncated ? " (truncated)" : ""}</div>`;
      return head + table + meta + (res.plan?.length ? `<div class="muted res-meta">Query plan</div>${planTree(res.plan)}` : "");
    }
    return head + `<div class="muted res-meta">OK${res.changes >= 0 ? ` · ${res.changes} row${res.changes === 1 ? "" : "s"} changed` : ""}</div>`;
  });
  const err = r.error ? `<div class="run-error"><b>Error${r.failed !== undefined ? ` in statement ${r.failed + 1}` : ""}:</b> ${esc(r.error)}</div>` : "";
  return `<div class="run-out">${blocks.join("")}${err}<div class="muted res-meta">${r.ms ?? 0} ms · fresh copy of the shop database</div></div>`;
}

export function pyResultHtml(r) {
  if (!r) return "";
  const out = r.stdout ? `<pre class="term-out">${esc(r.stdout)}</pre>` : `<div class="muted res-meta">No output.</div>`;
  const e = r.error;
  const err = e ? `<div class="run-error"><b>${esc(e.type || "Error")}${e.line ? ` (line ${e.line})` : ""}:</b> ${esc(e.message || "")}${e.trace ? `<pre>${esc(e.trace)}</pre>` : ""}</div>` : "";
  return `<div class="run-out">${out}${err}<div class="muted res-meta">${r.ms ?? 0} ms · sandboxed Python ${r.ok ? "" : "· failed"}</div></div>`;
}
