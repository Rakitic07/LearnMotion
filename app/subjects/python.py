"""Python: the data model to async and the GIL. Every python example runs in the sandboxed runner."""

from ._dsl import ex, flow, node, pkt, qa, step

CATEGORIES = [
    {"id": "core", "title": "Core Language", "color": "sky", "blurb": "Objects, names and built-in collections."},
    {"id": "functions", "title": "Functions", "color": "mint", "blurb": "Arguments, scope, closures, decorators."},
    {"id": "oop", "title": "Objects & Protocols", "color": "lilac", "blurb": "Classes, dataclasses, iteration."},
    {"id": "robust", "title": "Robust Code", "color": "lemon", "blurb": "Errors and resource management."},
    {"id": "concurrency", "title": "Concurrency", "color": "peach", "blurb": "asyncio, threads, processes and the GIL."},
]

TOPICS = [
    {
        "id": "objects-mutability", "title": "Names, Objects & Mutability", "category": "core", "level": "basic", "code": "OB",
        "tagline": "Variables are labels on objects; mutation is visible through every label.",
        "analogy": "Sticky notes on boxes. b = a sticks a second note on the same box. Putting something in the box is visible to both notes; moving a note to another box is not.",
        "what": "Everything in Python is an object with an identity (id), a type and a value. Names are references bound to objects; assignment never copies. Mutable objects (list, dict, set) can change in place; immutable ones (int, str, tuple, frozenset) cannot, so 'changing' them rebinds the name to a new object. is compares identity, == compares value. Function arguments are passed by object reference ('call by sharing').",
        "use_cases": ["Understanding why a function modified your list.", "Choosing tuples for dictionary keys.", "Copying nested data safely (copy.deepcopy)."],
        "key_points": [
            "Mutable default arguments are created once at definition time.",
            "Use is only for None/True/False and identity checks.",
            "Shallow copies share nested objects; deepcopy does not.",
            "Hashable (immutable) objects can be dict keys and set members.",
        ],
        "examples": [
            ex("Two names, one list", "basic", "Step through it in the Visualizer to see both names point to the same object.", "python", """
                a = [1, 2]
                b = a
                b.append(3)
                print(a, a is b)
                b = b + [4]          # creates a new list, rebinding b
                print(a, b, a is b)
            """),
            ex("Mutable default argument", "intermediate", "The classic bug and its fix.", "python", """
                def add_bad(item, bucket=[]):
                    bucket.append(item)
                    return bucket

                def add_good(item, bucket=None):
                    bucket = [] if bucket is None else bucket
                    bucket.append(item)
                    return bucket

                print(add_bad(1), add_bad(2))
                print(add_good(1), add_good(2))
            """),
            ex("Shallow vs deep copy", "intermediate", "Nested lists stay shared after a shallow copy.", "python", """
                import copy
                grid = [[0, 0], [0, 0]]
                shallow = list(grid)
                deep = copy.deepcopy(grid)
                grid[0][0] = 9
                print("shallow:", shallow)
                print("deep:   ", deep)
            """),
        ],
        "commands": ["id(x) · type(x) · x is y · x == y", "copy.copy(x) · copy.deepcopy(x)", "hash(x) (immutable → hashable)", "def f(x=None): x = [] if x is None else x"],
        "gotchas": ["[[0] * 3] * 3 creates three references to the same inner list.", "x is 256 works by caching accident; never use is for numbers or strings.", "+= on a list mutates in place, but on a tuple it rebinds."],
        "interview": [
            qa("basic", "Is Python pass-by-value or pass-by-reference?", "Neither exactly: call by sharing (object reference). The function gets a reference to the same object; mutating it is visible to the caller, rebinding the parameter is not."),
            qa("basic", "is vs ==?", "is checks identity (same object), == checks equality via __eq__. Use is for None."),
            qa("intermediate", "Why is a mutable default argument a bug?", "Defaults are evaluated once when the function is defined, so the same list is shared across calls. Use None and create inside."),
            qa("intermediate", "Why can't lists be dict keys?", "Dict keys must be hashable with a stable hash; lists are mutable, so their hash could change while stored. Use tuples."),
        ],
        "related": ["collections", "functions-args"],
        "flow": flow(
            [node("a", "a", 12, 30, "sky", "name", "pill"), node("b", "b", 12, 72, "mint", "name", "pill"), node("l1", "list", 55, 50, "lilac", "[1, 2]"),
             node("l2", "list", 88, 72, "peach", "[1, 2, 3, 4]", hidden=True)],
            [("a", "l1"), ("b", "l1"), ("b", "l2")],
            [
                step("a = [1, 2]", "A list object is created; <b>a</b> refers to it.", ["a", "l1"], [pkt("a", "l1")]),
                step("b = a", "No copy! <b>b</b> is a second reference to the same list.", ["b", "l1"], [pkt("b", "l1", "same id")]),
                step("b.append(3)", "Mutating through b changes the one shared object, so a sees it too.", ["l1"], set={"l1": {"sub": "[1, 2, 3]"}}),
                step("b = b + [4]", "+ builds a <b>new</b> list; b is rebound. a still points to the old list.", ["b", "l2"], [pkt("b", "l2", "rebind")], {"l2": {"hidden": False}}),
            ],
        ),
    },
    {
        "id": "collections", "title": "Lists, Dicts, Sets & Tuples", "category": "core", "level": "basic", "code": "CO",
        "tagline": "Pick the right built-in: complexity, ordering and the collections module.",
        "analogy": "A list is a numbered queue of people, a dict is a coat check (ticket → coat), a set is a guest list where names can't repeat, a tuple is a sealed envelope.",
        "what": "list: ordered, mutable, O(1) append and index, O(n) insert/remove at the front and membership. dict: hash map, O(1) average get/set, insertion-ordered since 3.7. set: hash set, O(1) membership, set algebra. tuple: immutable sequence, hashable if contents are. collections adds deque (O(1) both ends), Counter, defaultdict, namedtuple, OrderedDict; heapq and bisect give priority queues and sorted inserts.",
        "use_cases": ["Deduplicate with a set.", "Count words with Counter.", "BFS queue with deque.", "Group items with defaultdict(list)."],
        "key_points": [
            "x in list is O(n); x in set/dict is O(1) average.",
            "list.pop(0) is O(n): use deque.popleft().",
            "dict.get(k, default) and setdefault avoid KeyError.",
            "Sorting is stable; use key= rather than cmp.",
        ],
        "examples": [
            ex("Counter and defaultdict", "basic", "Count and group in one line each.", "python", """
                from collections import Counter, defaultdict
                words = "the quick brown fox jumps over the lazy dog and the cat".split()
                print(Counter(words).most_common(2))
                by_len = defaultdict(list)
                for w in words:
                    by_len[len(w)].append(w)
                print(dict(by_len))
            """),
            ex("Membership cost", "intermediate", "Time list vs set lookups.", "python", """
                import time
                data = list(range(200_000))
                s = set(data)
                t = time.perf_counter(); [199_999 in data for _ in range(200)]; lt = time.perf_counter() - t
                t = time.perf_counter(); [199_999 in s for _ in range(200)]; st = time.perf_counter() - t
                print(f"list {lt*1000:.1f} ms vs set {st*1000:.3f} ms")
            """),
            ex("deque and heapq", "intermediate", "A queue for BFS and a priority queue for the smallest items.", "python", """
                from collections import deque
                import heapq
                q = deque([1]); q.append(2); q.appendleft(0)
                print(q.popleft(), list(q))
                tasks = [(3, "low"), (1, "urgent"), (2, "normal")]
                heapq.heapify(tasks)
                print([heapq.heappop(tasks)[1] for _ in range(3)])
            """),
        ],
        "commands": ["Counter(it).most_common(n)", "defaultdict(list)", "deque.append / appendleft / popleft", "heapq.heappush / heappop / nlargest", "sorted(xs, key=lambda x: x.age, reverse=True)", "a | b · a & b · a - b (sets)"],
        "gotchas": ["Modifying a dict while iterating over it raises RuntimeError.", "{} is an empty dict, not a set: use set().", "Using a list as a queue with pop(0) in a hot loop."],
        "interview": [
            qa("basic", "List vs tuple?", "Lists are mutable and for homogeneous sequences that change; tuples are immutable, hashable if their items are, slightly smaller and convey fixed structure (records)."),
            qa("intermediate", "How does a Python dict work?", "An open-addressing hash table: the key's hash picks a slot, collisions probe other slots, and a separate compact array keeps insertion order. Average O(1), resizes as it fills."),
            qa("intermediate", "How would you find the top 3 most frequent items?", "Counter(items).most_common(3), or heapq.nlargest(3, counts.items(), key=...)."),
            qa("basic", "How do you remove duplicates but keep order?", "list(dict.fromkeys(items)), since dicts keep insertion order."),
        ],
        "related": ["comprehensions", "objects-mutability"],
        "flow": flow(
            [node("k", "key 'cat'", 10, 50, "slate", "", "pill"), node("h", "hash()", 32, 50, "lemon", "→ 0x…a3", "round"),
             node("s0", "slot 0", 62, 14, "sky", "empty"), node("s3", "slot 3", 62, 38, "sky", "'dog' → 2"), node("s4", "slot 4", 62, 62, "sky", "empty"), node("s7", "slot 7", 62, 86, "sky", "empty"), node("v", "value", 90, 50, "mint", "1", "round")],
            [("k", "h"), ("h", "s3"), ("s3", "s4"), ("s4", "v")],
            [
                step("Hash the key", "d['cat'] = 1 starts by computing hash('cat').", ["k", "h"], [pkt("k", "h")]),
                step("Pick a slot", "The hash maps to slot 3, but 'dog' already lives there: a collision.", ["s3"], [pkt("h", "s3", "slot 3", "rose")]),
                step("Probe", "Python probes another slot and finds slot 4 free.", ["s4"], [pkt("s3", "s4", "probe")], {"s4": {"sub": "'cat' → 1", "tint": "mint"}}),
                step("O(1) lookup", "Reading d['cat'] repeats the same hash and probe: constant time on average.", ["s4", "v"], [pkt("s4", "v", "1")]),
            ],
        ),
    },
    {
        "id": "comprehensions", "title": "Comprehensions, Slicing & Unpacking", "category": "core", "level": "basic", "code": "CP",
        "tagline": "Pythonic one-liners: build, filter and destructure data.",
        "analogy": "A cookie cutter on a conveyor belt: for each piece of dough (iterable), if it passes inspection (condition), stamp a shape (expression).",
        "what": "List, dict and set comprehensions build collections from iterables: [expr for x in xs if cond]. Generator expressions (parentheses) produce items lazily. Slicing seq[start:stop:step] copies part of a sequence; negative indices count from the end. Unpacking assigns from iterables: a, *rest = xs; first, *_, last; and ** merges dicts. The walrus operator := assigns inside expressions.",
        "use_cases": ["Transforming API results into dicts.", "Filtering and flattening nested lists.", "Swapping variables: a, b = b, a."],
        "key_points": [
            "Prefer comprehensions for simple transforms, loops for complex logic.",
            "sum(x for x in xs) avoids building a list.",
            "Slices never raise IndexError; they clamp.",
            "seq[::-1] reverses; seq[:] makes a shallow copy.",
        ],
        "examples": [
            ex("Comprehensions", "basic", "List, dict and set comprehensions with a filter.", "python", """
                nums = range(1, 11)
                squares = [n * n for n in nums if n % 2 == 0]
                parity = {n: "even" if n % 2 == 0 else "odd" for n in range(4)}
                initials = {w[0] for w in ["apple", "avocado", "banana"]}
                print(squares, parity, initials)
            """),
            ex("Nested and flattening", "intermediate", "Read nested comprehensions left to right like loops.", "python", """
                matrix = [[1, 2, 3], [4, 5, 6]]
                flat = [x for row in matrix for x in row]
                transposed = [[row[i] for row in matrix] for i in range(3)]
                print(flat, transposed)
            """),
            ex("Slicing and unpacking", "basic", "Star unpacking, swap and walrus.", "python", """
                xs = [10, 20, 30, 40, 50]
                print(xs[1:4], xs[-2:], xs[::-1], xs[::2])
                first, *middle, last = xs
                a, b = 1, 2; a, b = b, a
                print(first, middle, last, a, b)
                if (n := len(xs)) > 3:
                    print("long list:", n)
                print({**{"a": 1}, **{"b": 2, "a": 3}})
            """),
        ],
        "commands": ["[f(x) for x in xs if p(x)]", "{k: v for k, v in pairs}", "(x for x in xs)  # lazy", "seq[start:stop:step]", "a, *rest = xs", "merged = {**d1, **d2} · d1 | d2"],
        "gotchas": ["Huge list comprehensions consume memory; use generators.", "Comprehension variables don't leak in Python 3, but loop variables do.", "Overly clever nested comprehensions hurt readability."],
        "interview": [
            qa("basic", "List comprehension vs generator expression?", "A list comprehension builds the whole list in memory immediately. A generator expression yields items lazily on demand, using constant memory, and can be consumed once."),
            qa("basic", "How do you reverse a list?", "xs[::-1] for a new reversed copy, xs.reverse() in place, or reversed(xs) for an iterator."),
            qa("intermediate", "What does a, *b, c = range(5) give?", "a = 0, b = [1, 2, 3], c = 4."),
            qa("intermediate", "When should you avoid a comprehension?", "When it has side effects, multiple nested conditions, or needs try/except: a regular loop is clearer."),
        ],
        "related": ["iterators-generators", "collections"],
        "flow": flow(
            [node("src", "range(1, 11)", 10, 50, "slate", "1…10", "pill"), node("f", "if n % 2 == 0", 38, 50, "lemon", "filter"), node("m", "n * n", 64, 50, "lilac", "map"),
             node("out", "result", 90, 50, "mint", "[]")],
            [("src", "f"), ("f", "m"), ("m", "out")],
            [
                step("Iterate", "The comprehension pulls one value at a time from the iterable.", ["src"], [pkt("src", "f", "1")]),
                step("Filter", "1 is odd: dropped. 2 passes.", ["f"], [pkt("src", "f", "2"), pkt("f", "m", "2")]),
                step("Transform", "The expression n * n turns 2 into 4.", ["m", "out"], [pkt("m", "out", "4")], {"out": {"sub": "[4]"}}),
                step("Repeat", "…until the iterable is exhausted.", ["out"], set={"out": {"sub": "[4, 16, 36, 64, 100]"}}),
            ],
        ),
    },
    {
        "id": "functions-args", "title": "Functions & Arguments", "category": "functions", "level": "basic", "code": "FN",
        "tagline": "Positional, keyword, *args, **kwargs, keyword-only and lambdas.",
        "analogy": "A coffee order form: required boxes (positional), optional boxes with defaults, a free-text 'extras' area (*args/**kwargs), and boxes you must label by name (keyword-only).",
        "what": "Functions are first-class objects. Parameters can be positional-or-keyword, positional-only (before /), keyword-only (after * or *args), with defaults, plus *args (extra positionals as a tuple) and **kwargs (extra keywords as a dict). Calls can unpack with * and **. Type hints document intent and power tools like mypy but are not enforced at runtime. lambda creates small anonymous functions.",
        "use_cases": ["Designing clear APIs with keyword-only flags.", "Forwarding arguments in wrappers (*args, **kwargs).", "Passing key functions to sorted/max."],
        "key_points": [
            "Order: def f(pos_only, /, normal, *args, kw_only, **kwargs).",
            "Keyword-only booleans prevent f(True, False) mysteries.",
            "Functions return None by default.",
            "Type hints: list[int], dict[str, int], X | None (3.10+).",
        ],
        "examples": [
            ex("All parameter kinds", "intermediate", "See what lands where.", "python", """
                def f(a, b=2, /, c=3, *args, d, e=5, **kwargs):
                    print(f"a={a} b={b} c={c} args={args} d={d} e={e} kwargs={kwargs}")

                f(1, d=4)
                f(1, 20, 30, 40, 50, d=4, z=9)
            """),
            ex("Keyword-only flags and unpacking", "basic", "Readable call sites and argument forwarding.", "python", """
                def connect(host, port=5432, *, ssl=True, timeout=5.0):
                    return f"{host}:{port} ssl={ssl} timeout={timeout}"

                print(connect("db.internal", ssl=False))
                cfg = {"host": "db.internal", "port": 6543, "timeout": 2}
                print(connect(**cfg))
            """),
            ex("Functions are objects", "basic", "Pass them around, sort with key=.", "python", """
                people = [("Asha", 31), ("Ben", 25), ("Chen", 35)]
                print(sorted(people, key=lambda p: p[1]))
                ops = {"double": lambda x: x * 2, "square": lambda x: x ** 2}
                print({name: op(7) for name, op in ops.items()})
            """),
        ],
        "commands": ["def f(a, /, b, *, c): ...", "def f(*args, **kwargs): ...", "f(*xs, **kw)", "lambda x: x + 1", "def f(x: int) -> str: ..."],
        "gotchas": ["Mutable defaults are shared between calls.", "**kwargs swallowing typos silently.", "Overusing lambda where a named function is clearer."],
        "interview": [
            qa("basic", "What are *args and **kwargs?", "*args collects extra positional arguments into a tuple; **kwargs collects extra keyword arguments into a dict. At call sites, * and ** unpack sequences and mappings."),
            qa("intermediate", "What are keyword-only and positional-only parameters?", "Parameters after * (or *args) must be passed by name; parameters before / must be passed by position. They make APIs explicit and evolvable."),
            qa("intermediate", "Are type hints enforced?", "No. They are metadata used by type checkers, IDEs and libraries (pydantic, FastAPI) but Python does not check them at runtime."),
            qa("basic", "What does a function return without a return statement?", "None."),
        ],
        "related": ["scope-closures", "decorators"],
        "flow": flow(
            [node("call", "f(1, 20, 30, 40, d=4, z=9)", 18, 50, "slate", "call site", "pill"), node("a", "a, b", 60, 12, "sky", "positional-only"), node("c", "c", 60, 32, "sky"),
             node("args", "*args", 60, 52, "lemon", "tuple"), node("d", "d, e", 60, 72, "lilac", "keyword-only"), node("kw", "**kwargs", 60, 92, "peach", "dict")],
            [("call", "a"), ("call", "c"), ("call", "args"), ("call", "d"), ("call", "kw")],
            [
                step("Positional first", "1 and 20 fill a and b; 30 fills c.", ["a", "c"], [pkt("call", "a", "1, 20"), pkt("call", "c", "30")], {"a": {"sub": "a=1 b=20"}, "c": {"sub": "c=30"}}),
                step("Extras to *args", "40 has no named slot left, so it goes into the args tuple.", ["args"], [pkt("call", "args", "40")], {"args": {"sub": "(40,)"}}),
                step("Keywords by name", "d=4 fills the keyword-only d; e keeps its default.", ["d"], [pkt("call", "d", "d=4")], {"d": {"sub": "d=4 e=5"}}),
                step("Unknown keywords", "z=9 matches nothing, so it goes into **kwargs.", ["kw"], [pkt("call", "kw", "z=9")], {"kw": {"sub": "{'z': 9}"}}),
            ],
        ),
    },
    {
        "id": "scope-closures", "title": "Scope (LEGB) & Closures", "category": "functions", "level": "intermediate", "code": "SC",
        "tagline": "How names are resolved, nonlocal/global, and functions that remember.",
        "analogy": "Looking for your keys: first your pocket (Local), then the bag you're carrying (Enclosing), then the house (Global), then the neighbourhood lost-and-found (Built-in).",
        "what": "Python resolves names using LEGB: Local, Enclosing function scopes, Global (module), Built-in. Assignment inside a function makes a name local unless declared global or nonlocal. A closure is an inner function that captures variables from an enclosing scope; the variables live in cells that outlive the outer call. Late binding means closures see the variable's value at call time, not definition time.",
        "use_cases": ["Factories that build configured functions.", "Counters and memoization without classes.", "Callbacks that carry context."],
        "key_points": [
            "UnboundLocalError: assigning to a name anywhere in a function makes it local everywhere in it.",
            "nonlocal rebinds an enclosing variable; global a module variable.",
            "Loop closures capture the variable, not the value: use default args to freeze.",
            "Inspect captured cells via f.__closure__.",
        ],
        "examples": [
            ex("Closure counter", "intermediate", "The inner function keeps count alive between calls.", "python", """
                def make_counter():
                    count = 0
                    def inc():
                        nonlocal count
                        count += 1
                        return count
                    return inc

                c = make_counter()
                print(c(), c(), c())
                print(c.__closure__[0].cell_contents)
            """),
            ex("Late binding gotcha", "advanced", "All lambdas see the final i, unless you freeze it.", "python", """
                late = [lambda: i for i in range(3)]
                frozen = [lambda i=i: i for i in range(3)]
                print([f() for f in late], [f() for f in frozen])
            """),
            ex("UnboundLocalError", "intermediate", "Assignment makes total local for the whole function.", "python", """
                total = 10
                def add(x):
                    try:
                        total += x
                    except UnboundLocalError as e:
                        print("error:", e)
                add(5)
            """),
        ],
        "commands": ["LEGB: Local → Enclosing → Global → Built-in", "nonlocal name · global name", "f.__closure__ · f.__code__.co_freevars", "lambda i=i: i  # freeze loop value"],
        "gotchas": ["Shadowing built-ins (list = [...]) breaks later code.", "Using global for state shared between modules.", "Late-binding closures in loops."],
        "interview": [
            qa("intermediate", "What is a closure?", "A function object that remembers variables from the scope where it was defined, even after that scope has returned. Python stores them in cell objects."),
            qa("intermediate", "Explain LEGB.", "The order of name lookup: Local, Enclosing function scopes, Global module scope, Built-ins."),
            qa("advanced", "Why does [lambda: i for i in range(3)] return 2, 2, 2?", "Closures capture the variable i, not its value; when called, i is 2. Bind the value with a default argument (lambda i=i: i) or functools.partial."),
            qa("intermediate", "global vs nonlocal?", "global binds to the module-level name; nonlocal binds to the nearest enclosing function's name. Both are needed only for rebinding, not for mutation."),
        ],
        "related": ["decorators", "functions-args"],
        "flow": flow(
            [node("B", "Built-in", 50, 88, "slate", "print, len, …"), node("G", "Global", 50, 66, "lemon", "make_counter, c"), node("E", "Enclosing", 50, 44, "mint", "count = 0"),
             node("L", "Local (inc)", 50, 22, "sky", "—"), node("cell", "cell", 88, 44, "lilac", "count", "round")],
            [("L", "E"), ("E", "G"), ("G", "B"), ("E", "cell")],
            [
                step("Call inc()", "Python looks up count: not in inc's local scope…", ["L"], [pkt("L", "E", "count?")]),
                step("Found in Enclosing", "…found in make_counter's scope, stored in a <b>cell</b> shared with inc.", ["E", "cell"], [pkt("E", "cell")]),
                step("Outer call finished", "make_counter returned long ago, but the cell lives on, referenced by c.__closure__.", ["cell"], set={"cell": {"sub": "count = 3"}}),
                step("print lookup", "Names like print go all the way to Built-ins.", ["B"], [pkt("L", "E"), pkt("E", "G"), pkt("G", "B", "print")]),
            ],
        ),
    },
    {
        "id": "decorators", "title": "Decorators", "category": "functions", "level": "intermediate", "code": "DE",
        "tagline": "Wrap functions to add timing, caching, retries and auth without touching their bodies.",
        "analogy": "Gift wrapping: the present (function) is unchanged, but the wrapping adds a bow and a tag (behaviour before and after).",
        "what": "A decorator is a callable that takes a function and returns a replacement, applied with @decorator above def. Typical wrappers accept *args, **kwargs, do something before/after and call the original. functools.wraps copies the name and docstring. Decorators with arguments are factories returning decorators. Built-ins: @property, @staticmethod, @classmethod, @functools.lru_cache/cache, @dataclass.",
        "use_cases": ["Timing and logging calls.", "Caching expensive pure functions.", "Retrying flaky network calls.", "Web frameworks' @app.route."],
        "key_points": [
            "@d def f is f = d(f).",
            "Stacked decorators apply bottom-up.",
            "Always use functools.wraps in wrappers.",
            "lru_cache needs hashable arguments.",
        ],
        "examples": [
            ex("Timing decorator", "intermediate", "Wrap any function with before/after logic.", "python", """
                import functools, time

                def timed(fn):
                    @functools.wraps(fn)
                    def wrapper(*args, **kwargs):
                        start = time.perf_counter()
                        try:
                            return fn(*args, **kwargs)
                        finally:
                            print(f"{fn.__name__} took {(time.perf_counter() - start) * 1000:.2f} ms")
                    return wrapper

                @timed
                def slow_sum(n):
                    return sum(range(n))

                print(slow_sum(1_000_000), slow_sum.__name__)
            """),
            ex("Decorator with arguments: retry", "advanced", "A factory that returns a decorator.", "python", """
                import functools

                def retry(times):
                    def deco(fn):
                        @functools.wraps(fn)
                        def wrapper(*a, **kw):
                            for attempt in range(1, times + 1):
                                try:
                                    return fn(*a, **kw)
                                except ConnectionError as e:
                                    print(f"attempt {attempt} failed: {e}")
                            raise RuntimeError("gave up")
                        return wrapper
                    return deco

                calls = iter([ConnectionError("timeout"), ConnectionError("reset"), "ok"])

                @retry(times=3)
                def fetch():
                    r = next(calls)
                    if isinstance(r, Exception):
                        raise r
                    return r

                print(fetch())
            """),
            ex("Memoize with lru_cache", "basic", "Exponential recursion becomes linear.", "python", """
                from functools import lru_cache

                @lru_cache(maxsize=None)
                def fib(n):
                    return n if n < 2 else fib(n - 1) + fib(n - 2)

                print(fib(80), fib.cache_info())
            """),
        ],
        "commands": ["@functools.wraps(fn)", "@functools.lru_cache(maxsize=128) · @functools.cache", "def deco(arg): def inner(fn): ...", "@property · @classmethod · @staticmethod"],
        "gotchas": ["Forgetting wraps: name, docstring and signature are lost.", "Caching functions with side effects or unhashable args.", "Decorators that run expensive code at import time."],
        "interview": [
            qa("intermediate", "What is a decorator?", "A callable that takes a function (or class) and returns a new one, used to add behaviour around it. @d above def f is sugar for f = d(f)."),
            qa("intermediate", "Why use functools.wraps?", "It copies __name__, __doc__, __module__, __qualname__ and __wrapped__ onto the wrapper, so introspection, debugging and documentation still work."),
            qa("advanced", "How do you write a decorator that takes arguments?", "Write a function that takes the arguments and returns the real decorator: def retry(n): def deco(fn): ... return deco."),
            qa("advanced", "In what order are stacked decorators applied?", "Bottom-up at definition: @a @b def f → f = a(b(f)). At call time, a's wrapper runs first."),
        ],
        "related": ["scope-closures", "classes-dataclasses"],
        "flow": flow(
            [node("call", "slow_sum(10⁶)", 10, 50, "slate", "caller", "pill"), node("w", "wrapper", 40, 50, "lilac", "@timed"), node("fn", "slow_sum", 72, 50, "mint", "original"),
             node("log", "print", 40, 88, "lemon", "took 9 ms", "pill", True)],
            [("call", "w"), ("w", "fn"), ("w", "log")],
            [
                step("Decoration", "At definition, slow_sum = timed(slow_sum): the name now points to wrapper.", ["w"]),
                step("Call the wrapper", "Calling slow_sum actually calls wrapper, which starts a timer.", ["call", "w"], [pkt("call", "w", "args")]),
                step("Call the original", "wrapper calls the original function, captured in its closure.", ["fn"], [pkt("w", "fn", "*args"), pkt("fn", "w", "result")]),
                step("After logic", "finally: print the elapsed time, then return the result.", ["log"], [pkt("w", "log"), pkt("w", "call", "result")], {"log": {"hidden": False}}),
            ],
        ),
    },
    {
        "id": "classes-dataclasses", "title": "Classes, Dataclasses & Dunder Methods", "category": "oop", "level": "intermediate", "code": "CL",
        "tagline": "Instances, inheritance and MRO, properties, and the data model.",
        "analogy": "A class is a cookie cutter, instances are cookies. Dunder methods are the universal sockets that let your cookie plug into Python's built-in tools (len, +, ==, for).",
        "what": "Classes bundle state and behaviour. __init__ initializes instances; methods receive self. Class attributes are shared, instance attributes per object. Inheritance and super() follow the Method Resolution Order (C3 linearization). Dunder methods hook into syntax: __repr__, __eq__, __hash__, __len__, __iter__, __add__, __enter__/__exit__. @property exposes computed or validated attributes. @dataclass generates __init__, __repr__, __eq__ (and ordering, frozen, slots).",
        "use_cases": ["Domain objects with validation.", "Value objects (frozen dataclasses).", "Custom containers that work with len and for."],
        "key_points": [
            "Prefer composition over deep inheritance.",
            "__repr__ for developers, __str__ for users.",
            "Defining __eq__ without __hash__ makes instances unhashable.",
            "@dataclass(frozen=True, slots=True) for small immutable records.",
        ],
        "examples": [
            ex("Dataclass value object", "basic", "Generated __init__, __repr__ and __eq__.", "python", """
                from dataclasses import dataclass, field

                @dataclass(frozen=True)
                class Money:
                    amount: int
                    currency: str = "EUR"

                    def __add__(self, other):
                        assert self.currency == other.currency
                        return Money(self.amount + other.amount, self.currency)

                @dataclass
                class Cart:
                    items: list = field(default_factory=list)

                print(Money(5) + Money(7), Money(1) == Money(1), Cart())
            """),
            ex("Property with validation", "intermediate", "Keep the attribute API while adding rules.", "python", """
                class Account:
                    def __init__(self, owner, balance=0):
                        self.owner = owner
                        self.balance = balance

                    @property
                    def balance(self):
                        return self._balance

                    @balance.setter
                    def balance(self, value):
                        if value < 0:
                            raise ValueError("balance cannot be negative")
                        self._balance = value

                acct = Account("asha", 50)
                try:
                    acct.balance = -5
                except ValueError as e:
                    print(e, acct.balance)
            """),
            ex("MRO and super()", "advanced", "Cooperative multiple inheritance follows the MRO.", "python", """
                class Base:
                    def hello(self): return ["Base"]
                class A(Base):
                    def hello(self): return ["A"] + super().hello()
                class B(Base):
                    def hello(self): return ["B"] + super().hello()
                class C(A, B):
                    def hello(self): return ["C"] + super().hello()

                print([k.__name__ for k in C.__mro__])
                print(C().hello())
            """),
        ],
        "commands": ["@dataclass(frozen=True, order=True, slots=True)", "field(default_factory=list)", "@property / @x.setter", "super().__init__(...)", "Cls.__mro__", "__repr__ · __eq__ · __hash__ · __len__ · __iter__"],
        "gotchas": ["Mutable class attributes shared by all instances.", "Mutable dataclass defaults without default_factory (error).", "Calling a parent method directly instead of super() in multiple inheritance."],
        "interview": [
            qa("intermediate", "What does @dataclass give you?", "Auto-generated __init__, __repr__ and __eq__ from annotated fields, plus optional ordering, immutability (frozen), slots and keyword-only fields."),
            qa("intermediate", "@classmethod vs @staticmethod?", "classmethod receives the class (cls), useful for alternate constructors and respecting subclasses; staticmethod receives nothing and is just a namespaced function."),
            qa("advanced", "What is the MRO?", "Method Resolution Order: the linearized list of classes Python searches for attributes, computed by C3 linearization. super() moves to the next class in the instance's MRO, enabling cooperative multiple inheritance."),
            qa("advanced", "What are __slots__ for?", "They replace the per-instance __dict__ with fixed slots, saving memory and speeding attribute access, at the cost of not adding arbitrary attributes."),
        ],
        "related": ["iterators-generators", "decorators"],
        "flow": flow(
            [node("C", "C", 50, 12, "lilac", "C(A, B)"), node("A", "A", 25, 45, "sky"), node("B", "B", 75, 45, "mint"), node("Base", "Base", 50, 78, "lemon"), node("obj", "object", 50, 96, "slate", "", "pill")],
            [("C", "A"), ("C", "B"), ("A", "Base"), ("B", "Base"), ("Base", "obj")],
            [
                step("Call C().hello()", "Python looks for hello in C first.", ["C"]),
                step("super() → A", "C's super() is the next class in the MRO: A.", ["A"], [pkt("C", "A", "super()")]),
                step("A's super() → B (not Base!)", "Because the instance is a C, A's super() follows C's MRO to B.", ["B"], [pkt("A", "B", "super()", "lemon")]),
                step("Then Base", "MRO: C → A → B → Base → object. Result: ['C', 'A', 'B', 'Base'].", ["Base", "obj"], [pkt("B", "Base", "super()")]),
            ],
        ),
    },
    {
        "id": "iterators-generators", "title": "Iterators, Generators & itertools", "category": "oop", "level": "intermediate", "code": "IT",
        "tagline": "Lazy pipelines with yield, the iterator protocol and itertools.",
        "analogy": "A Pez dispenser: it hands out one candy each time you press, and doesn't need to hold the whole factory's output in your hand.",
        "what": "An iterable has __iter__ returning an iterator; an iterator has __next__ and raises StopIteration when done. for loops, unpacking and comprehensions use this protocol. A generator function contains yield: calling it returns a generator that runs until the next yield, pausing with its local state intact. Generators enable lazy pipelines over huge or infinite data. yield from delegates; itertools offers islice, chain, groupby, accumulate, product, count, tee.",
        "use_cases": ["Streaming a huge log file line by line.", "Infinite sequences (ids, retries).", "Composable data pipelines (read → parse → filter)."],
        "key_points": [
            "Generators are single-use; recreate to iterate again.",
            "Lazy evaluation: nothing runs until you iterate.",
            "itertools.groupby needs input sorted by the key.",
            "send() and return values make generators coroutines (historic asyncio).",
        ],
        "examples": [
            ex("A generator pauses at yield", "basic", "Step through with the Visualizer to watch the frame resume.", "python", """
                def countdown(n):
                    print("start")
                    while n > 0:
                        yield n
                        n -= 1
                    print("done")

                gen = countdown(3)
                print(next(gen))
                print(list(gen))
            """),
            ex("Lazy pipeline", "intermediate", "Only the needed items are ever computed.", "python", """
                import itertools

                def read_lines():
                    for i in itertools.count(1):
                        yield f"{i},{'ERROR' if i % 7 == 0 else 'INFO'},msg{i}"

                parsed = (line.split(",") for line in read_lines())
                errors = (p for p in parsed if p[1] == "ERROR")
                print(list(itertools.islice(errors, 3)))
            """),
            ex("Custom iterator class", "advanced", "Implement the protocol by hand, and itertools helpers.", "python", """
                import itertools

                class Squares:
                    def __init__(self, n):
                        self.i, self.n = 0, n
                    def __iter__(self):
                        return self
                    def __next__(self):
                        if self.i >= self.n:
                            raise StopIteration
                        self.i += 1
                        return self.i ** 2

                print(list(Squares(5)))
                print(list(itertools.accumulate([1, 2, 3, 4])))
                data = sorted(["apple", "avocado", "banana", "blueberry", "cherry"])
                print({k: list(g) for k, g in itertools.groupby(data, key=lambda w: w[0])})
            """),
        ],
        "commands": ["iter(x) · next(it, default)", "def gen(): yield x", "yield from other_gen()", "itertools: islice, chain, groupby, accumulate, product, count, pairwise", "(expr for x in xs)"],
        "gotchas": ["Iterating a generator twice: the second loop is empty.", "Calling len() on a generator fails.", "groupby on unsorted data produces repeated groups."],
        "interview": [
            qa("intermediate", "Iterable vs iterator?", "An iterable can produce an iterator via __iter__ (lists, dicts). An iterator yields items via __next__ and remembers its position; iterators are also iterable (returning self)."),
            qa("intermediate", "What does yield do?", "It turns the function into a generator. Each next() runs until the next yield, returns the value and pauses with all local state preserved."),
            qa("advanced", "Why use generators for large files?", "They process one item at a time with constant memory, and pipelines compose without building intermediate lists."),
            qa("advanced", "What is yield from?", "It delegates to a sub-iterator/generator, yielding all its values and passing send()/throw() through; it also returns the sub-generator's return value."),
        ],
        "related": ["comprehensions", "async-await"],
        "flow": flow(
            [node("caller", "caller", 12, 50, "slate", "next(gen)", "pill"), node("gen", "countdown frame", 55, 50, "lilac", "n = 3, paused"), node("y", "yield", 88, 50, "mint", "", "round")],
            [("caller", "gen"), ("gen", "y")],
            [
                step("Create", "countdown(3) returns a generator. No code has run yet.", ["gen"], set={"gen": {"sub": "not started"}}),
                step("next() runs to yield", "Prints 'start', reaches yield 3, and pauses.", ["gen", "y"], [pkt("caller", "gen", "next"), pkt("y", "caller", "3")], {"gen": {"sub": "n = 3, paused"}}),
                step("Resume", "Next next() continues after yield: n -= 1, loop, yield 2.", ["gen"], [pkt("caller", "gen", "next"), pkt("y", "caller", "2")], {"gen": {"sub": "n = 2, paused"}}),
                step("Exhausted", "When the function ends, StopIteration tells the for loop to stop.", ["caller"], [pkt("gen", "caller", "StopIteration", "rose")], {"gen": {"sub": "finished"}}),
            ],
        ),
    },
    {
        "id": "exceptions-context", "title": "Exceptions & Context Managers", "category": "robust", "level": "intermediate", "code": "EX",
        "tagline": "try/except/else/finally, custom exceptions, chaining and with-statements.",
        "analogy": "A fire drill: try is the normal day, except is the plan for a fire, else runs only if nothing burned, finally is locking the doors no matter what. A context manager is a hotel key card that checks you out automatically.",
        "what": "Exceptions signal errors and unwind the stack until handled. except catches specific types (avoid bare except); else runs if no exception; finally always runs. raise ... from e chains causes. Custom exceptions subclass Exception and form hierarchies. Context managers (__enter__/__exit__ or @contextmanager) guarantee setup/cleanup: files, locks, transactions, temporary state. ExceptionGroup and except* handle multiple concurrent errors (3.11+).",
        "use_cases": ["Translating low-level errors into domain errors.", "Always releasing locks or closing files.", "Timing blocks or temporarily changing settings."],
        "key_points": [
            "Catch the narrowest exception you can handle.",
            "EAFP (try first) is idiomatic, LBYL (check first) is fine for clarity.",
            "Never silently swallow exceptions; log or re-raise.",
            "__exit__ returning True suppresses the exception.",
        ],
        "examples": [
            ex("try / except / else / finally", "basic", "See which blocks run for good and bad input.", "python", """
                def parse(s):
                    try:
                        n = int(s)
                    except ValueError as e:
                        print(f"bad input {s!r}: {e}")
                        return None
                    else:
                        print("parsed", n)
                        return n
                    finally:
                        print("cleanup for", repr(s))

                parse("42")
                parse("forty-two")
            """),
            ex("Custom exceptions and chaining", "intermediate", "Wrap low-level errors with context.", "python", """
                class PaymentError(Exception):
                    pass

                def charge(amount):
                    try:
                        raise ConnectionError("PSP timeout")
                    except ConnectionError as e:
                        raise PaymentError(f"could not charge {amount}") from e

                try:
                    charge(10)
                except PaymentError as e:
                    print(type(e).__name__, "->", e, "| cause:", repr(e.__cause__))
            """),
            ex("Context managers", "intermediate", "Class-based and generator-based.", "python", """
                from contextlib import contextmanager, suppress
                import time

                @contextmanager
                def timer(label):
                    start = time.perf_counter()
                    try:
                        yield
                    finally:
                        print(f"{label}: {(time.perf_counter() - start) * 1000:.2f} ms")

                class Transaction:
                    def __enter__(self):
                        print("BEGIN"); return self
                    def __exit__(self, exc_type, exc, tb):
                        print("ROLLBACK" if exc_type else "COMMIT")
                        return False

                with timer("work"):
                    sum(range(100_000))
                with suppress(ValueError), Transaction():
                    raise ValueError("boom")
            """),
        ],
        "commands": ["try / except E as e / else / finally", "raise NewError(...) from e", "class AppError(Exception): ...", "with open(p) as f: ...", "@contextlib.contextmanager · contextlib.suppress · ExitStack"],
        "gotchas": ["Bare except: also catches KeyboardInterrupt and SystemExit.", "return inside finally swallows exceptions.", "Catching Exception and continuing with corrupted state."],
        "interview": [
            qa("basic", "What runs in else and finally?", "else runs only if the try block raised nothing; finally always runs, whether an exception happened, was handled, or the block returned."),
            qa("intermediate", "How do you write a context manager?", "A class with __enter__ and __exit__, or a generator decorated with @contextmanager where code before yield is setup and after (in finally) is cleanup."),
            qa("intermediate", "What does raise X from Y do?", "Sets X.__cause__ = Y, so tracebacks show 'The above exception was the direct cause of...', preserving the original error."),
            qa("advanced", "EAFP vs LBYL?", "Easier to Ask Forgiveness than Permission (try and handle exceptions) vs Look Before You Leap (check first). EAFP avoids race conditions like file existence checks and is idiomatic Python."),
        ],
        "related": ["classes-dataclasses", "async-await"],
        "flow": flow(
            [node("try", "try", 12, 50, "sky", "int('forty-two')"), node("exc", "except ValueError", 45, 25, "rose", "handled"), node("else", "else", 45, 75, "mint", "skipped"),
             node("fin", "finally", 80, 50, "lemon", "always runs")],
            [("try", "exc"), ("try", "else"), ("exc", "fin"), ("else", "fin")],
            [
                step("Run try", "int('forty-two') raises ValueError.", ["try"], set={"try": {"tint": "rose"}}),
                step("Match except", "The ValueError handler catches it; else is skipped.", ["exc"], [pkt("try", "exc", "ValueError", "rose")], {"else": {"tint": "slate"}}),
                step("Good input", "For '42', no exception: else runs instead.", ["else"], [pkt("try", "else", "ok", "mint")], {"else": {"tint": "mint", "sub": "runs"}, "try": {"tint": "sky", "sub": "int('42')"}}),
                step("finally always", "Cleanup runs in every case, even after return.", ["fin"], [pkt("exc", "fin"), pkt("else", "fin")]),
            ],
        ),
    },
    {
        "id": "async-await", "title": "asyncio: async / await", "category": "concurrency", "level": "advanced", "code": "AS",
        "tagline": "One thread, many waiting tasks: the event loop, coroutines and gather.",
        "analogy": "A chess master playing 20 boards: make a move, walk to the next board while the opponent thinks. One person, many games, no idle waiting.",
        "what": "async def defines a coroutine; await suspends it until the awaited operation completes, letting the event loop run other tasks. asyncio.run starts the loop; asyncio.gather and TaskGroup run coroutines concurrently; asyncio.wait_for and timeout add deadlines; Semaphore limits concurrency. It shines for I/O-bound work (HTTP, DB, sockets). Blocking calls (time.sleep, CPU loops, sync DB drivers) freeze the whole loop; offload them with asyncio.to_thread or a process pool.",
        "use_cases": ["Calling 100 APIs concurrently.", "WebSocket servers with thousands of connections.", "Async web frameworks (FastAPI, aiohttp)."],
        "key_points": [
            "Concurrency, not parallelism: still one thread.",
            "Forgetting await returns a coroutine object that never runs.",
            "Use asyncio.TaskGroup (3.11+) for structured concurrency and error handling.",
            "Never call blocking functions in a coroutine.",
        ],
        "examples": [
            ex("Sequential vs concurrent", "intermediate", "Three 0.3 s waits take 0.9 s sequentially, 0.3 s with gather.", "python", """
                import asyncio, time

                async def fetch(name, delay):
                    await asyncio.sleep(delay)
                    return f"{name} done"

                async def main():
                    t = time.perf_counter()
                    for n in "abc":
                        await fetch(n, 0.3)
                    print(f"sequential {time.perf_counter() - t:.2f}s")
                    t = time.perf_counter()
                    print(await asyncio.gather(*(fetch(n, 0.3) for n in "abc")))
                    print(f"gather {time.perf_counter() - t:.2f}s")

                asyncio.run(main())
            """),
            ex("Limit concurrency and add timeouts", "advanced", "Semaphore caps parallel calls; wait_for enforces a deadline.", "python", """
                import asyncio

                async def call(i, sem):
                    async with sem:
                        await asyncio.sleep(0.1 * (i % 3 + 1))
                        return i

                async def main():
                    sem = asyncio.Semaphore(2)
                    print(await asyncio.gather(*(call(i, sem) for i in range(6))))
                    try:
                        await asyncio.wait_for(asyncio.sleep(1), timeout=0.2)
                    except TimeoutError:
                        print("timed out")

                asyncio.run(main())
            """),
            ex("Blocking the loop", "advanced", "time.sleep blocks every task; to_thread does not.", "python", """
                import asyncio, time

                async def ticker():
                    for _ in range(3):
                        print("tick", round(time.perf_counter() - T0, 1))
                        await asyncio.sleep(0.1)

                async def main():
                    await asyncio.gather(ticker(), asyncio.to_thread(time.sleep, 0.3))

                T0 = time.perf_counter()
                asyncio.run(main())
            """),
        ],
        "commands": ["asyncio.run(main())", "await asyncio.gather(*coros)", "async with asyncio.TaskGroup() as tg: tg.create_task(c)", "asyncio.wait_for(c, timeout) · asyncio.timeout(s)", "asyncio.Semaphore(n)", "await asyncio.to_thread(blocking_fn)"],
        "gotchas": ["Calling requests.get inside async code blocks everything; use httpx/aiohttp.", "Fire-and-forget tasks get garbage collected; keep references.", "Mixing event loops across threads."],
        "interview": [
            qa("advanced", "How does asyncio achieve concurrency in one thread?", "Coroutines voluntarily yield at await points; the event loop multiplexes I/O readiness (epoll/kqueue) and resumes whichever coroutine's operation completed."),
            qa("intermediate", "When should you use asyncio vs threads vs processes?", "asyncio: many concurrent I/O tasks with async libraries. Threads: I/O with blocking libraries or simple concurrency. Processes: CPU-bound work that needs multiple cores."),
            qa("advanced", "What happens if you call a blocking function in a coroutine?", "The event loop thread is stuck, so all other tasks stall: latency spikes and timeouts. Use async libraries or run_in_executor / to_thread."),
            qa("advanced", "gather vs TaskGroup?", "gather returns results in order and by default leaves sibling tasks running when one fails. TaskGroup (3.11+) cancels siblings on failure and raises an ExceptionGroup, giving structured concurrency."),
        ],
        "related": ["gil-concurrency", "iterators-generators"],
        "flow": flow(
            [node("loop", "Event loop", 50, 50, "lilac", "1 thread", "round"), node("a", "task a", 15, 18, "sky", "ready"), node("b", "task b", 15, 82, "sky", "ready"),
             node("c", "task c", 85, 18, "sky", "ready"), node("io", "OS I/O", 85, 82, "lemon", "epoll / kqueue")],
            [("loop", "a"), ("loop", "b"), ("loop", "c"), ("loop", "io")],
            [
                step("Run task a", "The loop runs a until it hits <b>await</b> on a network call.", ["a", "loop"], [pkt("loop", "a", "run")], {"a": {"sub": "awaiting I/O"}}),
                step("Switch, don't wait", "While a waits, the loop runs b, then c.", ["b", "c"], [pkt("loop", "b", "run"), pkt("loop", "c", "run")], {"b": {"sub": "awaiting I/O"}, "c": {"sub": "awaiting I/O"}}),
                step("I/O ready", "The OS reports a's socket is readable.", ["io"], [pkt("io", "loop", "a ready")]),
                step("Resume", "a continues after its await. Total time ≈ the longest wait, not the sum.", ["a"], [pkt("loop", "a", "resume", "mint")], {"a": {"sub": "done", "tint": "mint"}}),
            ],
        ),
    },
    {
        "id": "gil-concurrency", "title": "The GIL, Threads & Processes", "category": "concurrency", "level": "advanced", "code": "GL",
        "tagline": "Why CPU-bound threads don't speed up, and what to use instead.",
        "analogy": "A kitchen with one knife (the GIL): many cooks (threads) can wait for the oven (I/O) at once, but only one can chop at a time. More kitchens (processes) means more knives.",
        "what": "CPython's Global Interpreter Lock lets only one thread execute Python bytecode at a time, simplifying memory management (reference counting). Threads still help for I/O, because the GIL is released while waiting on sockets, files or sleep, and C extensions (NumPy) can release it. For CPU-bound work, use multiprocessing / ProcessPoolExecutor (separate interpreters, pickled data), vectorized libraries, or native code. Python 3.13 ships an experimental free-threaded build (PEP 703) without the GIL. Shared state still needs locks: the GIL does not make your code thread-safe.",
        "use_cases": ["Downloading many files with a thread pool.", "Image processing across cores with a process pool.", "Parallel NumPy work that releases the GIL."],
        "key_points": [
            "concurrent.futures gives the same API for threads and processes.",
            "Processes pay startup and serialization costs; batch work.",
            "x += 1 is not atomic across threads; use Lock or queue.Queue.",
            "Profile first: maybe the bottleneck is I/O, not CPU.",
        ],
        "examples": [
            ex("Threads for I/O", "intermediate", "Waiting overlaps, so 5 × 0.2 s finishes in ~0.2 s.", "python", """
                import time
                from concurrent.futures import ThreadPoolExecutor

                def download(i):
                    time.sleep(0.2)          # I/O wait releases the GIL
                    return i

                t = time.perf_counter()
                with ThreadPoolExecutor(max_workers=5) as pool:
                    print(list(pool.map(download, range(5))))
                print(f"{time.perf_counter() - t:.2f}s")
            """),
            ex("Threads don't speed up CPU work", "advanced", "Same total time with 1 or 4 threads (on the standard GIL build).", "python", """
                import time
                from concurrent.futures import ThreadPoolExecutor

                def burn(n):
                    s = 0
                    for i in range(n):
                        s += i * i
                    return s

                for workers in (1, 4):
                    t = time.perf_counter()
                    with ThreadPoolExecutor(workers) as pool:
                        list(pool.map(burn, [300_000] * 4))
                    print(f"{workers} thread(s): {time.perf_counter() - t:.2f}s")
            """),
            ex("Race condition and a lock", "advanced", "Read-modify-write without a lock loses increments (sleep(0) forces a thread switch).", "python", """
                import threading, time

                counter = 0
                lock = threading.Lock()

                def work(n, use_lock):
                    global counter
                    for _ in range(n):
                        if use_lock:
                            with lock:
                                counter += 1
                        else:
                            v = counter
                            time.sleep(0)
                            counter = v + 1

                for use_lock in (False, True):
                    counter = 0
                    ts = [threading.Thread(target=work, args=(2_000, use_lock)) for _ in range(4)]
                    [t.start() for t in ts]; [t.join() for t in ts]
                    print("lock" if use_lock else "no lock", counter)
            """),
            ex("Processes for CPU work", "advanced", "Each process has its own GIL (run locally; the sandbox limits processes).", "python", """
                from concurrent.futures import ProcessPoolExecutor

                def burn(n):
                    return sum(i * i for i in range(n))

                if __name__ == "__main__":
                    with ProcessPoolExecutor() as pool:
                        print(list(pool.map(burn, [5_000_000] * 4)))
            """, runnable=False),
        ],
        "commands": ["ThreadPoolExecutor(max_workers=n).map(f, xs)", "ProcessPoolExecutor().map(f, xs, chunksize=k)", "threading.Lock() · queue.Queue()", "multiprocessing.Pool · shared_memory", "python3.13t (free-threaded build)"],
        "gotchas": ["Expecting threads to parallelize pure-Python CPU loops.", "Unpicklable functions/lambdas with process pools.", "Thinking the GIL makes compound operations atomic."],
        "interview": [
            qa("advanced", "What is the GIL and why does it exist?", "A mutex in CPython allowing one thread to execute bytecode at a time. It makes reference counting and the C API simple and fast for single-threaded code, at the cost of multi-core parallelism for Python code."),
            qa("intermediate", "Do threads help in Python?", "Yes for I/O-bound work and C extensions that release the GIL; no for pure-Python CPU-bound work, where processes or native code are needed."),
            qa("advanced", "Does the GIL make code thread-safe?", "No. Thread switches can happen between bytecodes, so read-modify-write sequences like counter += 1 can interleave. Use locks, queues or atomic structures."),
            qa("advanced", "What changes with free-threaded Python (PEP 703)?", "An optional build without the GIL (3.13+) allows true parallel threads; it uses per-object locking and biased reference counting, with some single-thread overhead and extension compatibility work."),
        ],
        "related": ["async-await", "exceptions-context"],
        "flow": flow(
            [node("gil", "GIL", 50, 15, "rose", "held by T1", "pill"), node("t1", "Thread 1", 18, 55, "sky", "running"), node("t2", "Thread 2", 50, 55, "sky", "waiting"),
             node("t3", "Thread 3", 82, 55, "sky", "waiting"), node("io", "I/O", 50, 90, "lemon", "socket read", "round")],
            [("gil", "t1"), ("gil", "t2"), ("gil", "t3"), ("t1", "io")],
            [
                step("One holder", "Only the thread holding the GIL runs Python bytecode.", ["gil", "t1"], [pkt("gil", "t1", "run")]),
                step("Release on I/O", "T1 starts a socket read and releases the GIL while waiting.", ["io", "t1"], [pkt("t1", "io", "read")], {"t1": {"sub": "waiting on I/O"}, "gil": {"sub": "free"}}),
                step("Another thread runs", "T2 grabs the GIL and runs. This is why threads help for I/O.", ["t2"], [pkt("gil", "t2", "run")], {"t2": {"sub": "running"}, "gil": {"sub": "held by T2"}}),
                step("CPU-bound?", "If every thread only computes, they take turns: no speed-up. Use processes for multiple cores.", ["t2", "t3"], set={"t3": {"sub": "still waiting"}}),
            ],
        ),
    },
]

SCENARIOS = [
    {"level": "intermediate", "topic": "objects-mutability", "q": "A function that builds a report sometimes returns data from a previous request.", "a": "Likely a mutable default argument or module-level list/dict shared across calls. Use None defaults and create fresh containers per call; avoid module-level mutable state in request handlers."},
    {"level": "advanced", "topic": "async-await", "q": "Your FastAPI endpoint's latency spikes for all users whenever one report is generated.", "a": "The report code is blocking the event loop (sync DB driver, CPU work, time.sleep). Move it to a thread or process pool (run_in_executor / to_thread), use async drivers, or a background job queue."},
    {"level": "advanced", "topic": "gil-concurrency", "q": "You added 8 threads to an image-resizing script and it got no faster.", "a": "Pure-Python CPU work is serialized by the GIL. Use ProcessPoolExecutor, a library that releases the GIL (Pillow/NumPy operations), or batch work to a worker service."},
    {"level": "intermediate", "topic": "iterators-generators", "q": "Processing a 20 GB log file crashes with MemoryError.", "a": "The code reads everything into a list (f.readlines() or a list comprehension). Iterate the file lazily line by line and chain generator expressions so memory stays constant."},
    {"level": "intermediate", "topic": "exceptions-context", "q": "Database connections leak until the pool is exhausted when errors happen.", "a": "Connections aren't released on exceptions. Use context managers (with pool.connection() as conn) or try/finally to guarantee release, and avoid bare except blocks that hide the problem."},
]

from .python_more import CATEGORIES as _MORE_CATEGORIES, SCENARIOS as _MORE_SCENARIOS, TOPICS as _MORE_TOPICS

CATEGORIES += _MORE_CATEGORIES
TOPICS += _MORE_TOPICS
SCENARIOS += _MORE_SCENARIOS
