import { $, esc, highlightCode } from "../util.js";
import { labHero } from "./common.js";

const presets = {
  static: (host, upstream) => `server {\n  listen 80;\n  server_name ${host};\n  root /srv/www;\n  index index.html;\n\n  location / {\n    try_files $uri $uri/ =404;\n  }\n\n  location = /healthz {\n    access_log off;\n    return 200 'ok';\n  }\n}`,
  proxy: (host, upstream) => `upstream app_pool {\n  least_conn;\n  server ${upstream}:8080;\n}\n\nserver {\n  listen 80;\n  server_name ${host};\n\n  location / {\n    proxy_pass http://app_pool;\n    proxy_set_header Host $host;\n    proxy_set_header X-Real-IP $remote_addr;\n    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n    proxy_set_header X-Forwarded-Proto $scheme;\n  }\n}`,
  tls: (host, upstream) => `server {\n  listen 443 ssl;\n  server_name ${host};\n  ssl_certificate /etc/ssl/${host}.crt;\n  ssl_certificate_key /etc/ssl/${host}.key;\n  ssl_protocols TLSv1.2 TLSv1.3;\n\n  location / {\n    proxy_pass http://${upstream}:8080;\n    proxy_set_header Host $host;\n    proxy_set_header X-Forwarded-Proto https;\n  }\n}`,
};

const clean = (value, fallback) => /^[a-zA-Z0-9.-]{1,100}$/.test(value) ? value : fallback;

export function lab(view, content) {
  view.innerHTML = `${labHero("NGX", "mint", "NGINX Config Lab", "Assemble a small NGINX server configuration and inspect the request path. These examples are for learning; validate paths and upstream trust before deploying.")}
    <section class="panel clay" style="margin-top:1rem">
      <div class="row">
        <label>Pattern<select id="nginxPattern"><option value="static">Static site</option><option value="proxy">Reverse proxy + upstream</option><option value="tls">TLS reverse proxy</option></select></label>
        <label>Hostname<input id="nginxHost" value="learn.example.test" maxlength="100"></label>
        <label>Upstream host<input id="nginxUpstream" value="app.internal" maxlength="100"></label>
      </div>
    </section>
    <section class="panel clay" style="margin-top:1rem"><div class="row"><h3 style="margin:0">Generated nginx.conf</h3><span class="pill neutral">NGINX syntax</span></div><pre class="code" id="nginxConfig"></pre></section>
    <section class="panel clay" style="margin-top:1rem"><h3>Request walkthrough</h3><div class="flow-list" id="nginxFlow"></div><p class="muted" id="nginxNote"></p></section>`;
  const draw = () => {
    const host = clean($("#nginxHost", view).value.trim(), "learn.example.test");
    const upstream = clean($("#nginxUpstream", view).value.trim(), "app.internal");
    const mode = $("#nginxPattern", view).value;
    $("#nginxConfig", view).innerHTML = highlightCode(presets[mode](host, upstream), "nginx");
    const steps = mode === "static"
      ? [["1 · Listen", "Accept HTTP on port 80 and match the configured host."], ["2 · Match", "Choose the location block for this URI."], ["3 · Serve", "Try the requested file and directory, otherwise return 404."]]
      : [["1 · Listen", mode === "tls" ? "Accept HTTPS and complete the TLS handshake with this certificate." : "Accept HTTP and match the configured host."], ["2 · Match", "Select the location that handles this request path."], ["3 · Proxy", `Send the request to ${upstream}:8080 and relay the upstream response.`]];
    $("#nginxFlow", view).innerHTML = steps.map(([title, text]) => `<article class="panel"><b>${esc(title)}</b><p>${esc(text)}</p></article>`).join("");
    $("#nginxNote", view).textContent = mode === "tls" ? "This lab displays configuration shape; install a valid certificate and test TLS behavior for your own hostname." : "Use nginx -t to validate syntax, then verify real requests and error logs after a controlled reload.";
  };
  view.querySelectorAll("#nginxPattern, #nginxHost, #nginxUpstream").forEach((control) => {
    control.addEventListener("input", draw);
    control.addEventListener("change", draw);
  });
  draw();
}

export function playground(view) {
  lab(view, { topics: [] });
}
