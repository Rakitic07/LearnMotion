import { $, highlightCode } from "../util.js";
import { scenarioLab } from "./catalog.js";

export function lab(view, content) {
  scenarioLab(view, "GO", "sky", "Go Code Lab", "Diagnose common Go failures using context, errors, races and profiling evidence.", content);
}

export function playground(view, content) {
  view.innerHTML = `<section class="topic-hero clay"><div class="code tint-sky">GO</div><div><h1>Go Practice Bench</h1><div class="muted">Tune a safe HTTP server skeleton and inspect the request lifecycle.</div></div></section><section class="panel clay" style="margin-top:1rem"><label>Read-header timeout (seconds) <b id="goTimeoutLabel">5</b><input id="goTimeout" type="range" min="1" max="30" value="5"></label><label class="check" style="display:flex;gap:.6rem;margin-top:.6rem"><input type="checkbox" id="goGraceful" checked> Include graceful shutdown and context cancellation</label><pre class="code" id="goCode" style="white-space:pre-wrap;margin-top:1rem"></pre></section>`;
  const draw = () => {
    const timeout = +$("#goTimeout", view).value;
    $("#goTimeoutLabel", view).textContent = timeout;
    const code = `srv := &http.Server{\n    Addr: \":8080\",\n    Handler: mux,\n    ReadHeaderTimeout: ${timeout} * time.Second,\n}\n\nif err := srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {\n    log.Fatal(err)\n}` + ($("#goGraceful", view).checked ? `\n\nctx, stop := signal.NotifyContext(context.Background(), os.Interrupt)\ndefer stop()\n<-ctx.Done()\nshutdownCtx, cancel := context.WithTimeout(context.Background(), 10*time.Second)\ndefer cancel()\n_ = srv.Shutdown(shutdownCtx)` : "");
    $("#goCode", view).innerHTML = highlightCode(code, "go");
  };
  $("#goTimeout", view).addEventListener("input", draw);
  $("#goGraceful", view).addEventListener("change", draw);
  draw();
}
