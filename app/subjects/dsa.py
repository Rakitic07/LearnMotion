"""dsa subject content."""

from ._dsl import chain, ex, qa, topic

CATEGORIES = [
    {"id": "foundations", "title": "Foundations", "color": "sky", "blurb": "Complexity analysis, memory and recursion."},
    {"id": "linear", "title": "Linear Structures & Hashing", "color": "mint", "blurb": "Arrays, strings, lists, stacks, queues and hash tables."},
    {"id": "sorting", "title": "Sorting", "color": "rose", "blurb": "Comparison and non-comparison sorts, stability and lower bounds."},
    {"id": "searching", "title": "Searching & Array Patterns", "color": "lemon", "blurb": "Binary search, two pointers, sliding windows and prefix sums."},
    {"id": "trees", "title": "Trees & Heaps", "color": "lilac", "blurb": "Binary trees, BSTs, heaps, tries, union-find and range trees."},
    {"id": "graphs", "title": "Graphs", "color": "peach", "blurb": "Representations, traversals, shortest paths and spanning trees."},
    {"id": "techniques", "title": "Techniques & Patterns", "color": "slate", "blurb": "DP, greedy, backtracking, bits and interview strategy."},
]

TOPICS = []

TOPICS += [
    topic(
        "big-o", "Big-O, Theta, Omega & Amortised Analysis", "foundations", "basic", "BO",
        "Describe how running time grows with input size, ignoring constants and machines.",
        "Big-O is like describing a commute by how it scales: walking doubles when the distance doubles, a flight barely changes. You care about the shape of the growth, not whether today's traffic added five minutes.",
        "Asymptotic analysis describes how the number of basic operations grows as the input size n grows. Big-O gives an upper bound (f grows no faster than g), Big-Omega a lower bound, and Big-Theta a tight bound when both hold. Constants and lower-order terms are dropped, so 3n^2 + 10n + 7 is Theta(n^2). The common ladder is O(1) < O(log n) < O(n) < O(n log n) < O(n^2) < O(2^n) < O(n!). Best, average and worst case are separate questions from O/Omega/Theta: you can state a Theta bound for the worst case of an algorithm. Amortised analysis averages the cost over a sequence of operations, so a dynamic array append is O(1) amortised even though an occasional resize costs O(n). Amortised is a guarantee over any sequence, unlike average case, which depends on an input distribution. In interviews, state time and space, name the variables (n, m, V, E) and explain the dominant term.",
        ["Choosing between two algorithms before writing code.", "Predicting whether a solution fits a 1-second limit for n = 10^5.", "Explaining why a list append is cheap but list.insert(0, x) is not.", "Spotting hidden quadratic loops in code review."],
        [
            "O is an upper bound, Omega a lower bound, Theta a tight bound.",
            "Drop constants and lower-order terms: 5n + 3 is O(n).",
            "Nested loops over the same input usually multiply: O(n * m).",
            "Halving the problem each step gives O(log n).",
            "Amortised O(1) means total cost of k operations is O(k), not every operation is O(1).",
        ],
        [
            ex("Counting operations", "basic", "Count basic steps for linear, quadratic and logarithmic loops.", "python", """
                def linear(n):
                    ops = 0
                    for _ in range(n):
                        ops += 1
                    return ops

                def quadratic(n):
                    ops = 0
                    for i in range(n):
                        for j in range(n):
                            ops += 1
                    return ops

                def logarithmic(n):
                    ops = 0
                    while n > 1:
                        n //= 2
                        ops += 1
                    return ops

                for n in (8, 16, 32, 64):
                    print(f"n={n:3}  O(n)={linear(n):4}  O(n^2)={quadratic(n):5}  O(log n)={logarithmic(n)}")
            """),
            ex("Amortised dynamic array", "intermediate", "Doubling capacity makes the total copy cost linear.", "python", """
                class DynArray:
                    def __init__(self):
                        self.cap, self.size, self.copies = 1, 0, 0
                        self.data = [None]

                    def append(self, x):
                        if self.size == self.cap:
                            self.cap *= 2
                            new = [None] * self.cap
                            for i in range(self.size):
                                new[i] = self.data[i]
                                self.copies += 1
                            self.data = new
                        self.data[self.size] = x
                        self.size += 1

                a = DynArray()
                for k in range(1, 1025):
                    a.append(k)
                    if k in (16, 128, 1024):
                        print(f"appends={k:5} copies={a.copies:5} copies/append={a.copies / k:.2f}")
                assert a.copies < 2 * a.size
            """),
        ],
        ["O(1) < O(log n) < O(n) < O(n log n) < O(n^2) < O(2^n)", "n=10^5 -> O(n log n) ok, O(n^2) too slow", "list.append amortised O(1); list.insert(0, x) O(n)", "dict/set lookup O(1) average, O(n) worst", "Sum of 1+2+...+n = n(n+1)/2 -> O(n^2)"],
        ["Big-O is not 'worst case'; it is an upper bound you can apply to any case.", "Two separate inputs give O(n + m) or O(n * m), not O(n).", "Hidden costs: slicing, 'in' on a list and string concatenation in loops are O(n).", "Amortised is not average case; it holds for every sequence of operations."],
        [
            qa("basic", "What is the difference between Big-O, Big-Omega and Big-Theta?", "Big-O is an asymptotic upper bound, Big-Omega a lower bound, and Big-Theta means both hold so the growth is tight. Saying binary search is O(n) is technically true but uninformative; Theta(log n) worst case is precise. Interviewers usually say Big-O but mean the tight bound."),
            qa("basic", "Why do we drop constants in Big-O?", "Constants depend on hardware, language and implementation, while the growth rate determines behaviour for large n. An O(n) algorithm with a large constant eventually beats an O(n^2) one. Constants still matter in practice for small n, which is why Timsort uses insertion sort on short runs."),
            qa("intermediate", "What does amortised O(1) mean for list.append?", "Most appends write into spare capacity in O(1); occasionally the array is full and is reallocated with geometric growth, copying O(n) elements. Because capacity grows by a constant factor, the total copying over n appends is O(n), so each append costs O(1) on average over the sequence. It is a worst-case guarantee over sequences, not a probabilistic claim."),
            qa("intermediate", "What is the complexity of two nested loops where the inner runs i times?", "The inner loop runs 0 + 1 + ... + (n-1) = n(n-1)/2 times, which is Theta(n^2). The triangle shape halves the constant but does not change the growth rate."),
            qa("advanced", "How do average case and amortised analysis differ?", "Average case assumes a probability distribution over inputs (for example, random pivots or random keys) and computes the expected cost. Amortised analysis makes no probabilistic assumption: it bounds the total cost of any sequence of operations, using techniques such as the aggregate, accounting or potential method."),
        ],
        ["space-complexity", "arrays-dynamic", "recursion"],
        chain(
            ("Write loops", "count steps", "Model the cost", "Count how many times the innermost statement runs as a function of n.", ),
            ("f(n)=3n^2+5n", "exact count", "Exact cost", "For a double loop plus a single loop you might get 3n^2 + 5n + 2 basic operations.", "count"),
            ("Drop terms", "keep dominant", "Simplify", "Lower-order terms and constants are dropped because n^2 dominates for large n.", "f(n)"),
            ("Theta(n^2)", "tight bound", "State the class", "The algorithm is Theta(n^2): doubling n roughly quadruples the work.", "n^2"),
        ),
    ),
    topic(
        "space-complexity", "Space Complexity & Memory", "foundations", "basic", "SC",
        "How much extra memory an algorithm needs as n grows, including the call stack.",
        "Space complexity is the size of your scratch paper. Some methods need a single sticky note no matter how big the problem, others need a copy of the whole book.",
        "Space complexity measures memory used as a function of input size. Auxiliary space counts only the extra memory beyond the input, and is usually what interviewers mean. Recursion consumes stack space proportional to the maximum depth, so a naive recursive DFS on a path-shaped tree uses O(n) space. An algorithm is in-place if it uses O(1) (sometimes O(log n)) auxiliary space, like heap sort or an in-place reversal. Memoisation trades space for time by storing subresults. In Python, slicing creates copies, so arr[1:] inside recursion silently adds O(n) per call. Generators and iterators let you stream data in O(1) space instead of materialising lists.",
        ["Deciding between merge sort (O(n) extra) and heap sort (O(1) extra) on constrained devices.", "Reducing a 2-D DP table to two rows.", "Streaming a huge log file with generators.", "Avoiding RecursionError by converting deep recursion to iteration."],
        [
            "Auxiliary space excludes the input; total space includes it.",
            "Recursion depth d costs O(d) stack frames.",
            "In-place means O(1) or O(log n) extra memory.",
            "Slicing and list comprehensions allocate new memory.",
            "Time-space trade-off: caches and lookup tables buy speed with memory.",
        ],
        [
            ex("In-place vs copy", "basic", "Reverse a list with O(1) extra space versus building a copy.", "python", """
                def reverse_in_place(a):
                    i, j = 0, len(a) - 1
                    while i < j:
                        a[i], a[j] = a[j], a[i]
                        i += 1
                        j -= 1
                    return a

                def reverse_copy(a):
                    return [a[k] for k in range(len(a) - 1, -1, -1)]

                data = [1, 2, 3, 4, 5]
                print("copy:", reverse_copy(data), "original kept:", data)
                print("in place:", reverse_in_place(data), "original changed:", data)
            """),
            ex("DP rolling rows", "intermediate", "Grid path count with a full table vs a single row.", "python", """
                def paths_full(r, c):
                    t = [[1] * c for _ in range(r)]
                    for i in range(1, r):
                        for j in range(1, c):
                            t[i][j] = t[i - 1][j] + t[i][j - 1]
                    return t[-1][-1]

                def paths_row(r, c):
                    row = [1] * c
                    for _ in range(1, r):
                        for j in range(1, c):
                            row[j] += row[j - 1]
                    return row[-1]

                print(paths_full(5, 6), paths_row(5, 6))
                assert paths_full(7, 7) == paths_row(7, 7) == 924
                print("full table cells:", 7 * 7, "rolling row cells:", 7)
            """),
            ex("Generator streaming", "basic", "sum over a generator never builds the full list.", "python", """
                import sys

                squares_list = [i * i for i in range(10_000)]
                squares_gen = (i * i for i in range(10_000))
                print("list bytes:", sys.getsizeof(squares_list))
                print("generator bytes:", sys.getsizeof(squares_gen))
                print(sum(squares_gen) == sum(squares_list))
            """),
        ],
        ["Recursion depth d -> O(d) stack", "arr[1:] copies O(n)", "sys.getsizeof(obj)", "sys.getrecursionlimit() (default 1000)", "Rolling DP rows: O(n*m) -> O(m)"],
        ["Forgetting the recursion stack when claiming O(1) space.", "Output arrays are usually not counted as auxiliary space, but say so explicitly.", "Python lists store pointers, so a list of ints uses far more memory than a C array."],
        [
            qa("basic", "What is auxiliary space?", "The extra memory an algorithm uses beyond its input. Merge sort needs O(n) auxiliary space for the merge buffer, while heap sort needs O(1). Total space adds the input size on top."),
            qa("basic", "Does recursion use extra space?", "Yes. Each active call holds a stack frame, so space is proportional to the maximum recursion depth. Balanced recursion like merge sort uses O(log n) stack, but a skewed tree or naive quicksort worst case can use O(n)."),
            qa("intermediate", "How can you reduce the space of a 2-D DP?", "If row i only depends on row i-1 (and the current row), keep two rows or a single row updated in the right order. This turns O(n*m) space into O(m) without changing time. You lose the ability to reconstruct the path unless you store extra information."),
            qa("intermediate", "Is quicksort in-place?", "It partitions within the array using O(1) extra memory per level, so it is called in-place, but recursion uses O(log n) stack on average and O(n) in the worst case. Recursing into the smaller side first and looping on the larger bounds the stack at O(log n)."),
        ],
        ["big-o", "recursion", "dynamic-programming"],
        chain(
            ("Input n", "given data", "Start", "The input itself occupies O(n); we measure what the algorithm adds."),
            ("Variables", "O(1)", "Scalars", "Counters, indices and pointers add constant space.", "n"),
            ("Buffers", "O(n) copies", "Allocations", "Merge buffers, hash maps and slices add memory proportional to their size.", "data"),
            ("Call stack", "O(depth)", "Recursion", "Every pending recursive call holds a frame until it returns.", "frames"),
            ("Total aux", "max of parts", "Report", "Auxiliary space is the peak of these extra allocations, for example O(n) for merge sort.", "peak"),
        ),
    ),
    topic(
        "recursion", "Recursion & the Call Stack", "foundations", "basic", "RC",
        "A function that solves a problem by calling itself on smaller inputs until a base case.",
        "Recursion is a stack of Russian dolls: you open each doll until you reach the smallest solid one, then you close them back up in reverse order.",
        "A recursive function has a base case that returns directly and a recursive case that reduces the problem and calls itself. Each call pushes a frame (arguments, locals, return address) onto the call stack, and frames are popped in last-in-first-out order when calls return. The recurrence relation describes cost: T(n) = T(n-1) + O(1) is O(n), T(n) = 2T(n/2) + O(n) is O(n log n), and T(n) = 2T(n-1) + O(1) is O(2^n). Missing or unreachable base cases cause infinite recursion and, in Python, RecursionError after about 1000 frames. Python does not perform tail-call optimisation, so deep linear recursion should be converted to a loop or an explicit stack. Overlapping subproblems (like naive Fibonacci) are a signal to add memoisation. Recursion is natural for trees, divide and conquer and backtracking.",
        ["Tree and graph traversals.", "Divide and conquer such as merge sort.", "Backtracking over permutations and subsets.", "Parsing nested structures like JSON or expressions."],
        [
            "Always define a base case that is reached for every input.",
            "Each call must make progress toward the base case.",
            "Stack depth equals space cost; Python's default limit is about 1000.",
            "Recurrences like T(n) = 2T(n/2) + n are solved with the Master theorem.",
            "Any recursion can be rewritten with an explicit stack.",
        ],
        [
            ex("Factorial and trace", "basic", "Show calls going down and returns coming back up.", "python", """
                def fact(n, depth=0):
                    pad = "  " * depth
                    print(f"{pad}fact({n}) called")
                    if n <= 1:
                        print(f"{pad}base case -> 1")
                        return 1
                    result = n * fact(n - 1, depth + 1)
                    print(f"{pad}fact({n}) returns {result}")
                    return result

                assert fact(4) == 24
            """),
            ex("Recursion vs explicit stack", "intermediate", "Sum a nested list recursively and iteratively.", "python", """
                def nested_sum(x):
                    if isinstance(x, int):
                        return x
                    return sum(nested_sum(item) for item in x)

                def nested_sum_iter(x):
                    total, stack = 0, [x]
                    while stack:
                        cur = stack.pop()
                        if isinstance(cur, int):
                            total += cur
                        else:
                            stack.extend(cur)
                    return total

                data = [1, [2, [3, 4]], [[5]], 6]
                print(nested_sum(data), nested_sum_iter(data))
                assert nested_sum(data) == nested_sum_iter(data) == 21
            """),
            ex("Exponential vs memoised", "intermediate", "Count calls of naive Fibonacci versus lru_cache.", "python", """
                from functools import lru_cache

                calls = 0
                def fib(n):
                    global calls
                    calls += 1
                    return n if n < 2 else fib(n - 1) + fib(n - 2)

                @lru_cache(maxsize=None)
                def fib_memo(n):
                    return n if n < 2 else fib_memo(n - 1) + fib_memo(n - 2)

                print("fib(20) =", fib(20), "naive calls:", calls)
                print("fib_memo(20) =", fib_memo(20), "cache info:", fib_memo.cache_info())
            """),
        ],
        ["T(n)=T(n-1)+O(1) -> O(n)", "T(n)=2T(n/2)+O(n) -> O(n log n)", "T(n)=2T(n-1)+O(1) -> O(2^n)", "sys.setrecursionlimit(10_000) (use sparingly)", "@functools.lru_cache(maxsize=None)"],
        ["No tail-call optimisation in Python; deep recursion raises RecursionError.", "Mutable default arguments shared across recursive calls cause bugs.", "Passing slices (arr[1:]) adds O(n) copying per call."],
        [
            qa("basic", "What happens on the call stack during recursion?", "Each call pushes a frame holding its parameters and local variables. When the base case returns, frames are popped in reverse order and each caller combines the returned value. The maximum number of frames alive at once is the recursion depth."),
            qa("basic", "What causes a stack overflow in recursion?", "Either a missing or unreachable base case, or legitimately very deep recursion such as walking a linked list of 100,000 nodes. Python raises RecursionError at its recursion limit. Fix it with a correct base case or by converting to iteration."),
            qa("intermediate", "How do you convert recursion to iteration?", "Use an explicit stack that stores the state each recursive call would have had, push initial state, and loop while the stack is non-empty. For post-order work, push a marker or a (node, visited) pair. Tail recursion converts directly to a while loop."),
            qa("intermediate", "What is the Master theorem?", "It solves recurrences T(n) = aT(n/b) + f(n) by comparing f(n) with n^(log_b a). If f is smaller, the leaves dominate (Theta(n^(log_b a))); if equal, multiply by log n; if larger and regular, f dominates. Merge sort has a=2, b=2, f=n, giving Theta(n log n)."),
            qa("advanced", "Why is naive recursive Fibonacci exponential?", "fib(n) calls fib(n-1) and fib(n-2), and each subtree recomputes the same values, giving roughly phi^n calls. Memoisation stores each fib(k) once, cutting it to O(n) time and O(n) space; a bottom-up loop gets O(1) space."),
        ],
        ["big-o", "divide-conquer", "backtracking", "dynamic-programming"],
        chain(
            ("fact(3)", "push frame", "First call", "fact(3) is not a base case, so it calls fact(2) and waits."),
            ("fact(2)", "push frame", "Recurse", "fact(2) calls fact(1); the stack now holds three frames.", "n-1"),
            ("fact(1)", "base case", "Bottom out", "n <= 1 returns 1 immediately without further calls.", "n-1"),
            ("Unwind", "pop frames", "Combine", "fact(2) returns 2*1 = 2, then fact(3) returns 3*2 = 6.", "1"),
        ),
    ),
    topic(
        "arrays-dynamic", "Arrays & Dynamic Arrays", "linear", "basic", "AR",
        "Contiguous memory with O(1) indexing; dynamic arrays grow by reallocating geometrically.",
        "An array is a row of numbered lockers: you walk straight to locker 37. A dynamic array is a row that moves to a bigger hallway, twice as long, whenever it fills up.",
        "A static array stores elements contiguously, so address(i) = base + i * size gives O(1) random access and excellent cache locality. Inserting or deleting in the middle shifts all later elements, costing O(n). A dynamic array (Python list, Java ArrayList, C++ vector) keeps spare capacity and, when full, allocates a larger block (growth factor about 1.125 in CPython, 1.5 or 2 elsewhere) and copies over, making append amortised O(1). Python lists store references to objects, not the objects themselves, so the list is contiguous but the values are not. pop() from the end is O(1) while pop(0) and insert(0, x) are O(n); use collections.deque for queue-like access. Searching an unsorted array is O(n); sorting first enables O(log n) binary search. The array module and bytearray provide compact typed storage.",
        ["Lookup tables indexed by integer keys.", "Buffers and matrices for numeric work.", "Backing storage for heaps, stacks and hash tables.", "Two-pointer and sliding-window problems."],
        [
            "Index access and update are O(1).",
            "Append is amortised O(1); insert/delete in the middle are O(n).",
            "Contiguity gives cache-friendly iteration.",
            "x in list is a linear scan; use a set for membership.",
            "Python list holds references, so [[0]*3]*3 shares the inner list.",
        ],
        [
            ex("Operation costs in practice", "basic", "Count shifts for front insert vs end append.", "python", """
                def insert_front(a, x):
                    a.append(None)
                    shifts = 0
                    for i in range(len(a) - 1, 0, -1):
                        a[i] = a[i - 1]
                        shifts += 1
                    a[0] = x
                    return shifts

                arr = [3, 4, 5, 6]
                print("shifts:", insert_front(arr, 2), arr)
                arr.append(7)
                print("append is O(1):", arr)
                print("index 3 ->", arr[3], "| 5 in arr ->", 5 in arr, "(linear scan)")
            """),
            ex("Aliasing trap", "basic", "Multiplying a nested list copies references.", "python", """
                bad = [[0] * 3] * 3
                bad[0][0] = 9
                print("shared rows:", bad)

                good = [[0] * 3 for _ in range(3)]
                good[0][0] = 9
                print("independent rows:", good)
            """),
            ex("Rotate array in place", "intermediate", "Rotate right by k using three reversals in O(n) time, O(1) space.", "python", """
                def reverse(a, i, j):
                    while i < j:
                        a[i], a[j] = a[j], a[i]
                        i += 1
                        j -= 1

                def rotate(a, k):
                    n = len(a)
                    k %= n
                    reverse(a, 0, n - 1)
                    reverse(a, 0, k - 1)
                    reverse(a, k, n - 1)
                    return a

                print(rotate([1, 2, 3, 4, 5, 6, 7], 3))
                assert rotate([1, 2, 3], 4) == [3, 1, 2]
            """),
        ],
        ["a[i] O(1) · a.append(x) amortised O(1)", "a.insert(0, x) / a.pop(0) O(n)", "x in a O(n) -> use set", "a.sort() O(n log n) in place", "[[0]*m for _ in range(n)] for 2-D"],
        ["[[0]*m]*n creates n references to one row.", "Removing items while iterating forward skips elements.", "list.remove(x) is O(n) and removes only the first match."],
        [
            qa("basic", "Why is array indexing O(1)?", "Elements are contiguous and fixed-size (or fixed-size references), so the address of element i is base + i * size, a single arithmetic computation. No traversal is needed, unlike a linked list."),
            qa("basic", "Why is inserting at the front of a Python list slow?", "All existing references must shift one slot to the right, which is O(n). For frequent front operations use collections.deque, which offers O(1) appendleft and popleft."),
            qa("intermediate", "How does a dynamic array achieve amortised O(1) append?", "When capacity runs out it allocates a block larger by a constant factor and copies elements. The total number of copies over n appends forms a geometric series bounded by a constant times n, so each append costs O(1) amortised. Growing by a fixed amount (say +10) would instead make it O(n) amortised."),
            qa("intermediate", "Why are arrays often faster than linked lists even for O(n) work?", "Contiguous memory is cache-friendly: the CPU prefetches neighbouring elements, so sequential scans hit the cache. Linked list nodes are scattered, causing cache misses on almost every step, and each node carries pointer overhead."),
        ],
        ["big-o", "two-pointers", "linked-lists", "strings"],
        chain(
            ("cap=4 full", "[1,2,3,4]", "Full array", "The dynamic array holds 4 items and has no spare slot."),
            ("append 5", "need room", "Trigger resize", "Appending requires more capacity than is available.", "5"),
            ("alloc cap=8", "new block", "Grow", "A block twice as large is allocated.", "grow"),
            ("copy 4", "O(n) once", "Copy", "The 4 existing items are copied; this cost is rare.", "copy"),
            ("write 5", "O(1)", "Append", "5 lands in slot 4; the next 3 appends need no copying.", "done"),
        ),
    ),
    topic(
        "strings", "Strings & String Manipulation", "linear", "basic", "ST",
        "Immutable character sequences; build with join, count with Counter, compare with care.",
        "A string is a necklace of beads glued in place. To change one bead you make a new necklace, so collect beads in a bag first and string them once at the end.",
        "In Python, str is an immutable sequence of Unicode code points, so every modification creates a new string. Repeated s += c in a loop can degrade to O(n^2); collecting pieces in a list and calling ''.join(parts) is O(n). Common interview tasks include reversal, palindromes, anagrams (compare Counter or sorted forms), character frequency, and parsing. Indexing and len are O(1), slicing is O(k) for k characters, and substring search with 'in' is about O(n*m) worst case. ord and chr convert between characters and code points, which is useful for 26-slot frequency arrays. Comparisons are lexicographic by code point, so uppercase letters sort before lowercase. For pattern matching at scale, use KMP or rolling hashes.",
        ["Validating palindromes and anagrams.", "Tokenising and parsing input lines.", "Building output efficiently with join.", "Frequency analysis with Counter or fixed arrays."],
        [
            "Strings are immutable; use a list and ''.join to build.",
            "Anagram check: Counter(a) == Counter(b) in O(n).",
            "ord(c) - ord('a') maps lowercase letters to 0-25.",
            "s[::-1] reverses in O(n) and creates a copy.",
            "Lexicographic comparison uses code points.",
        ],
        [
            ex("Palindrome and anagram", "basic", "Two-pointer palindrome check and Counter anagrams.", "python", """
                from collections import Counter

                def is_palindrome(s):
                    s = [c.lower() for c in s if c.isalnum()]
                    i, j = 0, len(s) - 1
                    while i < j:
                        if s[i] != s[j]:
                            return False
                        i += 1
                        j -= 1
                    return True

                print(is_palindrome("A man, a plan, a canal: Panama"))
                print(is_palindrome("hello"))
                print(Counter("listen") == Counter("silent"), sorted("listen") == sorted("silent"))
            """),
            ex("Group anagrams", "intermediate", "Use a 26-count tuple as a hash key.", "python", """
                from collections import defaultdict

                def group_anagrams(words):
                    groups = defaultdict(list)
                    for w in words:
                        counts = [0] * 26
                        for c in w:
                            counts[ord(c) - ord('a')] += 1
                        groups[tuple(counts)].append(w)
                    return list(groups.values())

                print(group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"]))
            """),
            ex("join vs +=", "basic", "Build a string efficiently.", "python", """
                parts = []
                for i in range(5):
                    parts.append(str(i * i))
                print(",".join(parts))
                words = "  the quick   brown fox ".split()
                print(" ".join(reversed(words)))
                print("compress:", "".join(f"{c}{n}" for c, n in [("a", 3), ("b", 1), ("c", 2)]))
            """),
        ],
        ["''.join(parts) O(n)", "Counter(s).most_common(k)", "ord(c) - ord('a') · chr(97 + i)", "s[::-1] · s.split() · s.strip()", "sub in s ~O(n*m) worst"],
        ["s += c in a loop may be quadratic.", "isalpha/isalnum accept Unicode letters, not only ASCII.", "sorted(s) returns a list, not a string."],
        [
            qa("basic", "Why are Python strings immutable and what does it cost?", "Immutability makes strings hashable and safe to share, but every edit creates a new object. Building a long string with += can copy repeatedly, so use ''.join on a list of pieces."),
            qa("basic", "How do you check if two strings are anagrams?", "Compare character counts: Counter(a) == Counter(b) is O(n). Sorting both and comparing is O(n log n). For lowercase ASCII, a 26-int array is fastest and uses O(1) space."),
            qa("intermediate", "How would you find the first non-repeating character?", "Count frequencies in one pass with Counter, then scan the string again and return the first character with count 1. This is O(n) time and O(k) space for alphabet size k."),
            qa("intermediate", "What is the complexity of substring search with 'in'?", "CPython uses an optimised two-way/Boyer-Moore-Horspool style search that is fast in practice, but naive worst-case analysis is O(n*m). Guaranteed linear algorithms are KMP and Z-algorithm; Rabin-Karp gives expected linear time with rolling hashes."),
        ],
        ["string-algorithms", "hash-tables", "two-pointers", "sliding-window"],
        chain(
            ("'racecar'", "input", "Start", "Place pointer i at index 0 and j at index 6."),
            ("r == r", "i=0, j=6", "Compare ends", "Characters match, move both pointers inward.", "i,j"),
            ("a == a", "i=1, j=5", "Continue", "Still matching, move inward again.", "i+1,j-1"),
            ("c == c", "i=2, j=4", "Continue", "Match again; next step i=3, j=3.", "i+1,j-1"),
            ("i >= j", "palindrome", "Done", "Pointers met without a mismatch, so the string is a palindrome.", "True"),
        ),
    ),
    topic(
        "linked-lists", "Linked Lists", "linear", "basic", "LL",
        "Nodes connected by pointers: O(1) splice at a known node, O(n) to find anything.",
        "A linked list is a treasure hunt: each clue tells you where the next clue is. You can insert a new clue anywhere instantly, but finding clue number 50 means following 49 clues.",
        "A singly linked list is a chain of nodes, each holding a value and a next pointer; a doubly linked list adds a prev pointer. Insertion and deletion at a known node are O(1) because only pointers change, but reaching the k-th node is O(k). A dummy (sentinel) head node removes edge cases when the head itself changes. Classic patterns include reversing with three pointers, fast and slow pointers for the middle and cycle detection (Floyd's algorithm), and merging two sorted lists. Linked lists have poor cache locality and per-node overhead, so arrays usually win in practice. Doubly linked lists combined with hash maps underpin LRU caches. Python has no built-in linked list type, but collections.deque is implemented as a doubly linked list of blocks.",
        ["LRU cache ordering with a doubly linked list.", "Undo histories and playlists.", "Free lists in memory allocators.", "Adjacency lists and hash-chaining buckets."],
        [
            "Access by index O(n); insert/delete at known node O(1).",
            "Use a dummy head to simplify edge cases.",
            "Reverse in O(n) time and O(1) space with prev/cur/next.",
            "Fast/slow pointers find the middle and detect cycles.",
            "Doubly linked lists allow O(1) removal given only the node.",
        ],
        [
            ex("Build, reverse and print", "basic", "Iterative reversal with three pointers.", "python", """
                class Node:
                    def __init__(self, val, nxt=None):
                        self.val, self.next = val, nxt

                def build(values):
                    dummy = tail = Node(0)
                    for v in values:
                        tail.next = Node(v)
                        tail = tail.next
                    return dummy.next

                def to_list(head):
                    out = []
                    while head:
                        out.append(head.val)
                        head = head.next
                    return out

                def reverse(head):
                    prev = None
                    while head:
                        head.next, prev, head = prev, head, head.next
                    return prev

                h = build([1, 2, 3, 4, 5])
                print(to_list(h))
                print(to_list(reverse(h)))
            """),
            ex("Floyd cycle detection and middle", "intermediate", "Slow moves one step, fast moves two.", "python", """
                class Node:
                    def __init__(self, val):
                        self.val, self.next = val, None

                nodes = [Node(i) for i in range(6)]
                for a, b in zip(nodes, nodes[1:]):
                    a.next = b

                def middle(head):
                    slow = fast = head
                    while fast and fast.next:
                        slow, fast = slow.next, fast.next.next
                    return slow.val

                def has_cycle(head):
                    slow = fast = head
                    while fast and fast.next:
                        slow, fast = slow.next, fast.next.next
                        if slow is fast:
                            return True
                    return False

                print("middle:", middle(nodes[0]), "cycle:", has_cycle(nodes[0]))
                nodes[-1].next = nodes[2]
                print("after linking tail to node 2, cycle:", has_cycle(nodes[0]))
            """),
            ex("Merge two sorted lists", "intermediate", "Dummy head keeps the code branch-free.", "python", """
                class Node:
                    def __init__(self, val, nxt=None):
                        self.val, self.next = val, nxt

                def from_list(vs):
                    head = None
                    for v in reversed(vs):
                        head = Node(v, head)
                    return head

                def merge(a, b):
                    dummy = tail = Node(0)
                    while a and b:
                        if a.val <= b.val:
                            tail.next, a = a, a.next
                        else:
                            tail.next, b = b, b.next
                        tail = tail.next
                    tail.next = a or b
                    return dummy.next

                m = merge(from_list([1, 4, 7]), from_list([2, 3, 8, 9]))
                out = []
                while m:
                    out.append(m.val)
                    m = m.next
                print(out)
            """),
        ],
        ["Reverse: prev, cur.next, cur = cur, prev, cur.next", "Middle: slow 1 step, fast 2 steps", "Cycle: Floyd O(n) time O(1) space", "dummy = Node(0); tail = dummy", "collections.deque for O(1) both ends"],
        ["Losing the rest of the list by overwriting next before saving it.", "Forgetting to update tail/prev pointers in doubly linked lists.", "Checking fast.next without first checking fast."],
        [
            qa("basic", "When would you prefer a linked list over an array?", "When you frequently insert or delete at positions you already hold references to, such as the LRU cache or splicing lists, and do not need random access. In most other cases arrays are faster due to cache locality and lower memory overhead."),
            qa("basic", "How do you reverse a singly linked list?", "Walk the list with prev = None and cur = head; at each step save cur.next, point cur.next to prev, then advance prev and cur. When cur is None, prev is the new head. O(n) time, O(1) space."),
            qa("intermediate", "How does Floyd's cycle detection work?", "A slow pointer moves one step and a fast pointer two steps. If there is a cycle, the fast pointer gains one node per step inside the loop and must meet the slow pointer; if fast reaches None, there is no cycle. Resetting one pointer to head and moving both one step finds the cycle start."),
            qa("intermediate", "How do you remove the n-th node from the end in one pass?", "Advance a lead pointer n steps, then move lead and a trailing pointer together until lead reaches the end; trailing now sits just before the target. A dummy head handles removing the first node."),
        ],
        ["lru-cache", "two-pointers", "stacks", "arrays-dynamic"],
        chain(
            ("1->2->3", "prev=None", "Start", "cur points at 1 and prev is None."),
            ("1->None", "prev=1", "Flip first", "Save next (2), point 1 back to None, advance.", "cur=1"),
            ("2->1", "prev=2", "Flip second", "Point 2 back to 1, advance to 3.", "cur=2"),
            ("3->2", "prev=3", "Flip third", "Point 3 back to 2; cur becomes None.", "cur=3"),
            ("3->2->1", "new head", "Return prev", "prev (3) is the head of the reversed list.", "head"),
        ),
    ),
    topic(
        "stacks", "Stacks", "linear", "basic", "SK",
        "Last in, first out: push and pop at one end in O(1).",
        "A stack is a pile of plates: you add to the top and take from the top. The first plate washed is the last one you use.",
        "A stack supports push, pop and peek at the top, all O(1). In Python a list works perfectly as a stack with append and pop; collections.deque also works. Stacks model anything that must be undone in reverse order: function calls, undo history, nested brackets and backtracking. Balanced parentheses checking pushes opening brackets and pops on closing ones. Postfix (reverse Polish) expressions evaluate naturally with a stack, and the shunting-yard algorithm converts infix to postfix. DFS can be implemented iteratively with an explicit stack. A monotonic stack, which keeps elements in sorted order, solves next-greater-element problems in O(n). A min-stack stores the current minimum alongside each element for O(1) getMin.",
        ["Validating brackets in code editors and parsers.", "Undo/redo stacks.", "Iterative DFS and backtracking.", "Evaluating expressions in calculators and compilers."],
        [
            "push/pop/peek are O(1): list.append, list.pop, a[-1].",
            "Check emptiness before pop to avoid IndexError.",
            "Brackets: push openers, pop and match on closers.",
            "Min-stack: store (value, current_min) pairs.",
            "The call stack is a stack; recursion can be replaced by one.",
        ],
        [
            ex("Balanced brackets", "basic", "Classic stack check.", "python", """
                def balanced(s):
                    pairs = {")": "(", "]": "[", "}": "{"}
                    stack = []
                    for c in s:
                        if c in "([{":
                            stack.append(c)
                        elif c in pairs:
                            if not stack or stack.pop() != pairs[c]:
                                return False
                    return not stack

                for s in ["([]{})", "([)]", "((", "{[()()]}"]:
                    print(f"{s:10} -> {balanced(s)}")
            """),
            ex("Evaluate postfix", "intermediate", "Reverse Polish notation evaluation.", "python", """
                def eval_rpn(tokens):
                    st = []
                    ops = {"+": lambda a, b: a + b, "-": lambda a, b: a - b,
                           "*": lambda a, b: a * b, "/": lambda a, b: int(a / b)}
                    for t in tokens:
                        if t in ops:
                            b, a = st.pop(), st.pop()
                            st.append(ops[t](a, b))
                        else:
                            st.append(int(t))
                        print(f"{t:>3} -> {st}")
                    return st[0]

                print("result:", eval_rpn("3 4 + 2 * 7 -".split()))
            """),
            ex("Min stack", "intermediate", "O(1) getMin by storing running minimums.", "python", """
                class MinStack:
                    def __init__(self):
                        self.st = []

                    def push(self, x):
                        m = min(x, self.st[-1][1]) if self.st else x
                        self.st.append((x, m))

                    def pop(self):
                        return self.st.pop()[0]

                    def get_min(self):
                        return self.st[-1][1]

                s = MinStack()
                for x in [5, 3, 7, 2, 8]:
                    s.push(x)
                    print("push", x, "min", s.get_min())
                s.pop(); s.pop()
                print("after two pops min", s.get_min())
            """),
        ],
        ["push: st.append(x) · pop: st.pop() · peek: st[-1]", "empty check: if not st", "All operations O(1)", "Monotonic stack -> next greater in O(n)", "Iterative DFS = stack"],
        ["Popping an empty list raises IndexError.", "Using list.pop(0) turns a stack into a slow queue.", "For RPN, operand order matters: second pop is the left operand."],
        [
            qa("basic", "What is a stack and where is it used?", "A LIFO structure with O(1) push and pop at the top. It is used for function calls, undo, bracket matching, expression evaluation, DFS and backtracking."),
            qa("basic", "How do you check balanced parentheses?", "Scan left to right, pushing opening brackets. On a closing bracket, the stack must be non-empty and its top must be the matching opener, which you pop. At the end the stack must be empty. O(n) time and space."),
            qa("intermediate", "How do you implement a stack with getMin in O(1)?", "Store each element together with the minimum of the stack at the time it was pushed. getMin reads the top pair's minimum; popping restores the previous minimum automatically. An alternative keeps a second stack of minimums."),
            qa("intermediate", "How do you implement a queue using two stacks?", "Push onto an input stack; when dequeuing, if the output stack is empty, pop everything from input onto output, which reverses the order. Each element is moved at most once, so operations are amortised O(1)."),
        ],
        ["queues-deques", "monotonic-stack", "dfs", "recursion"],
        chain(
            ("'([])'", "empty stack", "Start", "Scan the string from left to right."),
            ("push (", "[(]", "Opener", "Push '(' onto the stack.", "("),
            ("push [", "[(, []", "Opener", "Push '[' onto the stack.", "["),
            ("pop [", "matches ]", "Closer", "']' matches the top '[', so pop it.", "]"),
            ("pop (", "empty", "Balanced", "')' matches '('; the stack ends empty so the string is balanced.", ")"),
        ),
    ),
    topic(
        "queues-deques", "Queues & Deques", "linear", "basic", "QD",
        "First in, first out; a deque adds O(1) operations at both ends.",
        "A queue is the line at a coffee shop: first come, first served. A deque is a line where staff can also serve or seat people at the back.",
        "A queue supports enqueue at the back and dequeue at the front in O(1). In Python, use collections.deque with append and popleft; list.pop(0) is O(n) and should be avoided. A deque (double-ended queue) supports O(1) append, appendleft, pop and popleft, and deque(maxlen=k) acts as a fixed-size ring buffer. Queues drive BFS, task scheduling, and producer-consumer pipelines (queue.Queue is the thread-safe version). A circular buffer implements a bounded queue on a fixed array using head and tail indices modulo capacity. A monotonic deque keeps candidates in sorted order to compute sliding-window maximums in O(n). A priority queue is not FIFO; it serves the smallest key first and is built on a heap.",
        ["Breadth-first search level by level.", "Job and request scheduling.", "Sliding window maximum with a monotonic deque.", "Rate limiters and recent-history buffers with maxlen."],
        [
            "deque.append/popleft are O(1); list.pop(0) is O(n).",
            "deque(maxlen=k) drops the oldest item automatically.",
            "Indexing into the middle of a deque is O(n).",
            "Circular buffer: index = (head + i) % capacity.",
            "Use queue.Queue for threads, heapq for priorities.",
        ],
        [
            ex("deque basics", "basic", "FIFO, both-end operations and maxlen.", "python", """
                from collections import deque

                q = deque()
                for job in ["a", "b", "c"]:
                    q.append(job)
                print("serve", q.popleft(), "remaining", list(q))
                q.appendleft("urgent")
                print("after appendleft", list(q))

                recent = deque(maxlen=3)
                for x in range(1, 6):
                    recent.append(x)
                print("last 3:", list(recent))
            """),
            ex("Circular buffer queue", "intermediate", "Fixed-capacity queue on an array.", "python", """
                class RingQueue:
                    def __init__(self, cap):
                        self.buf, self.head, self.size = [None] * cap, 0, 0

                    def push(self, x):
                        if self.size == len(self.buf):
                            raise OverflowError("full")
                        self.buf[(self.head + self.size) % len(self.buf)] = x
                        self.size += 1

                    def pop(self):
                        x = self.buf[self.head]
                        self.head = (self.head + 1) % len(self.buf)
                        self.size -= 1
                        return x

                q = RingQueue(3)
                q.push(1); q.push(2); q.push(3)
                print(q.pop(), q.pop())
                q.push(4); q.push(5)
                print(q.buf, "head", q.head, "->", [q.pop() for _ in range(3)])
            """),
            ex("Sliding window maximum", "advanced", "Monotonic deque of indices.", "python", """
                from collections import deque

                def window_max(nums, k):
                    dq, out = deque(), []
                    for i, x in enumerate(nums):
                        while dq and nums[dq[-1]] <= x:
                            dq.pop()
                        dq.append(i)
                        if dq[0] <= i - k:
                            dq.popleft()
                        if i >= k - 1:
                            out.append(nums[dq[0]])
                    return out

                print(window_max([1, 3, -1, -3, 5, 3, 6, 7], 3))
            """),
        ],
        ["from collections import deque", "q.append(x) · q.popleft() O(1)", "q.appendleft(x) · q.pop()", "deque(maxlen=k) ring buffer", "queue.Queue() thread-safe"],
        ["list.pop(0) makes BFS O(n^2) on large graphs.", "deque random access is O(n) in the middle.", "A priority queue is not a FIFO queue."],
        [
            qa("basic", "Why should you not use a list as a queue in Python?", "list.pop(0) shifts every remaining element, costing O(n), so n dequeues become O(n^2). collections.deque gives O(1) popleft and append."),
            qa("basic", "What is a deque?", "A double-ended queue supporting O(1) insertion and removal at both ends. It can act as a stack, a queue or a bounded history buffer with maxlen."),
            qa("intermediate", "How does a circular buffer work?", "It uses a fixed array plus head and size (or head and tail) indices. Enqueue writes at (head + size) % capacity and dequeue reads at head and advances it modulo capacity. It avoids shifting and allocation, which suits embedded systems and streaming."),
            qa("advanced", "How do you compute the max of every window of size k in O(n)?", "Maintain a deque of indices whose values are decreasing. For each new element, pop from the back while the back's value is smaller or equal, push the index, and pop the front if it fell out of the window. The front is always the window maximum, and each index is pushed and popped once."),
        ],
        ["stacks", "bfs", "sliding-window", "heaps"],
        chain(
            ("enqueue a,b", "[a, b]", "Add", "Jobs join at the back of the deque."),
            ("enqueue c", "[a, b, c]", "Add more", "c joins behind b.", "c"),
            ("popleft", "serve a", "Dequeue", "The oldest item a leaves from the front in O(1).", "a"),
            ("[b, c]", "FIFO order", "Remaining", "b is next to be served, preserving arrival order.", "next"),
        ),
    ),
]

TOPICS += [
    topic(
        "hash-tables", "Hash Tables, Sets & Maps", "linear", "intermediate", "HT",
        "Hash keys into buckets for O(1) average insert, lookup and delete.",
        "A hash table is a cloakroom: the attendant turns your name into a hook number and hangs your coat there. Two names can map to the same hook, so the hook holds a short list or the coat goes to the next free hook.",
        "A hash table stores key-value pairs in an array of buckets, using a hash function to map each key to an index. A good hash spreads keys uniformly; equal keys must have equal hashes, which is why only immutable (hashable) objects can be dict keys in Python. Collisions are resolved by separate chaining (each bucket holds a list) or open addressing (probe for another slot, as CPython's dict does). The load factor, items divided by buckets, controls performance; when it crosses a threshold the table resizes and rehashes everything, which is amortised O(1). Average lookup, insert and delete are O(1), but adversarial or poor hashes can degrade them to O(n), which is why Python randomises string hashes per process. A set is a hash table of keys only, giving O(1) membership and set algebra. Python dicts preserve insertion order since 3.7. For cryptographic integrity use hashlib.sha256 or blake2b, which are designed for collision resistance rather than table indexing speed.",
        ["Counting frequencies and deduplicating.", "Two-sum style complement lookups.", "Caching and memoisation.", "Indexes from IDs to records."],
        [
            "Average O(1) get/put/delete; worst case O(n).",
            "Keys must be hashable and immutable; a == b implies hash(a) == hash(b).",
            "Load factor triggers resize and rehash (amortised O(1)).",
            "Chaining vs open addressing (linear/quadratic probing, double hashing).",
            "Use set for membership, Counter for counts, defaultdict for grouping.",
        ],
        [
            ex("Separate chaining from scratch", "intermediate", "Buckets of lists with resize at load factor 0.75.", "python", """
                class ChainMap:
                    def __init__(self, cap=4):
                        self.buckets = [[] for _ in range(cap)]
                        self.size = 0

                    def _idx(self, key):
                        return hash(key) % len(self.buckets)

                    def put(self, key, val):
                        b = self.buckets[self._idx(key)]
                        for pair in b:
                            if pair[0] == key:
                                pair[1] = val
                                return
                        b.append([key, val])
                        self.size += 1
                        if self.size / len(self.buckets) > 0.75:
                            self._resize()

                    def get(self, key):
                        for k, v in self.buckets[self._idx(key)]:
                            if k == key:
                                return v
                        raise KeyError(key)

                    def _resize(self):
                        old = [p for b in self.buckets for p in b]
                        self.buckets = [[] for _ in range(2 * len(self.buckets))]
                        self.size = 0
                        for k, v in old:
                            self.put(k, v)

                m = ChainMap()
                for i, w in enumerate(["apple", "banana", "cherry", "date", "elder"]):
                    m.put(w, i)
                print("buckets:", len(m.buckets), "load:", round(m.size / len(m.buckets), 2))
                print("cherry ->", m.get("cherry"))
            """),
            ex("Two sum with a dict", "basic", "Complement lookup in one pass.", "python", """
                def two_sum(nums, target):
                    seen = {}
                    for i, x in enumerate(nums):
                        if target - x in seen:
                            return seen[target - x], i
                        seen[x] = i
                    return None

                print(two_sum([2, 7, 11, 15], 9))
                print(two_sum([3, 2, 4], 6))
            """),
            ex("Sets, Counter and secure digests", "basic", "Set algebra, counting and SHA-256 fingerprints.", "python", """
                import hashlib
                from collections import Counter, defaultdict

                a, b = {1, 2, 3, 4}, {3, 4, 5}
                print("union", a | b, "inter", a & b, "diff", a - b)
                print(Counter("mississippi").most_common(2))
                groups = defaultdict(list)
                for w in ["ant", "bee", "ape", "bat"]:
                    groups[w[0]].append(w)
                print(dict(groups))
                print("sha256:", hashlib.sha256(b"hello").hexdigest()[:16])
                print("blake2b:", hashlib.blake2b(b"hello", digest_size=8).hexdigest())
            """),
        ],
        ["d.get(k, default) · k in d O(1) avg", "Counter(xs) · defaultdict(list)", "set ops: | & - ^", "load factor = n / buckets", "hashlib.sha256(data).hexdigest()"],
        ["Lists and dicts are unhashable; convert to tuple or frozenset for keys.", "Mutating an object after using it as a key breaks lookups.", "Worst case O(n) with many collisions; do not promise O(1) unconditionally.", "Iterating a set has no guaranteed order."],
        [
            qa("basic", "How does a hash table achieve O(1) lookup?", "The hash function maps a key to a bucket index directly, so lookup is a hash computation plus a check of a small bucket. With a good hash and a bounded load factor, buckets stay O(1) in expectation."),
            qa("intermediate", "What are the main collision resolution strategies?", "Separate chaining stores colliding entries in a per-bucket list or tree. Open addressing stores everything in the array and probes for another slot via linear probing, quadratic probing or double hashing. Open addressing is cache-friendly but needs tombstones for deletion and a lower load factor."),
            qa("intermediate", "What is the load factor and why does it matter?", "It is the number of entries divided by the number of buckets. As it grows, collisions and probe lengths increase, so tables resize (often doubling) when it crosses a threshold like 0.75 for chaining or about 2/3 for CPython dicts. Resizing rehashes everything in O(n) but happens rarely, keeping insert amortised O(1)."),
            qa("intermediate", "Why must dictionary keys be immutable?", "The bucket is chosen from the hash at insertion time. If the key changed afterwards, its hash would change and the entry would sit in the wrong bucket, making it unfindable. Python enforces this by making lists and dicts unhashable."),
            qa("advanced", "What is a hash flooding attack?", "An attacker sends many keys that collide, degrading every operation to O(n) and the whole request to O(n^2), causing denial of service. Python mitigates this with randomised SipHash for str and bytes, and Java converts long chains to balanced trees."),
        ],
        ["arrays-dynamic", "lru-cache", "two-pointers", "string-algorithms"],
        chain(
            ("key 'cat'", "put('cat', 1)", "Insert", "We want to store 'cat' -> 1."),
            ("hash()", "big integer", "Hash", "The hash function turns the key into an integer.", "'cat'"),
            ("mod 8", "bucket 5", "Index", "hash % capacity selects bucket 5.", "h"),
            ("collision?", "chain / probe", "Resolve", "If bucket 5 is occupied by another key, append to its chain or probe the next slot.", "idx"),
            ("load > 0.75", "resize x2", "Grow", "When the load factor is exceeded, double the buckets and rehash all keys.", "n/m"),
        ),
    ),
    topic(
        "lru-cache", "LRU Cache Design", "linear", "intermediate", "LR",
        "Hash map plus doubly linked list gives O(1) get and put with least-recently-used eviction.",
        "An LRU cache is a desk with limited space: whatever you touch moves to the top of the pile, and when the desk is full you throw away whatever is at the bottom, the thing you have not touched longest.",
        "An LRU (least recently used) cache holds at most capacity entries and, when full, evicts the entry that was accessed longest ago. The classic O(1) design combines a hash map from key to node with a doubly linked list ordered by recency. get looks up the node, moves it to the front and returns its value; put updates or inserts at the front and, if over capacity, removes the tail node and deletes its key from the map. Sentinel head and tail nodes remove null checks. In Python, collections.OrderedDict provides move_to_end and popitem(last=False), so a compact implementation needs no manual list. functools.lru_cache applies the same policy to function results. Variants include LFU (least frequently used), TTL expiry, and thread-safe caches with locks.",
        ["Memoising expensive function calls.", "Database page and buffer pools.", "CDN and web response caches.", "Interview design question testing data-structure composition."],
        [
            "Hash map gives O(1) lookup of the node.",
            "Doubly linked list gives O(1) move-to-front and remove-tail.",
            "Sentinel head/tail nodes simplify edge cases.",
            "OrderedDict.move_to_end + popitem(last=False) is the Pythonic version.",
            "Both get and put count as 'use' and refresh recency.",
        ],
        [
            ex("LRU with OrderedDict", "basic", "Compact and idiomatic.", "python", """
                from collections import OrderedDict

                class LRU:
                    def __init__(self, cap):
                        self.cap, self.d = cap, OrderedDict()

                    def get(self, k):
                        if k not in self.d:
                            return -1
                        self.d.move_to_end(k)
                        return self.d[k]

                    def put(self, k, v):
                        self.d[k] = v
                        self.d.move_to_end(k)
                        if len(self.d) > self.cap:
                            evicted = self.d.popitem(last=False)
                            print("evict", evicted)

                c = LRU(2)
                c.put(1, "a"); c.put(2, "b")
                print(c.get(1))
                c.put(3, "c")
                print(c.get(2), list(c.d.items()))
            """),
            ex("LRU with hash map + doubly linked list", "intermediate", "What interviewers expect you to build.", "python", """
                class Node:
                    def __init__(self, k=0, v=0):
                        self.k, self.v, self.prev, self.next = k, v, None, None

                class LRU:
                    def __init__(self, cap):
                        self.cap, self.map = cap, {}
                        self.head, self.tail = Node(), Node()
                        self.head.next, self.tail.prev = self.tail, self.head

                    def _remove(self, n):
                        n.prev.next, n.next.prev = n.next, n.prev

                    def _add_front(self, n):
                        n.prev, n.next = self.head, self.head.next
                        self.head.next.prev = n
                        self.head.next = n

                    def get(self, k):
                        if k not in self.map:
                            return -1
                        n = self.map[k]
                        self._remove(n); self._add_front(n)
                        return n.v

                    def put(self, k, v):
                        if k in self.map:
                            self._remove(self.map[k])
                        n = self.map[k] = Node(k, v)
                        self._add_front(n)
                        if len(self.map) > self.cap:
                            lru = self.tail.prev
                            self._remove(lru)
                            del self.map[lru.k]

                    def order(self):
                        out, n = [], self.head.next
                        while n is not self.tail:
                            out.append(n.k); n = n.next
                        return out

                c = LRU(3)
                for k in [1, 2, 3]:
                    c.put(k, k * 10)
                c.get(1)
                c.put(4, 40)
                print("order MRU->LRU:", c.order(), "get(2):", c.get(2))
            """),
            ex("functools.lru_cache", "basic", "The built-in decorator applies LRU to function calls.", "python", """
                from functools import lru_cache

                @lru_cache(maxsize=2)
                def square(x):
                    print("  computing", x)
                    return x * x

                for x in [2, 3, 2, 4, 3]:
                    print(x, "->", square(x))
                print(square.cache_info())
            """),
        ],
        ["OrderedDict: move_to_end(k), popitem(last=False)", "@functools.lru_cache(maxsize=128)", "get/put O(1)", "map: key -> node; list: MRU ... LRU", "f.cache_info() · f.cache_clear()"],
        ["Forgetting to delete the evicted key from the hash map.", "Not refreshing recency on put of an existing key.", "lru_cache arguments must be hashable."],
        [
            qa("intermediate", "How do you design an LRU cache with O(1) operations?", "Use a hash map from key to node in a doubly linked list kept in recency order. get moves the node to the front; put inserts at the front and, if over capacity, removes the tail node and its map entry. Both operations are O(1) because the map finds nodes and the list splices in constant time."),
            qa("intermediate", "Why a doubly linked list rather than a singly linked one?", "Removing an arbitrary node in O(1) requires access to its predecessor. A doubly linked node stores prev, so it can unlink itself; a singly linked list would need an O(n) search for the predecessor."),
            qa("intermediate", "How does OrderedDict make LRU easy in Python?", "OrderedDict maintains insertion order with an internal doubly linked list and offers move_to_end(key) and popitem(last=False) in O(1). Move a key to the end on access and pop from the front on eviction."),
            qa("advanced", "How would you make an LRU cache thread-safe or distributed?", "For threads, guard get and put with a lock, or shard the cache by key hash with one lock per shard to reduce contention. For distributed systems, use a store like Redis with an allkeys-lru eviction policy, which approximates LRU by sampling keys."),
        ],
        ["hash-tables", "linked-lists", "queues-deques"],
        chain(
            ("put 1,2,3", "MRU: 3,2,1", "Fill", "Capacity 3 is reached; 1 is least recently used."),
            ("get(1)", "MRU: 1,3,2", "Touch", "Accessing 1 moves it to the front; 2 is now LRU.", "1"),
            ("put 4", "over capacity", "Insert", "4 goes to the front and size becomes 4.", "4"),
            ("evict tail", "remove 2", "Evict", "The tail node 2 is unlinked and deleted from the map.", "LRU"),
            ("MRU: 4,1,3", "size 3", "Result", "Cache holds 4, 1, 3 and get(2) now returns -1.", "done"),
        ),
    ),
    topic(
        "bubble-sort", "Bubble Sort", "sorting", "basic", "BS",
        "Repeatedly swap adjacent out-of-order pairs; the largest value bubbles to the end each pass.",
        "Bubble sort is like bubbles rising in a glass: on each pass the biggest bubble floats up to the top, and the next pass only needs to handle what is below it.",
        "Bubble sort makes repeated passes over the array, comparing each adjacent pair and swapping them if they are out of order. After pass k, the k largest elements are in their final positions at the end, so each pass can stop one element earlier. With an early-exit flag (stop when a pass makes no swaps), the best case on already sorted input is O(n). Average and worst cases are O(n^2) comparisons and swaps, worst case being reverse-sorted input. It uses O(1) extra space, so it is in-place, and it is stable because it only swaps strictly greater neighbours. The number of swaps equals the number of inversions in the input. It is mainly a teaching tool; insertion sort dominates it in practice.",
        ["Teaching sorting and loop invariants.", "Detecting whether an array is already sorted in one pass.", "Tiny arrays on hardware where code size matters.", "Counting inversions conceptually (swaps = inversions)."],
        [
            "Best O(n) with early exit, average O(n^2), worst O(n^2).",
            "Space O(1): in-place.",
            "Stable: equal elements are never swapped.",
            "After pass i, the last i elements are final.",
            "Swaps performed equal the number of inversions.",
        ],
        [
            ex("Bubble sort with trace", "basic", "Show each pass and stop early when no swaps occur.", "python", """
                def bubble_sort(a):
                    a = list(a)
                    n = len(a)
                    for p in range(n - 1):
                        swapped = False
                        for i in range(n - 1 - p):
                            if a[i] > a[i + 1]:
                                a[i], a[i + 1] = a[i + 1], a[i]
                                swapped = True
                        print(f"pass {p + 1}: {a}")
                        if not swapped:
                            break
                    return a

                print(bubble_sort([5, 1, 4, 2, 8]))
                assert bubble_sort([3, 2, 1]) == [1, 2, 3]
            """),
            ex("Best case vs worst case", "intermediate", "Count comparisons for sorted and reversed input.", "python", """
                def bubble_count(a):
                    a, comps, swaps = list(a), 0, 0
                    n = len(a)
                    for p in range(n - 1):
                        swapped = False
                        for i in range(n - 1 - p):
                            comps += 1
                            if a[i] > a[i + 1]:
                                a[i], a[i + 1] = a[i + 1], a[i]
                                swaps += 1
                                swapped = True
                        if not swapped:
                            break
                    return comps, swaps

                n = 10
                print("sorted:  ", bubble_count(range(n)))
                print("reversed:", bubble_count(range(n, 0, -1)), "n(n-1)/2 =", n * (n - 1) // 2)
            """),
            ex("Stability check", "basic", "Equal keys keep their original order.", "python", """
                def bubble_by_key(a, key):
                    a = list(a)
                    for p in range(len(a) - 1):
                        for i in range(len(a) - 1 - p):
                            if key(a[i]) > key(a[i + 1]):
                                a[i], a[i + 1] = a[i + 1], a[i]
                    return a

                cards = [(3, "red"), (1, "blue"), (3, "green"), (1, "gold")]
                print(bubble_by_key(cards, key=lambda c: c[0]))
            """),
        ],
        ["Best O(n) · Avg O(n^2) · Worst O(n^2)", "Space O(1) · in-place · stable", "Early exit: break if no swaps", "Inner loop: range(n - 1 - pass)", "Swaps == inversions"],
        ["Without the swapped flag, the best case is O(n^2) too.", "Using >= instead of > breaks stability.", "Off-by-one in the inner range can index past the end."],
        [
            qa("basic", "What are the time and space complexities of bubble sort?", "Best case O(n) with an early-exit flag on sorted input, average and worst O(n^2). Space is O(1) because it swaps in place. It is stable."),
            qa("basic", "Why is bubble sort stable?", "It only swaps adjacent elements when the left is strictly greater than the right, so two equal elements never pass each other. Changing the comparison to >= would make it unstable."),
            qa("intermediate", "How is bubble sort related to inversions?", "An inversion is a pair i < j with a[i] > a[j]. Each adjacent swap removes exactly one inversion, so bubble sort performs exactly as many swaps as there are inversions, up to n(n-1)/2 for reversed input."),
            qa("intermediate", "Why is insertion sort preferred over bubble sort?", "Both are O(n^2) and stable, but insertion sort does fewer writes (shifting instead of three-assignment swaps), is adaptive in a finer way, and has better constants. It is the base case in Timsort and introsort; bubble sort is used almost nowhere in production."),
        ],
        ["insertion-sort", "selection-sort", "timsort-stability"],
        chain(
            ("[5,1,4,2,8]", "pass 1", "Start", "Compare adjacent pairs from left to right."),
            ("swap 5,1", "[1,5,4,2,8]", "Compare 0-1", "5 > 1, so swap them.", "5>1"),
            ("5 bubbles", "[1,4,2,5,8]", "Finish pass 1", "5 swaps past 4 and 2; 8 is already largest and stays last.", "5"),
            ("pass 2", "[1,2,4,5,8]", "Next pass", "4 swaps with 2; the tail 5, 8 is final.", "4"),
            ("pass 3", "no swaps", "Early exit", "No swaps occur, so the array is sorted: [1,2,4,5,8].", "done"),
        ),
    ),
    topic(
        "selection-sort", "Selection Sort", "sorting", "basic", "SS",
        "Repeatedly select the minimum of the unsorted part and swap it into place.",
        "Selection sort is picking a sports team: scan everyone left, pick the best, put them in the next slot, and repeat until nobody is left.",
        "Selection sort divides the array into a sorted prefix and an unsorted suffix. On each pass it scans the unsorted suffix for the minimum element and swaps it with the first unsorted position. It always performs n(n-1)/2 comparisons regardless of input, so best, average and worst cases are all O(n^2). It makes at most n-1 swaps, which is the minimum possible for a swap-based sort and useful when writes are expensive (for example flash memory). It is in-place with O(1) extra space. The standard array version is not stable, because the long-distance swap can jump an element past an equal one; a stable variant shifts elements instead of swapping, at the cost of more writes. Heap sort is essentially selection sort with a heap to find the minimum in O(log n).",
        ["Sorting when writes are far costlier than reads.", "Teaching invariants (sorted prefix grows by one).", "Very small arrays where simplicity matters.", "Understanding why heap sort works."],
        [
            "Best = average = worst = O(n^2) comparisons.",
            "At most n-1 swaps: O(n) writes.",
            "Space O(1): in-place.",
            "Not stable in the swapping form.",
            "Not adaptive: sorted input costs the same.",
        ],
        [
            ex("Selection sort with trace", "basic", "Show which minimum is chosen each pass.", "python", """
                def selection_sort(a):
                    a = list(a)
                    n = len(a)
                    for i in range(n - 1):
                        m = i
                        for j in range(i + 1, n):
                            if a[j] < a[m]:
                                m = j
                        a[i], a[m] = a[m], a[i]
                        print(f"pass {i + 1}: min={a[i]} -> {a}")
                    return a

                print(selection_sort([64, 25, 12, 22, 11]))
            """),
            ex("Why it is unstable", "intermediate", "A long swap moves an equal key past its twin.", "python", """
                def selection_by_key(a, key):
                    a = list(a)
                    for i in range(len(a) - 1):
                        m = min(range(i, len(a)), key=lambda j: key(a[j]))
                        a[i], a[m] = a[m], a[i]
                    return a

                data = [(4, "A"), (4, "B"), (1, "C")]
                out = selection_by_key(data, key=lambda x: x[0])
                print(out)
                print("stable?", [x[1] for x in out if x[0] == 4] == ["A", "B"])
            """),
            ex("Comparisons and swaps", "basic", "Same comparisons for any input, few swaps.", "python", """
                def counts(a):
                    a, comps, swaps = list(a), 0, 0
                    for i in range(len(a) - 1):
                        m = i
                        for j in range(i + 1, len(a)):
                            comps += 1
                            if a[j] < a[m]:
                                m = j
                        if m != i:
                            a[i], a[m] = a[m], a[i]
                            swaps += 1
                    return comps, swaps

                print("sorted  ", counts(range(8)))
                print("reversed", counts(range(8, 0, -1)))
                print("random  ", counts([5, 2, 7, 1, 8, 3, 6, 4]))
            """),
        ],
        ["Best/Avg/Worst O(n^2)", "Space O(1) · in-place · not stable", "Swaps <= n - 1", "Invariant: a[:i] sorted and final", "Heap sort = selection sort + heap"],
        ["It does not benefit from sorted input at all.", "Its instability surprises people sorting records by a secondary key.", "Fewer swaps does not mean fast: comparisons are still quadratic."],
        [
            qa("basic", "What is the complexity of selection sort?", "O(n^2) in the best, average and worst case because it always scans the entire unsorted part. It uses O(1) extra space and performs at most n-1 swaps."),
            qa("basic", "Is selection sort stable?", "Not in its usual form. Swapping the minimum into position i can move the element previously at i past an equal element later in the array. A stable variant inserts the minimum by shifting, which costs O(n^2) writes."),
            qa("intermediate", "When might selection sort be a reasonable choice?", "When writes are very expensive compared to reads, since it does O(n) swaps, or for tiny arrays where simple code matters. Otherwise insertion sort is better for small inputs."),
            qa("intermediate", "How does selection sort relate to heap sort?", "Both repeatedly extract the extreme element and place it at the boundary of the sorted region. Heap sort keeps the unsorted part in a heap so finding the max takes O(log n) instead of O(n), turning O(n^2) into O(n log n)."),
        ],
        ["bubble-sort", "heap-sort", "insertion-sort"],
        chain(
            ("64,25,12,22,11", "i=0", "Start", "The sorted prefix is empty."),
            ("min=11", "swap with 64", "Pass 1", "Scan finds 11 at index 4; swap with index 0 -> [11,25,12,22,64].", "11"),
            ("min=12", "swap with 25", "Pass 2", "Scan indices 1-4, find 12 -> [11,12,25,22,64].", "12"),
            ("min=22", "swap with 25", "Pass 3", "Scan indices 2-4, find 22 -> [11,12,22,25,64].", "22"),
            ("sorted", "4 passes", "Done", "Pass 4 keeps 25 in place; the array is sorted.", "done"),
        ),
    ),
    topic(
        "insertion-sort", "Insertion Sort", "sorting", "basic", "IS",
        "Grow a sorted prefix by inserting each new element into its place; fast on nearly sorted data.",
        "Insertion sort is how most people sort a hand of cards: pick up the next card and slide it left until it sits next to a smaller one.",
        "Insertion sort keeps a sorted prefix a[:i] and, for each new element a[i], shifts larger elements one slot right until it finds the insertion point. Best case is O(n) on already sorted input, because each element needs one comparison. Average and worst cases are O(n^2), with reverse-sorted input as the worst. More precisely it runs in O(n + inversions), so it is excellent for nearly sorted data. It is in-place with O(1) extra space, stable (it stops at elements that are less than or equal), and online (it can sort a stream as items arrive). Binary insertion sort finds the position with binary search, reducing comparisons to O(n log n) but not the O(n^2) shifts. Its low overhead makes it the small-array base case in Timsort, introsort and many merge sort implementations.",
        ["Small arrays (below about 16-64 elements) inside hybrid sorts.", "Nearly sorted data, such as appending a few new items.", "Online sorting of a stream.", "Maintaining a sorted list with bisect.insort."],
        [
            "Best O(n), average O(n^2), worst O(n^2); O(n + inversions).",
            "Space O(1): in-place.",
            "Stable and online.",
            "Shifts instead of swaps: one write per moved element.",
            "bisect.insort keeps a list sorted (O(log n) search, O(n) shift).",
        ],
        [
            ex("Insertion sort with trace", "basic", "Show the sorted prefix grow.", "python", """
                def insertion_sort(a):
                    a = list(a)
                    for i in range(1, len(a)):
                        key, j = a[i], i - 1
                        while j >= 0 and a[j] > key:
                            a[j + 1] = a[j]
                            j -= 1
                        a[j + 1] = key
                        print(f"insert {key}: {a[:i + 1]} | {a[i + 1:]}")
                    return a

                print(insertion_sort([5, 2, 4, 6, 1, 3]))
            """),
            ex("Adaptive on nearly sorted input", "intermediate", "Shifts equal the number of inversions.", "python", """
                def shifts(a):
                    a, s = list(a), 0
                    for i in range(1, len(a)):
                        key, j = a[i], i - 1
                        while j >= 0 and a[j] > key:
                            a[j + 1] = a[j]
                            j -= 1
                            s += 1
                        a[j + 1] = key
                    return s

                def inversions(a):
                    return sum(1 for i in range(len(a)) for j in range(i + 1, len(a)) if a[i] > a[j])

                for name, arr in [("sorted", list(range(10))), ("nearly", [0, 1, 3, 2, 4, 5, 7, 6, 8, 9]), ("reversed", list(range(9, -1, -1)))]:
                    print(f"{name:9} shifts={shifts(arr):3} inversions={inversions(arr)}")
            """),
            ex("bisect.insort", "basic", "Keep a list sorted as items arrive.", "python", """
                import bisect

                stream = [7, 3, 9, 1, 5]
                ordered = []
                for x in stream:
                    bisect.insort(ordered, x)
                    print("after", x, "->", ordered)
            """),
        ],
        ["Best O(n) · Avg O(n^2) · Worst O(n^2)", "Space O(1) · in-place · stable · online", "while j >= 0 and a[j] > key: shift", "bisect.insort(lst, x)", "Used for runs < 64 in Timsort"],
        ["Using >= in the while condition makes it unstable.", "Binary insertion reduces comparisons, not shifts.", "Forgetting j >= 0 leads to wrapping to a[-1] in Python."],
        [
            qa("basic", "What are insertion sort's complexities?", "Best case O(n) on sorted input, average and worst O(n^2). It uses O(1) extra space, is stable, adaptive and online."),
            qa("intermediate", "Why do hybrid sorts use insertion sort for small subarrays?", "For small n the O(n^2) term is tiny and insertion sort has very low overhead: no recursion, no extra memory and tight cache-friendly loops. Its constant factors beat merge or quick sort below roughly 16-64 elements."),
            qa("intermediate", "What does it mean that insertion sort is O(n + I)?", "Each shift fixes exactly one inversion, and every element needs at least one comparison, so running time is proportional to n plus the number of inversions I. Nearly sorted input with few inversions sorts in near-linear time."),
            qa("intermediate", "Does binary insertion sort make it O(n log n)?", "No. Binary search finds the position in O(log n) comparisons, but inserting still shifts up to i elements, so total time remains O(n^2). It helps only when comparisons are much more expensive than moves."),
        ],
        ["bubble-sort", "timsort-stability", "binary-search", "merge-sort"],
        chain(
            ("[5,2,4,6,1]", "prefix [5]", "Start", "The first element alone is a sorted prefix."),
            ("insert 2", "[2,5]", "Shift 5", "5 > 2 shifts right; 2 goes to index 0.", "2"),
            ("insert 4", "[2,4,5]", "Shift 5", "5 shifts right, 2 < 4 stops; insert 4.", "4"),
            ("insert 6", "[2,4,5,6]", "No shift", "6 >= 5 so it stays; one comparison only.", "6"),
            ("insert 1", "[1,2,4,5,6]", "Shift all", "All four elements shift right; 1 goes to the front.", "1"),
        ),
    ),
    topic(
        "merge-sort", "Merge Sort", "sorting", "intermediate", "MS",
        "Split in half, sort each half recursively, then merge two sorted halves in linear time.",
        "Merge sort is two people each sorting half a deck of exam papers, then combining the piles by repeatedly taking the smaller top paper.",
        "Merge sort is a divide and conquer algorithm: split the array into halves, recursively sort each, and merge the two sorted halves by repeatedly taking the smaller front element. The recursion has log n levels and each level does O(n) merge work, giving O(n log n) in the best, average and worst case (recurrence T(n) = 2T(n/2) + O(n)). The array version needs O(n) auxiliary space for merging plus O(log n) stack, so it is not in-place. It is stable as long as the merge takes from the left half on ties (<=). Merge sort sorts linked lists with O(1) extra space for merging and is the basis of external sorting, where chunks are sorted in memory and then k-way merged from disk. Bottom-up merge sort avoids recursion by merging runs of size 1, 2, 4 and so on. Counting inversions is a classic extension of the merge step.",
        ["Stable sorting of records by key.", "External sorting of data larger than memory.", "Sorting linked lists.", "Counting inversions and similar divide-and-conquer problems."],
        [
            "Best = average = worst = O(n log n).",
            "Space O(n) auxiliary for arrays: not in-place.",
            "Stable when ties take from the left half.",
            "Merge step is O(n + m) with two pointers.",
            "Parallelises well and suits external k-way merging (heapq.merge).",
        ],
        [
            ex("Top-down merge sort with trace", "basic", "Print merges as the recursion unwinds.", "python", """
                def merge(left, right):
                    out, i, j = [], 0, 0
                    while i < len(left) and j < len(right):
                        if left[i] <= right[j]:
                            out.append(left[i]); i += 1
                        else:
                            out.append(right[j]); j += 1
                    out.extend(left[i:]); out.extend(right[j:])
                    return out

                def merge_sort(a, depth=0):
                    if len(a) <= 1:
                        return a
                    mid = len(a) // 2
                    l, r = merge_sort(a[:mid], depth + 1), merge_sort(a[mid:], depth + 1)
                    m = merge(l, r)
                    print("  " * depth + f"merge {l} + {r} -> {m}")
                    return m

                print(merge_sort([38, 27, 43, 3, 9, 82, 10]))
            """),
            ex("Count inversions", "intermediate", "Count pairs during merge in O(n log n).", "python", """
                def sort_count(a):
                    if len(a) <= 1:
                        return a, 0
                    mid = len(a) // 2
                    l, x = sort_count(a[:mid])
                    r, y = sort_count(a[mid:])
                    out, i, j, inv = [], 0, 0, x + y
                    while i < len(l) and j < len(r):
                        if l[i] <= r[j]:
                            out.append(l[i]); i += 1
                        else:
                            out.append(r[j]); j += 1
                            inv += len(l) - i
                    out += l[i:] + r[j:]
                    return out, inv

                print(sort_count([2, 4, 1, 3, 5]))
                print(sort_count([5, 4, 3, 2, 1]))
            """),
            ex("Bottom-up and heapq.merge", "intermediate", "Iterative merging of runs and lazy k-way merge.", "python", """
                import heapq

                def bottom_up(a):
                    a, width = list(a), 1
                    while width < len(a):
                        for lo in range(0, len(a), 2 * width):
                            mid, hi = lo + width, min(lo + 2 * width, len(a))
                            a[lo:hi] = list(heapq.merge(a[lo:mid], a[mid:hi]))
                        print(f"width {width}: {a}")
                        width *= 2
                    return a

                bottom_up([5, 1, 6, 2, 8, 3, 7, 4])
                print(list(heapq.merge([1, 4, 9], [2, 3, 10], [0, 5])))
            """),
        ],
        ["Best/Avg/Worst O(n log n)", "Space O(n) aux · not in-place · stable", "T(n) = 2T(n/2) + O(n)", "heapq.merge(*sorted_iterables)", "Use <= in merge to stay stable"],
        ["Using < instead of <= in the merge breaks stability.", "Slicing in Python adds copies; pass indices for a tighter version.", "Recursion depth is only log n, but memory is O(n)."],
        [
            qa("basic", "What are merge sort's complexities?", "O(n log n) time in the best, average and worst case, O(n) auxiliary space for arrays, and O(log n) recursion stack. It is stable and not in-place."),
            qa("intermediate", "Why is merge sort O(n log n) in every case?", "It always splits exactly in half regardless of the data, producing log2 n levels, and each level merges a total of n elements in O(n). The input order affects only how many comparisons a merge makes, not the recursion structure."),
            qa("intermediate", "Why is merge sort preferred for linked lists?", "Linked lists lack random access, which hurts quicksort and heap sort, but merging only needs sequential traversal and can relink nodes with O(1) extra space. Finding the middle uses fast and slow pointers."),
            qa("intermediate", "How does external merge sort work?", "Read memory-sized chunks, sort each in RAM and write sorted runs to disk. Then perform a k-way merge using a min-heap holding the current head of each run, streaming output sequentially. This minimises random disk I/O."),
            qa("advanced", "Merge sort vs quicksort: when do you pick which?", "Quicksort is usually faster in memory due to in-place partitioning and cache locality, but has an O(n^2) worst case and is unstable. Merge sort guarantees O(n log n), is stable, and suits linked lists and external data, at the cost of O(n) extra memory."),
        ],
        ["quick-sort", "divide-conquer", "timsort-stability", "recursion"],
        chain(
            ("[38,27,43,3]", "n=4", "Split", "Divide into [38,27] and [43,3]."),
            ("split again", "[38][27][43][3]", "Base cases", "Single elements are already sorted.", "halves"),
            ("merge pairs", "[27,38] [3,43]", "Merge level 1", "Merge each pair by taking the smaller front element.", "runs"),
            ("merge all", "compare fronts", "Merge level 2", "3 < 27, take 3; 27 < 43, take 27; 38 < 43, take 38; then 43.", "fronts"),
            ("[3,27,38,43]", "sorted", "Done", "Two levels of O(n) merging: log n levels total.", "done"),
        ),
    ),
    topic(
        "quick-sort", "Quick Sort: Partition Schemes & Pivot Choice", "sorting", "intermediate", "QS",
        "Partition around a pivot so smaller items go left and larger go right, then recurse on both sides.",
        "Quicksort is a teacher who picks one student's height as a reference, sends shorter students to the left wall and taller ones to the right, then repeats in each group.",
        "Quicksort picks a pivot, partitions the array so elements less than the pivot come before it and greater ones after, then recursively sorts both sides. Lomuto partition scans with one pointer and swaps smaller items forward, placing the pivot at its final index; it is simple but does more swaps and degrades on many duplicates. Hoare partition moves two pointers inward from both ends and swaps out-of-place pairs; it does about three times fewer swaps but the pivot is not necessarily at its final position. Average and best time are O(n log n); worst is O(n^2) when pivots are consistently the smallest or largest, such as a first-element pivot on sorted input. Random pivots or median-of-three make the worst case extremely unlikely, and three-way (Dutch national flag) partitioning handles many equal keys in O(n). It is in-place with O(log n) average stack, but not stable. Introsort, used by C++ std::sort, switches to heap sort when recursion gets too deep, guaranteeing O(n log n).",
        ["General-purpose in-memory sorting of primitives (C qsort, C++ std::sort via introsort).", "Quickselect for k-th smallest.", "Cache-friendly sorting of large arrays.", "Three-way partitioning for data with many duplicates."],
        [
            "Best/average O(n log n), worst O(n^2).",
            "Space O(log n) stack average, O(n) worst; in-place partitioning.",
            "Not stable.",
            "Lomuto: simple, pivot ends at final index; Hoare: fewer swaps.",
            "Random or median-of-three pivots avoid sorted-input worst cases.",
        ],
        [
            ex("Lomuto partition with trace", "basic", "Last element as pivot, print each partition.", "python", """
                def lomuto(a, lo, hi):
                    pivot, i = a[hi], lo
                    for j in range(lo, hi):
                        if a[j] < pivot:
                            a[i], a[j] = a[j], a[i]
                            i += 1
                    a[i], a[hi] = a[hi], a[i]
                    return i

                def quicksort(a, lo=0, hi=None):
                    if hi is None:
                        hi = len(a) - 1
                    if lo < hi:
                        p = lomuto(a, lo, hi)
                        print(f"pivot {a[p]} at {p}: {a[lo:p]} [{a[p]}] {a[p + 1:hi + 1]}")
                        quicksort(a, lo, p - 1)
                        quicksort(a, p + 1, hi)
                    return a

                print(quicksort([10, 80, 30, 90, 40, 50, 70]))
            """),
            ex("Hoare partition with random pivot", "intermediate", "Two pointers moving inward.", "python", """
                import random

                def hoare(a, lo, hi):
                    r = random.randint(lo, hi)
                    a[lo], a[r] = a[r], a[lo]
                    pivot, i, j = a[lo], lo - 1, hi + 1
                    while True:
                        i += 1
                        while a[i] < pivot:
                            i += 1
                        j -= 1
                        while a[j] > pivot:
                            j -= 1
                        if i >= j:
                            return j
                        a[i], a[j] = a[j], a[i]

                def qs(a, lo, hi):
                    if lo < hi:
                        p = hoare(a, lo, hi)
                        qs(a, lo, p)
                        qs(a, p + 1, hi)

                random.seed(1)
                data = [random.randint(0, 99) for _ in range(15)]
                qs(data, 0, len(data) - 1)
                print(data)
                assert data == sorted(data)
            """),
            ex("Worst case and three-way partition", "advanced", "First-element pivot on sorted input vs 3-way on duplicates.", "python", """
                def naive_depth(a):
                    if len(a) <= 1:
                        return 0
                    p = a[0]
                    left = [x for x in a[1:] if x < p]
                    right = [x for x in a[1:] if x >= p]
                    return 1 + max(naive_depth(left), naive_depth(right))

                def three_way(a, lo, hi):
                    if lo >= hi:
                        return
                    p, lt, i, gt = a[lo], lo, lo, hi
                    while i <= gt:
                        if a[i] < p:
                            a[lt], a[i] = a[i], a[lt]; lt += 1; i += 1
                        elif a[i] > p:
                            a[i], a[gt] = a[gt], a[i]; gt -= 1
                        else:
                            i += 1
                    three_way(a, lo, lt - 1)
                    three_way(a, gt + 1, hi)

                print("depth on sorted n=200:", naive_depth(list(range(200))), "(O(n), so O(n^2) work)")
                d = [3, 1, 3, 2, 3, 3, 1, 2, 3]
                three_way(d, 0, len(d) - 1)
                print("3-way:", d)
            """),
        ],
        ["Best/Avg O(n log n) · Worst O(n^2)", "Space O(log n) avg stack · in-place · not stable", "Lomuto: i tracks end of < region", "Hoare: i from left, j from right, swap", "random.randint(lo, hi) pivot · median-of-three"],
        ["First or last element pivot on sorted input gives O(n^2).", "Many duplicates degrade Lomuto; use three-way partitioning.", "Recursing on the larger side first can blow the stack; recurse on the smaller side.", "Hoare returns a split index, not the pivot's final position."],
        [
            qa("basic", "What are quicksort's complexities?", "Best and average O(n log n), worst O(n^2). Space is O(log n) on average for the recursion stack and O(n) worst case. It is in-place but not stable."),
            qa("intermediate", "Compare Lomuto and Hoare partitioning.", "Lomuto uses one forward scan and places the pivot at its final index, which is easy to reason about but does more swaps and degrades to O(n^2) when all keys are equal. Hoare uses two pointers from both ends, does about three times fewer swaps and handles duplicates better, but returns a boundary index and the pivot may not be at its final position."),
            qa("intermediate", "When does quicksort hit its worst case and how do you avoid it?", "When every pivot is the minimum or maximum, partitions are of size n-1 and 0, giving n levels of O(n) work. This happens with a fixed first/last pivot on sorted or reverse-sorted input. Random pivots, median-of-three, or introsort's fallback to heap sort avoid it."),
            qa("intermediate", "Why is quicksort often faster than merge sort in practice?", "Partitioning works in place on contiguous memory with sequential access, giving excellent cache behaviour and no allocation for merge buffers. Its inner loop is very tight. Merge sort still wins when stability or guaranteed worst case is required."),
            qa("advanced", "What is three-way partitioning?", "It splits the array into less-than, equal-to and greater-than regions in one pass (Dijkstra's Dutch national flag). Equal keys are excluded from further recursion, so arrays with few distinct values sort in near O(n) instead of degrading."),
        ],
        ["merge-sort", "quickselect", "heap-sort", "divide-conquer"],
        chain(
            ("10,80,30,90,40", "pivot = 40", "Choose pivot", "Lomuto takes the last element, 40, as the pivot.", ),
            ("10 < 40", "i -> 1", "Scan", "10 is smaller, swap it into the left region (already there), i = 1.", "j=0"),
            ("30 < 40", "swap 80,30", "Scan", "30 is smaller, swap with a[1] -> [10,30,80,90,40], i = 2.", "j=2"),
            ("place pivot", "swap a[2],40", "Finish partition", "Swap pivot into index 2 -> [10,30,40,90,80].", "i=2"),
            ("recurse", "[10,30] | [90,80]", "Divide", "40 is final; quicksort both sides to get [10,30,40,80,90].", "split"),
        ),
    ),
    topic(
        "heap-sort", "Heap Sort", "sorting", "intermediate", "HS",
        "Build a max-heap, then repeatedly swap the root to the end and sift down: O(n log n) in place.",
        "Heap sort is a tournament: build a bracket so the champion sits on top, award them the last podium spot, then replay only the matches the champion was in to find the next champion.",
        "Heap sort first turns the array into a max-heap in O(n) using bottom-up heapify (sifting down from the last internal node to the root). It then repeatedly swaps the root (the maximum) with the last element of the heap, shrinks the heap by one, and sifts the new root down in O(log n). After n-1 extractions the array is sorted ascending. Time is O(n log n) in the best, average and worst case, and it uses O(1) auxiliary space, so it is in-place with a guaranteed bound, unlike quicksort. It is not stable, because sifting moves elements across long distances. In practice it is slower than quicksort due to poor cache locality (parent and child indices are far apart) and is used as the fallback in introsort. For children of index i, use 2i+1 and 2i+2; the parent is (i-1)//2.",
        ["Guaranteed O(n log n) with O(1) memory in embedded or real-time systems.", "Fallback inside introsort when recursion is too deep.", "Partial sorting: extract only the top k in O(n + k log n).", "Teaching heaps and priority queues."],
        [
            "Best = average = worst = O(n log n).",
            "Space O(1): in-place.",
            "Not stable.",
            "Bottom-up heapify builds the heap in O(n).",
            "Children at 2i+1 and 2i+2, parent at (i-1)//2.",
        ],
        [
            ex("Heap sort with trace", "basic", "Show the heap after build and each extraction.", "python", """
                def sift_down(a, i, n):
                    while True:
                        largest, l, r = i, 2 * i + 1, 2 * i + 2
                        if l < n and a[l] > a[largest]:
                            largest = l
                        if r < n and a[r] > a[largest]:
                            largest = r
                        if largest == i:
                            return
                        a[i], a[largest] = a[largest], a[i]
                        i = largest

                def heap_sort(a):
                    n = len(a)
                    for i in range(n // 2 - 1, -1, -1):
                        sift_down(a, i, n)
                    print("max-heap:", a)
                    for end in range(n - 1, 0, -1):
                        a[0], a[end] = a[end], a[0]
                        sift_down(a, 0, end)
                        print(f"extract {a[end]:2}: heap={a[:end]} sorted={a[end:]}")
                    return a

                print(heap_sort([4, 10, 3, 5, 1, 8]))
            """),
            ex("Using heapq", "basic", "heapq is a min-heap; popping n times sorts.", "python", """
                import heapq

                data = [9, 4, 7, 1, 8, 2]
                h = list(data)
                heapq.heapify(h)
                print("heapified:", h)
                print("sorted:", [heapq.heappop(h) for _ in range(len(data))])
                print("top 3:", heapq.nlargest(3, data), "bottom 2:", heapq.nsmallest(2, data))
            """),
            ex("Instability demo", "intermediate", "Equal keys can change relative order.", "python", """
                def heap_sort_key(a, key):
                    a, n = list(a), len(a)
                    def sift(i, n):
                        while True:
                            m, l, r = i, 2 * i + 1, 2 * i + 2
                            if l < n and key(a[l]) > key(a[m]): m = l
                            if r < n and key(a[r]) > key(a[m]): m = r
                            if m == i: return
                            a[i], a[m] = a[m], a[i]; i = m
                    for i in range(n // 2 - 1, -1, -1): sift(i, n)
                    for end in range(n - 1, 0, -1):
                        a[0], a[end] = a[end], a[0]; sift(0, end)
                    return a

                data = [(1, "a"), (1, "b"), (1, "c")]
                print(heap_sort_key(data, key=lambda x: x[0]))
            """),
        ],
        ["Best/Avg/Worst O(n log n)", "Space O(1) · in-place · not stable", "Build heap: for i in range(n//2-1, -1, -1)", "heapq.heapify(lst) O(n) · heappop O(log n)", "heapq.nlargest(k, xs)"],
        ["heapq is a min-heap; negate keys for a max-heap.", "Sifting down must stop at the current heap size, not len(a).", "Poor cache locality makes it slower than quicksort despite the same big-O."],
        [
            qa("basic", "What are heap sort's complexities?", "O(n log n) in all cases, O(1) auxiliary space, and it is not stable. Building the heap is O(n) and each of the n extractions costs O(log n)."),
            qa("intermediate", "Why is building a heap O(n) and not O(n log n)?", "Bottom-up heapify sifts down from the last internal node. Most nodes are near the leaves and sift only a short distance: n/4 nodes move at most 1 level, n/8 at most 2, and so on. The sum n * sum(k / 2^(k+1)) converges to O(n)."),
            qa("intermediate", "Why is heap sort slower than quicksort in practice?", "Sifting jumps between index i and 2i+1, which are far apart in memory for large heaps, causing cache misses. It also performs more comparisons per element. Quicksort scans memory sequentially."),
            qa("intermediate", "Where is heap sort actually used?", "Introsort (C++ std::sort and .NET Array.Sort) switches to heap sort when quicksort's recursion exceeds about 2 log n depth, guaranteeing O(n log n). It also suits memory-constrained systems that need a worst-case bound."),
        ],
        ["heaps", "selection-sort", "quick-sort"],
        chain(
            ("[4,10,3,5,1]", "unsorted", "Input", "Treat the array as a complete binary tree."),
            ("heapify", "[10,5,3,4,1]", "Build max-heap", "Sift down from index 1 then 0; the max 10 reaches the root.", "O(n)"),
            ("swap root", "[1,5,3,4 | 10]", "Extract max", "Swap 10 with the last element; 10 is now final.", "10"),
            ("sift down", "[5,4,3,1 | 10]", "Restore heap", "1 sinks below 5 and 4; the next max 5 is at the root.", "1"),
            ("repeat", "[1,3,4,5,10]", "Done", "Keep extracting until the heap has one element.", "sorted"),
        ),
    ),
]

TOPICS += [
    topic(
        "counting-sort", "Counting Sort", "sorting", "intermediate", "CS",
        "Count occurrences of each small integer key, then rebuild the array: O(n + k) without comparisons.",
        "Counting sort is sorting exam papers by grade using labelled trays: drop each paper into the tray for its grade, then stack the trays in order.",
        "Counting sort works on integer keys in a known small range [0, k). It counts how many times each key occurs, converts counts to prefix sums so count[v] tells where the last v belongs, and then places each element into an output array. Iterating the input from right to left during placement keeps equal keys in their original order, making it stable. Time is O(n + k) in the best, average and worst case, and space is O(n + k) for the count and output arrays, so it is not in-place. It beats comparison sorts when k is O(n), but becomes wasteful if k is huge (sorting a few 64-bit numbers). It does not compare elements, so the Omega(n log n) lower bound does not apply. Its stable variant is the per-digit subroutine inside radix sort.",
        ["Sorting ages, grades, or bytes (k = 256).", "Per-digit pass inside radix sort.", "Histogram-based tasks like bucketing pixel intensities.", "Sorting characters of a string over a small alphabet."],
        [
            "Best = average = worst = O(n + k).",
            "Space O(n + k): not in-place.",
            "Stable when placing elements from right to left.",
            "Only for integer (or integer-mappable) keys with a small range.",
            "Not comparison-based, so it can beat O(n log n).",
        ],
        [
            ex("Stable counting sort with trace", "basic", "Counts, prefix sums, then right-to-left placement.", "python", """
                def counting_sort(a, k):
                    count = [0] * k
                    for x in a:
                        count[x] += 1
                    print("counts:     ", count)
                    for v in range(1, k):
                        count[v] += count[v - 1]
                    print("prefix sums:", count)
                    out = [None] * len(a)
                    for x in reversed(a):
                        count[x] -= 1
                        out[count[x]] = x
                    return out

                print(counting_sort([4, 2, 2, 8, 3, 3, 1], 9))
            """),
            ex("Sorting records stably by small key", "intermediate", "Equal grades keep input order.", "python", """
                def counting_sort_by(items, key, k):
                    count = [0] * (k + 1)
                    for it in items:
                        count[key(it) + 1] += 1
                    for v in range(k):
                        count[v + 1] += count[v]
                    out = [None] * len(items)
                    for it in items:
                        out[count[key(it)]] = it
                        count[key(it)] += 1
                    return out

                students = [("ana", 3), ("ben", 1), ("cy", 3), ("dee", 2), ("eli", 1)]
                print(counting_sort_by(students, key=lambda s: s[1], k=4))
            """),
        ],
        ["Best/Avg/Worst O(n + k)", "Space O(n + k) · not in-place · stable", "count[v] += count[v-1] (prefix sums)", "Place from the right for stability", "collections.Counter for simple tallies"],
        ["Large key range k makes it slower and memory-hungry.", "Negative keys need an offset (x - min).", "The simple 'emit value count times' version loses attached data and stability."],
        [
            qa("basic", "What are counting sort's complexities?", "O(n + k) time in all cases and O(n + k) extra space, where k is the key range. It is stable (when implemented with prefix sums) and not in-place."),
            qa("intermediate", "Why can counting sort beat the O(n log n) lower bound?", "The lower bound applies only to comparison sorts. Counting sort uses keys as array indices, extracting information from the key values directly, so the decision-tree argument does not apply."),
            qa("intermediate", "How do you make counting sort stable?", "Turn counts into prefix sums giving ending positions, then iterate the input from right to left, decrementing count[key] and placing each item there. Alternatively compute starting positions and iterate left to right. Either way equal keys keep their input order."),
            qa("intermediate", "When is counting sort a bad idea?", "When the key range k is much larger than n, like sorting 100 numbers up to 10^9: memory and time become O(k). Then use radix sort with a smaller base or a comparison sort."),
        ],
        ["radix-sort", "bucket-sort", "sorting-lower-bound"],
        chain(
            ("[4,2,2,8,3]", "k = 9", "Input", "Keys lie in range 0-8."),
            ("count", "c[2]=2,c[3]=1", "Tally", "Count each key: 2 appears twice, 3, 4 and 8 once.", "keys"),
            ("prefix sum", "c[v]=end pos", "Positions", "Running totals give where each key's block ends: c[2]=2, c[3]=3, c[4]=4, c[8]=5.", "counts"),
            ("place", "right to left", "Stable fill", "Scan the input from the right, decrement c[x] and write x there.", "slots"),
            ("[2,2,3,4,8]", "O(n + k)", "Done", "Sorted without a single comparison.", "out"),
        ),
    ),
    topic(
        "radix-sort", "Radix Sort", "sorting", "intermediate", "RX",
        "Sort integers digit by digit with a stable sort, from least to most significant digit.",
        "Radix sort is like sorting mail first by house number, then by street, then by city, each time keeping the previous order within ties, so the final pile is fully ordered.",
        "LSD (least significant digit) radix sort processes keys one digit at a time, starting from the units digit, and uses a stable sort (usually counting sort over the base b) for each pass. Stability is essential: after sorting by the tens digit, items with equal tens digits stay ordered by their units digit. For d digits in base b the time is O(d * (n + b)) in the best, average and worst case, and space is O(n + b). With fixed-width keys such as 32-bit integers, d is constant and the sort is effectively linear. It is stable and not in-place in the usual implementation. MSD radix sort starts from the most significant digit and recurses into buckets, which suits strings and can stop early. Negative numbers need an offset or separate handling of the sign.",
        ["Sorting large arrays of fixed-width integers or IP addresses.", "Sorting fixed-length strings like dates (YYYYMMDD) or IDs.", "Suffix array construction.", "GPU sorting where parallel counting is cheap."],
        [
            "Best = average = worst = O(d * (n + b)).",
            "Space O(n + b): not in-place.",
            "Stable; requires a stable per-digit sort.",
            "LSD for fixed-width keys; MSD for variable-length strings.",
            "Larger base means fewer passes but bigger count arrays.",
        ],
        [
            ex("LSD radix sort with trace", "basic", "Base 10, one stable bucket pass per digit.", "python", """
                def radix_sort(a, base=10):
                    a = list(a)
                    exp, biggest = 1, max(a)
                    while biggest // exp > 0:
                        buckets = [[] for _ in range(base)]
                        for x in a:
                            buckets[(x // exp) % base].append(x)
                        a = [x for b in buckets for x in b]
                        print(f"by digit {exp:>4}: {a}")
                        exp *= base
                    return a

                print(radix_sort([170, 45, 75, 90, 802, 24, 2, 66]))
            """),
            ex("Why the per-digit sort must be stable", "intermediate", "An unstable pass scrambles earlier work.", "python", """
                nums = [21, 12, 22, 11]
                by_units = sorted(nums, key=lambda x: x % 10)
                stable = sorted(by_units, key=lambda x: x // 10)
                print("after units:", by_units, "after tens (stable):", stable)

                unstable = sorted(by_units, key=lambda x: (x // 10, -(x % 10)))
                print("an order-reversing tens pass would give:", unstable)
            """),
            ex("Radix sort with negatives", "intermediate", "Offset by the minimum, sort, shift back.", "python", """
                def radix_nonneg(a):
                    exp = 1
                    while a and max(a) // exp:
                        buckets = [[] for _ in range(10)]
                        for x in a:
                            buckets[(x // exp) % 10].append(x)
                        a = [x for b in buckets for x in b]
                        exp *= 10
                    return a

                data = [5, -3, 12, 0, -20, 7]
                lo = min(data)
                print([x + lo for x in radix_nonneg([x - lo for x in data])])
            """),
        ],
        ["Best/Avg/Worst O(d * (n + b))", "Space O(n + b) · not in-place · stable", "digit = (x // exp) % base", "Base 256 -> 4 passes for 32-bit ints", "LSD: units first; MSD: recursive buckets"],
        ["An unstable per-digit sort gives wrong results.", "Negative numbers need an offset or sign handling.", "For small n, the constant factors lose to Timsort."],
        [
            qa("basic", "What are radix sort's complexities?", "O(d * (n + b)) time in all cases for d digits in base b, and O(n + b) extra space. It is stable and not in-place."),
            qa("intermediate", "Why must LSD radix sort use a stable sort for each digit?", "Each pass must preserve the order established by previous, less significant digits. If the tens pass reordered keys with equal tens digits, the units ordering from the previous pass would be lost."),
            qa("intermediate", "LSD vs MSD radix sort?", "LSD processes the least significant digit first, needs fixed-width keys and always does d passes. MSD starts from the most significant digit, partitions into buckets and recurses, handles variable-length strings and can stop early once buckets are size one, but it has more overhead."),
            qa("advanced", "Is radix sort really linear?", "For keys of fixed width w bits it does w / log b passes, so with constant w it is O(n). But if keys grow with n (for example distinct keys need at least log n bits), d grows like log n / log b and the advantage over O(n log n) shrinks."),
        ],
        ["counting-sort", "bucket-sort", "sorting-lower-bound"],
        chain(
            ("5 numbers", "[170,45,75,90,802]", "Input", "Process units, then tens, then hundreds."),
            ("units", "[170,90,802,45,75]", "Pass 1", "Stable bucketing by the last digit: 0,0,2,5,5.", "x % 10"),
            ("tens", "[802,45,170,75,90]", "Pass 2", "Bucket by tens digit: 0,4,7,7,9; ties keep pass 1 order.", "(x//10)%10"),
            ("hundreds", "[45,75,90,170,802]", "Pass 3", "Bucket by hundreds digit: 0,0,0,1,8.", "(x//100)%10"),
            ("sorted", "O(d(n+b))", "Done", "Three stable passes produce a fully sorted array.", "done"),
        ),
    ),
    topic(
        "bucket-sort", "Bucket Sort", "sorting", "intermediate", "BU",
        "Scatter uniformly distributed values into buckets, sort each bucket, then concatenate.",
        "Bucket sort is sorting a pile of letters by first dropping them into 26 pigeonholes by initial letter, then tidying each small pigeonhole by hand.",
        "Bucket sort divides the value range into n buckets, distributes each element into the bucket for its range, sorts each bucket (often with insertion sort), and concatenates the buckets in order. If inputs are uniformly distributed, each bucket holds O(1) elements on average, so the expected time is O(n + k) for k buckets, and best case is O(n + k). The worst case is O(n^2) when all elements land in one bucket and insertion sort is used (O(n log n) with a better inner sort). Space is O(n + k), so it is not in-place. It is stable if elements are appended to buckets in order and the inner sort is stable. It is commonly applied to floats in [0, 1) and to problems like top-k frequent elements, where frequency is used as the bucket index.",
        ["Sorting uniformly distributed floats in [0, 1).", "Top-k frequent elements using frequency buckets.", "Histogramming and approximate ordering.", "Parallel sorting by key ranges."],
        [
            "Best O(n + k), average O(n + k) for uniform input, worst O(n^2).",
            "Space O(n + k): not in-place.",
            "Stable if the inner sort is stable.",
            "Performance depends on the input distribution.",
            "Bucket index for x in [0,1): int(x * k).",
        ],
        [
            ex("Bucket sort on floats", "basic", "Show the buckets before and after inner sorting.", "python", """
                def bucket_sort(a, k=5):
                    buckets = [[] for _ in range(k)]
                    for x in a:
                        buckets[min(int(x * k), k - 1)].append(x)
                    print("scattered:", buckets)
                    for b in buckets:
                        b.sort()
                    print("sorted each:", buckets)
                    return [x for b in buckets for x in b]

                print(bucket_sort([0.78, 0.17, 0.39, 0.26, 0.72, 0.94, 0.21, 0.12, 0.23, 0.68]))
            """),
            ex("Top-k frequent with frequency buckets", "intermediate", "O(n) by bucketing on count.", "python", """
                from collections import Counter

                def top_k_frequent(nums, k):
                    counts = Counter(nums)
                    buckets = [[] for _ in range(len(nums) + 1)]
                    for val, c in counts.items():
                        buckets[c].append(val)
                    out = []
                    for c in range(len(buckets) - 1, 0, -1):
                        for val in buckets[c]:
                            out.append(val)
                            if len(out) == k:
                                return out
                    return out

                print(top_k_frequent([1, 1, 1, 2, 2, 3, 4, 4, 4, 4], 2))
            """),
            ex("Skewed input worst case", "intermediate", "Everything falls into one bucket.", "python", """
                data = [0.01, 0.02, 0.015, 0.03, 0.005, 0.025]
                k = 6
                sizes = [0] * k
                for x in data:
                    sizes[min(int(x * k), k - 1)] += 1
                print("bucket sizes:", sizes, "-> inner sort does all the work")
            """),
        ],
        ["Best O(n+k) · Avg O(n+k) uniform · Worst O(n^2)", "Space O(n + k) · not in-place · stable*", "idx = min(int(x * k), k - 1)", "Inner sort: insertion sort or sorted()", "Top-k frequent: buckets[count]"],
        ["Skewed data collapses into a few buckets.", "Off-by-one: x == 1.0 maps to index k unless clamped.", "Choosing too many buckets wastes memory; too few loses the benefit."],
        [
            qa("basic", "What are bucket sort's complexities?", "Best and average O(n + k) when inputs are uniformly distributed, worst O(n^2) if everything lands in one bucket and insertion sort is used. Space is O(n + k). It is stable if the inner sort is stable."),
            qa("intermediate", "How does bucket sort differ from counting sort?", "Counting sort has one slot per exact key and needs integer keys in a small range. Bucket sort groups ranges of values, works for floats, and needs an inner sort per bucket, so its performance depends on how evenly values spread."),
            qa("intermediate", "How do you get top-k frequent elements in O(n)?", "Count frequencies with a hash map, then put each value into a bucket indexed by its frequency (at most n). Walk buckets from high frequency to low, collecting values until you have k."),
            qa("advanced", "How would you make bucket sort robust to skewed data?", "Choose bucket boundaries from sampled quantiles instead of equal-width ranges (as in sample sort), or use O(n log n) inner sorts so the worst case is bounded. Recursively bucketing large buckets also helps."),
        ],
        ["counting-sort", "radix-sort", "insertion-sort"],
        chain(
            ("4 floats, k=5", "[.78,.17,.39,.26]", "Input", "Floats in [0,1) go into 5 equal-width buckets."),
            ("scatter", "int(x*5)", "Distribute", ".17 -> bucket 0, .26 and .39 -> bucket 1, .78 -> bucket 3.", "x"),
            ("sort buckets", "insertion sort", "Inner sort", "Each bucket is small, so sorting it is cheap.", "buckets"),
            ("concatenate", "in bucket order", "Gather", "Read buckets 0..4 to get [.17,.26,.39,.78].", "lists"),
        ),
    ),
    topic(
        "timsort-stability", "Timsort & Sort Stability", "sorting", "intermediate", "TS",
        "Python's sorted() is a stable, adaptive merge/insertion hybrid that exploits existing runs.",
        "Timsort is a librarian who notices shelves already partly in order, keeps those stretches intact, tidies short messy stretches by hand, and then merges the stretches together.",
        "Timsort, designed by Tim Peters for Python and also used by Java for objects, scans the input for natural runs (ascending, or strictly descending ones that it reverses). Runs shorter than minrun (32-64) are extended with binary insertion sort, and runs are pushed onto a stack and merged according to invariants that keep merges balanced. Galloping mode speeds up merges when one run consistently wins, using exponential search. Complexity is O(n) best case on sorted or reverse-sorted input, and O(n log n) average and worst. It needs up to O(n) extra space for merging and is not in-place. A stable sort keeps equal elements in their original relative order, which enables multi-key sorting by sorting on the secondary key first and the primary key second. Python's sort with key= uses decorate-sort-undecorate internally, calling the key once per element.",
        ["Default sorting in Python (list.sort, sorted) and Java object sorts.", "Multi-key sorting via successive stable sorts.", "Real-world data that is partially ordered (logs, appended records).", "Sorting records by key without disturbing earlier orderings."],
        [
            "Best O(n), average O(n log n), worst O(n log n).",
            "Space O(n): not in-place.",
            "Stable: equal keys keep input order.",
            "Finds natural runs, uses binary insertion for short runs, merges with galloping.",
            "key= is computed once per element; reverse=True keeps stability.",
        ],
        [
            ex("Stability enables multi-key sorts", "basic", "Sort by secondary key, then by primary.", "python", """
                people = [("bob", 25), ("ann", 30), ("cat", 25), ("dan", 30), ("eve", 22)]
                by_name = sorted(people)
                by_age_then_name = sorted(by_name, key=lambda p: p[1])
                print(by_age_then_name)
                print(sorted(people, key=lambda p: (-p[1], p[0])))
            """),
            ex("Detect natural runs", "intermediate", "The first step of Timsort.", "python", """
                def runs(a):
                    out, i = [], 0
                    while i < len(a):
                        j = i + 1
                        if j < len(a) and a[j] < a[i]:
                            while j < len(a) and a[j] < a[j - 1]:
                                j += 1
                            out.append(a[i:j][::-1])
                        else:
                            while j < len(a) and a[j] >= a[j - 1]:
                                j += 1
                            out.append(a[i:j])
                        i = j
                    return out

                print(runs([1, 2, 5, 9, 8, 6, 3, 4, 7, 10]))
            """),
            ex("Mini Timsort", "advanced", "Insertion-sort fixed chunks then merge them.", "python", """
                import heapq

                def mini_timsort(a, minrun=4):
                    a = list(a)
                    for lo in range(0, len(a), minrun):
                        chunk = a[lo:lo + minrun]
                        for i in range(1, len(chunk)):
                            k, j = chunk[i], i - 1
                            while j >= 0 and chunk[j] > k:
                                chunk[j + 1] = chunk[j]; j -= 1
                            chunk[j + 1] = k
                        a[lo:lo + minrun] = chunk
                    print("runs:", [a[i:i + minrun] for i in range(0, len(a), minrun)])
                    size = minrun
                    while size < len(a):
                        for lo in range(0, len(a), 2 * size):
                            a[lo:lo + 2 * size] = list(heapq.merge(a[lo:lo + size], a[lo + size:lo + 2 * size]))
                        size *= 2
                    return a

                print(mini_timsort([9, 3, 7, 1, 8, 2, 6, 4, 5, 0, 11, 10]))
            """),
        ],
        ["Best O(n) · Avg/Worst O(n log n)", "Space O(n) · not in-place · stable", "sorted(xs, key=f, reverse=True)", "key=operator.itemgetter(1) · attrgetter('age')", "functools.cmp_to_key(cmp)"],
        ["list.sort() returns None; use sorted() for a new list.", "Comparing mixed types like int and str raises TypeError.", "Negating keys for descending order only works for numbers; use reverse=True or multiple passes."],
        [
            qa("basic", "What does it mean for a sort to be stable?", "Elements with equal keys appear in the output in the same relative order as in the input. It matters when sorting records by one field while preserving an earlier ordering by another."),
            qa("intermediate", "What are Timsort's complexities and why is the best case O(n)?", "O(n) best, O(n log n) average and worst, O(n) extra space, stable. On already sorted (or strictly reversed) input it detects a single run covering the whole array and finishes after one pass without merging."),
            qa("intermediate", "How do you sort by multiple keys in Python?", "Use a tuple key such as key=lambda r: (r.dept, -r.salary), or exploit stability by sorting on the least significant key first and then on more significant keys. The latter handles mixed ascending and descending on non-numeric fields."),
            qa("advanced", "What is galloping in Timsort?", "During a merge, if one run wins many comparisons in a row (MIN_GALLOP, initially 7), Timsort switches to exponential search to find how many elements from that run come next and copies them in bulk. It makes merging highly structured data much faster and adapts its threshold dynamically."),
            qa("advanced", "Which sorts are stable?", "Insertion, bubble, merge, counting, radix, bucket (with stable inner sort) and Timsort are stable. Selection sort, heap sort and typical quicksort are not. Any sort can be made stable by adding the original index as a tie-breaker."),
        ],
        ["merge-sort", "insertion-sort", "sorting-lower-bound"],
        chain(
            ("1,2,5,9,8,6,3", "scan", "Find runs", "Detect natural ascending and descending runs."),
            ("runs", "[1,2,5,9] [8,6,3]", "Split", "The second run is strictly descending.", "runs"),
            ("reverse", "[3,6,8]", "Normalise", "Descending runs are reversed in place, which keeps stability because they were strict.", "desc"),
            ("extend", "binary insertion", "Minrun", "Short runs are extended to minrun with binary insertion sort.", "short"),
            ("merge", "gallop if one wins", "Merge stack", "Runs are merged with balance invariants: [1,2,3,5,6,8,9].", "merge"),
        ),
    ),
    topic(
        "sorting-lower-bound", "Comparison Sort Lower Bound", "sorting", "advanced", "LB",
        "Any comparison-based sort needs Omega(n log n) comparisons in the worst case.",
        "Sorting by comparisons is a game of twenty questions with yes/no answers: with n! possible orderings, you need at least log2(n!) questions to pin down the right one.",
        "A comparison sort learns about the input only by comparing pairs of elements. Its behaviour can be modelled as a binary decision tree where each internal node is a comparison and each leaf is one output permutation. To sort correctly the tree must have at least n! leaves, one per possible ordering of distinct elements. A binary tree with L leaves has height at least log2 L, so the worst-case number of comparisons is at least log2(n!). By Stirling's approximation, log2(n!) is about n log2 n - 1.44n, which is Theta(n log n). Merge sort and heap sort therefore are asymptotically optimal comparison sorts. The bound also holds for the average case. Non-comparison sorts like counting, radix and bucket sort escape it by exploiting the structure of keys.",
        ["Arguing that an O(n log n) sort is optimal.", "Recognising when counting or radix sort can do better.", "Proving lower bounds for related problems via reduction (element distinctness, convex hull).", "Interview discussions about 'can you sort faster?'."],
        [
            "Decision tree must have at least n! leaves.",
            "Height >= log2(n!) = Theta(n log n).",
            "Applies to worst and average case of comparison sorts.",
            "Merge sort and heap sort are optimal up to constants.",
            "Non-comparison sorts sidestep it by using key structure.",
        ],
        [
            ex("log2(n!) vs n log2 n", "basic", "Compare the bound with merge sort's comparisons.", "python", """
                import math

                def merge_comparisons(a):
                    if len(a) <= 1:
                        return a, 0
                    m = len(a) // 2
                    l, x = merge_comparisons(a[:m])
                    r, y = merge_comparisons(a[m:])
                    out, i, j, c = [], 0, 0, x + y
                    while i < len(l) and j < len(r):
                        c += 1
                        if l[i] <= r[j]:
                            out.append(l[i]); i += 1
                        else:
                            out.append(r[j]); j += 1
                    return out + l[i:] + r[j:], c

                import random
                random.seed(0)
                for n in (4, 8, 16, 64, 256):
                    data = random.sample(range(n * 10), n)
                    bound = math.ceil(math.log2(math.factorial(n)))
                    print(f"n={n:4} lower bound={bound:5} merge sort used={merge_comparisons(data)[1]:5} n*log2(n)={n * math.log2(n):7.0f}")
            """),
            ex("Decision tree for 3 elements", "intermediate", "3! = 6 leaves needs height ceil(log2 6) = 3.", "python", """
                import itertools, math

                def sort3(a, b, c):
                    comps = 0
                    comps += 1
                    if a > b: a, b = b, a
                    comps += 1
                    if b > c: b, c = c, b
                    comps += 1
                    if a > b: a, b = b, a
                    return (a, b, c), comps

                worst = 0
                for p in itertools.permutations([1, 2, 3]):
                    out, c = sort3(*p)
                    worst = max(worst, c)
                    print(p, "->", out)
                print("permutations:", math.factorial(3), "min height:", math.ceil(math.log2(6)), "used:", worst)
            """),
        ],
        ["log2(n!) ~ n log2 n - 1.44 n", "Leaves >= n!  ->  height >= log2(n!)", "Optimal: merge sort, heap sort", "Escape hatch: counting/radix/bucket", "math.lgamma(n + 1) / math.log(2) = log2(n!)"],
        ["The bound is about comparisons, not total time with integer tricks.", "It assumes distinct keys; with few distinct values, three-way sorts can be faster.", "Being optimal asymptotically says nothing about constants or cache behaviour."],
        [
            qa("intermediate", "Why can no comparison sort beat O(n log n) in the worst case?", "Model the algorithm as a binary decision tree: every distinct input permutation must reach a different leaf, so there are at least n! leaves. A binary tree's height is at least log2 of its leaves, and log2(n!) = Theta(n log n) by Stirling's approximation."),
            qa("intermediate", "How do counting and radix sort avoid this bound?", "They are not comparison sorts: they use key values as array indices or digits, gaining more than one bit of information per operation. They pay with assumptions about the keys, such as small integer range or fixed width."),
            qa("advanced", "Does the bound also apply to the average case?", "Yes. In a binary tree with n! leaves, the average leaf depth is at least log2(n!), so the expected number of comparisons over uniformly random permutations is also Omega(n log n)."),
            qa("advanced", "How can the bound prove other lower bounds?", "By reduction: if a problem could be solved faster than n log n and that solution could be used to sort, sorting would beat its bound. For example, convex hull in the comparison model is Omega(n log n) because points on a parabola let you sort by computing the hull."),
        ],
        ["merge-sort", "counting-sort", "radix-sort", "big-o"],
        chain(
            ("n items", "n! orders", "Possibilities", "Distinct items can arrive in any of n! orders."),
            ("a < b ?", "yes / no", "Comparison", "Each comparison splits the remaining possibilities into two groups.", "query"),
            ("tree", "n! leaves", "Decision tree", "A correct sort needs a distinct leaf for every permutation.", "branches"),
            ("height", ">= log2(n!)", "Depth bound", "A binary tree with n! leaves has height at least log2(n!).", "leaves"),
            ("Stirling", "Theta(n log n)", "Conclusion", "log2(n!) is about n log2 n, so comparison sorts need Omega(n log n) comparisons.", "bound"),
        ),
    ),
    topic(
        "quickselect", "Quickselect & k-th Element", "sorting", "intermediate", "QK",
        "Partition like quicksort but recurse into only one side to find the k-th smallest in O(n) average.",
        "Quickselect is finding the 10th tallest person by splitting the room around a random person's height and then only searching the half that must contain your answer.",
        "Quickselect finds the k-th smallest element without fully sorting. It partitions the array around a pivot exactly like quicksort; if the pivot lands at index k it is the answer, otherwise it recurses into only the side containing k. Because it discards one side each time, the expected work is n + n/2 + n/4 + ... = O(n) with random pivots. The worst case is O(n^2) when pivots are consistently bad, and the median-of-medians pivot rule guarantees O(n) worst case at a higher constant. It works in place with O(1) extra space when written iteratively, and it reorders the array. Alternatives for the k largest are a size-k min-heap (O(n log k), good for streams) or heapq.nlargest. Quickselect underlies median finding, top-k queries and introselect in C++ std::nth_element.",
        ["Finding the median or percentile of a dataset.", "Top-k closest points or largest values.", "C++ std::nth_element and NumPy partition.", "Selecting a pivot for other algorithms."],
        [
            "Average O(n), worst O(n^2); median-of-medians gives worst O(n).",
            "Space O(1) iterative; reorders the input.",
            "k-th largest = (n - k)-th smallest (0-indexed).",
            "Heap alternative: O(n log k) and works on streams.",
            "Random pivots make bad cases unlikely.",
        ],
        [
            ex("Iterative quickselect", "basic", "Lomuto partition with random pivot, trace the shrinking range.", "python", """
                import random

                def quickselect(a, k):
                    a, lo, hi = list(a), 0, len(a) - 1
                    while True:
                        r = random.randint(lo, hi)
                        a[r], a[hi] = a[hi], a[r]
                        p, i = a[hi], lo
                        for j in range(lo, hi):
                            if a[j] < p:
                                a[i], a[j] = a[j], a[i]
                                i += 1
                        a[i], a[hi] = a[hi], a[i]
                        print(f"range [{lo},{hi}] pivot {p} -> index {i}")
                        if i == k:
                            return a[i]
                        if i < k:
                            lo = i + 1
                        else:
                            hi = i - 1

                random.seed(3)
                data = [7, 10, 4, 3, 20, 15, 1, 9]
                print("3rd smallest:", quickselect(data, 2), "check:", sorted(data)[2])
            """),
            ex("k-th largest three ways", "intermediate", "Quickselect, heap of size k, and heapq.nlargest.", "python", """
                import heapq

                def kth_largest_heap(nums, k):
                    h = []
                    for x in nums:
                        heapq.heappush(h, x)
                        if len(h) > k:
                            heapq.heappop(h)
                    return h[0]

                nums = [3, 2, 1, 5, 6, 4]
                k = 2
                print("heap:", kth_largest_heap(nums, k))
                print("nlargest:", heapq.nlargest(k, nums)[-1])
                print("sorted:", sorted(nums)[-k])
            """),
        ],
        ["Avg O(n) · Worst O(n^2) · median-of-medians O(n)", "k-th largest -> index n - k", "heapq.nlargest(k, xs) O(n log k)", "Min-heap of size k for streams", "statistics.median(xs)"],
        ["Off-by-one between 1-indexed k and 0-indexed positions.", "It mutates the array; copy first if order matters.", "Duplicates with Lomuto can degrade; use three-way partitioning."],
        [
            qa("intermediate", "How does quickselect achieve O(n) average time?", "After partitioning, it recurses into only the side containing k. With random pivots the subproblem shrinks by a constant fraction in expectation, so total work is a geometric series n + n/2 + n/4 + ... = O(n)."),
            qa("intermediate", "Quickselect vs a heap for the k-th largest?", "Quickselect is O(n) average and in place but needs all data in memory and mutates it. A min-heap of size k is O(n log k), uses O(k) memory and works on streams. For small k or streaming data the heap is often preferred."),
            qa("advanced", "What is median of medians?", "A deterministic pivot rule: split into groups of five, take each group's median, and recursively find the median of those medians. It guarantees the pivot is greater than about 30% and less than about 30% of elements, giving O(n) worst case, though with large constants."),
            qa("intermediate", "What is the worst case of quickselect?", "O(n^2), when each pivot is the smallest or largest remaining element so the range shrinks by only one. Random pivots make this astronomically unlikely, and introselect switches to median of medians if progress stalls."),
        ],
        ["quick-sort", "heaps", "divide-conquer"],
        chain(
            ("find k=2", "[7,10,4,3,20]", "Goal", "Find the 3rd smallest (index 2)."),
            ("pivot 7", "[4,3 | 7 | 10,20]", "Partition", "7 lands at index 2 after partitioning.", "pivot"),
            ("i == k ?", "2 == 2", "Check", "The pivot index equals k, so 7 is the answer.", "index"),
            ("else", "recurse one side", "Narrow", "If i < k search right, if i > k search left; never both.", "side"),
        ),
    ),
    topic(
        "binary-search", "Binary Search & Search on Answer", "searching", "intermediate", "BN",
        "Halve a sorted (or monotonic) search space each step: O(log n).",
        "Binary search is guessing a number between 1 and 100 when told 'higher' or 'lower': guess 50, then 75, and you are done in about seven guesses.",
        "Binary search finds a target in a sorted array by comparing with the middle element and discarding half the range each step, giving O(log n) time and O(1) space. The robust template searches for the first index where a monotonic predicate becomes true, using a half-open range lo, hi and mid = (lo + hi) // 2; this naturally yields lower_bound (first >= x) and upper_bound (first > x). Python's bisect module implements these as bisect_left and bisect_right. Binary search on the answer applies the same idea to a numeric answer space: if feasible(x) is monotonic (false...false, true...true), search for the smallest feasible x, as in 'minimum ship capacity to deliver in D days' or 'Koko eating bananas'. Variants include searching in a rotated sorted array, finding a peak, and searching on real numbers with a fixed number of iterations. Most bugs are off-by-one errors or infinite loops from not shrinking the range.",
        ["Lookup in sorted arrays and indexes.", "Finding insertion points and counts in sorted data (bisect).", "Minimising a maximum or maximising a minimum (search on answer).", "Debugging by bisection, like git bisect."],
        [
            "O(log n) time, O(1) space; needs sorted or monotonic predicate.",
            "Template: while lo < hi: mid = (lo+hi)//2; if ok(mid): hi = mid else lo = mid+1.",
            "bisect_left = first >= x; bisect_right = first > x.",
            "Search on answer: binary search over values with a feasibility check.",
            "Count of x in sorted a: bisect_right - bisect_left.",
        ],
        [
            ex("Classic and lower_bound", "basic", "Exact match and first-true template with trace.", "python", """
                import bisect

                def lower_bound(a, x):
                    lo, hi = 0, len(a)
                    while lo < hi:
                        mid = (lo + hi) // 2
                        print(f"  lo={lo} hi={hi} mid={mid} a[mid]={a[mid]}")
                        if a[mid] >= x:
                            hi = mid
                        else:
                            lo = mid + 1
                    return lo

                a = [1, 3, 5, 5, 5, 8, 13]
                print("lower_bound(5) =", lower_bound(a, 5))
                print("bisect_left:", bisect.bisect_left(a, 5), "bisect_right:", bisect.bisect_right(a, 5))
                print("count of 5:", bisect.bisect_right(a, 5) - bisect.bisect_left(a, 5))
            """),
            ex("Search on the answer", "intermediate", "Minimum ship capacity to ship packages within D days.", "python", """
                def days_needed(weights, cap):
                    days, load = 1, 0
                    for w in weights:
                        if load + w > cap:
                            days, load = days + 1, 0
                        load += w
                    return days

                def min_capacity(weights, d):
                    lo, hi = max(weights), sum(weights)
                    while lo < hi:
                        mid = (lo + hi) // 2
                        if days_needed(weights, mid) <= d:
                            hi = mid
                        else:
                            lo = mid + 1
                    return lo

                w = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
                print("min capacity for 5 days:", min_capacity(w, 5))
            """),
            ex("Rotated sorted array", "intermediate", "One half is always sorted.", "python", """
                def search_rotated(a, t):
                    lo, hi = 0, len(a) - 1
                    while lo <= hi:
                        mid = (lo + hi) // 2
                        if a[mid] == t:
                            return mid
                        if a[lo] <= a[mid]:
                            if a[lo] <= t < a[mid]:
                                hi = mid - 1
                            else:
                                lo = mid + 1
                        else:
                            if a[mid] < t <= a[hi]:
                                lo = mid + 1
                            else:
                                hi = mid - 1
                    return -1

                arr = [4, 5, 6, 7, 0, 1, 2]
                print([search_rotated(arr, t) for t in (0, 4, 2, 3)])
            """),
        ],
        ["bisect.bisect_left(a, x) · bisect.bisect_right(a, x)", "bisect.insort(a, x)", "mid = (lo + hi) // 2  (lo + (hi - lo)//2 in C/Java)", "O(log n): 10^9 -> ~30 steps", "Answer search: lo=min feasible, hi=max"],
        ["Infinite loop when lo = mid with lo < hi; use lo = mid + 1.", "Integer overflow of lo + hi in fixed-width languages.", "Array must be sorted by the same key you search with.", "Mixing closed [lo, hi] and half-open [lo, hi) conventions."],
        [
            qa("basic", "What is the complexity of binary search and what does it require?", "O(log n) time and O(1) space iteratively. It requires random access and a sorted array, or more generally a monotonic predicate over the search space."),
            qa("intermediate", "How do you find the first occurrence of a value?", "Use the lower_bound template: on a[mid] >= x set hi = mid, else lo = mid + 1, until lo == hi. lo is the first index with a[lo] >= x; check that it is in range and equals x. bisect_left does exactly this."),
            qa("intermediate", "What is binary search on the answer?", "Instead of searching an array, you search the range of possible answers and test each candidate with a feasibility function. If feasibility is monotonic, binary search finds the boundary in O(log range * cost of check). Examples include minimum capacity, minimum time and maximising the minimum distance."),
            qa("intermediate", "How do you search a rotated sorted array?", "At each step at least one half (lo..mid or mid..hi) is sorted, which you detect by comparing a[lo] with a[mid]. If the target lies within the sorted half's range, search there, otherwise search the other half. Still O(log n) for distinct values."),
            qa("advanced", "Why is mid = (lo + hi) // 2 dangerous in some languages?", "In languages with fixed-width integers like Java or C, lo + hi can overflow for large indices, producing a negative mid. Use lo + (hi - lo) / 2. Python integers do not overflow, so it is safe there."),
        ],
        ["two-pointers", "arrays-dynamic", "bst", "divide-conquer"],
        chain(
            ("find 13", "[1,3,5,8,13,21]", "Start", "lo = 0, hi = 5."),
            ("mid=2", "a[2]=5 < 13", "Go right", "Target is larger, so lo = 3.", "lo=0,hi=5"),
            ("mid=4", "a[4]=13", "Found", "a[4] equals the target after 2 probes.", "lo=3,hi=5"),
            ("log2 n", "~3 steps for 6", "Cost", "Each step halves the range: O(log n).", "found"),
        ),
    ),
    topic(
        "two-pointers", "Two Pointers", "searching", "basic", "TP",
        "Move two indices toward each other or in the same direction to replace nested loops with one pass.",
        "Two pointers is two people walking toward each other along a sorted shelf: if the pair of prices is too expensive, the right person steps left; if too cheap, the left person steps right.",
        "The two-pointer technique uses two indices that move through a sequence according to a rule, turning many O(n^2) pair searches into O(n). Opposite-direction pointers start at both ends of a sorted array and move inward, as in pair sum, container with most water, and palindrome checks. Same-direction (fast and slow) pointers handle in-place filtering, removing duplicates, and partitioning, where a write pointer trails a read pointer. On linked lists, fast and slow pointers find the middle and detect cycles. For 3Sum, sort the array, fix one element and run a two-pointer pass on the rest, giving O(n^2) instead of O(n^3). The key correctness argument is that each pointer move discards candidates that cannot be part of a better answer. Sorting first costs O(n log n) if the input is not already sorted.",
        ["Pair or triplet sums in sorted arrays.", "Removing duplicates or filtering in place.", "Merging two sorted arrays.", "Palindrome and reversal problems."],
        [
            "Opposite ends: sorted pair problems in O(n).",
            "Read/write pointers: in-place filtering with O(1) space.",
            "Fast/slow: cycle detection and middle finding.",
            "3Sum: sort + fix one + two pointers = O(n^2).",
            "Justify each move: it cannot skip a valid answer.",
        ],
        [
            ex("Pair sum in sorted array", "basic", "Trace how pointers move.", "python", """
                def pair_sum(a, target):
                    i, j = 0, len(a) - 1
                    while i < j:
                        s = a[i] + a[j]
                        print(f"i={i} j={j} sum={s}")
                        if s == target:
                            return a[i], a[j]
                        if s < target:
                            i += 1
                        else:
                            j -= 1
                    return None

                print(pair_sum([1, 2, 4, 7, 11, 15], 15))
            """),
            ex("Remove duplicates in place", "basic", "Write pointer trails read pointer.", "python", """
                def dedupe(a):
                    if not a:
                        return 0
                    w = 1
                    for r in range(1, len(a)):
                        if a[r] != a[w - 1]:
                            a[w] = a[r]
                            w += 1
                    return w

                arr = [0, 0, 1, 1, 1, 2, 2, 3, 3, 4]
                k = dedupe(arr)
                print(k, arr[:k])
            """),
            ex("3Sum and container with most water", "intermediate", "Two classic O(n^2) and O(n) uses.", "python", """
                def three_sum(nums):
                    nums, out = sorted(nums), []
                    for i in range(len(nums) - 2):
                        if i and nums[i] == nums[i - 1]:
                            continue
                        lo, hi = i + 1, len(nums) - 1
                        while lo < hi:
                            s = nums[i] + nums[lo] + nums[hi]
                            if s < 0:
                                lo += 1
                            elif s > 0:
                                hi -= 1
                            else:
                                out.append((nums[i], nums[lo], nums[hi]))
                                lo += 1
                                while lo < hi and nums[lo] == nums[lo - 1]:
                                    lo += 1
                    return out

                def max_area(h):
                    i, j, best = 0, len(h) - 1, 0
                    while i < j:
                        best = max(best, (j - i) * min(h[i], h[j]))
                        if h[i] < h[j]:
                            i += 1
                        else:
                            j -= 1
                    return best

                print(three_sum([-1, 0, 1, 2, -1, -4]))
                print(max_area([1, 8, 6, 2, 5, 4, 8, 3, 7]))
            """),
        ],
        ["i, j = 0, len(a) - 1; while i < j", "Write pointer: a[w] = a[r]; w += 1", "3Sum: sort, skip duplicates, O(n^2)", "Fast/slow: slow = slow.next; fast = fast.next.next", "Merge: compare a[i], b[j], advance smaller"],
        ["Opposite-end pair technique needs sorted input.", "Forgetting to skip duplicates produces repeated triplets.", "Moving the wrong pointer (e.g. the taller wall) misses the optimum."],
        [
            qa("basic", "When does the two-pointer technique apply?", "When the data is sorted or the problem has a monotonic property, so moving one pointer can safely discard options. Typical cases are pair sums, in-place filtering, merging sorted sequences and palindromes."),
            qa("intermediate", "Why is pair sum with two pointers correct?", "If a[i] + a[j] is too small, pairing a[i] with any element left of j is even smaller, so a[i] can be discarded and i moves right. Symmetrically, if the sum is too large, a[j] is discarded. No valid pair is skipped, giving O(n)."),
            qa("intermediate", "How do you solve 3Sum efficiently?", "Sort the array, then for each index i run a two-pointer search on the suffix for pairs summing to -nums[i]. Skip duplicate values for i and for the pointers to avoid repeated triplets. Total O(n^2) time, O(1) extra space beyond output."),
            qa("intermediate", "Why move the shorter wall in container with most water?", "The area is limited by the shorter wall. Moving the taller wall inward reduces width and cannot increase the limiting height, so it never improves the answer. Moving the shorter wall is the only move that might."),
        ],
        ["sliding-window", "binary-search", "arrays-dynamic", "linked-lists"],
        chain(
            ("1,2,4,7,11,15", "target 15", "Start", "i at 1, j at 15."),
            ("1+15=16", "too big", "Move j", "Sum exceeds target; 15 cannot pair with anything, j moves left.", "i=0,j=5"),
            ("1+11=12", "too small", "Move i", "Sum is below target; 1 is too small for any remaining partner.", "j=4"),
            ("2+11=13", "too small", "Move i", "Still small, advance i.", "i=1"),
            ("4+11=15", "found", "Done", "Pair (4, 11) found in O(n).", "i=2"),
        ),
    ),
    topic(
        "sliding-window", "Sliding Window", "searching", "intermediate", "SW",
        "Maintain a window over a contiguous range, expanding and shrinking it while updating state in O(1).",
        "A sliding window is reading a long scroll through a frame: you slide the frame along, adding the line entering and removing the line leaving, instead of rereading the whole frame each time.",
        "The sliding window pattern processes contiguous subarrays or substrings by keeping a window [left, right] and incremental state such as a running sum or a character count. Fixed-size windows add the entering element and remove the leaving one, giving O(n) for problems like maximum sum of k consecutive elements. Variable-size windows expand right until a condition breaks, then shrink left until it holds again, as in longest substring without repeating characters or minimum window containing a set. Each element enters and leaves the window at most once, so total work is O(n) even with an inner while loop. State is typically a sum, a hash map of counts, or a monotonic deque for window max/min. Sliding windows require that shrinking the window moves toward validity, which fails with negative numbers in sum constraints; then prefix sums with a hash map are used instead.",
        ["Maximum or average of every k-length window.", "Longest substring with at most k distinct characters.", "Minimum window substring.", "Rate limiting over a time window."],
        [
            "Fixed window: add right, remove right - k.",
            "Variable window: expand right, shrink left while invalid.",
            "Each index enters and leaves once: O(n).",
            "Track counts with a dict or Counter.",
            "Negative numbers break 'shrink to fix sum' logic.",
        ],
        [
            ex("Fixed window max sum", "basic", "Running sum instead of recomputing.", "python", """
                def max_sum_k(a, k):
                    s = sum(a[:k])
                    best = s
                    for r in range(k, len(a)):
                        s += a[r] - a[r - k]
                        print(f"window {a[r - k + 1:r + 1]} sum={s}")
                        best = max(best, s)
                    return best

                print("best:", max_sum_k([2, 1, 5, 1, 3, 2], 3))
            """),
            ex("Longest substring without repeats", "intermediate", "Variable window with last-seen index.", "python", """
                def longest_unique(s):
                    last, left, best, span = {}, 0, 0, (0, 0)
                    for right, c in enumerate(s):
                        if c in last and last[c] >= left:
                            left = last[c] + 1
                        last[c] = right
                        if right - left + 1 > best:
                            best, span = right - left + 1, (left, right + 1)
                    return best, s[span[0]:span[1]]

                for s in ["abcabcbb", "bbbbb", "pwwkew"]:
                    print(s, "->", longest_unique(s))
            """),
            ex("Minimum window substring", "advanced", "Expand to satisfy, shrink to minimise.", "python", """
                from collections import Counter

                def min_window(s, t):
                    need, missing = Counter(t), len(t)
                    left, best = 0, (0, float("inf"))
                    for right, c in enumerate(s):
                        if need[c] > 0:
                            missing -= 1
                        need[c] -= 1
                        while missing == 0:
                            if right - left < best[1] - best[0]:
                                best = (left, right)
                            need[s[left]] += 1
                            if need[s[left]] > 0:
                                missing += 1
                            left += 1
                    return "" if best[1] == float("inf") else s[best[0]:best[1] + 1]

                print(min_window("ADOBECODEBANC", "ABC"))
            """),
        ],
        ["s += a[r] - a[r - k]", "for right...: while invalid: left += 1", "Counter / dict of counts in window", "deque for window max/min", "Answer length: right - left + 1"],
        ["Negative numbers: shrinking does not reduce the sum reliably.", "Off-by-one in window length (right - left + 1).", "Forgetting to update the answer at the right moment (before or after shrinking)."],
        [
            qa("basic", "When should you consider a sliding window?", "When the problem asks about contiguous subarrays or substrings and the window's validity changes monotonically as you expand or shrink it. Typical phrasing: longest, shortest or count of subarrays meeting a condition."),
            qa("intermediate", "Why is a variable sliding window O(n) despite the nested loop?", "The left pointer only moves forward and never past the right pointer, so across the whole run it moves at most n times. Combined with n moves of the right pointer, the total is O(n)."),
            qa("intermediate", "How do you find the longest substring without repeating characters?", "Keep a map of each character's last index and a left boundary. When the current character was seen at or after left, move left to one past that index. The answer is the maximum of right - left + 1, in O(n) time."),
            qa("advanced", "Why does the sliding window fail for subarray sum equals k with negatives?", "With negative numbers, shrinking the window can increase the sum and expanding can decrease it, so there is no monotonic rule for which pointer to move. Use prefix sums with a hash map counting earlier prefix values instead."),
        ],
        ["two-pointers", "prefix-sums", "queues-deques", "hash-tables"],
        chain(
            ("[2,1,5,1,3,2]", "k = 3", "Start", "First window [2,1,5] has sum 8."),
            ("slide", "+1 -2", "Move right", "Add 1 and drop 2: window [1,5,1] sum 7.", "sum=8"),
            ("slide", "+3 -1", "Move right", "Window [5,1,3] sum 9, the new best.", "sum=7"),
            ("slide", "+2 -5", "Move right", "Window [1,3,2] sum 6.", "sum=9"),
            ("best = 9", "O(n)", "Done", "Each element was added once and removed once.", "max"),
        ),
    ),
    topic(
        "prefix-sums", "Prefix Sums & Difference Arrays", "searching", "basic", "PS",
        "Precompute running totals so any range sum is one subtraction.",
        "A prefix sum is the odometer in a car: to know how far you drove between two towns, subtract the reading at the first town from the reading at the second.",
        "A prefix sum array P has P[0] = 0 and P[i+1] = P[i] + a[i], so the sum of a[l..r] equals P[r+1] - P[l] in O(1) after O(n) preprocessing. In Python, itertools.accumulate builds it in one line. 2-D prefix sums use inclusion-exclusion to answer rectangle sums in O(1). Combining prefix sums with a hash map counts subarrays with sum k in O(n): for each prefix s, add the number of earlier prefixes equal to s - k; this works even with negative numbers. Difference arrays are the inverse idea: to add v to a range [l, r] in O(1), do d[l] += v and d[r+1] -= v, then take a prefix sum at the end. The same idea generalises to prefix XOR, prefix counts and modular prefix sums for divisibility problems. For ranges with updates interleaved with queries, use a Fenwick or segment tree.",
        ["Range sum queries on static arrays.", "Counting subarrays with a given sum or divisibility.", "Batch range updates with difference arrays (booking, flights).", "Image integral tables (2-D prefix sums)."],
        [
            "P[i+1] = P[i] + a[i]; sum(l..r) = P[r+1] - P[l].",
            "Subarray sum k: count prefix values with a hash map.",
            "Difference array: d[l] += v; d[r+1] -= v.",
            "2-D: S = P[r2][c2] - P[r1][c2] - P[r2][c1] + P[r1][c1].",
            "Updates plus queries need a Fenwick or segment tree.",
        ],
        [
            ex("Range sums", "basic", "Build with accumulate and answer queries in O(1).", "python", """
                from itertools import accumulate

                a = [3, 1, 4, 1, 5, 9, 2, 6]
                P = [0] + list(accumulate(a))
                print("prefix:", P)
                for l, r in [(0, 3), (2, 5), (4, 7)]:
                    print(f"sum a[{l}..{r}] = {P[r + 1] - P[l]} check {sum(a[l:r + 1])}")
            """),
            ex("Subarray sum equals k", "intermediate", "Prefix sums with a counting map; works with negatives.", "python", """
                from collections import defaultdict

                def count_subarrays(nums, k):
                    seen = defaultdict(int)
                    seen[0] = 1
                    s = count = 0
                    for x in nums:
                        s += x
                        count += seen[s - k]
                        seen[s] += 1
                    return count

                print(count_subarrays([1, 1, 1], 2))
                print(count_subarrays([3, 4, -7, 1, 3, 3, 1, -4], 7))
            """),
            ex("Difference array range updates", "intermediate", "Apply many range increments in O(n + q).", "python", """
                from itertools import accumulate

                n = 6
                updates = [(1, 3, 10), (2, 5, 5), (0, 1, 2)]
                d = [0] * (n + 1)
                for l, r, v in updates:
                    d[l] += v
                    d[r + 1] -= v
                print("diff:", d)
                print("result:", list(accumulate(d))[:n])
            """),
        ],
        ["P = [0] + list(itertools.accumulate(a))", "sum(l..r) = P[r+1] - P[l]", "count += seen[s - k]; seen[s] += 1", "d[l] += v; d[r+1] -= v", "Prefix XOR: x(l..r) = X[r+1] ^ X[l]"],
        ["Off-by-one: use a leading 0 so P has n+1 entries.", "Forgetting seen[0] = 1 misses subarrays starting at index 0.", "Prefix sums of floats accumulate rounding error."],
        [
            qa("basic", "How do prefix sums answer range sum queries in O(1)?", "Precompute P where P[i] is the sum of the first i elements. The sum of a[l..r] is P[r+1] - P[l], a single subtraction, after O(n) preprocessing."),
            qa("intermediate", "How do you count subarrays summing to k in O(n)?", "Iterate while keeping the running prefix sum s and a hash map of how many times each prefix value has occurred, initialised with {0: 1}. A subarray ending here sums to k exactly when an earlier prefix equals s - k, so add that count. It works with negative numbers."),
            qa("intermediate", "What is a difference array?", "An array d where d[i] = a[i] - a[i-1]. Adding v to the range [l, r] becomes d[l] += v and d[r+1] -= v, both O(1). After all updates, a prefix sum over d reconstructs the final array."),
            qa("advanced", "When are prefix sums not enough?", "When updates and queries interleave: a single point update would require O(n) to rebuild the prefix array. A Fenwick tree or segment tree supports both in O(log n)."),
        ],
        ["sliding-window", "segment-fenwick", "hash-tables", "dynamic-programming"],
        chain(
            ("[3,1,4,1,5]", "input", "Start", "We want many range sums quickly."),
            ("P", "[0,3,4,8,9,14]", "Build", "Running totals with a leading zero: O(n).", "accumulate"),
            ("query 1..3", "P[4]-P[1]", "Answer", "9 - 3 = 6, which is 1 + 4 + 1.", "l, r"),
            ("O(1) each", "q queries", "Cost", "Total O(n + q) instead of O(n * q).", "6"),
        ),
    ),
]

TOPICS += [
    topic(
        "binary-trees", "Binary Trees & Traversals", "trees", "basic", "BT",
        "Each node has at most two children; visit them pre-order, in-order, post-order or level by level.",
        "A binary tree is a family tree where everyone has at most two children. Traversals are different ways to call the whole family: parents before kids, kids before parents, or generation by generation.",
        "A binary tree consists of nodes with a value and left and right child pointers; the top node is the root and nodes without children are leaves. Depth-first traversals visit the root before its subtrees (pre-order), between them (in-order) or after them (post-order); breadth-first or level-order traversal uses a queue to visit nodes level by level. Every traversal is O(n) time; recursive DFS uses O(h) stack space where h is the height, which ranges from log n for balanced trees to n for skewed ones. Many tree problems reduce to a post-order computation where each node combines answers from its children, such as height, diameter, balanced check and maximum path sum. Pre-order is used to copy or serialise trees, in-order yields sorted order in a BST, and post-order is used to delete or evaluate expression trees. Complete binary trees can be stored in arrays with children at 2i+1 and 2i+2, which is how heaps work.",
        ["Expression trees and syntax trees in compilers.", "Hierarchical data like file systems and DOM (generalised trees).", "Serialising and deserialising structures.", "Foundation for BSTs, heaps and segment trees."],
        [
            "Pre-order: node, left, right. In-order: left, node, right. Post-order: left, right, node.",
            "Level-order uses a queue (BFS).",
            "Traversals are O(n) time and O(h) stack space.",
            "Height of a balanced tree is O(log n); of a skewed tree O(n).",
            "Post-order 'combine children' solves height, diameter and path sums.",
        ],
        [
            ex("Four traversals", "basic", "Recursive DFS orders plus BFS level order.", "python", """
                from collections import deque

                class Node:
                    def __init__(self, v, l=None, r=None):
                        self.v, self.l, self.r = v, l, r

                #        1
                #      2   3
                #     4 5   6
                root = Node(1, Node(2, Node(4), Node(5)), Node(3, None, Node(6)))

                def pre(n):  return [n.v] + pre(n.l) + pre(n.r) if n else []
                def ino(n):  return ino(n.l) + [n.v] + ino(n.r) if n else []
                def post(n): return post(n.l) + post(n.r) + [n.v] if n else []

                def levels(n):
                    out, q = [], deque([n])
                    while q:
                        out.append([x.v for x in q])
                        q = deque(c for x in q for c in (x.l, x.r) if c)
                    return out

                print("pre  ", pre(root))
                print("in   ", ino(root))
                print("post ", post(root))
                print("level", levels(root))
            """),
            ex("Height and diameter", "intermediate", "Post-order combination of child results.", "python", """
                class Node:
                    def __init__(self, v, l=None, r=None):
                        self.v, self.l, self.r = v, l, r

                root = Node(1, Node(2, Node(4, Node(7)), Node(5)), Node(3))

                def diameter(root):
                    best = 0
                    def height(n):
                        nonlocal best
                        if not n:
                            return 0
                        lh, rh = height(n.l), height(n.r)
                        best = max(best, lh + rh)
                        return 1 + max(lh, rh)
                    h = height(root)
                    return h, best

                h, d = diameter(root)
                print("height:", h, "diameter (edges):", d)
            """),
            ex("Iterative in-order", "intermediate", "Explicit stack instead of recursion.", "python", """
                class Node:
                    def __init__(self, v, l=None, r=None):
                        self.v, self.l, self.r = v, l, r

                root = Node(4, Node(2, Node(1), Node(3)), Node(6, Node(5), Node(7)))

                def inorder_iter(n):
                    out, stack = [], []
                    while stack or n:
                        while n:
                            stack.append(n)
                            n = n.l
                        n = stack.pop()
                        out.append(n.v)
                        n = n.r
                    return out

                print(inorder_iter(root))
            """),
        ],
        ["pre: N L R · in: L N R · post: L R N", "Level order: deque([root])", "height(n) = 1 + max(height(l), height(r))", "Array tree: children 2i+1, 2i+2", "DFS space O(h), BFS space O(width)"],
        ["Deep skewed trees can exceed Python's recursion limit.", "Diameter counts edges or nodes; clarify which.", "Forgetting the None base case causes AttributeError."],
        [
            qa("basic", "What are the three depth-first traversals?", "Pre-order visits node, left, right; in-order visits left, node, right; post-order visits left, right, node. All take O(n) time and O(h) space for the recursion stack."),
            qa("basic", "How do you do a level-order traversal?", "Push the root into a queue; repeatedly pop a node, record it and push its children. To group by level, process exactly len(queue) nodes per iteration. O(n) time and O(w) space where w is the maximum width."),
            qa("intermediate", "How do you compute the diameter of a binary tree?", "Do a post-order traversal returning each node's height; at each node, the longest path through it is left height + right height. Track the maximum over all nodes. It runs in O(n) because each node is visited once."),
            qa("intermediate", "Can you reconstruct a tree from traversals?", "Pre-order plus in-order (or post-order plus in-order) uniquely determine a tree with distinct values: the pre-order's first element is the root, and its position in in-order splits left and right subtrees. Pre-order plus post-order alone is ambiguous for nodes with one child."),
        ],
        ["bst", "bfs", "dfs", "recursion"],
        chain(
            ("root 1", "children 2,3", "Tree", "Tree: 1 has children 2 and 3; 2 has children 4 and 5."),
            ("pre-order", "1,2,4,5,3", "Node first", "Visit the node, then its left subtree, then its right.", "N L R"),
            ("in-order", "4,2,5,1,3", "Node middle", "Left subtree, node, right subtree.", "L N R"),
            ("post-order", "4,5,2,3,1", "Node last", "Both subtrees before the node, useful for combining results.", "L R N"),
            ("level-order", "1 | 2,3 | 4,5", "By depth", "A queue visits nodes generation by generation.", "queue"),
        ),
    ),
    topic(
        "bst", "Binary Search Trees", "trees", "intermediate", "BX",
        "Left subtree smaller, right subtree larger: search, insert and delete in O(h).",
        "A BST is a choose-your-own-adventure book for numbers: at each page you go left if your number is smaller and right if it is bigger, until you find it or run out of pages.",
        "A binary search tree maintains the invariant that every key in a node's left subtree is less than the node's key and every key in its right subtree is greater. Search, insert and delete follow a single root-to-leaf path, costing O(h) where h is the height. With random insertion order h is O(log n) on average, but inserting sorted data produces a linked-list-shaped tree with h = n, so operations degrade to O(n). In-order traversal of a BST yields keys in sorted order, which also enables k-th smallest and range queries. Deletion has three cases: a leaf is removed, a node with one child is replaced by that child, and a node with two children is replaced by its in-order successor (minimum of the right subtree), which is then deleted. Validating a BST requires passing down lower and upper bounds, not just comparing each node with its children. Self-balancing variants such as AVL and red-black trees guarantee O(log n).",
        ["Ordered maps and sets (TreeMap, std::map).", "Range queries and floor/ceiling lookups.", "Maintaining a dynamic sorted collection.", "Database index concepts (generalised as B-trees)."],
        [
            "Search/insert/delete O(h): O(log n) balanced, O(n) skewed.",
            "In-order traversal gives sorted keys.",
            "Delete with two children: replace with in-order successor.",
            "Validate using (low, high) bounds passed down.",
            "Python has no built-in BST; use bisect on a list or sortedcontainers.",
        ],
        [
            ex("Insert, search and in-order", "basic", "Build a BST and show the search path.", "python", """
                class Node:
                    def __init__(self, k):
                        self.k, self.l, self.r = k, None, None

                def insert(n, k):
                    if not n:
                        return Node(k)
                    if k < n.k:
                        n.l = insert(n.l, k)
                    elif k > n.k:
                        n.r = insert(n.r, k)
                    return n

                def search(n, k):
                    path = []
                    while n:
                        path.append(n.k)
                        if k == n.k:
                            return True, path
                        n = n.l if k < n.k else n.r
                    return False, path

                def inorder(n):
                    return inorder(n.l) + [n.k] + inorder(n.r) if n else []

                root = None
                for k in [50, 30, 70, 20, 40, 60, 80]:
                    root = insert(root, k)
                print("sorted:", inorder(root))
                print("search 60:", search(root, 60))
                print("search 65:", search(root, 65))
            """),
            ex("Delete with three cases", "intermediate", "Leaf, one child, two children.", "python", """
                class Node:
                    def __init__(self, k):
                        self.k, self.l, self.r = k, None, None

                def insert(n, k):
                    if not n: return Node(k)
                    if k < n.k: n.l = insert(n.l, k)
                    else: n.r = insert(n.r, k)
                    return n

                def delete(n, k):
                    if not n:
                        return None
                    if k < n.k:
                        n.l = delete(n.l, k)
                    elif k > n.k:
                        n.r = delete(n.r, k)
                    else:
                        if not n.l: return n.r
                        if not n.r: return n.l
                        s = n.r
                        while s.l:
                            s = s.l
                        n.k = s.k
                        n.r = delete(n.r, s.k)
                    return n

                def inorder(n):
                    return inorder(n.l) + [n.k] + inorder(n.r) if n else []

                root = None
                for k in [50, 30, 70, 20, 40, 60, 80]:
                    root = insert(root, k)
                for k in [20, 30, 50]:
                    root = delete(root, k)
                    print(f"delete {k}: {inorder(root)} root={root.k}")
            """),
            ex("Validate BST and skew", "intermediate", "Bounds-based validation and height on sorted inserts.", "python", """
                class Node:
                    def __init__(self, k, l=None, r=None):
                        self.k, self.l, self.r = k, l, r

                def valid(n, lo=float("-inf"), hi=float("inf")):
                    if not n:
                        return True
                    if not lo < n.k < hi:
                        return False
                    return valid(n.l, lo, n.k) and valid(n.r, n.k, hi)

                good = Node(5, Node(3, Node(2), Node(4)), Node(8))
                tricky = Node(5, Node(3, Node(2), Node(6)), Node(8))
                print("good:", valid(good), "tricky (6 in left subtree):", valid(tricky))

                def height_after(keys):
                    root, h = None, 0
                    for k in keys:
                        depth, parent, n = 1, None, root
                        while n:
                            parent, n, depth = n, (n.l if k < n.k else n.r), depth + 1
                        node = Node(k)
                        if not parent: root = node
                        elif k < parent.k: parent.l = node
                        else: parent.r = node
                        h = max(h, depth)
                    return h

                print("height sorted 1..31:", height_after(range(1, 32)))
                print("height balanced order:", height_after([16, 8, 24, 4, 12, 20, 28, 2, 6, 10, 14, 18, 22, 26, 30]))
            """),
        ],
        ["search/insert/delete O(h)", "Balanced h = O(log n); skewed h = n", "Successor = min of right subtree", "valid(n, lo, hi) with bounds", "bisect + list as a simple sorted set"],
        ["Comparing only with direct children does not validate a BST.", "Sorted inserts create a degenerate O(n) tree.", "Decide how duplicates are handled (reject, count, or go right)."],
        [
            qa("basic", "What is the BST property?", "For every node, all keys in the left subtree are smaller and all keys in the right subtree are larger. This allows search to discard one subtree at each step."),
            qa("intermediate", "What is the complexity of BST operations?", "O(h) for search, insert and delete, where h is the height. That is O(log n) for balanced trees and O(n) for degenerate trees, such as one built from sorted input."),
            qa("intermediate", "How do you delete a node with two children?", "Find its in-order successor (leftmost node of the right subtree) or predecessor, copy that key into the node, then delete the successor from the right subtree. The successor has at most one child, so that deletion is a simple case."),
            qa("intermediate", "How do you validate a BST?", "Recurse with an allowed range (lo, hi): each node must satisfy lo < key < hi, the left child gets (lo, key) and the right gets (key, hi). Alternatively check that an in-order traversal is strictly increasing. Comparing only parent and children misses violations deeper in the tree."),
            qa("advanced", "How do you find the k-th smallest element?", "Do an in-order traversal and stop at the k-th visited node, O(h + k). If you augment each node with its subtree size, you can descend directly in O(h) by comparing k with the left subtree size."),
        ],
        ["binary-trees", "balanced-trees", "binary-search"],
        chain(
            ("search 60", "root 50", "Start", "Compare 60 with the root 50."),
            ("60 > 50", "go right", "Right", "Move to the right child 70.", "50"),
            ("60 < 70", "go left", "Left", "Move to the left child of 70, which is 60.", "70"),
            ("60 == 60", "found", "Hit", "Found after 3 comparisons, one per level.", "60"),
            ("O(h)", "log n if balanced", "Cost", "A sorted insertion order would have made h = n.", "h"),
        ),
    ),
    topic(
        "balanced-trees", "Balanced Trees: AVL & Red-Black", "trees", "advanced", "AV",
        "Self-balancing BSTs use rotations to keep height O(log n) under any insertion order.",
        "A balanced tree is a mobile hanging from the ceiling: whenever one side gets too heavy, you shift a joint so the whole thing hangs level again.",
        "Self-balancing BSTs restore balance after insertions and deletions so the height stays O(log n), guaranteeing O(log n) search, insert and delete. AVL trees store each node's height and require the balance factor (left height minus right height) to be -1, 0 or 1; violations are fixed with single rotations (LL, RR) or double rotations (LR, RL). AVL trees are more strictly balanced (height at most about 1.44 log n), making lookups slightly faster. Red-black trees colour nodes red or black with rules: the root is black, red nodes have black children, and every root-to-leaf path has the same number of black nodes. This guarantees height at most 2 log(n+1) and needs fewer rotations on updates, so red-black trees back Java's TreeMap, C++ std::map and the Linux scheduler. B-trees generalise balancing to many keys per node for disk-based databases. A rotation is O(1) and preserves the in-order sequence.",
        ["Ordered maps and sets in standard libraries.", "Interval and order-statistic trees built on top.", "Kernel schedulers and memory managers.", "Database indexes (B-trees and B+ trees)."],
        [
            "Height O(log n) guaranteed: all operations O(log n).",
            "AVL: balance factor in {-1, 0, 1}; stricter, faster lookups.",
            "Red-black: colour rules; height <= 2 log(n+1); fewer rotations.",
            "Rotations are O(1) and preserve in-order order.",
            "Cases: LL -> right rotate, RR -> left rotate, LR/RL -> double rotation.",
        ],
        [
            ex("AVL insertion with rotations", "advanced", "Insert sorted keys and stay balanced.", "python", """
                class N:
                    def __init__(self, k):
                        self.k, self.l, self.r, self.h = k, None, None, 1

                def h(n): return n.h if n else 0
                def fix(n): n.h = 1 + max(h(n.l), h(n.r))
                def bal(n): return h(n.l) - h(n.r)

                def rot_right(y):
                    x = y.l
                    y.l, x.r = x.r, y
                    fix(y); fix(x)
                    return x

                def rot_left(x):
                    y = x.r
                    x.r, y.l = y.l, x
                    fix(x); fix(y)
                    return y

                def insert(n, k):
                    if not n:
                        return N(k)
                    if k < n.k: n.l = insert(n.l, k)
                    else: n.r = insert(n.r, k)
                    fix(n)
                    b = bal(n)
                    if b > 1 and k < n.l.k: return rot_right(n)
                    if b < -1 and k > n.r.k: return rot_left(n)
                    if b > 1:
                        n.l = rot_left(n.l); return rot_right(n)
                    if b < -1:
                        n.r = rot_right(n.r); return rot_left(n)
                    return n

                def inorder(n): return inorder(n.l) + [n.k] + inorder(n.r) if n else []

                root = None
                for k in range(1, 16):
                    root = insert(root, k)
                print("root:", root.k, "height:", root.h, "(plain BST would be 15)")
                print(inorder(root))
            """),
            ex("Rotation preserves order", "intermediate", "Right rotation on a left-left chain.", "python", """
                class N:
                    def __init__(self, k, l=None, r=None):
                        self.k, self.l, self.r = k, l, r

                def show(n):
                    return f"({show(n.l)} {n.k} {show(n.r)})" if n else "."

                def rot_right(y):
                    x = y.l
                    y.l, x.r = x.r, y
                    return x

                chain = N(30, N(20, N(10)))
                print("before:", show(chain))
                print("after: ", show(rot_right(chain)))
            """),
        ],
        ["AVL: |h(l) - h(r)| <= 1", "RB height <= 2 log2(n + 1)", "LL: rotate right · RR: rotate left", "LR: left(child) then right · RL: right(child) then left", "Java TreeMap / C++ std::map = red-black"],
        ["Forgetting to update heights after a rotation corrupts balance factors.", "Python has no built-in balanced BST; use sortedcontainers or bisect for practice.", "Red-black deletion has many cases; interviews rarely require coding it."],
        [
            qa("intermediate", "Why do we need balanced BSTs?", "A plain BST can degenerate into a linked list with height n under sorted insertions, making operations O(n). Balanced trees rebalance with rotations so the height stays O(log n) for any operation sequence."),
            qa("advanced", "Compare AVL and red-black trees.", "AVL trees are more rigidly balanced (height about 1.44 log n), so lookups are slightly faster, but inserts and deletes may need more rotations. Red-black trees allow height up to 2 log n but need at most two rotations per insert and three per delete, so they are preferred for write-heavy workloads and in standard libraries."),
            qa("advanced", "What are the red-black tree invariants?", "Every node is red or black, the root is black, null leaves are black, a red node cannot have a red child, and every path from a node to its descendant leaves has the same number of black nodes. Together these bound the height to 2 log(n+1)."),
            qa("intermediate", "What does a rotation do?", "It restructures a parent and child in O(1) by changing three pointers, raising one subtree and lowering another while preserving the in-order key order. Single rotations fix outside cases (LL, RR) and double rotations fix inside cases (LR, RL)."),
        ],
        ["bst", "binary-trees", "heaps"],
        chain(
            ("insert 10,20", "right child", "Start", "10 is root and 20 is its right child."),
            ("insert 30", "bal(10) = -2", "Imbalance", "The right-right chain 10-20-30 violates AVL balance.", "30"),
            ("rotate left", "at 10", "Fix RR", "20 becomes the root with 10 left and 30 right.", "RR"),
            ("height 2", "balanced", "Result", "In-order order 10, 20, 30 is unchanged; height stays O(log n).", "done"),
        ),
    ),
    topic(
        "heaps", "Heaps & Priority Queues", "trees", "intermediate", "HP",
        "A complete binary tree where each parent beats its children: O(1) peek, O(log n) push and pop.",
        "A heap is a company org chart where every manager outranks their direct reports. The CEO at the top is always the most senior, and when the CEO leaves, someone is promoted up the chain in a few steps.",
        "A binary min-heap is a complete binary tree stored in an array where every parent is less than or equal to its children, so the minimum sits at index 0. push appends at the end and sifts up, and pop swaps the root with the last element, removes it and sifts down; both are O(log n), and peek is O(1). heapify builds a heap from an arbitrary list in O(n). Python's heapq module implements a min-heap on plain lists; for a max-heap, push negated keys, and for complex items push tuples (priority, counter, item) so ties never compare the items. Priority queues built on heaps power Dijkstra, Prim, event simulation, scheduling, merging k sorted lists and streaming top-k. Two heaps (a max-heap of the lower half and a min-heap of the upper half) maintain a running median. Heaps do not support efficient search for arbitrary elements; decrease-key is usually done by lazy deletion.",
        ["Task scheduling by priority or deadline.", "Dijkstra and Prim algorithms.", "Top-k and k-way merge of sorted streams.", "Running median with two heaps."],
        [
            "peek O(1), push/pop O(log n), heapify O(n).",
            "Array layout: children 2i+1, 2i+2; parent (i-1)//2.",
            "heapq is a min-heap; negate for max-heap.",
            "Use (priority, counter, item) to break ties safely.",
            "Lazy deletion instead of decrease-key.",
        ],
        [
            ex("heapq essentials", "basic", "push, pop, heapify, max-heap via negation.", "python", """
                import heapq

                h = []
                for x in [5, 1, 8, 3, 2]:
                    heapq.heappush(h, x)
                    print("push", x, "->", h)
                print("pop order:", [heapq.heappop(h) for _ in range(len(h))])

                maxh = [-x for x in [5, 1, 8, 3]]
                heapq.heapify(maxh)
                print("max:", -maxh[0])

                tasks = []
                for i, (pri, name) in enumerate([(2, "write"), (1, "fix"), (2, "deploy")]):
                    heapq.heappush(tasks, (pri, i, name))
                print([heapq.heappop(tasks)[2] for _ in range(3)])
            """),
            ex("Merge k sorted lists", "intermediate", "Heap holds the current head of each list.", "python", """
                import heapq

                def merge_k(lists):
                    h = [(lst[0], i, 0) for i, lst in enumerate(lists) if lst]
                    heapq.heapify(h)
                    out = []
                    while h:
                        val, i, j = heapq.heappop(h)
                        out.append(val)
                        if j + 1 < len(lists[i]):
                            heapq.heappush(h, (lists[i][j + 1], i, j + 1))
                    return out

                print(merge_k([[1, 4, 7], [2, 5, 8], [0, 3, 6, 9]]))
            """),
            ex("Running median with two heaps", "advanced", "Max-heap low half, min-heap high half.", "python", """
                import heapq

                low, high = [], []
                def add(x):
                    heapq.heappush(low, -x)
                    heapq.heappush(high, -heapq.heappop(low))
                    if len(high) > len(low):
                        heapq.heappush(low, -heapq.heappop(high))

                def median():
                    if len(low) > len(high):
                        return -low[0]
                    return (-low[0] + high[0]) / 2

                for x in [5, 15, 1, 3, 8, 7]:
                    add(x)
                    print(f"add {x:2} -> median {median()}")
            """),
        ],
        ["heapq.heappush(h, x) · heapq.heappop(h) O(log n)", "heapq.heapify(lst) O(n) · h[0] peek", "heapq.heappushpop / heapreplace", "heapq.nlargest(k, xs) · nsmallest", "Max-heap: push -x"],
        ["heapq has no max-heap; negate numbers or wrap objects.", "Tuples with equal priorities compare the next field; add a counter.", "A heap list is not sorted; only h[0] is guaranteed minimal."],
        [
            qa("basic", "What are the complexities of heap operations?", "peek is O(1), push and pop are O(log n) because sift-up and sift-down follow one root-to-leaf path, and heapify of n elements is O(n). Searching for an arbitrary element is O(n)."),
            qa("intermediate", "How do you implement a max-heap with heapq?", "Push negated keys and negate again when popping, for numeric priorities. For non-numeric keys, wrap items in a class whose __lt__ is reversed, or push (-priority, counter, item)."),
            qa("intermediate", "How do you find the k largest elements of a stream?", "Maintain a min-heap of size k: push each element and pop when the size exceeds k. The heap then holds the k largest seen so far and h[0] is the k-th largest. O(n log k) time and O(k) space."),
            qa("advanced", "How does Dijkstra handle decrease-key with heapq?", "heapq cannot update priorities in place, so Dijkstra pushes a new (distance, node) entry whenever it finds a shorter path and, when popping, skips entries whose distance is greater than the best known. This lazy deletion keeps O((V + E) log V) time."),
        ],
        ["heap-sort", "dijkstra", "quickselect", "queues-deques"],
        chain(
            ("[1,3,8,5]", "min-heap", "Start", "Root 1 is the minimum."),
            ("push 2", "append at end", "Insert", "2 is placed at index 4 under parent 3.", "2"),
            ("sift up", "swap 2,3", "Restore", "2 < 3, swap: heap becomes [1,2,8,5,3]; 2 >= 1 stops.", "up"),
            ("pop", "return 1", "Extract", "Move last element 3 to the root and remove 1.", "min"),
            ("sift down", "[2,3,8,5]", "Restore", "3 swaps with the smaller child 2; heap order holds again.", "down"),
        ),
    ),
    topic(
        "tries", "Tries (Prefix Trees)", "trees", "intermediate", "TR",
        "A tree of characters where each path spells a prefix: lookups cost O(length of word).",
        "A trie is like a phone's predictive keyboard: after you type 'ca', it already knows every word branching from that point, 'cat', 'car', 'cave', without scanning a dictionary.",
        "A trie stores strings as paths from the root, one character per edge, with a flag marking nodes where a word ends. Insert and search take O(L) for a word of length L, independent of how many words are stored. startsWith(prefix) checks whether a path exists, which makes tries ideal for autocomplete, spell checking and prefix counting. Each node holds a map from character to child (a dict in Python, or a 26-slot array for lowercase letters); memory can be large because many nodes have few children. Compressed tries (radix trees) merge single-child chains to save space, as used in routing tables. Tries also solve word search on grids by pruning paths that are not prefixes of any word, and binary tries over bits solve maximum XOR pair problems. Storing a count at each node supports counting words with a given prefix.",
        ["Autocomplete and type-ahead search.", "Spell checkers and word games (Boggle, word search).", "IP routing with longest-prefix match.", "Maximum XOR of two numbers using a bitwise trie."],
        [
            "Insert/search/startsWith: O(L) per word.",
            "Node = children map + end-of-word flag.",
            "Memory heavy; compress single-child chains (radix tree).",
            "Prefix counts: store a counter per node.",
            "Prune DFS on grids when no trie child matches.",
        ],
        [
            ex("Trie with insert, search, prefix", "basic", "Dictionary-based children.", "python", """
                class Trie:
                    def __init__(self):
                        self.root = {}

                    def insert(self, word):
                        node = self.root
                        for c in word:
                            node = node.setdefault(c, {})
                        node["$"] = True

                    def _walk(self, s):
                        node = self.root
                        for c in s:
                            if c not in node:
                                return None
                            node = node[c]
                        return node

                    def search(self, word):
                        node = self._walk(word)
                        return bool(node and node.get("$"))

                    def starts_with(self, p):
                        return self._walk(p) is not None

                t = Trie()
                for w in ["car", "cart", "care", "cat", "dog"]:
                    t.insert(w)
                print(t.search("car"), t.search("ca"), t.starts_with("ca"), t.starts_with("cow"))
            """),
            ex("Autocomplete", "intermediate", "Collect all words below a prefix node.", "python", """
                def build(words):
                    root = {}
                    for w in words:
                        node = root
                        for c in w:
                            node = node.setdefault(c, {})
                        node["$"] = w
                    return root

                def complete(root, prefix):
                    node = root
                    for c in prefix:
                        if c not in node:
                            return []
                        node = node[c]
                    out, stack = [], [node]
                    while stack:
                        n = stack.pop()
                        for k, v in n.items():
                            if k == "$":
                                out.append(v)
                            else:
                                stack.append(v)
                    return sorted(out)

                root = build(["apple", "app", "apply", "ape", "banana", "band"])
                print(complete(root, "ap"))
                print(complete(root, "ban"))
            """),
            ex("Maximum XOR pair with a bit trie", "advanced", "Greedily choose the opposite bit.", "python", """
                def max_xor(nums, bits=5):
                    root = {}
                    for x in nums:
                        node = root
                        for b in range(bits - 1, -1, -1):
                            node = node.setdefault((x >> b) & 1, {})
                    best = 0
                    for x in nums:
                        node, cur = root, 0
                        for b in range(bits - 1, -1, -1):
                            bit = (x >> b) & 1
                            if 1 - bit in node:
                                cur |= 1 << b
                                node = node[1 - bit]
                            else:
                                node = node[bit]
                        best = max(best, cur)
                    return best

                nums = [3, 10, 5, 25, 2, 8]
                print(max_xor(nums), max(a ^ b for a in nums for b in nums))
            """),
        ],
        ["Insert/search O(L)", "node = node.setdefault(c, {})", "End marker: node['$'] = True", "Children array: [None] * 26 for a-z", "Space O(total characters)"],
        ["Forgetting the end-of-word flag makes prefixes look like words.", "Deleting requires pruning empty nodes bottom-up.", "Memory use can exceed a hash set for small dictionaries."],
        [
            qa("basic", "What is a trie and what is it good for?", "A tree where each edge is a character and each root-to-node path is a prefix, with flags for complete words. It gives O(L) insert and lookup and makes prefix queries like autocomplete natural."),
            qa("intermediate", "Trie vs hash set for storing words?", "A hash set gives O(L) average lookups too (hashing the string) and uses less memory, but cannot answer prefix queries efficiently. A trie supports startsWith, prefix counts, lexicographic iteration and early pruning in searches."),
            qa("intermediate", "How do tries speed up word search in a grid?", "Insert all target words into a trie, then DFS from each cell while walking the trie in parallel. As soon as the current path is not a trie prefix, the DFS stops, avoiding exploring paths that cannot form any word."),
            qa("advanced", "What is a radix (compressed) trie?", "A trie where chains of single-child nodes are merged into one edge labelled with a string. It reduces node count and memory, and is used in IP routing tables and some key-value stores."),
        ],
        ["hash-tables", "strings", "backtracking", "bit-manipulation"],
        chain(
            ("insert car", "c -> a -> r", "Build", "Create nodes c, a, r and mark r as a word end."),
            ("insert cat", "share c -> a", "Share prefix", "Reuse c and a; add a new child t.", "cat"),
            ("search ca", "path exists", "Lookup", "The path c-a exists but a has no end flag, so 'ca' is a prefix, not a word.", "ca"),
            ("startsWith", "O(L)", "Prefix query", "Any existing path means some word starts with that prefix.", "prefix"),
        ),
    ),
    topic(
        "union-find", "Union-Find (Disjoint Set Union)", "trees", "intermediate", "UF",
        "Track which elements are connected with near-constant-time union and find.",
        "Union-find is a set of clubs where each member knows someone closer to the club president. To see if two people are in the same club, follow the chain to each president and compare.",
        "Union-find maintains a partition of elements into disjoint sets, represented as a forest where each node points to a parent and each root is its set's representative. find(x) follows parent pointers to the root; union(a, b) links one root under the other. Path compression makes every node visited by find point directly to the root, and union by rank or size attaches the smaller tree under the larger. Together they give amortised O(alpha(n)) per operation, where alpha is the inverse Ackermann function, effectively constant. Union-find answers connectivity queries incrementally, detects cycles in undirected graphs (an edge whose endpoints already share a root closes a cycle), and is the core of Kruskal's MST algorithm. It counts connected components and groups equivalent items such as accounts sharing emails. It does not support efficient splitting (deleting edges).",
        ["Kruskal's minimum spanning tree.", "Cycle detection in undirected graphs.", "Counting connected components or islands dynamically.", "Merging equivalent records (accounts, synonyms)."],
        [
            "find with path compression; union by rank/size.",
            "Amortised O(alpha(n)), effectively O(1).",
            "Cycle if find(u) == find(v) before union.",
            "Components = number of distinct roots.",
            "No efficient deletion or splitting.",
        ],
        [
            ex("DSU with path compression and union by size", "basic", "Connect pairs and count components.", "python", """
                class DSU:
                    def __init__(self, n):
                        self.parent = list(range(n))
                        self.size = [1] * n
                        self.count = n

                    def find(self, x):
                        while self.parent[x] != x:
                            self.parent[x] = self.parent[self.parent[x]]
                            x = self.parent[x]
                        return x

                    def union(self, a, b):
                        ra, rb = self.find(a), self.find(b)
                        if ra == rb:
                            return False
                        if self.size[ra] < self.size[rb]:
                            ra, rb = rb, ra
                        self.parent[rb] = ra
                        self.size[ra] += self.size[rb]
                        self.count -= 1
                        return True

                d = DSU(7)
                for a, b in [(0, 1), (1, 2), (3, 4), (5, 6), (4, 6)]:
                    d.union(a, b)
                    print(f"union({a},{b}) components={d.count}")
                print("0~2:", d.find(0) == d.find(2), "2~3:", d.find(2) == d.find(3))
            """),
            ex("Cycle detection in an undirected graph", "intermediate", "An edge inside one set closes a cycle.", "python", """
                def has_cycle(n, edges):
                    parent = list(range(n))
                    def find(x):
                        while parent[x] != x:
                            parent[x] = parent[parent[x]]
                            x = parent[x]
                        return x
                    for u, v in edges:
                        ru, rv = find(u), find(v)
                        if ru == rv:
                            return (u, v)
                        parent[ru] = rv
                    return None

                print(has_cycle(4, [(0, 1), (1, 2), (2, 3)]))
                print(has_cycle(4, [(0, 1), (1, 2), (2, 0), (2, 3)]))
            """),
        ],
        ["parent = list(range(n))", "find: parent[x] = parent[parent[x]] (halving)", "union by size/rank", "Amortised O(alpha(n))", "Cycle: find(u) == find(v)"],
        ["Comparing parent[a] == parent[b] instead of find(a) == find(b).", "Recursive find can hit recursion limits on long chains without compression.", "Union-find only works for undirected connectivity, not directed reachability."],
        [
            qa("basic", "What operations does union-find support?", "find(x) returns the representative of x's set, and union(a, b) merges the sets containing a and b. It answers 'are a and b connected?' by comparing find(a) and find(b)."),
            qa("intermediate", "What are path compression and union by rank?", "Path compression makes nodes on a find path point directly (or closer) to the root, flattening the tree. Union by rank or size attaches the shallower or smaller tree under the other root, keeping trees short. Combined they give amortised inverse-Ackermann time per operation."),
            qa("intermediate", "How is union-find used in Kruskal's algorithm?", "Edges are processed in increasing weight; an edge is added to the MST only if its endpoints are in different sets, after which the sets are unioned. This prevents cycles and runs in O(E log E) dominated by sorting."),
            qa("advanced", "When would you choose union-find over BFS/DFS for connectivity?", "When edges arrive incrementally and you need connectivity answers between additions, union-find handles each in near O(1) without recomputing traversals. For a static graph, a single BFS/DFS labelling is equally good, and for edge deletions neither simple approach works well."),
        ],
        ["mst", "graph-representations", "dfs"],
        chain(
            ("{0}{1}{2}{3}", "each own root", "Start", "Every element is its own set."),
            ("union 0,1", "{0,1}", "Merge", "Root of 1 now points to root 0.", "0-1"),
            ("union 2,3", "{2,3}", "Merge", "A second component forms.", "2-3"),
            ("union 1,3", "{0,1,2,3}", "By size", "Roots 0 and 2 differ; attach one under the other.", "1-3"),
            ("find 3", "compress path", "Query", "3 now points straight at the root, making later finds O(1).", "find"),
        ),
    ),
    topic(
        "segment-fenwick", "Segment Trees & Fenwick Trees", "trees", "advanced", "SF",
        "Answer range queries and apply point updates in O(log n) each.",
        "A segment tree is a tournament bracket of subtotals: change one player's score and only the matches on their path to the final need rescoring, and any range is covered by a handful of bracket nodes.",
        "When an array receives both updates and range queries, prefix sums fail because each update costs O(n). A segment tree stores aggregates (sum, min, max, gcd) for segments in a binary tree: the root covers the whole array and each node splits its range in half. Point updates change O(log n) nodes on one path, and a range query combines O(log n) nodes that exactly cover the range. With lazy propagation, segment trees also support range updates in O(log n). A Fenwick tree (binary indexed tree) is a compact array-based structure for prefix sums: index i stores the sum of a block whose size is the lowest set bit of i, and both update and prefix query loop in O(log n) using i & -i. Fenwick trees use n+1 integers and are shorter to code but naturally support only invertible operations like sums; segment trees handle any associative operation. Building either takes O(n) or O(n log n).",
        ["Range sum or range minimum queries with updates.", "Counting inversions or rank queries with a Fenwick tree.", "Interval scheduling and calendar booking with lazy propagation.", "Competitive programming range problems."],
        [
            "Both: O(log n) update and query.",
            "Segment tree: any associative operation, 2n-4n memory.",
            "Fenwick: prefix sums with i & -i, n+1 memory.",
            "Range sum via Fenwick: prefix(r) - prefix(l-1).",
            "Lazy propagation enables O(log n) range updates.",
        ],
        [
            ex("Fenwick tree", "intermediate", "Point update and prefix sum with lowbit.", "python", """
                class Fenwick:
                    def __init__(self, n):
                        self.t = [0] * (n + 1)

                    def update(self, i, delta):
                        i += 1
                        while i < len(self.t):
                            self.t[i] += delta
                            i += i & -i

                    def prefix(self, i):
                        i += 1
                        s = 0
                        while i > 0:
                            s += self.t[i]
                            i -= i & -i
                        return s

                    def range_sum(self, l, r):
                        return self.prefix(r) - (self.prefix(l - 1) if l else 0)

                a = [5, 2, 9, 1, 7, 3]
                fw = Fenwick(len(a))
                for i, x in enumerate(a):
                    fw.update(i, x)
                print("sum[1..4] =", fw.range_sum(1, 4))
                fw.update(2, -9)
                print("after a[2] -= 9, sum[1..4] =", fw.range_sum(1, 4))
            """),
            ex("Iterative segment tree for range min", "advanced", "Bottom-up tree of size 2n.", "python", """
                class SegMin:
                    def __init__(self, a):
                        self.n = len(a)
                        self.t = [float("inf")] * self.n + list(a)
                        for i in range(self.n - 1, 0, -1):
                            self.t[i] = min(self.t[2 * i], self.t[2 * i + 1])

                    def update(self, i, v):
                        i += self.n
                        self.t[i] = v
                        while i > 1:
                            i //= 2
                            self.t[i] = min(self.t[2 * i], self.t[2 * i + 1])

                    def query(self, l, r):
                        res = float("inf")
                        l += self.n
                        r += self.n + 1
                        while l < r:
                            if l & 1:
                                res = min(res, self.t[l]); l += 1
                            if r & 1:
                                r -= 1; res = min(res, self.t[r])
                            l //= 2; r //= 2
                        return res

                st = SegMin([5, 2, 9, 1, 7, 3])
                print("min[0..2] =", st.query(0, 2), "min[2..5] =", st.query(2, 5))
                st.update(3, 10)
                print("after a[3]=10, min[2..5] =", st.query(2, 5))
            """),
            ex("Count inversions with Fenwick", "advanced", "Count earlier elements greater than the current one.", "python", """
                def inversions(a):
                    ranks = {v: i + 1 for i, v in enumerate(sorted(set(a)))}
                    t = [0] * (len(ranks) + 1)
                    inv = 0
                    for seen, x in enumerate(a):
                        i, le = ranks[x], 0
                        while i > 0:
                            le += t[i]; i -= i & -i
                        inv += seen - le
                        i = ranks[x]
                        while i < len(t):
                            t[i] += 1; i += i & -i
                    return inv

                print(inversions([2, 4, 1, 3, 5]), inversions([5, 4, 3, 2, 1]))
            """),
        ],
        ["Fenwick: i += i & -i (update), i -= i & -i (query)", "Range sum = prefix(r) - prefix(l - 1)", "Segment tree: children 2i, 2i+1; leaves at n..2n-1", "Update/query O(log n)", "Lazy propagation for range updates"],
        ["Fenwick trees are 1-indexed internally; off-by-one errors are common.", "Fenwick cannot do range min directly because min is not invertible.", "Recursive segment trees need 4n space to be safe."],
        [
            qa("intermediate", "When do you need a segment or Fenwick tree instead of prefix sums?", "When the array changes between queries. Prefix sums give O(1) queries but O(n) updates; these trees give O(log n) for both, which matters for many interleaved operations."),
            qa("intermediate", "How does a Fenwick tree work?", "Index i stores the sum of the range ending at i with length equal to its lowest set bit (i & -i). A prefix query sums O(log n) such blocks by repeatedly stripping the lowest bit, and an update adds to O(log n) blocks by repeatedly adding the lowest bit."),
            qa("advanced", "Segment tree vs Fenwick tree?", "Fenwick trees are smaller and simpler but best suited to invertible operations like sum and XOR. Segment trees support any associative operation (min, max, gcd), range updates with lazy propagation, and more complex merges, at the cost of more code and memory."),
            qa("advanced", "What is lazy propagation?", "For range updates, a segment tree node covering the whole update range records a pending update tag instead of updating every leaf. Tags are pushed down to children only when a later query or update needs to visit them, keeping range updates at O(log n)."),
        ],
        ["prefix-sums", "binary-trees", "bit-manipulation"],
        chain(
            ("[5,2,9,1]", "leaves", "Build", "Leaves hold elements; parents hold min of children: [2,1], root 1."),
            ("query 0..2", "cover nodes", "Decompose", "Range 0..2 is covered by node [5,2] and leaf 9.", "range"),
            ("combine", "min(2, 9)", "Answer", "Combine the O(log n) covering nodes: result 2.", "nodes"),
            ("update a[1]", "path to root", "Point update", "Set a[1] = 8 and recompute the O(log n) ancestors.", "a[1]"),
            ("re-query", "min(5, 9) = 5", "Fresh answer", "Queries immediately reflect the update.", "root"),
        ),
    ),
    topic(
        "graph-representations", "Graph Representations", "graphs", "basic", "GR",
        "Adjacency lists, adjacency matrices and edge lists each trade memory for query speed.",
        "A graph is a map of cities and roads. An adjacency list is each city's list of direct roads, an adjacency matrix is a mileage chart for every pair of cities, and an edge list is just the list of roads.",
        "A graph G = (V, E) consists of vertices and edges, which may be directed or undirected and weighted or unweighted. An adjacency list stores, for each vertex, its neighbours (and weights); it uses O(V + E) space and iterating a vertex's neighbours costs O(degree), which suits sparse graphs and most algorithms. An adjacency matrix uses O(V^2) space and answers 'is there an edge u-v?' in O(1), which suits dense graphs and algorithms like Floyd-Warshall. An edge list stores (u, v, w) tuples, which is the natural input for Kruskal and Bellman-Ford. Implicit graphs, such as grids where neighbours are computed from coordinates, need no stored structure. In Python, defaultdict(list) is the idiomatic adjacency list. For undirected graphs add both directions; for directed graphs track in-degrees when you need topological order.",
        ["Social networks and recommendation graphs.", "Road maps and routing.", "Dependency graphs for builds and package managers.", "Grids and game boards as implicit graphs."],
        [
            "Adjacency list: O(V + E) space, neighbours in O(degree).",
            "Adjacency matrix: O(V^2) space, edge check O(1).",
            "Edge list: simple, ideal for Kruskal and Bellman-Ford.",
            "Undirected graphs: store each edge twice.",
            "Grids are implicit graphs: neighbours via direction vectors.",
        ],
        [
            ex("Three representations", "basic", "Build each from the same edge list.", "python", """
                from collections import defaultdict

                n = 4
                edges = [(0, 1, 5), (0, 2, 3), (1, 3, 2), (2, 3, 7)]

                adj = defaultdict(list)
                for u, v, w in edges:
                    adj[u].append((v, w))
                    adj[v].append((u, w))
                print("adjacency list:", dict(adj))

                mat = [[0] * n for _ in range(n)]
                for u, v, w in edges:
                    mat[u][v] = mat[v][u] = w
                for row in mat:
                    print(row)
                print("edge 1-2?", mat[1][2] != 0, "| degree of 0:", len(adj[0]))
            """),
            ex("Grid as an implicit graph", "basic", "Neighbours computed from coordinates.", "python", """
                grid = [
                    "..#",
                    ".#.",
                    "...",
                ]
                R, C = len(grid), len(grid[0])

                def neighbours(r, c):
                    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < R and 0 <= nc < C and grid[nr][nc] == ".":
                            yield nr, nc

                print("neighbours of (0,0):", list(neighbours(0, 0)))
                print("neighbours of (2,1):", list(neighbours(2, 1)))
            """),
            ex("In-degree and out-degree", "intermediate", "Directed graph bookkeeping.", "python", """
                from collections import defaultdict

                deps = [("app", "lib"), ("app", "utils"), ("lib", "utils"), ("tests", "app")]
                out_edges, indeg = defaultdict(list), defaultdict(int)
                nodes = set()
                for a, b in deps:
                    out_edges[a].append(b)
                    indeg[b] += 1
                    nodes |= {a, b}
                for v in sorted(nodes):
                    print(f"{v:6} out={len(out_edges[v])} in={indeg[v]}")
            """),
        ],
        ["adj = defaultdict(list); adj[u].append(v)", "Matrix: [[0]*n for _ in range(n)]", "List O(V+E) · Matrix O(V^2)", "Dense: E ~ V^2 · Sparse: E ~ V", "Grid dirs: ((1,0),(-1,0),(0,1),(0,-1))"],
        ["Forgetting the reverse edge in undirected graphs.", "Matrices for sparse graphs with 10^5 nodes exhaust memory.", "Isolated vertices are missing from a defaultdict unless added explicitly."],
        [
            qa("basic", "Adjacency list vs adjacency matrix?", "Lists use O(V + E) space and enumerate neighbours in O(degree), ideal for sparse graphs. Matrices use O(V^2) space but check any edge in O(1), better for dense graphs or when V is small."),
            qa("basic", "How do you represent a weighted graph?", "Store (neighbour, weight) pairs in the adjacency list, put weights in the matrix cells (with infinity or None for no edge), or keep an edge list of (u, v, w) triples."),
            qa("intermediate", "Which representation do BFS and DFS prefer and why?", "Adjacency lists, because the traversal visits each vertex's neighbours once, giving O(V + E). With a matrix each vertex scans a whole row, making traversal O(V^2) regardless of edge count."),
            qa("intermediate", "How do you treat a grid as a graph?", "Each cell is a vertex and edges connect it to valid adjacent cells (4 or 8 directions), computed on the fly from coordinates with bounds and obstacle checks. No explicit structure is stored, and BFS/DFS work unchanged."),
        ],
        ["bfs", "dfs", "dijkstra", "union-find"],
        chain(
            ("edges", "(0,1),(0,2),(1,3)", "Input", "Start from an edge list."),
            ("adj list", "0:[1,2] 1:[0,3]", "Sparse", "Each vertex lists its neighbours: O(V + E) space.", "edges"),
            ("matrix", "4x4 grid of 0/1", "Dense", "Cell [u][v] marks an edge: O(V^2) space, O(1) lookup.", "edges"),
            ("choose", "by density", "Decide", "Use lists for sparse graphs and traversals; matrices for dense graphs or Floyd-Warshall.", "trade-off"),
        ),
    ),
]

TOPICS += [
    topic(
        "bfs", "Breadth-First Search", "graphs", "basic", "BF",
        "Explore a graph level by level with a queue; finds shortest paths in unweighted graphs.",
        "BFS is a ripple spreading from a stone dropped in a pond: everything one step away gets wet first, then everything two steps away, and so on.",
        "Breadth-first search starts from a source, marks it visited and pushes it into a queue; it then repeatedly pops a vertex and pushes all unvisited neighbours, marking them visited when enqueued. Because vertices are discovered in order of distance, BFS gives shortest paths (fewest edges) in unweighted graphs, and recording a parent pointer lets you reconstruct the path. Time is O(V + E) with an adjacency list and space is O(V) for the queue and visited set. Marking nodes visited when enqueuing (not when dequeuing) prevents duplicates in the queue. Multi-source BFS starts with several sources in the queue at distance 0, which solves 'rotting oranges' or 'distance to nearest exit'. 0-1 BFS uses a deque for graphs with edge weights 0 or 1. Bidirectional BFS searches from both ends and can drastically reduce explored nodes.",
        ["Shortest path in unweighted graphs and grids.", "Level-order traversal of trees.", "Multi-source spreading problems (fire, infection, rotting oranges).", "Word ladder and puzzle state searches."],
        [
            "Queue (deque) + visited set; O(V + E).",
            "Mark visited when enqueuing.",
            "First time a node is reached is via a shortest path (unweighted).",
            "Parent map reconstructs the path.",
            "Multi-source BFS: seed all sources at distance 0.",
        ],
        [
            ex("Shortest path with parents", "basic", "BFS on an adjacency list and path reconstruction.", "python", """
                from collections import deque

                graph = {
                    "A": ["B", "C"], "B": ["A", "D", "E"], "C": ["A", "F"],
                    "D": ["B"], "E": ["B", "F"], "F": ["C", "E"],
                }

                def bfs_path(g, s, t):
                    parent, q = {s: None}, deque([s])
                    while q:
                        u = q.popleft()
                        print("visit", u, "queue", list(q))
                        if u == t:
                            break
                        for v in g[u]:
                            if v not in parent:
                                parent[v] = u
                                q.append(v)
                    path, cur = [], t
                    while cur is not None:
                        path.append(cur)
                        cur = parent[cur]
                    return path[::-1]

                print("path:", bfs_path(graph, "A", "F"))
            """),
            ex("Grid shortest path", "intermediate", "Steps from top-left to bottom-right avoiding walls.", "python", """
                from collections import deque

                grid = ["..#.",
                        ".#..",
                        "....",
                        "#.#."]

                def shortest(grid):
                    R, C = len(grid), len(grid[0])
                    dist = {(0, 0): 0}
                    q = deque([(0, 0)])
                    while q:
                        r, c = q.popleft()
                        if (r, c) == (R - 1, C - 1):
                            return dist[(r, c)]
                        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < R and 0 <= nc < C and grid[nr][nc] == "." and (nr, nc) not in dist:
                                dist[(nr, nc)] = dist[(r, c)] + 1
                                q.append((nr, nc))
                    return -1

                print("steps:", shortest(grid))
            """),
            ex("Multi-source BFS: rotting oranges", "intermediate", "All rotten oranges spread simultaneously.", "python", """
                from collections import deque

                def minutes(grid):
                    R, C = len(grid), len(grid[0])
                    q = deque((r, c) for r in range(R) for c in range(C) if grid[r][c] == 2)
                    fresh = sum(row.count(1) for row in grid)
                    t = 0
                    while q and fresh:
                        for _ in range(len(q)):
                            r, c = q.popleft()
                            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                                nr, nc = r + dr, c + dc
                                if 0 <= nr < R and 0 <= nc < C and grid[nr][nc] == 1:
                                    grid[nr][nc] = 2
                                    fresh -= 1
                                    q.append((nr, nc))
                        t += 1
                    return t if fresh == 0 else -1

                print(minutes([[2, 1, 1], [1, 1, 0], [0, 1, 1]]))
            """),
        ],
        ["q = deque([s]); seen = {s}", "u = q.popleft(); for v in adj[u]", "O(V + E) time, O(V) space", "Level loop: for _ in range(len(q))", "0-1 BFS: appendleft for weight 0"],
        ["Marking visited on dequeue lets nodes enter the queue many times.", "BFS does not give shortest paths with arbitrary weights; use Dijkstra.", "Using list.pop(0) makes it O(V^2)."],
        [
            qa("basic", "Why does BFS find shortest paths in unweighted graphs?", "It processes vertices in nondecreasing order of distance from the source because the queue holds all distance-d vertices before any distance-(d+1) vertex. So the first time a vertex is discovered, it is via a path with the fewest edges."),
            qa("basic", "What is the complexity of BFS?", "O(V + E) time with an adjacency list, since each vertex is enqueued once and each edge examined once (twice for undirected). Space is O(V) for the queue and visited set."),
            qa("intermediate", "What is multi-source BFS?", "Initialise the queue with all source vertices at distance 0, then run BFS normally. Each vertex's distance becomes its distance to the nearest source, solving problems like nearest exit or simultaneous spreading in one O(V + E) pass."),
            qa("advanced", "What is bidirectional BFS and why is it faster?", "Run BFS from the source and target simultaneously, alternating frontiers, and stop when they meet. With branching factor b and distance d, it explores about 2 b^(d/2) nodes instead of b^d, a huge saving for problems like word ladder."),
        ],
        ["dfs", "graph-representations", "dijkstra", "queues-deques"],
        chain(
            ("start A", "queue [A]", "Seed", "Mark A visited and enqueue it."),
            ("pop A", "push B, C", "Level 1", "Neighbours B and C get distance 1.", "A"),
            ("pop B", "push D, E", "Level 2", "D and E get distance 2; A is already visited.", "B"),
            ("pop C", "push F", "Level 2", "F gets distance 2 via C.", "C"),
            ("path A-F", "A, C, F", "Reconstruct", "Follow parent pointers back from F.", "parents"),
        ),
    ),
    topic(
        "dfs", "Depth-First Search", "graphs", "basic", "DF",
        "Go as deep as possible along each branch before backtracking; uses recursion or a stack.",
        "DFS is exploring a maze by always taking the next unexplored corridor and only walking back when you hit a dead end, leaving chalk marks so you never revisit a room.",
        "Depth-first search visits a vertex, marks it, and recursively explores each unvisited neighbour before returning. It can be written recursively or with an explicit stack; both are O(V + E) time and O(V) space. DFS is the basis for connected components, flood fill, cycle detection, topological sorting, finding bridges and articulation points, and strongly connected components. In directed graphs, cycle detection uses three colours: white (unvisited), grey (on the current path) and black (finished); an edge to a grey vertex is a back edge, which means a cycle. Recording entry and exit times classifies edges and orders vertices; reverse post-order is a topological order of a DAG. DFS does not find shortest paths. On large graphs, recursion depth can exceed Python's limit, so use an iterative stack.",
        ["Counting connected components and islands.", "Cycle detection in directed and undirected graphs.", "Topological sort via post-order.", "Path existence, maze solving and flood fill."],
        [
            "O(V + E) time, O(V) space (stack or recursion).",
            "Three colours detect cycles in directed graphs.",
            "Undirected cycle: visited neighbour that is not the parent.",
            "Reverse post-order = topological order of a DAG.",
            "Prefer iterative DFS for very deep graphs in Python.",
        ],
        [
            ex("Count islands with DFS", "basic", "Flood fill each unvisited land cell.", "python", """
                grid = [list("11000"), list("11000"), list("00100"), list("00011")]

                def islands(g):
                    R, C = len(g), len(g[0])
                    def sink(r, c):
                        if 0 <= r < R and 0 <= c < C and g[r][c] == "1":
                            g[r][c] = "0"
                            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                                sink(r + dr, c + dc)
                    count = 0
                    for r in range(R):
                        for c in range(C):
                            if g[r][c] == "1":
                                count += 1
                                sink(r, c)
                    return count

                print("islands:", islands(grid))
            """),
            ex("Recursive vs iterative order", "basic", "Visit order and discovery path.", "python", """
                graph = {1: [2, 3], 2: [4, 5], 3: [6], 4: [], 5: [6], 6: []}

                def dfs_rec(u, seen, order):
                    seen.add(u)
                    order.append(u)
                    for v in graph[u]:
                        if v not in seen:
                            dfs_rec(v, seen, order)
                    return order

                def dfs_iter(s):
                    seen, order, stack = set(), [], [s]
                    while stack:
                        u = stack.pop()
                        if u in seen:
                            continue
                        seen.add(u)
                        order.append(u)
                        for v in reversed(graph[u]):
                            if v not in seen:
                                stack.append(v)
                    return order

                print("recursive:", dfs_rec(1, set(), []))
                print("iterative:", dfs_iter(1))
            """),
            ex("Directed cycle detection with colours", "intermediate", "Grey node on the stack means a back edge.", "python", """
                def find_cycle(graph):
                    WHITE, GREY, BLACK = 0, 1, 2
                    color = {u: WHITE for u in graph}
                    def visit(u, path):
                        color[u] = GREY
                        path.append(u)
                        for v in graph[u]:
                            if color[v] == GREY:
                                return path[path.index(v):] + [v]
                            if color[v] == WHITE:
                                c = visit(v, path)
                                if c:
                                    return c
                        color[u] = BLACK
                        path.pop()
                        return None
                    for u in graph:
                        if color[u] == WHITE:
                            c = visit(u, [])
                            if c:
                                return c
                    return None

                print(find_cycle({"a": ["b"], "b": ["c"], "c": []}))
                print(find_cycle({"a": ["b"], "b": ["c"], "c": ["a"]}))
            """),
        ],
        ["Recursive: visit(u): seen.add(u); for v in adj[u]", "Iterative: stack = [s]; u = stack.pop()", "Colours: WHITE/GREY/BLACK", "O(V + E)", "sys.setrecursionlimit or iterative for depth > 1000"],
        ["Undirected cycle check must ignore the edge back to the parent.", "Recursive DFS on a 10^5-node path raises RecursionError.", "Iterative DFS visit order differs from recursive unless neighbours are pushed reversed."],
        [
            qa("basic", "What is the complexity of DFS?", "O(V + E) time with an adjacency list because each vertex and edge is processed once, and O(V) space for the visited set and recursion or explicit stack."),
            qa("intermediate", "How do you detect a cycle in a directed graph?", "Run DFS with three states: unvisited, in progress (on the recursion stack) and done. Encountering an in-progress vertex means a back edge and thus a cycle. Kahn's algorithm is an alternative: a cycle exists if not all vertices are removed."),
            qa("intermediate", "How do you detect a cycle in an undirected graph?", "During DFS, if you reach an already visited vertex that is not the parent you came from, there is a cycle. Union-find is an alternative: an edge whose endpoints already share a root forms a cycle."),
            qa("intermediate", "When do you choose DFS over BFS?", "DFS suits exhaustive exploration, connectivity, cycle detection, topological order and backtracking, and uses memory proportional to depth. BFS is needed for shortest paths by edge count and uses memory proportional to the frontier width."),
        ],
        ["bfs", "topological-sort", "backtracking", "recursion"],
        chain(
            ("start 1", "stack [1]", "Begin", "Visit 1 and mark it."),
            ("go to 2", "path 1-2", "Deeper", "Take the first unvisited neighbour.", "1"),
            ("go to 4", "dead end", "Deepest", "4 has no unvisited neighbours.", "2"),
            ("backtrack", "try 5 -> 6", "Return", "Back at 2, explore 5 and then 6.", "4"),
            ("back to 1", "3 next", "Finish", "Visit 3; 6 is already seen. Order: 1, 2, 4, 5, 6, 3.", "pop"),
        ),
    ),
    topic(
        "topological-sort", "Topological Sort", "graphs", "intermediate", "TO",
        "Order the vertices of a DAG so every edge points forward; Kahn's algorithm or DFS post-order.",
        "Topological sort is getting dressed: socks before shoes, shirt before tie. Any order that respects all such rules works, and if the rules form a loop, nobody can get dressed.",
        "A topological ordering of a directed acyclic graph (DAG) lists vertices so that for every edge u -> v, u comes before v. Kahn's algorithm computes in-degrees, enqueues all vertices with in-degree 0, and repeatedly removes one, appends it to the order and decrements its neighbours' in-degrees, enqueuing any that drop to 0. If the output has fewer than V vertices, the graph has a cycle. The DFS approach appends each vertex after all its descendants finish (post-order) and reverses the result. Both run in O(V + E). Topological orders are generally not unique; using a min-heap instead of a queue in Kahn's algorithm gives the lexicographically smallest order. Applications include build systems, course scheduling, spreadsheet recalculation, and DP on DAGs such as longest path. Python 3.9+ ships graphlib.TopologicalSorter.",
        ["Build and task dependency ordering (make, Bazel, CI pipelines).", "Course schedule feasibility.", "Package installation order.", "Longest or shortest path in a DAG via DP."],
        [
            "Only DAGs have a topological order.",
            "Kahn: in-degree 0 queue; cycle if output size < V.",
            "DFS: reverse post-order.",
            "O(V + E) for both.",
            "graphlib.TopologicalSorter in the standard library.",
        ],
        [
            ex("Kahn's algorithm with trace", "basic", "Queue of zero in-degree nodes.", "python", """
                from collections import deque, defaultdict

                def kahn(n, edges):
                    adj, indeg = defaultdict(list), [0] * n
                    for u, v in edges:
                        adj[u].append(v)
                        indeg[v] += 1
                    q = deque(i for i in range(n) if indeg[i] == 0)
                    order = []
                    while q:
                        u = q.popleft()
                        order.append(u)
                        for v in adj[u]:
                            indeg[v] -= 1
                            if indeg[v] == 0:
                                q.append(v)
                        print(f"take {u}: indeg={indeg} queue={list(q)}")
                    return order if len(order) == n else None

                print("order:", kahn(6, [(5, 2), (5, 0), (4, 0), (4, 1), (2, 3), (3, 1)]))
                print("cycle:", kahn(3, [(0, 1), (1, 2), (2, 0)]))
            """),
            ex("DFS post-order", "intermediate", "Reverse of finish order.", "python", """
                def topo_dfs(graph):
                    seen, post = set(), []
                    def visit(u):
                        seen.add(u)
                        for v in graph.get(u, []):
                            if v not in seen:
                                visit(v)
                        post.append(u)
                    for u in graph:
                        if u not in seen:
                            visit(u)
                    return post[::-1]

                courses = {"intro": ["ds", "web"], "ds": ["algo"], "web": [], "algo": ["ml"], "ml": []}
                print(topo_dfs(courses))
            """),
            ex("graphlib.TopologicalSorter", "basic", "Standard library version; maps node -> predecessors.", "python", """
                from graphlib import TopologicalSorter, CycleError

                deps = {"deploy": {"test", "build"}, "test": {"build"}, "build": {"fetch"}}
                print(list(TopologicalSorter(deps).static_order()))
                try:
                    list(TopologicalSorter({"a": {"b"}, "b": {"a"}}).static_order())
                except CycleError as e:
                    print("cycle detected:", e.args[1])
            """),
        ],
        ["Kahn: indeg, deque of zeros, O(V + E)", "len(order) < V -> cycle", "DFS: post.append(u) then reverse", "heapq instead of deque -> lexicographic order", "graphlib.TopologicalSorter(deps).static_order()"],
        ["Running topological sort on a graph with a cycle silently gives a partial order unless you check the count.", "Edge direction confusion: 'a depends on b' means b -> a.", "Forgetting vertices with no edges at all."],
        [
            qa("basic", "What is a topological sort?", "A linear ordering of a DAG's vertices such that every directed edge u -> v has u before v. It exists if and only if the graph has no directed cycle."),
            qa("intermediate", "Explain Kahn's algorithm.", "Compute in-degrees, enqueue all vertices with in-degree 0, then repeatedly dequeue a vertex, output it, and decrement the in-degree of its successors, enqueuing those reaching 0. If fewer than V vertices are output, the remaining ones lie on a cycle. Runs in O(V + E)."),
            qa("intermediate", "How does DFS produce a topological order?", "A vertex is appended to a list only after all vertices reachable from it have finished. In a DAG, every edge u -> v therefore has v finishing before u, so reversing the finish order puts u before v."),
            qa("intermediate", "How do you solve course schedule (can you finish all courses)?", "Model courses as vertices and prerequisites as edges, then run Kahn's algorithm or DFS cycle detection. All courses can be finished exactly when the graph is acyclic, i.e. the topological order contains every course."),
        ],
        ["dfs", "bfs", "dynamic-programming", "graph-representations"],
        chain(
            ("indegrees", "4,5 have 0", "Init", "Edges 5->2, 5->0, 4->0, 4->1, 2->3, 3->1; queue [4, 5]."),
            ("take 4", "0:1, 1:1", "Remove", "Decrement 0 and 1; neither reaches 0 yet.", "4"),
            ("take 5", "push 2, 0", "Remove", "2 and 0 drop to in-degree 0 and are queued.", "5"),
            ("take 2, 0", "push 3", "Continue", "Removing 2 frees 3.", "2"),
            ("take 3, 1", "4,5,2,0,3,1", "Order", "All 6 vertices output, so the graph is a DAG.", "3"),
        ),
    ),
    topic(
        "dijkstra", "Dijkstra's Shortest Path", "graphs", "intermediate", "DJ",
        "Greedily settle the closest unvisited vertex using a min-heap; works with non-negative weights.",
        "Dijkstra is spreading water through pipes of different lengths: the water reaches nearby junctions first, and once a junction is wet, no later route can reach it sooner.",
        "Dijkstra's algorithm computes shortest path distances from a source in a graph with non-negative edge weights. It keeps a tentative distance for every vertex, initially infinity except 0 for the source, and a min-heap of (distance, vertex). Repeatedly pop the vertex with the smallest distance; if the popped distance is stale (larger than the recorded best), skip it; otherwise relax each outgoing edge, updating dist[v] = dist[u] + w when it improves and pushing the new pair. Once a vertex is popped with its current distance, that distance is final, which is the greedy correctness argument and why negative edges break it. With a binary heap the running time is O((V + E) log V), and space is O(V + E). Storing predecessors reconstructs paths. A* adds a heuristic to guide the search toward a target, and for unweighted graphs BFS is simpler and faster.",
        ["GPS and road network routing.", "Network routing protocols like OSPF.", "Cheapest flight or minimum cost paths.", "Grid paths with varying terrain costs."],
        [
            "Requires non-negative edge weights.",
            "Min-heap of (dist, node); skip stale entries.",
            "O((V + E) log V) with a binary heap.",
            "A popped vertex's distance is final.",
            "Keep a prev map to rebuild paths.",
        ],
        [
            ex("Dijkstra with heapq and trace", "basic", "Show each settled vertex.", "python", """
                import heapq

                graph = {
                    "A": [("B", 4), ("C", 1)],
                    "B": [("D", 1)],
                    "C": [("B", 2), ("D", 5)],
                    "D": [],
                }

                def dijkstra(g, s):
                    dist, prev = {v: float("inf") for v in g}, {}
                    dist[s] = 0
                    pq = [(0, s)]
                    while pq:
                        d, u = heapq.heappop(pq)
                        if d > dist[u]:
                            continue
                        print(f"settle {u} at {d}")
                        for v, w in g[u]:
                            if d + w < dist[v]:
                                dist[v], prev[v] = d + w, u
                                heapq.heappush(pq, (dist[v], v))
                    return dist, prev

                dist, prev = dijkstra(graph, "A")
                path, cur = [], "D"
                while cur != "A":
                    path.append(cur); cur = prev[cur]
                print(dist, "path to D:", ["A"] + path[::-1])
            """),
            ex("Why negative edges break it", "intermediate", "Dijkstra settles too early.", "python", """
                import heapq

                g = {"S": [("A", 2), ("B", 5)], "A": [], "B": [("A", -4)]}

                def dijkstra(g, s):
                    dist, done = {v: float("inf") for v in g}, set()
                    dist[s] = 0
                    pq = [(0, s)]
                    while pq:
                        d, u = heapq.heappop(pq)
                        if u in done:
                            continue
                        done.add(u)
                        for v, w in g[u]:
                            if v not in done and d + w < dist[v]:
                                dist[v] = d + w
                                heapq.heappush(pq, (dist[v], v))
                    return dist

                print("dijkstra:", dijkstra(g, "S"), "true shortest S->A is 5 + (-4) = 1")
            """),
            ex("Grid with weighted cells", "intermediate", "Minimum path cost moving in 4 directions.", "python", """
                import heapq

                cost = [[1, 3, 1, 2],
                        [1, 5, 1, 9],
                        [4, 2, 1, 1]]

                def min_cost(cost):
                    R, C = len(cost), len(cost[0])
                    best = {(0, 0): cost[0][0]}
                    pq = [(cost[0][0], 0, 0)]
                    while pq:
                        d, r, c = heapq.heappop(pq)
                        if (r, c) == (R - 1, C - 1):
                            return d
                        if d > best[(r, c)]:
                            continue
                        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < R and 0 <= nc < C:
                                nd = d + cost[nr][nc]
                                if nd < best.get((nr, nc), float("inf")):
                                    best[(nr, nc)] = nd
                                    heapq.heappush(pq, (nd, nr, nc))

                print("min cost:", min_cost(cost))
            """),
        ],
        ["heapq.heappush(pq, (dist, node))", "if d > dist[u]: continue  (stale)", "O((V + E) log V)", "Non-negative weights only", "Unweighted -> BFS; negative -> Bellman-Ford"],
        ["Negative edge weights produce wrong answers.", "Not skipping stale heap entries wastes time (still correct, slower).", "Stopping early is only valid once the target is popped, not when first pushed."],
        [
            qa("basic", "What problem does Dijkstra solve and what are its constraints?", "Single-source shortest paths in a weighted graph whose edge weights are all non-negative. With negative edges it can finalise a vertex too early and return wrong distances."),
            qa("intermediate", "What is Dijkstra's time complexity?", "O((V + E) log V) with a binary heap, since each edge relaxation may push into the heap and each pop costs O(log V). With a Fibonacci heap it is O(E + V log V); with an array scan it is O(V^2), which is fine for dense graphs."),
            qa("intermediate", "Why is a popped vertex's distance final?", "All remaining heap entries have distance at least d, and with non-negative weights any other path to the vertex would pass through one of them and only get longer. So no later path can improve it. This is the greedy-choice argument."),
            qa("intermediate", "How do you handle decrease-key with Python's heapq?", "Push a new (distance, vertex) entry whenever a shorter distance is found, and on pop discard entries whose distance exceeds the stored best. The heap can hold O(E) entries, keeping O(E log E) = O(E log V) time."),
            qa("advanced", "How does A* relate to Dijkstra?", "A* orders the heap by g(v) + h(v), where g is the distance so far and h is a heuristic estimate to the target. With h = 0 it is exactly Dijkstra; with an admissible and consistent heuristic it remains optimal while exploring far fewer vertices."),
        ],
        ["bellman-ford", "bfs", "heaps", "greedy"],
        chain(
            ("dist A=0", "heap [(0,A)]", "Init", "All other distances are infinity."),
            ("settle A", "B=4, C=1", "Relax", "Pop A, relax edges to B (4) and C (1).", "A"),
            ("settle C", "B=3, D=6", "Relax", "Pop C at 1: B improves to 3, D becomes 6.", "C"),
            ("settle B", "D=4", "Relax", "Pop B at 3: D improves to 4. Stale (4,B) is skipped later.", "B"),
            ("settle D", "A-C-B-D = 4", "Done", "D popped at 4; follow prev pointers for the path.", "D"),
        ),
    ),
    topic(
        "bellman-ford", "Bellman-Ford & Negative Cycles", "graphs", "advanced", "BL",
        "Relax every edge V-1 times; handles negative weights and detects negative cycles.",
        "Bellman-Ford is passing rumours of cheaper routes around a group V-1 times: after enough rounds everyone knows the best price, and if prices keep dropping after that, someone has found an infinite money loop.",
        "Bellman-Ford computes single-source shortest paths even when some edge weights are negative. It initialises distances (0 for the source, infinity otherwise) and performs V-1 rounds, relaxing every edge in each round. Because any shortest simple path has at most V-1 edges, after round k all shortest paths with at most k edges are correct. A V-th round that still improves some distance proves a negative cycle reachable from the source, so shortest paths are undefined. Time is O(V * E), slower than Dijkstra, and space is O(V). Early termination when a round makes no changes speeds it up in practice, and SPFA is a queue-based optimisation. Restricting to k rounds (copying distances each round) solves 'cheapest flight with at most k stops'. Applications include distance-vector routing (RIP) and currency arbitrage detection via negative log weights.",
        ["Graphs with negative edge weights.", "Detecting negative cycles and arbitrage.", "Shortest paths with at most k edges.", "Distance-vector routing protocols."],
        [
            "V-1 rounds of relaxing all edges: O(V * E).",
            "Extra round improvement => negative cycle.",
            "Handles negative weights; Dijkstra does not.",
            "Stop early if a round changes nothing.",
            "k-edge limit: relax from a copy of last round's distances.",
        ],
        [
            ex("Bellman-Ford with round trace", "basic", "Negative edge, no negative cycle.", "python", """
                def bellman_ford(n, edges, s):
                    dist = [float("inf")] * n
                    dist[s] = 0
                    for rnd in range(1, n):
                        changed = False
                        for u, v, w in edges:
                            if dist[u] + w < dist[v]:
                                dist[v] = dist[u] + w
                                changed = True
                        print(f"round {rnd}: {dist}")
                        if not changed:
                            break
                    for u, v, w in edges:
                        if dist[u] + w < dist[v]:
                            return None
                    return dist

                edges = [(0, 1, 4), (0, 2, 5), (1, 3, 3), (2, 1, -3), (3, 4, 2), (2, 4, 4)]
                print("result:", bellman_ford(5, edges, 0))
            """),
            ex("Negative cycle and arbitrage", "intermediate", "Use -log(rate) as weights.", "python", """
                import math

                def has_negative_cycle(n, edges):
                    dist = [0.0] * n
                    for _ in range(n - 1):
                        for u, v, w in edges:
                            if dist[u] + w < dist[v]:
                                dist[v] = dist[u] + w
                    return any(dist[u] + w < dist[v] - 1e-12 for u, v, w in edges)

                names = ["USD", "EUR", "GBP"]
                rates = {(0, 1): 0.9, (1, 2): 0.9, (2, 0): 1.3}
                edges = [(u, v, -math.log(r)) for (u, v), r in rates.items()]
                print("product of rates:", round(0.9 * 0.9 * 1.3, 3))
                print("arbitrage:", has_negative_cycle(3, edges))
            """),
            ex("Cheapest flight within k stops", "intermediate", "k+1 rounds using last round's snapshot.", "python", """
                def cheapest(n, flights, src, dst, k):
                    dist = [float("inf")] * n
                    dist[src] = 0
                    for _ in range(k + 1):
                        prev = dist[:]
                        for u, v, w in flights:
                            if prev[u] + w < dist[v]:
                                dist[v] = prev[u] + w
                    return dist[dst] if dist[dst] < float("inf") else -1

                flights = [(0, 1, 100), (1, 2, 100), (2, 3, 100), (0, 2, 500), (1, 3, 600)]
                print("k=1:", cheapest(4, flights, 0, 3, 1), "k=2:", cheapest(4, flights, 0, 3, 2))
            """),
        ],
        ["for _ in range(V - 1): for u, v, w in edges: relax", "Extra pass improves -> negative cycle", "O(V * E) time, O(V) space", "Arbitrage: weight = -log(rate)", "Floyd-Warshall: all pairs O(V^3)"],
        ["Updating in place within a round can use more than k edges; copy for k-limited variants.", "Unreachable vertices stay at infinity; inf + w is still inf in Python floats.", "Negative cycles not reachable from the source are not detected from that source."],
        [
            qa("intermediate", "Why does Bellman-Ford run V-1 iterations?", "A shortest path without cycles has at most V-1 edges. After i rounds of relaxing all edges, every shortest path using at most i edges is found, so V-1 rounds suffice when no negative cycle exists."),
            qa("intermediate", "How does Bellman-Ford detect negative cycles?", "After V-1 rounds, run one more pass. If any edge can still be relaxed, a distance can be lowered indefinitely, which only happens when a negative-weight cycle is reachable from the source."),
            qa("intermediate", "When would you use Bellman-Ford over Dijkstra?", "When the graph has negative edge weights, when you need to detect negative cycles, or when the number of edges in a path is limited (k stops). Otherwise Dijkstra's O((V + E) log V) is much faster than O(VE)."),
            qa("advanced", "How do you detect currency arbitrage?", "Model currencies as vertices and exchange rates as edges with weight -log(rate). A cycle whose product of rates exceeds 1 has a negative sum of weights, so Bellman-Ford's negative cycle detection finds arbitrage opportunities."),
        ],
        ["dijkstra", "dynamic-programming", "graph-representations"],
        chain(
            ("dist[0]=0", "others inf", "Init", "Edges include a negative edge 2->1 with weight -3."),
            ("round 1", "1=2, 3=7, 4=9", "Relax all", "In edge-list order, 0->1 gives 4, 0->2 gives 5, 1->3 gives 7, then 2->1 lowers 1 to 2.", "edges"),
            ("round 2", "3=5, 4=7", "Propagate", "Improvements flow along longer paths: 3 = 2+3, 4 = 5+2.", "dist"),
            ("no change", "early stop", "Converged", "A round with no updates means distances are final.", "stable"),
            ("extra pass", "no improvement", "Cycle check", "No edge relaxes further, so there is no negative cycle.", "check"),
        ),
    ),
    topic(
        "mst", "Minimum Spanning Trees: Kruskal & Prim", "graphs", "intermediate", "MT",
        "Connect all vertices with the minimum total edge weight and no cycles.",
        "An MST is laying fibre cable between towns as cheaply as possible: every town must be connected, but you never pay for a cable that would just create a redundant loop.",
        "A minimum spanning tree of a connected, undirected, weighted graph is a subset of V-1 edges that connects all vertices with minimum total weight. Kruskal's algorithm sorts edges by weight and adds each edge if it connects two different components, tracked with union-find; it runs in O(E log E). Prim's algorithm grows a single tree from a start vertex, repeatedly adding the cheapest edge leaving the tree using a min-heap; it runs in O((V + E) log V). Both are greedy and correct by the cut property: the lightest edge crossing any cut belongs to some MST. The cycle property says the heaviest edge on any cycle is not in the MST (if unique). Kruskal suits sparse graphs given as edge lists; Prim suits dense graphs or adjacency lists. If the graph is disconnected, Kruskal produces a minimum spanning forest. An MST is not the same as a shortest-path tree.",
        ["Designing cheap networks (cables, pipes, roads).", "Clustering by removing the heaviest MST edges.", "Approximation for metric travelling salesman.", "Image segmentation."],
        [
            "MST has exactly V-1 edges and no cycles.",
            "Kruskal: sort edges + union-find, O(E log E).",
            "Prim: min-heap from a start vertex, O((V + E) log V).",
            "Cut property justifies the greedy choice.",
            "MST minimises total weight, not individual path lengths.",
        ],
        [
            ex("Kruskal with union-find", "basic", "Accept or reject each edge in weight order.", "python", """
                def kruskal(n, edges):
                    parent = list(range(n))
                    def find(x):
                        while parent[x] != x:
                            parent[x] = parent[parent[x]]
                            x = parent[x]
                        return x
                    total, used = 0, []
                    for w, u, v in sorted(edges):
                        ru, rv = find(u), find(v)
                        if ru == rv:
                            print(f"skip {u}-{v} ({w}): would form a cycle")
                            continue
                        parent[ru] = rv
                        total += w
                        used.append((u, v, w))
                        print(f"take {u}-{v} ({w})")
                    return total, used

                edges = [(1, 0, 1), (4, 0, 2), (3, 1, 2), (2, 1, 3), (5, 2, 3), (7, 3, 4), (6, 2, 4)]
                print(kruskal(5, edges))
            """),
            ex("Prim with a heap", "intermediate", "Grow from vertex 0.", "python", """
                import heapq
                from collections import defaultdict

                def prim(n, edges):
                    adj = defaultdict(list)
                    for w, u, v in edges:
                        adj[u].append((w, v))
                        adj[v].append((w, u))
                    seen, total, pq, order = set(), 0, [(0, 0, -1)], []
                    while pq and len(seen) < n:
                        w, u, frm = heapq.heappop(pq)
                        if u in seen:
                            continue
                        seen.add(u)
                        total += w
                        if frm >= 0:
                            order.append((frm, u, w))
                        for nw, v in adj[u]:
                            if v not in seen:
                                heapq.heappush(pq, (nw, v, u))
                    return total, order

                edges = [(1, 0, 1), (4, 0, 2), (3, 1, 2), (2, 1, 3), (5, 2, 3), (7, 3, 4), (6, 2, 4)]
                print(prim(5, edges))
            """),
        ],
        ["Kruskal: sorted(edges) + union-find", "Prim: heapq of (w, v) crossing the cut", "Kruskal O(E log E) · Prim O((V+E) log V)", "MST edges = V - 1", "Clustering: drop k-1 heaviest MST edges"],
        ["MST applies to undirected graphs; directed version is arborescence (Edmonds).", "Confusing MST with shortest paths from a source.", "Disconnected graphs give a forest; check the edge count."],
        [
            qa("basic", "What is a minimum spanning tree?", "A set of V-1 edges connecting all vertices of a connected undirected weighted graph with no cycles and minimum total weight. It may not be unique when weights repeat."),
            qa("intermediate", "Compare Kruskal and Prim.", "Kruskal sorts all edges and uses union-find to add the cheapest edge joining two components, O(E log E), and works well on sparse edge lists. Prim grows one tree with a priority queue of crossing edges, O((V + E) log V), and is convenient with adjacency lists or dense graphs."),
            qa("intermediate", "Why is the greedy choice in MST algorithms correct?", "By the cut property: for any partition of vertices into two sets, the minimum-weight edge crossing the cut belongs to some MST. Both algorithms only ever add such an edge, so they never make a choice that cannot be extended to an optimum."),
            qa("advanced", "Is the MST path between two vertices a shortest path?", "No. The MST minimises total weight of the whole tree, not individual distances. A direct edge of weight 3 between A and B may be excluded if A and B are connected through cheaper edges summing to 4; Dijkstra solves shortest paths."),
        ],
        ["union-find", "greedy", "dijkstra", "heaps"],
        chain(
            ("sort edges", "1,2,3,4,5...", "Order", "Process edges from lightest to heaviest."),
            ("take 0-1 (1)", "join {0,1}", "Accept", "Endpoints are in different components.", "w=1"),
            ("take 1-3 (2)", "join {0,1,3}", "Accept", "Another cheap edge across components.", "w=2"),
            ("take 1-2 (3)", "skip 0-2 (4)", "Reject cycle", "0-2 now joins two vertices already connected.", "w=3"),
            ("take 2-4 (6)", "total 12", "Done", "V-1 = 4 edges chosen; total weight 1+2+3+6 = 12.", "w=6"),
        ),
    ),
    topic(
        "greedy", "Greedy Algorithms", "techniques", "intermediate", "GD",
        "Make the locally best choice at each step and never reconsider; correct only with a proof.",
        "Greedy is a hiker always taking the steepest uphill step. On a single hill that reaches the summit; on a mountain range it may strand you on a small peak.",
        "A greedy algorithm builds a solution step by step, always choosing the option that looks best right now, without backtracking. It works when the problem has the greedy-choice property (some optimal solution starts with the greedy choice) and optimal substructure (the rest is an optimal solution to the remaining subproblem). Correctness is usually shown by an exchange argument: take any optimal solution and swap in the greedy choice without making it worse. Classic successes include activity selection (pick the earliest finishing interval), Huffman coding, Dijkstra, Kruskal and Prim, fractional knapsack, and jump game. Classic failures include 0/1 knapsack and coin change with arbitrary denominations, which need dynamic programming. Greedy algorithms are typically O(n log n) due to sorting, plus O(n) for the scan. When unsure, test the greedy rule against brute force on small random inputs.",
        ["Interval scheduling and meeting rooms.", "Huffman compression.", "Minimum spanning trees and Dijkstra.", "Task scheduling with deadlines and jump game."],
        [
            "Needs greedy-choice property and optimal substructure.",
            "Prove with an exchange argument or 'greedy stays ahead'.",
            "Often sort first: O(n log n).",
            "Activity selection: sort by end time.",
            "Coin change greedy fails for denominations like {1, 3, 4}.",
        ],
        [
            ex("Activity selection", "basic", "Earliest finish time first.", "python", """
                def select(intervals):
                    chosen, end = [], float("-inf")
                    for s, e in sorted(intervals, key=lambda x: x[1]):
                        if s >= end:
                            chosen.append((s, e))
                            end = e
                    return chosen

                meetings = [(1, 4), (3, 5), (0, 6), (5, 7), (3, 9), (5, 9), (6, 10), (8, 11), (8, 12), (2, 14), (12, 16)]
                print(select(meetings))
            """),
            ex("When greedy fails: coin change", "intermediate", "Compare greedy with DP.", "python", """
                def greedy_coins(coins, amount):
                    used = []
                    for c in sorted(coins, reverse=True):
                        while amount >= c:
                            amount -= c
                            used.append(c)
                    return used if amount == 0 else None

                def dp_coins(coins, amount):
                    best = [0] + [float("inf")] * amount
                    for a in range(1, amount + 1):
                        for c in coins:
                            if c <= a:
                                best[a] = min(best[a], best[a - c] + 1)
                    return best[amount]

                for coins, amt in [([1, 5, 10, 25], 63), ([1, 3, 4], 6)]:
                    g = greedy_coins(coins, amt)
                    print(coins, amt, "greedy:", g, len(g), "| optimal count:", dp_coins(coins, amt))
            """),
            ex("Jump game and Huffman", "advanced", "Farthest reach and merging smallest frequencies.", "python", """
                import heapq

                def can_jump(nums):
                    reach = 0
                    for i, x in enumerate(nums):
                        if i > reach:
                            return False
                        reach = max(reach, i + x)
                    return True

                def huffman_cost(freqs):
                    h = list(freqs)
                    heapq.heapify(h)
                    cost = 0
                    while len(h) > 1:
                        a, b = heapq.heappop(h), heapq.heappop(h)
                        cost += a + b
                        heapq.heappush(h, a + b)
                    return cost

                print(can_jump([2, 3, 1, 1, 4]), can_jump([3, 2, 1, 0, 4]))
                print("huffman total bits:", huffman_cost([5, 9, 12, 13, 16, 45]))
            """),
        ],
        ["sorted(items, key=lambda x: x[1])  (by end time)", "Exchange argument for proofs", "Typical O(n log n)", "heapq for repeatedly picking the min", "Verify against brute force on small inputs"],
        ["Greedy that seems right often fails on crafted inputs (coins {1,3,4}).", "Sorting by start time instead of end time breaks activity selection.", "0/1 knapsack needs DP; only fractional knapsack is greedy."],
        [
            qa("basic", "What makes a problem solvable greedily?", "It must have the greedy-choice property, meaning a globally optimal solution can be reached by making the locally optimal choice, and optimal substructure, meaning the remaining problem after that choice is solved optimally in the same way."),
            qa("intermediate", "How do you prove a greedy algorithm correct?", "Common techniques are the exchange argument (transform any optimal solution into the greedy one step by step without worsening it) and 'greedy stays ahead' (show that after each step the greedy partial solution is at least as good as any other). Matroid theory gives a general framework."),
            qa("intermediate", "Why does activity selection sort by end time?", "Choosing the interval that finishes first leaves the most room for remaining intervals. An exchange argument shows that any optimal schedule's first interval can be replaced by the earliest-finishing one without conflicts, so greedy is optimal."),
            qa("intermediate", "Greedy vs dynamic programming?", "Greedy commits to one choice per step and never revisits it, so it is fast but only correct for special structures. DP considers all choices for each subproblem and reuses results, guaranteeing optimality for problems with overlapping subproblems, at higher cost."),
        ],
        ["dynamic-programming", "intervals", "mst", "dijkstra"],
        chain(
            ("sort by end", "(1,4),(3,5),...", "Order", "Sort meetings by finishing time."),
            ("take (1,4)", "end = 4", "Choose", "The earliest finisher is always safe to take.", "first"),
            ("skip (3,5)", "overlaps", "Reject", "Starts before 4, so it conflicts.", "end=4"),
            ("take (5,7)", "end = 7", "Choose", "First compatible meeting in end order.", "next"),
            ("take (8,11)", "(12,16) too", "Result", "Greedy picks 4 meetings, which is optimal.", "done"),
        ),
    ),
    topic(
        "dynamic-programming", "Dynamic Programming: Memoization vs Tabulation", "techniques", "intermediate", "DP",
        "Solve overlapping subproblems once and reuse them, top-down with a cache or bottom-up with a table.",
        "Dynamic programming is keeping a notebook of answers while doing homework: when a problem reappears, you copy your earlier answer instead of solving it again.",
        "Dynamic programming applies when a problem has optimal substructure (the optimum is built from optimal sub-solutions) and overlapping subproblems (the same subproblem recurs). The workflow is: define the state (what parameters identify a subproblem), write the recurrence (transition), set base cases, choose an evaluation order and extract the answer. Memoization (top-down) writes the natural recursion and caches results, for example with functools.lru_cache; it only computes reachable states but pays recursion overhead and risks deep stacks. Tabulation (bottom-up) fills a table in dependency order with loops; it avoids recursion and often allows space optimisation to a rolling array. Time complexity is number of states times work per transition. Classic warm-ups are Fibonacci, climbing stairs, house robber, coin change and unique grid paths. Reconstructing the actual solution requires storing choices or backtracking through the table.",
        ["Optimisation problems: minimum cost, maximum profit.", "Counting problems: number of ways or paths.", "Sequence problems on strings and arrays.", "Shortest paths on DAGs and Bellman-Ford style recurrences."],
        [
            "State + transition + base case + order + answer.",
            "Memoization: recursion + cache; tabulation: loops + table.",
            "Time = states x transitions per state.",
            "Rolling arrays cut space when only recent rows matter.",
            "Store choices to reconstruct the solution.",
        ],
        [
            ex("Climbing stairs three ways", "basic", "Memoized, tabulated, and O(1) space.", "python", """
                from functools import lru_cache

                @lru_cache(maxsize=None)
                def ways_memo(n):
                    if n <= 1:
                        return 1
                    return ways_memo(n - 1) + ways_memo(n - 2)

                def ways_table(n):
                    dp = [1] * (n + 1)
                    for i in range(2, n + 1):
                        dp[i] = dp[i - 1] + dp[i - 2]
                    return dp

                def ways_const(n):
                    a, b = 1, 1
                    for _ in range(n - 1):
                        a, b = b, a + b
                    return b

                print("table:", ways_table(10))
                print(ways_memo(30), ways_table(30)[-1], ways_const(30))
            """),
            ex("House robber with reconstruction", "intermediate", "Choose non-adjacent houses for max sum.", "python", """
                def rob(nums):
                    n = len(nums)
                    dp = [0] * (n + 1)
                    dp[1] = nums[0]
                    for i in range(2, n + 1):
                        dp[i] = max(dp[i - 1], dp[i - 2] + nums[i - 1])
                    picked, i = [], n
                    while i > 0:
                        if i == 1 or dp[i] != dp[i - 1]:
                            picked.append(i - 1)
                            i -= 2
                        else:
                            i -= 1
                    return dp[n], sorted(picked)

                print(rob([2, 7, 9, 3, 1]))
                print(rob([5, 1, 1, 5]))
            """),
            ex("Coin change: min coins and number of ways", "intermediate", "Two classic 1-D tables.", "python", """
                def min_coins(coins, amount):
                    dp = [0] + [float("inf")] * amount
                    for a in range(1, amount + 1):
                        for c in coins:
                            if c <= a and dp[a - c] + 1 < dp[a]:
                                dp[a] = dp[a - c] + 1
                    return dp[amount] if dp[amount] != float("inf") else -1

                def count_ways(coins, amount):
                    dp = [1] + [0] * amount
                    for c in coins:
                        for a in range(c, amount + 1):
                            dp[a] += dp[a - c]
                    return dp[amount]

                print("min coins for 11:", min_coins([1, 2, 5], 11))
                print("ways to make 5:", count_ways([1, 2, 5], 5))
            """),
        ],
        ["@functools.lru_cache(maxsize=None)", "dp = [0] * (n + 1); fill in order", "Time = #states x cost per state", "Rolling: a, b = b, a + b", "Count ways: loop coins outside to avoid permutations"],
        ["Wrong loop order in coin-count DP counts permutations instead of combinations.", "Memoization on mutable arguments (lists) fails: they are unhashable.", "Deep memoized recursion can still hit the recursion limit."],
        [
            qa("basic", "What two properties make a problem suitable for DP?", "Optimal substructure, so the optimal answer can be built from optimal answers to subproblems, and overlapping subproblems, so the same subproblems recur and caching saves work. Without overlap, plain divide and conquer suffices."),
            qa("intermediate", "Memoization vs tabulation?", "Memoization is top-down: write the recursion and cache results, computing only needed states, but with recursion overhead and stack depth limits. Tabulation is bottom-up: iterate states in dependency order, which is often faster, avoids recursion and enables rolling-array space savings, but may compute unneeded states."),
            qa("intermediate", "How do you approach a new DP problem?", "Define what a state means in words (for example dp[i] = best answer for the first i items), write the transition by considering the last decision, set base cases, decide the iteration order so dependencies are ready, and identify which state holds the final answer. Then analyse states times transitions."),
            qa("intermediate", "How do you reconstruct the actual solution, not just the value?", "Store the choice made at each state (a parent pointer) or, after filling the table, walk backwards from the final state checking which transition produced its value. Space-optimised rolling arrays usually lose this information."),
            qa("advanced", "Why does loop order matter in coin change counting?", "Iterating coins in the outer loop and amounts in the inner loop counts each multiset once, giving combinations. Swapping the loops counts each ordering separately, giving permutations, which answers a different question."),
        ],
        ["classic-dp", "recursion", "greedy", "space-complexity"],
        chain(
            ("fib(5)", "naive tree", "Problem", "Plain recursion recomputes fib(3) twice and fib(2) three times."),
            ("state", "dp[i] = fib(i)", "Define", "Each subproblem is identified by i.", "overlap"),
            ("recurrence", "dp[i-1]+dp[i-2]", "Transition", "Base cases dp[0] = 0, dp[1] = 1.", "state"),
            ("fill table", "0,1,1,2,3,5", "Tabulate", "Compute i = 2..5 in order, each once.", "order"),
            ("O(n)", "vs O(2^n)", "Result", "Two rolling variables reduce space to O(1).", "dp[5]"),
        ),
    ),
]

TOPICS += [
    topic(
        "classic-dp", "Classic DP: Knapsack, LIS, LCS, Edit Distance", "techniques", "advanced", "CD",
        "The canonical DP problems whose state designs reappear in countless interview questions.",
        "Classic DP problems are the standard chess openings of algorithms: once you know them, most new positions turn out to be variations you recognise.",
        "0/1 knapsack chooses items with weights and values to maximise value within capacity W; dp[w] is the best value for capacity w, and iterating w downwards ensures each item is used at most once, giving O(nW) time and O(W) space (pseudo-polynomial). Longest increasing subsequence (LIS) has an O(n^2) DP where dp[i] is the LIS ending at i, and an O(n log n) patience-sorting method that keeps tails[k] = smallest tail of an increasing subsequence of length k+1 and updates it with bisect_left. Longest common subsequence (LCS) uses dp[i][j] for prefixes a[:i] and b[:j]: if characters match, 1 + dp[i-1][j-1], else max(dp[i-1][j], dp[i][j-1]), O(nm). Edit (Levenshtein) distance uses the same grid with costs for insert, delete and replace: dp[i][j] = dp[i-1][j-1] if equal, else 1 + min of the three neighbours. These patterns generalise: knapsack to subset sum and partition, LCS to diff tools and DNA alignment, and edit distance to spell checking.",
        ["Budget allocation and subset-sum feasibility (knapsack).", "Diff tools and version control (LCS).", "Spell checkers and fuzzy matching (edit distance).", "Trend and sequence analysis (LIS)."],
        [
            "0/1 knapsack: dp[w] = max(dp[w], dp[w - wt] + val), loop w downward; O(nW).",
            "LIS: O(n^2) DP or O(n log n) with bisect on tails.",
            "LCS: match -> diag + 1, else max(up, left); O(nm).",
            "Edit distance: 1 + min(insert, delete, replace); O(nm).",
            "Knapsack is pseudo-polynomial: depends on the value of W.",
        ],
        [
            ex("0/1 knapsack", "intermediate", "1-D table iterated downward so items are not reused.", "python", """
                def knapsack(items, W):
                    dp = [0] * (W + 1)
                    for wt, val in items:
                        for w in range(W, wt - 1, -1):
                            dp[w] = max(dp[w], dp[w - wt] + val)
                        print(f"item (w={wt}, v={val}): {dp}")
                    return dp[W]

                print("best:", knapsack([(1, 1), (3, 4), (4, 5), (5, 7)], 7))
            """),
            ex("LIS in O(n log n)", "intermediate", "Patience sorting with bisect_left.", "python", """
                import bisect

                def lis(nums):
                    tails = []
                    for x in nums:
                        i = bisect.bisect_left(tails, x)
                        if i == len(tails):
                            tails.append(x)
                        else:
                            tails[i] = x
                        print(f"{x:3} -> tails {tails}")
                    return len(tails)

                print("LIS length:", lis([10, 9, 2, 5, 3, 7, 101, 18]))
            """),
            ex("LCS and edit distance", "advanced", "Two 2-D grids over string prefixes.", "python", """
                def lcs(a, b):
                    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
                    for i in range(1, len(a) + 1):
                        for j in range(1, len(b) + 1):
                            if a[i - 1] == b[j - 1]:
                                dp[i][j] = dp[i - 1][j - 1] + 1
                            else:
                                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
                    out, i, j = [], len(a), len(b)
                    while i and j:
                        if a[i - 1] == b[j - 1]:
                            out.append(a[i - 1]); i -= 1; j -= 1
                        elif dp[i - 1][j] >= dp[i][j - 1]:
                            i -= 1
                        else:
                            j -= 1
                    return dp[-1][-1], "".join(reversed(out))

                def edit(a, b):
                    prev = list(range(len(b) + 1))
                    for i in range(1, len(a) + 1):
                        cur = [i] + [0] * len(b)
                        for j in range(1, len(b) + 1):
                            if a[i - 1] == b[j - 1]:
                                cur[j] = prev[j - 1]
                            else:
                                cur[j] = 1 + min(prev[j], cur[j - 1], prev[j - 1])
                        prev = cur
                    return prev[-1]

                print("LCS:", lcs("ABCBDAB", "BDCABA"))
                print("edit(kitten, sitting):", edit("kitten", "sitting"))
                print("edit(horse, ros):", edit("horse", "ros"))
            """),
        ],
        ["Knapsack: for w in range(W, wt - 1, -1)", "LIS: bisect.bisect_left(tails, x)", "LCS: dp[i][j] = dp[i-1][j-1] + 1 if match", "Edit: 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])", "All grid DPs: O(n*m) time, O(min(n,m)) space"],
        ["Iterating capacity upward in 0/1 knapsack lets items be reused (that is unbounded knapsack).", "tails in the O(n log n) LIS is not an actual subsequence.", "Off-by-one between string index i-1 and table index i."],
        [
            qa("intermediate", "Why is 0/1 knapsack O(nW) considered pseudo-polynomial?", "The running time is polynomial in the numeric value of W, not in the number of bits needed to write W. Doubling the number of bits squares W, so the algorithm is exponential in input size; knapsack is NP-hard in general."),
            qa("intermediate", "Why iterate capacity downward in the 1-D knapsack?", "Going from high to low capacity means dp[w - wt] still holds the value from before the current item was considered, so each item is used at most once. Iterating upward would let dp[w - wt] already include the current item, giving the unbounded knapsack."),
            qa("advanced", "How does the O(n log n) LIS algorithm work?", "Maintain tails where tails[k] is the smallest possible tail of an increasing subsequence of length k+1. For each x, binary search the first tail >= x and replace it, or append if x is larger than all tails. tails stays sorted and its length is the LIS length."),
            qa("intermediate", "Explain the edit distance recurrence.", "dp[i][j] is the minimum edits to turn a[:i] into b[:j]. If a[i-1] == b[j-1], it equals dp[i-1][j-1]; otherwise 1 plus the minimum of dp[i-1][j] (delete), dp[i][j-1] (insert) and dp[i-1][j-1] (replace). Base cases are dp[i][0] = i and dp[0][j] = j."),
            qa("advanced", "How do LCS and edit distance relate?", "Both align two sequences on an (n+1) x (m+1) grid. If only insertions and deletions are allowed, edit distance equals n + m - 2 * LCS. Allowing substitutions gives Levenshtein distance."),
        ],
        ["dynamic-programming", "binary-search", "strings"],
        chain(
            ("horse -> ros", "6x4 grid", "Setup", "dp[i][0] = i deletions and dp[0][j] = j insertions."),
            ("h vs r", "replace = 1", "Cell (1,1)", "Characters differ: 1 + min(neighbours) = 1.", "row 1"),
            ("o vs o", "diag copy", "Match", "Equal characters copy the diagonal value without cost.", "match"),
            ("fill rows", "row by row", "Propagate", "Each cell uses up, left and diagonal neighbours.", "cells"),
            ("dp[5][3] = 3", "3 edits", "Answer", "horse -> rorse -> rose -> ros.", "result"),
        ),
    ),
    topic(
        "backtracking", "Backtracking", "techniques", "intermediate", "BC",
        "Build candidates incrementally, undo the last choice when it cannot lead to a solution.",
        "Backtracking is solving a maze by marking your path: at each fork you try one corridor, and when you hit a dead end you walk back to the last fork and try the next corridor.",
        "Backtracking explores a decision tree depth-first, building a partial solution one choice at a time. The template is: if the partial solution is complete, record it; otherwise for each valid choice, make it, recurse, and undo it (the 'backtrack' step). Pruning skips choices that cannot lead to a valid or better solution, which is what makes backtracking practical: N-Queens checks column and diagonal conflicts with sets, and combination sum stops when the remaining target is negative. The search space is often exponential: subsets are O(2^n), permutations O(n!), and combinations C(n, k), so complexity is usually expressed as output size times the cost of building each solution. To avoid duplicate results when the input has duplicates, sort first and skip equal siblings at the same depth. Backtracking differs from DP in that subproblems usually do not overlap, so caching does not help much. Constraint satisfaction problems like Sudoku and word search are classic examples.",
        ["Generating subsets, permutations and combinations.", "Constraint puzzles such as N-Queens and Sudoku.", "Word search on grids.", "Combination sum and partitioning problems."],
        [
            "Choose, explore (recurse), un-choose.",
            "Prune early to shrink the search tree.",
            "Subsets O(n * 2^n), permutations O(n * n!).",
            "Sort and skip equal siblings to avoid duplicates.",
            "Copy the path when recording a solution (path[:]).",
        ],
        [
            ex("Subsets and permutations", "basic", "The choose/explore/unchoose template.", "python", """
                def subsets(nums):
                    out, path = [], []
                    def go(i):
                        if i == len(nums):
                            out.append(path[:])
                            return
                        path.append(nums[i]); go(i + 1); path.pop()
                        go(i + 1)
                    go(0)
                    return out

                def permutations(nums):
                    out, path, used = [], [], [False] * len(nums)
                    def go():
                        if len(path) == len(nums):
                            out.append(path[:]); return
                        for i, x in enumerate(nums):
                            if not used[i]:
                                used[i] = True; path.append(x)
                                go()
                                path.pop(); used[i] = False
                    go()
                    return out

                print(subsets([1, 2, 3]))
                print(permutations([1, 2, 3]))
            """),
            ex("N-Queens with pruning", "intermediate", "Sets track attacked columns and diagonals.", "python", """
                def n_queens(n):
                    sols, cols, d1, d2, place = [], set(), set(), set(), []
                    def go(r):
                        if r == n:
                            sols.append(place[:]); return
                        for c in range(n):
                            if c in cols or r - c in d1 or r + c in d2:
                                continue
                            cols.add(c); d1.add(r - c); d2.add(r + c); place.append(c)
                            go(r + 1)
                            cols.remove(c); d1.remove(r - c); d2.remove(r + c); place.pop()
                    go(0)
                    return sols

                sols = n_queens(6)
                print("6-queens solutions:", len(sols))
                for c in sols[0]:
                    print(" ".join("Q" if i == c else "." for i in range(6)))
            """),
            ex("Combination sum without duplicates", "intermediate", "Sort, prune and skip equal siblings.", "python", """
                def combo_sum2(cands, target):
                    cands.sort()
                    out, path = [], []
                    def go(start, remain):
                        if remain == 0:
                            out.append(path[:]); return
                        for i in range(start, len(cands)):
                            if i > start and cands[i] == cands[i - 1]:
                                continue
                            if cands[i] > remain:
                                break
                            path.append(cands[i])
                            go(i + 1, remain - cands[i])
                            path.pop()
                    go(0, target)
                    return out

                print(combo_sum2([10, 1, 2, 7, 6, 1, 5], 8))
            """),
        ],
        ["path.append(x); go(...); path.pop()", "Record copies: out.append(path[:])", "Skip dups: if i > start and a[i] == a[i-1]: continue", "itertools.permutations / combinations", "Subsets 2^n · permutations n!"],
        ["Appending path instead of path[:] stores references that later change.", "Forgetting to undo state (sets, used flags) corrupts sibling branches.", "Without pruning, even n = 15 permutations is far too slow."],
        [
            qa("basic", "What is backtracking?", "A depth-first search over partial solutions: extend the candidate with a choice, recurse, and undo the choice when returning. It systematically enumerates all solutions while abandoning branches that violate constraints."),
            qa("intermediate", "How do you estimate backtracking complexity?", "Count the nodes in the decision tree and multiply by work per node. Subsets give 2^n leaves with O(n) copying, so O(n * 2^n); permutations give n! leaves, O(n * n!). Pruning reduces the practical count but rarely the worst-case bound."),
            qa("intermediate", "How do you avoid duplicate combinations when the input has duplicates?", "Sort the input, and at each recursion level skip a candidate equal to the previous candidate at the same level (i > start and a[i] == a[i-1]). This ensures each distinct value is chosen at most once per position in the tree."),
            qa("intermediate", "Backtracking vs dynamic programming?", "Backtracking enumerates solutions explicitly and suits problems asking for all configurations or with complex constraints. DP aggregates over overlapping subproblems and suits counting or optimisation; if backtracking states repeat, adding memoization turns it into DP."),
        ],
        ["recursion", "dfs", "dynamic-programming", "tries"],
        chain(
            ("[]", "start", "Root", "Begin with an empty subset at index 0."),
            ("take 1", "[1]", "Choose", "Include 1 and recurse to index 1.", "1"),
            ("take 2", "[1,2]", "Deeper", "Include 2, then decide on 3.", "2"),
            ("undo 2", "[1]", "Backtrack", "Pop 2 and explore the branch without it.", "pop"),
            ("8 subsets", "2^3 leaves", "Done", "Every include/exclude path produces one subset.", "leaves"),
        ),
    ),
    topic(
        "bit-manipulation", "Bit Manipulation", "techniques", "intermediate", "BM",
        "Use binary operators to test, set and combine flags and to solve parity and subset problems in O(1) per step.",
        "Bit manipulation is a row of light switches: you can flip one, check one, or compare two whole rows at once, all in a single motion.",
        "Integers are sequences of bits, and operators AND (&), OR (|), XOR (^), NOT (~) and shifts (<<, >>) act on all bits at once. Common tricks: x & 1 tests oddness, x & (x - 1) clears the lowest set bit (so it is zero exactly for powers of two), x & -x isolates the lowest set bit, and 1 << k builds a mask for bit k. XOR is its own inverse and a ^ a = 0, so XOR-ing all elements finds the single non-duplicated number. Bitmasks represent subsets of up to about 20 elements, enabling iteration over all 2^n subsets and bitmask DP (such as travelling salesman in O(2^n * n^2)). Python ints are arbitrary precision, so ~x equals -x - 1 and there is no overflow; use & 0xFFFFFFFF to emulate 32-bit behaviour. int.bit_count() (3.10+) and bin(x).count('1') count set bits, and x.bit_length() gives the position of the highest bit.",
        ["Feature flags and permission masks.", "Finding the unique element or missing number with XOR.", "Enumerating subsets and bitmask DP.", "Low-level protocols, hashing and compression."],
        [
            "Test bit k: (x >> k) & 1; set: x | (1 << k); clear: x & ~(1 << k).",
            "x & (x - 1) clears lowest set bit; power of two if result is 0.",
            "x & -x isolates lowest set bit (Fenwick trees use it).",
            "a ^ a = 0 and a ^ 0 = a: XOR cancels pairs.",
            "Python ints are unbounded; mask with 0xFFFFFFFF for 32-bit.",
        ],
        [
            ex("Bit tricks tour", "basic", "Test, set, clear, count and power-of-two checks.", "python", """
                x = 0b101100
                print("x =", bin(x), "bit 2 set?", (x >> 2) & 1)
                print("set bit 0:", bin(x | 1), "clear bit 3:", bin(x & ~(1 << 3)))
                print("lowest set bit:", bin(x & -x), "clear lowest:", bin(x & (x - 1)))
                print("popcount:", x.bit_count(), "bit_length:", x.bit_length())
                print("powers of two:", [n for n in range(1, 70) if n & (n - 1) == 0])
            """),
            ex("XOR to find the unique and missing numbers", "basic", "Pairs cancel out.", "python", """
                from functools import reduce
                from operator import xor

                nums = [4, 1, 2, 1, 2]
                print("single:", reduce(xor, nums))

                arr = [3, 0, 1, 5, 4]
                n = len(arr)
                missing = reduce(xor, range(n + 1)) ^ reduce(xor, arr)
                print("missing:", missing)
            """),
            ex("Subsets with bitmasks", "intermediate", "Each mask from 0 to 2^n - 1 is a subset.", "python", """
                items = ["a", "b", "c"]
                n = len(items)
                for mask in range(1 << n):
                    subset = [items[i] for i in range(n) if mask >> i & 1]
                    print(f"{mask:03b} -> {subset}")

                def count_bits_dp(n):
                    dp = [0] * (n + 1)
                    for i in range(1, n + 1):
                        dp[i] = dp[i >> 1] + (i & 1)
                    return dp

                print("bit counts 0..8:", count_bits_dp(8))
            """),
        ],
        ["x & 1 (odd) · x >> 1 (halve) · x << 1 (double)", "x & (x - 1) == 0 -> power of two", "x & -x lowest set bit", "x.bit_count() · bin(x).count('1')", "for mask in range(1 << n): subsets"],
        ["Operator precedence: x & 1 == 0 parses as x & (1 == 0); use parentheses.", "~x in Python is -x - 1, not a 32-bit complement.", "Right-shifting negative numbers is arithmetic (sign-preserving) in Python."],
        [
            qa("basic", "How do you check whether a number is a power of two?", "n > 0 and n & (n - 1) == 0. A power of two has exactly one set bit, and subtracting one flips that bit and all lower bits, so the AND is zero."),
            qa("basic", "How do you find the single number when every other appears twice?", "XOR all elements. Since a ^ a = 0 and XOR is commutative and associative, all pairs cancel and the remaining value is the single number. O(n) time and O(1) space."),
            qa("intermediate", "How do you count set bits efficiently?", "Brian Kernighan's method repeats x &= x - 1 until x is zero, looping once per set bit. In Python, int.bit_count() does it natively; hardware offers a POPCNT instruction."),
            qa("intermediate", "What is bitmask DP?", "DP whose state includes a bitmask representing a subset of up to about 20 items, such as dp[mask][i] = shortest path visiting the set mask and ending at i. It turns n! permutations into 2^n * n states, as in the Held-Karp travelling salesman algorithm."),
        ],
        ["tries", "segment-fenwick", "dynamic-programming", "backtracking"],
        chain(
            ("x = 12", "0b1100", "Start", "Binary 1100 has two set bits."),
            ("x - 1", "0b1011", "Subtract", "The lowest set bit flips to 0 and lower bits become 1.", "12"),
            ("x & (x-1)", "0b1000", "Clear lowest", "AND removes the lowest set bit: 8.", "11"),
            ("repeat", "0b0000", "Count", "One more step reaches 0, so 12 has 2 set bits.", "8"),
            ("x & -x", "0b0100", "Isolate", "Two's complement isolates the lowest set bit: 4.", "-12"),
        ),
    ),
    topic(
        "divide-conquer", "Divide & Conquer", "techniques", "intermediate", "DC",
        "Split a problem into independent subproblems, solve them recursively, and combine the results.",
        "Divide and conquer is how a general takes a city: split the army, capture each district separately, then unite the districts into one victory.",
        "Divide and conquer breaks a problem into smaller independent subproblems of the same type, solves each recursively, and combines their answers. Merge sort, quicksort, binary search, quickselect, Karatsuba multiplication, Strassen matrix multiplication and the closest pair of points are classic examples. Running time follows a recurrence T(n) = aT(n/b) + f(n), solved by the Master theorem: binary search is T(n/2) + O(1) = O(log n), merge sort 2T(n/2) + O(n) = O(n log n), and Karatsuba 3T(n/2) + O(n) = O(n^1.585). The key difference from dynamic programming is that subproblems do not overlap; if they did, memoisation would turn it into DP. Fast exponentiation computes x^n in O(log n) by squaring. Maximum subarray can be solved by divide and conquer in O(n log n), though Kadane's algorithm is O(n). Independent subproblems also make divide and conquer naturally parallel.",
        ["Sorting (merge sort, quicksort).", "Fast exponentiation and modular power.", "Large integer and matrix multiplication.", "Parallel processing via map-reduce style splits."],
        [
            "Divide, conquer recursively, combine.",
            "T(n) = aT(n/b) + f(n); use the Master theorem.",
            "Subproblems are independent (unlike DP).",
            "Fast power: x^n = (x^(n/2))^2, O(log n).",
            "Naturally parallelisable.",
        ],
        [
            ex("Fast exponentiation", "basic", "Recursive squaring with a call count.", "python", """
                calls = 0
                def power(x, n):
                    global calls
                    calls += 1
                    if n == 0:
                        return 1
                    half = power(x, n // 2)
                    return half * half * (x if n % 2 else 1)

                print(power(3, 13), 3 ** 13, "calls:", calls)
                print("built-in modular pow:", pow(7, 10**18, 1_000_000_007))
            """),
            ex("Maximum subarray by divide and conquer", "intermediate", "Best of left, right and crossing.", "python", """
                def max_sub(a, lo, hi):
                    if lo == hi:
                        return a[lo]
                    mid = (lo + hi) // 2
                    best_left = s = float("-inf"); total = 0
                    for i in range(mid, lo - 1, -1):
                        total += a[i]; best_left = max(best_left, total)
                    best_right = float("-inf"); total = 0
                    for i in range(mid + 1, hi + 1):
                        total += a[i]; best_right = max(best_right, total)
                    return max(max_sub(a, lo, mid), max_sub(a, mid + 1, hi), best_left + best_right)

                def kadane(a):
                    best = cur = a[0]
                    for x in a[1:]:
                        cur = max(x, cur + x)
                        best = max(best, cur)
                    return best

                arr = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
                print("divide and conquer:", max_sub(arr, 0, len(arr) - 1), "kadane:", kadane(arr))
            """),
            ex("Karatsuba multiplication", "advanced", "Three recursive multiplications instead of four.", "python", """
                def karatsuba(x, y):
                    if x < 10 or y < 10:
                        return x * y
                    m = max(len(str(x)), len(str(y))) // 2
                    p = 10 ** m
                    a, b = divmod(x, p)
                    c, d = divmod(y, p)
                    ac, bd = karatsuba(a, c), karatsuba(b, d)
                    mid = karatsuba(a + b, c + d) - ac - bd
                    return ac * p * p + mid * p + bd

                x, y = 12345678, 87654321
                print(karatsuba(x, y), x * y, karatsuba(x, y) == x * y)
            """),
        ],
        ["T(n)=T(n/2)+O(1) -> O(log n)", "T(n)=2T(n/2)+O(n) -> O(n log n)", "T(n)=3T(n/2)+O(n) -> O(n^1.585)", "pow(base, exp, mod) O(log exp)", "Overlapping subproblems -> use DP instead"],
        ["Base cases that do not shrink the problem cause infinite recursion.", "The combine step's cost often dominates; analyse it carefully.", "Overhead of recursion makes it slower than iteration for tiny inputs."],
        [
            qa("basic", "What are the three steps of divide and conquer?", "Divide the problem into smaller subproblems, conquer each recursively (solving tiny ones directly), and combine the sub-results into the answer. Merge sort divides in half, sorts each half and merges."),
            qa("intermediate", "How does divide and conquer differ from dynamic programming?", "Divide and conquer subproblems are independent, so each is solved once naturally. DP is used when subproblems overlap and would be recomputed many times, so results are cached or tabulated."),
            qa("intermediate", "How does fast exponentiation work?", "x^n = (x^(n/2))^2 for even n and x * x^(n-1) for odd n, so the exponent halves each step, needing O(log n) multiplications. Python's pow(x, n, m) does this with modular reduction, which is essential in cryptography."),
            qa("advanced", "Why is Karatsuba faster than schoolbook multiplication?", "Schoolbook multiplication of two n-digit numbers splits into four half-size products, T(n) = 4T(n/2) + O(n) = O(n^2). Karatsuba computes (a+b)(c+d) - ac - bd to get the middle term, needing only three products: T(n) = 3T(n/2) + O(n) = O(n^log2(3)), about n^1.585."),
        ],
        ["merge-sort", "quick-sort", "binary-search", "recursion"],
        chain(
            ("3^13", "n = 13", "Problem", "Compute 3 to the 13th power."),
            ("divide", "3^6", "Halve", "13 is odd: 3^13 = 3 * (3^6)^2.", "n//2"),
            ("recurse", "3^3, 3^1, 3^0", "Conquer", "Each call halves n until the base case 3^0 = 1.", "n//2"),
            ("combine", "square up", "Combine", "Square results on the way back, multiplying by 3 for odd n.", "half"),
            ("1594323", "5 calls", "Result", "O(log n) multiplications instead of 12.", "done"),
        ),
    ),
    topic(
        "monotonic-stack", "Monotonic Stack", "techniques", "intermediate", "MO",
        "Keep a stack in increasing or decreasing order to find next greater or smaller elements in O(n).",
        "A monotonic stack is a queue of people where anyone shorter than a newcomer leaves in frustration because they can no longer see the stage. Each person who leaves learns exactly who blocked them.",
        "A monotonic stack holds indices whose values are kept in sorted order (strictly decreasing for 'next greater', increasing for 'next smaller'). For each new element, pop all stack entries that it beats; for each popped index, the current element is its next greater (or smaller) element. Then push the current index. Each index is pushed and popped at most once, so the whole pass is O(n) time and O(n) space, replacing an O(n^2) nested scan. Classic problems include next greater element, daily temperatures, stock span, largest rectangle in a histogram, trapping rain water and sum of subarray minimums. For circular arrays, iterate twice over the indices modulo n. Choosing strict versus non-strict comparison controls how ties are handled, which matters when counting subarrays to avoid double counting.",
        ["Next greater or smaller element queries.", "Daily temperatures and stock span.", "Largest rectangle in a histogram.", "Trapping rain water and subarray minimum sums."],
        [
            "Store indices, not values, to compute distances.",
            "Decreasing stack -> next greater; increasing stack -> next smaller.",
            "Each element pushed and popped once: O(n).",
            "Circular arrays: loop 2n with i % n.",
            "Use strict vs non-strict comparisons deliberately for ties.",
        ],
        [
            ex("Next greater element and daily temperatures", "basic", "Pop smaller items when a bigger one arrives.", "python", """
                def next_greater(nums):
                    res, st = [-1] * len(nums), []
                    for i, x in enumerate(nums):
                        while st and nums[st[-1]] < x:
                            res[st.pop()] = x
                        st.append(i)
                        print(f"i={i} x={x} stack(values)={[nums[j] for j in st]}")
                    return res

                def daily_temperatures(t):
                    res, st = [0] * len(t), []
                    for i, x in enumerate(t):
                        while st and t[st[-1]] < x:
                            j = st.pop()
                            res[j] = i - j
                        st.append(i)
                    return res

                print(next_greater([2, 1, 2, 4, 3]))
                print(daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73]))
            """),
            ex("Largest rectangle in histogram", "advanced", "Increasing stack; pop computes the width.", "python", """
                def largest_rectangle(h):
                    st, best = [], 0
                    for i, x in enumerate(h + [0]):
                        while st and h[st[-1]] >= x:
                            height = h[st.pop()]
                            left = st[-1] + 1 if st else 0
                            best = max(best, height * (i - left))
                        st.append(i)
                    return best

                print(largest_rectangle([2, 1, 5, 6, 2, 3]))
                print(largest_rectangle([2, 4]))
            """),
            ex("Trapping rain water", "intermediate", "Water fills between walls popped from the stack.", "python", """
                def trap(h):
                    st, water = [], 0
                    for i, x in enumerate(h):
                        while st and h[st[-1]] < x:
                            bottom = st.pop()
                            if not st:
                                break
                            left = st[-1]
                            width = i - left - 1
                            water += width * (min(h[left], x) - h[bottom])
                        st.append(i)
                    return water

                print(trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]))
            """),
        ],
        ["while st and a[st[-1]] < x: res[st.pop()] = x", "st.append(i)  (store indices)", "O(n) time, O(n) space", "Append sentinel 0 to flush the stack", "Circular: for i in range(2 * n): x = a[i % n]"],
        ["Storing values instead of indices loses position information.", "Forgetting to flush remaining stack items (they have no next greater).", "Wrong tie comparison double counts in subarray-min problems."],
        [
            qa("intermediate", "What is a monotonic stack?", "A stack whose elements are kept in increasing or decreasing order by popping any elements that would violate the order before pushing. The pops reveal relationships like 'the first element to my right that is larger than me'."),
            qa("intermediate", "Why is the monotonic stack approach O(n)?", "Every index is pushed exactly once and popped at most once, so the total number of stack operations is at most 2n, even though there is a while loop inside the for loop."),
            qa("advanced", "How do you find the largest rectangle in a histogram?", "Maintain an increasing stack of bar indices. When a lower bar arrives, pop taller bars; for each popped bar, its rectangle extends from just after the new stack top to just before the current index. Appending a zero-height sentinel flushes the stack at the end, all in O(n)."),
            qa("intermediate", "How do you handle a circular array for next greater element?", "Iterate i from 0 to 2n - 1 using nums[i % n], but only push indices during the first pass. Elements near the end can then find their next greater element at the start of the array."),
        ],
        ["stacks", "queues-deques", "two-pointers", "sliding-window"],
        chain(
            ("[2,1,2,4,3]", "empty stack", "Start", "Find each element's next greater value."),
            ("push 2, 1", "stack [2,1]", "Decreasing", "1 is smaller than 2, so both wait.", "2,1"),
            ("x = 2", "pop 1 -> 2", "Resolve", "2 beats 1: next greater of 1 is 2. Push 2.", "2"),
            ("x = 4", "pop 2, 2 -> 4", "Resolve", "4 beats both 2s: their answer is 4.", "4"),
            ("x = 3", "end: 4,3 -> -1", "Flush", "Remaining items have no greater element: [4,2,4,-1,-1].", "3"),
        ),
    ),
    topic(
        "intervals", "Interval Problems", "techniques", "intermediate", "IN",
        "Sort intervals by start or end, then sweep to merge, insert, count overlaps or schedule.",
        "Interval problems are like managing a meeting room calendar: lay all bookings on a timeline in order, then a single pass shows which overlap and how many rooms you need.",
        "Interval problems involve ranges [start, end] and almost always begin by sorting. Merging overlapping intervals sorts by start and extends the last merged interval while the next start is at most its end, O(n log n). Inserting an interval into a sorted list copies intervals ending before it, merges those overlapping it, then copies the rest. The minimum number of meeting rooms equals the maximum number of simultaneous intervals, found with a min-heap of end times or a sweep line over +1 and -1 events. Sorting by end time and greedily picking non-overlapping intervals maximises the count kept (equivalently minimises removals). Interval intersection of two sorted lists uses two pointers. Be explicit about whether endpoints are inclusive: whether [1, 2] and [2, 3] overlap depends on the problem, and it changes the comparison from <= to <.",
        ["Calendar and meeting room scheduling.", "Merging time ranges in logs or reservations.", "Resource allocation and CPU scheduling.", "Genomic ranges and IP range consolidation."],
        [
            "Sort by start to merge; by end to select max non-overlapping.",
            "Overlap test: a.start <= b.end and b.start <= a.end (inclusive).",
            "Meeting rooms: heap of end times or sweep line events.",
            "Two sorted lists: two-pointer intersection.",
            "Clarify inclusive vs exclusive endpoints.",
        ],
        [
            ex("Merge intervals", "basic", "Sort by start and extend.", "python", """
                def merge(intervals):
                    out = []
                    for s, e in sorted(intervals):
                        if out and s <= out[-1][1]:
                            out[-1][1] = max(out[-1][1], e)
                        else:
                            out.append([s, e])
                        print(f"[{s},{e}] -> {out}")
                    return out

                print(merge([[1, 3], [8, 10], [2, 6], [15, 18], [9, 12]]))
            """),
            ex("Meeting rooms with a heap and sweep line", "intermediate", "Two ways to count max overlap.", "python", """
                import heapq

                def rooms_heap(meetings):
                    ends = []
                    for s, e in sorted(meetings):
                        if ends and ends[0] <= s:
                            heapq.heapreplace(ends, e)
                        else:
                            heapq.heappush(ends, e)
                    return len(ends)

                def rooms_sweep(meetings):
                    events = sorted([(s, 1) for s, _ in meetings] + [(e, -1) for _, e in meetings])
                    cur = best = 0
                    for _, d in events:
                        cur += d
                        best = max(best, cur)
                    return best

                m = [(0, 30), (5, 10), (15, 20), (10, 15), (25, 35)]
                print(rooms_heap(m), rooms_sweep(m))
            """),
            ex("Insert interval and intersections", "intermediate", "Linear passes over sorted lists.", "python", """
                def insert(intervals, new):
                    out, i, n = [], 0, len(intervals)
                    while i < n and intervals[i][1] < new[0]:
                        out.append(intervals[i]); i += 1
                    s, e = new
                    while i < n and intervals[i][0] <= e:
                        s, e = min(s, intervals[i][0]), max(e, intervals[i][1]); i += 1
                    out.append([s, e])
                    return out + intervals[i:]

                def intersect(a, b):
                    i = j = 0
                    out = []
                    while i < len(a) and j < len(b):
                        lo, hi = max(a[i][0], b[j][0]), min(a[i][1], b[j][1])
                        if lo <= hi:
                            out.append([lo, hi])
                        if a[i][1] < b[j][1]:
                            i += 1
                        else:
                            j += 1
                    return out

                print(insert([[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8]))
                print(intersect([[0, 2], [5, 10], [13, 23]], [[1, 5], [8, 12], [15, 24]]))
            """),
        ],
        ["intervals.sort(key=lambda x: x[0])", "Merge: if s <= last_end: extend", "Rooms: heapq of end times", "Sweep: (+1 at start, -1 at end), sort", "Overlap: max(starts) <= min(ends)"],
        ["Sweep ties: decide whether an end at t frees a room for a start at t (sort -1 before +1).", "Mutating input lists while merging can surprise callers.", "Sorting by start for 'max non-overlapping' gives wrong answers; sort by end."],
        [
            qa("basic", "How do you merge overlapping intervals?", "Sort by start time, then iterate: if the current interval starts at or before the last merged interval's end, extend that end to the maximum; otherwise append it as a new interval. O(n log n) for sorting plus O(n) for the pass."),
            qa("intermediate", "How do you find the minimum number of meeting rooms?", "Sort meetings by start and keep a min-heap of end times of ongoing meetings. For each meeting, if the earliest end is at or before its start, reuse that room (pop), then push its end. The heap's maximum size is the answer, O(n log n)."),
            qa("intermediate", "How do you remove the fewest intervals to make the rest non-overlapping?", "Sort by end time and greedily keep each interval whose start is at least the last kept end, counting the others as removals. Keeping the earliest-ending interval leaves the most room, which an exchange argument proves optimal."),
            qa("intermediate", "What is a sweep line?", "Convert intervals into events (start = +1, end = -1), sort events by time with a tie rule, and scan while maintaining a running count. The maximum count is the peak overlap. It generalises to skyline and rectangle area problems."),
        ],
        ["greedy", "heaps", "two-pointers", "timsort-stability"],
        chain(
            ("3 intervals", "[1,3],[8,10],[2,6]", "Input", "Overlaps are hidden by ordering."),
            ("sort by start", "[1,3],[2,6],[8,10]", "Sort", "Overlapping intervals become adjacent.", "sort"),
            ("[2,6]", "2 <= 3", "Extend", "Overlaps [1,3], so the merged interval becomes [1,6].", "[1,3]"),
            ("[8,10]", "8 > 6", "New", "No overlap; start a new merged interval.", "[1,6]"),
            ("result", "[1,6],[8,10]", "Done", "O(n log n) dominated by sorting.", "merged"),
        ),
    ),
    topic(
        "string-algorithms", "String Algorithms: KMP & Rolling Hash", "techniques", "advanced", "KM",
        "Find patterns in text in linear time using a failure function or a rolling hash.",
        "KMP is reading a long line of text while remembering how much of the search word you have already matched, so a mismatch never makes you reread the text. A rolling hash is a fingerprint you update one letter at a time as a window slides.",
        "Naive substring search compares the pattern at every position and costs O(n*m) in the worst case. The Knuth-Morris-Pratt (KMP) algorithm precomputes, for each prefix of the pattern, the length of the longest proper prefix that is also a suffix (the failure or LPS array). On a mismatch it falls back to that length instead of restarting, so the text pointer never moves backwards and the total time is O(n + m). The Rabin-Karp algorithm computes a polynomial hash of the pattern and of each text window, updating the window hash in O(1) as it slides (rolling hash); equal hashes are verified by direct comparison to rule out collisions, giving expected O(n + m). Rolling hashes also find repeated substrings, longest duplicate substring with binary search, and plagiarism fingerprints. The Z-algorithm computes, for each position, the longest substring starting there that matches a prefix, also in O(n). For integrity checks, cryptographic hashes like hashlib.sha256 are used instead of polynomial hashes, which are fast but not collision-resistant against adversaries.",
        ["Text editors' find feature and grep-like tools.", "DNA sequence matching.", "Plagiarism and duplicate detection via fingerprints.", "Finding repeated or periodic substrings."],
        [
            "KMP: LPS array + no backtracking in the text, O(n + m).",
            "LPS[i] = longest proper prefix of p[:i+1] that is also its suffix.",
            "Rabin-Karp: rolling hash, verify on hash match; expected O(n + m).",
            "Use a large prime modulus to reduce collisions.",
            "Polynomial hashes are not cryptographic; use sha256 for integrity.",
        ],
        [
            ex("KMP with LPS table", "intermediate", "Build the failure function and search.", "python", """
                def build_lps(p):
                    lps, k = [0] * len(p), 0
                    for i in range(1, len(p)):
                        while k and p[i] != p[k]:
                            k = lps[k - 1]
                        if p[i] == p[k]:
                            k += 1
                        lps[i] = k
                    return lps

                def kmp_search(text, p):
                    lps, k, hits = build_lps(p), 0, []
                    for i, c in enumerate(text):
                        while k and c != p[k]:
                            k = lps[k - 1]
                        if c == p[k]:
                            k += 1
                        if k == len(p):
                            hits.append(i - k + 1)
                            k = lps[k - 1]
                    return hits

                print("LPS of ababaca:", build_lps("ababaca"))
                print("matches:", kmp_search("abababacabababaca", "ababaca"))
            """),
            ex("Rabin-Karp rolling hash", "intermediate", "Slide a window hash and verify matches.", "python", """
                def rabin_karp(text, p, base=256, mod=1_000_000_007):
                    n, m = len(text), len(p)
                    if m > n:
                        return []
                    high = pow(base, m - 1, mod)
                    hp = ht = 0
                    for i in range(m):
                        hp = (hp * base + ord(p[i])) % mod
                        ht = (ht * base + ord(text[i])) % mod
                    hits = []
                    for i in range(n - m + 1):
                        if hp == ht and text[i:i + m] == p:
                            hits.append(i)
                        if i + m < n:
                            ht = ((ht - ord(text[i]) * high) * base + ord(text[i + m])) % mod
                    return hits

                print(rabin_karp("the cat sat on the mat with a cat", "cat"))
                print(rabin_karp("aaaaa", "aa"))
            """),
            ex("Z-algorithm and secure fingerprints", "advanced", "Prefix-match lengths, plus sha256 for integrity.", "python", """
                import hashlib

                def z_array(s):
                    z, l, r = [0] * len(s), 0, 0
                    for i in range(1, len(s)):
                        if i < r:
                            z[i] = min(r - i, z[i - l])
                        while i + z[i] < len(s) and s[z[i]] == s[i + z[i]]:
                            z[i] += 1
                        if i + z[i] > r:
                            l, r = i, i + z[i]
                    return z

                p, t = "aab", "baabaa"
                s = p + "#" + t
                z = z_array(s)
                print("z:", z)
                print("matches:", [i - len(p) - 1 for i in range(len(s)) if z[i] == len(p)])
                print("sha256 fingerprint:", hashlib.sha256(t.encode()).hexdigest()[:16])
            """),
        ],
        ["KMP O(n + m) · naive O(n * m)", "lps: while k and p[i] != p[k]: k = lps[k-1]", "Roll: h = ((h - c_out * B^(m-1)) * B + c_in) % MOD", "pow(base, m - 1, mod)", "str.find(p) for everyday use"],
        ["Skipping verification after a hash match reports false positives on collisions.", "Negative intermediate values when subtracting in modular arithmetic (Python % handles it).", "Off-by-one when falling back with lps[k - 1]."],
        [
            qa("intermediate", "Why is KMP linear?", "The text index only moves forward. On a mismatch, the pattern index falls back via the LPS array, and each fallback undoes progress previously gained by a match, so total fallbacks are bounded by total matches, at most n. Building the LPS table similarly costs O(m)."),
            qa("intermediate", "What does the LPS array represent?", "LPS[i] is the length of the longest proper prefix of pattern[:i+1] that is also a suffix of it. After matching i+1 characters and then mismatching, we know the last LPS[i] text characters already match the pattern's prefix, so we resume from there."),
            qa("intermediate", "How does Rabin-Karp work and what is its worst case?", "It hashes the pattern and each length-m window of the text with a polynomial rolling hash, updating the window hash in O(1). Matching hashes are verified character by character. Expected time is O(n + m), but many collisions (adversarial input or a weak modulus) degrade it to O(n * m)."),
            qa("advanced", "Can a rolling hash replace a cryptographic hash?", "No. Polynomial rolling hashes are designed for speed and are easy to collide deliberately. For integrity, signatures or deduplication against adversaries, use SHA-256 or BLAKE2; rolling hashes are suitable only for algorithmic search with verification."),
        ],
        ["strings", "hash-tables", "sliding-window"],
        chain(
            ("p = abab", "lps [0,0,1,2]", "Preprocess", "Compute the failure function of the pattern in O(m)."),
            ("text abaab", "match aba", "Scan", "Matching the first three characters sets k = 3.", "k=0"),
            ("mismatch", "k = lps[2] = 1", "Fall back", "Text 'a' vs pattern 'b' fails; reuse the matched 'a' prefix.", "k=3"),
            ("continue", "no text rewind", "Resume", "Compare the same text character with p[1]; the text pointer never moves back.", "k=1"),
            ("O(n + m)", "linear", "Result", "Every text character is processed with amortised O(1) work.", "done"),
        ),
    ),
    topic(
        "problem-solving-framework", "Interview Problem-Solving Framework", "techniques", "basic", "PF",
        "A repeatable process: clarify, examples, brute force, optimise with patterns, code, test, analyse.",
        "Solving an interview problem is like a doctor's visit: ask questions before prescribing, examine simple cases, propose a safe treatment, then refine it, and finally check the patient actually got better.",
        "Strong interview performance comes from a consistent process rather than memorised answers. First clarify inputs, outputs, constraints and edge cases (empty input, duplicates, negatives, size limits), because constraints hint at the target complexity: n up to 10^5 suggests O(n log n) or better, and n up to 20 allows O(2^n). Work through a small example by hand, then state a brute-force solution and its complexity to establish correctness. Optimise by spotting patterns: sorted input suggests binary search or two pointers, contiguous ranges suggest sliding window or prefix sums, 'top k' suggests a heap, dependencies suggest graphs, and 'number of ways' or 'min cost' with overlap suggests DP. Then write clean code with meaningful names, talking through your reasoning. Finally test with the example and edge cases, fix bugs, and state the time and space complexity. Communicating trade-offs is as important as reaching the optimal solution.",
        ["Coding interviews at any level.", "Approaching unfamiliar competitive programming problems.", "Structuring technical design discussions.", "Teaching and mentoring problem solving."],
        [
            "Clarify constraints first; they imply the target complexity.",
            "Brute force first, then optimise.",
            "Map problem signals to patterns.",
            "Narrate while coding; keep functions small.",
            "Test edge cases and state time/space complexity.",
        ],
        [
            ex("Brute force to optimal: pair with target sum", "basic", "O(n^2) -> O(n log n) -> O(n) with checks.", "python", """
                def brute(nums, t):
                    for i in range(len(nums)):
                        for j in range(i + 1, len(nums)):
                            if nums[i] + nums[j] == t:
                                return True
                    return False

                def sorted_two_pointers(nums, t):
                    a = sorted(nums)
                    i, j = 0, len(a) - 1
                    while i < j:
                        s = a[i] + a[j]
                        if s == t:
                            return True
                        i, j = (i + 1, j) if s < t else (i, j - 1)
                    return False

                def hashing(nums, t):
                    seen = set()
                    for x in nums:
                        if t - x in seen:
                            return True
                        seen.add(x)
                    return False

                cases = [([3, 8, 1, 5], 9, True), ([1, 2], 4, False), ([], 0, False), ([5, 5], 10, True), ([-2, 7], 5, True)]
                for nums, t, want in cases:
                    got = (brute(nums, t), sorted_two_pointers(nums, t), hashing(nums, t))
                    assert got == (want,) * 3, (nums, t, got)
                print("all approaches agree on", len(cases), "cases including edge cases")
            """),
            ex("Constraint to complexity cheat sheet", "basic", "Rough operation budgets for about one second.", "python", """
                import math

                budget = 10**8
                for n in (20, 500, 5000, 10**5, 10**6):
                    options = []
                    for name, f in [("2^n", lambda n: 2 ** n if n < 64 else float("inf")), ("n^3", lambda n: n ** 3),
                                    ("n^2", lambda n: n ** 2), ("n log n", lambda n: n * math.log2(n)), ("n", lambda n: n)]:
                        if f(n) <= budget:
                            options.append(name)
                    print(f"n={n:>8}: feasible -> {', '.join(options)}")
            """),
            ex("Randomised testing against brute force", "intermediate", "Catch bugs in an optimised solution quickly.", "python", """
                import random

                def max_subarray_fast(a):
                    best = cur = a[0]
                    for x in a[1:]:
                        cur = max(x, cur + x)
                        best = max(best, cur)
                    return best

                def max_subarray_brute(a):
                    return max(sum(a[i:j + 1]) for i in range(len(a)) for j in range(i, len(a)))

                random.seed(42)
                for _ in range(300):
                    arr = [random.randint(-10, 10) for _ in range(random.randint(1, 8))]
                    assert max_subarray_fast(arr) == max_subarray_brute(arr), arr
                print("300 random tests passed")
            """),
        ],
        ["n <= 20 -> 2^n · n <= 500 -> n^3 · n <= 5000 -> n^2", "n <= 10^6 -> n log n or n", "Sorted -> binary search / two pointers", "Top k -> heap · ranges -> prefix sums / window", "Ways / min cost with overlap -> DP"],
        ["Jumping into code before clarifying constraints and edge cases.", "Going silent; interviewers grade communication too.", "Claiming complexity without accounting for sorting, slicing or hashing costs.", "Not testing your code on the example before declaring it done."],
        [
            qa("basic", "What should you do in the first few minutes of a coding interview?", "Restate the problem, ask about input size, value ranges, duplicates, empty inputs and expected output format, and work through a small example. This avoids solving the wrong problem and reveals the target complexity."),
            qa("basic", "Why start with a brute-force solution?", "It proves you understand the problem, gives a correct baseline to test against, and its bottleneck often points to the optimisation (for example, a repeated inner search suggests a hash map). Mention its complexity, then improve."),
            qa("intermediate", "How do constraints hint at the algorithm?", "At roughly 10^8 simple operations per second: n <= 20 allows exponential search, n <= 500 allows O(n^3), n <= 5000 allows O(n^2), and n up to 10^5-10^6 needs O(n log n) or O(n). Very large values with small n suggest binary search on the answer."),
            qa("intermediate", "How do you test your solution during an interview?", "Trace the provided example by hand through your code, then try edge cases: empty or single-element input, all equal values, negatives, maximum sizes and already sorted or reversed input. Fix bugs calmly and explain the fix."),
            qa("advanced", "What do you do if you are stuck?", "Simplify: solve a smaller or constrained version, try more examples, think about which data structure would make the slow step fast, or consider standard patterns one by one. Share your thinking so the interviewer can give hints."),
        ],
        ["big-o", "two-pointers", "dynamic-programming", "hash-tables"],
        chain(
            ("Clarify", "inputs, limits", "Understand", "Ask about sizes, ranges, duplicates and edge cases."),
            ("Example", "by hand", "Explore", "Solve a small case manually to see the structure.", "constraints"),
            ("Brute force", "state O()", "Baseline", "Give a correct simple solution and its complexity.", "insight"),
            ("Optimise", "pick a pattern", "Improve", "Remove the bottleneck with a hash map, two pointers, heap, DP and so on.", "bottleneck"),
            ("Code + test", "edge cases", "Deliver", "Write clean code, trace the example, test edge cases, state final complexity.", "plan"),
        ),
    ),
]

SCENARIOS = [
    {"level": "basic", "topic": "insertion-sort", "q": "Your hand-written sort is O(n^2) even on already sorted input. Why, and which simple sort would fix it?",
     "a": "Selection sort, and bubble sort without an early-exit flag, always perform n(n-1)/2 comparisons regardless of order. Insertion sort is adaptive: on sorted input each element needs one comparison, giving O(n). Adding a 'no swaps this pass' flag also makes bubble sort O(n) in that case, and Python's built-in Timsort is O(n) on sorted data."},
    {"level": "intermediate", "topic": "quick-sort", "q": "A quicksort implementation becomes extremely slow and hits recursion limits when users upload pre-sorted files. What is happening?",
     "a": "It probably uses the first or last element as the pivot, so on sorted input every partition splits into sizes n-1 and 0. That gives O(n^2) time and O(n) recursion depth. Use a random or median-of-three pivot, recurse on the smaller side first and loop on the larger, or switch to introsort, which falls back to heap sort when depth exceeds about 2 log n."},
    {"level": "intermediate", "topic": "timsort-stability", "q": "You sort orders by date, then sort the result by customer, and the per-customer date order is preserved in Python but not in another language. Why?",
     "a": "Python's sort (Timsort) is stable, so sorting by customer keeps the earlier date order among equal customers. The other language's default sort may be an unstable quicksort or heap sort, for example C++ std::sort. Use a stable sort (std::stable_sort), or sort once with a composite key (customer, date)."},
    {"level": "intermediate", "topic": "hash-tables", "q": "An API that deduplicates user-supplied strings suddenly takes seconds per request under attack, even though dict lookups are O(1). What could explain it?",
     "a": "An attacker may be sending keys crafted to collide in the hash table, degrading operations to O(n) each and the request to O(n^2) (hash flooding). Python randomises str hashes to mitigate this, but custom __hash__ implementations or other languages may be vulnerable. Use randomised or keyed hashes, cap input sizes, and rate-limit requests."},
    {"level": "intermediate", "topic": "bfs", "q": "A grid shortest-path service occasionally runs out of memory and is slow, though the logic finds correct paths. The code marks cells visited when they are dequeued. What is wrong?",
     "a": "Marking visited on dequeue lets the same cell be enqueued many times by different neighbours before it is processed, blowing up the queue. Mark cells visited when they are enqueued so each enters the queue once, restoring O(V + E) time and O(V) memory. Also make sure the queue is a deque, not a list with pop(0)."},
    {"level": "advanced", "topic": "dijkstra", "q": "Your route planner returns a more expensive path after you added 'cashback' edges with negative cost. Why, and what should you use?",
     "a": "Dijkstra assumes non-negative weights: once a node is popped its distance is final, so a later negative edge that would lower it is ignored. Use Bellman-Ford (O(VE)), which also detects negative cycles, or reweight with Johnson's algorithm if you need repeated queries. Alternatively model cashback outside the graph so edge weights stay non-negative."},
    {"level": "intermediate", "topic": "dynamic-programming", "q": "A memoised recursive solution passes small tests but raises RecursionError for n = 50,000. How do you fix it without changing the algorithm's complexity?",
     "a": "Python's recursion limit (about 1000 frames) is exceeded because memoisation does not reduce depth. Convert to bottom-up tabulation, filling dp in dependency order with a loop, which uses no call stack and often allows a rolling array for O(1) or O(k) space. Raising sys.setrecursionlimit is a fragile workaround that can crash the interpreter."},
    {"level": "basic", "topic": "big-o", "q": "A function that removes duplicates by checking 'if x not in result' before appending is fast in tests but times out on 10^5 items. Why?",
     "a": "'x in list' is a linear scan, so the loop is O(n^2) overall, around 10^10 operations at n = 10^5 in the worst case. Track seen items in a set for O(1) average membership, making the whole pass O(n); dict.fromkeys(items) also deduplicates while preserving order."},
]
