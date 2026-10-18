import { $, highlightCode } from "../util.js";
import { scenarioLab } from "./catalog.js";

export function lab(view, content) {
  scenarioLab(view, "NODE", "mint", "Node.js Code Lab", "Diagnose event-loop blocking, unbounded streams and missed cancellation with production-shaped scenarios.", content);
}

export function playground(view) {
  view.innerHTML = `<section class="topic-hero clay"><div class="code tint-mint">JS</div><div><h1>Node.js Service Builder</h1><div class="muted">Tune request timeout, body limits and graceful termination for a small HTTP service.</div></div></section><div class="grid two" style="margin-top:1rem"><section class="panel clay"><label>Request timeout (ms) <b id="nodeTimeoutLabel">5000</b><input id="nodeTimeout" type="range" min="250" max="30000" step="250" value="5000"></label><label>Maximum body size (KB) <b id="nodeBodyLabel">256</b><input id="nodeBody" type="range" min="16" max="4096" step="16" value="256"></label><label class="check" style="display:flex;gap:.6rem;margin-top:.6rem"><input id="nodeSignal" type="checkbox" checked> Pass AbortSignal to downstream fetch</label></section><section class="panel clay"><h3>Service sketch</h3><pre id="nodeCode" class="code" style="white-space:pre-wrap"></pre><div id="nodeHint" class="muted"></div></section></div>`;
  const draw = () => {
    const timeout = +$("#nodeTimeout", view).value, body = +$("#nodeBody", view).value, signal = $("#nodeSignal", view).checked;
    $("#nodeTimeoutLabel", view).textContent = timeout; $("#nodeBodyLabel", view).textContent = body;
    const code = `const server = http.createServer(async (req, res) => {\n  const controller = new AbortController();\n  const timer = setTimeout(() => controller.abort(), ${timeout});\n  try {\n    // Reject bodies larger than ${body} KB while streaming.\n    const response = await fetch(UPSTREAM, {${signal ? " signal: controller.signal" : ""} });\n    res.writeHead(response.status);\n    await pipeline(response.body, res); // respects downstream backpressure\n  } catch (err) {\n    if (!res.headersSent) res.writeHead(err.name === 'AbortError' ? 504 : 502);\n    res.end();\n  } finally { clearTimeout(timer); }\n});\n\nprocess.on('SIGTERM', () => server.close(() => process.exit(0)));`;
    $("#nodeCode", view).innerHTML = highlightCode(code, "javascript");
    $("#nodeHint", view).textContent = "Also enforce the body limit in a streaming parser and put a bounded deadline on graceful shutdown; this sketch highlights the control points rather than serving as a drop-in framework.";
  };
  view.querySelectorAll("#nodeTimeout, #nodeBody, #nodeSignal").forEach((el) => { el.addEventListener("input", draw); el.addEventListener("change", draw); });
  draw();
}
