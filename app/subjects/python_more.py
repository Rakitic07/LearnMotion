"""More python topics, appended to the core module."""

from ._dsl import chain, ex, qa, topic

CATEGORIES = [
    {"id": "typing", "title": "Types & Typing", "color": "rose", "blurb": "Type hints, generics and protocols."},
    {"id": "stdlib", "title": "Standard Library", "color": "slate", "blurb": "Batteries included: data, text, time and files."},
    {"id": "tooling", "title": "Tooling & Runtime", "color": "sky", "blurb": "Packages, tests, logging, profiling and memory."},
]

TOPICS = []

TOPICS += [
    topic(
        "numbers-floats", "Numbers, Floats, Decimal & Fraction", "core", "basic", "NF",
        "Arbitrary-size ints, binary floats, and exact Decimal/Fraction when money or ratios matter.",
        "A float is a ruler marked in powers of two: most decimal lengths fall between two marks, so you get the closest mark, not the exact value. Decimal is a ruler marked in tenths; Fraction just keeps the numerator and denominator.",
        "Python ints have arbitrary precision: they grow as large as memory allows and never overflow. float is an IEEE-754 double (53 bits of mantissa), so values like 0.1 cannot be represented exactly and tiny rounding errors appear in arithmetic. Compare floats with math.isclose rather than ==. decimal.Decimal performs base-10 arithmetic with configurable precision and rounding modes, which makes it the right choice for money; always construct it from strings, not floats. fractions.Fraction stores exact rationals. Integer division // floors toward negative infinity and % takes the sign of the divisor, so divmod(-7, 2) is (-4, 1). round() uses banker's rounding (round half to even), so round(2.5) is 2.",
        ["Currency and invoicing with Decimal and ROUND_HALF_UP.", "Exact ratios in probability or music theory with Fraction.", "Tolerance-based float comparisons in tests and geometry.", "Big-integer math such as factorials and cryptographic arithmetic."],
        [
            "int is unbounded; float is a 64-bit IEEE-754 double.",
            "Use math.isclose(a, b, rel_tol=..., abs_tol=...) to compare floats.",
            "Build Decimal from str: Decimal('0.1'), never Decimal(0.1).",
            "// and % floor toward negative infinity; math.trunc rounds toward zero.",
            "round() is round-half-to-even; use Decimal.quantize for business rounding.",
        ],
        [
            ex("Why 0.1 + 0.2 != 0.3", "basic", "Float error, isclose, and exact alternatives.", "python", """
                import math
                from decimal import Decimal
                from fractions import Fraction

                print(0.1 + 0.2, 0.1 + 0.2 == 0.3)
                print(math.isclose(0.1 + 0.2, 0.3))
                print(Decimal("0.1") + Decimal("0.2"))
                print(Decimal(0.1))                      # the float's true value
                print(Fraction(1, 10) + Fraction(2, 10))
                print((0.1).as_integer_ratio())
            """),
            ex("Integer division, rounding, big ints", "basic", "Floor semantics and banker's rounding surprise many people.", "python", """
                print(7 // 2, -7 // 2, 7 % 3, -7 % 3, divmod(-7, 2))
                print(round(0.5), round(1.5), round(2.5), round(2.675, 2))
                print(2 ** 100)
                print(len(str(2 ** 10_000)), "digits")
                print(int("ff", 16), bin(10), hex(255), 1_000_000)
            """),
            ex("Money with Decimal", "intermediate", "Quantize to cents with explicit rounding.", "python", """
                from decimal import Decimal, ROUND_HALF_UP, getcontext

                price = Decimal("19.99")
                tax_rate = Decimal("0.0825")
                tax = (price * tax_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                print("tax:", tax, "total:", price + tax)

                getcontext().prec = 50
                print(Decimal(1) / Decimal(7))
            """),
        ],
        ["math.isclose(a, b, rel_tol=1e-9)", "Decimal('1.10').quantize(Decimal('0.01'), ROUND_HALF_UP)", "Fraction(3, 4) + Fraction(1, 4)", "divmod(a, b) · a // b · a % b", "float('inf') · float('nan') · math.isnan(x)"],
        ["Decimal(0.1) captures the float's binary error; pass a string.", "nan != nan, so nan in a list breaks sorting and equality checks.", "Summing many floats accumulates error; math.fsum is more accurate.", "Mixing Decimal and float raises TypeError (by design)."],
        [
            qa("basic", "Why is 0.1 + 0.2 not equal to 0.3?", "Floats are binary fractions; 0.1 and 0.2 have no exact binary representation, so each is stored as the nearest double and the rounding errors add up to 0.30000000000000004. Compare with math.isclose or use Decimal."),
            qa("basic", "What does round(2.5) return and why?", "2. Python 3 uses round-half-to-even (banker's rounding) to avoid systematic upward bias when rounding many values. Use Decimal.quantize with ROUND_HALF_UP for 'school' rounding."),
            qa("intermediate", "When would you use Decimal instead of float?", "For money and anything that must match human decimal arithmetic exactly, with controlled precision and rounding. It is slower than float, so it is not used for scientific computing."),
            qa("intermediate", "What is -7 // 2 and -7 % 2?", "-4 and 1. Floor division rounds toward negative infinity and the remainder has the sign of the divisor, so (a // b) * b + a % b == a always holds."),
            qa("advanced", "Can Python integers overflow?", "No; int is arbitrary-precision and grows by adding internal 30-bit digits. Operations get slower for huge values, and int-to-str conversion of very large numbers is limited by default (sys.set_int_max_str_digits) to prevent DoS."),
        ],
        ["objects-mutability", "collections"],
        chain(
            ("0.1 literal", "decimal text", "Parse", "The source text 0.1 is a decimal number that must become a binary double."),
            ("Nearest double", "53-bit mantissa", "Round to binary", "0.1 has no exact binary form, so Python stores the closest double: 0.1000000000000000055...", "0.1"),
            ("Add 0.2", "rounding again", "Arithmetic", "Adding two approximations and rounding the result yields 0.30000000000000004.", "approx"),
            ("Compare", "isclose / Decimal", "Fix", "Compare with tolerance (math.isclose) or switch to Decimal('0.1') for exact base-10 math.", "result"),
        ),
    ),
    topic(
        "strings-fstrings", "Strings & f-strings", "core", "basic", "SF",
        "Immutable Unicode text, fast joins, and the format-spec mini language.",
        "A string is a printed label: you cannot edit the ink, you print a new label. f-strings are a label template where you fill the blanks right where you write them.",
        "str is an immutable sequence of Unicode code points. Every 'modification' (replace, upper, slicing, concatenation) returns a new string, so building text in a loop with += can be quadratic; collect pieces in a list and call ''.join(parts). f-strings (f'...') evaluate expressions inline and support a format-spec mini language after a colon: width, alignment, fill, sign, thousands separators, precision and type (f'{x:>10,.2f}'). The conversion flags !r, !s and !a call repr, str and ascii, and f'{x=}' prints both the expression and its value for debugging. Python 3.12 relaxed f-string parsing so quotes and nested f-strings work naturally. str.format and % formatting still exist; string.Template is useful for user-supplied templates because it cannot evaluate expressions. Common methods include split, strip, partition, startswith with tuples, casefold for caseless comparisons, and removeprefix/removesuffix.",
        ["Building log lines and reports with aligned columns.", "Debug prints with f'{var=}'.", "Parsing simple text with split, partition and strip.", "Safe user-facing templates with string.Template."],
        [
            "Strings are immutable; use ''.join for many concatenations.",
            "Format spec: [[fill]align][sign][width][,][.precision][type].",
            "!r inside f-strings shows repr, ideal for logging values with quotes.",
            "casefold() is the right tool for case-insensitive comparison.",
            "Never build SQL or shell commands with f-strings from user input.",
        ],
        [
            ex("Format-spec tour", "basic", "Width, alignment, precision, separators and debug '='.", "python", """
                name, qty, price = "widget", 1234, 3.14159
                print(f"{name:<10}|{qty:>8,}|{price:>8.2f}|")
                print(f"{name:^10}|{qty:08d}|{price:.1%}|")
                print(f"{255:#x} {255:#b} {1e6:.2e}")
                print(f"{name!r} {qty=} {price*2=:.3f}")
                width = 12
                print(f"{'dynamic':*^{width}}")
            """),
            ex("join vs +=", "intermediate", "Both work; join is linear and idiomatic.", "python", """
                words = ["fast", "clear", "pythonic"]
                print(", ".join(words))
                print("-".join(str(n) for n in range(5)))
                line = "  key = value = more  "
                key, sep, value = line.strip().partition("=")
                print(repr(key.strip()), repr(value.strip()))
                print("report.csv".removesuffix(".csv"), "Straße".casefold() == "STRASSE".casefold())
                print("a,b,,c".split(","), "a  b   c".split())
            """),
            ex("Template for untrusted templates", "intermediate", "Template substitutes names only; it cannot run expressions.", "python", """
                from string import Template

                t = Template("Hello $name, your order $order_id ships today.")
                print(t.substitute(name="Ada", order_id=42))
                print(t.safe_substitute(name="Ada"))
            """),
        ],
        ["f'{x:>10.2f}' · f'{n:,}' · f'{p:.1%}'", "f'{value!r}' · f'{expr=}'", "''.join(parts)", "s.split() · s.partition('=') · s.strip()", "s.removeprefix('v') · s.casefold()"],
        ["s += piece in a big loop can be O(n^2); use join.", "split(' ') and split() differ: the latter collapses whitespace and drops empties.", "str.format(**user_dict) with user-controlled format strings can leak attributes."],
        [
            qa("basic", "Why are Python strings immutable?", "Immutability makes them hashable (usable as dict keys), safe to share between names and threads, and allows interning and caching. Any modification creates a new string."),
            qa("basic", "What does f'{x=}' do?", "It expands to the expression text followed by its repr, e.g. 'x=42'. It is a quick debugging aid added in Python 3.8 and can be combined with a format spec like f'{x=:.2f}'."),
            qa("intermediate", "Why prefer ''.join over += in a loop?", "Each += may allocate a new string and copy the old content, giving quadratic time in the worst case. join computes the total size once and copies each piece once, so it is linear."),
            qa("intermediate", "lower() vs casefold()?", "casefold is a more aggressive Unicode-aware folding meant for caseless matching; for example 'ß'.casefold() is 'ss' while lower() leaves it as 'ß'."),
        ],
        ["bytes-unicode", "comprehensions"],
        chain(
            ("f'...'", "template literal", "Parse", "The compiler splits the f-string into literal text and replacement fields at compile time."),
            ("Evaluate", "{price * qty}", "Run expressions", "Each field's expression runs in the current scope, just like normal code.", "expr"),
            ("Convert", "!r / !s", "Optional conversion", "!r calls repr(), !s calls str(); default is format(value, spec).", "value"),
            ("Format spec", ">10,.2f", "Apply __format__", "The value's __format__ applies alignment, width, separators and precision.", "obj"),
            ("Join", "new str", "Build result", "All pieces are concatenated into one new immutable string.", "text"),
        ),
    ),
    topic(
        "bytes-unicode", "Bytes, Unicode & Encodings", "core", "intermediate", "BU",
        "str is text, bytes is binary; encode at the edges and decode as early as possible.",
        "Unicode code points are ideas of letters; an encoding like UTF-8 is the handwriting that turns them into ink (bytes). You must know the handwriting to read the note back.",
        "In Python 3, str holds Unicode code points and bytes holds raw 8-bit values; they never mix implicitly. str.encode(encoding) converts text to bytes and bytes.decode(encoding) converts back; UTF-8 is the default and the right choice almost everywhere. UTF-8 is variable-length: ASCII takes 1 byte, most accented letters 2, CJK characters 3, and emoji 4, so len(text) and len(text.encode()) differ. Decoding with the wrong codec causes UnicodeDecodeError or mojibake; the errors argument ('strict', 'replace', 'ignore', 'backslashreplace') controls handling. Visually identical strings can be different code point sequences (precomposed vs combining accents), so normalize with unicodedata.normalize('NFC', s) before comparing. bytearray is the mutable variant, and memoryview gives zero-copy slices of binary buffers. The 'Unicode sandwich' rule is: decode bytes at input, work with str inside, encode at output.",
        ["Reading files and network data with an explicit encoding.", "Normalizing user names before comparing or storing them.", "Building binary protocols with bytes, struct and memoryview.", "Fixing mojibake by finding the right codec."],
        [
            "Always pass encoding='utf-8' when opening text files.",
            "len(str) counts code points; len(bytes) counts bytes.",
            "Normalize (NFC/NFKC) before comparing user-entered text.",
            "bytes literals use b'...'; indexing bytes returns ints.",
            "memoryview slices without copying large buffers.",
        ],
        [
            ex("Encode and decode", "basic", "Different characters take different numbers of bytes in UTF-8.", "python", """
                for ch in ["A", "é", "€", "中"]:
                    data = ch.encode("utf-8")
                    print(repr(ch), hex(ord(ch)), data, len(data), "bytes")

                raw = "café".encode("utf-8")
                print(raw.decode("utf-8"))
                print(raw.decode("latin-1"))                    # mojibake
                print(b"caf\\xe9".decode("utf-8", errors="replace"))
            """),
            ex("Normalization", "intermediate", "Same look, different code points, until you normalize.", "python", """
                import unicodedata

                a = "caf\\u00e9"          # precomposed e-acute
                b = "cafe\\u0301"         # e + combining accent
                print(a, b, a == b, len(a), len(b))
                na, nb = (unicodedata.normalize("NFC", s) for s in (a, b))
                print(na == nb, [unicodedata.name(c) for c in b[-2:]])
            """),
            ex("bytes, bytearray, memoryview", "advanced", "Mutable buffers and zero-copy views.", "python", """
                import struct

                buf = bytearray(b"HEADERpayload")
                view = memoryview(buf)
                view[0:6] = b"header"
                print(buf, buf[0], bytes(view[6:]))
                packed = struct.pack(">HI", 7, 65536)
                print(packed.hex(" "), struct.unpack(">HI", packed))
            """),
        ],
        ["s.encode('utf-8') · b.decode('utf-8', errors='replace')", "open(p, encoding='utf-8')", "unicodedata.normalize('NFC', s)", "bytes.fromhex('de ad') · b.hex()", "struct.pack('>I', n)"],
        ["Relying on the platform default encoding (historically cp1252 on Windows).", "Concatenating str and bytes raises TypeError.", "Slicing UTF-8 bytes can cut a multi-byte character in half.", "Iterating bytes yields ints, not 1-byte strings."],
        [
            qa("basic", "What is the difference between str and bytes?", "str is a sequence of Unicode code points (text); bytes is a sequence of integers 0-255 (binary data). You convert between them with encode and decode using a named encoding."),
            qa("intermediate", "Why can len('é') differ from len('é'.encode())?", "len of str counts code points (1) while UTF-8 encodes U+00E9 as two bytes. A string may also contain e plus a combining accent, making len 2 even as text."),
            qa("intermediate", "What is the Unicode sandwich?", "Decode bytes to str as soon as data enters the program, operate only on str internally, and encode back to bytes only when writing out. It confines encoding bugs to the boundaries."),
            qa("advanced", "Why normalize Unicode strings?", "Characters like é can be represented as one precomposed code point or a base letter plus combining mark. Without NFC/NFKC normalization, equal-looking usernames or keys compare unequal, which causes bugs and spoofing risks."),
        ],
        ["strings-fstrings", "objects-mutability"],
        chain(
            ("Bytes in", "b'caf\\xc3\\xa9'", "Input", "Data from a file or socket arrives as raw bytes."),
            ("decode()", "utf-8", "Decode early", "bytes.decode('utf-8') turns the bytes into code points.", "bytes"),
            ("str inside", "'café'", "Work with text", "All processing (split, normalize, compare) happens on str.", "str"),
            ("encode()", "utf-8", "Encode late", "Before writing out, str.encode('utf-8') produces bytes again.", "str"),
            ("Bytes out", "file / socket", "Output", "The wire or disk only ever sees bytes.", "bytes"),
        ),
    ),
    topic(
        "slicing-unpacking", "Slicing & Unpacking", "core", "basic", "SU",
        "seq[start:stop:step], slice objects, slice assignment and star unpacking.",
        "Slicing is cutting a loaf of bread with markers between slices, not on them. Unpacking is handing out the slices to named people, with one person allowed to take 'the rest'.",
        "Slices take half-open ranges [start, stop) so len(s[a:b]) == b - a and s[:k] + s[k:] == s. Negative indices count from the end, omitted bounds default to the ends, and out-of-range bounds clamp instead of raising. A step can skip or reverse (s[::-1]). Slicing a list makes a shallow copy; slice assignment can replace, insert or delete ranges in place, and del s[a:b] removes them. slice(start, stop, step) objects let you name and reuse slices, and custom classes receive them in __getitem__. Iterable unpacking binds several names at once, supports nesting, and a single starred name collects the leftovers into a list. In calls, *iterable and **mapping spread arguments; in literals, [*a, *b] and {**d1, **d2} merge collections.",
        ["Parsing fixed-width records with named slice objects.", "Swapping values and returning multiple results.", "Splitting head and tail: first, *rest = items.", "Merging lists and dicts in a literal."],
        [
            "Half-open ranges: s[:k] + s[k:] == s.",
            "Slices clamp out-of-range bounds; indexing raises IndexError.",
            "Slice assignment can change list length in place.",
            "Only one starred target per unpacking; it is always a list.",
            "a, b = b, a swaps via a temporary tuple.",
        ],
        [
            ex("Slicing rules", "basic", "Negative indices, steps, copies and clamping.", "python", """
                s = list(range(10))
                print(s[2:5], s[-3:], s[:-3], s[::3], s[::-1])
                print(s[8:100], s[100:])          # clamps, no error
                copy = s[:]
                print(copy == s, copy is s)
                text = "Python"
                print(text[1:4], text[::-1], text[-1])
            """),
            ex("Slice assignment and slice objects", "intermediate", "Replace, insert and delete ranges; name slices for records.", "python", """
                xs = [0, 1, 2, 3, 4, 5]
                xs[1:3] = ["a", "b", "c"]          # replace 2 with 3
                xs[0:0] = ["start"]               # insert
                del xs[-2:]                       # delete
                print(xs)

                record = "2026-10-17ALICE     0042"
                DATE, NAME, QTY = slice(0, 10), slice(10, 20), slice(20, 24)
                print(record[DATE], record[NAME].strip(), int(record[QTY]))
            """),
            ex("Unpacking everywhere", "basic", "Nested targets, star targets, and spreading in calls and literals.", "python", """
                head, *body, tail = [1, 2, 3, 4, 5]
                (x, y), label = (3, 4), "point"
                print(head, body, tail, x, y, label)

                def area(w, h, unit="cm"):
                    return f"{w * h} {unit}"

                dims = (3, 4)
                opts = {"unit": "m"}
                print(area(*dims, **opts))
                print([*range(3), *"ab"], {**{"a": 1}, "b": 2})
                for i, (k, v) in enumerate({"x": 1, "y": 2}.items()):
                    print(i, k, v)
            """),
        ],
        ["s[start:stop:step] · s[::-1] · s[:]", "slice(0, 10) · s[DATE]", "xs[1:3] = new · del xs[a:b]", "first, *rest = xs", "f(*args, **kwargs) · [*a, *b] · {**d1, **d2}"],
        ["s[:] on a list of lists is a shallow copy; inner lists are shared.", "Extended slice assignment (step != 1) requires equal lengths.", "Unpacking a dict iterates keys, not items.", "Unpacking too many or too few values raises ValueError."],
        [
            qa("basic", "Why are slices half-open?", "With [start, stop), the length is stop - start, adjacent slices s[:k] and s[k:] don't overlap and rejoin to s, and empty ranges are natural. It mirrors range()."),
            qa("basic", "What is the difference between s[10] and s[10:] on a short list?", "s[10] raises IndexError; s[10:] returns an empty list because slice bounds are clamped to the sequence length."),
            qa("intermediate", "How does a, b = b, a work?", "The right side is evaluated first into a tuple (b, a), then unpacked into the targets left to right. CPython optimizes small cases with stack rotation, but semantically it is tuple packing and unpacking."),
            qa("intermediate", "How does a class support slicing?", "Implement __getitem__ and check whether the key is a slice object; slice.indices(len(self)) normalizes start, stop and step for the sequence length."),
        ],
        ["comprehensions", "collections"],
        chain(
            ("s[1:7:2]", "slice syntax", "Build slice", "The subscript creates slice(1, 7, 2) and passes it to __getitem__."),
            ("Normalize", "slice.indices(n)", "Clamp bounds", "Negative and out-of-range values are converted to valid positions.", "slice"),
            ("Walk", "1, 3, 5", "Step through", "Indices are generated from start toward stop by step, stop excluded.", "idx"),
            ("New object", "shallow copy", "Return", "A new list (or str/tuple) containing references to the selected items.", "items"),
        ),
    ),
    topic(
        "truthiness-identity", "Truthiness, Identity & Equality", "core", "basic", "TI",
        "What counts as False, how and/or really work, and is vs ==.",
        "Truthiness asks 'is the box empty?' rather than 'is the box exactly False?'. Identity asks 'is this the same physical box?' while equality asks 'do the boxes hold the same things?'.",
        "Every object has a truth value: None, False, zero numbers, and empty containers are falsy; almost everything else is truthy. bool(x) calls __bool__, falling back to __len__, and objects with neither are truthy. The operators and/or short-circuit and return one of their operands, not necessarily a bool, which enables idioms like name = given or 'anonymous' but also bugs when 0 or '' are valid values. not always returns a bool. == calls __eq__ and compares values; is compares identity (the same object in memory) and cannot be overloaded. Use is only with singletons such as None, True, False, Ellipsis and sentinel objects. CPython caches small ints (-5..256) and interns some strings, so is can appear to work for them, but that is an implementation detail. Comparisons chain: a < b < c means a < b and b < c with b evaluated once.",
        ["Default values with or (when falsy values are invalid).", "Sentinel objects to distinguish 'not passed' from None.", "Writing __bool__ / __len__ for custom containers.", "Readable range checks with chained comparisons."],
        [
            "Falsy: None, False, 0, 0.0, 0j, '', b'', [], (), {}, set(), range(0).",
            "and/or return an operand; not returns a bool.",
            "Use 'x is None', never 'x == None'.",
            "is cannot be overridden; == can via __eq__.",
            "Chained comparisons evaluate the middle operand once.",
        ],
        [
            ex("Truth table of common values", "basic", "bool() of built-in values and custom objects.", "python", """
                values = [0, 1, -1, 0.0, "", "0", [], [0], {}, None, set(), range(0)]
                for v in values:
                    print(f"{v!r:>8} -> {bool(v)}")

                class Basket:
                    def __init__(self, items): self.items = items
                    def __len__(self): return len(self.items)

                print(bool(Basket([])), bool(Basket(["apple"])))
            """),
            ex("and / or return operands", "intermediate", "Great for defaults, dangerous when 0 is valid.", "python", """
                print(0 or "default", "" or None, [] and "never", 3 and 4)
                def retries(n=None):
                    bad = n or 3                       # 0 becomes 3!
                    good = 3 if n is None else n
                    return bad, good
                print(retries(0), retries(None), retries(5))
                print(1 < 2 < 3, 1 < 3 < 2, not [])
            """),
            ex("Identity vs equality", "intermediate", "is checks the same object; sentinels make 'missing' explicit.", "python", """
                a = [1, 2]; b = [1, 2]
                print(a == b, a is b)
                x = int("1000"); y = int("1000")
                print(x == y, x is y)              # big ints are not cached

                _MISSING = object()
                def get(d, key, default=_MISSING):
                    if key in d:
                        return d[key]
                    if default is _MISSING:
                        raise KeyError(key)
                    return default
                print(get({"a": None}, "a"), get({}, "b", None))
            """),
        ],
        ["bool(x) → __bool__ then __len__", "x = given or fallback", "x is None · x is not None", "_MISSING = object()  # sentinel", "lo <= x < hi"],
        ["'n or default' silently replaces valid 0, '' or [] values.", "Using is to compare strings or numbers works sometimes and then fails.", "numpy arrays and pandas objects raise on bool(); use .any()/.all().", "Defining __eq__ without __hash__ makes instances unhashable."],
        [
            qa("basic", "Which values are falsy in Python?", "None, False, numeric zeros (0, 0.0, 0j, Decimal(0)), empty sequences and collections ('', [], (), {}, set(), range(0)) and objects whose __bool__ returns False or __len__ returns 0."),
            qa("basic", "Why use 'is None' instead of '== None'?", "None is a singleton so identity is the exact check, it is faster, and it can't be fooled by a class whose __eq__ returns True for anything."),
            qa("intermediate", "What does 'a or b' return?", "a if a is truthy, otherwise b, without converting to bool. b is evaluated only when needed (short-circuit)."),
            qa("intermediate", "Why does 256 is 256 give True but some larger ints don't?", "CPython preallocates ints from -5 to 256 and reuses them, and the compiler may also fold equal constants. Larger ints created at runtime are separate objects. Identity of values is an implementation detail; compare with ==."),
        ],
        ["objects-mutability", "classes-dataclasses"],
        chain(
            ("if obj:", "truth test", "Ask for truth", "Python needs a bool for the condition."),
            ("__bool__?", "defined?", "Try __bool__", "If the type defines __bool__, its result (must be bool) is used.", "obj"),
            ("__len__?", "fallback", "Try __len__", "Otherwise len(obj) == 0 means False, anything else True.", "obj"),
            ("Default True", "plain objects", "Fallback", "Objects without either method are always truthy.", "obj"),
        ),
    ),
    topic(
        "control-flow-match", "Control Flow, match & Walrus", "core", "intermediate", "PM",
        "Loops with else, structural pattern matching, and assignment expressions.",
        "match is a mail sorter that looks at the shape of each parcel (size, labels, contents) rather than just its tracking number, and opens the right ones for you.",
        "Python's for and while loops support an else clause that runs only when the loop finishes without break, which neatly expresses 'search, and handle not found'. The match statement (3.10+) performs structural pattern matching: it compares a subject against patterns that can be literals, captures, sequences, mappings, class patterns with keyword or positional attributes, alternatives with |, and wildcards with _. Patterns can bind names, and guards (case x if x > 0) add conditions. Bare names in patterns are captures, not comparisons, so to match a constant you must use a dotted name like Color.RED. Class patterns use __match_args__ for positional matching, which dataclasses generate automatically. The walrus operator := (3.8+) assigns inside an expression, useful in while loops reading chunks and in comprehensions that reuse a computed value. Use these tools for clarity, not cleverness.",
        ["Parsing commands or JSON-like messages by shape.", "Search loops with for/else.", "Reading streams with while (chunk := f.read(n)).", "AST and event dispatch in interpreters."],
        [
            "Loop else runs when no break happened.",
            "case name: captures anything; use Enum.MEMBER or literals for constants.",
            "Mapping patterns match subsets of keys; **rest captures others.",
            "Class patterns use isinstance plus attribute checks.",
            ":= binds in the enclosing scope, even inside comprehensions.",
        ],
        [
            ex("Matching command shapes", "intermediate", "Sequence, literal, alternative and guard patterns.", "python", """
                def handle(cmd):
                    match cmd.split():
                        case ["quit" | "exit"]:
                            return "bye"
                        case ["go", ("north" | "south") as d]:
                            return f"moving {d}"
                        case ["take", *items] if items:
                            return f"taking {', '.join(items)}"
                        case [verb, *_]:
                            return f"unknown verb {verb!r}"
                        case []:
                            return "say something"

                for c in ["quit", "go north", "take key lamp", "dance", "", "take"]:
                    print(repr(c), "->", handle(c))
            """),
            ex("Mapping and class patterns", "advanced", "Destructure dicts and dataclasses in one step.", "python", """
                from dataclasses import dataclass

                @dataclass
                class Point:
                    x: int
                    y: int

                def describe(obj):
                    match obj:
                        case {"type": "user", "name": str(name), **rest}:
                            return f"user {name} extra={rest}"
                        case Point(0, 0):
                            return "origin"
                        case Point(x=0, y=y):
                            return f"on y axis at {y}"
                        case Point(x, y) if x == y:
                            return f"diagonal {x}"
                        case _:
                            return "something else"

                for o in [{"type": "user", "name": "ada", "id": 1}, Point(0, 0), Point(0, 5), Point(2, 2), 42]:
                    print(describe(o))
            """),
            ex("for/else and the walrus", "basic", "Search loops and assignment expressions.", "python", """
                def first_negative(nums):
                    for i, n in enumerate(nums):
                        if n < 0:
                            print("found at", i)
                            break
                    else:
                        print("no negatives")

                first_negative([3, 1, -2])
                first_negative([1, 2])

                import io
                stream = io.StringIO("abcdefghij")
                while chunk := stream.read(4):
                    print("chunk", chunk)
                data = [1, 5, 9, 12]
                print([y for x in data if (y := x * x) > 20])
            """),
        ],
        ["match x: case [a, b]: · case {'k': v}: · case Cls(attr=v):", "case A | B: · case _: · case x if cond:", "for ...: ... else: ...  # no break", "while (line := f.readline()):", "__match_args__ = ('x', 'y')"],
        ["case RED: captures anything into RED instead of comparing; use Color.RED.", "match does not fall through; the first matching case wins.", "str patterns in sequence patterns: a string subject never matches [a, b].", "Overusing := makes code harder to read."],
        [
            qa("intermediate", "When does a loop's else block run?", "When the loop completes normally (iterable exhausted or while condition false) without hitting break. It does not run after break, and it runs even when the loop body never executed."),
            qa("intermediate", "Why does 'case STATUS:' match everything?", "A bare name in a pattern is a capture pattern that binds the subject to that name. Constants must be dotted names (Status.OK), literals, or checked with a guard."),
            qa("advanced", "How do class patterns work?", "case Point(x=0, y=y) checks isinstance(subject, Point) then reads attributes. Positional sub-patterns are mapped to attribute names via Point.__match_args__, which dataclasses and namedtuples define automatically."),
            qa("basic", "What is the walrus operator?", "':=' assigns a value to a name as part of an expression and returns it, e.g. while (chunk := f.read(4096)):. It avoids computing a value twice or splitting a loop condition awkwardly."),
        ],
        ["classes-dataclasses", "comprehensions"],
        chain(
            ("Subject", "match cmd", "Evaluate", "The subject expression is evaluated once."),
            ("case 1", "pattern test", "Try patterns", "Patterns are tried top to bottom; structure, types and literals must fit.", "value"),
            ("Bind", "captures", "Capture names", "On a structural match, capture names are bound to the matching parts.", "match"),
            ("Guard", "if cond", "Check guard", "If a guard is present it must be truthy, otherwise the next case is tried.", "names"),
            ("Run body", "first win", "Execute", "The first case that matches and passes its guard runs; no fall-through.", "ok"),
        ),
    ),
    topic(
        "dict-internals", "Dict Internals & Ordering", "core", "advanced", "DI",
        "Compact hash tables, insertion order, views and safe mutation.",
        "A dict is a library with a card catalog: the catalog (hash index) says which shelf slot to look at, and the books sit on shelves in the order they arrived.",
        "CPython's dict is a hash table split into a sparse index array and a dense entries array of (hash, key, value). Lookup hashes the key, probes the index with open addressing until it finds a slot whose stored hash and key match (identity first, then ==), giving O(1) average time. Because entries are appended in order, dicts preserve insertion order, which is a language guarantee since 3.7; deleting and reinserting a key moves it to the end. The table resizes when about two thirds full, which occasionally costs O(n) but amortizes to O(1). keys(), values() and items() return live views: keys and items views support set operations. Mutating the size of a dict while iterating raises RuntimeError, so iterate over list(d) when deleting. Useful methods include get, setdefault, pop with default, update, and the | and |= merge operators (3.9+). Keys must be hashable and must keep a stable hash while stored.",
        ["Caches and memo tables keyed by tuples.", "Counting and grouping (with Counter/defaultdict).", "Ordered JSON-like records relying on insertion order.", "Fast set-like key comparisons with dict views."],
        [
            "Average O(1) get/set/delete; worst case O(n) with pathological collisions.",
            "Insertion order is guaranteed; updates keep position, delete+insert moves to end.",
            "Views are dynamic and keys()/items() support &, |, -.",
            "Don't add or remove keys while iterating; iterate over a copy.",
            "d1 | d2 merges (right wins); d.get(k, default) avoids KeyError.",
        ],
        [
            ex("Order, views and merging", "intermediate", "Views reflect later changes; keys views do set algebra.", "python", """
                d = {"b": 1, "a": 2}
                keys = d.keys()
                d["c"] = 3
                print(list(keys))                 # live view sees 'c'
                d["b"] = 10                       # update keeps position
                del d["a"]; d["a"] = 2            # reinsert goes to end
                print(d)
                other = {"a": 0, "z": 26}
                print(d.keys() & other.keys(), d.keys() - other.keys())
                print(d | other, {**other, **d})
            """),
            ex("Safe deletion while iterating", "basic", "Changing size during iteration raises; copy the keys first.", "python", """
                prices = {"apple": 0, "pear": 3, "plum": 0, "fig": 5}
                try:
                    for k in prices:
                        if prices[k] == 0:
                            del prices[k]
                except RuntimeError as e:
                    print("error:", e)

                prices = {"apple": 0, "pear": 3, "plum": 0, "fig": 5}
                for k in list(prices):
                    if prices[k] == 0:
                        del prices[k]
                print(prices)
                print({k: v for k, v in prices.items() if v > 3})
            """),
            ex("Hashing and collisions", "advanced", "Keys that hash equal still work; lookup checks equality too.", "python", """
                class Key:
                    def __init__(self, name): self.name = name
                    def __hash__(self): return 42             # every key collides
                    def __eq__(self, other): return isinstance(other, Key) and self.name == other.name
                    def __repr__(self): return f"Key({self.name!r})"

                d = {Key("a"): 1, Key("b"): 2}
                print(d[Key("b")], len(d))
                print(hash(1) == hash(1.0) == hash(True), {1: "int", 1.0: "float", True: "bool"})
                import sys
                print(sys.getsizeof({}), sys.getsizeof({i: i for i in range(100)}))
            """),
        ],
        ["d.get(k, default) · d.setdefault(k, []).append(x)", "d.pop(k, None) · d.popitem()", "d1 | d2 · d1 |= d2", "d.keys() & other.keys()", "for k in list(d): ..."],
        ["1, 1.0 and True are the same key because they are equal and hash equal.", "Mutating a key object after insertion makes it unreachable.", "Relying on order in code that must also run on very old Pythons (< 3.7).", "dict.fromkeys(keys, []) shares one list among all keys."],
        [
            qa("intermediate", "Are dicts ordered?", "Yes, since Python 3.7 the language guarantees insertion order (CPython 3.6 did it as an implementation detail). Updating an existing key keeps its position; deleting and re-adding moves it to the end."),
            qa("advanced", "How does a dict lookup work?", "Python computes hash(key), uses it to pick a slot in the index table and probes with open addressing. For each candidate it compares the stored hash and then identity or == with the key, returning the value on a match or raising KeyError when an empty slot is reached."),
            qa("advanced", "Why does CPython use a separate index and entries array?", "The compact layout (3.6+) stores a small sparse index of integers plus a dense array of entries, cutting memory 20-25% and making iteration fast and naturally ordered."),
            qa("intermediate", "Why does {1: 'a', True: 'b'} have one key?", "1 == True and hash(1) == hash(True), so they are the same dict key. The first key object is kept and the value is overwritten with 'b'."),
        ],
        ["collections", "objects-mutability"],
        chain(
            ("d[key]", "lookup", "Start", "Lookup begins with the key object."),
            ("hash(key)", "__hash__", "Hash", "The key's hash picks a starting slot in the sparse index.", "key"),
            ("Probe index", "open addressing", "Find slot", "Collisions are resolved by probing a pseudo-random sequence of slots.", "hash"),
            ("Compare", "is, then ==", "Check entry", "The entry's stored hash and key are compared; identity is checked before equality.", "slot"),
            ("Value", "entries[i]", "Return", "On a match the value from the dense entries array is returned.", "hit"),
        ),
    ),
    topic(
        "sets-hashing", "Sets & Hashing (__hash__ / __eq__)", "core", "intermediate", "SH",
        "Fast membership and set algebra, plus the contract every hashable object must keep.",
        "A set is a club bouncer with a perfect memory: you are either on the list or not, and nobody gets in twice. Your hash is your membership card number; two people with equal identities must carry the same number.",
        "set is a mutable unordered collection of unique hashable objects with O(1) average membership, add and remove. frozenset is its immutable, hashable twin, so it can be a dict key or a member of another set. Sets support union |, intersection &, difference -, symmetric difference ^, and subset tests <=. Hashing is what makes this fast: hash(x) must stay constant during the object's lifetime, and objects that compare equal must have equal hashes (the reverse need not hold). By default user classes hash by identity; if you define __eq__ without __hash__, Python sets __hash__ to None and instances become unhashable. To make value objects hashable, base __hash__ on the same immutable fields used by __eq__, for example hash((self.x, self.y)), or use @dataclass(frozen=True). String hashes are randomized per process (PYTHONHASHSEED) to defend against hash-flooding attacks, so set iteration order of strings can vary between runs.",
        ["Deduplicating while not caring about order.", "Fast 'have I seen this?' checks in graph traversals.", "Comparing permission sets or tag sets with set algebra.", "Using frozenset or frozen dataclasses as dict keys."],
        [
            "a == b must imply hash(a) == hash(b).",
            "Hash only immutable state that also defines equality.",
            "__eq__ without __hash__ makes instances unhashable.",
            "frozenset and frozen dataclasses are hashable value types.",
            "Set iteration order is arbitrary; sort for stable output.",
        ],
        [
            ex("Set algebra", "basic", "Membership, union, intersection and difference.", "python", """
                backend = {"python", "sql", "docker", "linux"}
                frontend = {"js", "css", "docker"}
                print(sorted(backend & frontend), sorted(backend | frontend))
                print(sorted(backend - frontend), sorted(backend ^ frontend))
                print({"sql", "linux"} <= backend, "go" in backend)
                seen = set()
                dupes = [x for x in [3, 1, 3, 2, 1] if x in seen or seen.add(x)]
                print(dupes, list(dict.fromkeys([3, 1, 3, 2, 1])))   # ordered dedupe
            """),
            ex("The __eq__/__hash__ contract", "intermediate", "Defining __eq__ removes the default hash; restore it correctly.", "python", """
                class Loose:
                    def __init__(self, x): self.x = x
                    def __eq__(self, o): return isinstance(o, Loose) and self.x == o.x

                try:
                    {Loose(1)}
                except TypeError as e:
                    print("TypeError:", e)

                class Money:
                    __slots__ = ("amount", "currency")
                    def __init__(self, amount, currency):
                        self.amount, self.currency = amount, currency
                    def __eq__(self, o):
                        return isinstance(o, Money) and (self.amount, self.currency) == (o.amount, o.currency)
                    def __hash__(self):
                        return hash((self.amount, self.currency))

                print(len({Money(5, "EUR"), Money(5, "EUR"), Money(5, "USD")}))
            """),
            ex("Frozen value objects", "intermediate", "frozen dataclasses and frozensets as dict keys.", "python", """
                from dataclasses import dataclass

                @dataclass(frozen=True)
                class Cell:
                    row: int
                    col: int

                walls = {Cell(0, 1), Cell(2, 2)}
                print(Cell(0, 1) in walls, hash(Cell(0, 1)) == hash(Cell(0, 1)))
                routes = {frozenset({"A", "B"}): 5}
                print(routes[frozenset({"B", "A"})])
            """),
        ],
        ["a | b · a & b · a - b · a ^ b · a <= b", "s.add(x) · s.discard(x) · s.remove(x)", "frozenset(items)", "def __hash__(self): return hash((self.a, self.b))", "@dataclass(frozen=True)"],
        ["{} is an empty dict; use set() for an empty set.", "Hashing mutable fields: changing them strands the object in the wrong bucket.", "remove() raises KeyError on missing items; discard() does not.", "Expecting deterministic order of sets of strings across runs."],
        [
            qa("intermediate", "What is the __hash__/__eq__ contract?", "If a == b then hash(a) must equal hash(b), and an object's hash must not change while it is in a set or dict. Unequal objects may share a hash (collisions), which only costs speed."),
            qa("intermediate", "Why do my objects become unhashable after adding __eq__?", "Python sets __hash__ = None when a class defines __eq__ without __hash__, because the identity-based default would violate the contract. Define __hash__ from the same fields or use a frozen dataclass."),
            qa("basic", "set vs frozenset?", "set is mutable and unhashable; frozenset is immutable and hashable, so it can be a dict key or an element of another set."),
            qa("advanced", "Why are string hashes randomized?", "Hash randomization (SipHash with a per-process seed) prevents attackers from crafting many colliding keys that degrade dict/set operations to O(n) each, a denial-of-service attack. PYTHONHASHSEED can fix the seed for reproducibility."),
        ],
        ["dict-internals", "classes-dataclasses"],
        chain(
            ("x in s", "membership", "Ask", "Membership tests start from the candidate object."),
            ("hash(x)", "__hash__", "Hash", "The hash chooses which bucket of the table to inspect.", "x"),
            ("Bucket", "probe", "Locate", "Python probes slots until it finds a matching hash or an empty slot.", "hash"),
            ("__eq__", "confirm", "Confirm", "Equal hashes are confirmed with identity or __eq__; mismatches keep probing.", "cand"),
            ("True/False", "O(1) avg", "Answer", "Found means True, an empty slot means False, without scanning everything.", "result"),
        ),
    ),
    topic(
        "sorting-keys", "Sorting & Key Functions", "core", "basic", "SK",
        "sorted vs list.sort, key functions, stability and multi-level ordering.",
        "Sorting with a key is like sorting students by their exam score written on a sticky note: you compare the notes, but you move the students.",
        "sorted(iterable) returns a new list; list.sort() sorts in place and returns None. Both use Timsort, an adaptive, stable merge sort that runs in O(n log n) worst case and close to O(n) on already partially ordered data. The key argument maps each element to a comparison key exactly once (decorate-sort-undecorate), which is faster and clearer than comparing complex objects directly. operator.itemgetter and attrgetter build fast key functions, and tuples as keys give multi-level sorting. Stability means equal keys keep their original relative order, so you can sort by a secondary key first and then by the primary key, or mix ascending and descending. reverse=True flips the order while staying stable. For legacy comparison functions use functools.cmp_to_key. min, max, heapq.nsmallest and itertools.groupby also accept key functions.",
        ["Leaderboards sorted by score then name.", "Case-insensitive sorting with key=str.casefold.", "Top-N queries with heapq.nlargest(key=...).", "Grouping sorted records with itertools.groupby."],
        [
            "list.sort() returns None; sorted() returns a new list.",
            "key is called once per element; comparisons use the keys.",
            "Timsort is stable: equal keys keep input order.",
            "Mixed directions: negate numeric keys or sort in multiple stable passes.",
            "itemgetter/attrgetter are fast, picklable key functions.",
        ],
        [
            ex("Key functions", "basic", "Sort by length, case-insensitive, by dict field.", "python", """
                from operator import itemgetter

                words = ["banana", "Apple", "cherry", "date"]
                print(sorted(words), sorted(words, key=str.casefold))
                print(sorted(words, key=len), sorted(words, key=len, reverse=True))
                people = [{"name": "ann", "age": 31}, {"name": "bob", "age": 25}, {"name": "cid", "age": 31}]
                print([p["name"] for p in sorted(people, key=itemgetter("age"))])
                print(max(people, key=itemgetter("age"))["name"])
            """),
            ex("Multi-key and mixed direction", "intermediate", "Tuple keys, negation, and stable multi-pass sorting.", "python", """
                from operator import attrgetter
                from dataclasses import dataclass

                @dataclass
                class Player:
                    name: str
                    score: int
                    team: str

                ps = [Player("zed", 90, "red"), Player("amy", 95, "blue"), Player("bo", 90, "blue")]
                by_score_desc_name = sorted(ps, key=lambda p: (-p.score, p.name))
                print([p.name for p in by_score_desc_name])

                tmp = sorted(ps, key=attrgetter("name"))              # secondary first
                result = sorted(tmp, key=attrgetter("team"), reverse=True)
                print([(p.team, p.name) for p in result])
            """),
            ex("cmp_to_key and sort() returning None", "intermediate", "Adapting an old-style comparator; a classic mistake.", "python", """
                from functools import cmp_to_key

                def by_version(a, b):
                    pa, pb = [int(x) for x in a.split(".")], [int(x) for x in b.split(".")]
                    return (pa > pb) - (pa < pb)

                versions = ["1.10.0", "1.2.3", "1.2.10", "0.9"]
                print(sorted(versions))                                  # string order is wrong
                print(sorted(versions, key=cmp_to_key(by_version)))
                print(sorted(versions, key=lambda v: tuple(map(int, v.split(".")))))
                xs = [3, 1, 2]
                print(xs.sort(), xs)
            """),
        ],
        ["sorted(xs, key=f, reverse=True)", "xs.sort(key=str.casefold)", "key=itemgetter('age') · key=attrgetter('name')", "key=lambda r: (-r.score, r.name)", "functools.cmp_to_key(cmp)"],
        ["x = xs.sort() sets x to None.", "Sorting strings of numbers gives lexicographic order ('10' < '9').", "Mixing types (int and str) raises TypeError in Python 3.", "NaN values break ordering silently."],
        [
            qa("basic", "sorted() vs list.sort()?", "sorted accepts any iterable and returns a new list; list.sort sorts the list in place, returns None and is slightly more memory efficient."),
            qa("intermediate", "What does stable sorting mean and why is it useful?", "Elements with equal keys keep their original relative order. It lets you sort by multiple criteria in successive passes (least significant first) and keeps prior orderings meaningful."),
            qa("intermediate", "Why is key= preferred over a comparison function?", "The key is computed once per element (n calls) and then cheap comparisons are made on keys, whereas a cmp function is called O(n log n) times. Python 3 removed cmp= in favor of key; cmp_to_key adapts legacy code."),
            qa("advanced", "What algorithm does Python use for sorting?", "Timsort (now with powersort merge policy in 3.11+): it detects existing runs, extends short runs with binary insertion sort, and merges runs with galloping. It is stable, O(n log n) worst case and O(n) on sorted input."),
        ],
        ["functions-args", "collections"],
        chain(
            ("Items", "unsorted", "Input", "sorted() receives any iterable and materializes a list."),
            ("key(x)", "once each", "Decorate", "The key function is called once per item to produce comparable keys.", "item"),
            ("Timsort", "find runs", "Sort keys", "Natural runs are found and merged; equal keys keep their order.", "keys"),
            ("Undecorate", "items only", "Return", "The items are returned in key order; the keys are discarded.", "order"),
        ),
    ),
]

TOPICS += [
    topic(
        "lambdas-higher-order", "Lambdas & Higher-Order Functions", "functions", "basic", "LH",
        "Functions are values: pass them, return them, and compose them.",
        "A higher-order function is a kitchen appliance that takes an attachment: the mixer stays the same, and you snap in a whisk, a hook or a blade (the function you pass).",
        "In Python functions are first-class objects: they can be stored in variables and data structures, passed as arguments and returned from other functions. A higher-order function takes or returns a function, such as map, filter, sorted(key=...), max(key=...) and functools.reduce. lambda creates a small anonymous function limited to a single expression; it is ideal for short key functions and callbacks but should not be assigned to a name (use def for a name and a docstring). map and filter return lazy iterators, and comprehensions are often clearer than map/filter with lambdas. Returning inner functions creates closures that remember variables from the enclosing scope, which is the basis of decorators and factories. A classic pitfall is late binding: lambdas created in a loop all see the final loop value unless you bind it via a default argument. The operator module provides fast function versions of operators (add, mul, itemgetter, methodcaller).",
        ["Key functions for sorted, min, max and groupby.", "Callback registries and event handlers.", "Function factories such as make_multiplier(3).", "Strategy selection via a dict of functions."],
        [
            "lambda args: expression; no statements or annotations.",
            "map/filter are lazy; wrap in list() to materialize.",
            "Prefer comprehensions over map+lambda for readability.",
            "Loop lambdas capture variables late; bind with x=x.",
            "operator.add/mul/itemgetter avoid trivial lambdas.",
        ],
        [
            ex("Functions as values", "basic", "Store functions in a dict and pass them around.", "python", """
                import operator

                ops = {"+": operator.add, "-": operator.sub, "*": operator.mul, "max": max}
                for sym, fn in ops.items():
                    print(sym, fn(7, 3))

                def apply_twice(f, x):
                    return f(f(x))
                print(apply_twice(lambda n: n * 10, 2), apply_twice(str.upper, "hi"))
            """),
            ex("map, filter, reduce vs comprehensions", "basic", "Equivalent pipelines, two styles.", "python", """
                from functools import reduce

                nums = [1, 2, 3, 4, 5, 6]
                print(list(map(lambda n: n * n, filter(lambda n: n % 2 == 0, nums))))
                print([n * n for n in nums if n % 2 == 0])
                print(reduce(lambda acc, n: acc * n, nums, 1))
                lazy = map(str, nums)
                print(lazy, next(lazy), list(lazy))
            """),
            ex("Late binding in loops", "intermediate", "All closures see the last i unless you bind it.", "python", """
                bad = [lambda: i for i in range(3)]
                good = [lambda i=i: i for i in range(3)]
                print([f() for f in bad], [f() for f in good])

                def make_multiplier(k):
                    def mul(x):
                        return x * k
                    return mul
                triple = make_multiplier(3)
                print(triple(5), triple.__closure__[0].cell_contents)
            """),
        ],
        ["lambda x: x * 2", "map(f, xs) · filter(pred, xs)", "functools.reduce(f, xs, init)", "operator.itemgetter(1) · operator.methodcaller('strip')", "[lambda i=i: i for i in range(3)]"],
        ["Assigning lambdas to names (f = lambda...) loses a useful __name__ in tracebacks.", "Late-binding closures in loops.", "Lambdas cannot be pickled, which breaks multiprocessing.", "map(f, a, b) stops at the shortest iterable silently."],
        [
            qa("basic", "What is a higher-order function?", "A function that takes another function as an argument or returns one. Examples are map, filter, sorted with key, and decorators."),
            qa("basic", "What are the limits of lambda?", "A lambda is a single expression with no statements (no assignment statements, loops, try or return keyword), no annotations and an anonymous __name__. Use def for anything non-trivial."),
            qa("intermediate", "Why does [lambda: i for i in range(3)] return 2 for every call?", "Closures capture variables, not values. All lambdas reference the same i, which is 2 after the loop. Bind the current value with a default argument (lambda i=i: i) or use functools.partial."),
            qa("intermediate", "map/filter or comprehension?", "Comprehensions are usually more readable and avoid lambda call overhead. map is fine (and fast) when applying an existing function such as map(int, parts)."),
        ],
        ["scope-closures", "decorators", "sorting-keys"],
        chain(
            ("def / lambda", "function object", "Create", "Defining a function creates an object with code, defaults and closure cells."),
            ("Pass it", "f as argument", "Hand over", "The function object is passed like any other value.", "f"),
            ("HOF calls f", "map / sorted", "Invoke", "The higher-order function calls f for each item it processes.", "item"),
            ("Results", "new values", "Collect", "Results are yielded lazily (map) or collected (sorted) for the caller.", "f(x)"),
        ),
    ),
    topic(
        "functools-tools", "functools: cache, partial, reduce, singledispatch", "functions", "intermediate", "FT",
        "Standard tools for caching, partial application, generic functions and well-behaved wrappers.",
        "functools is a toolbox for functions: a memory notebook (lru_cache), a pre-filled form (partial), a folding machine (reduce) and a receptionist who routes calls by visitor type (singledispatch).",
        "functools.lru_cache(maxsize=...) memoizes a function's results keyed by its arguments, which must be hashable; cache is an unbounded version, and cache_info()/cache_clear() help inspect and reset it. cached_property computes an attribute once per instance and stores it in the instance dict. partial(f, *args, **kwargs) freezes some arguments to create a simpler callable, often clearer than a lambda and picklable. reduce(f, iterable, initial) folds a sequence into one value, though sum, math.prod, any, all and loops are frequently clearer. singledispatch turns a function into a generic function that picks an implementation based on the type of the first argument, with register() adding overloads (singledispatchmethod does the same for methods). wraps copies __name__, __doc__ and __wrapped__ onto decorator wrappers, and total_ordering fills in comparison methods from __eq__ and one ordering method.",
        ["Memoizing expensive pure functions (recursive DP, config parsing).", "Pre-configuring callbacks with partial.", "Type-based dispatch for serializers or renderers.", "Lazy, computed-once attributes with cached_property."],
        [
            "lru_cache keys on arguments; they must be hashable.",
            "Caching methods with lru_cache keeps self alive; prefer cached_property or per-instance caches.",
            "partial objects expose .func, .args and .keywords.",
            "singledispatch dispatches on the first argument's type (MRO-aware).",
            "Always use @wraps in decorators.",
        ],
        [
            ex("lru_cache on recursion", "intermediate", "Exponential Fibonacci becomes linear.", "python", """
                from functools import lru_cache
                import time

                @lru_cache(maxsize=None)
                def fib(n):
                    return n if n < 2 else fib(n - 1) + fib(n - 2)

                t = time.perf_counter()
                print(fib(200))
                print(fib.cache_info(), f"{(time.perf_counter() - t) * 1000:.2f} ms")
                fib.cache_clear()
                print(fib.cache_info())
            """),
            ex("partial and reduce", "basic", "Freeze arguments; fold a sequence.", "python", """
                from functools import partial, reduce
                import operator

                parse_hex = partial(int, base=16)
                print(parse_hex("ff"), parse_hex.func, parse_hex.keywords)
                log_warn = partial(print, "[WARN]", sep=" ")
                log_warn("disk almost full")
                print(reduce(operator.mul, range(1, 6), 1))
                print(reduce(lambda acc, kv: {**acc, kv[0]: kv[1]}, [("a", 1), ("b", 2)], {}))
            """),
            ex("singledispatch and cached_property", "advanced", "Generic functions by type; computed-once attributes.", "python", """
                from functools import singledispatch, cached_property
                from datetime import date

                @singledispatch
                def to_json(obj):
                    raise TypeError(f"cannot serialize {type(obj).__name__}")

                @to_json.register
                def _(obj: date):
                    return obj.isoformat()

                @to_json.register(list)
                def _(obj):
                    return [to_json(x) for x in obj]

                @to_json.register(int)
                @to_json.register(str)
                def _(obj):
                    return obj

                print(to_json([1, "a", date(2026, 10, 17)]))

                class Report:
                    @cached_property
                    def total(self):
                        print("computing...")
                        return sum(range(1000))
                r = Report()
                print(r.total, r.total)
            """),
        ],
        ["@lru_cache(maxsize=128) · f.cache_info() · f.cache_clear()", "@functools.cache · @cached_property", "partial(f, a, key=v)", "reduce(op, xs, initial)", "@singledispatch · @f.register(type)", "@wraps(fn) · @total_ordering"],
        ["Caching functions with side effects or mutable return values (callers can mutate the cached object).", "Unhashable arguments (lists, dicts) raise TypeError with lru_cache.", "lru_cache on methods holds references to every self it has seen.", "reduce without an initial value fails on empty input."],
        [
            qa("intermediate", "How does lru_cache work?", "It wraps the function with a dict keyed by the call's arguments plus a doubly linked list tracking recency. Hits return the stored result; when maxsize is reached the least recently used entry is evicted. maxsize=None disables eviction."),
            qa("intermediate", "partial vs lambda?", "Both create a callable with some arguments fixed. partial is introspectable (.func/.args/.keywords), picklable when the function is, and binds values immediately, avoiding late-binding surprises."),
            qa("advanced", "What problem does singledispatch solve?", "It replaces chains of isinstance checks with a registry of implementations keyed by type of the first argument. Dispatch follows the MRO, so registering a base class covers subclasses, and new types can be supported without editing the original function."),
            qa("advanced", "Why is lru_cache on instance methods risky?", "self becomes part of the cache key, so the cache keeps every instance alive (memory leak) and the cache is shared across instances. Use cached_property, a per-instance dict, or a module-level cached function taking explicit keys."),
        ],
        ["decorators", "lambdas-higher-order"],
        chain(
            ("fib(30)", "call", "Call", "The wrapped function is called with arguments."),
            ("Make key", "args + kwargs", "Build key", "lru_cache builds a hashable key from the arguments.", "args"),
            ("Cache hit?", "dict lookup", "Look up", "If the key is present the result returns instantly and moves to most recent.", "key"),
            ("Compute", "miss", "Call original", "On a miss the original function runs and the result is stored.", "miss"),
            ("Evict LRU", "maxsize", "Bound size", "If the cache is full, the least recently used entry is dropped.", "store"),
        ),
    ),
    topic(
        "generators-advanced", "Generators: send, yield from & Pipelines", "functions", "advanced", "GA",
        "Two-way generators, delegation with yield from, close/throw, and lazy pipelines.",
        "A generator is a worker who pauses mid-task at every yield and waits. send() is handing the worker a note when they resume; yield from is the worker delegating a sub-task to an apprentice and relaying everything in between.",
        "A generator function returns a generator object whose frame is suspended at each yield. Beyond next(), generators support send(value), which resumes the generator and makes the paused yield expression evaluate to value; the generator must first be primed with next() or send(None). throw(exc) raises an exception at the paused yield, and close() raises GeneratorExit so finally blocks run. A return statement inside a generator sets StopIteration.value. yield from subgen delegates fully: it re-yields values, forwards send and throw calls, and evaluates to the subgenerator's return value, which makes it the clean way to compose generators and flatten recursive structures. Chaining generator functions builds lazy pipelines that process large streams in constant memory. These mechanics were the historical foundation of asyncio coroutines; modern code uses async/await for concurrency and keeps generators for data streams.",
        ["Streaming ETL pipelines over large files or sockets.", "Running averages or state machines driven with send().", "Recursive tree flattening with yield from.", "Cleanup of resources when a consumer stops early (close and finally)."],
        [
            "Prime a generator with next(g) before send(value).",
            "value = yield x: x goes out, value comes in.",
            "yield from forwards next/send/throw and returns the subgenerator's return value.",
            "close() triggers GeneratorExit; finally blocks run.",
            "Generators are single-use iterators.",
        ],
        [
            ex("A coroutine-style running average", "advanced", "send() pushes values in; the yield expression receives them.", "python", """
                def averager():
                    total, count, avg = 0.0, 0, None
                    while True:
                        value = yield avg
                        if value is None:
                            break
                        total += value
                        count += 1
                        avg = total / count
                    return count

                g = averager()
                next(g)                      # prime: run to the first yield
                for v in (10, 20, 60):
                    print("avg:", g.send(v))
                try:
                    g.send(None)
                except StopIteration as stop:
                    print("processed", stop.value, "values")
            """),
            ex("yield from delegation", "intermediate", "Flatten nested data and capture a subgenerator's return value.", "python", """
                def flatten(node):
                    for item in node:
                        if isinstance(item, list):
                            yield from flatten(item)
                        else:
                            yield item

                print(list(flatten([1, [2, [3, 4]], [], 5])))

                def child():
                    yield "a"
                    yield "b"
                    return "child done"

                def parent():
                    result = yield from child()
                    yield f"parent got: {result}"

                print(list(parent()))
            """),
            ex("Lazy pipeline with cleanup", "intermediate", "Stages pull one item at a time; close() runs finally.", "python", """
                import io

                LOG = io.StringIO("INFO ok\\nERROR disk\\nINFO ok\\nERROR net\\nERROR cpu\\n")

                def read_lines(f):
                    try:
                        for line in f:
                            yield line.rstrip()
                    finally:
                        print("reader closed")

                def only_errors(lines):
                    return (l for l in lines if l.startswith("ERROR"))

                reader = read_lines(LOG)
                errors = only_errors(reader)
                print(next(errors), next(errors))
                reader.close()
            """),
        ],
        ["value = yield out", "next(g) · g.send(v) · g.throw(Exc) · g.close()", "result = yield from sub()", "return x  # becomes StopIteration.value", "inspect.getgeneratorstate(g)"],
        ["send(non-None) to a just-started generator raises TypeError.", "Swallowing GeneratorExit and yielding again raises RuntimeError.", "Consuming a generator twice yields nothing the second time.", "A StopIteration raised inside a generator becomes RuntimeError (PEP 479)."],
        [
            qa("advanced", "What does generator.send() do?", "It resumes the generator and makes the paused yield expression evaluate to the sent value, then runs until the next yield and returns that yielded value. next(g) is equivalent to g.send(None)."),
            qa("advanced", "What does yield from add over a for loop with yield?", "Besides re-yielding values, it transparently forwards send(), throw() and close() to the subgenerator and evaluates to the subgenerator's return value. A plain loop only handles next()."),
            qa("intermediate", "How do you clean up resources in a generator?", "Wrap the body in try/finally or a with block. If the consumer stops early, calling close() (or garbage collection) raises GeneratorExit at the paused yield so the finally block runs."),
            qa("intermediate", "How does a generator return a value?", "A return value statement raises StopIteration(value); for loops ignore it, but yield from captures it as the expression's result and manual callers read it from StopIteration.value."),
        ],
        ["iterators-generators", "async-await"],
        chain(
            ("g = gen()", "created", "Create", "Calling a generator function only creates the object; no body code runs yet."),
            ("next(g)", "prime", "Prime", "Runs to the first yield and pauses there.", "None"),
            ("send(10)", "resume", "Send in", "The paused yield evaluates to 10 and the body continues.", "10"),
            ("yield avg", "pause", "Yield out", "The next yielded value is returned to the caller of send().", "avg"),
            ("return", "StopIteration", "Finish", "Returning raises StopIteration carrying the return value.", "value"),
        ),
    ),
    topic(
        "dunder-data-model", "Dunder Methods & the Data Model", "oop", "intermediate", "DM",
        "Make your objects work with len, +, ==, in, for and print by implementing protocols.",
        "Dunder methods are the sockets on the wall that Python's built-in appliances plug into: implement __len__ and len() works, implement __add__ and + works.",
        "Python's data model defines special 'dunder' (double underscore) methods that the interpreter calls for built-in syntax and functions. __repr__ gives an unambiguous developer representation (shown in the REPL and containers) and __str__ a friendly one for print. __eq__, __lt__ and friends implement comparisons, and returning NotImplemented lets Python try the reflected method on the other operand. Arithmetic uses __add__, __mul__ and so on, with __radd__ for reflected operations and __iadd__ for in-place +=. Container behavior comes from __len__, __getitem__, __contains__ and __iter__; callables implement __call__; context managers implement __enter__/__exit__. Special methods are looked up on the type, not the instance, so assigning them on an instance has no effect. Implementing the right protocols lets your class plug into sorted, sum, in, for loops and the standard library without inheritance.",
        ["Value types such as Vector, Money or Matrix with operators.", "Custom containers that work with len, in and for.", "Readable debugging via __repr__.", "Callable objects that keep state (__call__)."],
        [
            "Always implement __repr__; __str__ falls back to it.",
            "Return NotImplemented (not raise) for unsupported operand types.",
            "__radd__ enables sum() and 3 + obj.",
            "Special methods are looked up on the class.",
            "functools.total_ordering fills in missing comparisons.",
        ],
        [
            ex("A Vector value type", "intermediate", "repr, equality, arithmetic, reflected ops, abs and bool.", "python", """
                import math

                class Vector:
                    def __init__(self, x, y): self.x, self.y = x, y
                    def __repr__(self): return f"Vector({self.x}, {self.y})"
                    def __eq__(self, o):
                        return NotImplemented if not isinstance(o, Vector) else (self.x, self.y) == (o.x, o.y)
                    def __add__(self, o):
                        if isinstance(o, Vector): return Vector(self.x + o.x, self.y + o.y)
                        return NotImplemented
                    def __radd__(self, o):
                        return self if o == 0 else self.__add__(o)       # lets sum() start at 0
                    def __mul__(self, k): return Vector(self.x * k, self.y * k)
                    __rmul__ = __mul__
                    def __abs__(self): return math.hypot(self.x, self.y)
                    def __bool__(self): return bool(abs(self))
                    __hash__ = None

                v = Vector(3, 4)
                print(v + Vector(1, 1), 2 * v, abs(v), bool(Vector(0, 0)))
                print(sum([Vector(1, 2), Vector(3, 4)]), v == Vector(3, 4))
            """),
            ex("A container protocol", "intermediate", "len, indexing, slicing, in and iteration from a few methods.", "python", """
                class Playlist:
                    def __init__(self, *songs): self._songs = list(songs)
                    def __len__(self): return len(self._songs)
                    def __getitem__(self, i):
                        if isinstance(i, slice):
                            return Playlist(*self._songs[i])
                        return self._songs[i]
                    def __contains__(self, s): return s.lower() in (x.lower() for x in self._songs)
                    def __repr__(self): return f"Playlist{tuple(self._songs)}"

                p = Playlist("Intro", "Song A", "Song B", "Outro")
                print(len(p), p[0], p[1:3], "song a" in p)
                print([s for s in p])          # iteration falls back to __getitem__
                print(list(reversed(p)))
            """),
            ex("__call__ and lookup on the type", "advanced", "Callable objects; instance-level dunders are ignored.", "python", """
                class Counter:
                    def __init__(self): self.calls = 0
                    def __call__(self, *args):
                        self.calls += 1
                        return f"call #{self.calls} with {args}"

                c = Counter()
                print(c(1), c("x"), callable(c))
                c.__len__ = lambda: 99
                try:
                    len(c)
                except TypeError as e:
                    print("TypeError:", e)
            """),
        ],
        ["__repr__ · __str__ · __format__", "__eq__ · __lt__ · __hash__", "__add__ · __radd__ · __iadd__ → NotImplemented", "__len__ · __getitem__ · __contains__ · __iter__", "__call__ · __enter__ · __exit__ · __bool__"],
        ["Raising TypeError instead of returning NotImplemented breaks reflected operations.", "Defining __eq__ disables hashing unless you define __hash__.", "__iadd__ must return self (or a new object) or the name becomes None.", "Expensive __repr__ slows debugging and logging."],
        [
            qa("basic", "__repr__ vs __str__?", "__repr__ should be unambiguous, ideally valid code to recreate the object, and is used by the REPL, debuggers and containers. __str__ is for end-user display; if missing, str() uses __repr__."),
            qa("intermediate", "What is NotImplemented for?", "A binary dunder returns NotImplemented to say it can't handle the other operand; Python then tries the reflected method (e.g. other.__radd__) and only raises TypeError if both decline."),
            qa("intermediate", "How do you make sum() work for a custom class?", "sum starts with 0, so implement __radd__ that handles 0 (returning self) and delegates to __add__ otherwise, or pass a start value: sum(items, Vector(0, 0))."),
            qa("advanced", "Why doesn't setting obj.__len__ on an instance affect len(obj)?", "Implicit special method lookup bypasses the instance dict and goes straight to the type for speed and correctness. Only methods defined on the class (or set on the class) are used."),
        ],
        ["classes-dataclasses", "properties-descriptors"],
        chain(
            ("a + b", "syntax", "Operator", "The interpreter translates + into a protocol call."),
            ("a.__add__(b)", "type(a)", "Try left", "The left operand's type method is called first.", "b"),
            ("NotImplemented", "can't handle", "Decline", "If it returns NotImplemented, Python tries the other side.", "?"),
            ("b.__radd__(a)", "type(b)", "Try right", "The reflected method of the right operand gets a chance.", "a"),
            ("Result", "or TypeError", "Finish", "A value is returned, or TypeError if both sides decline.", "value"),
        ),
    ),
    topic(
        "properties-descriptors", "Properties & Descriptors", "oop", "advanced", "PD",
        "Managed attributes: @property for one class, descriptors for reusable attribute logic.",
        "A property is a receptionist at the door of an attribute: reads and writes pass through them so they can check IDs. A descriptor is a receptionist agency you can hire for any number of doors in any class.",
        "@property turns a method into a computed attribute with optional setter and deleter, letting you start with plain attributes and add validation later without changing callers. Under the hood, property is a descriptor: any class attribute that defines __get__, and optionally __set__ or __delete__, intercepts attribute access on instances. Data descriptors (with __set__ or __delete__) take priority over the instance __dict__, while non-data descriptors (only __get__, like functions) can be shadowed by instance attributes. That is exactly how methods work: functions are non-data descriptors whose __get__ returns a bound method. __set_name__ (3.6+) tells a descriptor the attribute name it was assigned to, making reusable validators simple. Descriptors power property, classmethod, staticmethod, cached_property, __slots__ and ORM fields. For attribute access fallback there are also __getattr__ (called only when normal lookup fails) and __getattribute__ (called for every access).",
        ["Validation of fields (positive numbers, non-empty strings).", "Computed or derived attributes such as area or full_name.", "Reusable typed fields in ORMs and config objects.", "Lazy loading and deprecation shims for renamed attributes."],
        [
            "@property + @x.setter keeps attribute syntax with validation.",
            "Descriptors implement __get__/__set__/__delete__ on a class attribute.",
            "Data descriptors beat instance __dict__; non-data descriptors lose to it.",
            "__set_name__ receives the owner class and attribute name.",
            "__getattr__ is a fallback; __getattribute__ intercepts everything.",
        ],
        [
            ex("property with validation", "basic", "Callers keep using attribute syntax.", "python", """
                class Temperature:
                    def __init__(self, celsius):
                        self.celsius = celsius          # goes through the setter

                    @property
                    def celsius(self):
                        return self._c

                    @celsius.setter
                    def celsius(self, value):
                        if value < -273.15:
                            raise ValueError("below absolute zero")
                        self._c = value

                    @property
                    def fahrenheit(self):
                        return self._c * 9 / 5 + 32

                t = Temperature(25)
                print(t.celsius, t.fahrenheit)
                t.celsius = 30
                print(t.fahrenheit)
                try:
                    t.celsius = -300
                except ValueError as e:
                    print("ValueError:", e)
            """),
            ex("A reusable validating descriptor", "advanced", "__set_name__ learns the field name; one class serves many fields.", "python", """
                class Positive:
                    def __set_name__(self, owner, name):
                        self.name = "_" + name
                    def __get__(self, obj, objtype=None):
                        if obj is None:
                            return self
                        return getattr(obj, self.name)
                    def __set__(self, obj, value):
                        if not isinstance(value, (int, float)) or value <= 0:
                            raise ValueError(f"{self.name[1:]} must be positive, got {value!r}")
                        setattr(obj, self.name, value)

                class Order:
                    qty = Positive()
                    price = Positive()
                    def __init__(self, qty, price):
                        self.qty, self.price = qty, price

                o = Order(3, 9.5)
                print(o.qty * o.price, Order.qty)
                for bad in ({"qty": 0, "price": 1}, {"qty": 1, "price": "x"}):
                    try:
                        Order(**bad)
                    except ValueError as e:
                        print(e)
            """),
            ex("Methods are descriptors", "advanced", "Function.__get__ produces bound methods; instance dict shadows non-data descriptors.", "python", """
                class Greeter:
                    def hello(self):
                        return f"hello from {type(self).__name__}"

                g = Greeter()
                f = Greeter.__dict__["hello"]
                bound = f.__get__(g, Greeter)
                print(bound(), bound.__self__ is g)
                g.hello = lambda: "shadowed by instance attribute"
                print(g.hello())

                class Lazy:
                    def __getattr__(self, name):
                        return f"<missing {name}>"
                print(Lazy().anything)
            """),
        ],
        ["@property · @x.setter · @x.deleter", "__get__(self, obj, objtype) · __set__(self, obj, value)", "__set_name__(self, owner, name)", "__getattr__ (fallback) · __getattribute__ (always)", "vars(obj) · type(obj).__dict__"],
        ["Storing descriptor values on the descriptor itself shares them across all instances.", "A property and an instance attribute with the same name cause infinite recursion in the setter.", "__getattribute__ overrides easily recurse; call object.__getattribute__.", "Heavy work in properties surprises callers who expect cheap attribute access."],
        [
            qa("intermediate", "Why use @property instead of getter/setter methods?", "It keeps the public API as plain attributes while allowing validation or computation later, so you can start simple and add logic without breaking callers."),
            qa("advanced", "What is a descriptor?", "An object defining __get__, __set__ or __delete__ that is stored as a class attribute; attribute access on instances is routed through those methods. property, classmethod, staticmethod and functions (bound methods) are all descriptors."),
            qa("advanced", "Data vs non-data descriptor precedence?", "Lookup order is: data descriptors on the type, then the instance __dict__, then non-data descriptors and plain class attributes. That's why you can override a method per instance but not a property."),
            qa("intermediate", "__getattr__ vs __getattribute__?", "__getattribute__ is called on every attribute access; __getattr__ is called only when normal lookup raises AttributeError. Prefer __getattr__ for proxies and defaults because it is much harder to break."),
        ],
        ["classes-dataclasses", "dunder-data-model"],
        chain(
            ("obj.attr", "lookup", "Access", "Attribute access calls type(obj).__getattribute__."),
            ("Data desc?", "type MRO", "Check type", "If the class defines a data descriptor for the name, its __get__ wins.", "name"),
            ("Instance dict", "obj.__dict__", "Check instance", "Otherwise the instance's own __dict__ is consulted.", "name"),
            ("Non-data desc", "methods etc.", "Check class", "Then non-data descriptors (functions become bound methods) or plain class attributes.", "name"),
            ("__getattr__", "fallback", "Fallback", "If all fail, __getattr__ is called if defined; else AttributeError.", "miss"),
        ),
    ),
    topic(
        "inheritance-mro", "Inheritance, MRO & super()", "oop", "intermediate", "IM",
        "How Python resolves methods across multiple bases and why super() means 'next in line'.",
        "The MRO is a queue at a help desk: Python asks each class in order until one can answer. super() doesn't mean 'my parent', it means 'the next person in this specific queue'.",
        "A class can inherit from one or more base classes, and attribute lookup follows the Method Resolution Order (MRO), visible in Cls.__mro__ or Cls.mro(). Python computes it with C3 linearization, which preserves each class's local base order and guarantees a class appears before its bases, rejecting inconsistent hierarchies with TypeError. super() returns a proxy that continues the lookup from the class after the current one in the MRO of the instance's type, not necessarily the textual parent. This enables cooperative multiple inheritance: if every class in a diamond calls super().__init__(**kwargs), each __init__ runs exactly once. Mixins are small classes that add behavior (logging, serialization) and rely on cooperative super(). isinstance and issubclass follow the hierarchy, and abstract base classes can also register virtual subclasses. Prefer composition when the relationship is 'has-a', keep hierarchies shallow, and use inheritance for real 'is-a' relationships and framework extension points.",
        ["Framework extension points (views, handlers, test cases).", "Mixins like JSONMixin or ReprMixin.", "Diamond hierarchies with cooperative __init__.", "Overriding a method while reusing the base behavior with super()."],
        [
            "Lookup order is Cls.__mro__, computed by C3 linearization.",
            "super() follows the MRO of type(self), not the literal parent.",
            "Cooperative classes accept **kwargs and always call super().",
            "Each class appears once in the MRO, so diamonds run each base once.",
            "Favor composition over deep inheritance trees.",
        ],
        [
            ex("Diamond and the MRO", "intermediate", "super() chains through every class exactly once.", "python", """
                class Base:
                    def greet(self): return ["Base"]

                class Left(Base):
                    def greet(self): return ["Left"] + super().greet()

                class Right(Base):
                    def greet(self): return ["Right"] + super().greet()

                class Child(Left, Right):
                    def greet(self): return ["Child"] + super().greet()

                print([c.__name__ for c in Child.__mro__])
                print(Child().greet())
                print([c.__name__ for c in Left.__mro__])
            """),
            ex("Cooperative __init__ with mixins", "advanced", "Each class consumes its own kwargs and passes the rest on.", "python", """
                class Named:
                    def __init__(self, *, name, **kw):
                        self.name = name
                        super().__init__(**kw)

                class Timestamped:
                    def __init__(self, *, created="2026-10-17", **kw):
                        self.created = created
                        super().__init__(**kw)

                class ReprMixin:
                    def __repr__(self):
                        fields = ", ".join(f"{k}={v!r}" for k, v in vars(self).items())
                        return f"{type(self).__name__}({fields})"

                class Document(ReprMixin, Named, Timestamped):
                    def __init__(self, *, pages, **kw):
                        self.pages = pages
                        super().__init__(**kw)

                print(Document(name="spec", pages=12))
                print([c.__name__ for c in Document.__mro__])
            """),
            ex("Inconsistent hierarchy", "advanced", "C3 refuses orders that contradict the base lists.", "python", """
                class A: pass
                class B(A): pass
                try:
                    class C(A, B): pass
                except TypeError as e:
                    print("TypeError:", e)

                class D(B, A): pass
                print([c.__name__ for c in D.__mro__], issubclass(D, A), isinstance(D(), B))
            """),
        ],
        ["Cls.__mro__ · Cls.mro()", "super().method(*args, **kwargs)", "class C(Mixin, Base): ...", "isinstance(obj, (A, B)) · issubclass(C, A)", "def __init__(self, *, x, **kw): super().__init__(**kw)"],
        ["Calling Base.__init__(self) directly in a diamond runs some bases twice and skips others.", "Not forwarding **kwargs breaks cooperative chains.", "Mixin order matters: put mixins before the base class.", "super() with no args only works inside a method defined in a class body."],
        [
            qa("intermediate", "What is the MRO?", "The Method Resolution Order is the linear list of classes Python searches for attributes, available as Cls.__mro__. It is computed with C3 linearization so subclasses come before bases and base order is preserved."),
            qa("advanced", "What does super() actually do?", "It returns a proxy that looks up attributes starting after the current class in type(self).__mro__. In multiple inheritance this may be a sibling class, not the parent, which is what makes cooperative inheritance work."),
            qa("advanced", "How do you design cooperative multiple inheritance?", "Every class in the chain calls super() exactly once, accepts and forwards **kwargs, consumes its own keyword arguments, and the chain ends at a root (object) that accepts no extras."),
            qa("intermediate", "When prefer composition over inheritance?", "When the relationship is 'has-a' or you only need some behavior of another class. Composition keeps coupling low, avoids fragile base class issues and makes testing with substitutes easier."),
        ],
        ["classes-dataclasses", "abstract-base-classes"],
        chain(
            ("Child()", "instance", "Call", "child.greet() starts lookup on type(child)."),
            ("Child", "MRO[0]", "Own class", "Child.greet runs and calls super().greet().", "greet"),
            ("Left", "MRO[1]", "Next in MRO", "super() moves to Left, which also calls super().", "super"),
            ("Right", "MRO[2]", "Sibling", "Left's super() is Right, not Base, because of Child's MRO.", "super"),
            ("Base", "MRO[3]", "Root", "Base runs once at the end; then object.", "super"),
        ),
    ),
    topic(
        "abstract-base-classes", "Abstract Base Classes (abc)", "oop", "intermediate", "AB",
        "Declare required methods, check interfaces, and use collections.abc for free mixin methods.",
        "An ABC is a job description: it lists the duties every hire must perform, and the agency refuses to place anyone who left a duty blank.",
        "The abc module lets you define abstract base classes by inheriting from ABC (or using ABCMeta) and marking methods with @abstractmethod. A class with unimplemented abstract methods cannot be instantiated, so missing implementations fail early with a clear TypeError instead of at the first call. Abstract methods can still have a body that subclasses call through super(), and you can combine @abstractmethod with @property or @classmethod. ABCs support virtual subclasses through register() and structural checks through __subclasshook__, which is how isinstance(x, collections.abc.Iterable) works for any object with __iter__. collections.abc provides interfaces like Sequence, Mapping, MutableMapping, Iterable and Hashable; inheriting from them and implementing a few core methods gives you the rest as mixin methods for free. For static duck typing without inheritance, typing.Protocol is often a lighter alternative.",
        ["Plugin interfaces that every implementation must satisfy.", "Custom containers via collections.abc.Mapping or Sequence.", "Runtime checks like isinstance(obj, Iterable).", "Template method pattern with abstract hooks."],
        [
            "Instantiation fails until every abstract method is implemented.",
            "collections.abc mixins provide methods from a few required ones.",
            "register() creates virtual subclasses without inheritance.",
            "Abstract methods can have default implementations.",
            "Protocols offer structural typing for type checkers.",
        ],
        [
            ex("Enforcing an interface", "basic", "Missing implementations fail at construction time.", "python", """
                from abc import ABC, abstractmethod

                class Storage(ABC):
                    @abstractmethod
                    def save(self, key, data): ...

                    @abstractmethod
                    def load(self, key): ...

                    def exists(self, key):                       # concrete helper
                        try:
                            self.load(key); return True
                        except KeyError:
                            return False

                class MemoryStorage(Storage):
                    def __init__(self): self._d = {}
                    def save(self, key, data): self._d[key] = data
                    def load(self, key): return self._d[key]

                class Broken(Storage):
                    def save(self, key, data): pass

                s = MemoryStorage(); s.save("a", 1)
                print(s.load("a"), s.exists("a"), s.exists("b"))
                try:
                    Broken()
                except TypeError as e:
                    print("TypeError:", e)
            """),
            ex("Free methods from collections.abc", "intermediate", "Implement 3 methods of Mapping, get keys/items/get/== for free.", "python", """
                from collections.abc import Mapping

                class CaseInsensitive(Mapping):
                    def __init__(self, data): self._d = {k.lower(): v for k, v in data.items()}
                    def __getitem__(self, k): return self._d[k.lower()]
                    def __iter__(self): return iter(self._d)
                    def __len__(self): return len(self._d)

                h = CaseInsensitive({"Content-Type": "json", "X-Id": "7"})
                print(h["content-type"], h.get("X-ID"), "x-id" in h, list(h.items()))
                print(h == {"content-type": "json", "x-id": "7"})
            """),
            ex("Virtual subclasses and structural checks", "advanced", "isinstance works without inheritance.", "python", """
                from abc import ABC
                from collections.abc import Iterable, Sized, Hashable

                class Countdown:
                    def __init__(self, n): self.n = n
                    def __iter__(self): return iter(range(self.n, 0, -1))

                print(isinstance(Countdown(3), Iterable), isinstance(Countdown(3), Sized))
                print(isinstance([], Hashable), isinstance((), Hashable))

                class Serializer(ABC): pass
                Serializer.register(dict)
                print(isinstance({}, Serializer), issubclass(dict, Serializer))
            """),
        ],
        ["class Base(ABC): @abstractmethod def run(self): ...", "Base.register(OtherClass)", "Base.__abstractmethods__", "from collections.abc import Mapping, Sequence, Iterable", "@property @abstractmethod def name(self): ..."],
        ["Forgetting to inherit from ABC means @abstractmethod is not enforced.", "register() does not check that methods actually exist.", "Abstract checks happen at instantiation, not at class definition.", "Overusing ABCs where duck typing or Protocol suffices."],
        [
            qa("intermediate", "What does @abstractmethod do?", "In a class whose metaclass is ABCMeta, it records the method in __abstractmethods__; any class that still has abstract methods cannot be instantiated and raises TypeError listing them."),
            qa("intermediate", "Why inherit from collections.abc.Mapping instead of dict?", "Mapping gives a correct read-only mapping from __getitem__, __iter__ and __len__, with get, keys, items, values, __contains__ and __eq__ built on them. Subclassing dict is tricky because many dict methods bypass your overridden __getitem__."),
            qa("advanced", "What is a virtual subclass?", "A class registered with ABC.register() so isinstance/issubclass return True without real inheritance. The ABC does not verify methods; __subclasshook__ can implement structural checks instead, as Iterable does."),
            qa("advanced", "ABC vs typing.Protocol?", "ABCs are nominal and enforced at runtime (instantiation checks, isinstance). Protocols are structural and mainly checked statically by type checkers; any class with matching methods satisfies them without inheritance."),
        ],
        ["inheritance-mro", "classes-dataclasses"],
        chain(
            ("Base(ABC)", "ABCMeta", "Define", "ABCMeta collects methods marked with @abstractmethod."),
            ("Subclass", "implements", "Inherit", "The subclass overrides some or all abstract methods.", "methods"),
            ("Recompute", "abstract set", "Track", "ABCMeta recomputes which methods are still abstract.", "set"),
            ("Instantiate", "Sub()", "Check", "object.__new__ refuses if the set is non-empty: TypeError.", "check"),
        ),
    ),
    topic(
        "metaclasses", "Metaclasses & __init_subclass__", "oop", "advanced", "MC",
        "Classes are objects too: customize their creation with __init_subclass__, decorators or metaclasses.",
        "If a class is a cookie cutter, a metaclass is the factory that makes cookie cutters. Most bakeries never need a custom factory; a sticker on each new cutter (__init_subclass__) is usually enough.",
        "Every class is an instance of a metaclass, by default type, so type(int) is type. When Python executes a class statement it collects the body into a namespace (from __prepare__), then calls metaclass(name, bases, namespace) which runs __new__ and __init__ to create the class object. A custom metaclass can validate or modify classes, auto-register them, or inject methods, and it is inherited by all subclasses. Since Python 3.6, __init_subclass__ on a base class handles most of these needs, such as plugin registration or checking required attributes, with far less complexity, and __set_name__ lets descriptors learn their names. Class decorators are another lightweight option to post-process a single class. Real-world metaclass users include ABCMeta, Enum's EnumType and ORMs like Django models. Metaclass conflicts arise when combining bases with unrelated metaclasses. The rule of thumb is to reach for a metaclass only when simpler hooks cannot do the job.",
        ["Plugin registries populated automatically on subclassing.", "Validating that subclasses define required attributes.", "ORM or serialization frameworks building fields from annotations.", "Understanding how Enum, ABC and dataclasses work internally."],
        [
            "Classes are instances of type (or a custom metaclass).",
            "type(name, bases, ns) creates a class dynamically.",
            "__init_subclass__ runs on the parent when a subclass is created.",
            "Metaclasses are inherited and can conflict.",
            "Prefer decorators/__init_subclass__ before metaclasses.",
        ],
        [
            ex("Classes are objects", "intermediate", "type creates classes; type is its own type.", "python", """
                print(type(42), type(int), type(type))
                Point = type("Point", (), {"x": 0, "show": lambda self: f"Point(x={self.x})"})
                p = Point()
                print(p.show(), Point.__name__, isinstance(Point, type))
            """),
            ex("Plugin registry with __init_subclass__", "intermediate", "No metaclass needed for registration and validation.", "python", """
                class Exporter:
                    registry = {}

                    def __init_subclass__(cls, *, fmt, **kw):
                        super().__init_subclass__(**kw)
                        if not hasattr(cls, "export"):
                            raise TypeError(f"{cls.__name__} must define export()")
                        Exporter.registry[fmt] = cls

                class CsvExporter(Exporter, fmt="csv"):
                    def export(self, rows): return "\\n".join(",".join(map(str, r)) for r in rows)

                class JsonExporter(Exporter, fmt="json"):
                    def export(self, rows):
                        import json
                        return json.dumps(rows)

                print(Exporter.registry)
                print(Exporter.registry["csv"]().export([[1, 2], [3, 4]]))
                try:
                    class Bad(Exporter, fmt="xml"): pass
                except TypeError as e:
                    print("TypeError:", e)
            """),
            ex("A metaclass that enforces naming", "advanced", "Metaclass __new__ sees the namespace before the class exists.", "python", """
                class NoCamelMethods(type):
                    def __new__(mcls, name, bases, ns):
                        bad = [k for k, v in ns.items() if callable(v) and any(c.isupper() for c in k)]
                        if bad:
                            raise TypeError(f"{name}: use snake_case for {bad}")
                        cls = super().__new__(mcls, name, bases, ns)
                        cls.created_by = mcls.__name__
                        return cls

                class Service(metaclass=NoCamelMethods):
                    def fetch_data(self): return "ok"

                print(Service().fetch_data(), Service.created_by, type(Service).__name__)
                try:
                    class Legacy(Service):
                        def fetchData(self): pass
                except TypeError as e:
                    print("TypeError:", e)
            """),
        ],
        ["type(obj) · type(name, bases, ns)", "class Meta(type): def __new__(mcls, name, bases, ns): ...", "class C(metaclass=Meta): ...", "def __init_subclass__(cls, **kw): super().__init_subclass__(**kw)", "__prepare__ · __set_name__ · class decorators"],
        ["Metaclass conflict TypeError when combining bases with different metaclasses.", "Metaclasses make code hard to read and debug; document why you need one.", "Forgetting super().__init_subclass__(**kw) breaks cooperative hooks.", "Metaclass __call__ overrides change how every instance is created."],
        [
            qa("advanced", "What is a metaclass?", "The class of a class: it controls how class objects are created and behave. type is the default metaclass; a custom one subclasses type and overrides __new__, __init__, __prepare__ or __call__."),
            qa("advanced", "What happens when Python executes a class statement?", "It resolves the metaclass, calls __prepare__ to get a namespace, executes the body into it, then calls metaclass(name, bases, namespace). That runs __new__/__init__, triggers __set_name__ on attributes and __init_subclass__ on the parent."),
            qa("intermediate", "When use __init_subclass__ instead of a metaclass?", "For subclass registration, validation and configuration via class keyword arguments. It is simpler, composes with other hooks, and avoids metaclass conflicts."),
            qa("intermediate", "Give real-world examples of metaclasses.", "ABCMeta enforces abstract methods, EnumType makes Enum members singletons and iterable, and ORMs like Django and SQLAlchemy declarative use metaclasses to turn class attributes into columns."),
        ],
        ["classes-dataclasses", "abstract-base-classes", "enums"],
        chain(
            ("class C(B):", "statement", "Start", "Python sees a class statement and finds the metaclass (from bases or metaclass=)."),
            ("__prepare__", "namespace", "Namespace", "The metaclass provides the dict the body executes in.", "ns"),
            ("Run body", "defs, attrs", "Execute", "Methods and attributes are stored into the namespace.", "ns"),
            ("Meta.__new__", "create class", "Create", "metaclass(name, bases, ns) builds the class object.", "ns"),
            ("Hooks", "__init_subclass__", "Post-process", "__set_name__ and the parent's __init_subclass__ run on the new class.", "C"),
        ),
    ),
    topic(
        "enums", "Enums", "oop", "basic", "EN",
        "Named constants with identity, iteration, flags and string/int variants.",
        "An Enum is a fixed menu: you can only order what is printed on it, each item has a name and a code, and the kitchen never confuses 'Large' with the number 3.",
        "enum.Enum defines a set of named, unique constants. Members are singletons, so you compare them with is or ==, and they have .name and .value attributes. Enums are iterable in definition order, support lookup by value (Color(1)) and by name (Color['RED']), and reject unknown values with ValueError. auto() generates values automatically. IntEnum and StrEnum (3.11+) members also behave like ints or strings, which helps interoperability with JSON or databases but weakens type safety. Flag and IntFlag support bitwise combinations such as Permission.READ | Permission.WRITE. Duplicate values create aliases unless the class is decorated with @unique. Enums can have methods and properties, and they work well with match statements via dotted names (case Status.ACTIVE). Using enums instead of magic strings catches typos early and documents the allowed values.",
        ["Order or job states (PENDING, RUNNING, DONE).", "Permission bitmasks with Flag.", "API values that must serialize as strings (StrEnum).", "Exhaustive dispatch in match statements."],
        [
            "Members are singletons with .name and .value.",
            "Lookup: Color(1) by value, Color['RED'] by name.",
            "@unique forbids aliases; auto() picks values.",
            "StrEnum/IntEnum mix in str/int behavior.",
            "Flag supports |, & and membership.",
        ],
        [
            ex("Basic Enum", "basic", "Names, values, iteration and lookup.", "python", """
                from enum import Enum, auto

                class Status(Enum):
                    PENDING = auto()
                    RUNNING = auto()
                    DONE = auto()

                    @property
                    def is_final(self):
                        return self is Status.DONE

                print(list(Status), Status.RUNNING.name, Status.RUNNING.value)
                print(Status(3), Status["PENDING"], Status.DONE.is_final)
                try:
                    Status(99)
                except ValueError as e:
                    print("ValueError:", e)
            """),
            ex("StrEnum and match", "intermediate", "String-compatible members and dotted case patterns.", "python", """
                from enum import StrEnum
                import json

                class Method(StrEnum):
                    GET = "GET"
                    POST = "POST"

                def handle(m: Method):
                    match m:
                        case Method.GET:
                            return "read"
                        case Method.POST:
                            return "write"

                print(handle(Method("POST")), Method.GET == "GET", json.dumps({"m": Method.GET}))
                print(f"{Method.POST}", Method.POST.upper())
            """),
            ex("Flags and unique", "intermediate", "Combine permissions with bitwise operators; catch accidental aliases.", "python", """
                from enum import Flag, Enum, auto, unique

                class Perm(Flag):
                    READ = auto()
                    WRITE = auto()
                    EXEC = auto()
                    RW = READ | WRITE

                p = Perm.READ | Perm.WRITE
                print(p, p is Perm.RW, Perm.WRITE in p, Perm.EXEC in p, list(p))

                try:
                    @unique
                    class Size(Enum):
                        SMALL = 1
                        LITTLE = 1
                except ValueError as e:
                    print("ValueError:", e)
            """),
        ],
        ["class Color(Enum): RED = auto()", "Color(1) · Color['RED'] · Color.RED.name / .value", "StrEnum · IntEnum · Flag · IntFlag", "@unique", "case Color.RED:"],
        ["Comparing a plain Enum member to its raw value is False (Status.DONE == 3).", "IntEnum members compare equal to ints, which can hide bugs.", "Duplicate values silently create aliases without @unique.", "Pickling/JSON of plain Enums needs .value or a custom encoder."],
        [
            qa("basic", "Why use Enum instead of string constants?", "Enums restrict values to a known set, catch typos at attribute access, are iterable and self-documenting, and type checkers can verify exhaustiveness."),
            qa("intermediate", "Enum vs IntEnum vs StrEnum?", "Enum members are only equal to themselves. IntEnum/StrEnum members are also ints/strings, so they compare equal to raw values and serialize naturally, at the cost of looser type safety."),
            qa("intermediate", "What is a Flag enum?", "A Flag's members are bit values that can be combined with |, tested with in or &, and iterated; IntFlag additionally behaves like an int. Useful for permission sets and option masks."),
            qa("advanced", "How are enum members singletons?", "The EnumType metaclass creates each member once when the class body executes and stores it; Color(1) and Color['RED'] look up existing members instead of creating new objects, so identity comparison is safe."),
        ],
        ["metaclasses", "control-flow-match"],
        chain(
            ("class Enum", "body", "Define", "Each class attribute in the body becomes a candidate member."),
            ("EnumType", "metaclass", "Build members", "The metaclass turns each attribute into a singleton member.", "attrs"),
            ("Lookup", "Color(1)", "Find", "Value or name lookups return the existing member, never a new one.", "value"),
            ("Compare", "is / ==", "Use", "Members compare by identity; plain Enum never equals its raw value.", "member"),
        ),
    ),
    topic(
        "slots-memory", "__slots__ & Object Memory", "oop", "advanced", "SL",
        "Drop the per-instance __dict__ to save memory and block accidental attributes.",
        "A normal object carries a backpack (__dict__) it can stuff anything into. A slotted object has a tool belt with a fixed set of labeled pouches: lighter, but no room for surprises.",
        "By default each instance stores its attributes in a per-instance __dict__, which is flexible but costs memory (CPython has key-sharing dicts, yet the dict still adds overhead). Declaring __slots__ = ('x', 'y') on a class replaces the dict with fixed slot descriptors, making instances smaller and attribute access slightly faster. Slotted instances reject attributes not listed in __slots__ with AttributeError, which also catches typos. Slots are inherited only if every class in the hierarchy declares them; a subclass without __slots__ regains __dict__. You must add '__weakref__' to slots if instances need weak references, and class attributes with the same name as a slot conflict. dataclasses support @dataclass(slots=True) since 3.10. Slots matter when you create millions of small objects; for a few instances the flexibility of __dict__ is usually worth more. sys.getsizeof and tracemalloc help measure the difference.",
        ["Millions of small records (points, graph nodes, events).", "Preventing typo-created attributes on value objects.", "Memory-constrained services and caches.", "Dataclasses with slots=True for lean records."],
        [
            "__slots__ removes the instance __dict__ (and __weakref__ unless listed).",
            "Unknown attributes raise AttributeError.",
            "Every class in the hierarchy must define __slots__ to keep the savings.",
            "@dataclass(slots=True) generates slots for you.",
            "Measure with tracemalloc before optimizing.",
        ],
        [
            ex("Memory comparison", "advanced", "Measure allocation for many instances with tracemalloc.", "python", """
                import tracemalloc

                class Plain:
                    def __init__(self, x, y): self.x, self.y = x, y

                class Slotted:
                    __slots__ = ("x", "y")
                    def __init__(self, x, y): self.x, self.y = x, y

                def measure(cls, n=50_000):
                    tracemalloc.start()
                    objs = [cls(i, i) for i in range(n)]
                    size, _ = tracemalloc.get_traced_memory()
                    tracemalloc.stop()
                    return size // n

                print("plain   bytes/obj:", measure(Plain))
                print("slotted bytes/obj:", measure(Slotted))
                print(hasattr(Plain(1, 2), "__dict__"), hasattr(Slotted(1, 2), "__dict__"))
            """),
            ex("Slots block unknown attributes", "intermediate", "Typos become errors instead of silent new attributes.", "python", """
                class Point:
                    __slots__ = ("x", "y")
                    def __init__(self, x, y): self.x, self.y = x, y

                p = Point(1, 2)
                p.x = 10
                try:
                    p.z = 3
                except AttributeError as e:
                    print("AttributeError:", e)

                class Point3(Point):           # no __slots__: gets a __dict__ again
                    pass
                q = Point3(1, 2); q.z = 3
                print(q.z, hasattr(q, "__dict__"))
            """),
            ex("dataclass(slots=True)", "intermediate", "Lean records with generated slots.", "python", """
                from dataclasses import dataclass
                import weakref

                @dataclass(slots=True, frozen=True)
                class Event:
                    kind: str
                    ts: float

                e = Event("click", 1.5)
                print(e, Event.__slots__)
                try:
                    weakref.ref(e)
                except TypeError as err:
                    print("TypeError:", err)

                @dataclass(slots=True, weakref_slot=True)
                class Node:
                    name: str
                print(weakref.ref(Node("a"))() is None)
            """),
        ],
        ["__slots__ = ('x', 'y')", "__slots__ = ('x', '__weakref__')", "@dataclass(slots=True)", "sys.getsizeof(obj) · tracemalloc.start()", "hasattr(obj, '__dict__')"],
        ["A subclass without __slots__ silently reintroduces __dict__.", "Slots break weakrefs unless '__weakref__' is listed.", "Setting a class attribute default with the same name as a slot raises ValueError.", "Multiple inheritance from two classes with non-empty slots causes layout conflicts."],
        [
            qa("intermediate", "What does __slots__ do?", "It declares a fixed set of attribute names stored in compact slot descriptors instead of a per-instance __dict__, reducing memory and preventing creation of other attributes."),
            qa("advanced", "When are slots worth it?", "When you have very many instances of a small class (hundreds of thousands or more) or want to forbid dynamic attributes. For a handful of objects the memory saving is negligible and you lose flexibility."),
            qa("advanced", "What happens with slots in inheritance?", "Slots of each class are added to the layout; if any class in the chain lacks __slots__, instances get a __dict__ again. Subclasses should declare only their new names, and two bases with non-empty slots can't be combined."),
            qa("intermediate", "How are slots implemented?", "For each name the class gets a member descriptor that reads and writes a fixed offset in the instance's memory layout, which is a data descriptor on the type, similar in spirit to a property."),
        ],
        ["classes-dataclasses", "properties-descriptors"],
        chain(
            ("class Point", "__slots__", "Declare", "The class lists its attribute names in __slots__."),
            ("Descriptors", "x, y", "Create slots", "type creates a member descriptor per name, at fixed offsets.", "names"),
            ("Instance", "no __dict__", "Allocate", "Each instance holds just the slot pointers: smaller objects.", "layout"),
            ("p.z = 3", "AttributeError", "Guard", "Names outside __slots__ have nowhere to go and are rejected.", "z"),
        ),
    ),
]

TOPICS += [
    topic(
        "type-hints", "Type Hints Basics", "typing", "basic", "TH",
        "Annotations for humans and type checkers: built-in generics, Optional, unions and aliases.",
        "Type hints are labels on moving boxes: the movers (Python) don't read them, but the inspector (mypy, pyright, your IDE) checks every box against its label before the truck leaves.",
        "Type hints annotate parameters, return values and variables, e.g. def total(prices: list[float]) -> float. Python does not enforce them at runtime; they are stored in __annotations__ and used by static checkers like mypy and pyright, IDEs for completion, and libraries such as dataclasses, pydantic and FastAPI. Since 3.9 you can use built-in generics like list[int] and dict[str, int], and since 3.10 the union syntax int | None replaces Optional[int]. Use collections.abc types (Iterable, Sequence, Mapping, Callable) for parameters to accept many concrete types, and concrete types for return values. Literal restricts values to specific constants, TypedDict types dict-shaped data, Final marks constants, and type aliases (the type statement in 3.12) name complex types. Any opts out of checking and should be rare. Gradual typing means you can add hints incrementally, starting with public APIs.",
        ["Catching None-related bugs before production.", "Better IDE autocompletion and refactoring.", "Self-documenting public APIs.", "Runtime validation in pydantic/FastAPI models."],
        [
            "Hints are not enforced at runtime by Python itself.",
            "Use X | None for optional values (3.10+).",
            "Accept abstract types (Iterable), return concrete ones (list).",
            "Literal, TypedDict and Final express precise contracts.",
            "Run mypy/pyright in CI to get the value.",
        ],
        [
            ex("Annotations are metadata", "basic", "Python stores but does not enforce them.", "python", """
                def greet(name: str, times: int = 1) -> str:
                    return " ".join([f"hi {name}"] * times)

                print(greet("ada", 2))
                print(greet.__annotations__)
                print(greet(42))                       # runs fine; a type checker would flag it
            """),
            ex("Modern hint syntax", "intermediate", "Built-in generics, unions, Literal, TypedDict and aliases.", "python", """
                from collections.abc import Iterable, Callable
                from typing import Literal, TypedDict, Final, get_type_hints

                MAX_RETRIES: Final = 3
                Mode = Literal["r", "w"]

                class User(TypedDict):
                    id: int
                    email: str
                    nickname: str | None

                def average(xs: Iterable[float]) -> float | None:
                    xs = list(xs)
                    return sum(xs) / len(xs) if xs else None

                def apply(f: Callable[[int], int], values: list[int]) -> list[int]:
                    return [f(v) for v in values]

                u: User = {"id": 1, "email": "a@example.com", "nickname": None}
                print(average([1, 2, 3]), average([]), apply(lambda v: v * 2, [1, 2]))
                print(get_type_hints(User), u["email"])
            """),
            ex("Narrowing with checks", "intermediate", "Checkers understand isinstance and None checks.", "python", """
                def length(value: str | list[int] | None) -> int:
                    if value is None:
                        return 0
                    if isinstance(value, str):
                        return len(value.strip())          # value: str here
                    return sum(value)                      # value: list[int] here

                print(length(None), length("  hi "), length([1, 2, 3]))
            """),
        ],
        ["def f(x: int, y: str | None = None) -> list[str]:", "from collections.abc import Iterable, Mapping, Callable", "Literal['a', 'b'] · TypedDict · Final", "type UserId = int  # 3.12", "mypy --strict src/ · pyright"],
        ["Mutable default with a type hint is still a mutable default.", "Using list instead of Sequence/Iterable for parameters rejects tuples and generators.", "Overusing Any silently disables checking.", "Annotations referencing later classes need quotes or from __future__ import annotations."],
        [
            qa("basic", "Does Python enforce type hints at runtime?", "No. The interpreter stores annotations but ignores them when calling functions. Static checkers (mypy, pyright) and some libraries (pydantic, FastAPI) use them."),
            qa("basic", "Optional[int] vs int | None?", "They mean the same thing: the value may be an int or None. int | None is the modern 3.10+ syntax; Optional does not mean 'optional argument', only 'nullable'."),
            qa("intermediate", "Why annotate parameters with Iterable instead of list?", "It accepts any iterable (tuples, sets, generators) so callers aren't forced to build lists, and it documents that the function only iterates. Returning a concrete list gives callers the most capabilities."),
            qa("intermediate", "What is TypedDict for?", "It types dictionaries with a fixed set of string keys and per-key value types, common for JSON payloads, while remaining plain dicts at runtime."),
        ],
        ["typing-advanced", "functions-args"],
        chain(
            ("Write hints", "x: int -> str", "Annotate", "You add annotations to signatures and variables."),
            ("Store", "__annotations__", "Runtime", "Python only stores them; the code runs the same.", "hints"),
            ("Type check", "mypy / pyright", "Static check", "Checkers infer and verify types across calls without running the code.", "source"),
            ("Report", "errors / IDE", "Feedback", "Mismatches surface in CI or in the editor before production.", "issues"),
        ),
    ),
    topic(
        "typing-advanced", "Generics, TypeVar & Protocol", "typing", "advanced", "TG",
        "Reusable typed functions and classes, structural interfaces, and overloads.",
        "A generic is a labeled container that says 'whatever you put in, you get the same kind out'. A Protocol is a job ad that says 'anyone who can do X may apply', no diploma (inheritance) required.",
        "Generics let you write functions and classes that work over many types while preserving the relationship between inputs and outputs. A TypeVar like T stands for 'some type' consistent within one call, so def first(xs: list[T]) -> T tells the checker that first([1, 2]) returns int. Python 3.12 adds native syntax: def first[T](xs: list[T]) -> T and class Box[T]: .... TypeVars can be bounded (bound=Comparable) or constrained to specific types. typing.Protocol defines structural interfaces: any class with matching methods satisfies it without inheriting, which is static duck typing; @runtime_checkable allows isinstance checks for method presence. @overload declares several signatures for one implementation, and ParamSpec preserves a wrapped function's parameters in decorators. Variance (covariant/contravariant) explains why list[int] is not a list[float] but Sequence[int] is a Sequence[float]. Self, TypeGuard/TypeIs and Never cover common advanced patterns.",
        ["Typed containers and repositories (Repository[User]).", "Interfaces for plugins without forcing a base class (Protocol).", "Decorators that keep the original signature (ParamSpec).", "Functions with different return types per argument type (@overload)."],
        [
            "TypeVar links input and output types within a call.",
            "3.12 syntax: def f[T](x: T) -> T and class Box[T].",
            "Protocol = structural typing; no inheritance needed.",
            "Bounds restrict a TypeVar to subtypes of a given type.",
            "Mutable containers are invariant; read-only ones can be covariant.",
        ],
        [
            ex("Generic functions and classes", "intermediate", "3.12 type parameter syntax; runs normally at runtime.", "python", """
                from collections.abc import Sequence

                def first[T](xs: Sequence[T], default: T) -> T:
                    return xs[0] if xs else default

                class Stack[T]:
                    def __init__(self) -> None:
                        self._items: list[T] = []
                    def push(self, item: T) -> None:
                        self._items.append(item)
                    def pop(self) -> T:
                        return self._items.pop()

                s: Stack[int] = Stack()
                s.push(1); s.push(2)
                print(first([3, 4], 0), first([], "none"), s.pop())
                print(Stack.__type_params__)
            """),
            ex("Protocols: structural typing", "advanced", "Anything with .area() qualifies; runtime_checkable enables isinstance.", "python", """
                from typing import Protocol, runtime_checkable
                import math

                @runtime_checkable
                class Shape(Protocol):
                    def area(self) -> float: ...

                class Circle:
                    def __init__(self, r: float): self.r = r
                    def area(self) -> float: return math.pi * self.r ** 2

                class Square:
                    def __init__(self, s: float): self.s = s
                    def area(self) -> float: return self.s ** 2

                def total_area(shapes: list[Shape]) -> float:
                    return sum(s.area() for s in shapes)

                print(round(total_area([Circle(1), Square(2)]), 3))
                print(isinstance(Square(1), Shape), isinstance("text", Shape))
            """),
            ex("Bounded TypeVar, overload and ParamSpec", "advanced", "Precise signatures for checkers; ordinary behavior at runtime.", "python", """
                from typing import TypeVar, overload, ParamSpec, Callable
                from functools import wraps

                N = TypeVar("N", int, float)
                def clamp(x: N, lo: N, hi: N) -> N:
                    return max(lo, min(x, hi))

                @overload
                def parse(v: str) -> int: ...
                @overload
                def parse(v: bytes) -> str: ...
                def parse(v):
                    return int(v) if isinstance(v, str) else v.decode()

                P = ParamSpec("P")
                R = TypeVar("R")
                def logged(fn: Callable[P, R]) -> Callable[P, R]:
                    @wraps(fn)
                    def inner(*args: P.args, **kwargs: P.kwargs) -> R:
                        print("calling", fn.__name__, args, kwargs)
                        return fn(*args, **kwargs)
                    return inner

                @logged
                def add(a: int, b: int = 0) -> int:
                    return a + b

                print(clamp(15, 0, 10), clamp(0.5, 0.0, 1.0), parse("42"), parse(b"hi"), add(2, b=3))
            """),
        ],
        ["T = TypeVar('T') · def f[T](x: T) -> T", "class Repo[T]: ...", "class Readable(Protocol): def read(self) -> bytes: ...", "@overload · ParamSpec · Concatenate", "TypeVar('T', bound=Hashable) · Self · TypeIs"],
        ["runtime_checkable isinstance only checks method names exist, not signatures.", "list[Dog] is not a list[Animal] (invariance) even if Dog subclasses Animal.", "Overload signatures must be followed by one real implementation.", "Too much generic machinery can hurt readability."],
        [
            qa("intermediate", "What is a TypeVar?", "A placeholder for a type that is consistent within a single use, letting checkers connect parameter and return types, as in def identity(x: T) -> T. It can be bounded or constrained to limit allowed types."),
            qa("advanced", "Protocol vs ABC?", "Protocols use structural subtyping: any class with the required members matches, checked statically, no inheritance needed. ABCs are nominal: classes must inherit or register, and checks happen at runtime."),
            qa("advanced", "Why is list[int] not compatible with list[float]?", "Lists are mutable and therefore invariant: a function taking list[float] could append a float into your list[int]. Read-only types like Sequence[float] are covariant, so Sequence[int] is accepted."),
            qa("advanced", "What is ParamSpec used for?", "It captures the full parameter list of a callable so decorators can declare that the wrapper has the same signature as the wrapped function, preserving type checking of call sites."),
        ],
        ["type-hints", "abstract-base-classes", "decorators"],
        chain(
            ("first[T]", "generic def", "Declare", "The function declares a type parameter T."),
            ("Call site", "first([1, 2])", "Infer", "The checker infers T = int from the argument.", "list[int]"),
            ("Substitute", "T := int", "Solve", "T is replaced everywhere in the signature.", "T"),
            ("Return type", "int", "Check", "The result is known to be int, so misuse is flagged downstream.", "int"),
        ),
    ),
    topic(
        "collections-module", "collections: deque, Counter, defaultdict, namedtuple", "stdlib", "basic", "CM",
        "Specialized containers that replace a lot of hand-written bookkeeping.",
        "collections is a set of specialized drawers: a revolving door (deque), a tally sheet (Counter), a drawer that creates folders on demand (defaultdict), and labeled envelopes (namedtuple).",
        "The collections module extends the built-ins with high-performance containers. deque is a double-ended queue with O(1) appends and pops at both ends, an optional maxlen for bounded buffers, and rotate; list.pop(0) is O(n) by comparison. Counter is a dict subclass for counting hashables, with most_common, arithmetic (+, -, &, |) and update. defaultdict calls a factory for missing keys, making grouping (defaultdict(list)) and nested counts trivial. namedtuple creates lightweight immutable tuple subclasses with named fields, _replace and _asdict; typing.NamedTuple is the annotated class syntax. OrderedDict still offers move_to_end and order-sensitive equality, useful for LRU caches, and ChainMap layers several mappings for config lookups (CLI over env over defaults). Choosing these over manual dict/list code makes intent clearer and is usually faster because they are implemented in C.",
        ["Sliding windows and BFS queues with deque.", "Word frequencies and top-N with Counter.", "Grouping records by key with defaultdict(list).", "Lightweight records with namedtuple; layered config with ChainMap."],
        [
            "deque: O(1) at both ends; maxlen evicts old items.",
            "Counter.most_common(n) and Counter arithmetic.",
            "defaultdict(factory) creates values on missing-key access.",
            "namedtuple is immutable, indexable and memory-light.",
            "ChainMap searches mappings in order; writes go to the first.",
        ],
        [
            ex("deque and Counter", "basic", "Bounded history and frequency counting.", "python", """
                from collections import deque, Counter

                recent = deque(maxlen=3)
                for page in ["home", "docs", "blog", "about", "docs"]:
                    recent.append(page)
                print(recent)
                recent.appendleft("start"); recent.rotate(1)
                print(recent)

                words = "the cat and the hat and the bat".split()
                c = Counter(words)
                print(c.most_common(2), c["dog"])
                print(c + Counter(["cat", "cat"]), c - Counter({"the": 2}))
            """),
            ex("defaultdict grouping and nesting", "basic", "No more 'if key not in d' boilerplate.", "python", """
                from collections import defaultdict

                orders = [("alice", "book"), ("bob", "pen"), ("alice", "lamp")]
                by_user = defaultdict(list)
                for user, item in orders:
                    by_user[user].append(item)
                print(dict(by_user))

                matrix = defaultdict(lambda: defaultdict(int))
                matrix["a"]["x"] += 1; matrix["a"]["y"] += 2; matrix["b"]["x"] += 5
                print({k: dict(v) for k, v in matrix.items()})
                print("ghost" in by_user, by_user["ghost"], "ghost" in by_user)
            """),
            ex("namedtuple, OrderedDict, ChainMap", "intermediate", "Records, LRU ordering and layered lookups.", "python", """
                from collections import namedtuple, OrderedDict, ChainMap
                from typing import NamedTuple

                Point = namedtuple("Point", "x y")
                p = Point(1, 2)
                print(p, p.x, p[1], p._replace(x=9), p._asdict())

                class Pixel(NamedTuple):
                    x: int
                    y: int
                    color: str = "black"
                print(Pixel(3, 4))

                lru = OrderedDict(a=1, b=2, c=3)
                lru.move_to_end("a"); lru.popitem(last=False)
                print(lru)

                defaults = {"debug": False, "port": 8000}
                env = {"port": 9000}
                cli = {"debug": True}
                cfg = ChainMap(cli, env, defaults)
                print(cfg["debug"], cfg["port"], dict(cfg))
            """),
        ],
        ["deque(maxlen=n) · appendleft · popleft · rotate", "Counter(xs).most_common(3)", "defaultdict(list) · defaultdict(int)", "namedtuple('P', 'x y') · class P(NamedTuple)", "OrderedDict.move_to_end · ChainMap(a, b, c)"],
        ["Reading a missing key from a defaultdict inserts it.", "Counter subtraction with - drops non-positive counts; use subtract() to keep them.", "deque indexing in the middle is O(n).", "namedtuple fields cannot start with an underscore."],
        [
            qa("basic", "Why use deque instead of list for a queue?", "list.pop(0) and insert(0, x) shift every element, O(n). deque is a doubly linked list of blocks with O(1) appends and pops at both ends, and it is thread-safe for those operations."),
            qa("basic", "What does defaultdict do on a missing key?", "It calls its default_factory with no arguments, stores the result under that key and returns it, so d[k].append(x) works without initialization."),
            qa("intermediate", "How do you get the top 3 most frequent items?", "Counter(items).most_common(3), which uses a heap internally when n is small relative to the number of distinct items."),
            qa("intermediate", "namedtuple vs dataclass?", "namedtuple is an immutable tuple: lightweight, indexable, unpackable, hashable. dataclass is a regular class: mutable by default, supports defaults, methods, slots and frozen mode, but isn't a tuple."),
        ],
        ["collections", "heapq-bisect", "dict-internals"],
        chain(
            ("Raw data", "events / words", "Input", "A stream of items arrives that you need to organize."),
            ("Pick tool", "what do you need?", "Choose", "Ends of a queue: deque. Counts: Counter. Groups: defaultdict.", "items"),
            ("C-speed ops", "O(1) ops", "Operate", "Operations are implemented in C with the right complexity.", "op"),
            ("Result", "clear intent", "Output", "Less bookkeeping code and the intent is obvious to readers.", "data"),
        ),
    ),
    topic(
        "heapq-bisect", "heapq & bisect", "stdlib", "intermediate", "HB",
        "Priority queues on plain lists, and binary search on sorted lists.",
        "heapq is a hospital triage line: whoever is most urgent is always at the front, even as new patients arrive. bisect is finding your page in a dictionary by opening it in the middle and halving the search each time.",
        "heapq implements a binary min-heap on top of a regular list: heap[0] is always the smallest item, heappush and heappop are O(log n), and heapify turns a list into a heap in O(n). Store tuples like (priority, counter, item) so ties are broken without comparing items, and negate priorities to simulate a max-heap. heapq.nsmallest and nlargest find top-k items efficiently, and heapq.merge lazily merges already sorted iterables. bisect performs binary search on a sorted list: bisect_left/bisect_right return insertion points in O(log n), and insort inserts while keeping order (the insertion itself is O(n) due to shifting). Since 3.10 both accept a key function. Together they solve scheduling, Dijkstra's shortest paths, streaming top-k, percentile buckets, and range lookups such as grading scales.",
        ["Task schedulers and event simulations.", "Dijkstra and A* shortest-path algorithms.", "Top-k items from a big stream.", "Mapping scores to grades or timestamps to buckets with bisect."],
        [
            "heap[0] is the minimum; there is no built-in max-heap.",
            "Use (priority, seq, item) tuples to avoid comparing items.",
            "heapify is O(n); push/pop are O(log n).",
            "bisect_left vs bisect_right differ for equal values.",
            "insort keeps a list sorted but insertion is O(n).",
        ],
        [
            ex("Priority queue", "intermediate", "Tie-break with a counter so tasks never get compared.", "python", """
                import heapq, itertools

                counter = itertools.count()
                pq = []
                for prio, task in [(3, "write docs"), (1, "fix prod bug"), (2, "review PR"), (1, "rotate keys")]:
                    heapq.heappush(pq, (prio, next(counter), task))
                print("peek:", pq[0][2])
                while pq:
                    prio, _, task = heapq.heappop(pq)
                    print(prio, task)

                nums = [5, 1, 9, 3, 7]
                print(heapq.nlargest(2, nums), heapq.nsmallest(2, nums))
                max_heap = [-n for n in nums]; heapq.heapify(max_heap)
                print("max:", -max_heap[0])
            """),
            ex("bisect for range lookups", "intermediate", "Grades, insertion points and keyed search.", "python", """
                from bisect import bisect_left, bisect_right, insort, bisect

                def grade(score, breakpoints=(60, 70, 80, 90), grades="FDCBA"):
                    return grades[bisect(breakpoints, score)]
                print([grade(s) for s in (33, 60, 77, 89, 90, 100)])

                xs = [10, 20, 20, 30]
                print(bisect_left(xs, 20), bisect_right(xs, 20))
                insort(xs, 25); print(xs)

                events = [(1, "boot"), (5, "login"), (9, "logout")]
                i = bisect_right(events, 6, key=lambda e: e[0])
                print("last event before t=6:", events[i - 1])
            """),
            ex("Dijkstra in a few lines", "advanced", "heapq is the classic frontier for shortest paths.", "python", """
                import heapq

                graph = {"A": {"B": 4, "C": 1}, "C": {"B": 2, "D": 7}, "B": {"D": 1}, "D": {}}

                def dijkstra(src):
                    dist = {src: 0}
                    frontier = [(0, src)]
                    while frontier:
                        d, node = heapq.heappop(frontier)
                        if d > dist.get(node, float("inf")):
                            continue
                        for nxt, w in graph[node].items():
                            nd = d + w
                            if nd < dist.get(nxt, float("inf")):
                                dist[nxt] = nd
                                heapq.heappush(frontier, (nd, nxt))
                    return dist

                print(dijkstra("A"))
                print(list(heapq.merge([1, 4, 9], [2, 3, 10])))
            """),
        ],
        ["heapq.heappush(h, (prio, n, item)) · heappop(h)", "heapq.heapify(xs) · h[0]", "heapq.nlargest(k, xs, key=f)", "bisect_left(xs, x) · bisect_right(xs, x)", "insort(xs, x, key=f)"],
        ["Comparing payloads on equal priority raises TypeError for non-comparable items.", "Mutating a priority in place breaks the heap invariant; push a new entry and skip stale ones.", "bisect on an unsorted list returns meaningless results.", "A heap list is not sorted beyond heap[0]."],
        [
            qa("intermediate", "How do you implement a max-heap with heapq?", "Push negated keys (-priority) and negate again when popping, or wrap items in a class with reversed __lt__. heapq only provides a min-heap."),
            qa("intermediate", "Why push (priority, counter, item)?", "If two priorities are equal, tuple comparison falls back to the next element; a monotonic counter guarantees uniqueness and FIFO order without ever comparing items, which may not be comparable."),
            qa("advanced", "nlargest vs sorted()[:k]?", "nlargest keeps a heap of size k, O(n log k) time and O(k) memory, which wins for small k on large inputs. For k close to n, sorting is simpler and comparable."),
            qa("intermediate", "bisect_left vs bisect_right?", "For values equal to x, bisect_left returns the position before them and bisect_right the position after them. Use left for 'first index >= x' and right for 'first index > x'."),
        ],
        ["collections-module", "sorting-keys"],
        chain(
            ("heappush", "append + sift", "Insert", "The item is appended and sifted up until its parent is smaller.", ""),
            ("Invariant", "parent <= kids", "Maintain", "Every parent is <= its children; heap[0] is the minimum.", "item"),
            ("heappop", "take root", "Remove min", "The root is removed and the last element moves to the top.", "min"),
            ("Sift down", "O(log n)", "Restore", "It sinks below smaller children until the invariant holds again.", "last"),
        ),
    ),
    topic(
        "itertools-module", "itertools", "stdlib", "intermediate", "IT",
        "Lazy building blocks for combining, slicing, grouping and generating iterators.",
        "itertools is a set of plumbing fittings for data pipes: joints (chain), valves (islice, takewhile), splitters (tee), and sorters (groupby) that connect without storing the water.",
        "itertools provides fast, memory-efficient iterator building blocks implemented in C. Infinite iterators include count, cycle and repeat. Terminating tools include chain and chain.from_iterable for concatenation, islice for slicing any iterator, takewhile/dropwhile for predicate cut-offs, compress, filterfalse, accumulate for running totals, pairwise (3.10) for consecutive pairs, batched (3.12) for fixed-size chunks, zip_longest for uneven inputs, starmap and tee to split one iterator into several. groupby groups consecutive items with equal keys, so input usually needs to be sorted by the same key first. Combinatoric generators include product, permutations, combinations and combinations_with_replacement. Because everything is lazy, you can process infinite or huge streams and only pay for what you consume. Many recipes in the docs (and the more-itertools package) build on these primitives.",
        ["Chunking API calls with batched.", "Running totals and moving windows with accumulate and pairwise.", "Generating test grids with product.", "Grouping sorted records with groupby."],
        [
            "All tools are lazy; wrap in list() to materialize.",
            "groupby only groups consecutive equal keys.",
            "islice works on any iterator, including infinite ones.",
            "tee buffers values; don't use the original iterator afterwards.",
            "product/permutations/combinations grow combinatorially.",
        ],
        [
            ex("Slicing and combining streams", "basic", "Infinite counters, chain, islice and pairwise.", "python", """
                from itertools import count, cycle, islice, chain, pairwise, accumulate, batched

                print(list(islice(count(10, 5), 4)))
                print(list(islice(cycle("AB"), 5)))
                print(list(chain([1, 2], (3, 4), "xy")))
                print(list(pairwise([1, 4, 9, 16])))
                print(list(accumulate([3, 1, 4, 1, 5])), list(accumulate([3, 1, 4], max)))
                print(list(batched(range(7), 3)))
            """),
            ex("groupby needs sorted input", "intermediate", "Groups are consecutive runs; sort by the same key first.", "python", """
                from itertools import groupby
                from operator import itemgetter

                sales = [("east", 10), ("west", 5), ("east", 7), ("west", 3), ("north", 1)]
                print([(k, len(list(g))) for k, g in groupby(sales, key=itemgetter(0))])
                sales.sort(key=itemgetter(0))
                for region, rows in groupby(sales, key=itemgetter(0)):
                    print(region, sum(amount for _, amount in rows))
                print(["".join(g) for _, g in groupby("aaabccdd")])
            """),
            ex("Combinatorics", "intermediate", "product, permutations and combinations.", "python", """
                from itertools import product, permutations, combinations, combinations_with_replacement, takewhile, zip_longest

                print(list(product(["S", "M"], ["red", "blue"])))
                print(list(permutations("abc", 2)))
                print(list(combinations([1, 2, 3, 4], 2)))
                print(len(list(combinations_with_replacement(range(3), 2))))
                print(list(takewhile(lambda x: x < 10, [1, 5, 12, 3])))
                print(list(zip_longest("ab", [1, 2, 3], fillvalue="-")))
            """),
        ],
        ["islice(it, start, stop) · chain.from_iterable(lists)", "groupby(sorted(xs, key=k), key=k)", "accumulate(xs) · pairwise(xs) · batched(xs, n)", "product(a, b) · permutations(xs, r) · combinations(xs, r)", "takewhile · dropwhile · zip_longest · tee"],
        ["Consuming a groupby group after advancing to the next one yields nothing.", "list(count()) never finishes.", "tee can use a lot of memory if one branch runs far ahead.", "Combinatoric explosions: product of 10 lists of 10 is 10 billion tuples."],
        [
            qa("intermediate", "Why does groupby return the same key multiple times?", "groupby only merges consecutive items with equal keys. If the input isn't sorted (or clustered) by that key, the same key appears in several groups. Sort by the key first or use a defaultdict."),
            qa("intermediate", "How do you take the first n items from a generator?", "itertools.islice(gen, n). Generators don't support slicing syntax, and islice consumes only what it needs, so it works on infinite iterators."),
            qa("basic", "chain vs chain.from_iterable?", "chain(a, b, c) takes iterables as arguments; chain.from_iterable(iterable_of_iterables) takes a single iterable that yields iterables, which can itself be lazy, e.g. flattening a generator of lists."),
            qa("advanced", "How would you process a huge stream in fixed-size chunks?", "Use itertools.batched(stream, n) (3.12+) or a recipe with islice in a loop; each chunk is a tuple and only one chunk is in memory at a time, ideal for bulk inserts or batched API calls."),
        ],
        ["iterators-generators", "comprehensions", "generators-advanced"],
        chain(
            ("count()", "infinite", "Source", "An infinite lazy iterator produces numbers on demand."),
            ("map/filter", "transform", "Transform", "Each value flows through transformations one at a time.", "n"),
            ("islice(…, 5)", "take 5", "Limit", "islice stops pulling after five items.", "value"),
            ("Consumer", "list / for", "Consume", "Only five values were ever computed; memory stays constant.", "5 items"),
        ),
    ),
    topic(
        "regex", "Regular Expressions (re)", "stdlib", "intermediate", "RE",
        "Pattern matching on text: raw strings, groups, flags, and avoiding catastrophic backtracking.",
        "A regex is a stencil you slide across text: wherever the cut-out shape fits, you have a match, and the labeled holes (groups) tell you which pieces landed where.",
        "The re module provides Perl-style regular expressions. Always write patterns as raw strings (r'\\d+') so backslashes reach the regex engine untouched. re.search finds the first match anywhere, re.match only at the start, and re.fullmatch requires the whole string to match, which is the right choice for validation. findall returns strings or tuples of groups, finditer yields Match objects lazily, sub replaces using strings or functions, and split splits on a pattern. Groups capture parts of a match; named groups (?P<name>...) make results readable via m['name'] or groupdict(). Quantifiers are greedy by default and become lazy with ?, flags like re.IGNORECASE, re.MULTILINE and re.VERBOSE change behavior, and re.compile reuses a pattern efficiently. Nested quantifiers like (a+)+ can backtrack exponentially on hostile input (ReDoS), so keep patterns simple, anchor them, and limit input size. For structured formats such as HTML, JSON or emails, prefer a real parser.",
        ["Validating identifiers, codes and simple formats with fullmatch.", "Extracting fields from log lines with named groups.", "Search-and-replace with callable replacements.", "Tokenizing simple languages."],
        [
            "Use raw strings: r'\\d+\\s'.",
            "match = start only, search = anywhere, fullmatch = entire string.",
            "Named groups (?P<name>...) and m.groupdict() aid readability.",
            "Greedy .* vs lazy .*? changes what is captured.",
            "Beware nested quantifiers (ReDoS); prefer parsers for structured data.",
        ],
        [
            ex("search, match, fullmatch, findall", "basic", "The core API on a few strings.", "python", r"""
                import re

                text = "Order 42 shipped on 2026-10-17, order 7 pending"
                print(re.search(r"\d+", text).group())
                print(re.match(r"\d+", text))
                print(re.findall(r"\d+", text))
                print(re.findall(r"(\w+) (\d+)", text))
                print(bool(re.fullmatch(r"[A-Z]{3}-\d{4}", "ABC-1234")), bool(re.fullmatch(r"[A-Z]{3}-\d{4}", "ABC-12345")))
                print(re.split(r"[,;]\s*", "a, b;c ,d"))
            """),
            ex("Named groups on log lines", "intermediate", "Compiled verbose pattern with named groups.", "python", r"""
                import re

                LOG = re.compile(r'''
                    (?P<ip>\d{1,3}(?:\.\d{1,3}){3})\s+
                    (?P<method>GET|POST|PUT|DELETE)\s+
                    (?P<path>\S+)\s+
                    (?P<status>\d{3})
                ''', re.VERBOSE)

                lines = ["10.0.0.1 GET /index.html 200", "10.0.0.2 POST /api/login 401", "garbage line"]
                for line in lines:
                    if m := LOG.search(line):
                        print(m["method"], m["path"], int(m["status"]), m.groupdict()["ip"])
                    else:
                        print("no match:", line)
            """),
            ex("sub with functions, greedy vs lazy", "intermediate", "Callable replacements and quantifier behavior.", "python", r"""
                import re

                html = "<b>bold</b> and <i>italic</i>"
                print(re.findall(r"<.*>", html))
                print(re.findall(r"<.*?>", html))

                def mask(m):
                    digits = m.group()
                    return "*" * (len(digits) - 4) + digits[-4:]
                print(re.sub(r"\d{12,16}", mask, "card 4111111111111111 exp 12/29"))
                print(re.sub(r"(\w+)@(\w+)\.com", r"\2 at \1", "ada@example.com"))
                print(re.sub(r"\s+", " ", "too    many\n\tspaces").strip())
            """),
        ],
        ["re.search(r'\\d+', s) · re.fullmatch(p, s)", "re.findall · re.finditer · re.sub(p, fn, s) · re.split", "(?P<name>...) · m['name'] · m.groupdict()", "re.compile(p, re.I | re.M | re.X)", ".*? (lazy) · (?:...) (non-capturing) · \\b (word boundary)"],
        ["Forgetting the r prefix turns '\\b' into a backspace character.", "re.match does not search the whole string; validation needs fullmatch or anchors.", "findall with one group returns only the group, not the whole match.", "Catastrophic backtracking with patterns like (a+)+$ on long inputs."],
        [
            qa("basic", "re.match vs re.search vs re.fullmatch?", "match anchors at the start of the string, search scans for the first match anywhere, and fullmatch requires the entire string to match the pattern, which is what you want for validation."),
            qa("basic", "Why use raw strings for regex?", "Backslashes are escape characters in normal Python strings ('\\b' is a backspace). A raw string passes backslashes through unchanged so the regex engine sees \\b, \\d and friends."),
            qa("intermediate", "Greedy vs lazy quantifiers?", "Greedy quantifiers (*, +) consume as much as possible and backtrack; lazy ones (*?, +?) consume as little as possible. On '<b>x</b>', <.*> matches the whole string while <.*?> matches '<b>'."),
            qa("advanced", "What is ReDoS and how do you avoid it?", "Regular-expression denial of service: ambiguous patterns with nested quantifiers backtrack exponentially on crafted input, freezing the process. Avoid nested quantifiers, anchor patterns, limit input length, and use possessive quantifiers/atomic groups (3.11+) or a parser."),
        ],
        ["strings-fstrings", "bytes-unicode"],
        chain(
            ("r'(?P<y>\\d+)'", "raw pattern", "Write", "A raw string pattern describes the shape of text you want."),
            ("re.compile", "state machine", "Compile", "The pattern is compiled into matcher bytecode, and cached.", "pattern"),
            ("Scan text", "try positions", "Match", "The engine tries positions, backtracking when a path fails.", "text"),
            ("Match obj", "groups / span", "Result", "On success you get a Match with group(), groupdict() and span().", "match"),
        ),
    ),
    topic(
        "datetime-timezones", "datetime & Time Zones", "stdlib", "intermediate", "DT",
        "Aware vs naive datetimes, zoneinfo, UTC storage, parsing and arithmetic.",
        "A naive datetime is a wall clock photo with no city in the frame: you know it says 9:00, not where. An aware datetime includes the city, so everyone can convert it to their own clock.",
        "datetime offers date, time, datetime and timedelta types. A naive datetime has no tzinfo and its meaning is ambiguous; an aware datetime carries a tzinfo and represents an exact instant. Use datetime.now(timezone.utc) for the current instant (datetime.utcnow is deprecated because it returns a naive value) and zoneinfo.ZoneInfo('Europe/Berlin') for IANA time zones with daylight-saving rules. Best practice is to store and compute in UTC, and convert to local time only for display with astimezone. Arithmetic with timedelta works on wall-clock fields within a zone, so across DST changes an aware datetime plus 24 hours may not land on the same local time; do exact duration math in UTC. Parse with fromisoformat (which handles offsets and 'Z' since 3.11) or strptime, and format with isoformat or strftime. For durations of code execution use time.perf_counter or time.monotonic, not wall-clock time.",
        ["Storing timestamps in databases as UTC.", "Showing events in each user's local time zone.", "Scheduling with correct DST behavior.", "Measuring elapsed time with monotonic clocks."],
        [
            "Prefer aware datetimes; store UTC, display local.",
            "datetime.now(timezone.utc), not utcnow().",
            "zoneinfo.ZoneInfo provides IANA zones with DST.",
            "Comparing naive and aware datetimes raises TypeError.",
            "Use time.perf_counter/monotonic for durations.",
        ],
        [
            ex("Aware datetimes and conversion", "basic", "Create in UTC, convert for display.", "python", """
                from datetime import datetime, timezone, timedelta
                from zoneinfo import ZoneInfo

                instant = datetime(2026, 10, 17, 17, 15, tzinfo=timezone.utc)
                for zone in ["Asia/Kolkata", "Europe/London", "America/New_York"]:
                    print(zone, instant.astimezone(ZoneInfo(zone)).isoformat())

                naive = datetime(2026, 10, 17, 17, 15)
                try:
                    print(naive < instant)
                except TypeError as e:
                    print("TypeError:", e)
                print(instant + timedelta(days=1, hours=2))
            """),
            ex("DST pitfalls", "advanced", "Wall-clock arithmetic vs exact elapsed time across a DST change.", "python", """
                from datetime import datetime, timedelta, timezone
                from zoneinfo import ZoneInfo

                ny = ZoneInfo("America/New_York")
                before = datetime(2026, 3, 7, 12, 0, tzinfo=ny)      # day before DST starts
                wall = before + timedelta(days=1)                    # same local time next day
                print(wall, wall.utcoffset())
                elapsed = wall.astimezone(timezone.utc) - before.astimezone(timezone.utc)
                print("real elapsed:", elapsed)

                exact = (before.astimezone(timezone.utc) + timedelta(hours=24)).astimezone(ny)
                print("24h later:", exact)
            """),
            ex("Parsing and formatting", "basic", "ISO 8601, strptime, strftime and date math.", "python", """
                from datetime import datetime, date

                ts = datetime.fromisoformat("2026-10-17T22:45:00+05:30")
                print(ts, ts.tzinfo, ts.timestamp())
                print(datetime.fromisoformat("2026-10-17T17:15:00Z"))
                d = datetime.strptime("17/10/2026 08:30", "%d/%m/%Y %H:%M")
                print(d.strftime("%A, %d %B %Y at %I:%M %p"))
                print((date(2026, 12, 25) - date(2026, 10, 17)).days, "days to go")
                print(date(2026, 10, 17).isocalendar())
            """),
        ],
        ["datetime.now(timezone.utc)", "dt.astimezone(ZoneInfo('Asia/Kolkata'))", "datetime.fromisoformat(s) · dt.isoformat()", "datetime.strptime(s, '%Y-%m-%d') · dt.strftime(fmt)", "time.perf_counter() · time.monotonic()"],
        ["datetime.utcnow() returns a naive object that looks like local time to other code.", "Using pytz-style localize assumptions with zoneinfo (just pass tzinfo=).", "Adding timedelta across DST changes wall-clock vs elapsed semantics.", "Measuring durations with time.time(), which can jump with clock adjustments."],
        [
            qa("basic", "Naive vs aware datetime?", "A naive datetime has no tzinfo, so it doesn't identify a specific instant. An aware datetime includes a tzinfo (UTC offset or zone) and can be compared and converted unambiguously."),
            qa("intermediate", "How should you store timestamps?", "As aware UTC datetimes (or epoch seconds) in storage and APIs, converting to the user's zone only at display time. Store the user's IANA zone name separately if you need local scheduling."),
            qa("intermediate", "Why is datetime.utcnow() discouraged?", "It returns a naive datetime holding UTC values; any code treating it as local time or calling .timestamp() on it gets wrong results. datetime.now(timezone.utc) returns an aware object instead."),
            qa("advanced", "How does DST affect arithmetic?", "Adding a timedelta to an aware datetime in a zone changes the wall-clock fields, then the offset is recalculated, so 'one day later' may be 23 or 25 real hours. Do exact elapsed-time math in UTC and wall-clock math (same local time tomorrow) in the zone."),
        ],
        ["numbers-floats", "json-csv"],
        chain(
            ("Input", "'2026-10-17T…Z'", "Parse", "Text from an API is parsed with fromisoformat into an aware datetime."),
            ("UTC", "tzinfo=UTC", "Normalize", "Convert to UTC for storage and comparisons.", "aware"),
            ("Compute", "timedelta", "Arithmetic", "Durations and comparisons are exact in UTC.", "utc"),
            ("Display", "astimezone(zone)", "Localize", "Convert to the viewer's IANA zone only when rendering.", "utc"),
        ),
    ),
    topic(
        "json-csv", "JSON & CSV Serialization", "stdlib", "basic", "JC",
        "Turn Python data into text and back: json, csv, custom encoders and safe parsing.",
        "Serialization is packing a suitcase for a flight: everything must be folded into a standard shape (JSON or CSV) so another airport, or language, can unpack it.",
        "The json module converts between Python objects and JSON text: dumps/loads work with strings and dump/load with file objects. dicts become objects, lists and tuples become arrays, str, int, float, bool and None map to their JSON equivalents, and dict keys are converted to strings. Other types (datetime, Decimal, sets, dataclasses) need a default= function or a JSONEncoder subclass, and object_hook or parse_float=Decimal customize decoding. indent, sort_keys and separators control formatting, and ensure_ascii=False keeps non-ASCII text readable. The csv module handles quoting, embedded commas and newlines correctly: use csv.reader/writer for rows and DictReader/DictWriter for header-based records, opening files with newline=''. Never use eval or pickle to load untrusted data; json.loads is safe because it only builds plain data, while pickle can execute code. Validate parsed data before trusting it, for example with dataclasses or pydantic.",
        ["REST API payloads and config files.", "Exporting reports to CSV for spreadsheets.", "Serializing dataclasses and datetimes with a default function.", "Streaming large CSV files row by row."],
        [
            "json.dumps(obj, default=fn) for unsupported types.",
            "Tuples become lists; dict keys become strings.",
            "csv handles quoting; never split lines on commas manually.",
            "Open CSV files with newline='' and an explicit encoding.",
            "json is safe to load from untrusted input; pickle is not.",
        ],
        [
            ex("json round trip with custom types", "basic", "default= for datetime/Decimal/dataclasses and parse_float for exact decimals.", "python", """
                import json
                from dataclasses import dataclass, asdict, is_dataclass
                from datetime import datetime, timezone
                from decimal import Decimal

                @dataclass
                class Invoice:
                    id: int
                    amount: Decimal
                    issued: datetime
                    tags: set

                def encode(o):
                    if is_dataclass(o): return asdict(o)
                    if isinstance(o, datetime): return o.isoformat()
                    if isinstance(o, Decimal): return str(o)
                    if isinstance(o, set): return sorted(o)
                    raise TypeError(f"not serializable: {type(o).__name__}")

                inv = Invoice(7, Decimal("19.99"), datetime(2026, 10, 17, tzinfo=timezone.utc), {"b", "a"})
                text = json.dumps(inv, default=encode, indent=2)
                print(text)
                back = json.loads('{"price": 19.99, "ok": true, "none": null}', parse_float=Decimal)
                print(back, json.dumps({1: (1, 2)}), json.dumps("café", ensure_ascii=False))
            """),
            ex("csv with tricky values", "basic", "Commas, quotes and newlines are handled by the csv module.", "python", """
                import csv, io

                rows = [{"name": "Ada, Countess", "note": 'said "hi"', "qty": 3},
                        {"name": "Bob", "note": "multi\\nline", "qty": 5}]
                buf = io.StringIO(newline="")
                writer = csv.DictWriter(buf, fieldnames=["name", "note", "qty"])
                writer.writeheader()
                writer.writerows(rows)
                print(buf.getvalue())

                buf.seek(0)
                for rec in csv.DictReader(buf):
                    print(rec["name"], "|", repr(rec["note"]), "|", int(rec["qty"]) * 2)
            """),
            ex("Never eval data", "intermediate", "json and ast.literal_eval parse data without executing code.", "python", """
                import json, ast

                payload = '{"user": "ada", "roles": ["admin"]}'
                print(json.loads(payload)["roles"])
                print(ast.literal_eval("{'a': [1, 2, (3, 4)]}"))
                try:
                    ast.literal_eval("__import__('os').getcwd()")
                except ValueError as e:
                    print("rejected:", type(e).__name__)
                try:
                    json.loads("{'single': 'quotes'}")
                except json.JSONDecodeError as e:
                    print("JSONDecodeError:", e.msg, "at col", e.colno)
            """),
        ],
        ["json.dumps(o, indent=2, sort_keys=True, default=fn)", "json.loads(s, parse_float=Decimal, object_hook=fn)", "csv.DictReader(f) · csv.DictWriter(f, fieldnames)", "open(p, 'w', newline='', encoding='utf-8')", "ast.literal_eval(s)  # never eval()"],
        ["json converts tuples to lists and int keys to strings, so round trips are not exact.", "Floats in JSON lose Decimal precision unless parse_float=Decimal is used.", "Forgetting newline='' with csv on Windows produces blank lines.", "pickle.loads on untrusted data allows arbitrary code execution."],
        [
            qa("basic", "How do you serialize a datetime to JSON?", "Pass default= a function that returns dt.isoformat() for datetime objects (or subclass JSONEncoder). On load, parse the string back with datetime.fromisoformat, possibly in an object_hook."),
            qa("intermediate", "Why is pickle dangerous for untrusted data?", "Unpickling can call arbitrary callables via __reduce__, so a crafted payload can execute code. Use JSON or another data-only format for anything crossing a trust boundary, or sign the data with HMAC-SHA256 if you must pickle."),
            qa("basic", "Why use the csv module instead of split(',')?", "CSV fields can contain quoted commas, escaped quotes and embedded newlines. The csv module implements the quoting rules (dialects) correctly for both reading and writing."),
            qa("intermediate", "How do you preserve exact decimals when loading JSON?", "json.loads(text, parse_float=Decimal) makes every JSON number with a fraction a Decimal instead of a float, avoiding binary rounding for prices."),
        ],
        ["pathlib-file-io", "datetime-timezones", "security-basics"],
        chain(
            ("Python obj", "dict / dataclass", "Start", "In-memory data with Python types."),
            ("Encode", "default=fn", "Convert types", "Unsupported types are turned into JSON-friendly values.", "obj"),
            ("Text", "JSON / CSV", "Serialize", "The data becomes portable text for files, APIs or queues.", "str"),
            ("Decode", "loads / reader", "Parse", "The receiver parses text back into plain data structures.", "text"),
            ("Validate", "schema / types", "Trust check", "Validate shape and types before using the data.", "data"),
        ),
    ),
    topic(
        "pathlib-file-io", "File I/O & pathlib", "stdlib", "basic", "PL",
        "Object-oriented paths, text vs binary modes, context managers and safe temp files.",
        "pathlib turns paths from strings you have to glue together into map objects that know how to join, find their parent, and list what is around them.",
        "pathlib.Path represents filesystem paths as objects: the / operator joins segments, and attributes like name, stem, suffix and parent replace manual string slicing. Path methods cover common operations: exists, is_file, mkdir(parents=True, exist_ok=True), iterdir, glob and rglob, read_text/write_text, read_bytes/write_bytes, rename, unlink and resolve. open() returns file objects; use them in a with block so they are closed even on errors. Text mode decodes using an encoding (always pass encoding='utf-8'), while 'b' modes read raw bytes. Modes include 'r', 'w' (truncate), 'a' (append), 'x' (exclusive create) and '+' for read/write. Iterating a file object yields lines lazily, which keeps memory constant for large files. tempfile.TemporaryDirectory and NamedTemporaryFile give safe scratch space, and writing to a temp file then os.replace makes updates atomic. Validate paths built from user input to prevent directory traversal.",
        ["Reading config and data files portably across OSes.", "Walking project trees with rglob.", "Atomic file updates via temp file plus os.replace.", "Streaming large logs line by line."],
        [
            "Path('a') / 'b' / 'c.txt' joins portably.",
            "Always use with open(...) and an explicit encoding.",
            "Iterate the file object for line-by-line streaming.",
            "'x' mode fails if the file exists; 'w' truncates.",
            "Resolve and check user paths stay inside a base directory.",
        ],
        [
            ex("Path anatomy", "basic", "Pure path operations, no disk access.", "python", """
                from pathlib import Path, PurePosixPath, PureWindowsPath

                p = PurePosixPath("/srv/app/data") / "reports" / "2026-10.csv.gz"
                print(p.name, p.stem, p.suffix, p.suffixes, p.parent, p.parts[:3])
                print(p.with_suffix(".json"), p.with_name("summary.txt"))
                print(PureWindowsPath(r"C:\\Users\\ada") / "notes.txt")
                print(PurePosixPath("a/b/../c").as_posix(), Path("x.py").suffix == ".py")
            """),
            ex("Reading and writing in a temp dir", "intermediate", "write_text, glob, streaming lines and atomic replace.", "python", """
                import os, tempfile
                from pathlib import Path

                with tempfile.TemporaryDirectory() as tmp:
                    base = Path(tmp)
                    (base / "logs").mkdir(parents=True, exist_ok=True)
                    for i in range(3):
                        (base / "logs" / f"app{i}.log").write_text(f"INFO start\\nERROR boom {i}\\n", encoding="utf-8")

                    errors = 0
                    for log in sorted(base.glob("logs/*.log")):
                        with log.open(encoding="utf-8") as f:
                            errors += sum(1 for line in f if line.startswith("ERROR"))
                    print("files:", [p.name for p in sorted(base.rglob("*.log"))], "errors:", errors)

                    target = base / "config.json"
                    tmp_file = target.with_suffix(".tmp")
                    tmp_file.write_text('{"version": 2}', encoding="utf-8")
                    os.replace(tmp_file, target)                  # atomic swap
                    print(target.read_text(encoding="utf-8"), target.stat().st_size, "bytes")
            """),
            ex("Prevent path traversal", "intermediate", "Resolve user paths and ensure they stay inside a base directory.", "python", """
                import tempfile
                from pathlib import Path

                def safe_join(base: Path, user_path: str) -> Path:
                    candidate = (base / user_path).resolve()
                    if not candidate.is_relative_to(base.resolve()):
                        raise ValueError(f"path escapes base: {user_path!r}")
                    return candidate

                with tempfile.TemporaryDirectory() as tmp:
                    base = Path(tmp)
                    print(safe_join(base, "reports/q3.csv").name)
                    for evil in ["../../etc/passwd", "/etc/shadow"]:
                        try:
                            safe_join(base, evil)
                        except ValueError as e:
                            print(e)
            """),
        ],
        ["Path.home() / '.config' / 'app.toml'", "p.read_text(encoding='utf-8') · p.write_bytes(b)", "p.mkdir(parents=True, exist_ok=True)", "p.glob('*.py') · p.rglob('*.log') · p.iterdir()", "with open(p, 'a', encoding='utf-8') as f: f.write(line)"],
        ["Opening files without an encoding uses a platform-dependent default.", "Mode 'w' silently truncates existing files.", "Reading whole huge files with read() exhausts memory.", "Joining user input into paths without validation enables directory traversal."],
        [
            qa("basic", "Why prefer pathlib over os.path?", "Paths become objects with readable operators and methods (p / 'x', p.suffix, p.read_text()), work across OSes, and reduce string-manipulation bugs. Most standard library functions accept Path objects."),
            qa("basic", "Why use with open(...)?", "The context manager closes the file even when exceptions occur, flushing buffers and releasing OS handles. Without it, files may stay open until garbage collection."),
            qa("intermediate", "How do you update a file atomically?", "Write the new content to a temporary file in the same directory, flush (and fsync if durability matters), then os.replace(tmp, target), which atomically swaps the name so readers see either old or new content."),
            qa("intermediate", "How do you read a 10 GB file safely?", "Iterate over the file object (for line in f) or read fixed-size chunks with f.read(n) in a loop. Both keep memory bounded instead of loading everything with read() or readlines()."),
        ],
        ["exceptions-context", "json-csv", "bytes-unicode"],
        chain(
            ("Path(...)", "object", "Build path", "Compose the path with / instead of string concatenation."),
            ("open()", "mode + encoding", "Open", "Choose text or binary mode and an explicit encoding.", "path"),
            ("with block", "context mgr", "Guard", "The with block guarantees close() on success or error.", "file"),
            ("Stream", "for line in f", "Process", "Iterate lazily so large files use constant memory.", "lines"),
            ("Close", "flush + release", "Finish", "Leaving the block flushes buffers and releases the OS handle.", "done"),
        ),
    ),
]

TOPICS += [
    topic(
        "modules-packages", "Modules, Packages & Imports", "tooling", "basic", "MP",
        "How import finds, executes and caches code, and how to structure packages.",
        "Importing is checking out a book from a library: the first time, the librarian finds it on the shelves (sys.path), prepares it once, and keeps it at the front desk (sys.modules) for everyone after.",
        "A module is a .py file; a package is a directory of modules, usually with an __init__.py that runs when the package is imported. The first import of a module searches sys.path via finders, executes the module's top-level code once, and caches the resulting module object in sys.modules; later imports just return the cached object. import pkg.mod binds pkg, from pkg import name binds name directly, and relative imports (from . import x) work only inside packages. The if __name__ == '__main__': guard keeps script-only code from running on import, and python -m pkg.mod runs a module with its package context. Circular imports happen when two modules import each other at top level; fix them by moving shared code to a third module, importing inside functions, or importing the module rather than names. __all__ controls what from mod import * exports. importlib.import_module loads modules by name dynamically, and importlib.reload re-executes one in development.",
        ["Organizing a codebase into packages and subpackages.", "Plugins loaded by name with importlib.", "Scripts that are also importable (the __main__ guard).", "Debugging ModuleNotFoundError and circular imports."],
        [
            "Module code runs once per process; sys.modules caches it.",
            "sys.path order decides which module wins.",
            "Use absolute imports in applications; relative ones inside packages.",
            "Guard script code with if __name__ == '__main__'.",
            "Run package modules with python -m package.module.",
        ],
        [
            ex("Build and import a package on the fly", "intermediate", "Creates a tiny package in a temp dir and shows caching.", "python", """
                import sys, tempfile, importlib
                from pathlib import Path

                with tempfile.TemporaryDirectory() as tmp:
                    pkg = Path(tmp) / "shop"
                    pkg.mkdir()
                    (pkg / "__init__.py").write_text("print('init shop')\\nfrom .pricing import total\\n__all__ = ['total']\\n")
                    (pkg / "pricing.py").write_text("print('load pricing')\\ndef total(xs):\\n    return sum(xs)\\n")
                    sys.path.insert(0, tmp)

                    import shop
                    import shop                       # cached: no second 'init'
                    print(shop.total([1, 2, 3]), shop.__all__)
                    print("shop.pricing" in sys.modules, shop.pricing.__name__)
                    mod = importlib.import_module("shop.pricing")
                    print(mod is shop.pricing)
                    sys.path.remove(tmp)
            """),
            ex("__name__ and module objects", "basic", "Inspect what import gives you.", "python", """
                import math, json, types

                print(__name__)
                print(math.__name__, type(math).__name__, hasattr(json, "__file__"))
                fake = types.ModuleType("plugins.hello", "a dynamic module")
                exec("def greet(): return 'hello from a dynamic module'", fake.__dict__)
                print(fake.greet(), fake.__doc__)

                if __name__ == "__main__":
                    print("running as a script")
            """),
            ex("Typical project layout", "basic", "src layout with a package and tests.", "text", """
                myproject/
                  pyproject.toml
                  src/
                    shop/
                      __init__.py        # public API: from .pricing import total
                      pricing.py
                      cli.py             # if __name__ == "__main__": main()
                  tests/
                    test_pricing.py
                # run:  python -m shop.cli
            """, runnable=False),
        ],
        ["import pkg.mod · from pkg import name · from . import sibling", "python -m pkg.module", "if __name__ == '__main__': main()", "importlib.import_module('pkg.mod') · importlib.reload(m)", "sys.path · sys.modules · __all__"],
        ["Naming your file random.py or json.py shadows the standard library module.", "Circular imports leave partially initialized modules (AttributeError on import).", "Heavy work at import time slows every consumer.", "Relative imports fail when running a file directly instead of with -m."],
        [
            qa("basic", "What happens when you import a module the first time?", "Python checks sys.modules; on a miss, finders search sys.path, a loader creates a module object, executes its top-level code in the module namespace and stores it in sys.modules. Subsequent imports return the cached object."),
            qa("basic", "What is if __name__ == '__main__' for?", "When run as a script, a module's __name__ is '__main__'; when imported, it's the module's name. The guard keeps script entry code from running on import (and is required for multiprocessing on spawn)."),
            qa("intermediate", "How do you fix a circular import?", "Move shared definitions into a separate module, import inside the function that needs it, or import the module (import a) instead of names (from a import x) so attribute lookup happens later. Often it signals a layering problem."),
            qa("intermediate", "Absolute vs relative imports?", "Absolute imports (from shop.pricing import total) are explicit and work from anywhere; relative imports (from .pricing import total) refer to the current package and only work inside packages. PEP 8 recommends absolute imports for clarity."),
        ],
        ["venv-packaging", "scope-closures"],
        chain(
            ("import shop", "statement", "Request", "The import statement asks for module 'shop'."),
            ("sys.modules?", "cache", "Check cache", "If already loaded, the cached module is returned immediately.", "name"),
            ("Finders", "sys.path", "Search", "Finders walk sys.path for a matching package or module.", "miss"),
            ("Execute", "top-level code", "Load", "A new module object is created and its code runs once.", "spec"),
            ("Bind name", "shop", "Cache & bind", "The module is stored in sys.modules and bound in the importer's scope.", "module"),
        ),
    ),
    topic(
        "venv-packaging", "Virtual Environments, pip & pyproject", "tooling", "basic", "VP",
        "Isolated environments, reproducible dependencies and modern packaging metadata.",
        "A virtual environment is a separate toolbox per project, so upgrading the hammer for one house doesn't break the scaffolding of another.",
        "A virtual environment (python -m venv .venv) is a directory with its own interpreter link and site-packages, so each project can pin different library versions without touching the system Python. Activating it puts its bin (Scripts on Windows) first on PATH; inside, sys.prefix differs from sys.base_prefix. pip installs packages from PyPI; always run it as python -m pip so it targets the interpreter you expect. Pin dependencies for applications with a lock file (pip freeze > requirements.txt, pip-tools, uv or Poetry), while libraries declare compatible ranges. pyproject.toml is the standard project file: [build-system] names the build backend, and [project] holds name, version, requires-python, dependencies, optional dependencies and entry points (console scripts). pip install -e . installs your package in editable mode for development. Tools like uv, Poetry and pipx speed up or simplify these workflows, and dependency hashes plus trusted indexes protect against supply-chain attacks.",
        ["Isolating each project's dependencies.", "Reproducible CI builds from a lock file.", "Publishing a library with pyproject.toml.", "Installing CLI tools globally with pipx."],
        [
            "One venv per project; never pip install into the system Python.",
            "Use python -m pip to avoid mixing interpreters.",
            "Applications pin exact versions; libraries declare ranges.",
            "pyproject.toml [project] holds metadata and dependencies.",
            "Add .venv to .gitignore; commit the lock file.",
        ],
        [
            ex("Am I in a venv?", "basic", "sys.prefix vs base_prefix and where packages go.", "python", """
                import sys, sysconfig
                from importlib import metadata

                print("in venv:", sys.prefix != sys.base_prefix)
                print("python:", sys.version.split()[0])
                print("purelib:", sysconfig.get_paths()["purelib"].endswith("site-packages"))
                try:
                    print("pip", metadata.version("pip"))
                except metadata.PackageNotFoundError:
                    print("pip metadata not visible here (sandbox runs without site-packages)")
            """),
            ex("Everyday venv workflow", "basic", "Create, activate, install, freeze.", "bash", """
                python3 -m venv .venv
                source .venv/bin/activate          # Windows: .venv\\Scripts\\activate
                python -m pip install --upgrade pip
                python -m pip install "requests>=2.32,<3"
                python -m pip freeze > requirements.txt
                python -m pip install -r requirements.txt
                python -m pip install -e ".[dev]"   # editable install with extras
                deactivate
            """, runnable=False),
            ex("Minimal pyproject.toml", "intermediate", "Standard metadata with a console script and dev extras.", "toml", """
                [build-system]
                requires = ["hatchling"]
                build-backend = "hatchling.build"

                [project]
                name = "shop"
                version = "0.1.0"
                requires-python = ">=3.11"
                dependencies = ["httpx>=0.27"]

                [project.optional-dependencies]
                dev = ["pytest>=8", "mypy"]

                [project.scripts]
                shop = "shop.cli:main"
            """, runnable=False),
        ],
        ["python -m venv .venv && source .venv/bin/activate", "python -m pip install -r requirements.txt", "python -m pip freeze · pip list --outdated", "pip install -e '.[dev]'", "uv venv · uv pip install · pipx install ruff"],
        ["Running a global pip that installs into a different interpreter.", "Committing .venv to git (it is machine-specific).", "Unpinned dependencies make builds change underneath you.", "sudo pip install can break OS tools that rely on system Python."],
        [
            qa("basic", "Why use virtual environments?", "They isolate each project's dependencies so different projects can use conflicting versions, keep the system Python clean, and make environments reproducible from a requirements or lock file."),
            qa("basic", "Why python -m pip instead of pip?", "It guarantees pip runs with the same interpreter you are targeting; a bare pip on PATH may belong to another Python, installing packages where your program can't see them."),
            qa("intermediate", "What goes in pyproject.toml?", "The [build-system] table (build backend and its requirements), the [project] table (name, version, requires-python, dependencies, optional dependencies, scripts) and tool configuration such as [tool.pytest.ini_options] or [tool.ruff]."),
            qa("intermediate", "How do you make builds reproducible?", "Pin exact versions (and ideally hashes) in a lock file generated by pip-tools, uv or Poetry, install with that file in CI and production, and update dependencies deliberately with tests."),
        ],
        ["modules-packages", "testing-pytest"],
        chain(
            ("python -m venv", ".venv/", "Create", "A directory with an interpreter link and empty site-packages is created."),
            ("activate", "PATH first", "Activate", "The venv's bin directory is placed first on PATH.", "env"),
            ("pip install", "from PyPI/lock", "Install", "Packages are installed into the venv's site-packages only.", "deps"),
            ("Lock", "requirements.txt", "Pin", "Exact versions are recorded for reproducible installs.", "versions"),
            ("CI / prod", "same versions", "Reproduce", "Every environment installs the same pinned set.", "lock"),
        ),
    ),
    topic(
        "logging-module", "Logging", "tooling", "intermediate", "LG",
        "Loggers, levels, handlers and formatters instead of print, with lazy formatting.",
        "Logging is a newsroom: reporters (loggers) file stories with an urgency level, editors (handlers) decide which outlets get them, and the layout team (formatters) decides how each story looks.",
        "The logging module separates producing log records from deciding where they go. Code calls logger = logging.getLogger(__name__) and then logger.debug/info/warning/error/critical; logger.exception inside an except block also records the traceback. Loggers form a dot-separated hierarchy (app.db is a child of app), and records propagate up to ancestor handlers, so applications configure handlers once at the root or a top-level logger while libraries only create loggers and add a NullHandler. Levels filter at both logger and handler level. Handlers send records to streams, files (RotatingFileHandler), syslog or HTTP; formatters control the layout, and filters or LoggerAdapters can inject context such as request ids. Pass arguments separately (logger.info('user %s', uid)) so formatting only happens if the record is emitted. Configure with basicConfig for scripts or dictConfig for apps, and consider JSON formatting for log aggregation. Never log secrets, tokens or full personal data.",
        ["Application diagnostics in production.", "Library code that stays quiet unless the app enables it.", "Structured JSON logs for ELK or Datadog.", "Tracing requests with contextual ids."],
        [
            "Use getLogger(__name__) per module.",
            "Configure handlers once, in the application entry point.",
            "Lazy args: logger.info('x=%s', x), not f-strings.",
            "logger.exception logs at ERROR with the traceback.",
            "Libraries add NullHandler and never call basicConfig.",
        ],
        [
            ex("Levels, handlers and formatters", "basic", "Configure once; module loggers inherit.", "python", """
                import logging, sys

                logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                                    format="%(levelname)-7s %(name)s: %(message)s", force=True)
                log = logging.getLogger("shop.orders")

                log.debug("hidden: below INFO")
                log.info("order %s created for %s", 42, "ada")
                log.warning("stock low: %d left", 3)
                try:
                    1 / 0
                except ZeroDivisionError:
                    log.exception("price calculation failed")
                logging.getLogger("shop").setLevel(logging.WARNING)
                log.info("now filtered by the parent level")
                log.error("still shown")
            """),
            ex("Hierarchy, propagation and context", "intermediate", "Child loggers propagate; a filter injects a request id.", "python", """
                import logging, sys, contextvars

                request_id = contextvars.ContextVar("request_id", default="-")

                class RequestIdFilter(logging.Filter):
                    def filter(self, record):
                        record.request_id = request_id.get()
                        return True

                handler = logging.StreamHandler(sys.stdout)
                handler.setFormatter(logging.Formatter("[%(request_id)s] %(name)s %(levelname)s %(message)s"))
                handler.addFilter(RequestIdFilter())
                app = logging.getLogger("app")
                app.addHandler(handler); app.setLevel(logging.DEBUG); app.propagate = False

                db = logging.getLogger("app.db")
                request_id.set("req-7f3a")
                db.debug("query took %.1f ms", 12.34)
                logging.getLogger("app.api").info("200 GET /orders")
                print(db.parent.name, db.getEffectiveLevel() == logging.DEBUG)
            """),
            ex("dictConfig for applications", "intermediate", "Declarative config with a rotating file handler.", "python", """
                import logging.config

                LOGGING = {
                    "version": 1,
                    "disable_existing_loggers": False,
                    "formatters": {"plain": {"format": "%(asctime)s %(levelname)s %(name)s %(message)s"}},
                    "handlers": {
                        "console": {"class": "logging.StreamHandler", "formatter": "plain"},
                        "file": {"class": "logging.handlers.RotatingFileHandler", "filename": "app.log",
                                 "maxBytes": 5_000_000, "backupCount": 3, "formatter": "plain"},
                    },
                    "root": {"level": "INFO", "handlers": ["console", "file"]},
                }
                logging.config.dictConfig(LOGGING)
                logging.getLogger(__name__).info("configured")
            """, runnable=False),
        ],
        ["log = logging.getLogger(__name__)", "log.info('user %s', uid) · log.exception('failed')", "logging.basicConfig(level=logging.INFO, format=...)", "logging.config.dictConfig(cfg)", "logging.getLogger('lib').addHandler(logging.NullHandler())"],
        ["Calling basicConfig in a library hijacks the application's logging.", "f-strings in log calls format even when the level is disabled.", "Adding handlers repeatedly (e.g. per request) duplicates every line.", "Logging passwords, tokens or full card numbers."],
        [
            qa("basic", "Why use logging instead of print?", "Logging provides levels, timestamps, module names, configurable destinations and formats, and can be turned up or down without code changes. print goes only to stdout and can't be filtered or routed."),
            qa("intermediate", "How does logger propagation work?", "A record created on 'app.db' is handled by its own handlers and then passed to the handlers of 'app' and the root logger, unless propagate is False. Levels on loggers decide whether a record is created; levels on handlers decide whether it is emitted there."),
            qa("intermediate", "Why log.info('x %s', x) instead of an f-string?", "The message is only formatted if the record passes level checks, saving work for disabled debug logs, and aggregators can group records by the constant message template."),
            qa("advanced", "How should a library configure logging?", "It should only call logging.getLogger(__name__) and optionally add a NullHandler to its top logger. Handlers, levels and formats belong to the application, which configures them once at startup."),
        ],
        ["exceptions-context", "modules-packages"],
        chain(
            ("log.info()", "logger app.db", "Emit", "Code creates a record if the logger's effective level allows it."),
            ("Filters", "add context", "Filter", "Filters can drop records or attach extra fields like request ids.", "record"),
            ("Propagate", "app → root", "Bubble up", "The record travels up the logger hierarchy to ancestor handlers.", "record"),
            ("Handler", "level check", "Route", "Each handler applies its own level and destination.", "record"),
            ("Formatter", "text / JSON", "Render", "The formatter renders the final line for the stream or file.", "line"),
        ),
    ),
    topic(
        "testing-pytest", "Testing with unittest & pytest", "tooling", "intermediate", "TP",
        "Assertions, fixtures, parametrization and mocking for fast, trustworthy tests.",
        "Tests are a building's smoke detectors: cheap to install, quiet when all is well, and they tell you exactly which room is on fire before the whole house burns.",
        "unittest is the standard library's xUnit framework: test classes inherit TestCase, use setUp/tearDown and assertion methods like assertEqual and assertRaises. pytest is the de facto community standard: plain functions with bare assert statements (rewritten to show rich failure diffs), fixtures injected by argument name with scopes and yield-based teardown, @pytest.mark.parametrize for table-driven tests, tmp_path and monkeypatch fixtures, and a huge plugin ecosystem (pytest-cov, pytest-xdist, pytest-asyncio). pytest also runs unittest-style tests. unittest.mock provides Mock, MagicMock and patch to replace collaborators such as HTTP clients or clocks; patch where the name is looked up, not where it is defined, and prefer autospec to catch wrong call signatures. Good tests are fast, isolated, deterministic and focused on behavior; the test pyramid favors many unit tests, fewer integration tests and a handful of end-to-end tests. Measure coverage, but treat it as a guide, not a goal.",
        ["Unit tests for pure business logic.", "Mocking external APIs, time and randomness.", "Table-driven tests with parametrize.", "Regression tests that reproduce a bug before fixing it."],
        [
            "pytest: plain assert, fixtures by name, parametrize.",
            "Fixtures with yield give setup and teardown.",
            "patch where the object is used, e.g. 'app.service.requests.get'.",
            "Use autospec=True so mocks reject invalid calls.",
            "Tests must be deterministic: control time, randomness and I/O.",
        ],
        [
            ex("unittest in the playground", "basic", "TestCase with setUp, assertions and assertRaises.", "python", """
                import sys, unittest

                def apply_discount(price, pct):
                    if not 0 <= pct <= 100:
                        raise ValueError("pct must be 0-100")
                    return round(price * (100 - pct) / 100, 2)

                class DiscountTests(unittest.TestCase):
                    def setUp(self):
                        self.price = 80.0
                    def test_basic(self):
                        self.assertEqual(apply_discount(self.price, 25), 60.0)
                    def test_zero(self):
                        self.assertEqual(apply_discount(self.price, 0), self.price)
                    def test_invalid(self):
                        with self.assertRaises(ValueError):
                            apply_discount(self.price, 120)

                suite = unittest.defaultTestLoader.loadTestsFromTestCase(DiscountTests)
                result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)
                print("ok:", result.wasSuccessful())
            """),
            ex("Mocking with unittest.mock", "intermediate", "Replace a collaborator and assert how it was called.", "python", """
                from unittest.mock import Mock, patch, create_autospec

                class Payments:
                    def charge(self, user_id: int, cents: int) -> str: ...

                def checkout(gateway, user_id, cart):
                    total = sum(cart.values())
                    receipt = gateway.charge(user_id, total)
                    return {"receipt": receipt, "total": total}

                gw = create_autospec(Payments, instance=True)
                gw.charge.return_value = "rcpt-001"
                print(checkout(gw, 7, {"book": 1500, "pen": 250}))
                gw.charge.assert_called_once_with(7, 1750)
                try:
                    gw.charge(1)                    # autospec catches wrong signature
                except TypeError as e:
                    print("TypeError:", e)

                import time
                with patch("time.time", return_value=1_700_000_000.0):
                    print(time.time())
                flaky = Mock(side_effect=[ConnectionError("down"), "ok"])
                for _ in range(2):
                    try: print(flaky())
                    except ConnectionError as e: print("retry after", e)
            """),
            ex("pytest style", "intermediate", "Fixtures, parametrize, tmp_path and monkeypatch (run with pytest locally).", "python", """
                import pytest
                from shop.pricing import apply_discount

                @pytest.fixture
                def cart():
                    items = {"book": 1500, "pen": 250}
                    yield items                    # teardown code would follow
                    items.clear()

                @pytest.mark.parametrize("price, pct, expected", [(100, 0, 100), (100, 25, 75), (80, 50, 40)])
                def test_discount(price, pct, expected):
                    assert apply_discount(price, pct) == expected

                def test_invalid_pct():
                    with pytest.raises(ValueError, match="0-100"):
                        apply_discount(10, 101)

                def test_total(cart):
                    assert sum(cart.values()) == 1750

                def test_config(tmp_path, monkeypatch):
                    monkeypatch.setenv("SHOP_ENV", "test")
                    (tmp_path / "cfg.toml").write_text("debug = true")
                    assert (tmp_path / "cfg.toml").exists()

                # run: python -m pytest -q -k discount --maxfail=1
            """, runnable=False),
        ],
        ["python -m pytest -q -k name -x --lf", "@pytest.fixture(scope='module') · yield", "@pytest.mark.parametrize('a, b', [(1, 2)])", "with pytest.raises(ValueError, match='msg'):", "patch('pkg.mod.name', autospec=True) · Mock(side_effect=...)"],
        ["Patching the definition site instead of the lookup site has no effect.", "Tests that depend on execution order or shared global state are flaky.", "Over-mocking tests implementation details instead of behavior.", "Real network or clock calls make tests slow and nondeterministic."],
        [
            qa("basic", "Why is pytest popular over unittest?", "Plain assert with detailed failure introspection, less boilerplate (functions instead of classes), powerful fixtures with dependency injection and scopes, parametrization, and a large plugin ecosystem. It also runs existing unittest tests."),
            qa("intermediate", "What is a pytest fixture?", "A function decorated with @pytest.fixture whose return or yielded value is injected into tests that name it as a parameter. Code after yield runs as teardown, and scope controls how often it is created (function, module, session)."),
            qa("intermediate", "Where do you patch with mock.patch?", "Where the object is looked up at runtime: if app/service.py does from requests import get, patch 'app.service.get', not 'requests.get'. The patch replaces the name in that module's namespace."),
            qa("advanced", "How do you keep tests deterministic?", "Inject or patch time (freezegun or a clock parameter), seed or inject random generators, isolate the filesystem with tmp_path, avoid real network calls with fakes, and avoid shared mutable state between tests."),
        ],
        ["exceptions-context", "venv-packaging"],
        chain(
            ("Collect", "test_*.py", "Discover", "pytest discovers test files, classes and functions by naming convention."),
            ("Fixtures", "setup", "Inject", "Requested fixtures are created according to their scope.", "deps"),
            ("Run test", "assert", "Execute", "The test runs; assert rewriting captures values on failure.", "inputs"),
            ("Teardown", "after yield", "Clean up", "Fixture code after yield runs even when the test fails.", "result"),
            ("Report", "pass / fail", "Summarize", "Results, diffs and durations are reported; CI fails on errors.", "status"),
        ),
    ),
    topic(
        "profiling-performance", "Profiling & Performance", "tooling", "advanced", "PP",
        "Measure first with timeit and cProfile, then fix algorithms, data structures and hot loops.",
        "Optimizing without profiling is fixing a traffic jam by repaving random streets. A profiler is the traffic helicopter that shows the one intersection where everyone is stuck.",
        "Performance work starts with measurement. timeit runs a small snippet many times with a high-resolution timer and disables GC to reduce noise, which makes it right for micro-benchmarks. cProfile records how many times each function is called and how long it takes (total time and cumulative time including callees); pstats sorts and filters the results, and tools like snakeviz visualize them. Sampling profilers such as py-spy and Scalene profile running production processes with low overhead, and tracemalloc finds memory hot spots. Most wins come from better algorithms and data structures: a set instead of list membership, a dict index instead of nested loops, avoiding repeated work with caching. Next come Python-level idioms: local variable lookups, built-ins and comprehensions implemented in C, str.join, and avoiding attribute lookups in hot loops. For heavy numeric work, vectorize with NumPy, or move hot paths to C extensions, Cython, or Rust. Python 3.11+ is substantially faster thanks to the specializing adaptive interpreter.",
        ["Finding the slow function behind a latency regression.", "Choosing between two implementations with timeit.", "Reducing memory with tracemalloc snapshots.", "Profiling production processes with py-spy."],
        [
            "Measure before and after; optimize the hot path only.",
            "timeit for snippets; cProfile for whole programs.",
            "Sort by cumulative time to find expensive call trees.",
            "Algorithmic fixes (O(n^2) to O(n)) beat micro-tweaks.",
            "Built-ins and C-implemented tools beat hand-written loops.",
        ],
        [
            ex("timeit: list vs set membership", "intermediate", "Data structure choice dominates micro-optimizations.", "python", """
                import timeit

                setup = "items = list(range(10_000)); s = set(items)"
                t_list = timeit.timeit("9_999 in items", setup=setup, number=2_000)
                t_set = timeit.timeit("9_999 in s", setup=setup, number=2_000)
                print(f"list: {t_list * 1000:.2f} ms   set: {t_set * 1000:.3f} ms   speedup ~{t_list / t_set:.0f}x")

                loop = timeit.timeit("r = []\\nfor i in range(1000): r.append(i * 2)", number=500)
                comp = timeit.timeit("[i * 2 for i in range(1000)]", number=500)
                print(f"loop+append: {loop * 1000:.1f} ms   comprehension: {comp * 1000:.1f} ms")
            """),
            ex("cProfile and pstats", "advanced", "Find the function that dominates cumulative time.", "python", """
                import cProfile, pstats, io

                def slow_unique(xs):
                    out = []
                    for x in xs:
                        if x not in out:          # O(n) scan each time
                            out.append(x)
                    return out

                def fast_unique(xs):
                    return list(dict.fromkeys(xs))

                def main():
                    data = [i % 500 for i in range(5_000)]
                    return len(slow_unique(data)), len(fast_unique(data))

                prof = cProfile.Profile()
                print(prof.runcall(main))
                out = io.StringIO()
                pstats.Stats(prof, stream=out).sort_stats("cumulative").print_stats(4)
                print("\\n".join(l for l in out.getvalue().splitlines() if "unique" in l or "ncalls" in l))
            """),
            ex("Profiling commands", "basic", "Profile scripts and live processes.", "bash", """
                python -m cProfile -s cumtime app.py | head -30
                python -m cProfile -o prof.out app.py && python -m pstats prof.out
                python -m timeit -s "xs = list(range(1000))" "sum(xs)"
                py-spy top --pid 12345            # sample a running process
                py-spy record -o flame.svg -- python app.py
                python -X importtime -c "import mypkg" 2> imports.txt
            """, runnable=False),
        ],
        ["python -m timeit -s 'setup' 'stmt'", "python -m cProfile -s cumtime app.py", "pstats.Stats(p).sort_stats('cumulative').print_stats(10)", "tracemalloc.start(); snapshot.statistics('lineno')", "py-spy top --pid PID · python -X importtime"],
        ["Benchmarking with time.time() once instead of repeated, high-resolution timing.", "Profiler overhead distorts very small functions; confirm with timeit.", "Optimizing code that isn't on the hot path.", "Micro-benchmarks that don't reflect real data sizes."],
        [
            qa("intermediate", "How do you find why a Python program is slow?", "Reproduce with realistic input, run cProfile (or py-spy for live processes), sort by cumulative time to find the expensive call tree, then look at tottime for the actual hot functions. Fix, then re-measure."),
            qa("intermediate", "tottime vs cumtime in cProfile?", "tottime is time spent in the function itself excluding calls it makes; cumtime includes all callees. High cumtime with low tottime means the cost is in what it calls."),
            qa("advanced", "What are common Python performance wins?", "Better algorithms and data structures (sets/dicts for lookups), avoiding repeated work (caching, hoisting), using built-ins and comprehensions, batching I/O, and moving numeric loops to NumPy or native extensions. Concurrency helps only for I/O-bound waits or with processes for CPU work."),
            qa("advanced", "Why does timeit disable garbage collection by default?", "So GC pauses don't add noise to micro-benchmarks. If the code allocates many objects and GC cost matters, re-enable it with setup='gc.enable()' for a realistic number."),
        ],
        ["memory-gc", "functools-tools", "gil-concurrency"],
        chain(
            ("Symptom", "slow request", "Notice", "A latency regression or slow job is observed."),
            ("Profile", "cProfile / py-spy", "Measure", "Collect call counts and timings with realistic input.", "workload"),
            ("Hot spot", "cumtime top", "Locate", "Sort by cumulative time to find the expensive call tree.", "stats"),
            ("Fix", "algorithm / data", "Improve", "Change the algorithm or data structure first, then micro-optimize.", "target"),
            ("Re-measure", "timeit / bench", "Verify", "Confirm the improvement and guard it with a benchmark.", "patch"),
        ),
    ),
    topic(
        "memory-gc", "Memory Management, Refcounting & GC", "tooling", "advanced", "GC",
        "Reference counting, the cyclic garbage collector, weak references and finding leaks.",
        "Reference counting is a library card that counts how many people hold a book; at zero, it goes back on the shelf instantly. The cycle collector is the night janitor who finds books only held by each other and returns them.",
        "CPython manages memory primarily with reference counting: every object stores how many references point to it, and when the count drops to zero the object is deallocated immediately, which makes cleanup deterministic for most objects. sys.getrefcount shows the count (plus one for its own argument). Reference cycles, such as a parent and child pointing at each other, never reach zero, so a generational cyclic garbage collector (the gc module) periodically finds unreachable cycles among container objects and frees them. gc.collect forces a collection, gc.get_threshold shows when generations are scanned, and gc.freeze helps fork-based servers avoid copy-on-write. weakref.ref, WeakValueDictionary and WeakKeyDictionary reference objects without keeping them alive, which is ideal for caches and observer lists, and weakref.finalize registers cleanup callbacks. Small objects come from the pymalloc allocator, so freed memory is often reused rather than returned to the OS. Leaks in Python usually mean something still holds references: global caches, unbounded lru_cache, closures, or lingering tracebacks. tracemalloc snapshots show which lines allocate the most.",
        ["Diagnosing memory growth in long-running services.", "Caches that don't prevent garbage collection (weakref).", "Breaking reference cycles in trees and graphs.", "Tuning or freezing GC in pre-fork servers."],
        [
            "Most objects are freed immediately when their refcount hits zero.",
            "The gc module collects unreachable reference cycles.",
            "weakref lets you refer without owning.",
            "tracemalloc compares snapshots to find growth.",
            "Leaks usually mean unexpected references (globals, caches, closures).",
        ],
        [
            ex("Reference counts", "intermediate", "Counts change as names and containers refer to an object.", "python", """
                import sys

                data = []
                print(sys.getrefcount(data))      # +1 for the function argument
                alias = data
                holder = [data, data]
                print(sys.getrefcount(data))
                del alias, holder
                print(sys.getrefcount(data))

                class Noisy:
                    def __del__(self): print("freed immediately")
                n = Noisy()
                n = None
                print("after rebinding")
            """),
            ex("Cycles and the collector", "advanced", "Refcounting can't free cycles; gc.collect can.", "python", """
                import gc, weakref

                class Node:
                    def __init__(self, name): self.name, self.peer = name, None

                gc.disable()
                a, b = Node("a"), Node("b")
                a.peer, b.peer = b, a                  # cycle
                probe = weakref.ref(a)
                del a, b
                print("alive after del:", probe() is not None)
                print("collected:", gc.collect() > 0, "alive now:", probe() is not None)
                gc.enable()
                print(gc.get_threshold(), [g["collections"] >= 0 for g in gc.get_stats()])
            """),
            ex("weakref caches and tracemalloc", "advanced", "A cache that doesn't keep values alive; find the biggest allocations.", "python", """
                import weakref, tracemalloc

                class Image:
                    def __init__(self, name): self.name = name

                cache = weakref.WeakValueDictionary()
                img = Image("logo.png")
                cache["logo"] = img
                print(list(cache.keys()))
                del img
                print(list(cache.keys()))

                tracemalloc.start()
                before = tracemalloc.take_snapshot()
                leak = [str(i) * 10 for i in range(20_000)]
                after = tracemalloc.take_snapshot()
                top = after.compare_to(before, "lineno")[0]
                print(f"+{top.size_diff // 1024} KiB at line {top.traceback[0].lineno}")
                tracemalloc.stop()
            """),
        ],
        ["sys.getrefcount(x) · sys.getsizeof(x)", "gc.collect() · gc.get_threshold() · gc.freeze()", "weakref.ref(obj) · WeakValueDictionary() · weakref.finalize", "tracemalloc.start(); snap.compare_to(old, 'lineno')", "objgraph / memray / guppy (third-party)"],
        ["__del__ methods run at unpredictable times for cycles and may never run at shutdown.", "Storing exceptions keeps their traceback frames (and all locals) alive.", "Unbounded caches (dicts, lru_cache(None)) look like leaks.", "Freed memory may not be returned to the OS, so RSS stays high."],
        [
            qa("intermediate", "How does CPython manage memory?", "Primarily by reference counting with immediate deallocation at zero, plus a generational cyclic garbage collector for unreachable reference cycles. Small objects are allocated from pymalloc arenas."),
            qa("advanced", "Why does Python need a garbage collector if it has refcounting?", "Objects in a reference cycle keep each other's count above zero even when nothing else refers to them. The cyclic GC traverses container objects, finds groups unreachable from outside, and frees them."),
            qa("advanced", "What is a weak reference and when do you use it?", "A reference that doesn't increase the refcount, so the object can still be collected; accessing it returns None afterwards. Use it for caches, registries and observer lists that shouldn't keep objects alive."),
            qa("advanced", "How do you investigate a memory leak?", "Track growth over time, take tracemalloc snapshots and compare them to find allocating lines, inspect referrers with gc.get_referrers or objgraph, and look for global caches, closures, unbounded queues or stored tracebacks."),
        ],
        ["objects-mutability", "slots-memory", "profiling-performance"],
        chain(
            ("Create", "refcount = 1", "Allocate", "A new object starts with one reference from its name."),
            ("Share", "refcount = 3", "Reference", "Other names and containers add references.", "ref"),
            ("Release", "refcount → 0", "Free", "When the last reference goes away the object is freed immediately.", "del"),
            ("Cycle?", "a ↔ b", "Leftovers", "Objects that only reference each other never hit zero.", "cycle"),
            ("gc.collect", "unreachable", "Collect", "The cyclic GC finds unreachable groups and frees them.", "scan"),
        ),
    ),
    topic(
        "contextlib-advanced", "contextlib: Advanced Context Managers", "robust", "intermediate", "CL",
        "@contextmanager, ExitStack, suppress, redirect_stdout and async context managers.",
        "A context manager is a hotel checkout: whatever happens during your stay, on the way out the room is cleaned and the key is returned. ExitStack is a concierge managing checkouts for a whole group of rooms you booked on the fly.",
        "The with statement calls __enter__ on entry and __exit__ on exit, passing exception details so cleanup always runs and the manager can optionally suppress errors by returning True. contextlib.contextmanager turns a generator into a context manager: code before yield is setup, the yielded value is bound by as, and code after yield (inside try/finally) is teardown; exceptions in the with body are raised at the yield. ExitStack manages a dynamic number of context managers and callbacks, unwinding them in reverse order, which is ideal when you open N files or conditionally acquire resources; pop_all transfers ownership. suppress(Exc) ignores specific exceptions, redirect_stdout captures prints, closing calls close(), nullcontext stands in for an optional manager, and chdir (3.11) temporarily changes directory. asynccontextmanager and AsyncExitStack provide the same patterns for async with. ContextDecorator lets a manager double as a decorator.",
        ["Timing and tracing blocks of code.", "Opening a variable number of files or connections safely.", "Temporarily changing state (cwd, env vars, settings) and restoring it.", "Transactions that commit or roll back."],
        [
            "@contextmanager: setup, yield, teardown in finally.",
            "Exceptions from the with body surface at the yield.",
            "ExitStack unwinds in LIFO order, even on errors.",
            "Returning True from __exit__ suppresses the exception.",
            "nullcontext() makes optional managers uniform.",
        ],
        [
            ex("@contextmanager patterns", "basic", "Timer and transaction-style commit/rollback.", "python", """
                from contextlib import contextmanager
                import time

                @contextmanager
                def timer(label):
                    start = time.perf_counter()
                    try:
                        yield
                    finally:
                        print(f"{label}: {(time.perf_counter() - start) * 1000:.2f} ms")

                @contextmanager
                def transaction(db):
                    snapshot = dict(db)
                    try:
                        yield db
                        print("commit")
                    except Exception as e:
                        db.clear(); db.update(snapshot)
                        print("rollback:", e)
                        raise

                with timer("sum"):
                    sum(range(100_000))
                accounts = {"a": 100, "b": 0}
                try:
                    with transaction(accounts) as db:
                        db["a"] -= 150
                        if db["a"] < 0:
                            raise ValueError("insufficient funds")
                except ValueError:
                    pass
                print(accounts)
            """),
            ex("ExitStack for dynamic resources", "advanced", "Acquire N resources; all are released in reverse order.", "python", """
                from contextlib import ExitStack, contextmanager

                @contextmanager
                def resource(name, fail=False):
                    print("open", name)
                    try:
                        if fail:
                            raise RuntimeError(f"{name} failed to open")
                        yield name
                    finally:
                        print("close", name)

                with ExitStack() as stack:
                    handles = [stack.enter_context(resource(n)) for n in ("db", "cache", "queue")]
                    stack.callback(print, "callback runs too")
                    print("using", handles)

                try:
                    with ExitStack() as stack:
                        for n, fail in (("a", False), ("b", True), ("c", False)):
                            stack.enter_context(resource(n, fail))
                except RuntimeError as e:
                    print("error:", e)
            """),
            ex("suppress, redirect_stdout, nullcontext", "intermediate", "Small utilities that remove boilerplate.", "python", """
                from contextlib import suppress, redirect_stdout, nullcontext
                import io, threading

                with suppress(KeyError):
                    {}["missing"]
                print("KeyError suppressed")

                buf = io.StringIO()
                with redirect_stdout(buf):
                    print("captured line")
                print("captured:", buf.getvalue().strip())

                def work(lock=None):
                    with lock if lock is not None else nullcontext():
                        return "done"
                print(work(), work(threading.Lock()))

                class Quiet:
                    def __enter__(self): return self
                    def __exit__(self, exc_type, exc, tb):
                        print("exit saw", exc_type.__name__ if exc_type else None)
                        return exc_type is ZeroDivisionError
                with Quiet():
                    1 / 0
                print("continued after suppressed ZeroDivisionError")
            """),
        ],
        ["@contextmanager def cm(): setup; try: yield x; finally: teardown", "with ExitStack() as s: s.enter_context(cm()) · s.callback(f)", "with suppress(FileNotFoundError): ...", "redirect_stdout(buf) · closing(obj) · nullcontext()", "@asynccontextmanager · AsyncExitStack · contextlib.chdir(path)"],
        ["Forgetting try/finally around yield skips teardown when the body raises.", "Yielding more than once in a @contextmanager generator raises RuntimeError.", "Accidentally returning a truthy value from __exit__ swallows exceptions.", "redirect_stdout is process-global and not thread-safe."],
        [
            qa("intermediate", "How does @contextmanager work?", "It wraps a generator: __enter__ runs it to the yield and returns the yielded value; __exit__ resumes it, either normally or by throwing the body's exception at the yield. Code after the yield (ideally in finally) is the cleanup."),
            qa("intermediate", "When would you use ExitStack?", "When the number or kind of context managers is decided at runtime, such as opening a list of files, or when cleanup callbacks must be registered conditionally. Everything entered is exited in reverse order even if a later step fails."),
            qa("basic", "How can a context manager suppress an exception?", "If __exit__ returns a truthy value, the exception is swallowed and execution continues after the with block. contextlib.suppress does this for listed exception types."),
            qa("advanced", "How do you write an async context manager?", "Implement __aenter__/__aexit__ as coroutines or decorate an async generator with @asynccontextmanager, then use async with. AsyncExitStack handles dynamic sets of async managers."),
        ],
        ["exceptions-context", "generators-advanced"],
        chain(
            ("with cm():", "statement", "Enter", "The with statement calls cm.__enter__()."),
            ("Setup", "before yield", "Acquire", "The generator runs up to yield: open, lock or start a timer.", "enter"),
            ("Body", "your code", "Use", "The yielded value is bound with as and the block runs.", "value"),
            ("__exit__", "exc info", "Exit", "On exit, any exception is thrown into the generator at the yield.", "exc?"),
            ("Teardown", "finally", "Release", "The finally block cleans up; the exception propagates unless suppressed.", "done"),
        ),
    ),
    topic(
        "security-basics", "Security Basics in Python", "robust", "intermediate", "SE",
        "secrets for tokens, sha256 and HMAC for integrity, scrypt for passwords, and never eval untrusted input.",
        "Security code is a bank vault door: the lock design (algorithms) must be proven and standard, the combination (secrets) must never be written on the door (source code), and you never let a stranger's note operate the controls (eval).",
        "Use the secrets module, which draws from the OS CSPRNG, for tokens, password-reset links and API keys; the random module is predictable and must never be used for security. hashlib provides SHA-256, SHA-512, SHA-3 and BLAKE2 for integrity checks and fingerprints; MD5 and SHA-1 are broken and must not be used for security. Message authentication uses hmac with SHA-256, and comparisons of secrets must use hmac.compare_digest or secrets.compare_digest to avoid timing attacks. Passwords must never be stored with a fast hash: use a slow, salted key-derivation function such as hashlib.scrypt or a library like argon2-cffi or bcrypt, with a unique random salt per password. Credentials belong in environment variables or a secrets manager, never in source code. Never call eval, exec or pickle.loads on untrusted input; use json or ast.literal_eval. Run subprocesses with argument lists instead of shell=True, use parameterized SQL queries, and keep dependencies updated and audited (pip-audit).",
        ["Generating session ids, reset tokens and API keys.", "Storing user passwords safely.", "Signing webhooks and verifying payload integrity.", "Reviewing code for eval, shell injection and hardcoded secrets."],
        [
            "secrets.token_urlsafe(32) for tokens; never random.",
            "SHA-256/BLAKE2 for integrity; never MD5/SHA-1.",
            "Passwords: salted scrypt/argon2/bcrypt, never a plain hash.",
            "Compare secrets with hmac.compare_digest.",
            "Secrets come from os.environ or a vault; never hardcode them.",
        ],
        [
            ex("Tokens and digests", "basic", "CSPRNG tokens, SHA-256 and BLAKE2 fingerprints.", "python", """
                import secrets, hashlib

                print("token:", len(secrets.token_urlsafe(32)), "chars")
                print("hex key bits:", len(secrets.token_hex(32)) * 4)
                print("pin:", f"{secrets.randbelow(1_000_000):06d}".isdigit())

                data = b"release-1.4.2.tar.gz contents"
                print("sha256:", hashlib.sha256(data).hexdigest()[:16], "...")
                print("blake2b:", hashlib.blake2b(data, digest_size=16).hexdigest())
                print(hashlib.sha256(b"a").digest() == hashlib.sha256(b"a").digest())
            """),
            ex("Password hashing with scrypt", "intermediate", "Unique salt per password, slow KDF, constant-time verification.", "python", """
                import hashlib, hmac, secrets

                N, R, P = 2**14, 8, 1

                def hash_password(password: str) -> str:
                    salt = secrets.token_bytes(16)
                    dk = hashlib.scrypt(password.encode(), salt=salt, n=N, r=R, p=P, dklen=32)
                    return f"scrypt${N}${R}${P}${salt.hex()}${dk.hex()}"

                def verify_password(password: str, stored: str) -> bool:
                    _, n, r, p, salt_hex, dk_hex = stored.split("$")
                    dk = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt_hex), n=int(n), r=int(r), p=int(p), dklen=32)
                    return hmac.compare_digest(dk.hex(), dk_hex)

                stored = hash_password("correct horse battery staple")
                print(stored[:24] + "...")
                print(verify_password("correct horse battery staple", stored), verify_password("guess", stored))
                print(hash_password("same") != hash_password("same"))       # different salts
            """),
            ex("Signing webhooks with HMAC-SHA256", "intermediate", "Secret from the environment; constant-time signature check.", "python", """
                import hmac, hashlib, os, json

                SECRET = os.environ.get("WEBHOOK_SECRET", "EXAMPLE-ONLY-not-a-real-secret").encode()

                def sign(body: bytes) -> str:
                    return hmac.new(SECRET, body, hashlib.sha256).hexdigest()

                def verify(body: bytes, signature: str) -> bool:
                    return hmac.compare_digest(sign(body), signature)

                body = json.dumps({"event": "paid", "order": 42}).encode()
                sig = sign(body)
                print(verify(body, sig), verify(body.replace(b"42", b"43"), sig))

                user_input = "__import__('os').getcwd()"
                import ast
                try:
                    ast.literal_eval(user_input)       # never eval(user_input)
                except ValueError:
                    print("rejected untrusted expression")
            """),
        ],
        ["secrets.token_urlsafe(32) · secrets.compare_digest(a, b)", "hashlib.sha256(b).hexdigest() · hashlib.blake2b(b)", "hashlib.scrypt(pw, salt=salt, n=2**14, r=8, p=1)", "hmac.new(key, msg, hashlib.sha256).hexdigest()", "os.environ['API_KEY'] · subprocess.run(['ls', path]) · pip-audit"],
        ["Using random for tokens: its Mersenne Twister output is predictable.", "Hashing passwords with plain sha256 (fast and unsalted) instead of a KDF.", "Comparing signatures with == leaks timing information.", "eval/exec/pickle on untrusted data and subprocess with shell=True enable code execution."],
        [
            qa("basic", "secrets vs random?", "random uses the Mersenne Twister, which is fast but predictable once enough outputs are observed, fine for simulations. secrets uses the operating system's cryptographically secure generator and is required for tokens, keys and passwords."),
            qa("intermediate", "How should passwords be stored?", "Never in plain text or with a fast hash. Use a slow, memory-hard, salted KDF such as argon2id, scrypt or bcrypt with a unique random salt per user, store the parameters with the hash, and verify with a constant-time comparison."),
            qa("intermediate", "Why use hmac.compare_digest instead of ==?", "== may return as soon as the first differing byte is found, so response timing reveals how much of a guessed signature is correct. compare_digest takes time independent of where the inputs differ."),
            qa("advanced", "Why is eval on user input dangerous, and what are alternatives?", "eval executes arbitrary Python, so input like __import__('os').system(...) runs commands with your process's privileges. Parse data with json or ast.literal_eval, or write a small explicit parser for expressions."),
            qa("intermediate", "Where should credentials live in a Python app?", "In environment variables or a secrets manager (Vault, AWS Secrets Manager, Kubernetes Secrets), loaded at runtime with os.environ. They must not be committed to source control, logged, or embedded in images."),
        ],
        ["json-csv", "exceptions-context"],
        chain(
            ("Password", "user input", "Receive", "The plaintext password arrives over TLS and is never logged."),
            ("Salt", "token_bytes(16)", "Randomize", "A unique random salt is generated with the secrets module.", "pw"),
            ("scrypt", "slow + memory", "Derive", "A memory-hard KDF turns password and salt into a key.", "salt"),
            ("Store", "params$salt$hash", "Persist", "Parameters, salt and derived key are stored; never the password.", "dk"),
            ("Verify", "compare_digest", "Check login", "Re-derive with the stored salt and compare in constant time.", "hash"),
        ),
    ),
    topic(
        "threading-locks", "Threading Primitives: Locks, Events, Queues", "concurrency", "intermediate", "TL",
        "Lock, RLock, Event, Condition, Semaphore and queue.Queue for safe thread coordination.",
        "Threads are cooks sharing one kitchen. A Lock is the single knife everyone must take turns with, an Event is the dinner bell, a Semaphore is a limited number of stove burners, and a Queue is the order rail between the counter and the cooks.",
        "threading.Thread runs a callable in a new OS thread; start() launches it and join() waits for it, and daemon threads don't block interpreter exit. Because thread switches can happen between bytecodes, compound operations on shared state need synchronization. Lock provides mutual exclusion (use it with with), and RLock can be re-acquired by the thread that holds it, which helps with recursive code. Event lets threads wait for a flag set by another thread, Condition combines a lock with wait/notify for complex state changes, and Semaphore or BoundedSemaphore limits concurrent access to a resource such as connections. queue.Queue is a thread-safe FIFO with blocking put/get, maxsize for back-pressure, and task_done/join for completion tracking, which makes the producer-consumer pattern the simplest correct design. threading.local gives per-thread data. Deadlocks come from acquiring multiple locks in inconsistent order, so keep critical sections small, acquire locks in a fixed order, and use timeouts.",
        ["Producer-consumer pipelines with queue.Queue.", "Limiting concurrent connections with a Semaphore.", "Graceful shutdown signaled with an Event.", "Protecting shared counters and caches with Lock."],
        [
            "Always acquire locks with 'with lock:'.",
            "Queue is the safest way to share work between threads.",
            "Event.wait(timeout) for clean shutdown signals.",
            "Acquire multiple locks in a consistent global order.",
            "join() threads; use daemon threads only for disposable work.",
        ],
        [
            ex("Producer-consumer with Queue", "intermediate", "Workers pull jobs; sentinels stop them; join waits for completion.", "python", """
                import threading, queue

                jobs = queue.Queue(maxsize=5)
                results, results_lock = [], threading.Lock()
                STOP = object()

                def worker(wid):
                    while True:
                        item = jobs.get()
                        if item is STOP:
                            jobs.task_done()
                            return
                        with results_lock:
                            results.append((wid, item * item))
                        jobs.task_done()

                threads = [threading.Thread(target=worker, args=(i,)) for i in range(3)]
                for t in threads: t.start()
                for n in range(10): jobs.put(n)
                for _ in threads: jobs.put(STOP)
                jobs.join()
                for t in threads: t.join()
                print(sorted(v for _, v in results))
                print("workers used:", sorted({w for w, _ in results}) != [])
            """),
            ex("Event and Semaphore", "intermediate", "A start signal, and a limit of 2 concurrent 'connections'.", "python", """
                import threading, time

                go = threading.Event()
                pool = threading.BoundedSemaphore(2)
                active, peak, lock = 0, 0, threading.Lock()

                def client(i):
                    global active, peak
                    go.wait()
                    with pool:
                        with lock:
                            active += 1; peak = max(peak, active)
                        time.sleep(0.02)
                        with lock:
                            active -= 1

                ts = [threading.Thread(target=client, args=(i,)) for i in range(6)]
                for t in ts: t.start()
                print("all waiting:", not go.is_set())
                go.set()
                for t in ts: t.join()
                print("peak concurrent:", peak)
            """),
            ex("RLock, Condition and thread-local data", "advanced", "Re-entrant locking, wait/notify and per-thread state.", "python", """
                import threading

                class Account:
                    def __init__(self): self._lock = threading.RLock(); self.balance = 0
                    def deposit(self, n):
                        with self._lock: self.balance += n
                    def deposit_twice(self, n):
                        with self._lock:                  # re-acquired inside deposit()
                            self.deposit(n); self.deposit(n)

                acct = Account(); acct.deposit_twice(5); print(acct.balance)

                items, cond = [], threading.Condition()
                def consumer():
                    with cond:
                        cond.wait_for(lambda: len(items) >= 3, timeout=2)
                        print("consumer saw", items)
                t = threading.Thread(target=consumer); t.start()
                for i in range(3):
                    with cond:
                        items.append(i); cond.notify_all()
                t.join()

                local = threading.local()
                def tag(name):
                    local.name = name
                    print("thread sees", local.name)
                for n in ("a", "b"):
                    th = threading.Thread(target=tag, args=(n,)); th.start(); th.join()
            """),
        ],
        ["t = threading.Thread(target=f, args=(x,)); t.start(); t.join()", "with lock: ...  # Lock / RLock", "event.set() · event.wait(timeout)", "Semaphore(n) · Condition.wait_for(pred)", "q = queue.Queue(maxsize); q.put(x); q.get(); q.task_done(); q.join()"],
        ["Acquiring two locks in different orders in two threads deadlocks.", "Forgetting task_done() makes Queue.join() hang forever.", "Daemon threads are killed abruptly at exit, skipping cleanup.", "Holding a lock while doing I/O serializes all threads."],
        [
            qa("intermediate", "Lock vs RLock?", "A Lock can be acquired once and blocks even its own holder on a second acquire. An RLock tracks its owner and a recursion count, so the same thread can re-acquire it, which is useful when locked methods call other locked methods."),
            qa("intermediate", "Why is queue.Queue preferred for thread communication?", "It encapsulates locking and condition variables, offers blocking get/put with timeouts and maxsize for back-pressure, and task_done/join for completion tracking. Passing messages avoids most shared-state bugs."),
            qa("advanced", "How do you avoid deadlocks?", "Acquire locks in a single global order, keep critical sections small, avoid calling unknown code while holding locks, use timeouts (lock.acquire(timeout=...)), and prefer message passing with queues."),
            qa("intermediate", "What is a Semaphore used for?", "It allows up to N concurrent holders, such as limiting simultaneous database connections or API calls. BoundedSemaphore additionally raises an error if released more times than acquired."),
        ],
        ["gil-concurrency", "concurrent-futures"],
        chain(
            ("Producer", "q.put(job)", "Enqueue", "The producer puts jobs on a bounded queue; it blocks when full."),
            ("Queue", "thread-safe", "Buffer", "The queue's internal lock and conditions coordinate access.", "job"),
            ("Worker", "q.get()", "Dequeue", "Each worker blocks on get() and receives one job at a time.", "job"),
            ("Shared state", "with lock:", "Protect", "Updates to shared results happen inside a lock.", "result"),
            ("task_done", "q.join()", "Complete", "Workers mark jobs done; join() returns when all are processed.", "done"),
        ),
    ),
    topic(
        "concurrent-futures", "concurrent.futures & multiprocessing", "concurrency", "intermediate", "CF",
        "Executors, futures, as_completed and process pools for parallel CPU work.",
        "An executor is a staffing agency: you submit tasks and get receipts (futures) back immediately. Thread workers share one office; process workers each get their own office, so they truly work in parallel but must mail documents (pickle) back and forth.",
        "concurrent.futures provides a high-level interface over thread and process pools. ThreadPoolExecutor suits I/O-bound work like HTTP calls or file reads, while ProcessPoolExecutor runs CPU-bound Python code in separate processes, each with its own interpreter and GIL, achieving true parallelism. submit(fn, *args) returns a Future with result(timeout), exception(), done() and add_done_callback; map(fn, iterable) returns results in input order, and as_completed yields futures as they finish. Exceptions raised in workers are re-raised when you call result(). Process pools pickle functions, arguments and results, so functions must be defined at module top level, arguments should be small, and chunksize helps with many tiny tasks. The multiprocessing module offers lower-level Process, Pool, Queue, Manager and shared_memory, and start methods (fork, spawn, forkserver) affect what is inherited; spawn requires the if __name__ == '__main__' guard. Executors work as context managers that wait for pending work on exit.",
        ["Parallel HTTP calls with a thread pool.", "CPU-heavy image or data processing with a process pool.", "Fan-out/fan-in jobs collected with as_completed.", "Running blocking calls from asyncio via run_in_executor."],
        [
            "Threads for I/O-bound work; processes for CPU-bound Python.",
            "Future.result() re-raises worker exceptions.",
            "map keeps input order; as_completed gives completion order.",
            "Process pools pickle everything; keep functions top-level.",
            "Guard process code with if __name__ == '__main__'.",
        ],
        [
            ex("ThreadPoolExecutor with as_completed", "intermediate", "Simulated I/O tasks finish out of order; errors surface via result().", "python", """
                from concurrent.futures import ThreadPoolExecutor, as_completed
                import time

                def fetch(url, delay):
                    time.sleep(delay)
                    if "bad" in url:
                        raise ConnectionError(f"{url} unreachable")
                    return f"{url}: 200"

                jobs = {"https://a.example": 0.06, "https://b.example": 0.02, "https://bad.example": 0.04}
                start = time.perf_counter()
                with ThreadPoolExecutor(max_workers=3) as pool:
                    futures = {pool.submit(fetch, u, d): u for u, d in jobs.items()}
                    for fut in as_completed(futures):
                        try:
                            print(fut.result())
                        except ConnectionError as e:
                            print("failed:", e)
                print(f"total ~{time.perf_counter() - start:.2f}s (not the 0.12s sum)")
            """),
            ex("map, timeouts and callbacks", "intermediate", "Ordered results, a per-future timeout and done callbacks.", "python", """
                from concurrent.futures import ThreadPoolExecutor, TimeoutError, wait, FIRST_COMPLETED
                import time

                def square(n):
                    time.sleep(0.01 * (5 - n))
                    return n * n

                with ThreadPoolExecutor(4) as pool:
                    print(list(pool.map(square, range(5))))
                    slow = pool.submit(time.sleep, 0.2)
                    try:
                        slow.result(timeout=0.05)
                    except TimeoutError:
                        print("timed out waiting (task keeps running)")
                    f = pool.submit(square, 4)
                    f.add_done_callback(lambda fut: print("callback got", fut.result()))
                    done, pending = wait([f, slow], return_when=FIRST_COMPLETED)
                    print(len(done), "done first")
            """),
            ex("ProcessPoolExecutor for CPU work", "advanced", "True parallelism across cores (run locally; the sandbox limits processes).", "python", """
                from concurrent.futures import ProcessPoolExecutor
                import math, time

                def count_primes(limit):                     # must be top-level to be picklable
                    return sum(1 for n in range(2, limit) if all(n % d for d in range(2, math.isqrt(n) + 1)))

                if __name__ == "__main__":
                    chunks = [200_000] * 8
                    t = time.perf_counter()
                    with ProcessPoolExecutor() as pool:
                        print(sum(pool.map(count_primes, chunks, chunksize=2)))
                    print(f"{time.perf_counter() - t:.2f}s using all cores")

                    from multiprocessing import Pool, get_context
                    with get_context("spawn").Pool(4) as p:
                        print(p.map(count_primes, [10_000, 20_000]))
            """, runnable=False),
        ],
        ["with ThreadPoolExecutor(max_workers=8) as ex: ex.map(f, xs)", "fut = ex.submit(f, x); fut.result(timeout=5)", "for f in as_completed(futs): ...", "ProcessPoolExecutor(max_workers=os.cpu_count())", "multiprocessing.get_context('spawn') · shared_memory · Manager()"],
        ["Lambdas and nested functions cannot be pickled for process pools.", "Huge arguments are copied (pickled) to each process, eating time and memory.", "Forgetting to call result() hides exceptions raised in workers.", "result(timeout) doesn't cancel the running task."],
        [
            qa("intermediate", "ThreadPoolExecutor vs ProcessPoolExecutor?", "Threads share memory and are cheap, ideal for I/O-bound tasks where the GIL is released while waiting. Processes have separate interpreters and GILs, giving real CPU parallelism at the cost of startup time and pickling data between processes."),
            qa("intermediate", "map vs submit + as_completed?", "map returns results in input order and raises the first exception when you reach it while iterating. submit returns Futures you can handle individually, and as_completed yields them as they finish, which suits progress reporting and per-task error handling."),
            qa("advanced", "Why must process pool functions be top-level?", "Tasks are sent to workers by pickling a reference to the function (module and qualified name). Lambdas, closures and nested functions can't be located by name in the worker, so pickling fails."),
            qa("advanced", "What are multiprocessing start methods?", "fork copies the parent process (fast, but unsafe with threads), spawn starts a fresh interpreter and imports the main module (requires the __main__ guard, default on macOS and Windows), and forkserver forks from a clean server process. Python 3.14 moves the Linux default away from fork."),
        ],
        ["gil-concurrency", "threading-locks", "asyncio-patterns"],
        chain(
            ("submit(f, x)", "caller", "Submit", "The caller hands a task to the executor and gets a Future back."),
            ("Work queue", "pending", "Queue", "Tasks wait in an internal queue until a worker is free.", "task"),
            ("Workers", "threads / procs", "Run", "Workers execute tasks; process pools pickle the call to a child process.", "task"),
            ("Future", "result / error", "Complete", "The worker sets the Future's result or exception.", "outcome"),
            ("as_completed", "fan-in", "Collect", "The caller gathers results as they finish.", "future"),
        ),
    ),
    topic(
        "asyncio-patterns", "asyncio Patterns: Tasks, gather, Queues", "concurrency", "advanced", "AP",
        "TaskGroup, gather, timeouts, semaphores, queues and offloading blocking code.",
        "The event loop is a single chef running many timers: start the rice, then while it simmers, chop vegetables. Tasks are the timers, and an await is the chef saying 'wake me when this is ready'.",
        "asyncio runs many coroutines concurrently on one thread, switching only at await points. asyncio.run starts the event loop; create_task schedules a coroutine to run concurrently and returns a Task you can await or cancel. asyncio.TaskGroup (3.11+) is the structured way to run related tasks: it waits for all of them, and if one fails it cancels the rest and raises an ExceptionGroup, handled with except*. asyncio.gather runs awaitables concurrently and returns results in order, with return_exceptions=True to collect errors instead of failing fast. asyncio.timeout and wait_for impose deadlines, Semaphore limits concurrency (for example to respect API rate limits), and asyncio.Queue builds producer-consumer pipelines with back-pressure. Blocking calls (time.sleep, sync drivers, CPU work) stall the whole loop, so offload them with asyncio.to_thread or run_in_executor. Keep references to created tasks, propagate CancelledError rather than swallowing it, and use async with/async for for async resources and streams.",
        ["Calling many HTTP APIs concurrently with a concurrency limit.", "Async web servers (FastAPI, aiohttp) handling thousands of connections.", "Crawler or ETL pipelines with asyncio.Queue workers.", "Deadlines and cancellation for slow dependencies."],
        [
            "TaskGroup gives structured concurrency and cancels siblings on error.",
            "gather(return_exceptions=True) collects results and errors.",
            "asyncio.timeout(seconds) bounds any block of awaits.",
            "Semaphore caps in-flight operations.",
            "asyncio.to_thread for blocking calls; never time.sleep in async code.",
        ],
        [
            ex("gather vs TaskGroup", "advanced", "Concurrent awaits, error collection and structured failure.", "python", """
                import asyncio, time

                async def fetch(name, delay, fail=False):
                    await asyncio.sleep(delay)
                    if fail:
                        raise ValueError(f"{name} failed")
                    return f"{name} ok"

                async def main():
                    t = time.perf_counter()
                    print(await asyncio.gather(fetch("a", 0.05), fetch("b", 0.03)))
                    print(f"took ~{time.perf_counter() - t:.2f}s")
                    print(await asyncio.gather(fetch("c", 0.01), fetch("d", 0.01, fail=True), return_exceptions=True))
                    try:
                        async with asyncio.TaskGroup() as tg:
                            tg.create_task(fetch("e", 0.2))
                            tg.create_task(fetch("f", 0.01, fail=True))
                    except* ValueError as eg:
                        print("TaskGroup errors:", [str(e) for e in eg.exceptions])

                asyncio.run(main())
            """),
            ex("Rate limiting and timeouts", "advanced", "Semaphore caps concurrency; asyncio.timeout enforces deadlines.", "python", """
                import asyncio

                limit = asyncio.Semaphore(2)
                in_flight = peak = 0

                async def call_api(i):
                    global in_flight, peak
                    async with limit:
                        in_flight += 1; peak = max(peak, in_flight)
                        await asyncio.sleep(0.02)
                        in_flight -= 1
                        return i

                async def slow():
                    await asyncio.sleep(1)

                async def main():
                    print(await asyncio.gather(*(call_api(i) for i in range(6))), "peak:", peak)
                    try:
                        async with asyncio.timeout(0.05):
                            await slow()
                    except TimeoutError:
                        print("deadline exceeded, slow() was cancelled")
                    print(await asyncio.to_thread(sum, range(1000)))

                asyncio.run(main())
            """),
            ex("Queue workers", "advanced", "Producer-consumer with asyncio.Queue and graceful shutdown.", "python", """
                import asyncio

                async def producer(q):
                    for url in [f"/page/{i}" for i in range(7)]:
                        await q.put(url)

                async def worker(name, q, results):
                    while True:
                        url = await q.get()
                        try:
                            await asyncio.sleep(0.01)
                            results.append((name, url))
                        finally:
                            q.task_done()

                async def main():
                    q, results = asyncio.Queue(maxsize=3), []
                    workers = [asyncio.create_task(worker(f"w{i}", q, results)) for i in range(3)]
                    await producer(q)
                    await q.join()
                    for w in workers:
                        w.cancel()
                    await asyncio.gather(*workers, return_exceptions=True)
                    print(len(results), "pages;", sorted({n for n, _ in results}))

                asyncio.run(main())
            """),
        ],
        ["asyncio.run(main())", "async with asyncio.TaskGroup() as tg: tg.create_task(c())", "await asyncio.gather(*coros, return_exceptions=True)", "async with asyncio.timeout(5): ... · asyncio.wait_for(c, 5)", "asyncio.Semaphore(10) · asyncio.Queue(maxsize) · asyncio.to_thread(f)"],
        ["Calling a coroutine without await creates it but never runs it.", "Fire-and-forget create_task without keeping a reference can be garbage collected.", "Swallowing CancelledError breaks cancellation and timeouts.", "Blocking calls (requests, time.sleep, heavy CPU) freeze every task on the loop."],
        [
            qa("intermediate", "gather vs TaskGroup?", "gather runs awaitables concurrently and returns results in order; by default the first exception propagates but other tasks keep running. TaskGroup provides structured concurrency: on failure it cancels remaining tasks and raises an ExceptionGroup, and it never leaks tasks beyond its block."),
            qa("advanced", "How do you limit concurrency in asyncio?", "Wrap the critical section in async with semaphore where semaphore = asyncio.Semaphore(n), or use a fixed number of worker tasks consuming an asyncio.Queue. Both keep at most n operations in flight."),
            qa("advanced", "How do you call blocking code from async code?", "Use await asyncio.to_thread(func, *args) or loop.run_in_executor(pool, func) so the call runs in a thread (or process pool for CPU work) while the event loop keeps serving other tasks."),
            qa("advanced", "How does cancellation work?", "task.cancel() raises CancelledError inside the coroutine at its next await. Code should clean up in finally and re-raise; timeouts are implemented by cancelling, so swallowing CancelledError breaks them."),
        ],
        ["async-await", "concurrent-futures", "contextlib-advanced"],
        chain(
            ("asyncio.run", "event loop", "Start", "asyncio.run creates the loop and runs the main coroutine."),
            ("create_task", "schedule", "Spawn", "Coroutines become Tasks scheduled on the loop.", "coro"),
            ("await I/O", "suspend", "Yield control", "At an await on I/O or sleep, the task suspends and the loop runs others.", "task"),
            ("Ready", "callback", "Resume", "When the I/O completes, the loop resumes the waiting task.", "event"),
            ("Gather", "TaskGroup", "Join", "Results and errors are collected when all tasks finish.", "result"),
        ),
    ),
]

SCENARIOS = [
    {"level": "intermediate", "topic": "numbers-floats", "q": "Invoice totals are off by a cent for some customers compared with the accounting system.", "a": "Prices are computed with binary floats and rounded with round(), which uses banker's rounding. Switch to Decimal constructed from strings, quantize to cents with ROUND_HALF_UP at defined points, and store amounts as Decimal or integer cents."},
    {"level": "advanced", "topic": "datetime-timezones", "q": "A daily report job runs an hour early for half the year.", "a": "The schedule uses naive datetimes or fixed UTC offsets, so DST shifts the local time. Store the IANA zone (zoneinfo), compute the next local run time in that zone, convert to UTC for the scheduler, and use aware datetimes everywhere."},
    {"level": "intermediate", "topic": "security-basics", "q": "A security review finds password reset tokens generated with random.randint and passwords stored as sha256(password).", "a": "random is predictable; generate tokens with secrets.token_urlsafe and store only their hash with an expiry. Replace the fast unsalted hash with a salted KDF (argon2id, bcrypt or hashlib.scrypt), rehashing users on their next login."},
    {"level": "advanced", "topic": "memory-gc", "q": "A long-running worker's memory grows steadily until it is OOM-killed.", "a": "Something keeps references alive: an unbounded dict or lru_cache, growing lists, stored exceptions with tracebacks, or reference cycles with __del__. Compare tracemalloc snapshots over time, inspect referrers, bound caches (maxsize, TTL, WeakValueDictionary) and break cycles."},
    {"level": "intermediate", "topic": "logging-module", "q": "After adding a library, every log line appears twice and some lines appear in a different format.", "a": "Handlers are attached at multiple levels (or the library calls basicConfig), so records propagate to two handlers. Configure handlers only once at the application root, set propagate=False where you attach a dedicated handler, and make libraries use NullHandler."},
    {"level": "advanced", "topic": "asyncio-patterns", "q": "An async service that calls a partner API starts getting 429 Too Many Requests and timeouts under load.", "a": "Unbounded gather fires every request at once. Cap in-flight calls with an asyncio.Semaphore or a fixed worker pool over an asyncio.Queue, add asyncio.timeout deadlines and retries with exponential backoff and jitter, and honor Retry-After headers."},
]
