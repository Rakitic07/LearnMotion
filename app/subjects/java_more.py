"""More java topics, appended to the core module."""

from ._dsl import chain, ex, qa, topic

CATEGORIES = [
    {"id": "language", "title": "Language Deep Dive", "color": "rose", "blurb": "Types, strings, equality, enums and annotations."},
    {"id": "ecosystem", "title": "Ecosystem & Security", "color": "slate", "blurb": "Build, test, Spring, JDBC, patterns and crypto."},
]


def jx(title, level, description, src):
    return ex(title, level, description, "java", src, runnable=False)


_LANGUAGE = [
    topic(
        id="primitives-wrappers", title="Primitives, Wrappers & Autoboxing", category="language", level="basic", code="PW",
        tagline="Eight primitive types, their wrapper classes and the hidden cost of boxing.",
        analogy="A primitive is cash in your pocket; a wrapper is the same cash sealed in an envelope with a label. Envelopes can go into filing cabinets (collections) and can be empty (null), but opening them every time is slower.",
        what="Java has eight primitive types: byte, short, int, long, float, double, char and boolean. They hold values directly, live in local variables or inside objects, and cannot be null. Each has a wrapper class (Integer, Long, Double...) because generics and collections only work with objects. Since Java 5 the compiler inserts autoboxing (Integer.valueOf) and unboxing (intValue) automatically. Integer.valueOf caches values from -128 to 127, which is why == on small boxed values seems to work and then fails for larger ones. Unboxing a null wrapper throws NullPointerException. Primitive specialisations such as IntStream and arrays like int[] avoid boxing overhead in hot paths.",
        use_cases=["Counting and arithmetic in tight loops with int/long.", "Storing numbers in List<Integer> or Map<String, Long>.", "Representing an optional numeric column (Integer can be null).", "Choosing BigDecimal for money instead of double."],
        key_points=[
            "Compare wrappers with equals or unbox first; never with ==.",
            "Integer cache covers -128..127 (upper bound tunable with -XX:AutoBoxCacheMax).",
            "Integer overflow wraps silently; use Math.addExact to detect it.",
            "double is binary floating point: 0.1 + 0.2 != 0.3. Use BigDecimal for money.",
            "Prefer IntStream, LongStream and primitive arrays for large numeric workloads.",
        ],
        examples=[
            jx("The == trap with boxed values", "basic", "Works for small numbers, breaks for large ones.", """
                Integer a = 127, b = 127;
                System.out.println(a == b);        // true  (cached instances)
                Integer c = 128, d = 128;
                System.out.println(c == d);        // false (two different objects)
                System.out.println(c.equals(d));   // true
                int e = c;                         // unboxing: c.intValue()
            """),
            jx("Null unboxing and overflow", "intermediate", "Two silent failures and how to guard them.", """
                Map<String, Integer> stock = new HashMap<>();
                // int qty = stock.get("apple");          // NullPointerException on unboxing
                int qty = stock.getOrDefault("apple", 0);  // safe

                int big = Integer.MAX_VALUE;
                int wrapped = big + 1;                     // -2147483648, no error
                int checked = Math.addExact(big, 1);       // throws ArithmeticException
            """),
            jx("Avoid boxing in hot loops", "intermediate", "Stream<Integer> vs IntStream.", """
                List<Integer> nums = IntStream.range(0, 1_000_000).boxed().toList();
                long slow = nums.stream().reduce(0, Integer::sum);       // boxes every step
                long fast = IntStream.range(0, 1_000_000).asLongStream().sum(); // no boxing

                BigDecimal price = new BigDecimal("0.10").add(new BigDecimal("0.20"));
                System.out.println(price);   // 0.30 exactly
            """),
        ],
        commands=["Integer.valueOf(42) / intValue()", "Integer.parseInt(\"42\")", "Math.addExact(a, b)", "new BigDecimal(\"0.10\")", "-XX:AutoBoxCacheMax=1000"],
        gotchas=["Ternaries mixing int and Integer can unbox a null and throw NPE.", "List.remove(int index) vs remove(Object o): remove(1) removes by index on a List<Integer>.", "new Integer(5) is deprecated for removal since Java 9; use valueOf.", "new BigDecimal(0.1) captures the binary error; pass a String."],
        interview=[
            qa("basic", "Why does Java have both int and Integer?", "int is a primitive stored directly, cheap and never null. Integer is an object needed for generics, collections and nullability. Autoboxing (Java 5) converts between them automatically."),
            qa("basic", "Why can Integer == Integer return false?", "== compares references for objects. Integer.valueOf caches -128 to 127, so small values share instances, but larger values are distinct objects. Use equals or compare unboxed ints."),
            qa("intermediate", "When does autoboxing cause a NullPointerException?", "Whenever a null wrapper is unboxed: assigning map.get(k) to an int, arithmetic on a null Integer, or a ternary whose result type is primitive. Use getOrDefault or Optional to avoid it."),
            qa("intermediate", "Why not use double for money?", "double is binary floating point and cannot represent most decimal fractions exactly, so rounding errors accumulate. Use BigDecimal built from strings, or long cents, with explicit RoundingMode."),
        ],
        related=["collections", "generics", "lambdas-streams"],
        flow=chain(
            ("int 300", "primitive", "Primitive value", "The value sits directly in a local variable slot: no object, no null."),
            ("valueOf", "autobox", "Autoboxing", "Adding it to a List calls <b>Integer.valueOf(300)</b>; outside the cache this allocates.", "box"),
            ("Integer", "heap object", "Wrapper on heap", "The list holds a reference to an Integer object.", "ref"),
            ("intValue", "unbox", "Unboxing", "Reading it back into an int calls intValue(); a null reference throws NPE here.", "unbox"),
        ),
    ),
    topic(
        id="strings", title="Strings, StringBuilder & the String Pool", category="language", level="basic", code="ST",
        tagline="Immutable strings, interning, compact strings and efficient building.",
        analogy="A String is a printed page: you cannot erase it, only print a new one. StringBuilder is a whiteboard you keep editing and then photograph once at the end.",
        what="String is immutable and final: every concat, replace or toUpperCase returns a new object. String literals are interned in the string pool (on the heap since Java 7), so identical literals share one instance, while new String(\"x\") creates a separate object. Since Java 9 compact strings store Latin-1 text in one byte per char, and string concatenation with + compiles to invokedynamic (StringConcatFactory), which is efficient for single expressions. Inside loops, use StringBuilder to avoid creating many intermediate strings. Java 11 added isBlank, strip, lines and repeat; Java 12 added indent and transform; Java 15 text blocks. Always compare content with equals, never ==.",
        use_cases=["Building log lines, CSV rows or SQL with placeholders.", "Using strings as safe HashMap keys (immutable, cached hash).", "Parsing and cleaning user input with strip and split.", "Joining collections with String.join or Collectors.joining."],
        key_points=[
            "Immutability makes strings thread-safe and safe as map keys.",
            "== compares references; equals compares characters.",
            "StringBuilder in loops; + is fine in a single expression (Java 9+ indy concat).",
            "StringBuilder is not synchronized; StringBuffer is, and is rarely needed.",
            "strip() is Unicode-aware; trim() only removes chars <= U+0020.",
        ],
        examples=[
            jx("Pool, == and equals", "basic", "Why == sometimes appears to work.", """
                String a = "java";
                String b = "java";
                String c = new String("java");
                System.out.println(a == b);           // true  (same pooled literal)
                System.out.println(a == c);           // false (new object)
                System.out.println(a.equals(c));      // true
                System.out.println(a == c.intern());  // true
            """),
            jx("Building strings in a loop", "basic", "Quadratic copying vs one buffer.", """
                // Slow: creates a new String on every iteration
                String csv = "";
                for (String s : items) csv += s + ",";

                // Fast: one growing buffer
                StringBuilder sb = new StringBuilder(items.size() * 8);
                for (String s : items) sb.append(s).append(',');
                String out = sb.toString();

                // Simplest: String.join(",", items) or items.stream().collect(Collectors.joining(","))
            """),
            jx("Modern String API (11+)", "intermediate", "Helpers that replaced utility libraries.", """
                "  hi  ".isBlank();          // false
                "\\u2003hi ".strip();          // "hi" (Unicode whitespace)
                "ab".repeat(3);              // "ababab"
                "a\\nb\\nc".lines().count();    // 3
                "data".transform(s -> s + "!"); // Java 12
                String.format("%s=%d", "n", 3); // or "%s=%d".formatted("n", 3) in Java 15
            """),
        ],
        commands=["s.equals(t) / equalsIgnoreCase", "new StringBuilder().append(x)", "String.join(\",\", list)", "s.strip() · s.isBlank() (11+)", "\"%s\".formatted(x) (15+)"],
        gotchas=["Using == for string comparison passes tests with literals and fails with user input.", "substring no longer shares the backing array (since 7u6), so it copies.", "split takes a regex: split(\".\") returns an empty array; use split(\"\\\\.\").", "Strings holding passwords linger in memory; prefer char[] and clear it."],
        interview=[
            qa("basic", "Why are Strings immutable in Java?", "Immutability allows safe sharing via the string pool, makes strings thread-safe without locking, lets the hash code be cached for fast map lookups, and prevents security issues where a validated value (like a file path) is changed afterwards."),
            qa("basic", "String vs StringBuilder vs StringBuffer?", "String is immutable. StringBuilder is a mutable, unsynchronized buffer for building text efficiently. StringBuffer is the older synchronized version; it is rarely useful because builders are almost always thread-confined."),
            qa("intermediate", "What is the string pool and intern()?", "A JVM-wide table of unique string instances. Literals are interned automatically; intern() returns the pooled copy of any string. Since Java 7 the pool lives on the heap and can be garbage collected."),
            qa("advanced", "What are compact strings?", "Since Java 9 (JEP 254), String stores characters in a byte[] with a coder flag: Latin-1 strings use one byte per char and others use UTF-16. This roughly halves memory for typical ASCII-heavy applications without API changes."),
        ],
        related=["primitives-wrappers", "text-blocks", "memory-gc"],
        flow=chain(
            ("\"java\"", "literal", "Literal", "The compiler records the literal in the class constant pool."),
            ("String pool", "interned", "Interned", "On first use the JVM interns it; later identical literals reuse the same instance.", "intern"),
            ("concat", "new String", "Concatenation", "a + b creates a new String; the originals never change.", "copy"),
            ("Builder", "mutable buffer", "StringBuilder", "In loops, append into one buffer and call toString() once.", "append"),
        ),
    ),
    topic(
        id="text-blocks", title="Text Blocks", category="language", level="basic", code="TB",
        tagline="Multi-line string literals with triple quotes (Java 15).",
        analogy="Instead of dictating a letter one line at a time with 'new line, quote, plus', you hand over the whole page exactly as it looks.",
        what="Text blocks, previewed in Java 13 and final in Java 15 (JEP 378), are multi-line string literals delimited by three double quotes. The opening delimiter must be followed by a line break. The compiler strips incidental indentation, determined by the least-indented line including the closing delimiter, and normalises line endings to \\n. Escapes still work, plus two new ones: a backslash at line end joins lines, and \\s keeps a trailing space. Text blocks produce ordinary String objects, so they work with formatted() and every String method. They are ideal for JSON, SQL, HTML and test fixtures, but they do not perform interpolation; use formatted() or parameters.",
        use_cases=["Embedding JSON payloads in tests.", "Readable multi-line SQL with ? placeholders.", "HTML or email templates.", "Expected output in snapshot tests."],
        key_points=[
            "Opening \"\"\" must be followed by a newline.",
            "Position of the closing delimiter controls the stripped indentation.",
            "\\ at end of line suppresses the newline; \\s preserves a space.",
            "No interpolation: use .formatted(...) (Java 15).",
        ],
        examples=[
            jx("Before and after (Java 8 vs 15)", "basic", "Same JSON, two styles.", r'''
                // Java 8
                String json8 = "{\n" +
                               "  \"name\": \"Ada\",\n" +
                               "  \"lang\": \"java\"\n" +
                               "}";

                // Java 15+
                String json15 = """
                    {
                      "name": "Ada",
                      "lang": "java"
                    }
                    """;
            '''),
            jx("SQL with placeholders", "basic", "Readable query, still parameterised.", '''
                String sql = """
                    SELECT id, email
                    FROM customers
                    WHERE country = ?
                      AND created_at > ?
                    ORDER BY id
                    """;
                try (PreparedStatement ps = conn.prepareStatement(sql)) {
                    ps.setString(1, country);
                    ps.setObject(2, since);
                }
            '''),
            jx("Escapes and formatting", "intermediate", "Line joining, trailing spaces, formatted().", r'''
                String oneLine = """
                    a very long sentence that \
                    continues here""";            // no newline inserted

                String padded = """
                    name:\s
                    """;                          // keeps the trailing space

                String greeting = """
                    Hello %s, you have %d new messages.
                    """.formatted("Ada", 3);
            '''),
        ],
        commands=['String s = """\\n  ...\\n  """;', "s.formatted(args) (15+)", "s.stripIndent() (15+)", "s.translateEscapes() (15+)"],
        gotchas=["Putting text on the same line as the opening \"\"\" is a compile error.", "Moving the closing delimiter left adds indentation to every line.", "Concatenating user input into a text-block SQL still causes injection; use placeholders."],
        interview=[
            qa("basic", "What problem do text blocks solve?", "They remove the noise of escaped quotes, \\n and + concatenation when writing multi-line strings, making JSON, SQL and HTML readable. They became final in Java 15."),
            qa("intermediate", "How is indentation handled?", "The compiler finds the minimum indentation across non-blank lines and the closing delimiter, removes that common prefix, and strips trailing whitespace. You control the result by where you place the closing \"\"\"."),
            qa("intermediate", "Do text blocks support interpolation?", "No. They produce a normal String constant. Use formatted(), String.format or MessageFormat; string templates were previewed in 21-22 and then withdrawn."),
            qa("basic", "What do the \\ and \\s escapes do in a text block?", "A backslash at the end of a line joins it with the next line without a newline. \\s is a single space that is not stripped as trailing whitespace."),
        ],
        related=["strings", "java-versions"],
        flow=chain(
            ("Source", "triple quotes", "Write the block", "Text is written as it should look, indented with the code."),
            ("Strip indent", "common prefix", "Incidental indent", "The compiler removes the shared indentation and trailing spaces.", "strip"),
            ("Escapes", "\\n \\s \\", "Process escapes", "Escape sequences are interpreted after stripping.", "escape"),
            ("String", "constant", "Ordinary String", "The result is a normal interned String constant.", "String"),
        ),
    ),
    topic(
        id="var-inference", title="Local Variable Type Inference (var)", category="language", level="basic", code="VR",
        tagline="var lets the compiler infer local types (Java 10) without making Java dynamic.",
        analogy="Writing 'the usual' at a cafe where they know your order: the barista still makes exactly one specific drink; you just did not spell it out.",
        what="Java 10 (JEP 286) introduced var for local variables with an initialiser, enhanced for loops and try-with-resources. The compiler infers the static type from the right-hand side at compile time; the variable is still strongly typed and cannot later hold a different type. Java 11 allowed var in lambda parameters so they can carry annotations. var is not allowed for fields, method parameters, return types, or without an initialiser, and var x = null does not compile. It shines when the type is obvious or very long (generic maps, iterators), and hurts readability when the right side hides the type, such as var result = service.process(). var is a reserved type name, not a keyword, so existing variables named var still compile.",
        use_cases=["Shortening long generic declarations.", "Loop variables over entries of a Map.", "try-with-resources with verbose resource types.", "Annotating lambda parameters: (@NonNull var s) -> ..."],
        key_points=[
            "Inference happens at compile time; types are still static.",
            "Only for locals with initialisers, for loops and lambda params (11).",
            "var list = new ArrayList<>() infers ArrayList<Object>: give a type argument.",
            "Use when the type is obvious from the right side.",
        ],
        examples=[
            jx("Before and after", "basic", "Java 8 verbosity vs Java 10.", """
                // Java 8
                Map<String, List<Order>> byCustomer8 = new HashMap<String, List<Order>>();
                for (Map.Entry<String, List<Order>> e : byCustomer8.entrySet()) { }

                // Java 10+
                var byCustomer = new HashMap<String, List<Order>>();
                for (var e : byCustomer.entrySet()) {
                    String customer = e.getKey();
                    int count = e.getValue().size();
                }
            """),
            jx("Where var is not allowed", "intermediate", "Compile errors worth knowing.", """
                class Bad {
                    // var field = 1;                  // error: not for fields
                    // var method() { return 1; }      // error: not for return types
                    void m() {
                        // var x;                      // error: needs initialiser
                        // var n = null;               // error: cannot infer
                        // var arr = {1, 2};           // error: array initialiser needs type
                        var ok = new int[]{1, 2};      // fine
                        var list = new ArrayList<String>(); // ArrayList<String>
                    }
                }
            """),
            jx("var in lambdas (Java 11)", "intermediate", "Allows annotations on implicit params.", """
                BiFunction<String, String, String> join = (var a, var b) -> a + b;
                Consumer<String> c = (@Deprecated var s) -> System.out.println(s);

                try (var in = Files.newBufferedReader(Path.of("app.log"))) {
                    in.lines().filter(l -> l.contains("ERROR")).forEach(System.out::println);
                }
            """),
        ],
        commands=["var x = expr; (10+)", "for (var e : map.entrySet())", "(var a, var b) -> a + b (11+)", "try (var in = ...)"],
        gotchas=["Diamond with var infers Object: var l = new ArrayList<>() is ArrayList<Object>.", "var with numeric literals: var n = 1 is int, so later n = 3_000_000_000L will not compile.", "Hiding the type of a method result hurts code review readability."],
        interview=[
            qa("basic", "Does var make Java dynamically typed?", "No. The compiler infers a single static type at compile time and the variable keeps it. Assigning a value of another type later is a compile error."),
            qa("basic", "Where can var be used?", "Local variables with initialisers, enhanced for and classic for loop indexes, try-with-resources variables, and lambda parameters (Java 11). Not fields, parameters of methods, return types or catch parameters."),
            qa("intermediate", "What does var list = new ArrayList<>() infer?", "ArrayList<Object>, because the diamond has nothing to infer from. Write new ArrayList<String>() or declare the type explicitly."),
            qa("intermediate", "Why allow var in lambda parameters if they are already inferred?", "Java 11 (JEP 323) allowed it so implicitly typed parameters can carry annotations or modifiers like final, which requires a type position."),
        ],
        related=["generics", "lambdas-streams", "java-versions"],
        flow=chain(
            ("var x = ...", "declaration", "Declare", "You write var with an initialiser."),
            ("javac", "infers type", "Infer", "The compiler takes the static type of the right-hand expression.", "type"),
            ("Static type", "fixed", "Fixed type", "x now has that exact type; later assignments must match.", "HashMap<..>"),
            ("Bytecode", "same as explicit", "No runtime cost", "Generated bytecode is identical to writing the type explicitly.", "class"),
        ),
    ),
    topic(
        id="switch-expressions", title="Switch Expressions", category="language", level="intermediate", code="SW",
        tagline="Arrow labels, yield and exhaustive switch that returns a value (Java 14).",
        analogy="An old switch is a building with stairs between floors: miss a 'break' landing and you fall to the next floor. A switch expression is an elevator: press a button, arrive at exactly one floor.",
        what="Switch expressions were previewed in Java 12-13 and finalised in Java 14 (JEP 361). Case labels can use the arrow form case X -> ..., which never falls through, and several constants can share one label separated by commas. A switch can now be an expression that produces a value; block bodies return it with yield. Switch expressions must be exhaustive: for enums every constant must be covered or a default given, and the compiler checks it. Java 21 extended switch with type patterns, record patterns, guards (when) and case null. The classic colon form still exists and still falls through, so mixing styles in one switch is not allowed.",
        use_cases=["Mapping enum values to labels or prices.", "Replacing long if-else chains on a single value.", "Computing a value in one expression and assigning it to a final variable.", "Dispatching on sealed types with patterns (Java 21)."],
        key_points=[
            "Arrow cases never fall through; no break needed.",
            "case A, B -> groups labels.",
            "yield returns a value from a block body.",
            "Expressions must be exhaustive; the compiler enforces it.",
            "Java 21 adds patterns, when guards and case null.",
        ],
        examples=[
            jx("Java 8 vs Java 14", "basic", "Same logic, without fall-through risk.", """
                // Java 8 statement
                int days8;
                switch (month) {
                    case FEBRUARY: days8 = 28; break;
                    case APRIL: case JUNE: case SEPTEMBER: case NOVEMBER: days8 = 30; break;
                    default: days8 = 31;
                }

                // Java 14 expression
                int days = switch (month) {
                    case FEBRUARY -> 28;
                    case APRIL, JUNE, SEPTEMBER, NOVEMBER -> 30;
                    default -> 31;
                };
            """),
            jx("yield in block bodies", "intermediate", "Multi-statement branches.", """
                String label = switch (status) {
                    case ACTIVE -> "Active";
                    case SUSPENDED -> {
                        log.info("suspended account {}", id);
                        yield "Suspended";
                    }
                    case CLOSED -> "Closed";
                };   // no default: every enum constant is covered
            """),
            jx("Pattern switch (Java 21)", "advanced", "Type patterns, guards and null.", """
                static String describe(Object o) {
                    return switch (o) {
                        case null -> "null";
                        case Integer i when i > 100 -> "big int " + i;
                        case Integer i -> "int " + i;
                        case String s -> "string of length " + s.length();
                        default -> "other " + o.getClass().getSimpleName();
                    };
                }
            """),
        ],
        commands=["case A, B -> value", "yield value;", "case Type t when cond -> (21+)", "case null, default -> (21+)"],
        gotchas=["Adding an enum constant breaks compilation of exhaustive switches without default: that is a feature.", "A classic switch on a null reference throws NPE unless case null is present (21+).", "You cannot mix arrow and colon labels in one switch."],
        interview=[
            qa("basic", "What is the difference between a switch statement and a switch expression?", "A statement performs actions; an expression evaluates to a value that can be assigned or returned. Expressions (Java 14) must be exhaustive and use arrow cases or yield."),
            qa("intermediate", "What does yield do?", "It returns a value from a block body inside a switch expression, similar to return for a method. It is needed because a block has several statements and no implicit result."),
            qa("intermediate", "How does exhaustiveness work with enums?", "If every constant is covered, no default is needed; the compiler inserts a hidden default that throws MatchException (IncompatibleClassChangeError before 21) if a new constant appears at runtime from separate compilation."),
            qa("advanced", "What did Java 21 add to switch?", "Pattern matching for switch (JEP 441): type patterns, record patterns, when guards, case null, and exhaustiveness checking over sealed hierarchies."),
        ],
        related=["pattern-matching", "records-sealed", "enums"],
        flow=chain(
            ("selector", "value or object", "Evaluate selector", "The switch evaluates its selector once."),
            ("match case", "top to bottom", "Find a match", "Labels and patterns are checked in order; guards filter further.", "test"),
            ("arrow body", "no fall-through", "Run one branch", "Only the matching branch runs; there is no fall-through.", "->"),
            ("result", "yield value", "Produce value", "The expression yields one value, guaranteed by exhaustiveness.", "value"),
        ),
    ),
    topic(
        id="equals-hashcode", title="The equals and hashCode Contract", category="language", level="intermediate", code="EH",
        tagline="Rules that keep HashMap, HashSet and caches working correctly.",
        analogy="A library catalogue: hashCode decides which shelf a book goes on, equals checks if it is the exact book. If two copies of the same book are filed on different shelves, the librarian will never find the second one.",
        what="Object.equals defaults to reference identity and hashCode to an identity-based number. When a class defines logical equality, it must override both. The equals contract requires reflexivity, symmetry, transitivity, consistency and x.equals(null) == false. The hashCode contract requires that equal objects produce equal hash codes; unequal objects may collide, but fewer collisions mean faster maps. Fields used in equals must be the same as, or a superset of, those used in hashCode, and should be immutable, otherwise an object mutated after insertion becomes unreachable in a HashSet. Inheritance makes symmetric equals hard; prefer final classes or composition. Records (Java 16) generate correct equals, hashCode and toString from their components.",
        use_cases=["Value objects used as HashMap keys.", "Deduplicating entities with a HashSet.", "Comparing DTOs in unit tests.", "Cache keys composed of several fields."],
        key_points=[
            "Override both or neither.",
            "Equal objects must have equal hash codes; the reverse is not required.",
            "Base equality on immutable fields.",
            "Use Objects.equals / Objects.hash, or let records generate them.",
            "getClass() vs instanceof: choose deliberately for subclass behaviour.",
        ],
        examples=[
            jx("Broken key: equals without hashCode", "basic", "The map cannot find the entry.", """
                class Point {
                    final int x, y;
                    Point(int x, int y) { this.x = x; this.y = y; }
                    @Override public boolean equals(Object o) {
                        return o instanceof Point p && p.x == x && p.y == y;
                    }
                    // hashCode missing: identity hash used
                }
                Set<Point> set = new HashSet<>();
                set.add(new Point(1, 2));
                set.contains(new Point(1, 2));   // false (different buckets)
            """),
            jx("Correct implementation and the record shortcut", "intermediate", "Hand-written vs Java 16.", """
                public final class Sku {
                    private final String vendor;
                    private final int number;
                    public Sku(String vendor, int number) { this.vendor = vendor; this.number = number; }

                    @Override public boolean equals(Object o) {
                        if (this == o) return true;
                        if (!(o instanceof Sku other)) return false;
                        return number == other.number && vendor.equals(other.vendor);
                    }
                    @Override public int hashCode() { return 31 * vendor.hashCode() + number; }
                }

                record SkuRecord(String vendor, int number) {}   // same semantics, generated
            """),
            jx("Mutating a key", "advanced", "Why key fields must be immutable.", """
                class Tag { String name; Tag(String n) { name = n; }
                    public boolean equals(Object o) { return o instanceof Tag t && t.name.equals(name); }
                    public int hashCode() { return name.hashCode(); } }

                Set<Tag> tags = new HashSet<>();
                Tag t = new Tag("java");
                tags.add(t);
                t.name = "kotlin";          // hash changes, entry stays in the old bucket
                tags.contains(t);           // false
                tags.remove(t);             // false: a leak that never goes away
            """),
        ],
        commands=["Objects.equals(a, b)", "Objects.hash(f1, f2)", "record Key(String a, int b) {} (16+)", "System.identityHashCode(o)"],
        gotchas=["Using mutable fields (or JPA-generated ids that change on persist) in hashCode.", "equals(Foo other) overloads instead of overriding equals(Object).", "Mixing getClass() and instanceof checks across a hierarchy breaks symmetry.", "Arrays use identity equals: use Arrays.equals and Arrays.hashCode for array fields."],
        interview=[
            qa("basic", "What is the equals/hashCode contract?", "If a.equals(b) then a.hashCode() == b.hashCode(). equals must be reflexive, symmetric, transitive, consistent, and return false for null. Unequal objects may share a hash code."),
            qa("intermediate", "What happens if you override equals but not hashCode?", "Two logically equal objects get different identity hash codes, land in different buckets, and hash-based collections fail to find or deduplicate them."),
            qa("intermediate", "instanceof or getClass() in equals?", "instanceof allows subclasses to be equal to the parent, which can break symmetry if subclasses add state. getClass() is strict but violates Liskov substitution. The cleanest option is final classes or records."),
            qa("advanced", "Why is 31 commonly used in hashCode?", "It is an odd prime that spreads values well, and 31 * x can be optimised to (x << 5) - x. Objects.hash uses the same scheme, but allocates a varargs array."),
        ],
        related=["oop-basics", "collections", "records-sealed"],
        flow=chain(
            ("put(key)", "insert", "Insert", "The map needs to store the key."),
            ("hashCode()", "bucket index", "Pick bucket", "hashCode decides the bucket.", "hash"),
            ("equals()", "compare in bucket", "Compare", "Within the bucket, equals finds the exact key.", "equals"),
            ("get(key)", "same path", "Lookup", "Lookups repeat both steps; a mismatched hashCode searches the wrong bucket.", "lookup"),
        ),
    ),
    topic(
        id="comparable-comparator", title="Comparable vs Comparator", category="language", level="basic", code="CC",
        tagline="Natural ordering vs pluggable ordering, and the Java 8 comparator combinators.",
        analogy="Comparable is a book's built-in page number: there is one natural order. Comparator is a librarian who can sort the same books by author, date or size on request.",
        what="Comparable<T> defines a class's natural ordering via compareTo, used by Collections.sort, TreeMap and TreeSet when no comparator is given. Comparator<T> is a separate strategy object with compare(a, b), so one class can be sorted many ways. Both return negative, zero or positive. Java 8 added fluent factories and combinators: Comparator.comparing, thenComparing, reversed, nullsFirst and comparingInt to avoid boxing. Ordering should be consistent with equals, otherwise a TreeSet treats compare-equal elements as duplicates. Never implement compare by subtracting ints, as overflow flips the sign; use Integer.compare.",
        use_cases=["Sorting employees by department then salary.", "Natural ordering for value types like Money or Version.", "TreeMap with case-insensitive keys.", "Top-N queries with a PriorityQueue."],
        key_points=[
            "Comparable: one natural order inside the class.",
            "Comparator: external, composable, many orders.",
            "Use Integer.compare, not a - b.",
            "Keep compareTo consistent with equals for sorted sets and maps.",
        ],
        examples=[
            jx("Natural ordering", "basic", "Implement Comparable for a value type.", """
                record Version(int major, int minor) implements Comparable<Version> {
                    @Override public int compareTo(Version o) {
                        int c = Integer.compare(major, o.major);
                        return c != 0 ? c : Integer.compare(minor, o.minor);
                    }
                }
                List<Version> vs = new ArrayList<>(List.of(new Version(2, 1), new Version(1, 9)));
                Collections.sort(vs);   // [1.9, 2.1]
            """),
            jx("Java 7 vs Java 8 comparators", "basic", "Anonymous class vs combinators.", """
                // Java 7
                Collections.sort(people, new Comparator<Person>() {
                    public int compare(Person a, Person b) { return a.getName().compareTo(b.getName()); }
                });

                // Java 8+
                people.sort(Comparator.comparing(Person::dept)
                        .thenComparing(Person::salary, Comparator.reverseOrder())
                        .thenComparing(Person::name, Comparator.nullsLast(String::compareTo)));
            """),
            jx("Overflow bug and TreeSet surprise", "intermediate", "Two classic mistakes.", """
                Comparator<Integer> broken = (a, b) -> a - b;            // overflows for large values
                Comparator<Integer> safe = Integer::compare;

                Set<String> s = new TreeSet<>(String.CASE_INSENSITIVE_ORDER);
                s.add("Java"); s.add("JAVA");
                System.out.println(s.size());   // 1: compare()==0 means duplicate
            """),
        ],
        commands=["Comparator.comparing(T::key)", ".thenComparing(...).reversed()", "Comparator.comparingInt(...)", "Comparator.nullsFirst(...)", "list.sort(cmp)"],
        gotchas=["reversed() applies to the whole chain built so far, not just the last key.", "Type inference fails on comparing(p -> p.name()).reversed(); add a type witness or use a method reference.", "Comparators inconsistent with equals make TreeSet and HashSet disagree."],
        interview=[
            qa("basic", "Comparable vs Comparator?", "Comparable is implemented by the class itself (compareTo) and defines its single natural order. Comparator is a separate object (compare) so you can define many orderings without changing the class."),
            qa("intermediate", "Why is return a - b a bad comparator?", "Integer subtraction can overflow, turning a large positive difference negative and producing wrong or inconsistent order. Use Integer.compare(a, b)."),
            qa("intermediate", "What does consistent with equals mean?", "compareTo returns 0 exactly when equals returns true. Sorted collections use compareTo for identity, so an inconsistent order makes TreeSet drop elements a HashSet would keep. BigDecimal is a known exception (2.0 vs 2.00)."),
            qa("basic", "How do you sort by multiple fields in Java 8+?", "Chain Comparator.comparing(first).thenComparing(second), optionally with reversed() or a reverseOrder() key comparator, and pass it to List.sort or stream sorted()."),
        ],
        related=["collections", "lambdas-streams", "equals-hashcode"],
        flow=chain(
            ("sort()", "needs order", "Sort request", "A sort or TreeMap needs to compare two elements."),
            ("Comparable", "natural", "Natural order", "Without a comparator it calls a.compareTo(b).", "compareTo"),
            ("Comparator", "pluggable", "Custom order", "With a comparator it calls cmp.compare(a, b).", "compare"),
            ("Ordered", "sorted result", "Result", "The sign of the result decides position; 0 means equal.", "-1/0/1"),
        ),
    ),
    topic(
        id="immutability", title="Immutability & Defensive Copies", category="language", level="intermediate", code="IM",
        tagline="Objects that never change are simpler, safer and thread-safe for free.",
        analogy="A signed contract: once printed and signed it never changes. If you need different terms, you sign a new contract instead of scribbling on the old one.",
        what="An immutable object's state cannot change after construction. To build one: make the class final (or use a record), make all fields private final, provide no setters, and defensively copy mutable inputs and outputs such as lists, arrays and Date. Immutable objects are inherently thread-safe, can be shared and cached freely, and make reliable map keys. Java offers String, the boxed types, java.time classes, records (16) and unmodifiable collections from List.of (9) and List.copyOf (10). Collections.unmodifiableList returns a read-only view, not a copy: changes to the backing list are still visible. 'Withers' return modified copies, and for large objects the cost of copying is usually smaller than the cost of debugging shared mutable state.",
        use_cases=["Value objects: Money, Address, DateRange.", "Configuration shared across threads.", "Cache keys and map keys.", "Event and message payloads."],
        key_points=[
            "final class, private final fields, no setters.",
            "Copy mutable inputs in the constructor and outputs in getters.",
            "List.copyOf (10) makes a true immutable copy; unmodifiableList is only a view.",
            "final on a reference does not make the referenced object immutable.",
            "Records are shallowly immutable: copy mutable components in the compact constructor.",
        ],
        examples=[
            jx("Hand-written immutable class", "basic", "Classic recipe.", """
                public final class Team {
                    private final String name;
                    private final List<String> members;

                    public Team(String name, List<String> members) {
                        this.name = Objects.requireNonNull(name);
                        this.members = List.copyOf(members);   // Java 10: defensive, immutable copy
                    }
                    public String name() { return name; }
                    public List<String> members() { return members; }   // already immutable
                    public Team withMember(String m) {
                        var copy = new ArrayList<>(members);
                        copy.add(m);
                        return new Team(name, copy);
                    }
                }
            """),
            jx("Record with defensive copy", "intermediate", "Records are only shallowly immutable.", """
                public record Order(String id, List<String> lines) {
                    public Order {                      // compact constructor
                        Objects.requireNonNull(id);
                        lines = List.copyOf(lines);     // guard against caller mutation
                    }
                }
            """),
            jx("View vs copy", "intermediate", "unmodifiableList leaks changes.", """
                List<String> source = new ArrayList<>(List.of("a"));
                List<String> view = Collections.unmodifiableList(source);
                List<String> copy = List.copyOf(source);
                source.add("b");
                System.out.println(view);   // [a, b]  view sees the change
                System.out.println(copy);   // [a]     copy does not
                // view.add("c");            // UnsupportedOperationException
            """),
        ],
        commands=["List.of / Set.of / Map.of (9+)", "List.copyOf(coll) (10+)", "Collections.unmodifiableList(l)", "record R(...) {} (16+)", "stream.toList() (16+, unmodifiable)"],
        gotchas=["Returning an internal array or ArrayList lets callers mutate your object.", "java.util.Date and Calendar are mutable; use java.time.", "final fields can still be changed via reflection or deserialization if not guarded."],
        interview=[
            qa("basic", "How do you make a class immutable?", "Declare it final, make fields private final, set them only in the constructor, provide no setters, and defensively copy mutable fields on the way in and out. Or use a record and copy mutable components."),
            qa("intermediate", "Why are immutable objects thread-safe?", "Their state never changes after construction, and final fields have special JMM guarantees: once the constructor finishes (without leaking this), all threads see the initialised values without synchronization."),
            qa("intermediate", "unmodifiableList vs List.copyOf?", "Collections.unmodifiableList wraps the original and reflects later changes to it. List.copyOf (Java 10) creates an independent immutable copy (or returns the argument if it is already one) and rejects nulls."),
            qa("advanced", "Are records immutable?", "Shallowly: components are final and there are no setters, but a List component can still be mutated. Copy it with List.copyOf in the compact constructor to make the record deeply immutable."),
        ],
        related=["records-sealed", "collections", "concurrency"],
        flow=chain(
            ("Constructor", "validate", "Validate inputs", "Check nulls and invariants once, at construction."),
            ("Copy", "List.copyOf", "Defensive copy", "Copy mutable arguments so callers cannot change them later.", "copy"),
            ("final fields", "frozen", "Freeze", "Fields are final; the JMM publishes them safely.", "publish"),
            ("Share", "any thread", "Share freely", "The object can be cached, used as a key, and read by any thread.", "share"),
            ("withX()", "new instance", "Change = new object", "Modifications return a new instance.", "new"),
        ),
    ),
    topic(
        id="interface-methods", title="Interfaces & Abstract Classes", category="language", level="intermediate", code="IF",
        tagline="Default, static and private interface methods vs abstract base classes.",
        analogy="An interface is a job description listing what someone can do; since Java 8 it can include 'how we usually do it' notes. An abstract class is a half-built house: it already has walls (state) and you finish the rooms.",
        what="An interface declares a contract that classes implement; a class can implement many interfaces but extend only one class. Java 8 added default methods (bodies that implementers inherit, which let the JDK add stream() to Collection without breaking code) and static methods. Java 9 added private methods to share code between defaults. Interfaces still cannot hold instance state, only constants. An abstract class can have fields, constructors, protected members and abstract methods, and fits when subclasses share state or a template method. If a class inherits the same default method from two interfaces, it must override it and can call a specific one with X.super.method(). Sealed interfaces (17) restrict which classes may implement them.",
        use_cases=["Defining service contracts (Repository, PaymentGateway).", "Evolving a published interface with default methods.", "Template method pattern with an abstract base class.", "Functional interfaces for lambdas."],
        key_points=[
            "Interfaces: multiple inheritance of type and behaviour, no instance state.",
            "default (8), static (8) and private (9) interface methods.",
            "Abstract classes: state, constructors, single inheritance.",
            "Diamond conflict: override and pick with A.super.m().",
            "Class methods always win over interface defaults.",
        ],
        examples=[
            jx("Default, static and private methods", "basic", "Java 8 and 9 interface features.", """
                public interface Shape {
                    double area();

                    default String describe() {                 // Java 8
                        return name() + " with area " + format(area());
                    }
                    default String name() { return getClass().getSimpleName(); }

                    static Shape unitSquare() { return () -> 1.0; }   // Java 8

                    private String format(double d) {           // Java 9
                        return String.format("%.2f", d);
                    }
                }
            """),
            jx("Resolving the diamond", "intermediate", "Two defaults with the same signature.", """
                interface Walker  { default String move() { return "walk"; } }
                interface Swimmer { default String move() { return "swim"; } }

                class Duck implements Walker, Swimmer {
                    @Override public String move() {          // required: compile error otherwise
                        return Walker.super.move() + " and " + Swimmer.super.move();
                    }
                }
            """),
            jx("Abstract class as a template", "intermediate", "Shared state and a fixed algorithm.", """
                public abstract class Importer {
                    protected final Logger log = Logger.getLogger(getClass().getName());
                    private int imported;

                    public final void run(Path file) throws IOException {   // template method
                        for (String line : Files.readAllLines(file)) {
                            if (accept(line)) { save(parse(line)); imported++; }
                        }
                        log.info("imported " + imported);
                    }
                    protected boolean accept(String line) { return !line.isBlank(); }
                    protected abstract Record parse(String line);
                    protected abstract void save(Record r);
                }
            """),
        ],
        commands=["interface X { default void m() {} } (8+)", "static methods in interfaces (8+)", "private methods in interfaces (9+)", "X.super.m()", "sealed interface X permits A, B (17+)"],
        gotchas=["Default methods cannot override Object methods such as equals or toString.", "Adding a default method can still break implementers that already have a method with the same signature but different return type.", "Static interface methods are not inherited: call Shape.unitSquare(), not Square.unitSquare()."],
        interview=[
            qa("basic", "Interface vs abstract class?", "Interfaces define capabilities, support multiple inheritance and hold no instance state. Abstract classes can have fields, constructors and non-public members but allow only single inheritance. Use interfaces for contracts and abstract classes to share implementation and state."),
            qa("intermediate", "Why were default methods added in Java 8?", "To evolve interfaces without breaking existing implementations, mainly so Collection could gain stream(), forEach and removeIf. They also enable mixin-style behaviour."),
            qa("intermediate", "How is a default method conflict resolved?", "Rules: class methods win over defaults; a more specific interface wins over its parent; otherwise the class must override and may delegate with InterfaceName.super.method()."),
            qa("basic", "Can an interface have private methods?", "Yes, since Java 9. Private (and private static) methods let default methods share helper code without exposing it to implementers."),
        ],
        related=["oop-basics", "records-sealed", "functional-interfaces"],
        flow=chain(
            ("interface", "contract", "Contract", "The interface declares abstract methods every implementer must provide."),
            ("default", "Java 8", "Default body", "Default methods give a fallback implementation.", "inherit"),
            ("abstract cls", "state + template", "Shared state", "An abstract class can add fields and a template method.", "extend"),
            ("concrete", "implements", "Concrete class", "The concrete class fills in the gaps and can override defaults.", "override"),
        ),
    ),
    topic(
        id="enums", title="Enums in Depth", category="language", level="basic", code="EN",
        tagline="Type-safe constants with fields, methods, EnumMap and EnumSet.",
        analogy="Enums are like the fixed sizes on a coffee menu: small, medium, large. Nobody can order 'medium-ish', and each size can carry its own price and volume.",
        what="An enum (Java 5) declares a fixed set of named instances of a class. Each constant is a singleton created when the enum class initialises, so == comparison is safe. Enums can have fields, constructors (implicitly private), methods, and constant-specific bodies that override abstract methods. They can implement interfaces but cannot extend classes because they implicitly extend java.lang.Enum. values(), valueOf(String), name() and ordinal() are generated. EnumMap and EnumSet are array- and bitmask-backed collections that are much faster than HashMap and HashSet for enum keys. Enums work in switch, are serializable by name, and are the simplest correct way to write a singleton.",
        use_cases=["Order status, HTTP methods, days of the week.", "Strategy per constant (operation enums).", "State machines with allowed transitions.", "Thread-safe singletons."],
        key_points=[
            "Compare with ==; constants are singletons.",
            "Do not persist ordinal(): reordering breaks data. Persist name() or a code field.",
            "EnumSet/EnumMap are compact and fast.",
            "valueOf throws IllegalArgumentException for unknown names.",
        ],
        examples=[
            jx("Fields, constructor and lookup", "basic", "Rich enum with a safe parser.", """
                public enum Plan {
                    FREE(0), PRO(1_200), TEAM(4_900);

                    private final int monthlyCents;
                    Plan(int cents) { this.monthlyCents = cents; }
                    public int monthlyCents() { return monthlyCents; }

                    private static final Map<String, Plan> BY_NAME =
                        Arrays.stream(values()).collect(Collectors.toMap(p -> p.name().toLowerCase(), p -> p));

                    public static Optional<Plan> parse(String s) {
                        return Optional.ofNullable(BY_NAME.get(s.toLowerCase()));
                    }
                }
            """),
            jx("Constant-specific behaviour", "intermediate", "Each constant overrides a method.", """
                public enum Op implements IntBinaryOperator {
                    ADD("+") { public int applyAsInt(int a, int b) { return a + b; } },
                    MUL("*") { public int applyAsInt(int a, int b) { return a * b; } };

                    private final String symbol;
                    Op(String symbol) { this.symbol = symbol; }
                    public String symbol() { return symbol; }
                }
                int r = Op.MUL.applyAsInt(6, 7);   // 42
            """),
            jx("EnumSet, EnumMap and the singleton", "intermediate", "Efficient collections and a safe singleton.", """
                EnumSet<DayOfWeek> weekend = EnumSet.of(DayOfWeek.SATURDAY, DayOfWeek.SUNDAY);
                EnumMap<Plan, Integer> seats = new EnumMap<>(Plan.class);
                seats.merge(Plan.PRO, 1, Integer::sum);

                public enum Registry {
                    INSTANCE;
                    private final Map<String, String> data = new ConcurrentHashMap<>();
                    public void put(String k, String v) { data.put(k, v); }
                }
            """),
        ],
        commands=["Plan.values() / valueOf(\"PRO\")", "p.name() · p.ordinal()", "EnumSet.of(...) / allOf / range", "new EnumMap<>(Plan.class)", "switch (plan) { case PRO -> ... }"],
        gotchas=["Storing ordinal() in a database breaks when constants are reordered.", "valueOf is case-sensitive and throws on unknown input.", "Calling values() in a hot loop allocates a new array each time; cache it."],
        interview=[
            qa("basic", "Why use enums instead of int constants?", "Enums are type-safe (you cannot pass 7 where a Plan is expected), have readable names, can carry data and behaviour, and work with switch exhaustiveness and EnumSet/EnumMap."),
            qa("intermediate", "Why is an enum the best singleton?", "The JVM guarantees one instance per constant, initialised thread-safely on class init. Serialization and reflection cannot create extra instances, unlike a hand-written singleton."),
            qa("intermediate", "Why are EnumSet and EnumMap fast?", "EnumSet is a bit vector (a long for up to 64 constants) and EnumMap an array indexed by ordinal, so operations avoid hashing and are compact."),
            qa("basic", "Can an enum extend a class or implement an interface?", "It implicitly extends java.lang.Enum so it cannot extend another class, but it can implement any number of interfaces."),
        ],
        related=["oop-basics", "switch-expressions", "design-patterns"],
        flow=chain(
            ("enum Plan", "declaration", "Declare", "Constants are declared with optional constructor arguments."),
            ("class init", "once", "Create constants", "When Plan is first used, each constant is created exactly once.", "init"),
            ("singletons", "== safe", "Compare by ==", "Every reference to Plan.PRO is the same object.", "PRO"),
            ("EnumMap", "array by ordinal", "Fast collections", "EnumMap and EnumSet index by ordinal internally.", "index"),
        ),
    ),
    topic(
        id="annotations", title="Annotations", category="language", level="intermediate", code="AN",
        tagline="Metadata for the compiler, tools and frameworks: built-ins, custom and processing.",
        analogy="Sticky notes on documents. Some are read by the mail room on the way (compiler), some are thrown away after sorting (source retention), and some stay on the file for anyone who opens it later (runtime retention).",
        what="Annotations (Java 5) attach metadata to declarations and, since Java 8, to type uses. Built-ins include @Override, @Deprecated(since, forRemoval), @SuppressWarnings, @FunctionalInterface and @SafeVarargs. Custom annotations are declared with @interface and configured by meta-annotations: @Retention (SOURCE, CLASS, RUNTIME) controls how long they survive, @Target restricts where they may appear, plus @Inherited, @Documented and @Repeatable (8). Runtime-retained annotations are read via reflection, which is how Spring, JPA and JUnit wire behaviour. Annotation processors run at compile time (javac -processor) to generate code, as Lombok, MapStruct and Dagger do. Annotation elements may only be primitives, String, Class, enums, other annotations or arrays of these.",
        use_cases=["Compile-time checks with @Override and @FunctionalInterface.", "Framework configuration: @RestController, @Entity, @Test.", "Validation constraints like @NotNull and @Size.", "Code generation by annotation processors."],
        key_points=[
            "Retention: SOURCE (compiler only), CLASS (default, in bytecode), RUNTIME (reflective).",
            "@Target limits placement: TYPE, METHOD, FIELD, PARAMETER, TYPE_USE...",
            "Elements are constants: primitives, String, Class, enums, annotations, arrays.",
            "Annotations do nothing by themselves; something must read them.",
        ],
        examples=[
            jx("Declaring a custom annotation", "basic", "Meta-annotations control behaviour.", """
                @Retention(RetentionPolicy.RUNTIME)
                @Target(ElementType.METHOD)
                @Documented
                public @interface Timed {
                    String value() default "";
                    long warnAboveMillis() default 500;
                }

                class ReportService {
                    @Timed(value = "report.build", warnAboveMillis = 200)
                    public Report build() { return new Report(); }
                }
            """),
            jx("Reading it with reflection", "intermediate", "What a framework does under the hood.", """
                for (Method m : ReportService.class.getDeclaredMethods()) {
                    Timed t = m.getAnnotation(Timed.class);
                    if (t != null) {
                        long start = System.nanoTime();
                        m.invoke(service);
                        long ms = (System.nanoTime() - start) / 1_000_000;
                        if (ms > t.warnAboveMillis()) System.out.println(t.value() + " slow: " + ms + " ms");
                    }
                }
            """),
            jx("Built-ins and repeatable", "intermediate", "Java 8/9 improvements.", """
                @Deprecated(since = "3.2", forRemoval = true)   // Java 9 elements
                public void oldApi() { }

                @Repeatable(Schedules.class)
                @interface Schedule { String cron(); }
                @interface Schedules { Schedule[] value(); }

                @Schedule(cron = "0 0 * * *")
                @Schedule(cron = "0 12 * * *")                  // Java 8 repeatable
                void cleanup() { }
            """),
        ],
        commands=["@Retention(RetentionPolicy.RUNTIME)", "@Target(ElementType.METHOD)", "m.getAnnotation(X.class)", "javac -processor com.x.MyProcessor", "@Deprecated(forRemoval = true)"],
        gotchas=["Forgetting @Retention(RUNTIME) makes getAnnotation return null.", "@Inherited only works for class-level annotations, not methods or interfaces.", "Heavy reflection on annotations at request time is slow; cache the results."],
        interview=[
            qa("basic", "What are the retention policies?", "SOURCE annotations are discarded by the compiler (e.g. @Override). CLASS, the default, are stored in bytecode but not available reflectively. RUNTIME are available via reflection at runtime, which frameworks require."),
            qa("intermediate", "How do frameworks like Spring use annotations?", "They scan classes, read RUNTIME annotations via reflection or bytecode readers, and then register beans, create proxies, or map routes accordingly. Annotations are just markers; the framework supplies the behaviour."),
            qa("intermediate", "What is an annotation processor?", "A javax.annotation.processing.Processor that runs inside javac, inspects annotated elements, and can generate new source files or report errors. Lombok, MapStruct and Dagger use it to avoid runtime reflection."),
            qa("advanced", "What are type annotations?", "Java 8 (JSR 308) allows annotations wherever a type is used, e.g. List<@NonNull String> or casts. Checkers like the Checker Framework use them for pluggable type systems such as nullness analysis."),
        ],
        related=["reflection", "spring-boot", "junit-mockito"],
        flow=chain(
            ("@Timed", "declared", "Annotate", "The developer annotates a method."),
            ("javac", "SOURCE / CLASS", "Compile", "The compiler checks targets and can run annotation processors.", "process"),
            ("Bytecode", "RUNTIME kept", "Store", "RUNTIME annotations are stored in the class file attributes.", ".class"),
            ("Reflection", "getAnnotation", "Read", "A framework reads the annotation at startup.", "scan"),
            ("Behaviour", "proxy / route", "Apply", "The framework wraps or registers the method accordingly.", "wire"),
        ),
    ),
    topic(
        id="reflection", title="Reflection & Method Handles", category="language", level="advanced", code="RF",
        tagline="Inspect and invoke classes at runtime, and what modules changed about it.",
        analogy="Reflection is like reading a building's blueprints while standing inside it and then opening doors that have no handles. Powerful for maintenance crews (frameworks), risky for everyone else.",
        what="The java.lang.reflect API lets code discover classes, fields, methods and constructors at runtime and invoke them dynamically, starting from a Class object (Foo.class, obj.getClass() or Class.forName). setAccessible(true) bypasses access checks, but since Java 9 modules and especially Java 16-17 (strong encapsulation, JEP 403) it fails for JDK internals unless the package is opened with --add-opens. Reflection powers dependency injection, ORMs, serializers and test frameworks. It is slower than direct calls and defeats compile-time checking, so production code should cache Method objects or use MethodHandles (Java 7), which the JIT optimises better; since Java 18 core reflection itself is implemented on method handles (JEP 416). Records expose getRecordComponents (16) and sealed classes getPermittedSubclasses (17).",
        use_cases=["Dependency injection and bean wiring.", "Object mappers (JSON, JPA) reading fields.", "Plugin systems loading classes by name.", "Test utilities invoking private methods (sparingly)."],
        key_points=[
            "Class.forName, getDeclaredMethods, getDeclaredFields, newInstance via constructors.",
            "setAccessible(true) is restricted by modules since 9 and enforced since 16-17.",
            "Cache reflective lookups; prefer MethodHandles for hot paths.",
            "Class.newInstance() is deprecated (9); use getDeclaredConstructor().newInstance().",
            "Never load class names from untrusted input.",
        ],
        examples=[
            jx("Inspect and invoke", "intermediate", "Basic reflective calls.", """
                Class<?> type = Class.forName("com.example.Greeter");
                Object greeter = type.getDeclaredConstructor().newInstance();

                Method greet = type.getMethod("greet", String.class);
                Object result = greet.invoke(greeter, "Ada");

                for (Field f : type.getDeclaredFields()) {
                    System.out.println(f.getName() + " : " + f.getType().getSimpleName());
                }
            """),
            jx("MethodHandles (Java 7+)", "advanced", "Faster, type-checked dynamic invocation.", """
                MethodHandles.Lookup lookup = MethodHandles.lookup();
                MethodHandle length = lookup.findVirtual(String.class, "length", MethodType.methodType(int.class));
                int n = (int) length.invokeExact("reflection");    // 10

                // Records (Java 16): generic toString-like dump
                for (RecordComponent rc : Point.class.getRecordComponents()) {
                    System.out.println(rc.getName() + "=" + rc.getAccessor().invoke(point));
                }
            """),
            jx("Strong encapsulation (Java 16/17)", "advanced", "Why old libraries break on upgrade.", """
                Field f = String.class.getDeclaredField("value");
                f.setAccessible(true);   // Java 17: InaccessibleObjectException

                // Temporary bridge only, while upgrading the library:
                //   java --add-opens java.base/java.lang=ALL-UNNAMED -jar app.jar
                // Proper fix: use public APIs or open your own packages in module-info:
                //   opens com.example.model to com.fasterxml.jackson.databind;
            """),
        ],
        commands=["Class.forName(\"x.Y\")", "type.getDeclaredMethods()", "m.setAccessible(true)", "MethodHandles.lookup().findVirtual(...)", "--add-opens java.base/java.lang=ALL-UNNAMED"],
        gotchas=["InaccessibleObjectException after upgrading to Java 17 for libraries poking at JDK internals.", "Reflective invocation wraps exceptions in InvocationTargetException; unwrap getCause().", "Class.forName with user-controlled names enables gadget and injection attacks.", "Reflection does not see generic type arguments erased at runtime, except in signatures."],
        interview=[
            qa("intermediate", "What is reflection used for?", "Inspecting and manipulating classes at runtime without compile-time knowledge: dependency injection, ORMs, JSON mapping, test frameworks and plugin loading. Application code should rarely need it directly."),
            qa("advanced", "How did Java 9-17 change reflection?", "Modules restrict deep reflection to packages that are explicitly opened. Java 16 made strong encapsulation of JDK internals the default and 17 removed the --illegal-access switch, so setAccessible on JDK internals fails unless --add-opens is used."),
            qa("advanced", "Reflection vs MethodHandles?", "MethodHandles (Java 7) are typed, directly executable references checked at lookup time; the JIT can inline them, especially when stored in static final fields. Reflection checks access on every call and boxes arguments, so it is typically slower."),
            qa("intermediate", "Why is reflection considered risky?", "It bypasses encapsulation and compile-time type checks, breaks easily on refactoring, hurts performance, and when driven by untrusted input it can instantiate dangerous classes."),
        ],
        related=["annotations", "modules", "jvm-basics"],
        flow=chain(
            ("Class<?>", "forName / .class", "Get Class", "Start with a Class object for the type."),
            ("Lookup", "methods, fields", "Discover members", "getDeclaredMethods and friends list members.", "query"),
            ("Access check", "module + modifiers", "Check access", "Modules and modifiers decide if setAccessible is allowed.", "check"),
            ("invoke()", "dynamic call", "Invoke", "The method runs; exceptions arrive wrapped in InvocationTargetException.", "call"),
        ),
    ),
]

_CORE = [
    topic(
        id="optional", title="Optional", category="core", level="basic", code="OP",
        tagline="A container for a value that may be absent, designed for return types (Java 8).",
        analogy="A gift box that is either holding a present or clearly labelled 'empty'. You check the label instead of reaching in and getting bitten by a null.",
        what="java.util.Optional<T>, added in Java 8, represents a possibly missing result so that absence is visible in the method signature. Create one with Optional.of (non-null), ofNullable or empty, and consume it with map, flatMap, filter, orElse, orElseGet, orElseThrow and ifPresentOrElse (9). Java 9 also added or() and stream(), Java 10 orElseThrow() without arguments, and Java 11 isEmpty(). Optional is meant for return values; it is not Serializable and should not be used for fields, method parameters or collections. orElse evaluates its argument eagerly, while orElseGet takes a supplier and evaluates lazily. Primitive variants OptionalInt, OptionalLong and OptionalDouble avoid boxing.",
        use_cases=["Repository finders: findById returns Optional<User>.", "Chaining lookups that may each fail.", "Parsing configuration values with defaults.", "Stream terminal operations like findFirst and max."],
        key_points=[
            "Use for return types, not fields or parameters.",
            "Never call get() without a check; prefer orElseThrow().",
            "orElse is eager, orElseGet is lazy.",
            "Return an empty collection rather than Optional<List<T>>.",
            "An Optional reference itself must never be null.",
        ],
        examples=[
            jx("Null checks vs Optional", "basic", "Java 7 style vs Java 8 chain.", """
                // Java 7
                String city = "unknown";
                User u = repo.find(id);
                if (u != null && u.getAddress() != null && u.getAddress().getCity() != null) {
                    city = u.getAddress().getCity();
                }

                // Java 8+
                String city8 = repo.findById(id)
                        .map(User::getAddress)
                        .map(Address::getCity)
                        .orElse("unknown");
            """),
            jx("orElse vs orElseGet", "intermediate", "Eager vs lazy fallback.", """
                User user = cache.get(id)
                        .orElse(loadFromDatabase(id));        // ALWAYS calls the database

                User user2 = cache.get(id)
                        .orElseGet(() -> loadFromDatabase(id)); // only when empty

                User user3 = repo.findById(id)
                        .orElseThrow(() -> new NotFoundException("user " + id));
            """),
            jx("Java 9-11 additions", "intermediate", "or, ifPresentOrElse, stream, isEmpty.", """
                Optional<Config> cfg = fromEnv().or(() -> fromFile());          // 9
                cfg.ifPresentOrElse(this::apply, () -> log.warn("no config"));  // 9
                List<String> emails = users.stream()
                        .map(User::email)               // Optional<String>
                        .flatMap(Optional::stream)      // 9: drop empties
                        .toList();
                if (cfg.isEmpty()) { }                  // 11
            """),
        ],
        commands=["Optional.ofNullable(x)", "opt.map(f).orElse(d)", "opt.orElseGet(supplier)", "opt.orElseThrow() (10+)", "opt.ifPresentOrElse(a, b) (9+)"],
        gotchas=["Optional.of(null) throws NPE; use ofNullable.", "Using isPresent() + get() is just a verbose null check.", "Optional fields in JPA entities or DTOs complicate serialization."],
        interview=[
            qa("basic", "Why was Optional introduced?", "To make a possibly missing return value explicit in the API, forcing callers to handle absence instead of risking NullPointerException, and to allow fluent chaining with map and flatMap."),
            qa("intermediate", "orElse vs orElseGet?", "orElse(value) always evaluates its argument, even if the Optional has a value. orElseGet(supplier) only calls the supplier when empty, so use it for expensive defaults."),
            qa("intermediate", "Where should you not use Optional?", "Fields, method parameters, collection elements and serialized DTOs. It adds allocation, is not Serializable, and for collections an empty collection already expresses absence."),
            qa("basic", "map vs flatMap on Optional?", "map applies a function returning a plain value and wraps it. flatMap expects a function that already returns an Optional and avoids nesting Optional<Optional<T>>."),
        ],
        related=["lambdas-streams", "exceptions", "functional-interfaces"],
        flow=chain(
            ("findById", "may be absent", "Return Optional", "The method signals that the result may be missing."),
            ("map", "transform", "Transform", "map runs only when a value is present.", "value"),
            ("filter", "keep if", "Filter", "filter turns a value into empty if the predicate fails.", "test"),
            ("orElseThrow", "unwrap", "Unwrap", "Finally unwrap with a default or a meaningful exception.", "result"),
        ),
    ),
    topic(
        id="functional-interfaces", title="Functional Interfaces", category="core", level="intermediate", code="FI",
        tagline="Single-abstract-method types that lambdas target: Function, Supplier, Consumer, Predicate.",
        analogy="A power socket with one standard shape. Any appliance (lambda) with the matching plug (parameter and return types) can be plugged in.",
        what="A functional interface has exactly one abstract method, and a lambda or method reference can be used wherever one is expected. Java 8 added the java.util.function package with 43 interfaces: the core ones are Function<T,R>, BiFunction, Supplier<T>, Consumer<T>, Predicate<T>, UnaryOperator and BinaryOperator, plus primitive specialisations like IntPredicate and ToLongFunction that avoid boxing. Older interfaces such as Runnable, Callable and Comparator also qualify. The optional @FunctionalInterface annotation makes the compiler verify the single-method rule. Default methods such as andThen, compose, negate and and/or allow composition. Lambdas capture only effectively final local variables, and checked exceptions are not allowed by the standard interfaces, so you may need your own interface that declares throws.",
        use_cases=["Passing behaviour to APIs: retry(op), timed(task).", "Building validation rules with Predicate composition.", "Lazy values with Supplier.", "Custom callbacks and event handlers."],
        key_points=[
            "One abstract method; defaults and static methods do not count.",
            "Function, Supplier, Consumer, Predicate and their Bi/primitive variants.",
            "Compose with andThen, compose, and, or, negate.",
            "Captured locals must be effectively final.",
            "Standard interfaces cannot throw checked exceptions.",
        ],
        examples=[
            jx("The core four", "basic", "Shapes of the most used interfaces.", """
                Supplier<UUID> newId = UUID::randomUUID;              // () -> T
                Consumer<String> log = s -> System.out.println(s);    // T -> void
                Predicate<String> blank = String::isBlank;            // T -> boolean
                Function<String, Integer> len = String::length;       // T -> R

                log.accept(newId.get().toString());
                boolean ok = blank.negate().test("java");
                int n = len.andThen(x -> x * 2).apply("abc");         // 6
            """),
            jx("Composing predicates", "intermediate", "Reusable validation rules.", """
                Predicate<String> notBlank = s -> !s.isBlank();
                Predicate<String> shortEnough = s -> s.length() <= 64;
                Predicate<String> hasAt = s -> s.contains("@");

                Predicate<String> validEmail = notBlank.and(shortEnough).and(hasAt);
                List<String> valid = inputs.stream().filter(validEmail).toList();
                Predicate<String> invalid = Predicate.not(validEmail);    // Java 11
            """),
            jx("Your own interface with checked exceptions", "advanced", "Bridge lambdas and IOExceptions.", """
                @FunctionalInterface
                interface IoFunction<T, R> {
                    R apply(T t) throws IOException;

                    static <T, R> Function<T, R> unchecked(IoFunction<T, R> f) {
                        return t -> {
                            try { return f.apply(t); }
                            catch (IOException e) { throw new UncheckedIOException(e); }
                        };
                    }
                }
                List<String> contents = paths.stream().map(IoFunction.unchecked(Files::readString)).toList();
            """),
        ],
        commands=["Function<T,R> · apply", "Supplier<T> · get", "Consumer<T> · accept", "Predicate<T> · test · Predicate.not (11+)", "@FunctionalInterface"],
        gotchas=["Capturing a mutable local causes 'must be final or effectively final' errors; use an AtomicInteger or redesign.", "Using Function<Integer,Integer> instead of IntUnaryOperator boxes in hot paths.", "Overloads taking different functional interfaces can make lambda calls ambiguous."],
        interview=[
            qa("basic", "What is a functional interface?", "An interface with exactly one abstract method, which makes it a target for lambdas and method references. Examples: Runnable, Comparator, Function, Predicate."),
            qa("intermediate", "Supplier vs Consumer vs Function vs Predicate?", "Supplier takes nothing and returns a value; Consumer takes a value and returns nothing; Function maps a T to an R; Predicate tests a T and returns boolean."),
            qa("intermediate", "Why must captured variables be effectively final?", "Lambdas capture the value, not the variable, and may run later on another thread. Allowing mutation would create confusing semantics and data races, so the compiler forbids reassigning captured locals."),
            qa("advanced", "How do you use a lambda that throws a checked exception?", "Define your own functional interface whose method declares throws, then wrap it to rethrow as an unchecked exception (e.g. UncheckedIOException), or handle the exception inside the lambda."),
        ],
        related=["lambdas-streams", "method-references", "interface-methods"],
        flow=chain(
            ("Interface", "one abstract", "Define shape", "A functional interface fixes parameter and return types."),
            ("Lambda", "s -> s.trim()", "Write lambda", "The lambda body supplies the single method.", "body"),
            ("invokedynamic", "LambdaMetafactory", "Link", "At first call the JVM links an implementation class.", "indy"),
            ("Instance", "apply / test", "Call", "Callers invoke apply/test/accept; composition adds more steps.", "call"),
        ),
    ),
    topic(
        id="method-references", title="Method References", category="core", level="basic", code="MR",
        tagline="Shorthand for lambdas that just call an existing method: Type::method.",
        analogy="Instead of writing 'call Ada and ask her to do the report', you just point at Ada's name on the team sheet.",
        what="Method references (Java 8) are compact lambdas that delegate to an existing method or constructor. There are four kinds: static (Integer::parseInt), bound instance on a specific object (System.out::println, list::add), unbound instance on an arbitrary object of a type (String::toUpperCase, where the first lambda parameter becomes the receiver), and constructor (ArrayList::new, int[]::new). The compiler picks the target method by matching the functional interface signature, which can be ambiguous with overloads. A bound receiver is evaluated once when the reference is created, unlike a lambda that re-evaluates the expression on each call. Method references compile to the same invokedynamic mechanism as lambdas.",
        use_cases=["Mapping in streams: map(String::trim).", "Collecting into specific collections: toCollection(TreeSet::new).", "Event handlers and callbacks: button.onClick(this::save).", "Comparator keys: comparing(Person::name)."],
        key_points=[
            "Static: Type::staticMethod.",
            "Bound: obj::method (receiver fixed at creation).",
            "Unbound: Type::instanceMethod (first argument is receiver).",
            "Constructor: Type::new, Type[]::new.",
        ],
        examples=[
            jx("The four kinds", "basic", "Lambda and equivalent reference.", """
                Function<String, Integer> parse = Integer::parseInt;         // s -> Integer.parseInt(s)
                Consumer<String> print = System.out::println;               // s -> System.out.println(s)
                Function<String, String> upper = String::toUpperCase;       // s -> s.toUpperCase()
                Supplier<List<String>> make = ArrayList::new;               // () -> new ArrayList<>()
                IntFunction<String[]> arr = String[]::new;                  // n -> new String[n]

                String[] names = people.stream().map(Person::name).toArray(String[]::new);
            """),
            jx("Bound receiver is evaluated once", "intermediate", "A subtle difference from lambdas.", """
                Counter c = new Counter();
                Runnable r1 = c::increment;          // captures this c now
                Runnable r2 = () -> c.increment();   // same here, but:

                Supplier<String> ref = current()::name;       // current() called once, now
                Supplier<String> lam = () -> current().name(); // current() called on every get()
                // A null receiver fails immediately for the reference (NPE at creation).
            """),
            jx("Unbound with two arguments", "intermediate", "Receiver plus parameter.", """
                BiFunction<String, String, Boolean> startsWith = String::startsWith;   // (s, p) -> s.startsWith(p)
                Comparator<String> byIgnoreCase = String::compareToIgnoreCase;        // (a, b) -> a.compareToIgnoreCase(b)
                Set<String> sorted = names.stream().collect(Collectors.toCollection(TreeSet::new));
            """),
        ],
        commands=["Integer::parseInt", "System.out::println", "String::length", "ArrayList::new", "String[]::new"],
        gotchas=["Overloaded methods like Integer::toString can be ambiguous for Function<Integer,String>.", "obj::method with null obj throws NPE immediately, not when called.", "Overusing references with long chains can obscure intent; a named lambda may read better."],
        interview=[
            qa("basic", "What kinds of method references exist?", "Static (Type::staticMethod), bound instance (obj::method), unbound instance (Type::instanceMethod, receiver is first argument) and constructor (Type::new or Type[]::new)."),
            qa("intermediate", "How does String::compareToIgnoreCase fit Comparator<String>?", "It is an unbound reference: compare(a, b) becomes a.compareToIgnoreCase(b), with the first argument as receiver and the second as the method argument."),
            qa("intermediate", "Method reference vs lambda: any behavioural difference?", "For bound references the receiver expression is evaluated once at creation (and null fails immediately), whereas a lambda evaluates it on each invocation. Otherwise they are equivalent and both use invokedynamic."),
            qa("basic", "When should you prefer a lambda?", "When the call needs extra arguments, transformation or conditions, or when an overloaded method makes the reference ambiguous or unclear."),
        ],
        related=["functional-interfaces", "lambdas-streams", "collectors"],
        flow=chain(
            ("Target type", "Function<S,I>", "Target", "The context expects a functional interface."),
            ("Type::m", "reference", "Reference", "You name an existing method instead of writing a body.", "ref"),
            ("Resolve", "match signature", "Resolve overload", "The compiler matches parameters and return type to choose the method.", "match"),
            ("Call", "delegates", "Invoke", "Calling apply delegates straight to the referenced method.", "apply"),
        ),
    ),
    topic(
        id="collectors", title="Collectors in Depth", category="core", level="intermediate", code="CL",
        tagline="groupingBy, partitioningBy, toMap, teeing and writing custom collectors.",
        analogy="A sorting office: letters (elements) come down a belt and the collector decides which bins they go into, how they are counted, and how the bins are labelled at the end.",
        what="A Collector describes a mutable reduction with four functions: supplier (new container), accumulator (add element), combiner (merge partial results for parallel streams) and finisher (final transform). The Collectors class (Java 8) provides toList, toSet, toMap, joining, counting, summingInt, averagingDouble, groupingBy and partitioningBy, and downstream collectors let you nest them, e.g. groupingBy(dept, counting()). Java 9 added filtering and flatMapping, Java 10 toUnmodifiableList/Set/Map, and Java 12 teeing to combine two collectors. Java 16 added Stream.toList(), which returns an unmodifiable list. toMap throws IllegalStateException on duplicate keys unless you pass a merge function. Parallel streams split work and use the combiner, so collectors must be associative.",
        use_cases=["Grouping orders by customer and summing totals.", "Partitioning users into active and inactive.", "Building lookup maps by id.", "Computing min and max in one pass with teeing."],
        key_points=[
            "groupingBy(classifier, downstream) for nested aggregation.",
            "toMap needs a merge function when keys can repeat.",
            "partitioningBy always returns both true and false keys.",
            "Stream.toList() (16) is unmodifiable; Collectors.toList() makes no promise.",
            "teeing (12) combines two collectors' results.",
        ],
        examples=[
            jx("Group, count and sum", "basic", "Typical reporting queries.", """
                Map<String, Long> ordersPerCustomer = orders.stream()
                        .collect(Collectors.groupingBy(Order::customer, Collectors.counting()));

                Map<String, BigDecimal> revenue = orders.stream()
                        .collect(Collectors.groupingBy(Order::customer, TreeMap::new,
                                Collectors.reducing(BigDecimal.ZERO, Order::total, BigDecimal::add)));

                Map<Boolean, List<User>> split = users.stream()
                        .collect(Collectors.partitioningBy(User::active));
            """),
            jx("toMap with duplicates", "intermediate", "Avoid IllegalStateException.", """
                // Throws if two users share an email
                Map<String, User> byEmail = users.stream()
                        .collect(Collectors.toMap(User::email, u -> u));

                // Keep the most recent one
                Map<String, User> latest = users.stream()
                        .collect(Collectors.toMap(User::email, u -> u,
                                (a, b) -> a.updatedAt().isAfter(b.updatedAt()) ? a : b,
                                LinkedHashMap::new));
            """),
            jx("Java 9-16 collectors", "advanced", "filtering, flatMapping, teeing, toList.", """
                Map<String, Set<String>> tagsByAuthor = posts.stream()
                        .collect(Collectors.groupingBy(Post::author,
                                Collectors.flatMapping(p -> p.tags().stream(), Collectors.toSet())));   // 9

                record Range(int min, int max) {}
                Range r = nums.stream().collect(Collectors.teeing(                                  // 12
                        Collectors.minBy(Integer::compare), Collectors.maxBy(Integer::compare),
                        (mn, mx) -> new Range(mn.orElseThrow(), mx.orElseThrow())));

                List<String> names = users.stream().map(User::name).toList();                       // 16
            """),
        ],
        commands=["Collectors.groupingBy(f, counting())", "Collectors.toMap(k, v, merge)", "Collectors.partitioningBy(p)", "Collectors.joining(\", \", \"[\", \"]\")", "Collectors.teeing(c1, c2, f) (12+)"],
        gotchas=["toMap rejects null values with NPE (HashMap.merge is used).", "groupingBy returns a HashMap with no order; pass TreeMap::new or LinkedHashMap::new if order matters.", "Calling add on the result of Stream.toList() throws UnsupportedOperationException."],
        interview=[
            qa("intermediate", "What are the components of a Collector?", "supplier creates the result container, accumulator folds each element in, combiner merges two partial containers (used in parallel), and finisher converts to the final type. Characteristics such as IDENTITY_FINISH and CONCURRENT allow optimisations."),
            qa("intermediate", "groupingBy vs partitioningBy?", "groupingBy classifies by any key and only creates keys that appear. partitioningBy uses a predicate and always returns a map with both true and false keys."),
            qa("basic", "Stream.toList() vs Collectors.toList()?", "Stream.toList() (Java 16) returns an unmodifiable list and allows nulls. Collectors.toList() currently returns an ArrayList, but its mutability is not guaranteed. Use toUnmodifiableList or toCollection for explicit guarantees."),
            qa("advanced", "What does Collectors.teeing do?", "Introduced in Java 12, it sends every element to two downstream collectors and merges their results with a BiFunction, allowing for example min and max or count and sum in a single pass."),
        ],
        related=["lambdas-streams", "collections", "method-references"],
        flow=chain(
            ("supplier", "new container", "Create", "A new result container is created (per thread in parallel)."),
            ("accumulator", "add element", "Accumulate", "Each element is folded into the container.", "elem"),
            ("combiner", "merge partials", "Combine", "Parallel partial containers are merged.", "merge"),
            ("finisher", "final form", "Finish", "The container is converted to the final result.", "result"),
        ),
    ),
    topic(
        id="hashmap-internals", title="HashMap Internals", category="core", level="advanced", code="HM",
        tagline="Buckets, hash spreading, resizing and tree bins (Java 8).",
        analogy="A coat check with numbered hooks. The ticket number (hash) picks the hook; if several coats end up on one hook they are hung in a chain, and if the chain gets very long the attendant reorganises it into a sorted rack (tree).",
        what="HashMap stores entries in an array of buckets whose length is always a power of two. The key's hashCode is spread by XOR-ing its high bits into the low bits (h ^ (h >>> 16)) and the bucket index is hash & (n - 1). Collisions are stored as a linked list; since Java 8, a bucket with more than 8 entries in a table of at least 64 buckets is converted to a red-black tree (TREEIFY_THRESHOLD), turning worst-case lookups from O(n) into O(log n). When size exceeds capacity times load factor (default 16 x 0.75), the table doubles and entries are split into the same index or index plus old capacity. HashMap permits one null key and null values, is not thread-safe, and iteration order is unspecified. LinkedHashMap adds insertion or access order, which makes it a simple LRU cache.",
        use_cases=["Caches and lookups by id.", "Counting with merge or compute.", "Pre-sizing maps for known bulk loads.", "LRU caches with LinkedHashMap.removeEldestEntry."],
        key_points=[
            "Default capacity 16, load factor 0.75, capacity always a power of two.",
            "Index = spread(hash) & (n - 1).",
            "Tree bins (Java 8) when a bucket exceeds 8 entries and table >= 64.",
            "Resize doubles the table: an O(n) pause during put.",
            "Not thread-safe: concurrent puts can lose updates.",
        ],
        examples=[
            jx("Counting idioms", "basic", "merge and compute replace get-then-put.", """
                Map<String, Integer> counts = new HashMap<>();
                for (String w : words) {
                    counts.merge(w, 1, Integer::sum);        // Java 8
                }
                Map<String, List<String>> index = new HashMap<>();
                for (String w : words) {
                    index.computeIfAbsent(w.substring(0, 1), k -> new ArrayList<>()).add(w);
                }
            """),
            jx("Pre-sizing (Java 19)", "intermediate", "Avoid repeated resizes for bulk loads.", """
                // Before Java 19: capacity must account for the load factor
                Map<Long, User> m8 = new HashMap<>((int) (expected / 0.75f) + 1);

                // Java 19+: says what you mean
                Map<Long, User> m19 = HashMap.newHashMap(expected);
                HashSet<Long> s19 = HashSet.newHashSet(expected);
            """),
            jx("Simplified put path", "advanced", "What the JDK does on put.", """
                static int spread(Object key) {
                    int h;
                    return key == null ? 0 : (h = key.hashCode()) ^ (h >>> 16);
                }
                // index = spread(key) & (table.length - 1)
                // empty bucket          -> new node
                // same key (hash+equals) -> replace value
                // list length > 8       -> treeify (if table.length >= 64, else resize)
                // ++size > threshold    -> resize(): double table, split each bucket in two

                // LRU cache with LinkedHashMap
                class Lru<K, V> extends LinkedHashMap<K, V> {
                    private final int max;
                    Lru(int max) { super(16, 0.75f, true); this.max = max; }
                    @Override protected boolean removeEldestEntry(Map.Entry<K, V> e) { return size() > max; }
                }
            """),
        ],
        commands=["map.merge(k, 1, Integer::sum)", "map.computeIfAbsent(k, f)", "HashMap.newHashMap(n) (19+)", "new LinkedHashMap<>(16, .75f, true)", "map.getOrDefault(k, d)"],
        gotchas=["Poor hashCode (e.g. constant) degrades every operation; tree bins only help if keys are Comparable.", "Modifying a map while iterating throws ConcurrentModificationException.", "Concurrent modification from several threads can corrupt or lose entries; use ConcurrentHashMap.", "new HashMap<>(n) is not 'room for n entries' before Java 19's newHashMap."],
        interview=[
            qa("intermediate", "How does HashMap find the bucket for a key?", "It calls hashCode, spreads high bits into low bits with h ^ (h >>> 16), and masks with (table length - 1). The power-of-two table makes the mask equivalent to a modulo."),
            qa("advanced", "What changed in HashMap in Java 8?", "Buckets with many collisions are converted from linked lists into red-black trees (more than 8 nodes and table at least 64), giving O(log n) worst case and mitigating hash-flooding attacks. Resizing also preserves order within split buckets."),
            qa("intermediate", "What happens on resize?", "When size exceeds capacity x load factor, a new table of double size is allocated and each bucket is split into two: entries stay at index i or move to i + oldCapacity depending on one hash bit."),
            qa("intermediate", "Why is the load factor 0.75?", "It is a time/space trade-off: higher values save memory but lengthen chains, lower values waste space and resize more often. 0.75 keeps expected chain length small under Poisson-distributed hashes."),
        ],
        related=["collections", "equals-hashcode", "concurrent-utils"],
        flow=chain(
            ("key", "hashCode()", "Hash", "put calls the key's hashCode."),
            ("spread", "h ^ h>>>16", "Spread bits", "High bits are mixed into low bits.", "hash"),
            ("bucket", "hash & (n-1)", "Index", "The masked hash selects a bucket.", "index"),
            ("chain/tree", "equals()", "Collision", "Collisions form a list; >8 becomes a red-black tree.", "equals"),
            ("resize", "x2 at 75%", "Grow", "Past the threshold the table doubles and buckets split.", "rehash"),
        ),
    ),
    topic(
        id="list-set-map", title="List, Set & Map Implementations", category="core", level="basic", code="LM",
        tagline="Choosing ArrayList, LinkedList, HashSet, TreeMap and friends, plus fail-fast iterators and List.of.",
        analogy="Different storage furniture: an ArrayList is a numbered shelf, a LinkedList is a chain of boxes, a HashSet is a set of labelled drawers, and a TreeMap is an alphabetised filing cabinet.",
        what="ArrayList is backed by a resizable array: O(1) random access and amortised O(1) append, but O(n) inserts in the middle. LinkedList is a doubly linked list with poor cache locality; ArrayDeque is usually the better queue or stack. HashSet and HashMap give O(1) average operations with no order; LinkedHashSet/Map keep insertion order; TreeSet/TreeMap keep sorted order with O(log n) and navigation methods like floor and ceiling. Iterators of non-concurrent collections are fail-fast: a structural change outside the iterator throws ConcurrentModificationException on the next step, so remove with Iterator.remove or removeIf (8). Java 9 added immutable factories List.of, Set.of and Map.of that reject nulls and duplicates, and Java 10 added copyOf.",
        use_cases=["ArrayList for most sequences.", "ArrayDeque for queues and stacks.", "LinkedHashMap for ordered JSON-like output.", "TreeMap for range queries and leaderboards."],
        key_points=[
            "Default to ArrayList, HashMap, HashSet, ArrayDeque.",
            "Tree* for sorted order and range views; Linked* for insertion order.",
            "Fail-fast iterators detect concurrent modification on a best-effort basis.",
            "List.of / Map.of (9) are immutable and null-hostile.",
            "Program to interfaces: List<String> list = new ArrayList<>().",
        ],
        examples=[
            jx("Factories: Java 8 vs 9", "basic", "Creating small constant collections.", """
                // Java 8
                List<String> l8 = Collections.unmodifiableList(Arrays.asList("a", "b"));
                Map<String, Integer> m8 = new HashMap<>();
                m8.put("a", 1); m8.put("b", 2);

                // Java 9+
                List<String> l = List.of("a", "b");
                Set<String> s = Set.of("x", "y");             // duplicates -> IllegalArgumentException
                Map<String, Integer> m = Map.of("a", 1, "b", 2);
                Map<String, Integer> big = Map.ofEntries(Map.entry("c", 3), Map.entry("d", 4));
            """),
            jx("Fail-fast iteration", "intermediate", "Removing safely while iterating.", """
                List<String> names = new ArrayList<>(List.of("ann", "bob", "cy"));
                // for (String n : names) if (n.startsWith("b")) names.remove(n);  // ConcurrentModificationException

                Iterator<String> it = names.iterator();
                while (it.hasNext()) if (it.next().startsWith("b")) it.remove();   // safe

                names.removeIf(n -> n.length() < 3);                               // Java 8, simplest
            """),
            jx("Navigable TreeMap", "intermediate", "Range queries without scanning.", """
                TreeMap<Integer, String> grades = new TreeMap<>(Map.of(90, "A", 80, "B", 70, "C", 0, "F"));
                String g = grades.floorEntry(84).getValue();          // "B"
                SortedMap<Integer, String> passing = grades.tailMap(70);
                Deque<Integer> stack = new ArrayDeque<>();
                stack.push(1); stack.push(2); stack.pop();            // 2
            """),
        ],
        commands=["List.of(...) / Map.of(...) (9+)", "List.copyOf(c) (10+)", "list.removeIf(p) (8+)", "new ArrayDeque<>()", "treeMap.floorEntry(k)"],
        gotchas=["Arrays.asList is fixed-size: add throws, but set writes through to the array.", "List.of(...).contains(null) throws NPE.", "LinkedList.get(i) is O(n); looping with get(i) is O(n^2).", "Set.of and Map.of iteration order is deliberately randomised per JVM run."],
        interview=[
            qa("basic", "ArrayList vs LinkedList?", "ArrayList has O(1) random access and great cache locality; middle insertions shift elements. LinkedList has O(1) insertion at known nodes but O(n) access and high memory overhead per node. ArrayList (or ArrayDeque) wins in almost all real workloads."),
            qa("intermediate", "What is a fail-fast iterator?", "An iterator that checks a modification counter (modCount) and throws ConcurrentModificationException if the collection was structurally changed outside the iterator. It is best-effort, meant to catch bugs, not to provide thread safety."),
            qa("basic", "How do List.of and Arrays.asList differ?", "List.of (Java 9) is fully immutable and rejects nulls. Arrays.asList is a fixed-size view over an array: set works and writes through, add and remove throw, and nulls are allowed."),
            qa("intermediate", "HashMap vs LinkedHashMap vs TreeMap?", "HashMap: O(1), no order. LinkedHashMap: O(1) plus insertion or access order, useful for LRU caches. TreeMap: O(log n), sorted by key with navigation and range views."),
        ],
        related=["collections", "hashmap-internals", "sequenced-collections"],
        flow=chain(
            ("Need order?", "requirements", "Requirements", "Decide on ordering, uniqueness and access pattern."),
            ("List", "ArrayList", "Sequence", "Indexed sequence: ArrayList; queue/stack: ArrayDeque.", "index"),
            ("Set", "Hash/Tree", "Uniqueness", "Unique elements: HashSet, LinkedHashSet or TreeSet.", "unique"),
            ("Map", "Hash/Tree", "Key lookup", "Key to value: HashMap, LinkedHashMap or TreeMap.", "key"),
            ("Iterate", "fail-fast", "Iterate safely", "Modify via iterator.remove or removeIf to avoid CME.", "next"),
        ),
    ),
    topic(
        id="nio-files", title="I/O and NIO.2 (Path & Files)", category="core", level="intermediate", code="NI",
        tagline="Modern file handling with Path, Files and streams of lines (Java 7+).",
        analogy="Old java.io.File is a paper map with vague street names; NIO.2's Path and Files is a GPS that also tells you why a route failed.",
        what="Classic java.io offers byte streams (InputStream/OutputStream) and character streams (Reader/Writer), decorated with buffering. Java 7 introduced NIO.2 (JSR 203) with java.nio.file: Path represents a location, and the Files utility class reads, writes, copies, moves, walks trees and inspects attributes, throwing descriptive exceptions such as NoSuchFileException instead of returning false. Java 8 added Files.lines and Files.walk as lazy streams that must be closed, Java 11 Files.readString/writeString and Path.of, and Java 12 Files.mismatch. Always specify a charset (UTF-8 is the default since Java 18, JEP 400) and use try-with-resources. For untrusted file names, normalise paths and check they stay inside an allowed base directory to prevent path traversal.",
        use_cases=["Reading config and small files with readString.", "Streaming large logs line by line.", "Walking directories to find or clean files.", "Atomic file replacement with Files.move(ATOMIC_MOVE)."],
        key_points=[
            "Path.of (11) / Paths.get (7) build paths; Files does the work.",
            "Files.lines and Files.walk must be closed (try-with-resources).",
            "readAllLines loads everything into memory; stream for big files.",
            "Default charset is UTF-8 since Java 18.",
            "Validate user-supplied paths with normalize() and startsWith(base).",
        ],
        examples=[
            jx("Java 6 vs Java 11", "basic", "Reading a whole file.", """
                // Java 6
                BufferedReader r = null;
                StringBuilder sb = new StringBuilder();
                try {
                    r = new BufferedReader(new InputStreamReader(new FileInputStream("cfg.txt"), "UTF-8"));
                    String line;
                    while ((line = r.readLine()) != null) sb.append(line).append('\\n');
                } finally { if (r != null) r.close(); }

                // Java 11
                String cfg = Files.readString(Path.of("cfg.txt"));
                Files.writeString(Path.of("out.txt"), cfg.toUpperCase(), StandardCharsets.UTF_8);
            """),
            jx("Streaming and walking", "intermediate", "Lazy streams that must be closed.", """
                try (Stream<String> lines = Files.lines(Path.of("app.log"))) {
                    long errors = lines.filter(l -> l.contains("ERROR")).count();
                }
                try (Stream<Path> files = Files.walk(Path.of("build"), 3)) {
                    files.filter(p -> p.toString().endsWith(".tmp"))
                         .forEach(p -> { try { Files.delete(p); } catch (IOException e) { throw new UncheckedIOException(e); } });
                }
            """),
            jx("Safe paths and atomic writes", "advanced", "Prevent traversal; never leave half-written files.", """
                Path base = Path.of("/srv/uploads").toAbsolutePath().normalize();
                Path target = base.resolve(userFileName).normalize();
                if (!target.startsWith(base)) throw new SecurityException("path traversal attempt");

                Path tmp = Files.createTempFile(base, "upload-", ".part");
                Files.write(tmp, bytes);
                Files.move(tmp, base.resolve(UUID.randomUUID() + ".bin"), StandardCopyOption.ATOMIC_MOVE);
            """),
        ],
        commands=["Files.readString(Path.of(f)) (11+)", "Files.lines(p) in try-with-resources", "Files.walk(dir, depth)", "Files.copy(a, b, REPLACE_EXISTING)", "Files.move(a, b, ATOMIC_MOVE)"],
        gotchas=["Forgetting to close Files.lines leaks file handles until GC.", "File.delete() returns false silently; Files.delete throws with a reason.", "Relying on the platform default charset before Java 18 caused mojibake across OSes.", "resolve() with an absolute user path ignores the base entirely."],
        interview=[
            qa("basic", "java.io.File vs java.nio.file.Path?", "File is the legacy API with boolean return codes and limited metadata. Path plus Files (Java 7) give precise exceptions, symbolic link handling, attributes, directory streams, watch services and stream-based APIs."),
            qa("intermediate", "Why must Files.lines be closed?", "It returns a lazily populated stream backed by an open file handle. The handle is released only when the stream is closed, so use try-with-resources."),
            qa("intermediate", "How do you prevent path traversal?", "Resolve user input against a base directory, normalize the result, and check that it still startsWith the normalized absolute base. Better still, generate server-side file names and never use the raw input."),
            qa("advanced", "What did JEP 400 change?", "Since Java 18 the default charset is UTF-8 on all platforms, so APIs like FileReader and Files without explicit charsets behave consistently. You can still pass a charset explicitly, which is recommended for clarity."),
        ],
        related=["exceptions", "lambdas-streams", "java-security"],
        flow=chain(
            ("Path.of", "location", "Locate", "Build a Path; nothing touches the disk yet."),
            ("validate", "normalize", "Validate", "Normalize and check against the allowed base directory.", "check"),
            ("Files.*", "read/write", "Operate", "Files performs the operation with precise exceptions.", "I/O"),
            ("close", "try-with-res", "Release", "Streams and channels are closed automatically.", "close"),
        ),
    ),
    topic(
        id="serialization", title="Serialization & Its Risks", category="core", level="advanced", code="SE",
        tagline="Java native serialization, why it is dangerous, and safer alternatives.",
        analogy="Native deserialization is like accepting a flat-packed kit from a stranger and letting it assemble itself in your living room: the instructions can include 'and then open the back door'.",
        what="Java native serialization (Serializable, ObjectOutputStream, ObjectInputStream) converts object graphs into bytes and back, using serialVersionUID to detect incompatible class versions. During deserialization the JVM instantiates classes named in the stream and calls methods like readObject, which attackers can chain into gadget chains that run arbitrary code; many critical CVEs stem from this. Java 9 introduced serialization filters (JEP 290, ObjectInputFilter) and Java 17 context-specific filter factories (JEP 415) to allow-list classes and limit depth and size. The safest approach is to never deserialize untrusted native objects and to use data formats such as JSON or Protobuf with explicit schemas, avoiding polymorphic default typing in Jackson. Records serialize through their canonical constructor, which revalidates invariants, making them safer than ordinary classes.",
        use_cases=["Legacy session replication and RMI (avoid for new code).", "JSON APIs with Jackson or JSON-B.", "Protobuf or Avro for service-to-service messages.", "Caching DTOs in Redis as JSON."],
        key_points=[
            "Never deserialize untrusted data with ObjectInputStream.",
            "If unavoidable, use ObjectInputFilter allow-lists (9+, 17+ factories).",
            "Declare serialVersionUID explicitly for Serializable classes.",
            "Prefer JSON/Protobuf with schema validation.",
            "Jackson: never enable default typing for untrusted input.",
        ],
        examples=[
            jx("The dangerous pattern", "basic", "What to avoid.", """
                // DO NOT do this with network, file upload, cookie or queue data
                try (ObjectInputStream in = new ObjectInputStream(request.getInputStream())) {
                    Object o = in.readObject();   // instantiates any class on the classpath
                }
            """),
            jx("Allow-list with ObjectInputFilter (Java 9+)", "intermediate", "Defence in depth for legacy flows.", """
                ObjectInputFilter filter = ObjectInputFilter.Config.createFilter(
                        "com.example.dto.*;java.base/java.lang.*;java.util.*;maxdepth=5;maxbytes=65536;!*");
                try (ObjectInputStream in = new ObjectInputStream(input)) {
                    in.setObjectInputFilter(filter);
                    OrderDto dto = (OrderDto) in.readObject();
                }
                // JVM-wide: -Djdk.serialFilter=com.example.dto.*;!*
            """),
            jx("Prefer JSON with explicit types", "intermediate", "Records plus Jackson, no polymorphic typing.", """
                public record OrderDto(String id, int quantity) {
                    public OrderDto {
                        if (quantity <= 0) throw new IllegalArgumentException("quantity");
                    }
                }
                ObjectMapper mapper = new ObjectMapper()
                        .configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, true);
                OrderDto dto = mapper.readValue(json, OrderDto.class);   // concrete type only
            """),
        ],
        commands=["implements Serializable + serialVersionUID", "ObjectInputFilter.Config.createFilter(...) (9+)", "-Djdk.serialFilter=pattern", "ObjectMapper.readValue(json, Type.class)", "transient for non-serialized fields"],
        gotchas=["Changing a class without serialVersionUID breaks deserialization of stored data.", "Singletons and invariants can be bypassed by deserialization unless readResolve / validation is used.", "Libraries on the classpath (old Commons Collections, etc.) provide gadget chains even if you never use them."],
        interview=[
            qa("intermediate", "Why is Java deserialization dangerous?", "readObject instantiates classes chosen by the byte stream and runs their deserialization hooks. Attackers chain such hooks in classpath libraries (gadget chains) to achieve remote code execution, so untrusted data must never be deserialized natively."),
            qa("intermediate", "What is serialVersionUID?", "A version identifier for a Serializable class. If not declared, the JVM computes one from the class structure, so harmless changes break compatibility. Declare it explicitly and change it only for incompatible versions."),
            qa("advanced", "How do serialization filters work?", "JEP 290 (Java 9) lets you set an ObjectInputFilter per stream or JVM-wide that accepts or rejects classes by pattern and limits depth, references, array length and bytes. JEP 415 (Java 17) adds filter factories to choose filters per context."),
            qa("basic", "What does transient do?", "It excludes a field from native serialization; after deserialization it has its default value. Use it for caches, derived data or sensitive values."),
        ],
        related=["records-sealed", "java-security", "nio-files"],
        flow=chain(
            ("bytes", "untrusted input", "Receive", "A byte stream arrives from a client or queue."),
            ("readObject", "names classes", "Instantiate", "The stream names classes; the JVM creates them.", "class"),
            ("gadgets", "hooks run", "Hooks execute", "readObject hooks in libraries can be chained into code execution.", "exploit"),
            ("filter", "allow-list", "Filter", "An ObjectInputFilter rejects unexpected classes and sizes.", "deny"),
            ("JSON + DTO", "safer", "Safer path", "Prefer JSON or Protobuf mapped to concrete, validated types.", "safe"),
        ),
    ),
    topic(
        id="java-time", title="The java.time API", category="core", level="basic", code="TM",
        tagline="Immutable dates, times, zones and durations (Java 8, JSR 310).",
        analogy="Old Date was a wristwatch that also pretended to be a calendar and time zone, and anyone could twist its hands. java.time gives you separate, sealed instruments: a calendar, a clock, a world-time map and a stopwatch.",
        what="java.time, introduced in Java 8 (JSR 310, based on Joda-Time), replaces the mutable and confusing java.util.Date and Calendar. Instant is a point on the UTC timeline, ideal for timestamps and storage. LocalDate, LocalTime and LocalDateTime are human calendar values without a zone. ZonedDateTime adds a ZoneId with daylight-saving rules, and OffsetDateTime a fixed offset, which maps well to databases and APIs. Duration measures machine time in seconds and nanos, Period measures calendar amounts in years, months and days. All classes are immutable and thread-safe, and DateTimeFormatter is thread-safe unlike SimpleDateFormat. Inject a Clock to make time-dependent code testable.",
        use_cases=["Storing event timestamps as Instant (UTC).", "Scheduling in a user's local time zone.", "Computing ages, due dates and business days.", "Parsing and formatting ISO-8601 in APIs."],
        key_points=[
            "Store Instant/UTC; convert to ZonedDateTime only for display.",
            "LocalDateTime has no zone: not a moment in time.",
            "Duration for elapsed time, Period for calendar differences.",
            "DateTimeFormatter is immutable and thread-safe.",
            "Inject Clock for testability.",
        ],
        examples=[
            jx("Date/Calendar vs java.time", "basic", "Adding a month, Java 7 vs Java 8.", """
                // Java 7
                Calendar cal = Calendar.getInstance();
                cal.setTime(new Date());
                cal.add(Calendar.MONTH, 1);       // mutates; months are 0-based
                Date due7 = cal.getTime();

                // Java 8+
                LocalDate due = LocalDate.now().plusMonths(1);   // new immutable object
                Period age = Period.between(LocalDate.of(1990, 5, 17), LocalDate.now());
            """),
            jx("Zones and DST", "intermediate", "Same instant, different wall clocks.", """
                Instant now = Instant.now();
                ZonedDateTime kolkata = now.atZone(ZoneId.of("Asia/Kolkata"));
                ZonedDateTime newYork = now.atZone(ZoneId.of("America/New_York"));

                ZonedDateTime meeting = ZonedDateTime.of(2026, 3, 8, 2, 30, 0, 0, ZoneId.of("America/New_York"));
                System.out.println(meeting);   // shifted to 03:30 because 02:30 does not exist (DST gap)

                Duration d = Duration.between(start, Instant.now());
                String iso = DateTimeFormatter.ISO_OFFSET_DATE_TIME.format(kolkata);
            """),
            jx("Testable time with Clock", "intermediate", "Inject a fixed clock in tests.", """
                class TokenService {
                    private final Clock clock;
                    TokenService(Clock clock) { this.clock = clock; }
                    boolean expired(Instant issuedAt) {
                        return issuedAt.plus(Duration.ofMinutes(15)).isBefore(Instant.now(clock));
                    }
                }
                // production: new TokenService(Clock.systemUTC())
                // test:       new TokenService(Clock.fixed(Instant.parse("2026-01-01T00:00:00Z"), ZoneOffset.UTC))
            """),
        ],
        commands=["Instant.now()", "LocalDate.of(2026, 1, 31).plusMonths(1)", "ZonedDateTime.now(ZoneId.of(\"UTC\"))", "Duration.between(a, b)", "DateTimeFormatter.ofPattern(\"yyyy-MM-dd\")"],
        gotchas=["LocalDateTime.now() on servers in different zones gives different values: use Instant.", "Pattern YYYY is week-based year; use yyyy (or uuuu).", "plusMonths(1) on Jan 31 gives Feb 28/29, not an error.", "SimpleDateFormat shared between threads corrupts results; replace with DateTimeFormatter."],
        interview=[
            qa("basic", "Why was java.time introduced?", "Date and Calendar were mutable, not thread-safe, had 0-based months and mixed concepts. java.time (Java 8) offers immutable, clearly separated types for instants, local dates, zoned times and durations."),
            qa("intermediate", "Instant vs LocalDateTime vs ZonedDateTime?", "Instant is an absolute UTC point. LocalDateTime is a wall-clock date-time with no zone, so it is not a moment. ZonedDateTime combines a local date-time with a ZoneId and DST rules, mapping to exactly one instant."),
            qa("basic", "Duration vs Period?", "Duration is time-based (seconds and nanoseconds), suited to elapsed machine time. Period is date-based (years, months, days) and respects calendar lengths, suited to human differences like age."),
            qa("intermediate", "How do you test code that depends on the current time?", "Inject a java.time.Clock and call now(clock) everywhere. Tests pass Clock.fixed or Clock.offset to get deterministic results."),
        ],
        related=["immutability", "exceptions", "junit-mockito"],
        flow=chain(
            ("Instant", "UTC moment", "Capture", "Record when something happened as an Instant."),
            ("Store", "UTC / offset", "Persist", "Store UTC (TIMESTAMP WITH TIME ZONE or epoch).", "save"),
            ("ZoneId", "user zone", "Apply zone", "Convert to the user's ZoneId with DST rules.", "atZone"),
            ("Format", "ISO / pattern", "Display", "Format with a thread-safe DateTimeFormatter.", "text"),
        ),
    ),
]

_RUNTIME = [
    topic(
        id="executors", title="Threads & ExecutorService", category="runtime", level="intermediate", code="ES",
        tagline="Thread pools, Callable, Future and clean shutdown instead of new Thread().",
        analogy="Hiring a new employee for every letter is slow and chaotic. A thread pool is a fixed mailroom team: tasks go into a tray, and whoever is free takes the next one.",
        what="A Thread is an OS-level execution unit; creating one per task is expensive and unbounded. The Executor framework (Java 5, java.util.concurrent) separates task submission from execution: ExecutorService manages a pool of worker threads and a work queue. submit returns a Future for a Callable's result; invokeAll and invokeAny run batches. Executors offers factories (newFixedThreadPool, newCachedThreadPool, newScheduledThreadPool, newWorkStealingPool and, since Java 21, newVirtualThreadPerTaskExecutor), but production code often configures ThreadPoolExecutor directly to bound its queue and choose a rejection policy. Executors must be shut down with shutdown and awaitTermination; since Java 19 ExecutorService is AutoCloseable, so try-with-resources waits for tasks. Name your threads, and never swallow exceptions from tasks, as they are captured inside the Future until get() is called.",
        use_cases=["Parallel calls to several downstream services.", "Background jobs and scheduled tasks.", "CPU-bound batch processing sized to core count.", "Bounding concurrency against a fragile dependency."],
        key_points=[
            "Prefer executors over raw threads.",
            "Bound queues; unbounded queues hide overload until OOM.",
            "Future.get blocks; always pass a timeout.",
            "shutdown + awaitTermination, or try-with-resources (19+).",
            "CPU-bound: about N cores threads; I/O-bound: virtual threads (21+).",
        ],
        examples=[
            jx("Submitting Callables", "basic", "Run tasks and gather results.", """
                ExecutorService pool = Executors.newFixedThreadPool(4);
                try {
                    Future<Integer> f = pool.submit(() -> expensiveComputation());
                    Integer result = f.get(2, TimeUnit.SECONDS);   // bounded wait
                } catch (TimeoutException e) {
                    // cancel or fall back
                } finally {
                    pool.shutdown();
                    pool.awaitTermination(10, TimeUnit.SECONDS);
                }
            """),
            jx("A bounded, named pool", "intermediate", "What production code should configure.", """
                ThreadFactory tf = Thread.ofPlatform().name("billing-", 0).factory();   // Java 21 builder
                ThreadPoolExecutor pool = new ThreadPoolExecutor(
                        8, 8, 0L, TimeUnit.MILLISECONDS,
                        new ArrayBlockingQueue<>(500),                   // bounded queue
                        tf,
                        new ThreadPoolExecutor.CallerRunsPolicy());      // back-pressure instead of OOM
            """),
            jx("Java 19+ try-with-resources", "intermediate", "close() waits for submitted tasks.", """
                List<String> urls = List.of("a", "b", "c");
                try (ExecutorService ex = Executors.newVirtualThreadPerTaskExecutor()) {   // Java 21
                    List<Future<String>> fs = urls.stream().map(u -> ex.submit(() -> fetch(u))).toList();
                    for (Future<String> f : fs) System.out.println(f.get());
                }   // close() = shutdown + await
            """),
        ],
        commands=["Executors.newFixedThreadPool(n)", "pool.submit(callable).get(t, unit)", "pool.invokeAll(tasks)", "pool.shutdown(); awaitTermination(...)", "Executors.newVirtualThreadPerTaskExecutor() (21+)"],
        gotchas=["Executors.newFixedThreadPool uses an unbounded LinkedBlockingQueue.", "newCachedThreadPool can create thousands of platform threads under load.", "Exceptions in submit() tasks are hidden until get(); use execute or log inside tasks.", "Forgetting shutdown keeps non-daemon threads and the JVM alive."],
        interview=[
            qa("basic", "Why use an ExecutorService instead of new Thread()?", "Thread creation is costly and unbounded. Executors reuse threads, queue work, bound concurrency, return Futures for results and exceptions, and offer orderly shutdown."),
            qa("intermediate", "submit vs execute?", "execute(Runnable) returns nothing and uncaught exceptions go to the thread's handler. submit returns a Future; exceptions are captured and rethrown as ExecutionException from get(), so they are silent if nobody calls get."),
            qa("intermediate", "How do you size a thread pool?", "For CPU-bound work, about the number of cores. For blocking I/O, roughly cores x (1 + wait/compute time), bounded by downstream limits. On Java 21 virtual threads remove most sizing concerns for I/O."),
            qa("advanced", "What rejection policies does ThreadPoolExecutor offer?", "AbortPolicy (throw RejectedExecutionException, default), CallerRunsPolicy (run in the submitting thread, natural back-pressure), DiscardPolicy and DiscardOldestPolicy. You can also implement your own."),
        ],
        related=["concurrency", "completable-future", "virtual-threads"],
        flow=chain(
            ("submit()", "Callable", "Submit", "The caller submits a task and gets a Future immediately."),
            ("queue", "bounded", "Queue", "The task waits in the pool's work queue.", "task"),
            ("worker", "pool thread", "Execute", "A free worker thread takes and runs it.", "run"),
            ("Future", "get(timeout)", "Result", "The Future completes with a value or exception.", "result"),
            ("shutdown", "await", "Shut down", "Stop accepting tasks and wait for running ones.", "close"),
        ),
    ),
    topic(
        id="completable-future", title="CompletableFuture", category="runtime", level="advanced", code="CP",
        tagline="Composable asynchronous pipelines: thenApply, thenCompose, allOf and timeouts (Java 8/9).",
        analogy="Ordering at a food court with a buzzer. You place several orders, keep chatting, and attach instructions like 'when the pizza is ready, bring it to table 4'. Nobody stands at the counter waiting.",
        what="CompletableFuture (Java 8) is a Future you can complete manually and chain non-blocking callbacks on. supplyAsync and runAsync start work on the common ForkJoinPool unless you pass an executor. thenApply maps a result, thenCompose flat-maps to another async call, thenCombine joins two independent futures, and allOf / anyOf coordinate many. Errors propagate down the chain until handled with exceptionally, handle or whenComplete, and arrive wrapped in CompletionException. Java 9 added orTimeout, completeOnTimeout and delayedExecutor; Java 12 exceptionallyCompose. Methods without the Async suffix may run in the completing thread, while *Async variants hop to an executor. For blocking I/O, pass a dedicated executor or, on Java 21, consider plain blocking code on virtual threads instead.",
        use_cases=["Fan-out to several services and combine results.", "Non-blocking pipelines in reactive-style code.", "Timeouts and fallbacks on slow dependencies.", "Bridging callback APIs into futures."],
        key_points=[
            "thenApply = map, thenCompose = flatMap, thenCombine = zip.",
            "Pass your own executor for blocking work; the common pool is small.",
            "Handle errors with exceptionally / handle; unwrap CompletionException.",
            "orTimeout / completeOnTimeout (9) bound latency.",
            "join() throws unchecked, get() throws checked exceptions.",
        ],
        examples=[
            jx("Fan-out and combine", "intermediate", "Two calls in parallel, combined.", """
                ExecutorService io = Executors.newFixedThreadPool(16);

                CompletableFuture<User> user = CompletableFuture.supplyAsync(() -> userApi.get(id), io);
                CompletableFuture<List<Order>> orders = CompletableFuture.supplyAsync(() -> orderApi.list(id), io);

                CompletableFuture<Profile> profile = user.thenCombine(orders, Profile::new);
                Profile p = profile.join();
            """),
            jx("Compose, timeout and fallback", "advanced", "Dependent calls with resilience (Java 9+).", """
                CompletableFuture<Price> price = CompletableFuture
                        .supplyAsync(() -> catalog.find(sku), io)
                        .thenCompose(item -> CompletableFuture.supplyAsync(() -> pricing.quote(item), io))
                        .orTimeout(800, TimeUnit.MILLISECONDS)                    // Java 9
                        .exceptionally(ex -> {
                            log.warn("pricing failed: {}", ex.toString());
                            return Price.UNKNOWN;
                        });
            """),
            jx("Waiting for many", "intermediate", "allOf returns Void; collect results afterwards.", """
                List<CompletableFuture<String>> calls = urls.stream()
                        .map(u -> CompletableFuture.supplyAsync(() -> fetch(u), io))
                        .toList();
                CompletableFuture.allOf(calls.toArray(CompletableFuture[]::new)).join();
                List<String> bodies = calls.stream().map(CompletableFuture::join).toList();
            """),
        ],
        commands=["CompletableFuture.supplyAsync(s, executor)", "f.thenApply(fn) / thenCompose(fn)", "a.thenCombine(b, fn)", "CompletableFuture.allOf(fs...)", "f.orTimeout(1, SECONDS) (9+)"],
        gotchas=["Blocking I/O on the common ForkJoinPool starves parallel streams and other async tasks.", "Forgetting a terminal handler swallows exceptions silently.", "cancel(true) does not interrupt the running task.", "thenApply vs thenApplyAsync: non-async callbacks may run on the caller thread if already completed."],
        interview=[
            qa("intermediate", "thenApply vs thenCompose?", "thenApply transforms the result with a function returning a plain value. thenCompose takes a function returning another CompletionStage and flattens it, avoiding CompletableFuture<CompletableFuture<T>>."),
            qa("intermediate", "Which thread runs a CompletableFuture callback?", "Non-async callbacks run in whichever thread completes the previous stage, or immediately in the caller if already complete. *Async variants run in the given executor or the common ForkJoinPool."),
            qa("advanced", "How are exceptions handled?", "An exception completes the stage exceptionally and skips subsequent thenApply stages until exceptionally, handle or whenComplete. join wraps it in CompletionException and get in ExecutionException; inspect getCause()."),
            qa("advanced", "Why pass a custom executor?", "The common pool has about cores-1 threads and is shared JVM-wide. Blocking I/O there starves other users. A dedicated, bounded executor (or virtual threads) isolates the workload."),
        ],
        related=["executors", "concurrency", "virtual-threads"],
        flow=chain(
            ("supplyAsync", "start", "Start", "Work begins on an executor; the caller continues."),
            ("thenApply", "map", "Transform", "When it completes, transform the value.", "value"),
            ("thenCompose", "next async", "Chain", "Start a dependent async call.", "future"),
            ("exceptionally", "fallback", "Recover", "Failures skip ahead to the handler.", "error"),
            ("join", "result", "Collect", "The final result is consumed.", "done"),
        ),
    ),
    topic(
        id="jmm-locks", title="Java Memory Model, synchronized & volatile", category="runtime", level="advanced", code="JM",
        tagline="Visibility, ordering and happens-before: why correct concurrent code needs more than luck.",
        analogy="Each thread has its own notebook copy of shared notes (CPU caches). volatile and locks are the rule 'write it on the shared whiteboard and read from there', so everyone sees the latest version in the right order.",
        what="The Java Memory Model (JSR 133, Java 5) defines when a write by one thread is guaranteed to be visible to another. Without synchronization, compilers and CPUs may reorder instructions and cache values, so a thread may never see an update. The JMM defines happens-before edges: unlocking a monitor happens-before every later lock of it, a volatile write happens-before subsequent reads, Thread.start happens-before the thread's actions, and actions in a thread happen-before another thread's join returns. synchronized provides mutual exclusion and visibility; volatile provides visibility and ordering but not atomicity, so count++ on a volatile is still a race. ReentrantLock (Java 5) adds tryLock with timeout, interruptible locking, fairness and multiple Conditions; ReadWriteLock and StampedLock (8) optimise read-heavy data. Final fields are safely published once the constructor completes.",
        use_cases=["Stop flags shared between threads (volatile).", "Protecting compound invariants with synchronized.", "Timeouts on lock acquisition with tryLock.", "Double-checked locking for lazy singletons."],
        key_points=[
            "Data race = conflicting access without a happens-before edge.",
            "volatile: visibility + ordering, no atomic read-modify-write.",
            "synchronized: mutual exclusion + visibility, reentrant.",
            "ReentrantLock: tryLock, lockInterruptibly, Conditions; always unlock in finally.",
            "Lock ordering prevents deadlocks.",
        ],
        examples=[
            jx("Visibility bug and the volatile fix", "basic", "A loop that may never stop.", """
                class Worker implements Runnable {
                    private volatile boolean running = true;   // without volatile the loop may spin forever
                    public void run() {
                        while (running) { doWork(); }
                    }
                    public void stop() { running = false; }
                }
            """),
            jx("Double-checked locking done right", "advanced", "volatile is required.", """
                class Config {
                    private static volatile Config instance;
                    static Config get() {
                        Config c = instance;
                        if (c == null) {
                            synchronized (Config.class) {
                                c = instance;
                                if (c == null) instance = c = load();
                            }
                        }
                        return c;
                    }
                }
                // Simpler: holder idiom  ->  private static class Holder { static final Config I = load(); }
            """),
            jx("ReentrantLock with timeout", "intermediate", "Avoid waiting forever.", """
                private final ReentrantLock lock = new ReentrantLock();

                boolean transfer(Account from, Account to, long cents) throws InterruptedException {
                    if (!lock.tryLock(200, TimeUnit.MILLISECONDS)) return false;
                    try {
                        from.withdraw(cents);
                        to.deposit(cents);
                        return true;
                    } finally {
                        lock.unlock();
                    }
                }
            """),
        ],
        commands=["synchronized (lock) { ... }", "private volatile boolean flag;", "lock.tryLock(t, unit) / unlock() in finally", "new ReentrantReadWriteLock()", "jcmd <pid> Thread.print (find deadlocks)"],
        gotchas=["volatile count++ loses updates: use AtomicInteger or a lock.", "Synchronizing on different objects (or on a boxed Integer/String literal) gives no mutual exclusion.", "Acquiring two locks in different orders in different threads deadlocks.", "Before Java 24, synchronized blocks pinned virtual threads during blocking I/O."],
        interview=[
            qa("intermediate", "What does volatile guarantee?", "Every read sees the most recent write by any thread, and writes/reads are not reordered across it (a volatile write happens-before subsequent reads of the same variable). It does not make compound actions like i++ atomic."),
            qa("advanced", "What is happens-before?", "A partial order defined by the JMM: if action A happens-before B, B sees A's effects. Edges include program order, monitor unlock to later lock, volatile write to later read, Thread.start and join, and executor submission to task execution."),
            qa("intermediate", "synchronized vs ReentrantLock?", "Both are reentrant and give mutual exclusion and visibility. ReentrantLock adds tryLock with timeout, interruptible acquisition, optional fairness and multiple Condition objects, but requires explicit unlock in finally."),
            qa("advanced", "Why does double-checked locking need volatile?", "Without it, the reference may be published before the constructor's writes are visible, because writes can be reordered. Another thread could then see a non-null but partially initialised object."),
            qa("intermediate", "How do you prevent deadlocks?", "Acquire locks in a global consistent order, hold them briefly, use tryLock with timeouts, avoid calling alien code while holding a lock, and prefer higher-level concurrency utilities."),
        ],
        related=["concurrency", "concurrent-utils", "immutability"],
        flow=chain(
            ("Thread A", "writes x", "Write", "Thread A writes shared data, then releases a lock or writes a volatile."),
            ("Release", "unlock / vol-w", "Publish", "The release flushes prior writes for others.", "publish"),
            ("Edge", "happens-before", "Happens-before", "The JMM creates an ordering edge to the next acquire.", "hb"),
            ("Acquire", "lock / vol-r", "Acquire", "Thread B locks the same monitor or reads the volatile.", "acquire"),
            ("Thread B", "sees x", "Visible", "B is guaranteed to see A's earlier writes.", "x"),
        ),
    ),
    topic(
        id="concurrent-utils", title="ConcurrentHashMap & Atomic Classes", category="runtime", level="advanced", code="CU",
        tagline="Lock-free counters, CAS and thread-safe maps without global locks.",
        analogy="A supermarket with many checkout lanes (bins) instead of one cashier for the whole store. Atomic classes are a tally counter with a single click button: nobody can half-press it.",
        what="java.util.concurrent offers thread-safe building blocks that scale better than synchronized wrappers. ConcurrentHashMap (redesigned in Java 8) uses CAS to insert into empty bins and locks only the head node of a bin when needed, so reads are lock-free and writes contend only per bin. Its compute, computeIfAbsent and merge are atomic per key, which makes check-then-act races disappear; it forbids null keys and values. Atomic classes (AtomicInteger, AtomicLong, AtomicReference) use compare-and-set hardware instructions for lock-free updates, with updateAndGet and accumulateAndGet (8) for functional updates. Under heavy contention LongAdder and LongAccumulator (8) stripe counts across cells and outperform AtomicLong. VarHandle (Java 9) exposes the same atomic operations on fields and array elements. Iterators of concurrent collections are weakly consistent and never throw ConcurrentModificationException.",
        use_cases=["Request counters and metrics (LongAdder).", "Per-key caches with computeIfAbsent.", "Lock-free state transitions with AtomicReference.", "Rate limiter buckets keyed by client."],
        key_points=[
            "Use compute/merge for atomic per-key updates, not get-then-put.",
            "No nulls in ConcurrentHashMap.",
            "CAS loops are lock-free but can spin under contention.",
            "LongAdder for hot counters; AtomicLong for exact sequential ids.",
            "size() is an estimate under concurrent updates; mappingCount() for large maps.",
        ],
        examples=[
            jx("Race vs atomic merge", "intermediate", "Check-then-act is broken even on a concurrent map.", """
                ConcurrentHashMap<String, Integer> hits = new ConcurrentHashMap<>();

                // Broken: two threads read the same value and both write +1
                Integer old = hits.get(path);
                hits.put(path, old == null ? 1 : old + 1);

                // Correct: atomic per key
                hits.merge(path, 1, Integer::sum);
                hits.computeIfAbsent(user, u -> loadProfile(u));   // loads at most once per key
            """),
            jx("Atomics and CAS", "intermediate", "Lock-free updates.", """
                AtomicLong ids = new AtomicLong();
                long next = ids.incrementAndGet();

                AtomicReference<State> state = new AtomicReference<>(State.NEW);
                boolean started = state.compareAndSet(State.NEW, State.RUNNING);   // only one thread wins

                AtomicInteger max = new AtomicInteger();
                max.accumulateAndGet(observed, Math::max);                         // Java 8
            """),
            jx("LongAdder for hot counters", "advanced", "Striped counting under contention.", """
                LongAdder requests = new LongAdder();
                // in every request thread:
                requests.increment();
                // in the metrics thread:
                long total = requests.sum();

                ConcurrentHashMap<String, LongAdder> perRoute = new ConcurrentHashMap<>();
                perRoute.computeIfAbsent(route, r -> new LongAdder()).increment();
            """),
        ],
        commands=["map.merge(k, 1, Integer::sum)", "map.computeIfAbsent(k, f)", "atomic.compareAndSet(expect, update)", "new LongAdder().increment()", "VarHandle.compareAndSet(...) (9+)"],
        gotchas=["Long-running functions in computeIfAbsent block other updates to that bin and must not modify the map recursively.", "Collections.synchronizedMap locks the whole map and iteration still needs manual synchronization.", "Combining two atomic operations (get then set) is not atomic as a whole."],
        interview=[
            qa("intermediate", "How does ConcurrentHashMap achieve concurrency in Java 8+?", "It uses CAS to insert into empty bins and synchronizes only on the first node of a bin for updates, while reads use volatile reads without locking. Resizing is done cooperatively by multiple threads. Java 7 used fixed segments instead."),
            qa("intermediate", "Why are nulls not allowed in ConcurrentHashMap?", "With concurrent updates, get returning null would be ambiguous: absent key or null value? You cannot check containsKey atomically afterwards, so nulls are banned."),
            qa("advanced", "What is CAS?", "Compare-and-swap is a CPU instruction that sets a memory location to a new value only if it still holds the expected value, returning success. Atomic classes loop on CAS for lock-free updates, which may retry under contention and is subject to the ABA problem."),
            qa("advanced", "AtomicLong vs LongAdder?", "AtomicLong keeps one value and all threads CAS on it, which contends heavily. LongAdder spreads increments across cells and sums them on read: much faster for write-heavy counters, but sum() is not an atomic snapshot."),
        ],
        related=["jmm-locks", "hashmap-internals", "concurrency"],
        flow=chain(
            ("put / merge", "key", "Update", "A thread updates one key."),
            ("bin", "hash -> bin", "Find bin", "The key hashes to a bin in the table.", "hash"),
            ("CAS", "empty bin", "Lock-free insert", "Empty bins are filled with compare-and-set, no lock.", "CAS"),
            ("bin lock", "head node", "Per-bin lock", "Occupied bins lock only their head node briefly.", "sync"),
            ("readers", "no lock", "Concurrent reads", "Readers proceed without locking via volatile reads.", "get"),
        ),
    ),
    topic(
        id="jit-tuning", title="JIT Compilation & JVM Flags", category="runtime", level="advanced", code="JT",
        tagline="Tiered compilation, inlining, escape analysis and the flags that actually matter.",
        analogy="A new delivery driver first reads directions turn by turn (interpreter). After a week they know the busy routes by heart and take shortcuts (JIT). If a road closes, they fall back to reading directions (deoptimisation).",
        what="HotSpot starts by interpreting bytecode while profiling call counts, branch frequencies and receiver types. Tiered compilation (default since Java 8) compiles warm methods with C1 for fast startup and hot ones with C2 for peak performance, using speculative optimisations such as inlining, escape analysis (scalar replacement of non-escaping objects), loop unrolling and devirtualisation. If speculation fails, for example a new subclass is loaded, the code is deoptimised and recompiled. The JIT warm-up explains why the first requests are slow and why benchmarks need JMH. Startup can be improved with Class Data Sharing (AppCDS, Java 10+, default CDS archive since 12), the AOT cache from Project Leyden (Java 24-25), or GraalVM native image. Useful flags include -Xms/-Xmx, -XX:MaxRAMPercentage, -XX:+UseG1GC/-XX:+UseZGC, -Xlog:gc*, and diagnostic options like -XX:+PrintCompilation.",
        use_cases=["Diagnosing slow first requests after deploy.", "Writing trustworthy microbenchmarks with JMH.", "Reducing startup time with AppCDS / AOT cache.", "Right-sizing heap in containers."],
        key_points=[
            "Interpreter -> C1 -> C2 tiered compilation.",
            "Inlining is the gateway optimisation; small methods are cheap.",
            "Deoptimisation happens when assumptions break.",
            "Measure with JMH, not System.nanoTime loops.",
            "Change flags based on evidence (GC logs, JFR), not folklore.",
        ],
        examples=[
            jx("JMH benchmark", "intermediate", "Correct microbenchmarking.", """
                @BenchmarkMode(Mode.AverageTime)
                @OutputTimeUnit(TimeUnit.NANOSECONDS)
                @Warmup(iterations = 5) @Measurement(iterations = 5) @Fork(1)
                @State(Scope.Thread)
                public class ConcatBench {
                    String a = "foo", b = "bar";

                    @Benchmark public String plus() { return a + b; }
                    @Benchmark public String builder() { return new StringBuilder(a).append(b).toString(); }
                    // Return values so the JIT cannot eliminate the work as dead code.
                }
            """),
            jx("Escape analysis in action", "advanced", "Allocation the JIT can remove.", """
                record Point(int x, int y) {}

                static int distanceSq(int x, int y) {
                    Point p = new Point(x, y);      // never escapes this method
                    return p.x() * p.x() + p.y() * p.y();
                }
                // After C2 compilation and inlining, Point is scalar-replaced:
                // no heap allocation happens in the hot loop.
                // Inspect with: -XX:+UnlockDiagnosticVMOptions -XX:+PrintCompilation -XX:+PrintInlining
            """),
            jx("Startup and container flags", "intermediate", "A sensible baseline.", """
                // java -XX:MaxRAMPercentage=75 -XX:+UseG1GC \\
                //      -Xlog:gc*:file=gc.log:time,uptime \\
                //      -XX:+ExitOnOutOfMemoryError \\
                //      -jar app.jar
                //
                // AppCDS (Java 13+): java -XX:ArchiveClassesAtExit=app.jsa -jar app.jar   (training run)
                //                    java -XX:SharedArchiveFile=app.jsa -jar app.jar
                // AOT cache (Java 25): java -XX:AOTCacheOutput=app.aot -jar app.jar
                System.out.println(ManagementFactory.getRuntimeMXBean().getInputArguments());
            """),
        ],
        commands=["-XX:MaxRAMPercentage=75", "-XX:+PrintCompilation", "-Xlog:gc*:file=gc.log", "-XX:SharedArchiveFile=app.jsa", "java -XX:+PrintFlagsFinal -version", "jcmd <pid> Compiler.codecache"],
        gotchas=["Benchmarks without warm-up or dead-code protection measure nothing meaningful.", "Huge methods (>8000 bytecodes) are not JIT-compiled by default.", "Copying tuning flags from blogs often hurts: modern defaults are good.", "A full code cache stops compilation and slows the app silently."],
        interview=[
            qa("intermediate", "What is tiered compilation?", "HotSpot interprets first, then compiles warm methods with C1 (fast compile, light optimisation, with profiling) and the hottest with C2 (aggressive, profile-guided optimisation). It balances startup and peak performance."),
            qa("advanced", "What is escape analysis?", "The JIT determines whether an object can be seen outside the method or thread. If not, it can allocate it on the stack or eliminate it via scalar replacement, and remove locks on it (lock elision)."),
            qa("advanced", "What is deoptimisation?", "Compiled code relies on speculative assumptions such as a single implementation of a call. When an assumption is invalidated, the JVM discards the compiled code and returns to the interpreter for that frame, later recompiling with updated profiles."),
            qa("intermediate", "How do you reduce JVM startup time?", "Use Class Data Sharing / AppCDS, the Java 24-25 AOT cache, fewer classes and lazy initialisation, jlink-trimmed runtimes, CRaC checkpoints, or GraalVM native image for the lowest startup at the cost of peak throughput and dynamic features."),
        ],
        related=["jvm-basics", "gc-collectors", "profiling-leaks"],
        flow=chain(
            ("Interpreter", "profiles", "Interpret", "Bytecode runs interpreted while the JVM counts calls and branches."),
            ("C1", "quick compile", "Tier 3 C1", "Warm methods get a fast C1 compile with profiling.", "warm"),
            ("C2", "optimise", "Tier 4 C2", "Hot methods are recompiled by C2 with inlining and escape analysis.", "hot"),
            ("Native code", "fast path", "Peak speed", "Compiled code runs at peak speed.", "native"),
            ("Deopt", "assumption broke", "Deoptimise", "If an assumption fails, fall back to the interpreter and recompile.", "deopt"),
        ),
    ),
    topic(
        id="gc-collectors", title="Garbage Collectors: G1, ZGC, Shenandoah", category="runtime", level="advanced", code="ZG",
        tagline="Choosing a collector by throughput, latency and footprint.",
        analogy="Cleaning a busy restaurant. Serial closes the restaurant to clean. Parallel closes it but brings a big crew. G1 cleans one section at a time during short closures. ZGC and Shenandoah clean while guests are still eating.",
        what="HotSpot ships several collectors. Serial (single-threaded) suits small heaps and containers with one CPU. Parallel GC maximises throughput with multi-threaded stop-the-world collections, good for batch jobs. G1 (default since Java 9) splits the heap into regions, collects those with the most garbage first, and targets a pause goal (-XX:MaxGCPauseMillis, default 200 ms). ZGC (production in Java 15, generational in 21, the default mode in 23 and the only mode since 24) and Shenandoah (production in 15) do almost all work concurrently using load or forwarding barriers, keeping pauses typically under a millisecond regardless of heap size, at the cost of some throughput and CPU. Epsilon (11) is a no-op collector for testing. Choose by measuring: GC logs, pause percentiles and allocation rate tell you more than defaults debates.",
        use_cases=["Low-latency APIs: generational ZGC.", "Batch and ETL jobs: Parallel GC.", "General services: G1 defaults.", "Tiny containers: Serial GC."],
        key_points=[
            "G1 is the default (9+); start there.",
            "ZGC/Shenandoah: sub-millisecond pauses, more CPU.",
            "Parallel: best throughput, longer pauses.",
            "Most objects die young: the generational hypothesis.",
            "Read logs: -Xlog:gc* before tuning anything.",
        ],
        examples=[
            jx("Selecting a collector", "basic", "Flags per workload.", """
                // General purpose (default since 9):
                // java -XX:+UseG1GC -XX:MaxGCPauseMillis=100 -jar app.jar
                // Low latency (generational ZGC; default ZGC mode from 23):
                // java -XX:+UseZGC -XX:+ZGenerational -jar app.jar          (21-22)
                // java -XX:+UseZGC -jar app.jar                             (23+)
                // Throughput batch:
                // java -XX:+UseParallelGC -jar batch.jar
                // Shenandoah (in most OpenJDK builds):
                // java -XX:+UseShenandoahGC -jar app.jar
                System.out.println(ManagementFactory.getGarbageCollectorMXBeans().stream()
                        .map(GarbageCollectorMXBean::getName).toList());
            """),
            jx("Reading GC activity from code", "intermediate", "Basic metrics without an agent.", """
                for (GarbageCollectorMXBean gc : ManagementFactory.getGarbageCollectorMXBeans()) {
                    System.out.printf("%s count=%d time=%d ms%n",
                            gc.getName(), gc.getCollectionCount(), gc.getCollectionTime());
                }
                MemoryUsage heap = ManagementFactory.getMemoryMXBean().getHeapMemoryUsage();
                System.out.printf("heap used=%d MB max=%d MB%n", heap.getUsed() >> 20, heap.getMax() >> 20);
            """),
            jx("Reducing allocation pressure", "advanced", "The cheapest GC is the one that does not run.", """
                // Allocation-heavy: new list and boxed Integers per call
                List<Integer> squares(int n) {
                    List<Integer> out = new ArrayList<>();
                    for (int i = 0; i < n; i++) out.add(i * i);
                    return out;
                }
                // Lean: primitive array, pre-sized, no boxing
                int[] squaresFast(int n) {
                    int[] out = new int[n];
                    for (int i = 0; i < n; i++) out[i] = i * i;
                    return out;
                }
            """),
        ],
        commands=["-XX:+UseG1GC -XX:MaxGCPauseMillis=100", "-XX:+UseZGC (generational by default from 23)", "-XX:+UseParallelGC", "-Xlog:gc*:file=gc.log:time", "jcmd <pid> GC.heap_info", "jstat -gcutil <pid> 1000"],
        gotchas=["Setting -Xms much smaller than -Xmx causes early resizing churn in services.", "Calling System.gc() triggers full collections; disable with -XX:+DisableExplicitGC if libraries do it.", "Huge objects (humongous in G1, >= half a region) are allocated directly in old regions and can trigger premature collections.", "Low pause collectors need CPU headroom; throttled containers can stall them."],
        interview=[
            qa("intermediate", "How does G1 work?", "It divides the heap into equal regions acting as eden, survivor or old. Young collections evacuate live objects from young regions; concurrent marking finds old regions with most garbage, which are collected in mixed collections within a pause-time goal."),
            qa("advanced", "How do ZGC and Shenandoah achieve tiny pauses?", "They mark, relocate and update references concurrently with the application, using load barriers (ZGC, with coloured pointers) or forwarding barriers (Shenandoah). Pauses are limited to root scanning and remain short regardless of heap size."),
            qa("intermediate", "When would you choose Parallel GC?", "For batch or offline workloads where total throughput matters more than individual pause times, since it spends the least CPU per collected byte, accepting longer stop-the-world pauses."),
            qa("basic", "What is the generational hypothesis?", "Most objects die young. Collecting a small young generation frequently is cheap because few objects survive, while long-lived objects are promoted to an old generation collected less often."),
        ],
        related=["memory-gc", "jit-tuning", "profiling-leaks"],
        flow=chain(
            ("Allocate", "eden / TLAB", "Allocate", "New objects are bump-allocated in thread-local buffers in eden."),
            ("Young GC", "evacuate live", "Young collection", "Live young objects are copied to survivor space; garbage is free.", "survivors"),
            ("Promote", "old regions", "Promote", "Objects that survive several cycles are promoted to old regions.", "tenure"),
            ("Concurrent", "mark", "Concurrent mark", "Old regions are marked concurrently with the app.", "mark"),
            ("Compact", "evacuate", "Reclaim", "G1 mixed collections or ZGC relocation free and compact memory.", "free"),
        ),
    ),
    topic(
        id="profiling-leaks", title="Memory Leaks & Profiling (JFR, jcmd)", category="runtime", level="advanced", code="PF",
        tagline="Finding leaks, hot spots and lock contention in production with built-in tools.",
        analogy="A car's flight recorder: it keeps recording quietly while you drive, so after a strange noise you can replay exactly what happened instead of guessing.",
        what="A Java memory leak is memory that is still reachable but no longer needed, such as ever-growing static maps, caches without eviction, listeners never removed, ThreadLocals in pooled threads, or class loader leaks in redeployed apps. Symptoms are rising old-generation usage after each full GC and finally OutOfMemoryError. Java Flight Recorder (open-sourced in Java 11) records low-overhead events about allocation, GC, locks, I/O and CPU sampling and is analysed with JDK Mission Control. jcmd is the Swiss Army knife: list JVMs, print threads, take heap dumps, read flags and start JFR without restarting. Heap dumps (.hprof) analysed in Eclipse MAT show dominator trees and paths to GC roots. Async-profiler adds flame graphs for CPU and allocations, and -XX:+HeapDumpOnOutOfMemoryError captures evidence automatically.",
        use_cases=["Investigating gradual heap growth.", "Finding CPU hot spots with flame graphs.", "Diagnosing deadlocks and lock contention.", "Native memory issues in containers."],
        key_points=[
            "Leak = reachable but useless objects; find the GC root path.",
            "JFR is safe for production (around 1% overhead).",
            "Enable -XX:+HeapDumpOnOutOfMemoryError everywhere.",
            "Thread dumps several seconds apart reveal stuck threads.",
            "Native memory: -XX:NativeMemoryTracking=summary.",
        ],
        examples=[
            jx("Classic leaks", "basic", "Unbounded static cache and ThreadLocal.", """
                class SessionRegistry {
                    // Leak: grows forever, entries never removed
                    private static final Map<String, Session> SESSIONS = new HashMap<>();
                    static void register(Session s) { SESSIONS.put(s.id(), s); }
                }

                class RequestContext {
                    static final ThreadLocal<User> CURRENT = new ThreadLocal<>();
                    // In pooled threads, always clean up:
                    static void run(User u, Runnable r) {
                        CURRENT.set(u);
                        try { r.run(); } finally { CURRENT.remove(); }
                    }
                }
            """),
            jx("Bounded cache fix", "intermediate", "Evict instead of growing.", """
                Cache<String, Session> sessions = Caffeine.newBuilder()
                        .maximumSize(100_000)
                        .expireAfterAccess(Duration.ofMinutes(30))
                        .build();

                // Pure JDK alternative for small LRU caches: LinkedHashMap with removeEldestEntry
            """),
            jx("Diagnostics toolkit", "intermediate", "Commands to run against a live JVM.", """
                // jcmd                                   list JVMs
                // jcmd <pid> Thread.print                thread dump (deadlocks reported at end)
                // jcmd <pid> GC.heap_dump /tmp/app.hprof heap dump for Eclipse MAT
                // jcmd <pid> JFR.start duration=120s filename=/tmp/rec.jfr settings=profile
                // jcmd <pid> VM.native_memory summary    needs -XX:NativeMemoryTracking=summary
                // jfr print --events jdk.ObjectAllocationSample /tmp/rec.jfr
                // java -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/dumps -jar app.jar
                Recording r = new Recording(Configuration.getConfiguration("profile"));   // jdk.jfr API
                r.start();
            """),
        ],
        commands=["jcmd <pid> GC.heap_dump file.hprof", "jcmd <pid> JFR.start duration=60s filename=r.jfr", "jcmd <pid> Thread.print", "-XX:+HeapDumpOnOutOfMemoryError", "jfr summary r.jfr", "jstat -gcutil <pid> 1s"],
        gotchas=["Heap dumps pause the JVM and can contain secrets and personal data: protect and delete them.", "Heap dumps are as large as the heap; ensure disk space in the container.", "A growing heap is not a leak if it drops after a full GC; check the post-GC baseline.", "Thread-local caches and class loader leaks often appear only after many redeploys."],
        interview=[
            qa("intermediate", "How can Java leak memory with a garbage collector?", "The GC only frees unreachable objects. If something still references unneeded objects, such as a static map, unremoved listener, unbounded cache or ThreadLocal in a pooled thread, they stay reachable and accumulate."),
            qa("intermediate", "How do you investigate an OutOfMemoryError?", "Capture a heap dump (HeapDumpOnOutOfMemoryError or jcmd GC.heap_dump), open it in Eclipse MAT, inspect the dominator tree and the path to GC roots of the largest retainers, and correlate with GC logs and JFR allocation events."),
            qa("advanced", "What is JFR and why is it production-safe?", "Java Flight Recorder is built into the JVM and writes binary events into thread-local buffers with minimal overhead, around 1% with the default profile. It records GC, allocation samples, locks, I/O, exceptions and CPU samples for later analysis in JDK Mission Control."),
            qa("advanced", "What causes class loader leaks?", "An object loaded by a parent class loader (e.g. a JDBC driver registry, ThreadLocal or thread) holds a reference into classes of a child (webapp) loader. After redeploy the old loader and all its classes cannot be collected, filling metaspace."),
        ],
        related=["memory-gc", "gc-collectors", "jit-tuning"],
        flow=chain(
            ("Symptom", "heap grows", "Notice", "Post-GC heap baseline keeps rising, or latency climbs."),
            ("Record", "JFR / GC logs", "Record", "Capture JFR and GC logs while the problem happens.", "events"),
            ("Heap dump", "jcmd", "Snapshot", "Take a heap dump of the live objects.", ".hprof"),
            ("Analyse", "MAT roots", "Find retainer", "Dominator tree and GC-root paths reveal who holds memory.", "path"),
            ("Fix", "evict / remove", "Fix and verify", "Bound the cache or remove the reference, then confirm a flat baseline.", "fix"),
        ),
    ),
]

_MODERN = [
    topic(
        id="virtual-threads", title="Virtual Threads, Structured Concurrency & Scoped Values", category="modern", level="advanced", code="VI",
        tagline="Millions of cheap threads (Java 21), task scopes and immutable context passing.",
        analogy="Platform threads are full-time staff with desks; you can only hire a few hundred. Virtual threads are freelancers who borrow a desk only while actually working and leave it while waiting on the phone, so you can have millions.",
        what="Virtual threads (Project Loom, final in Java 21, JEP 444) are lightweight threads scheduled by the JVM onto a small pool of carrier platform threads. When a virtual thread blocks on I/O, sleep or a lock, it unmounts and its stack is stored on the heap, freeing the carrier for other work. This brings back the simple thread-per-request style with blocking code while scaling like asynchronous code. Before Java 24, blocking inside synchronized pinned the carrier; JEP 491 (Java 24) removed that limitation for most cases. Virtual threads should never be pooled; create one per task and limit access to scarce resources with semaphores or connection pools. Structured concurrency (preview since 21, reworked in Java 25 with StructuredTaskScope.open) treats related subtasks as one unit that succeeds, fails and cancels together. Scoped values (final in Java 25, JEP 506) pass immutable context to callees and child threads more cheaply and safely than ThreadLocal.",
        use_cases=["High-concurrency HTTP servers and clients with blocking code.", "Fan-out of many I/O calls per request.", "Replacing reactive code purely written for scalability.", "Passing request context (user, trace id) through calls."],
        key_points=[
            "Thread.ofVirtual() / newVirtualThreadPerTaskExecutor (21).",
            "Great for I/O-bound work; no gain for CPU-bound work.",
            "Do not pool virtual threads; bound resources with Semaphore.",
            "Pinning in synchronized fixed in 24; native frames still pin.",
            "StructuredTaskScope cancels siblings on failure; ScopedValue replaces ThreadLocal for context.",
        ],
        examples=[
            jx("Platform pool vs virtual threads", "basic", "Java 8 style vs Java 21.", """
                // Java 8: 200 threads cap concurrent blocking calls
                ExecutorService pool = Executors.newFixedThreadPool(200);

                // Java 21: one virtual thread per task
                try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
                    IntStream.range(0, 10_000).forEach(i ->
                        executor.submit(() -> {
                            Thread.sleep(Duration.ofSeconds(1));   // unmounts, carrier is freed
                            return i;
                        }));
                }   // waits for all 10,000 tasks: about one second total

                Thread t = Thread.ofVirtual().name("worker-", 0).start(() -> System.out.println("hi"));
            """),
            jx("Bounding a downstream resource", "intermediate", "Millions of threads, but limited DB access.", """
                private final Semaphore dbPermits = new Semaphore(20);

                Report load(long id) throws InterruptedException {
                    dbPermits.acquire();
                    try {
                        return repository.load(id);   // blocking JDBC call is fine on a virtual thread
                    } finally {
                        dbPermits.release();
                    }
                }
            """),
            jx("Structured concurrency and scoped values (Java 25 preview API)", "advanced", "Compile and run with --enable-preview.", """
                static final ScopedValue<String> TRACE_ID = ScopedValue.newInstance();   // final in 25

                Response handle(String traceId, long userId) throws InterruptedException {
                    return ScopedValue.where(TRACE_ID, traceId).call(() -> {
                        try (var scope = StructuredTaskScope.open()) {           // preview
                            var user = scope.fork(() -> userService.find(userId));
                            var orders = scope.fork(() -> orderService.recent(userId));
                            scope.join();          // fails fast and cancels the sibling on error
                            return new Response(user.get(), orders.get());
                        }
                    });
                }
                // Inside userService: TRACE_ID.get() is visible to forked subtasks too.
            """),
        ],
        commands=["Thread.ofVirtual().start(r) (21+)", "Executors.newVirtualThreadPerTaskExecutor()", "Thread.startVirtualThread(r)", "-Djdk.tracePinnedThreads=full (21-23)", "spring.threads.virtual.enabled=true", "--enable-preview (StructuredTaskScope)"],
        gotchas=["Pooling virtual threads defeats their purpose and limits concurrency.", "Unbounded concurrency can overwhelm databases; virtual threads do not add DB connections.", "Heavy ThreadLocal use multiplies memory with millions of threads.", "CPU-bound work does not speed up; use a parallel stream or fixed pool sized to cores."],
        interview=[
            qa("intermediate", "What is a virtual thread?", "A java.lang.Thread implemented by the JVM rather than the OS. It runs mounted on a carrier platform thread and unmounts when it blocks, so millions can exist with small heap-allocated stacks. Final in Java 21."),
            qa("intermediate", "When do virtual threads help, and when do they not?", "They help when many tasks spend most time blocked on I/O, by increasing concurrency without async code. They do not make CPU-bound work faster and do not remove limits of downstream resources."),
            qa("advanced", "What is pinning?", "A virtual thread is pinned when it cannot unmount while blocking, so its carrier is blocked too. In Java 21-23 this happened inside synchronized blocks and native calls; Java 24 (JEP 491) fixed synchronized, leaving mainly native frames and class initialisers."),
            qa("advanced", "What problem does structured concurrency solve?", "With plain executors, a failed subtask leaves siblings running and leaks threads. StructuredTaskScope ties subtasks to a lexical scope: they are joined together, failures cancel siblings, and thread dumps show the parent-child relationship."),
            qa("advanced", "Why use ScopedValue instead of ThreadLocal?", "ScopedValues are immutable, bound for a bounded dynamic scope, automatically inherited by structured subtasks, and cheap to read. ThreadLocals are mutable, can leak in pools, and copying inheritable ones to millions of threads is costly."),
        ],
        related=["concurrency", "executors", "completable-future", "jmm-locks"],
        flow=chain(
            ("Virtual thr", "task", "Start", "A virtual thread is created for each task, cheaply."),
            ("Mount", "carrier thread", "Mount", "The scheduler mounts it on a carrier platform thread.", "run"),
            ("Block I/O", "unmount", "Unmount", "On blocking I/O its stack moves to the heap and the carrier is freed.", "park"),
            ("Other work", "carrier reused", "Reuse carrier", "The carrier runs other virtual threads meanwhile.", "next"),
            ("Resume", "remount", "Resume", "When I/O completes, it is remounted, possibly on another carrier.", "unpark"),
        ),
    ),
    topic(
        id="sequenced-collections", title="Sequenced Collections", category="modern", level="intermediate", code="SQ",
        tagline="getFirst, getLast, reversed and friends on every ordered collection (Java 21).",
        analogy="Every queue, playlist and train already had a front and back, but each one had a different way of asking 'who is first?'. Java 21 gave them all the same question.",
        what="Before Java 21 there was no common type for collections with a defined encounter order, and getting the last element meant list.get(list.size() - 1), deque.getLast(), or iterating a LinkedHashSet to the end. JEP 431 (Java 21) added three interfaces: SequencedCollection (addFirst, addLast, getFirst, getLast, removeFirst, removeLast, reversed), SequencedSet, and SequencedMap (firstEntry, lastEntry, pollFirstEntry, putFirst, putLast, sequencedKeySet, sequencedValues, sequencedEntrySet, reversed). List, Deque, LinkedHashSet, SortedSet, LinkedHashMap and SortedMap were retrofitted into this hierarchy. reversed() returns a view, not a copy, so changes flow both ways. Unmodifiable collections throw UnsupportedOperationException from mutators, and sorted collections throw it from addFirst/addLast because the position is determined by ordering.",
        use_cases=["Reading the newest or oldest entry of an ordered map.", "Iterating a list or LinkedHashSet backwards without index math.", "Moving a key to the front of an LRU-like LinkedHashMap.", "APIs that accept any ordered collection."],
        key_points=[
            "New interfaces: SequencedCollection, SequencedSet, SequencedMap.",
            "getFirst/getLast throw NoSuchElementException when empty.",
            "reversed() is a live view.",
            "TreeSet.addFirst throws: sorted order wins.",
        ],
        examples=[
            jx("Before and after (Java 8 vs 21)", "basic", "First and last element.", """
                // Java 8
                String last8 = list.get(list.size() - 1);
                String firstOfSet8 = linkedSet.iterator().next();
                Map.Entry<String, Integer> lastEntry8 = null;
                for (Map.Entry<String, Integer> e : linkedMap.entrySet()) lastEntry8 = e;

                // Java 21
                String last = list.getLast();
                String firstOfSet = linkedSet.getFirst();
                Map.Entry<String, Integer> lastEntry = linkedMap.lastEntry();
            """),
            jx("Reversed views", "intermediate", "Iterate backwards without copying.", """
                List<String> events = new ArrayList<>(List.of("login", "view", "logout"));
                for (String e : events.reversed()) System.out.println(e);   // logout, view, login

                List<String> rev = events.reversed();
                rev.addFirst("crash");       // adds at the END of events
                System.out.println(events);  // [login, view, logout, crash]
            """),
            jx("SequencedMap operations", "intermediate", "Ordered maps get a uniform API.", """
                LinkedHashMap<String, Integer> recent = new LinkedHashMap<>();
                recent.put("a", 1); recent.put("b", 2); recent.put("c", 3);
                recent.putFirst("c", 3);                      // move/insert at front
                Map.Entry<String, Integer> oldest = recent.pollLastEntry();   // removes "b"
                SequencedSet<String> keys = recent.sequencedKeySet();
                keys.reversed().forEach(System.out::println);
            """),
        ],
        commands=["list.getFirst() / getLast() (21+)", "coll.reversed() (21+)", "map.firstEntry() / lastEntry()", "map.pollFirstEntry()", "linkedMap.putFirst(k, v)"],
        gotchas=["Subclasses that already defined methods like getFirst with a different return type fail to compile on 21.", "reversed() is a view: mutating it mutates the original.", "HashSet and HashMap are not sequenced; there is no defined order to expose."],
        interview=[
            qa("basic", "What are sequenced collections?", "Java 21 (JEP 431) interfaces that unify collections with a defined encounter order, providing getFirst, getLast, addFirst, addLast, removeFirst, removeLast and reversed, plus SequencedMap equivalents."),
            qa("intermediate", "Which classes implement SequencedCollection?", "List implementations, Deque implementations, LinkedHashSet, and SortedSet/NavigableSet such as TreeSet (via SequencedSet). LinkedHashMap and SortedMap implement SequencedMap."),
            qa("intermediate", "What does reversed() return?", "A reverse-ordered view backed by the original collection. Reads and writes go through to the original, so no copying happens."),
            qa("intermediate", "Why does TreeSet.addFirst throw?", "Elements in a sorted set are positioned by the comparator, so explicit positioning is meaningless; addFirst and addLast throw UnsupportedOperationException."),
        ],
        related=["collections", "list-set-map", "java-versions"],
        flow=chain(
            ("Ordered coll", "List / Deque", "Ordered collection", "List, Deque, LinkedHashSet and LinkedHashMap all have encounter order."),
            ("Sequenced", "Java 21", "Common interface", "They now share SequencedCollection or SequencedMap.", "retrofit"),
            ("getFirst", "getLast", "Uniform access", "Ends are accessed the same way everywhere.", "ends"),
            ("reversed()", "live view", "Reverse view", "reversed() offers a backwards view without copying.", "view"),
        ),
    ),
    topic(
        id="record-patterns", title="Record Patterns & Data-Oriented Programming", category="modern", level="intermediate", code="RP",
        tagline="Deconstruct records in instanceof and switch, including nested patterns (Java 21).",
        analogy="Instead of opening a parcel, then the box inside, then the envelope, and reading each label separately, you describe the shape you expect and the contents fall into named hands in one move.",
        what="Record patterns, previewed in Java 19-20 and final in Java 21 (JEP 440), let you test whether a value is a record of a given type and bind its components in a single step: if (o instanceof Point(int x, int y)). Patterns nest, so a Line(Point(var x1, var y1), Point p2) can be matched directly. They work in switch together with sealed interfaces, giving exhaustive data-oriented code without the visitor pattern. Generic record patterns infer type arguments. Java 22 finalised unnamed variables and patterns (JEP 456), so components you do not need can be written as _. Type inference with var inside patterns keeps them compact. Primitive type patterns are in preview from Java 23 onwards.",
        use_cases=["Interpreters and expression evaluators over sealed ASTs.", "Handling message or event variants.", "Destructuring API results like Success/Failure.", "Replacing visitor-pattern boilerplate."],
        key_points=[
            "Pattern binds components via accessor methods.",
            "Nesting deconstructs deep structures in one case.",
            "Sealed + records + switch = exhaustive matching.",
            "_ (Java 22) ignores components.",
            "Null never matches a record pattern.",
        ],
        examples=[
            jx("instanceof: Java 8 vs 16 vs 21", "basic", "Three generations of the same check.", """
                // Java 8
                if (obj instanceof Point) {
                    Point p = (Point) obj;
                    System.out.println(p.x() + p.y());
                }
                // Java 16: type pattern
                if (obj instanceof Point p) System.out.println(p.x() + p.y());
                // Java 21: record pattern
                if (obj instanceof Point(int x, int y)) System.out.println(x + y);
            """),
            jx("Exhaustive evaluator", "intermediate", "Sealed interface plus nested patterns.", """
                sealed interface Expr permits Num, Add, Mul, Neg {}
                record Num(int value) implements Expr {}
                record Add(Expr left, Expr right) implements Expr {}
                record Mul(Expr left, Expr right) implements Expr {}
                record Neg(Expr inner) implements Expr {}

                static int eval(Expr e) {
                    return switch (e) {
                        case Num(var v) -> v;
                        case Add(Num(var a), Num(var b)) -> a + b;      // nested fast path
                        case Add(var l, var r) -> eval(l) + eval(r);
                        case Mul(var l, var r) -> eval(l) * eval(r);
                        case Neg(var inner) -> -eval(inner);
                    };   // no default: compiler knows all cases
                }
            """),
            jx("Unnamed patterns (Java 22)", "intermediate", "Ignore what you do not need.", """
                sealed interface Result<T> permits Ok, Err {}
                record Ok<T>(T value, Instant at) implements Result<T> {}
                record Err<T>(String message, int code) implements Result<T> {}

                static <T> String summary(Result<T> r) {
                    return switch (r) {
                        case Ok<T>(var v, _) -> "ok: " + v;
                        case Err<T>(var msg, _) -> "error: " + msg;
                    };
                }
            """),
        ],
        commands=["o instanceof Point(int x, int y) (21+)", "case Add(var l, var r) ->", "case Ok(var v, _) -> (22+)", "case Type t when cond ->", "sealed interface X permits A, B"],
        gotchas=["Adding a new permitted subtype breaks exhaustive switches at compile time (good) and throws MatchException for stale binaries.", "Record patterns call accessors; expensive or side-effecting accessors run during matching.", "Overly deep nested patterns can hurt readability; split into helper methods."],
        interview=[
            qa("intermediate", "What is a record pattern?", "A pattern that matches a record type and extracts its components into variables, e.g. case Point(int x, int y). It was finalised in Java 21 and can be nested and used in instanceof and switch."),
            qa("intermediate", "How do sealed types and record patterns work together?", "A sealed interface lists all permitted record implementations, so a switch with record patterns over it can be checked for exhaustiveness without a default. Adding a variant forces every switch to be updated."),
            qa("advanced", "What is data-oriented programming in Java?", "Modelling data as immutable records and sealed hierarchies, and putting operations in pattern-matching functions rather than in polymorphic methods. It suits ASTs, messages and results where the set of variants is fixed and operations grow."),
            qa("basic", "What does _ mean in a pattern?", "Since Java 22 (JEP 456), _ is an unnamed pattern or variable: it matches anything and binds nothing, signalling that the component is intentionally ignored."),
        ],
        related=["records-sealed", "pattern-matching", "switch-expressions"],
        flow=chain(
            ("Value", "Expr e", "Input", "A value of a sealed type reaches the switch."),
            ("Type test", "is Add?", "Test type", "The pattern checks the record type.", "instanceof"),
            ("Deconstruct", "accessors", "Extract", "Components are read via accessors and matched recursively.", "l, r"),
            ("Bind", "var l, var r", "Bind", "Matched components are bound to variables.", "bind"),
            ("Branch", "exhaustive", "Run branch", "The branch runs; the compiler proved every variant is handled.", "result"),
        ),
    ),
]

_VERSIONS = [
    topic(
        id="modules", title="Modules (JPMS)", category="versions", level="advanced", code="MD",
        tagline="module-info.java, strong encapsulation, jdeps and jlink (Java 9).",
        analogy="A classpath is an open-plan office where anyone can walk into any room. Modules give every team a room with a door and a sign saying which rooms visitors may enter.",
        what="The Java Platform Module System (Project Jigsaw, Java 9) groups packages into named modules declared in module-info.java. A module states what it requires and which packages it exports; non-exported packages are inaccessible to other modules even if their classes are public. opens grants deep reflective access, typically to frameworks, and provides/uses wires ServiceLoader services. The JDK itself was split into about 70 modules, which lets jlink build a minimal runtime image for containers. Code on the classpath lives in the unnamed module, and plain JARs on the module path become automatic modules, which allows gradual migration. Strong encapsulation of JDK internals was enforced in Java 16-17. Java 25 added module import declarations (JEP 511): import module java.base; imports all exported packages of a module.",
        use_cases=["Smaller container images with jlink.", "Enforcing architecture boundaries in large codebases.", "Library authors hiding internal packages.", "Plugin discovery with ServiceLoader."],
        key_points=[
            "requires, requires transitive, exports, opens, uses, provides.",
            "public is no longer enough: the package must be exported.",
            "Classpath code = unnamed module; plain JARs on module path = automatic modules.",
            "jdeps finds dependencies; jlink builds custom runtimes.",
            "Split packages across modules are not allowed.",
        ],
        examples=[
            jx("module-info.java", "basic", "A typical application module.", """
                module com.example.orders {
                    requires java.net.http;
                    requires transitive com.example.common;   // readers of orders also read common
                    requires static lombok;                    // compile-time only

                    exports com.example.orders.api;            // public API
                    opens com.example.orders.model to com.fasterxml.jackson.databind;   // reflection only

                    uses com.example.orders.spi.PaymentProvider;
                    provides com.example.orders.spi.PaymentProvider with com.example.orders.internal.CardProvider;
                }
            """),
            jx("ServiceLoader with modules", "intermediate", "Discover implementations at runtime.", """
                ServiceLoader<PaymentProvider> loader = ServiceLoader.load(PaymentProvider.class);
                PaymentProvider provider = loader.stream()
                        .map(ServiceLoader.Provider::get)
                        .filter(p -> p.supports("card"))
                        .findFirst()
                        .orElseThrow();
            """),
            jx("Tooling: jdeps and jlink", "intermediate", "Analyse and build a slim runtime.", """
                // jdeps --print-module-deps --ignore-missing-deps target/app.jar
                //   -> java.base,java.net.http,java.sql
                // jlink --add-modules java.base,java.net.http,java.sql \\
                //       --strip-debug --no-header-files --no-man-pages --output build/jre
                // build/jre/bin/java -jar target/app.jar
                // javac -d out --module-source-path src -m com.example.orders
                // java --module-path out -m com.example.orders/com.example.orders.Main
                // Java 25:  import module java.base;   at the top of a source file
                ModuleLayer.boot().modules().forEach(m -> System.out.println(m.getName()));
            """),
        ],
        commands=["jdeps --print-module-deps app.jar", "jlink --add-modules ... --output jre", "java --module-path mods -m mod/Main", "java --list-modules", "--add-opens mod/pkg=ALL-UNNAMED"],
        gotchas=["Reflection-heavy frameworks need opens, otherwise InaccessibleObjectException.", "Split packages (same package in two modules) fail at startup.", "Many libraries are still automatic modules with unstable names; check Automatic-Module-Name.", "Most applications keep using the classpath; modules are optional."],
        interview=[
            qa("intermediate", "What problem does JPMS solve?", "It provides reliable configuration (missing modules fail at startup, not at runtime) and strong encapsulation (only exported packages are accessible). It also made the JDK modular so runtimes can be trimmed with jlink."),
            qa("intermediate", "exports vs opens?", "exports makes public types of a package accessible at compile and run time. opens allows deep reflection on all members, including private ones, at runtime only, which frameworks like Jackson or Hibernate need."),
            qa("advanced", "What are the unnamed and automatic modules?", "Everything on the classpath belongs to the unnamed module, which reads all modules. A plain JAR placed on the module path becomes an automatic module that exports all its packages and reads all modules, easing migration."),
            qa("intermediate", "What does requires transitive mean?", "Any module that requires this module also implicitly reads the transitive dependency, which is necessary when your exported API exposes types from that dependency."),
        ],
        related=["jvm-basics", "reflection", "build-tools"],
        flow=chain(
            ("module-info", "declare", "Declare", "Each module states requires and exports."),
            ("Resolve", "module graph", "Resolve graph", "At startup the JVM resolves the full module graph; missing modules fail fast.", "requires"),
            ("Encapsulate", "exports only", "Encapsulate", "Only exported packages are accessible; opens allows reflection.", "exports"),
            ("jlink", "custom JRE", "Link", "jlink assembles only the needed modules into a runtime.", "image"),
        ),
    ),
    topic(
        id="http-client", title="The HTTP Client (Java 11)", category="versions", level="intermediate", code="HC",
        tagline="java.net.http: HTTP/2, async requests and TLS 1.3 without third-party libraries.",
        analogy="HttpURLConnection is an old rotary phone with confusing dials. HttpClient is a smartphone: one app for calls, async messages and secure lines.",
        what="The java.net.http module, incubated in Java 9 and standardised in Java 11 (JEP 321), replaces the awkward HttpURLConnection. HttpClient is immutable, thread-safe and meant to be reused; it supports HTTP/1.1 and HTTP/2, redirects, proxies, authentication, cookies, WebSocket and both synchronous send and asynchronous sendAsync returning CompletableFuture. HttpRequest is built with a fluent builder and BodyPublishers, and responses are read with BodyHandlers such as ofString, ofInputStream or ofFile. Since Java 21 HttpClient is AutoCloseable. TLS is configured through SSLContext and SSLParameters, and should be restricted to TLSv1.3 where peers support it. Always set connect and request timeouts, and pass credentials from the environment or a secret store, never as literals.",
        use_cases=["Calling REST APIs from services and CLIs.", "Parallel async requests with sendAsync.", "Downloading files directly to disk.", "Health checks and webhooks without extra dependencies."],
        key_points=[
            "Build one HttpClient and reuse it.",
            "Set connectTimeout on the client and timeout per request.",
            "sendAsync returns CompletableFuture<HttpResponse<T>>.",
            "Restrict TLS to TLSv1.3 via SSLParameters.",
            "Read tokens from the environment or a vault.",
        ],
        examples=[
            jx("HttpURLConnection vs HttpClient", "basic", "Java 8 vs Java 11.", """
                // Java 8
                HttpURLConnection c = (HttpURLConnection) new URL("https://api.example.com/items").openConnection();
                c.setRequestMethod("GET");
                try (InputStream in = c.getInputStream()) {
                    String body8 = new String(in.readAllBytes(), StandardCharsets.UTF_8);   // readAllBytes is 9+
                }

                // Java 11
                HttpClient client = HttpClient.newBuilder()
                        .connectTimeout(Duration.ofSeconds(3))
                        .followRedirects(HttpClient.Redirect.NORMAL)
                        .build();
                HttpRequest req = HttpRequest.newBuilder(URI.create("https://api.example.com/items"))
                        .timeout(Duration.ofSeconds(5)).GET().build();
                String body = client.send(req, HttpResponse.BodyHandlers.ofString()).body();
            """),
            jx("POST JSON with a token from the environment", "intermediate", "No hardcoded secrets.", """
                String token = System.getenv("API_TOKEN");   // injected by the platform; never a literal
                HttpRequest post = HttpRequest.newBuilder(URI.create("https://api.example.com/orders"))
                        .header("Content-Type", "application/json")
                        .header("Authorization", "Bearer " + token)
                        .timeout(Duration.ofSeconds(5))
                        .POST(HttpRequest.BodyPublishers.ofString(\"\"\"
                            {"sku": "A-1", "quantity": 2}
                            \"\"\"))
                        .build();
                HttpResponse<String> res = client.send(post, HttpResponse.BodyHandlers.ofString());
                if (res.statusCode() >= 400) throw new IllegalStateException("HTTP " + res.statusCode());
            """),
            jx("Async fan-out over TLS 1.3", "advanced", "Restrict protocols and run requests concurrently.", """
                SSLParameters tls = new SSLParameters();
                tls.setProtocols(new String[] {"TLSv1.3"});

                try (HttpClient client = HttpClient.newBuilder()           // AutoCloseable since 21
                        .version(HttpClient.Version.HTTP_2)
                        .sslContext(SSLContext.getDefault())             // default trust store validates certificates
                        .sslParameters(tls)
                        .build()) {
                    List<CompletableFuture<String>> calls = uris.stream()
                            .map(u -> client.sendAsync(HttpRequest.newBuilder(u).build(), HttpResponse.BodyHandlers.ofString())
                                    .thenApply(HttpResponse::body))
                            .toList();
                    calls.forEach(f -> System.out.println(f.join().length()));
                }
            """),
        ],
        commands=["HttpClient.newHttpClient()", "HttpRequest.newBuilder(uri).timeout(d).build()", "client.send(req, BodyHandlers.ofString())", "client.sendAsync(req, handler)", "-Djdk.tls.client.protocols=TLSv1.3"],
        gotchas=["Creating a new HttpClient per request wastes connection pools and threads.", "No default request timeout: a hung server blocks forever.", "Disabling certificate validation with a trust-all TrustManager is never acceptable, even temporarily.", "Some headers (Host, Connection, Content-Length) are restricted and cannot be set."],
        interview=[
            qa("basic", "Why use HttpClient over HttpURLConnection?", "HttpClient (Java 11) has a clean builder API, supports HTTP/2, WebSocket and asynchronous requests via CompletableFuture, is immutable and thread-safe, and has better timeout handling."),
            qa("intermediate", "Should you create a client per request?", "No. HttpClient holds a connection pool and executor; create one per configuration and reuse it across threads. Since Java 21 you can close it when the application shuts down."),
            qa("intermediate", "How do you make async requests?", "Call sendAsync, which returns a CompletableFuture<HttpResponse<T>>, and compose it with thenApply or combine several with allOf. On Java 21 you can also call send on virtual threads."),
            qa("advanced", "How do you enforce TLS 1.3 and secure certificates?", "Set SSLParameters protocols to TLSv1.3 (or -Djdk.tls.client.protocols), keep the default trust store or a vetted custom one, and never install trust-all managers. Server certificates should be checked for expiry, RSA 2048+ or EC P-256+ keys and SHA-2 signatures."),
        ],
        related=["completable-future", "virtual-threads", "java-security"],
        flow=chain(
            ("Client", "reused", "Build client", "One HttpClient with timeouts, redirects and TLS settings."),
            ("Request", "builder", "Build request", "An immutable HttpRequest with method, headers and body.", "req"),
            ("TLS 1.3", "handshake", "Secure", "The connection negotiates TLS 1.3 and validates the certificate.", "TLS"),
            ("Send", "sync / async", "Send", "send blocks; sendAsync returns a CompletableFuture.", "HTTP/2"),
            ("Response", "BodyHandler", "Read", "A BodyHandler converts the body to String, stream or file.", "200"),
        ),
    ),
]

_ECOSYSTEM = [
    topic(
        id="build-tools", title="Build Tools: Maven & Gradle", category="ecosystem", level="basic", code="BT",
        tagline="Dependencies, lifecycles, wrappers and reproducible builds.",
        analogy="A recipe book plus a pantry service. You list the ingredients (dependencies) and steps (lifecycle), and the tool fetches exactly the right versions and cooks the same dish on every machine.",
        what="Maven (2004) uses a declarative pom.xml and a fixed lifecycle (validate, compile, test, package, verify, install, deploy) driven by plugins, with dependencies resolved from repositories such as Maven Central. Gradle uses a Groovy or Kotlin DSL with a task graph, incremental builds and a build cache, and is the default for Android and popular for large multi-project builds. Both resolve transitive dependencies; conflicts are settled by nearest-wins in Maven and highest-version in Gradle, so inspect the tree. Use the wrappers (mvnw, gradlew) to pin the tool version, and compile with --release (maven.compiler.release or Gradle toolchains) to target a Java version reliably. A BOM (bill of materials) aligns versions of related libraries, for example Spring Boot's dependency management. Add dependency vulnerability scanning to CI, and never commit repository credentials; supply them via environment variables or CI secrets.",
        use_cases=["Compiling, testing and packaging JARs in CI.", "Managing transitive dependency versions with BOMs.", "Multi-module projects sharing code.", "Producing container images (Jib, Spring Boot buildpacks)."],
        key_points=[
            "Commit the wrapper; build with ./mvnw or ./gradlew.",
            "Set release 17/21 instead of source/target.",
            "Use a BOM to align versions.",
            "Inspect conflicts: mvn dependency:tree / gradle dependencies.",
            "Keep credentials out of pom.xml and build scripts.",
        ],
        examples=[
            jx("Maven pom essentials", "basic", "Shown as Java-comment text: a minimal pom.", """
                // <project>
                //   <groupId>com.example</groupId><artifactId>orders</artifactId><version>1.0.0</version>
                //   <properties>
                //     <maven.compiler.release>21</maven.compiler.release>
                //   </properties>
                //   <dependencies>
                //     <dependency>
                //       <groupId>org.junit.jupiter</groupId><artifactId>junit-jupiter</artifactId>
                //       <version>5.11.0</version><scope>test</scope>
                //     </dependency>
                //   </dependencies>
                // </project>
                // ./mvnw clean verify      runs compile, test, package, integration checks
                public class Main { public static void main(String[] a) { System.out.println("built"); } }
            """),
            jx("Gradle Kotlin DSL", "intermediate", "Toolchains pin the JDK used for compilation.", """
                // build.gradle.kts
                // plugins { java; application }
                // java { toolchain { languageVersion = JavaLanguageVersion.of(21) } }
                // repositories { mavenCentral() }
                // dependencies {
                //     implementation(platform("org.springframework.boot:spring-boot-dependencies:3.3.4"))
                //     implementation("com.fasterxml.jackson.core:jackson-databind")   // version from BOM
                //     testImplementation("org.junit.jupiter:junit-jupiter:5.11.0")
                // }
                // tasks.test { useJUnitPlatform() }
                // ./gradlew build --scan
                record BuildInfo(String version) {}
            """),
            jx("Reading build metadata at runtime", "intermediate", "Version from the JAR manifest, credentials from env.", """
                String version = Main.class.getPackage().getImplementationVersion();   // from MANIFEST.MF
                // Repository credentials belong in ~/.m2/settings.xml with env placeholders:
                //   <password>${env.REPO_PASSWORD}</password>
                // or Gradle: credentials { username = System.getenv("REPO_USER"); password = System.getenv("REPO_PASSWORD") }
                System.out.println("orders " + version);
            """),
        ],
        commands=["./mvnw clean verify", "./mvnw dependency:tree", "./gradlew build", "./gradlew dependencies --configuration runtimeClasspath", "javac --release 21"],
        gotchas=["source/target without release can compile against newer JDK APIs and fail at runtime on older JVMs.", "Snapshot or dynamic versions (1.+) make builds non-reproducible.", "Two versions of a library on the classpath lead to NoSuchMethodError at runtime.", "Committing settings.xml or gradle.properties with real tokens leaks credentials."],
        interview=[
            qa("basic", "Maven vs Gradle?", "Maven is declarative XML with a fixed lifecycle and strong conventions. Gradle is a programmable DSL with a task graph, incremental builds and caching, which is faster and more flexible for large builds but can become complex."),
            qa("intermediate", "How are dependency conflicts resolved?", "Maven picks the version nearest to the root of the tree (first declaration wins at equal depth); Gradle picks the highest requested version by default. Use dependencyManagement, BOMs or constraints to force a version and inspect the tree."),
            qa("intermediate", "Why use --release instead of -source/-target?", "--release (Java 9+) compiles against the API signature of the target version, preventing accidental use of newer APIs that would fail at runtime on the older JVM."),
            qa("basic", "Why commit the Maven or Gradle wrapper?", "It pins the build tool version and downloads it automatically, so every developer and CI agent builds with the same tool regardless of local installation."),
        ],
        related=["modules", "junit-mockito", "spring-boot"],
        flow=chain(
            ("pom / gradle", "declare", "Declare", "Dependencies, plugins and Java release are declared."),
            ("Resolve", "Maven Central", "Resolve", "Transitive dependencies are downloaded and versions reconciled.", "deps"),
            ("Compile", "--release 21", "Compile", "Sources are compiled for the target Java version.", "classes"),
            ("Test", "JUnit 5", "Test", "Unit and integration tests run.", "report"),
            ("Package", "JAR / image", "Package", "A JAR or container image is produced and published.", "artifact"),
        ),
    ),
    topic(
        id="junit-mockito", title="Unit Testing: JUnit 5 & Mockito", category="ecosystem", level="intermediate", code="JU",
        tagline="Readable tests, parameterised cases, mocks and assertions.",
        analogy="A flight simulator. You test the pilot (your class) against fake weather and fake air traffic control (mocks) so failures are safe, repeatable and fast.",
        what="JUnit 5 (Jupiter, 2017) is the standard test framework: @Test methods, lifecycle hooks (@BeforeEach, @AfterAll), @DisplayName, @Nested classes, @ParameterizedTest with sources like @CsvSource and @MethodSource, and assertions such as assertEquals, assertThrows and assertAll. Extensions (@ExtendWith) replace JUnit 4 runners and rules. Mockito creates test doubles: mock() or @Mock returns stubs, when(...).thenReturn(...) defines behaviour, verify checks interactions, and ArgumentCaptor inspects arguments. AssertJ provides fluent, readable assertions. Good unit tests are fast, isolated and deterministic: inject dependencies through constructors, use a fixed Clock for time, and mock only boundaries you own, testing real collaborators where cheap. Integration tests with Testcontainers run against real databases in Docker.",
        use_cases=["Testing business logic in isolation.", "Table-driven tests for edge cases.", "Verifying interactions with external gateways.", "Integration tests against a real database with Testcontainers."],
        key_points=[
            "Arrange, act, assert; one behaviour per test.",
            "assertThrows returns the exception for further checks.",
            "@ParameterizedTest replaces copy-pasted tests.",
            "Mock boundaries (HTTP, DB gateways), not value objects.",
            "Constructor injection makes classes testable.",
        ],
        examples=[
            jx("JUnit 5 basics", "basic", "Assertions and exceptions.", """
                class PriceCalculatorTest {
                    private final PriceCalculator calc = new PriceCalculator();

                    @Test
                    @DisplayName("applies 10% discount above 100")
                    void discount() {
                        assertEquals(new BigDecimal("108.00"), calc.total(new BigDecimal("120.00")));
                    }

                    @Test
                    void rejectsNegative() {
                        var ex = assertThrows(IllegalArgumentException.class, () -> calc.total(new BigDecimal("-1")));
                        assertTrue(ex.getMessage().contains("negative"));
                    }
                }
            """),
            jx("Parameterised tests", "intermediate", "Table-driven edge cases.", """
                @ParameterizedTest(name = "{0} -> {1}")
                @CsvSource({
                    "'',        false",
                    "a@b.io,    true",
                    "no-at,     false",
                    "x@y,       true"
                })
                void validatesEmail(String input, boolean expected) {
                    assertEquals(expected, EmailValidator.isValid(input));
                }
            """),
            jx("Mockito stubs and verification", "intermediate", "Isolate a service from its gateway.", """
                @ExtendWith(MockitoExtension.class)
                class CheckoutServiceTest {
                    @Mock PaymentGateway gateway;
                    @InjectMocks CheckoutService service;

                    @Test
                    void chargesOnce() {
                        when(gateway.charge(any(), eq(4_200L))).thenReturn(new Receipt("r-1"));

                        Receipt r = service.checkout(new Cart(List.of(new Item("book", 4_200L))));

                        assertThat(r.id()).isEqualTo("r-1");                    // AssertJ
                        verify(gateway, times(1)).charge(any(), eq(4_200L));
                        verifyNoMoreInteractions(gateway);
                    }
                }
            """),
        ],
        commands=["@Test · @BeforeEach · @Nested", "assertThrows(Ex.class, () -> ...)", "@ParameterizedTest @CsvSource", "when(m.call()).thenReturn(v)", "verify(m).call(eq(x))", "./mvnw test -Dtest=PriceCalculatorTest"],
        gotchas=["Over-mocking couples tests to implementation details and breaks on every refactor.", "Tests depending on execution order, current time or random values are flaky.", "Mixing JUnit 4 and 5 annotations silently skips tests.", "Mockito strict stubs fail on unused stubbing: remove it instead of switching to lenient."],
        interview=[
            qa("basic", "What changed from JUnit 4 to JUnit 5?", "JUnit 5 is modular (Platform, Jupiter, Vintage), uses @BeforeEach/@AfterEach instead of @Before/@After, replaces runners and rules with the extension model, adds nested and parameterised tests, and requires Java 8+."),
            qa("intermediate", "Mock vs stub vs spy?", "A stub returns canned answers; a mock additionally verifies interactions; a spy wraps a real object and calls real methods unless stubbed. Mockito's mock() supports stubbing and verification; spy() creates partial mocks."),
            qa("intermediate", "What should you not mock?", "Value objects, records and collections, types you do not own (wrap them behind your own interface first), and simple collaborators that are cheap to use for real."),
            qa("advanced", "How do you test code that uses the database?", "Unit-test logic with mocked repositories, and write integration tests against the real database engine with Testcontainers, applying migrations, so SQL and mappings are verified without depending on a shared environment."),
        ],
        related=["build-tools", "spring-boot", "java-time"],
        flow=chain(
            ("Arrange", "mocks, input", "Arrange", "Create the object under test and stub its collaborators."),
            ("Act", "call method", "Act", "Call the behaviour being tested.", "call"),
            ("Assert", "assertEquals", "Assert", "Check the returned value or state.", "result"),
            ("Verify", "verify(mock)", "Verify", "Check important interactions with boundaries.", "calls"),
        ),
    ),
    topic(
        id="spring-boot", title="Spring Boot Basics", category="ecosystem", level="intermediate", code="SB",
        tagline="Auto-configuration, dependency injection, REST controllers and externalised config.",
        analogy="A furnished apartment. Spring Boot moves in the standard furniture (web server, JSON, connection pool) based on what you brought, and you only rearrange what you want differently.",
        what="Spring Framework provides an inversion-of-control container that creates beans and injects their dependencies, plus modules for web, data, security and more. Spring Boot adds auto-configuration (beans created based on the classpath and properties), starter dependencies, an embedded server (Tomcat by default) and production features via Actuator. A @SpringBootApplication class bootstraps component scanning and auto-configuration. Controllers annotated with @RestController map HTTP requests with @GetMapping and friends, and services are injected through constructors. Configuration lives in application.yml with profiles and can be bound to type-safe @ConfigurationProperties records; secrets must come from environment variables or a secret manager. Spring Boot 3 (2022) requires Java 17, moved to the jakarta.* namespace, and supports GraalVM native images; Boot 3.2 added virtual-thread support with spring.threads.virtual.enabled.",
        use_cases=["REST APIs and microservices.", "Batch jobs and message consumers.", "Data access with Spring Data JPA/JDBC.", "Health, metrics and readiness probes for Kubernetes."],
        key_points=[
            "Constructor injection; avoid field injection.",
            "Auto-configuration backs off when you define your own bean.",
            "Externalise config; secrets via env or vault.",
            "Actuator: /actuator/health, metrics; restrict exposure.",
            "Boot 3 = Java 17+ and jakarta.* packages.",
        ],
        examples=[
            jx("A minimal REST service", "basic", "Application, controller and service.", """
                @SpringBootApplication
                public class OrdersApplication {
                    public static void main(String[] args) { SpringApplication.run(OrdersApplication.class, args); }
                }

                @RestController
                @RequestMapping("/api/orders")
                class OrderController {
                    private final OrderService service;
                    OrderController(OrderService service) { this.service = service; }   // constructor injection

                    @GetMapping("/{id}")
                    OrderDto get(@PathVariable long id) { return service.find(id); }

                    @PostMapping
                    @ResponseStatus(HttpStatus.CREATED)
                    OrderDto create(@Valid @RequestBody CreateOrder req) { return service.create(req); }
                }
            """),
            jx("Type-safe configuration", "intermediate", "Records bound from application.yml.", """
                // application.yml
                //   payments:
                //     base-url: https://payments.internal
                //     timeout: 2s
                //     api-key: ${PAYMENTS_API_KEY}     # from the environment, never a literal
                //   spring.threads.virtual.enabled: true   # Boot 3.2+, Java 21
                @ConfigurationProperties(prefix = "payments")
                public record PaymentsProperties(URI baseUrl, Duration timeout, String apiKey) {}

                @Configuration
                @EnableConfigurationProperties(PaymentsProperties.class)
                class PaymentsConfig { }
            """),
            jx("Error handling", "intermediate", "Consistent problem responses (RFC 7807).", """
                @RestControllerAdvice
                class ApiErrors {
                    @ExceptionHandler(NotFoundException.class)
                    ProblemDetail notFound(NotFoundException e) {
                        ProblemDetail pd = ProblemDetail.forStatus(HttpStatus.NOT_FOUND);
                        pd.setDetail(e.getMessage());
                        return pd;
                    }
                }
            """),
        ],
        commands=["./mvnw spring-boot:run", "SPRING_PROFILES_ACTIVE=prod java -jar app.jar", "GET /actuator/health", "@ConfigurationProperties(prefix = \"x\")", "./mvnw spring-boot:build-image"],
        gotchas=["Field injection with @Autowired hides dependencies and complicates tests.", "Exposing all Actuator endpoints publicly leaks environment and heap data.", "@Transactional on private methods or self-invocation is ignored because of proxies.", "Upgrading Boot 2 to 3 requires changing javax.* imports to jakarta.*."],
        interview=[
            qa("basic", "What does Spring Boot add on top of Spring?", "Auto-configuration based on classpath and properties, curated starter dependencies, an embedded server, externalised configuration with profiles, and production features like Actuator health and metrics."),
            qa("intermediate", "Why prefer constructor injection?", "Dependencies are explicit and can be final, the object is never partially initialised, it is trivially constructible in unit tests without Spring, and circular dependencies surface early."),
            qa("intermediate", "How does auto-configuration work?", "Boot loads auto-configuration classes listed in META-INF/spring/...AutoConfiguration.imports. Each is guarded by conditions like @ConditionalOnClass and @ConditionalOnMissingBean, so it backs off when you define your own bean."),
            qa("advanced", "Why does @Transactional sometimes not work?", "Spring applies it through a proxy, so calls from within the same class (self-invocation) bypass the proxy, and private or final methods cannot be intercepted. Also, only unchecked exceptions trigger rollback by default."),
        ],
        related=["annotations", "jdbc-pools", "junit-mockito"],
        flow=chain(
            ("main()", "SpringApplication", "Start", "SpringApplication.run boots the context."),
            ("Auto-config", "conditions", "Auto-configure", "Beans are created based on classpath and properties.", "beans"),
            ("DI", "constructors", "Inject", "Dependencies are injected through constructors.", "inject"),
            ("Tomcat", "embedded", "Serve", "The embedded server starts and maps routes to controllers.", "HTTP"),
            ("Actuator", "health", "Operate", "Health and metrics endpoints serve probes and monitoring.", "probe"),
        ),
    ),
    topic(
        id="jdbc-pools", title="JDBC & Connection Pools", category="ecosystem", level="intermediate", code="DB",
        tagline="PreparedStatement, transactions and HikariCP done safely.",
        analogy="Opening a database connection is like setting up a phone call through an operator. A connection pool keeps a few lines open and passes them between callers, instead of dialling from scratch every time.",
        what="JDBC is Java's low-level database API: a DataSource gives Connections, which create PreparedStatements that return ResultSets. Always use PreparedStatement with ? placeholders so user input is bound as data, preventing SQL injection, and close resources with try-with-resources. Transactions are controlled with setAutoCommit(false), commit and rollback, and the isolation level determines visible anomalies. Opening physical connections is slow (TCP, TLS, authentication), so applications use a pool such as HikariCP (the Spring Boot default) that reuses connections; size it small (often around 10 per instance) based on database capacity rather than request count. Credentials must come from the environment or a secret manager, and connections should use TLS. Batching (addBatch/executeBatch) and fetch sizes improve bulk performance; higher-level tools like JPA/Hibernate, jOOQ or Spring JdbcTemplate build on JDBC.",
        use_cases=["Reading and writing relational data from services.", "Bulk imports with batched inserts.", "Transactional money transfers.", "Tuning pool size for a Kubernetes deployment."],
        key_points=[
            "PreparedStatement with ? placeholders, never string concatenation.",
            "try-with-resources for Connection, Statement, ResultSet.",
            "Explicit transactions for multi-statement units of work.",
            "Small pools; total connections = pool size x instances.",
            "Credentials from environment or vault; TLS to the database.",
        ],
        examples=[
            jx("Injection-safe query", "basic", "Concatenation vs placeholders.", """
                // Vulnerable: input "x' OR '1'='1" returns every row
                String bad = "SELECT * FROM users WHERE email = '" + email + "'";

                String sql = "SELECT id, name FROM users WHERE email = ?";
                try (Connection c = dataSource.getConnection();
                     PreparedStatement ps = c.prepareStatement(sql)) {
                    ps.setString(1, email);
                    try (ResultSet rs = ps.executeQuery()) {
                        while (rs.next()) System.out.println(rs.getLong("id") + " " + rs.getString("name"));
                    }
                }
            """),
            jx("Transactions", "intermediate", "Commit both updates or neither.", """
                try (Connection c = dataSource.getConnection()) {
                    c.setAutoCommit(false);
                    try (PreparedStatement debit = c.prepareStatement("UPDATE accounts SET balance = balance - ? WHERE id = ?");
                         PreparedStatement credit = c.prepareStatement("UPDATE accounts SET balance = balance + ? WHERE id = ?")) {
                        debit.setLong(1, cents); debit.setLong(2, from); debit.executeUpdate();
                        credit.setLong(1, cents); credit.setLong(2, to); credit.executeUpdate();
                        c.commit();
                    } catch (SQLException e) {
                        c.rollback();
                        throw e;
                    }
                }
            """),
            jx("HikariCP pool with secrets from the environment", "intermediate", "Configure once at startup.", """
                HikariConfig cfg = new HikariConfig();
                cfg.setJdbcUrl(System.getenv("DB_URL"));            // e.g. jdbc:postgresql://db:5432/app?sslmode=verify-full
                cfg.setUsername(System.getenv("DB_USER"));
                cfg.setPassword(System.getenv("DB_PASSWORD"));      // never a literal in source
                cfg.setMaximumPoolSize(10);
                cfg.setConnectionTimeout(3_000);
                cfg.setMaxLifetime(Duration.ofMinutes(30).toMillis());
                HikariDataSource dataSource = new HikariDataSource(cfg);
            """),
        ],
        commands=["conn.prepareStatement(\"... WHERE id = ?\")", "ps.setString(1, v) / executeQuery()", "conn.setAutoCommit(false); commit()", "ps.addBatch(); ps.executeBatch()", "spring.datasource.hikari.maximum-pool-size=10"],
        gotchas=["Not closing connections leaks pool slots until requests time out waiting.", "Huge pools multiplied by many pods exhaust the database's max_connections.", "Placeholders cannot bind identifiers (table/column names); allow-list them instead.", "Long transactions hold locks and connections; keep them short and avoid remote calls inside."],
        interview=[
            qa("basic", "Statement vs PreparedStatement?", "PreparedStatement precompiles SQL with ? placeholders and binds values as data, preventing SQL injection and allowing plan reuse. Statement concatenates SQL text and should not be used with user input."),
            qa("intermediate", "Why use a connection pool?", "Creating a physical connection requires network, TLS and authentication round trips. A pool keeps connections open and lends them out, reducing latency and capping concurrent database load."),
            qa("intermediate", "How large should the pool be?", "Smaller than intuition suggests: database throughput is limited by cores and disk, so roughly cores x 2 (plus spindles) for the database, divided across all application instances. Measure wait time and database load rather than matching thread count."),
            qa("advanced", "What isolation levels exist and what do they prevent?", "READ UNCOMMITTED allows dirty reads; READ COMMITTED prevents them; REPEATABLE READ also prevents non-repeatable reads; SERIALIZABLE prevents phantoms and write skew. Higher levels add locking or abort-and-retry costs."),
        ],
        related=["exceptions", "spring-boot", "java-security"],
        flow=chain(
            ("Request", "needs data", "Borrow", "A request borrows a connection from the pool."),
            ("Pool", "HikariCP", "Reuse", "An idle, already-authenticated connection is handed out.", "conn"),
            ("Prepared", "? placeholders", "Bind", "SQL is prepared and parameters are bound safely.", "params"),
            ("Transaction", "commit", "Execute", "Statements run in a transaction and are committed or rolled back.", "SQL"),
            ("Return", "close()", "Return", "close() returns the connection to the pool.", "release"),
        ),
    ),
    topic(
        id="design-patterns", title="Design Patterns in Java", category="ecosystem", level="intermediate", code="DP",
        tagline="Builder, singleton, strategy, factory, observer and decorator, the modern way.",
        analogy="Patterns are well-known chess openings: not rules you must follow, but proven moves with names, so teammates instantly understand the plan.",
        what="Design patterns are reusable solutions to recurring design problems, catalogued by the Gang of Four in 1994. In modern Java several are simplified by language features. Builder handles objects with many optional parameters and keeps them immutable; records cover the simple cases. Singleton is best implemented as an enum or managed by a DI container rather than with static state. Strategy, Command and Template Method often collapse into lambdas and functional interfaces since Java 8. Factory methods such as List.of and Optional.of hide construction details, and sealed interfaces with pattern matching (17/21) can replace Visitor. Decorator wraps behaviour (like BufferedReader around Reader), and Observer underlies listeners and reactive streams. Apply patterns to solve a real problem, not to show them off.",
        use_cases=["Builders for complex request or config objects.", "Pluggable pricing or routing strategies.", "Decorating repositories with caching or metrics.", "Event listeners and domain events."],
        key_points=[
            "Builder for many optional parameters; records for plain data.",
            "Enum singleton or DI-managed singletons.",
            "Strategy via lambdas and functional interfaces.",
            "Decorator composes behaviour without subclass explosion.",
            "Sealed types + switch can replace Visitor.",
        ],
        examples=[
            jx("Builder", "basic", "Readable construction of an immutable object.", """
                public final class HttpCall {
                    private final URI uri; private final Duration timeout; private final Map<String, String> headers;
                    private HttpCall(Builder b) { uri = b.uri; timeout = b.timeout; headers = Map.copyOf(b.headers); }
                    public static Builder to(URI uri) { return new Builder(uri); }

                    public static final class Builder {
                        private final URI uri;
                        private Duration timeout = Duration.ofSeconds(5);
                        private final Map<String, String> headers = new LinkedHashMap<>();
                        private Builder(URI uri) { this.uri = Objects.requireNonNull(uri); }
                        public Builder timeout(Duration t) { this.timeout = t; return this; }
                        public Builder header(String k, String v) { headers.put(k, v); return this; }
                        public HttpCall build() { return new HttpCall(this); }
                    }
                }
                HttpCall call = HttpCall.to(URI.create("https://api.example.com")).timeout(Duration.ofSeconds(2)).header("Accept", "application/json").build();
            """),
            jx("Strategy: Java 7 class vs Java 8 lambda", "intermediate", "Behaviour as a value.", """
                // Java 7: one class per strategy
                interface Discount { BigDecimal apply(BigDecimal amount); }
                class BlackFriday implements Discount {
                    public BigDecimal apply(BigDecimal a) { return a.multiply(new BigDecimal("0.7")); }
                }

                // Java 8+: lambdas in a map
                Map<String, UnaryOperator<BigDecimal>> discounts = Map.of(
                        "none", a -> a,
                        "black-friday", a -> a.multiply(new BigDecimal("0.7")),
                        "loyalty", a -> a.subtract(new BigDecimal("5")).max(BigDecimal.ZERO));
                BigDecimal total = discounts.getOrDefault(code, a -> a).apply(amount);
            """),
            jx("Decorator", "intermediate", "Add caching around any repository.", """
                interface ProductRepo { Optional<Product> find(String sku); }

                final class CachingProductRepo implements ProductRepo {
                    private final ProductRepo delegate;
                    private final Map<String, Optional<Product>> cache = new ConcurrentHashMap<>();
                    CachingProductRepo(ProductRepo delegate) { this.delegate = delegate; }

                    @Override public Optional<Product> find(String sku) {
                        return cache.computeIfAbsent(sku, delegate::find);
                    }
                }
                ProductRepo repo = new CachingProductRepo(new JdbcProductRepo(dataSource));
            """),
        ],
        commands=["enum Singleton { INSTANCE }", "Builder: X.builder().a(1).build()", "Map<String, Function<..>> strategies", "new BufferedReader(new FileReader(f)) (decorator)", "sealed interface + switch (visitor replacement)"],
        gotchas=["Classic lazy singletons with static mutable state make testing and concurrency hard.", "Pattern overuse (factories of factories) adds indirection without benefit.", "Builders without validation in build() let invalid objects escape."],
        interview=[
            qa("basic", "When would you use the Builder pattern?", "When a constructor would have many parameters, especially optional ones, or when you want readable, validated construction of an immutable object. For a few required fields a record or static factory is simpler."),
            qa("intermediate", "What is the best way to implement a singleton in Java?", "A single-element enum: the JVM guarantees one instance, thread-safe initialisation, and protection against reflection and serialization. In applications, letting a DI container manage a singleton-scoped bean is usually even better."),
            qa("intermediate", "How have lambdas changed classic patterns?", "Strategy, Command, Template Method and Observer often need only a functional interface and a lambda or method reference instead of a class hierarchy, reducing boilerplate dramatically."),
            qa("advanced", "Decorator vs inheritance?", "Decorators wrap an object implementing the same interface and add behaviour at runtime, combining freely (caching plus metrics plus retries). Inheritance fixes the combination at compile time and leads to a subclass explosion."),
        ],
        related=["oop-basics", "enums", "functional-interfaces", "immutability"],
        flow=chain(
            ("Problem", "recurring", "Recognise", "Identify a recurring design problem, like many optional params."),
            ("Pattern", "named solution", "Choose", "Pick the pattern that fits, e.g. Builder or Strategy.", "pattern"),
            ("Modern Java", "lambdas, records", "Simplify", "Use lambdas, records, enums or sealed types to cut boilerplate.", "simplify"),
            ("Apply", "small scope", "Apply", "Apply it where it pays off, and stop there.", "code"),
        ),
    ),
    topic(
        id="java-security", title="Java Security & Cryptography", category="ecosystem", level="advanced", code="SX",
        tagline="SHA-256, AES-GCM, SecureRandom, password hashing, KeyStores and TLS 1.3.",
        analogy="Security is a bank vault, not a padlock you invent yourself. Use the vault the experts built (JCA algorithms), keep the keys in a separate safe (KMS), and check the guard's ID badge (certificates) every time.",
        what="The Java Cryptography Architecture (JCA/JCE) provides vetted primitives through provider-based factories such as MessageDigest, Cipher, Mac, KeyGenerator, SecureRandom and KeyStore. Use SHA-256 or stronger for hashing; MD5 and SHA-1 are broken for security purposes. For encryption use AES/GCM/NoPadding with a 256-bit key and a fresh random 12-byte IV for every message, which gives confidentiality and integrity; never use ECB, unauthenticated CBC, DES, 3DES or RC4. Random tokens and IVs must come from SecureRandom, never java.util.Random. Passwords are hashed with slow algorithms (Argon2id or bcrypt via libraries, or PBKDF2WithHmacSHA256 with a high iteration count) and compared in constant time. Keys and secrets belong in a KMS, vault or KeyStore whose password comes from the environment, never in source code. TLS should be restricted to TLSv1.3 (Java 11+), and every certificate in a KeyStore must be checked for expiry, key strength (RSA 2048+ or EC P-256+), a SHA-2 signature and whether it is self-signed.",
        use_cases=["Encrypting sensitive fields at rest.", "Generating session tokens and reset links.", "Hashing and verifying user passwords.", "Configuring mutual TLS between services."],
        key_points=[
            "SHA-256+ for digests; HMAC-SHA256 for message authentication.",
            "AES-256-GCM, 12-byte random IV, 128-bit tag; never reuse an IV with the same key.",
            "SecureRandom for all security-relevant randomness.",
            "Slow, salted password hashing; MessageDigest.isEqual for constant-time compare.",
            "TLSv1.3; validate certificates; keys from KMS/env, never hardcoded.",
        ],
        examples=[
            jx("SHA-256 and HMAC", "basic", "Integrity checks without MD5 or SHA-1.", """
                byte[] digest = MessageDigest.getInstance("SHA-256").digest(fileBytes);
                String hex = HexFormat.of().formatHex(digest);                   // Java 17

                byte[] macKey = Base64.getDecoder().decode(System.getenv("WEBHOOK_HMAC_KEY"));   // from a secret store
                Mac mac = Mac.getInstance("HmacSHA256");
                mac.init(new SecretKeySpec(macKey, "HmacSHA256"));
                byte[] expected = mac.doFinal(payload);
                boolean valid = MessageDigest.isEqual(expected, receivedSignature);   // constant time
            """),
            jx("AES-256-GCM encryption", "advanced", "Authenticated encryption with a random 12-byte IV.", """
                // Key: generated once and stored in a KMS / KeyStore, not in code
                KeyGenerator kg = KeyGenerator.getInstance("AES");
                kg.init(256);
                SecretKey key = kg.generateKey();

                SecureRandom rng = new SecureRandom();
                byte[] iv = new byte[12];                       // fresh for every message
                rng.nextBytes(iv);

                Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
                cipher.init(Cipher.ENCRYPT_MODE, key, new GCMParameterSpec(128, iv));
                cipher.updateAAD("order:42".getBytes(StandardCharsets.UTF_8));   // bound context
                byte[] ciphertext = cipher.doFinal(plaintext);
                byte[] stored = ByteBuffer.allocate(iv.length + ciphertext.length).put(iv).put(ciphertext).array();

                // Decrypt: same key, IV from the prefix, same AAD; tampering throws AEADBadTagException
            """),
            jx("Tokens, passwords, KeyStore and TLS 1.3", "advanced", "Everyday secure defaults.", """
                byte[] tokenBytes = new byte[32];
                new SecureRandom().nextBytes(tokenBytes);
                String resetToken = Base64.getUrlEncoder().withoutPadding().encodeToString(tokenBytes);

                byte[] salt = new byte[16];
                new SecureRandom().nextBytes(salt);
                PBEKeySpec spec = new PBEKeySpec(passwordChars, salt, 600_000, 256);
                byte[] hash = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256").generateSecret(spec).getEncoded();
                spec.clearPassword();

                char[] ksPass = System.getenv("KEYSTORE_PASSWORD").toCharArray();   // never a literal
                KeyStore ks = KeyStore.getInstance("PKCS12");
                try (InputStream in = Files.newInputStream(Path.of("/etc/app/tls.p12"))) { ks.load(in, ksPass); }
                X509Certificate cert = (X509Certificate) ks.getCertificate("server");
                cert.checkValidity();                                   // throws if expired or not yet valid
                System.out.println(cert.getSigAlgName() + " " + cert.getPublicKey().getAlgorithm());
                // Also verify RSA >= 2048 / EC P-256+, SHA-2 signature, and whether issuer equals subject (self-signed).

                SSLContext tls = SSLContext.getInstance("TLSv1.3");
                KeyManagerFactory kmf = KeyManagerFactory.getInstance(KeyManagerFactory.getDefaultAlgorithm());
                kmf.init(ks, ksPass);
                tls.init(kmf.getKeyManagers(), null, new SecureRandom());   // null = default trust managers
            """),
        ],
        commands=["MessageDigest.getInstance(\"SHA-256\")", "Cipher.getInstance(\"AES/GCM/NoPadding\")", "new GCMParameterSpec(128, iv12)", "new SecureRandom().nextBytes(buf)", "SSLContext.getInstance(\"TLSv1.3\")", "keytool -list -v -keystore tls.p12"],
        gotchas=["Reusing an IV with the same AES-GCM key destroys both confidentiality and integrity.", "Cipher.getInstance(\"AES\") defaults to ECB mode: always specify AES/GCM/NoPadding.", "java.util.Random and Math.random are predictable and unsuitable for tokens.", "Trust-all TrustManagers or disabled hostname verification make TLS useless, and expired or self-signed KeyStore certificates must be flagged (self-signed only for dev or explicitly configured internal trust)."],
        interview=[
            qa("intermediate", "Why AES-GCM instead of AES-CBC or ECB?", "ECB leaks patterns because identical blocks encrypt identically, and CBC provides no integrity and is prone to padding-oracle attacks. GCM is an AEAD mode giving confidentiality plus an authentication tag that detects tampering, as long as the 12-byte IV is never reused with the same key."),
            qa("intermediate", "SecureRandom vs Random?", "java.util.Random is a fast linear congruential generator whose output can be predicted from a few values. SecureRandom is a cryptographically strong generator seeded from the OS, required for keys, IVs, salts, tokens and session IDs."),
            qa("advanced", "How should passwords be stored?", "Never encrypted or hashed with a fast hash. Use a slow, salted algorithm such as Argon2id or bcrypt from a vetted library, or PBKDF2WithHmacSHA256 with around 600,000 iterations, a unique per-user salt, and constant-time comparison."),
            qa("advanced", "What would you check about a certificate loaded from a KeyStore?", "That it is within its validity period, uses a strong key (RSA 2048+ or EC P-256+), is signed with a SHA-2 algorithm rather than MD5 or SHA-1, and whether it is self-signed, which is only acceptable for development or explicitly configured internal trust. keytool -list -v or openssl x509 -text shows these fields."),
            qa("intermediate", "Where should encryption keys and secrets live?", "In a KMS, HSM or secret manager (or a protected KeyStore whose password is injected at runtime), never in source code or images. Separate keys by purpose, rotate them, and audit access."),
        ],
        related=["http-client", "serialization", "jdbc-pools", "nio-files"],
        flow=chain(
            ("Key", "KMS / KeyStore", "Get key", "A 256-bit AES key is loaded from a KMS or KeyStore, never from code."),
            ("IV", "SecureRandom 12B", "Fresh IV", "A new random 12-byte IV is generated for this message.", "iv"),
            ("AES-GCM", "encrypt + tag", "Encrypt", "AES/GCM/NoPadding produces ciphertext plus a 128-bit tag.", "ct+tag"),
            ("Store", "iv || ct", "Store", "The IV is stored next to the ciphertext; it is not secret.", "blob"),
            ("Decrypt", "verify tag", "Verify", "Decryption checks the tag; any tampering throws.", "plain"),
        ),
    ),
]

TOPICS = _LANGUAGE + _CORE + _RUNTIME + _MODERN + _VERSIONS + _ECOSYSTEM

SCENARIOS = [
    {"level": "intermediate", "topic": "concurrent-utils", "q": "A per-endpoint request counter stored in a HashMap shows lower totals than the load balancer reports.", "a": "HashMap is not thread-safe and get-then-put increments lose updates under concurrency. Switch to ConcurrentHashMap<String, LongAdder> and call computeIfAbsent(route, r -> new LongAdder()).increment(), or merge(route, 1L, Long::sum). LongAdder scales best for hot counters."},
    {"level": "advanced", "topic": "java-security", "q": "A security review finds customer data encrypted with Cipher.getInstance(\"AES\") and a key stored as a constant in the code.", "a": "That defaults to AES/ECB, which leaks patterns and has no integrity, and the hardcoded key must be treated as compromised. Rotate the key into a KMS or KeyStore loaded via an environment-provided password, re-encrypt data with AES/GCM/NoPadding using a 256-bit key and a fresh random 12-byte IV per record stored alongside the ciphertext, and add a scanner to CI to block hardcoded secrets."},
    {"level": "intermediate", "topic": "jdbc-pools", "q": "After scaling a service from 3 to 30 pods, the database starts rejecting connections.", "a": "Each pod has its own pool, so 30 x maximumPoolSize exceeded the database's max_connections. Reduce the per-pod pool (often 5-10), make sure connections are closed via try-with-resources, consider a server-side pooler like PgBouncer, and size based on database capacity rather than pod count."},
    {"level": "advanced", "topic": "profiling-leaks", "q": "Old-generation usage after each full GC creeps up over several days until the service hits OutOfMemoryError.", "a": "That is a leak: objects stay reachable. Enable -XX:+HeapDumpOnOutOfMemoryError, take a jcmd GC.heap_dump when usage is high, and analyse the dominator tree and GC-root paths in Eclipse MAT. Typical culprits are unbounded static maps or caches, ThreadLocals in pooled threads and listeners never removed; replace them with bounded caches and cleanup in finally blocks."},
    {"level": "intermediate", "topic": "completable-future", "q": "A dashboard that aggregates five downstream calls with CompletableFuture.supplyAsync becomes slow whenever parallel streams run elsewhere in the app.", "a": "Without an executor argument, supplyAsync uses the shared common ForkJoinPool, and blocking HTTP calls starve it. Pass a dedicated bounded executor (or a virtual-thread executor on Java 21), add orTimeout with a fallback via exceptionally, and keep parallel streams for CPU-bound work only."},
    {"level": "basic", "topic": "equals-hashcode", "q": "Duplicate customers appear in a HashSet<Customer> even though equals compares email addresses.", "a": "Customer overrides equals but not hashCode, so equal objects land in different buckets. Implement hashCode from the same immutable field (email), or convert Customer to a record, and make sure the email cannot change while the object is in the set."},
]
