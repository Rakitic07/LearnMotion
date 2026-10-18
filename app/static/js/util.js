export const $ = (sel, root = document) => root.querySelector(sel);
export const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

const ESC = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
export const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ESC[c]);

// Escapes, then lets long identifiers (requiredDuringSchedulingIgnoredDuringExecution) wrap at camelCase humps.
export const prose = (s) => esc(s).replace(/[A-Za-z][A-Za-z0-9./-]{17,}/g, (w) => w.replace(/([a-z0-9])(?=[A-Z])|([./-])(?=\w)/g, "$1$2<wbr>"));

export function el(html) {
  const t = document.createElement("template");
  t.innerHTML = html.trim();
  return t.content.firstElementChild;
}

export async function api(path, body) {
  const opts = body === undefined ? {} : {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-K8s-Playground": "1" },
    body: JSON.stringify(body),
  };
  try {
    const res = await fetch(path, opts);
    const data = await res.json().catch(() => ({ ok: false, error: `HTTP ${res.status}` }));
    if (!res.ok && data.ok === undefined) data.ok = false;
    return data;
  } catch (err) {
    return { ok: false, error: String(err) };
  }
}

let toastTimer;
export function toast(msg, bad = false) {
  const t = $("#toast");
  t.textContent = msg;
  t.className = `toast clay${bad ? " bad" : ""}`;
  t.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => (t.hidden = true), 2600);
}

export async function copy(text) {
  try {
    await navigator.clipboard.writeText(text);
    toast("Copied to clipboard");
  } catch {
    toast("Copy failed — select and copy manually", true);
  }
}

export const store = {
  get(key, fallback) {
    try {
      const v = localStorage.getItem(`k8s-everything:${key}`);
      return v === null ? fallback : JSON.parse(v);
    } catch {
      return fallback;
    }
  },
  set(key, value) {
    localStorage.setItem(`k8s-everything:${key}`, JSON.stringify(value));
    window.dispatchEvent(new CustomEvent("lm:store", { detail: { key } }));
  },
  remove(key) {
    localStorage.removeItem(`k8s-everything:${key}`);
  },
  keys() {
    const prefix = "k8s-everything:";
    return Object.keys(localStorage).filter((k) => k.startsWith(prefix)).map((k) => k.slice(prefix.length));
  },
};

export async function send(method, path, body, headers = {}) {
  try {
    const res = await fetch(path, {
      method,
      headers: { "X-K8s-Playground": "1", ...(body === undefined ? {} : { "Content-Type": "application/json" }), ...headers },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    const data = await res.json().catch(() => ({ ok: false, error: `HTTP ${res.status}` }));
    return { ...data, ok: res.ok && data.ok !== false, status: res.status };
  } catch (err) {
    return { ok: false, status: 0, error: String(err) };
  }
}

function hlValue(v) {
  if (!v) return "";
  let comment = "";
  const ci = v.indexOf(" #");
  if (ci >= 0 && !/["']/.test(v)) {
    comment = v.slice(ci);
    v = v.slice(0, ci);
  }
  let out;
  const t = v.trim();
  if (/^(-?\d+(\.\d+)?|true|false|null)$/.test(t)) out = `<span class="n">${esc(v)}</span>`;
  else if (/^[[{|>]/.test(t)) out = esc(v);
  else out = `<span class="s">${esc(v)}</span>`;
  return out + (comment ? `<span class="c">${esc(comment)}</span>` : "");
}

export function highlightYaml(src) {
  return src.split("\n").map((line) => {
    if (/^\s*#/.test(line)) return `<span class="c">${esc(line)}</span>`;
    if (/^---/.test(line)) return `<span class="d">${esc(line)}</span>`;
    const m = line.match(/^(\s*(?:-\s+)*)([^\s:#\-[{][^:#]*?)(:)(\s+|$)(.*)$/);
    if (m) return `${esc(m[1])}<span class="k">${esc(m[2])}</span>${m[3]}${m[4]}${hlValue(m[5])}`;
    const li = line.match(/^(\s*-\s+)(.*)$/);
    if (li) return esc(li[1]) + hlValue(li[2]);
    return esc(line);
  }).join("\n");
}

const WORDS = (s) => new Set(s.split(" "));
const LANGS = {
  javascript: {
    comment: String.raw`//[^\n]*|/\*[\s\S]*?\*/`,
    keywords: WORDS("async await break case catch class const continue debugger default delete do else export extends finally for from function get if import in instanceof let new of return set static super switch this throw try typeof var void while with yield true false null undefined as satisfies type interface implements private protected public readonly enum namespace declare keyof infer unknown never any boolean number string symbol bigint override abstract constructor require module exports process global Buffer __dirname __filename"),
    builtins: WORDS("Array Object String Number Boolean Map Set Promise Math JSON Error Date RegExp Intl console window document fetch URL Headers AbortController FormData Response Request Symbol Proxy Reflect PromiseLike"),
  },
  css: {
    comment: String.raw`/\*[\s\S]*?\*/`,
    keywords: WORDS("important important from to and or not only screen print media supports container keyframes font-face property layer import namespace charset scope starting-style hover focus focus-visible active visited checked disabled enabled before after first-child last-child nth-child root host has where is not var calc min max clamp url linear-gradient radial-gradient color-mix rgb rgba hsl hsla transparent currentColor inherit initial unset revert auto none flex grid inline block absolute relative fixed sticky center stretch start end normal bold solid dashed dotted hidden visible clip scroll flow-root max-content min-content fit-content repeat subgrid nowrap wrap border-box content-box ease-in out forwards infinite alternate"),
    properties: WORDS("accent-color align-content align-items align-self animation animation-delay animation-direction animation-duration animation-fill-mode animation-iteration-count animation-name animation-timing-function appearance aspect-ratio backdrop-filter background background-color background-image background-position background-repeat background-size block-size border border-block border-color border-radius border-style border-width bottom box-shadow box-sizing color column-gap columns content cursor display fill filter flex flex-basis flex-direction flex-flow flex-grow flex-shrink flex-wrap float font font-family font-feature-settings font-size font-style font-weight gap grid grid-area grid-auto-columns grid-auto-flow grid-auto-rows grid-column grid-column-gap grid-row grid-template grid-template-areas grid-template-columns grid-template-rows height inline-size inset isolation justify-content justify-items justify-self left letter-spacing line-height list-style margin margin-block margin-block-end margin-block-start margin-bottom margin-inline margin-left margin-right margin-top max-height max-width min-height min-width object-fit object-position opacity order outline outline-color outline-offset outline-style outline-width overflow overflow-x overflow-y padding padding-block padding-bottom padding-inline padding-left padding-right padding-top pointer-events position resize right row-gap scale text-align text-decoration text-overflow text-shadow text-transform top transform transform-origin transition transition-delay transition-duration transition-property transition-timing-function user-select vertical-align visibility white-space width word-break word-wrap z-index"),
    builtins: WORDS("var calc min max clamp rgb rgba hsl hsla color-mix url linear-gradient radial-gradient conic-gradient"),
  },
  hcl: {
    comment: String.raw`#[^\n]*|//[^\n]*|/\*[\s\S]*?\*/`,
    keywords: WORDS("resource data module provider terraform variable output locals required_providers backend dynamic lifecycle provisioner connection import moved check removed ephemeral cloud workspace for_each count depends_on depends_on_each_sensitive sensitive nullable type default description validation condition error_message sensitive nullable true false null self each path module local var resource_count"),
    builtins: WORDS("string number bool list map set object tuple any yamldecode jsonencode file templatefile lookup merge coalesce flatten concat length contains keys values format replace join split cidrsubnet tostring tonumber toset tomap try can"),
  },
  go: {
    comment: String.raw`//[^\n]*|/\*[\s\S]*?\*/`,
    keywords: WORDS("package import const var type func return if else for range switch case default break continue fallthrough defer go select chan map struct interface nil true false iota make new append delete len cap panic recover goto") ,
    builtins: WORDS("error string bool byte rune int int8 int16 int32 int64 uint uint8 uint16 uint32 uint64 uintptr float32 float64 complex64 complex128 any comparable fmt context http os io json time sync errors log testing strconv bytes strings net url sort math reflect runtime") ,
  },
  groovy: {
    comment: String.raw`//[^\n]*|/\*[\s\S]*?\*/`,
    keywords: WORDS("as assert break case catch class const continue def default do else enum extends false finally for if implements import in instanceof interface new null package return super switch this throw throws trait true try while void static public private protected final override pipeline agent stages stage steps post script environment tools options parameters triggers when parallel matrix input timeout retry node sh bat echo checkout build parameters environment any none always success failure unstable") ,
    builtins: WORDS("String Integer Boolean List Map Set Closure GString println readFile writeFile sh checkout error library currentBuild params env") ,
  },
  json: { comment: null, keywords: WORDS("true false null"), builtins: new Set() },
  ini: { comment: String.raw`[;#][^\n]*`, keywords: new Set(), builtins: new Set(), properties: new Set() },
  dockerfile: {
    comment: String.raw`#[^\n]*`,
    keywords: WORDS("FROM RUN CMD LABEL EXPOSE ENV ADD COPY ENTRYPOINT VOLUME USER WORKDIR ARG ONBUILD STOPSIGNAL HEALTHCHECK SHELL AS"),
    builtins: new Set(),
  },
  sql: {
    comment: String.raw`--[^\n]*`,
    keywords: WORDS("select from where and or not in is null as join left right inner outer full cross on group by having order asc desc limit offset insert into values update set delete create table index unique primary key foreign references drop alter add column default check constraint begin commit rollback savepoint release transaction with recursive union all distinct case when then else end exists between like explain query plan pragma over partition rows range preceding following unbounded current row integer text real boolean timestamptz bigint uuid timeuuid view materialized if for share skip locked isolation level read committed serializable repeatable"),
    builtins: WORDS("count sum avg min max coalesce rank dense_rank row_number lag lead json_extract group_concat lower upper length date now"),
  },
  python: {
    comment: String.raw`#[^\n]*`,
    keywords: WORDS("def return if elif else for while in not and or is None True False class import from as with try except finally raise yield lambda pass break continue global nonlocal async await assert del match case"),
    builtins: WORDS("print len range list dict set tuple int str float bool sum min max sorted enumerate zip map filter isinstance type id iter next open super object repr abs any all round hash input"),
  },
  bash: {
    comment: String.raw`(?:^|(?<=\s))#[^\n]*`,
    keywords: WORDS("git aws kubectl curl cat echo cd export sudo dnf printf sha1sum gh sam cdk terraform pytest ls pwd mkdir touch rm cp mv chmod chown ln grep sed awk sort uniq cut wc head tail find xargs tee ps kill top systemctl journalctl ip ss dig ping tar df du mount strace lsof java javac jshell jwebserver mvn gradle"),
    builtins: WORDS("if then fi for do done in while case esac function return local set exit elif else"),
  },
  java: {
    comment: String.raw`//[^\n]*|/\*[\s\S]*?\*/`,
    keywords: WORDS("abstract assert boolean break byte case catch char class continue default do double else enum extends final finally float for if implements import instanceof int interface long native new package private protected public return short static strictfp super switch synchronized this throw throws transient try void volatile while var record sealed permits non-sealed yield when module exports requires true false null"),
    builtins: WORDS("String System Integer Long Double Boolean Object List Map Set Optional Stream Collectors Arrays Collections Files Path Paths Thread Executors HttpClient HttpRequest HttpResponse URI IO Math Record Override FunctionalInterface"),
  },
  nginx: {
    comment: String.raw`#[^\n]*`,
    keywords: WORDS("events http mail stream server location upstream map geo if limit_except split_clients server_name types include root alias index try_files return rewrite set break keepalive_timeout sendfile tcp_nopush tcp_nodelay client_max_body_size client_body_timeout client_header_timeout large_client_header_buffers error_page access_log error_log listen ssl ssl_certificate ssl_certificate_key ssl_protocols ssl_ciphers gzip gzip_types add_header expires proxy_pass proxy_set_header proxy_http_version proxy_connect_timeout proxy_read_timeout proxy_send_timeout proxy_buffering proxy_buffers proxy_redirect fastcgi_pass fastcgi_param uwsgi_pass grpc_pass auth_basic satisfy allow deny") ,
    builtins: WORDS("on off default_server default keepalive no_cache internal permanent redirect last named off always http2 http3 reuseport ipv6only ssl http_1_1 all none debug info notice warn error crit alert emerg main combined escape json") ,
  },
  // Fallback palette for snippets whose author did not mark a language.
  generic: {
    comment: String.raw`(?:^|(?<=\s))#[^\n]*|//[^\n]*`,
    keywords: WORDS("abstract and as async await break case catch class const continue def delete do else enum export extends false finally for from function if implements import in interface let match module new not null of or package private protected public return static struct super switch this throw true try type typeof undefined var void while with yield"),
    builtins: WORDS("Array Boolean Error Map Math Object Promise Set String JSON console document fetch len list dict print range self str int float bool true false null"),
  },
};

function highlightMarkup(src) {
  const tokens = /<!--[\s\S]*?-->|<\/?[A-Za-z][^>]*>/g;
  let out = "", last = 0;
  for (const match of src.matchAll(tokens)) {
    out += esc(src.slice(last, match.index)); last = match.index + match[0].length;
    const token = match[0];
    if (token.startsWith("<!--")) { out += `<span class="c">${esc(token)}</span>`; continue; }
    const tag = token.match(/^(<\/?)([A-Za-z][\w:-]*)/);
    if (!tag) { out += esc(token); continue; }
    let inner = `${esc(tag[1])}<span class="t">${esc(tag[2])}</span>`;
    const rest = token.slice(tag[0].length);
    inner += esc(rest).replace(/([\w:-]+)(=)("[^"<>]*"|'[^'<>]*')/g, '<span class="a">$1</span>$2<span class="s">$3</span>');
    out += inner;
  }
  return out + esc(src.slice(last));
}

function highlightJsx(src) {
  const tags = /<!--[\s\S]*?-->|<\/?[A-Za-z][^>]*>/g;
  let out = "", last = 0;
  for (const match of src.matchAll(tags)) {
    out += highlightCode(src.slice(last, match.index), "javascript");
    out += highlightMarkup(match[0]);
    last = match.index + match[0].length;
  }
  return out + highlightCode(src.slice(last), "javascript");
}

/** Single-pass tokenizer: escapes everything, then wraps comments, strings, numbers and keywords. */
export function highlightCode(src, lang = "text") {
  const requestedLang = String(lang || "text").toLowerCase();
  const aliases = { js: "javascript", jsx: "javascript", ts: "javascript", tsx: "javascript", typescript: "javascript", node: "javascript", nodejs: "javascript", "node.js": "javascript", react: "javascript", py: "python", yml: "yaml", terraform: "hcl", tf: "hcl", hcl: "hcl", sh: "bash", shell: "bash", properties: "ini", toml: "ini", http: "generic", text: "generic", markdown: "generic", gherkin: "generic", protobuf: "generic" };
  lang = aliases[requestedLang] || requestedLang;
  // Content in generated lesson catalogs is sometimes missing a language label.
  // Infer common formats from unmistakable syntax so those snippets still get colored.
  if (lang === "generic") {
    const trimmed = String(src).trimStart();
    if (/^(?:\{\s*["\w-]+\s*:|\[\s*(?:\{|"))/.test(trimmed)) lang = "json";
    else if (/^(?:resource|data|module|provider|variable|output|terraform)\s+"/.test(trimmed)) lang = "hcl";
    else if (/^(?:events|http|stream|mail|upstream|server|map|geo)\s*\{|^(?:\s*(?:listen|server_name|location|proxy_pass|root|try_files|worker_processes)\s+[^\n;]*;)/m.test(trimmed)) lang = "nginx";
    else if (/^(?:SELECT|INSERT|UPDATE|DELETE|CREATE|WITH)\b/i.test(trimmed)) lang = "sql";
    else if (/^(?:FROM|RUN|COPY|WORKDIR|ARG|ENTRYPOINT)\s+\S/m.test(trimmed)) lang = "dockerfile";
    else if (/^(?:from\s+[\w.]+\s+import\s|def\s+\w+\s*\(|class\s+\w+\s*(?:\([^\n]*\))?\s*:|if\s+__name__\s*==|print\s*\()/m.test(trimmed)) lang = "python";
    else if (/^(?:package\s+[\w.]+;|import\s+(?:java|javax)\.|public\s+(?:final\s+)?class\s|public\s+static\s+void\s+main\s*\(|System\.out\.|@Override\b)/m.test(trimmed)) lang = "java";
    else if (/^(?:\w[\w.-]*:|\s+-\s+\w)/m.test(trimmed) && /\n/.test(trimmed)) lang = "yaml";
    else if (/^(?:\s*(?:import |export |const |let |function |async function |interface |type ))/m.test(trimmed) || /=>/.test(trimmed)) lang = "javascript";
    else if (/^\s*<(?:(?:!doctype|html|head|body|main|section|article|div|p|button|input|form|ul|li)\b)/im.test(trimmed)) lang = "html";
    else if (/^\s*(?:\.[\w-]+|#[\w-]+|@media)\s*[{\n]/m.test(trimmed)) lang = "css";
    if (lang === "javascript" && /<[A-Z][\w.]*\b|<[a-z][\w-]*(?:\s+\w+\s*=|\s*\/?>)/.test(trimmed)) lang = "jsx";
  }
  if (lang === "yaml") return highlightYaml(src);
  if (lang === "jsx" || requestedLang === "jsx" || requestedLang === "tsx") return highlightJsx(src);
  if (lang === "html" || lang === "xml") return highlightMarkup(src);
  const L = LANGS[lang] || LANGS.generic;
  const str = lang === "java" ? String.raw`"""[\s\S]*?"""|"(?:[^"\\\n]|\\.)*"|'(?:[^'\\\n]|\\.)*'` : lang === "python" ? String.raw`"""[\s\S]*?"""|'''[\s\S]*?'''|[rbf]?"(?:[^"\\\n]|\\.)*"|[rbf]?'(?:[^'\\\n]|\\.)*'` : String.raw`"(?:[^"\\\n]|\\.)*"|'(?:[^'\\\n]|\\.)*'`;
  const parts = [L.comment, str, String.raw`#[\da-fA-F]{3,8}\b`, String.raw`\b\d[\d_]*(?:\.\d+)?\b`, String.raw`[A-Za-z_$][\w$.-]*`].filter(Boolean).map((p) => `(${p})`);
  const re = new RegExp(parts.join("|"), "gm");
  const hasComment = !!L.comment;
  let out = "";
  let last = 0;
  for (const m of src.matchAll(re)) {
    out += esc(src.slice(last, m.index));
    last = m.index + m[0].length;
    const [tok] = m;
    const g = hasComment ? m.slice(1) : [undefined, ...m.slice(1)];
    if (g[0]) out += `<span class="c">${esc(tok)}</span>`;
    else if (g[1]) out += lang === "json" && src.slice(last).match(/^\s*:/) ? `<span class="k">${esc(tok)}</span>` : `<span class="s">${esc(tok)}</span>`;
    else if (g[2]) out += `<span class="v">${esc(tok)}</span>`;
    else if (g[3]) out += `<span class="n">${esc(tok)}</span>`;
    else {
      const low = lang === "sql" ? tok.toLowerCase() : lang === "dockerfile" ? tok.toUpperCase() : tok;
      const after = src.slice(last);
      if (lang === "nginx" && /^\$[\w]+$/.test(tok)) out += `<span class="v">${esc(tok)}</span>`;
      else if ((lang === "css" && /^\s*:/.test(after)) || (lang === "hcl" && /^\s*=/.test(after)) || (lang === "ini" && /^\s*=/.test(after))) out += `<span class="a">${esc(tok)}</span>`;
      else if (L.keywords.has(low)) out += `<span class="k">${esc(tok)}</span>`;
      else if (L.builtins.has(low)) out += `<span class="f">${esc(tok)}</span>`;
      else out += esc(tok);
    }
  }
  return out + esc(src.slice(last));
}

export function enableTabIndent(textarea, width = 2) {
  const pad = " ".repeat(width);
  textarea.addEventListener("keydown", (e) => {
    if (e.key !== "Tab") return;
    e.preventDefault();
    const { selectionStart: s, selectionEnd: end, value } = textarea;
    textarea.value = value.slice(0, s) + pad + value.slice(end);
    textarea.selectionStart = textarea.selectionEnd = s + width;
  });
}

export const levelPill = (level) => `<span class="pill ${esc(level)}">${esc(level)}</span>`;
