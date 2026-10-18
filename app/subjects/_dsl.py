"""Tiny helpers that keep subject content files readable."""

from textwrap import dedent


def code(text: str) -> str:
    return dedent(text).strip() + "\n"


def ex(title: str, level: str, description: str, lang: str, src: str, runnable: bool = True) -> dict:
    return {"title": title, "level": level, "description": description, "lang": lang, "code": code(src), "runnable": runnable}


def qa(level: str, q: str, a: str) -> dict:
    return {"level": level, "q": q, "a": a}


def node(id: str, label: str, x: float, y: float, tint: str = "sky", sub: str = "", shape: str = "box", hidden: bool = False) -> dict:
    return {"id": id, "label": label, "x": x, "y": y, "tint": tint, "sub": sub, "shape": shape, "hidden": hidden}


def pkt(a: str, b: str, label: str = "", tint: str = "") -> dict:
    return {"from": a, "to": b, "label": label, "tint": tint}


def step(title: str, text: str, active=(), packets=(), set: dict | None = None) -> dict:
    return {"title": title, "text": text, "active": list(active), "packets": list(packets), "set": set or {}}


def flow(nodes: list, links: list, steps: list) -> dict:
    return {"nodes": nodes, "links": [list(l) for l in links], "steps": steps}


_TINTS = ("sky", "mint", "lemon", "lilac", "peach", "rose", "slate")


def chain(*stages: tuple) -> dict:
    """Left-to-right flow with one step per stage.

    Each stage is (label, sub, step_title, step_text) with an optional fifth item: the packet label
    carried from the previous stage. Up to 4 stages sit on one row; 5-8 snake over two rows.
    """
    n = len(stages)
    assert 2 <= n <= 8, "chain() needs 2-8 stages"
    per_row = n if n <= 4 else (n + 1) // 2
    nodes, steps = [], []
    for i, st in enumerate(stages):
        label, sub, title, text = st[:4]
        row, col = divmod(i, per_row)
        if row:
            col = per_row - 1 - col
        x = 12 + col * (76 / max(per_row - 1, 1))
        y = 50 if n <= 4 else (28 if row == 0 else 74)
        nid = f"s{i}"
        nodes.append(node(nid, label, round(x, 1), y, _TINTS[i % len(_TINTS)], sub, "box"))
        packets = [pkt(f"s{i - 1}", nid, st[4] if len(st) > 4 else "", _TINTS[i % len(_TINTS)])] if i else []
        steps.append(step(title, text, [nid], packets))
    links = [(f"s{i}", f"s{i + 1}") for i in range(n - 1)]
    return flow(nodes, links, steps)


def topic(id: str, title: str, category: str, level: str, code: str, tagline: str, analogy: str, what: str,
          use_cases: list, key_points: list, examples: list, commands: list, gotchas: list, interview: list,
          related: list, flow: dict) -> dict:
    return {"id": id, "title": title, "category": category, "level": level, "code": code, "tagline": tagline,
            "analogy": analogy, "what": what, "use_cases": use_cases, "key_points": key_points, "examples": examples,
            "commands": commands, "gotchas": gotchas, "interview": interview, "related": related, "flow": flow}
