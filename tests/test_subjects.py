import json

import pytest

from app import create_app, pyexec, sqlrun, subjects

HEADERS = {"X-K8s-Playground": "1"}
LOGO_SUBJECTS = {"db", "git", "python", "aws", "linux", "java"}
NEW = ["db", "sysdesign", "git", "python", "aws", "linux", "java", "cicd", "dsa", "qa", "ds", "ml"]
TOPIC_KEYS = ("id", "title", "category", "level", "tagline", "analogy", "what", "use_cases", "key_points",
              "examples", "commands", "gotchas", "interview", "related", "flow")
EXPECTED_SQL_ERRORS = ("CHECK constraint failed", "FOREIGN KEY constraint failed")


@pytest.fixture()
def client():
    return create_app().test_client()


def test_subjects_endpoint(client):
    data = client.get("/api/subjects").get_json()
    ids = [s["id"] for s in data]
    assert ids[0] == "k8s" and set(NEW) <= set(ids)
    for s in data:
        assert s["topics"] >= 50 and s["questions"] >= 100, s["id"]
        assert len(s["blobs"]) == 4, s["id"]


@pytest.mark.parametrize("sid", NEW)
def test_content_endpoint(client, sid):
    data = client.get(f"/api/content?subject={sid}").get_json()
    assert data["subject"]["id"] == sid
    assert len(data["topics"]) >= 10
    assert client.get("/api/content?subject=nope").status_code == 404


@pytest.mark.parametrize("sid", NEW)
def test_topics_complete_and_linked(sid):
    c = subjects.content(sid)
    ids = {t["id"] for t in c["topics"]}
    assert len(ids) == len(c["topics"]), f"{sid} duplicate topic ids"
    cats = {cat["id"] for cat in c["categories"]}
    for t in c["topics"]:
        for key in TOPIC_KEYS:
            assert t.get(key), f"{sid}/{t['id']} missing {key}"
        assert t["category"] in cats
        assert set(t["related"]) <= ids, f"{sid}/{t['id']} bad related"
        assert len(t["interview"]) >= 4
        flow = t["flow"]
        nodes = {n["id"] for n in flow["nodes"]}
        for link in flow["links"]:
            assert link[0] in nodes and link[1] in nodes, f"{sid}/{t['id']} link {link}"
        assert flow["steps"]
        for st in flow["steps"]:
            assert set(st.get("active", [])) <= nodes
            assert set(st.get("set", {})) <= nodes
            for p in st.get("packets", []):
                assert p["from"] in nodes and p["to"] in nodes
    for sc in c.get("scenarios", []):
        assert sc["topic"] in ids, f"{sid} scenario topic {sc['topic']}"
    json.dumps(c)


def test_k8s_topics_have_scene_or_flow():
    c = subjects.content("k8s")
    ids = {t["id"] for t in c["topics"]}
    assert len(ids) == len(c["topics"])
    for t in c["topics"]:
        assert t.get("scene") or t.get("flow", {}).get("steps"), t["id"]
        assert set(t["related"]) <= ids and len(t["interview"]) >= 4, t["id"]
        assert all(ex.get("yaml") for ex in t["examples"]), t["id"]
    assert all(sc["topic"] in ids for sc in c["scenarios"])


def test_java_examples_are_static_java():
    for t in subjects.content("java")["topics"]:
        for ex in t["examples"]:
            assert ex["lang"] == "java" and not ex["runnable"], f"{t['id']}: {ex['title']}"


NODE_CHECK = """
const root = process.argv[2];
const { ShellSim } = await import(root + "/labs/shellsim.js");
const { CHALLENGES } = await import(root + "/labs/linux.js");
const { analyze } = await import(root + "/labs/java.js");
const { TASKS } = await import(root + "/labs/javadata.js");
const examples = JSON.parse(process.argv[3]);
const fails = [];
for (const e of examples) {
  const s = new ShellSim();
  for (const line of e.code.split("\\n").map((l) => l.trim()).filter((l) => l && !l.startsWith("#"))) {
    const out = s.run(line);
    if (/command not found|invalid option|usage:|syntax error|not simulated/.test(out)) fails.push(`${e.where}: ${line}: ${out.trim()}`);
  }
}
for (const c of CHALLENGES) {
  const s = new ShellSim();
  (c.setup || []).forEach((l) => s.run(l));
  if (c.check(s, "")) fails.push(`challenge solved before start: ${c.title}`);
  let out = "";
  for (const l of c.solution) out = s.run(l);
  if (!c.check(s, out)) fails.push(`challenge solution fails: ${c.title}`);
}
for (const t of TASKS) for (const v of t.versions) {
  const r = analyze(v.code);
  if (r.min > Math.max(8, v.v)) fails.push(`java ${t.id}@${v.v} detected as ${r.min}`);
}
console.log(JSON.stringify(fails));
"""


def test_browser_labs_logic_with_node(tmp_path):
    import shutil
    import subprocess
    from pathlib import Path

    node = shutil.which("node")
    if not node:
        pytest.skip("node not installed")
    root = Path(__file__).resolve().parent.parent / "app" / "static" / "js"
    examples = [{"where": f"{t['id']}/{ex['title']}", "code": ex["code"]}
                for t in subjects.content("linux")["topics"] for ex in t["examples"] if ex["runnable"]]
    stub = "globalThis.localStorage={getItem:()=>null,setItem(){}};globalThis.document={documentElement:{dataset:{}},querySelector:()=>null};"
    script = tmp_path / "check.mjs"
    script.write_text(stub + NODE_CHECK)
    res = subprocess.run([node, str(script), root.as_uri(), json.dumps(examples)], capture_output=True, text=True, timeout=60)
    assert res.returncode == 0, res.stderr
    assert json.loads(res.stdout.strip().splitlines()[-1]) == []


def test_db_examples_run_on_seed():
    for t in subjects.content("db")["topics"]:
        for ex in t["examples"]:
            if ex["lang"] != "sql" or not ex["runnable"]:
                continue
            r = sqlrun.run(ex["code"])
            assert r["ok"] or any(e in r["error"] for e in EXPECTED_SQL_ERRORS), f"{t['id']}: {ex['title']}: {r.get('error')}"


@pytest.mark.parametrize("sid", ["python", "sysdesign", "dsa", "qa", "ds", "ml", "cicd"])
def test_python_examples_run(sid):
    for t in subjects.content(sid)["topics"]:
        for ex in t["examples"]:
            if ex["lang"] == "python" and ex["runnable"]:
                r = pyexec.run(ex["code"])
                assert r["ok"] or r["error"]["type"] != "SyntaxError", f"{t['id']}: {ex['title']}"
                assert r["ok"], f"{t['id']}: {ex['title']}: {r['error']}"


def test_sql_runner_basics_and_sandbox():
    r = sqlrun.run("SELECT COUNT(*) FROM customers", explain=True)
    assert r["ok"] and r["results"][0]["rows"] == [[12]]
    sqlrun.run("DELETE FROM customers")
    assert sqlrun.run("SELECT COUNT(*) FROM customers")["results"][0]["rows"] == [[12]]
    for bad in ("ATTACH DATABASE ':memory:' AS x", "SELECT load_extension('x')", "PRAGMA writable_schema = ON"):
        try:
            res = sqlrun.run(bad)
        except sqlrun.SQLError:
            continue
        assert not res["ok"], bad


def test_sql_runner_timeout():
    r = sqlrun.run("WITH RECURSIVE c(x) AS (SELECT 1 UNION ALL SELECT x + 1 FROM c) SELECT COUNT(*) FROM c")
    assert not r["ok"] and "3 seconds" in r["error"]


def test_python_runner_output_trace_and_limits():
    r = pyexec.run("x = [1]\ny = x\ny.append(2)\nprint(x)", trace=True)
    assert r["ok"] and r["stdout"] == "[1, 2]\n"
    last = r["steps"][-1]["stack"][0]["vars"]
    assert last["x"]["id"] == last["y"]["id"]
    assert pyexec.run("print(input())", stdin="hi")["stdout"] == "hi\n"
    assert pyexec.run("1/0")["error"]["type"] == "ZeroDivisionError"
    r = pyexec.run("while True: pass")
    assert not r["ok"] and "Stopped" in r["error"]["message"]
    r = pyexec.run("import os\nprint(sorted(k for k in os.environ if 'KEY' in k or 'TOKEN' in k or 'SECRET' in k))")
    assert r["stdout"].strip() == "[]"


def test_runner_endpoints_require_header(client):
    assert client.post("/api/sql/run", json={"sql": "SELECT 1"}).status_code == 403
    assert client.post("/api/python/run", json={"code": "print(1)"}).status_code == 403
    assert client.post("/api/sql/run", json={"sql": "SELECT 1"}, headers=HEADERS).get_json()["ok"]
    assert client.post("/api/python/run", json={"code": "print(1)"}, headers=HEADERS).get_json()["stdout"] == "1\n"


@pytest.mark.parametrize("sid", NEW)
def test_frontend_modules_served(client, sid):
    for path in (f"/static/js/labs/{sid}.js", f"/static/js/gamedata/{sid}.js"):
        res = client.get(path)
        assert res.status_code == 200, path
        res.close()
    for path in ("/static/js/landing.js", "/static/js/flow.js", "/static/js/labs/gitsim.js", "/static/js/labs/shellsim.js",
                 "/static/js/labs/javadata.js", "/static/css/subjects.css", "/static/img/app-logo.png", f"/static/img/{sid}-logo.png" if sid in LOGO_SUBJECTS else "/static/js/icons.js"):
        res = client.get(path)
        assert res.status_code == 200, path
        res.close()


def test_search_index_covers_every_topic(client):
    rows = client.get("/api/search-index").get_json()
    keys = {(r["sid"], r["id"]) for r in rows}
    for s in subjects.SUBJECTS:
        for t in subjects.content(s["id"])["topics"]:
            assert (s["id"], t["id"]) in keys
    assert all(r["title"] and r["subject"] and r["level"] for r in rows)
    res = client.get("/static/js/search.js")
    assert res.status_code == 200
    res.close()
