"""Small helper for focused subject catalogs with consistent runnable lesson fields."""

import re

from ._dsl import chain, ex, qa, topic


def _example_language(source, prefix):
    """Attach a useful lexer to generated examples instead of defaulting every snippet to text."""
    code = str(source).strip()
    first = code.splitlines()[0].strip() if code else ""
    if re.match(r"(?:terraform|nginx|node|npm|npx|go|kubectl|docker|curl|openssl|ps|tail|grep|cp|namei|python|pytest|java|javac)\s", first):
        return "bash"
    if prefix == "NGX":
        return "nginx"
    if prefix in {"JS", "NODE", "NJS"}:
        return "jsx" if re.search(r"<[A-Z][\w.]*\b|<[a-z][\w-]*(?:\s+\w+\s*=|\s*/?>)", code) else "javascript"
    if prefix == "RCT":
        return "jsx"
    if prefix in {"TF", "TERR"}:
        return "hcl"
    if prefix in {"CSS"}:
        return "css"
    if prefix in {"JAVA"}:
        return "java"
    if prefix in {"PY", "PYTH"}:
        return "python"
    if prefix in {"GO"}:
        return "go"
    if re.match(r"(?:resource|data|module|provider|variable|output|terraform|locals|moved|check|ephemeral)\s*[\"{]", code):
        return "hcl"
    if re.match(r"(?:package\s+\w+|func\s+\w+|type\s+\w+\s+struct)", code):
        return "go"
    if re.match(r"(?:def\s+\w+\s*\(|from\s+\w+\s+import|class\s+\w+\s*:\s*$)", code):
        return "python"
    if re.match(r"(?:public\s+class|package\s+\w|System\.out\.|public\s+static)", code):
        return "java"
    if re.match(r"(?:const|let|var|function|import|export|async function)\b", code) or "=>" in code:
        return "javascript"
    return "text"


def build_lessons(rows, prefix, analogy):
    lessons = []
    for row in rows:
        (id, title, category, level, what, example, key, question, answer, *related) = row
        lessons.append(topic(
            id, title, category, level, prefix, f"{title} in practice", analogy,
            what,
            ["Choosing an implementation for a real service.", "Debugging the behavior using observable evidence."],
            [key, "Start with the failure mode and verify the intended behavior with a focused check."],
            [ex("Try it", level, "A small configuration or command to make this concept concrete.", _example_language(example, prefix), example, runnable=False)],
            [example, "Check the runtime metrics and logs before changing production settings."],
            ["A happy-path demo does not establish delivery, failure recovery or security guarantees."],
            [qa(level, question, answer)], related,
            chain(("Input", "request or event", "Observe the input", "Identify the relevant request, event or configuration."),
                  ("Runtime", "policy + state", "Apply the rule", key),
                  ("Evidence", "result + telemetry", "Verify behavior", "Check the result and the evidence that explains it.")),
        ))
    return lessons


def build_guided_catalog(rows, prefix, analogy):
    """Build compact but actionable catalog lessons from focused practice rows.

    Each row is (id, title, category, level, explanation, example, question,
    answer[, related]).
    """
    lessons = []
    for row in rows:
        id, title, category, level, explanation, example, question, answer, *tail = row
        related = tail[0] if tail else []
        key = f"{title}: {example}"
        lessons.append(topic(
            id, title, category, level, prefix, f"{title} in practice", analogy,
            explanation,
            ["Start with the smallest representative example.", "Verify the result using logs, metrics or a diff before applying broadly."],
            [key, "Keep the configuration reviewable and make failure behavior explicit."],
            [ex("Practice example", level, "A compact starting point to adapt and validate.", _example_language(example, prefix), example, runnable=False)],
            [example, "Review the generated output and confirm it matches the intended scope."],
            ["A successful syntax check does not prove the runtime identity, permissions or target scope are correct."],
            [qa(level, question, answer)], related,
            chain(("Input", "declaration or event", "Inspect the source", "Identify the exact input, target and owner."),
                  ("Apply", title, "Run the focused operation", key),
                  ("Verify", "result + evidence", "Check state and telemetry", "Confirm the outcome, failure mode and rollback path.")),
        ))
    return lessons


def build_practice_catalog(rows, prefix, analogy):
    """Build concise, practical lessons from (id,title,category,level,what,try) rows."""
    guided = []
    for id, title, category, level, what, practice in rows:
        guided.append((id, title, category, level, what, practice,
                       f"What should you verify when applying {title}?",
                       f"{what} Practice: {practice} Confirm the change is scoped to the intended environment, inspect the resulting state, and keep a rollback path.", []))
    return build_guided_catalog(guided, prefix, analogy)
