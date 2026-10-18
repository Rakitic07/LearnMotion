export const WORDS = [
  { answer: "ARRAY", term: "Array", clue: "Contiguous block of elements with O(1) access by index" },
  { answer: "LINKEDLIST", term: "Linked list", clue: "Nodes joined by pointers; O(1) insert at a known node, O(n) access by index" },
  { answer: "STACK", term: "Stack", clue: "Last in, first out; push and pop at the same end" },
  { answer: "QUEUE", term: "Queue", clue: "First in, first out; the structure behind BFS" },
  { answer: "DEQUE", term: "Deque", clue: "Double-ended queue with O(1) push and pop at both ends" },
  { answer: "HEAP", term: "Heap", clue: "Complete binary tree where every parent beats its children; backs a priority queue" },
  { answer: "HASHTABLE", term: "Hash table", clue: "Maps keys to buckets for average O(1) lookup" },
  { answer: "COLLISION", term: "Collision", clue: "Two different keys landing in the same hash bucket" },
  { answer: "TRIE", term: "Trie", clue: "Prefix tree that stores strings one character per level" },
  { answer: "BST", term: "Binary search tree", clue: "Tree where left subtree < node < right subtree" },
  { answer: "GRAPH", term: "Graph", clue: "Vertices connected by edges, directed or undirected" },
  { answer: "BFS", term: "Breadth-first search", clue: "Explores level by level with a queue; finds shortest paths in unweighted graphs" },
  { answer: "DFS", term: "Depth-first search", clue: "Goes as deep as possible before backtracking, using a stack or recursion" },
  { answer: "DIJKSTRA", term: "Dijkstra's algorithm", clue: "Shortest paths with non-negative weights using a priority queue" },
  { answer: "TOPOLOGICAL", term: "Topological sort", clue: "Orders a DAG so every edge points forward" },
  { answer: "UNIONFIND", term: "Union-find", clue: "Disjoint-set structure with path compression; detects cycles in Kruskal" },
  { answer: "RECURSION", term: "Recursion", clue: "A function solving a problem by calling itself on smaller inputs" },
  { answer: "MEMOIZATION", term: "Memoization", clue: "Caching results of recursive calls so each subproblem is solved once" },
  { answer: "TABULATION", term: "Tabulation", clue: "Bottom-up dynamic programming that fills a table in order" },
  { answer: "GREEDY", term: "Greedy algorithm", clue: "Takes the locally best choice at each step and never looks back" },
  { answer: "BACKTRACKING", term: "Backtracking", clue: "Builds candidates step by step and abandons a branch as soon as it fails" },
  { answer: "BINARYSEARCH", term: "Binary search", clue: "Halves a sorted range each step to find a target in O(log n)" },
  { answer: "TWOPOINTERS", term: "Two pointers", clue: "Two indices moving through a sorted array, often from both ends" },
  { answer: "SLIDINGWINDOW", term: "Sliding window", clue: "Keeps a running range over a sequence, adding on the right and dropping on the left" },
  { answer: "PREFIXSUM", term: "Prefix sum", clue: "Running totals that answer any range-sum query in O(1)" },
  { answer: "PIVOT", term: "Pivot", clue: "Element quicksort partitions around" },
  { answer: "PARTITION", term: "Partition", clue: "Quicksort step that moves smaller items left of the pivot and larger right" },
  { answer: "MERGESORT", term: "Merge sort", clue: "Stable divide-and-conquer sort with guaranteed O(n log n) and O(n) extra space" },
  { answer: "QUICKSORT", term: "Quicksort", clue: "In-place sort, O(n log n) on average but O(n squared) with bad pivots" },
  { answer: "HEAPSORT", term: "Heap sort", clue: "In-place O(n log n) sort that repeatedly moves the max of a heap to the back" },
  { answer: "STABLE", term: "Stable sort", clue: "Keeps equal elements in their original relative order" },
  { answer: "INPLACE", term: "In-place", clue: "Uses only O(1) or O(log n) extra memory beyond the input" },
  { answer: "AMORTIZED", term: "Amortized cost", clue: "Average cost per operation over a sequence, like O(1) list append despite resizes" },
  { answer: "LOGARITHMIC", term: "Logarithmic time", clue: "Growth of O(log n): doubling the input adds one step" },
];

export const RUSH = [
  { task: "Time complexity of binary search", answer: "O(log n)", wrong: ["O(n)", "O(1)", "O(n log n)"] },
  { task: "Average time of quicksort", answer: "O(n log n)", wrong: ["O(n)", "O(n²)", "O(log n)"] },
  { task: "Quicksort, last-element pivot, already sorted input", answer: "O(n²)", wrong: ["O(n log n)", "O(n)", "O(2^n)"] },
  { task: "Lookup in a hash map (average)", answer: "O(1)", wrong: ["O(log n)", "O(n)", "O(n log n)"] },
  { task: "Push or pop on a stack", answer: "O(1)", wrong: ["O(log n)", "O(n)", "O(n²)"] },
  { task: "Search in a balanced binary search tree", answer: "O(log n)", wrong: ["O(1)", "O(n)", "O(n log n)"] },
  { task: "Search in an unsorted array", answer: "O(n)", wrong: ["O(log n)", "O(1)", "O(n log n)"] },
  { task: "Extra space of merge sort on an array", answer: "O(n)", wrong: ["O(1)", "O(log n)", "O(n²)"] },
  { task: "Extra space of heap sort", answer: "O(1)", wrong: ["O(n)", "O(log n)", "O(n log n)"] },
  { task: "Insert into a binary heap", answer: "O(log n)", wrong: ["O(1)", "O(n)", "O(n log n)"] },
  { task: "Peek at the minimum of a min-heap", answer: "O(1)", wrong: ["O(log n)", "O(n)", "O(n log n)"] },
  { task: "BFS over a graph with V vertices and E edges", answer: "O(V + E)", wrong: ["O(V * E)", "O(E log V)", "O(V²)"] },
  { task: "Dijkstra with a binary heap", answer: "O((V + E) log V)", wrong: ["O(V + E)", "O(V³)", "O(E²)"] },
  { task: "Naive recursive Fibonacci", answer: "O(2^n)", wrong: ["O(n)", "O(n²)", "O(log n)"] },
  { task: "Fibonacci with memoization", answer: "O(n)", wrong: ["O(2^n)", "O(n²)", "O(log n)"] },
  { task: "Counting sort with value range k", answer: "O(n + k)", wrong: ["O(n log n)", "O(n * k)", "O(k log n)"] },
  { task: "Generate every subset of n items", answer: "O(2^n)", wrong: ["O(n²)", "O(n log n)", "O(n)"] },
  { task: "Two nested loops over the same array", answer: "O(n²)", wrong: ["O(n)", "O(2n)", "O(n log n)"] },
  { task: "Append to a Python list (amortized)", answer: "O(1)", wrong: ["O(n)", "O(log n)", "O(n log n)"] },
  { task: "Insertion sort on an already sorted array", answer: "O(n)", wrong: ["O(n²)", "O(n log n)", "O(1)"] },
];

export const BUGS = [
  {
    symptom: "IndexError: list index out of range when the target is larger than every element.",
    lang: "python",
    code: `def binary_search(xs, target):
    lo, hi = 0, len(xs)
    while lo <= hi:
        mid = (lo + hi) // 2
        if xs[mid] == target:
            return mid
        if xs[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1`,
    bug: [1],
    why: "With an inclusive loop (lo <= hi) the upper bound must be the last valid index. hi = len(xs) lets mid reach len(xs). Use hi = len(xs) - 1.",
  },
  {
    symptom: "lower_bound hangs forever when the target is bigger than the middle element.",
    lang: "python",
    code: `def lower_bound(xs, target):
    lo, hi = 0, len(xs)
    while lo < hi:
        mid = (lo + hi) // 2
        if xs[mid] < target:
            lo = mid
        else:
            hi = mid
    return lo`,
    bug: [5],
    why: "When hi = lo + 1, mid equals lo, so lo = mid never shrinks the range. Everything up to mid is known to be too small: lo = mid + 1.",
  },
  {
    symptom: "RecursionError: maximum recursion depth exceeded, even for a list of 3 items.",
    lang: "python",
    code: `def merge_sort(xs):
    mid = len(xs) // 2
    left = merge_sort(xs[:mid])
    right = merge_sort(xs[mid:])
    return merge(left, right)`,
    bug: [1],
    why: "There is no base case. A one-element list splits into [] and [x] forever. Add if len(xs) <= 1: return xs before splitting.",
  },
  {
    symptom: "Quicksort output is almost sorted, but pivot values end up in the wrong places.",
    lang: "python",
    code: `def partition(a, lo, hi):
    pivot = a[hi]
    i = lo
    for j in range(lo, hi):
        if a[j] < pivot:
            a[i], a[j] = a[j], a[i]
            i += 1
    a[i], a[lo] = a[lo], a[i]
    return i`,
    bug: [7],
    why: "Lomuto partition must finish by moving the pivot from a[hi] into its final slot a[i]. Swapping with a[lo] puts an arbitrary element there instead: a[i], a[hi] = a[hi], a[i].",
  },
  {
    symptom: "The 'BFS' visits nodes depth-first, and the shortest paths it reports are too long.",
    lang: "python",
    code: `from collections import deque

def bfs(graph, start):
    seen = {start}
    q = deque([start])
    order = []
    while q:
        node = q.pop()
        order.append(node)
        for nxt in graph[node]:
            if nxt not in seen:
                seen.add(nxt)
                q.append(nxt)
    return order`,
    bug: [7],
    why: "pop() takes from the same end append() adds to, which is a stack (LIFO), so this is DFS. BFS needs FIFO: q.popleft().",
  },
  {
    symptom: "0/1 knapsack returns a total that uses the same item several times.",
    lang: "python",
    code: `def knapsack(items, cap):
    best = [0] * (cap + 1)
    for weight, value in items:
        for c in range(weight, cap + 1):
            best[c] = max(best[c], best[c - weight] + value)
    return best[cap]`,
    bug: [3],
    why: "Walking capacity upwards lets best[c - weight] already include the current item, which is the unbounded knapsack. Iterate downwards: range(cap, weight - 1, -1).",
  },
  {
    symptom: "IndexError: list index out of range on the very first pass of bubble sort.",
    lang: "python",
    code: `def bubble_sort(xs):
    n = len(xs)
    for i in range(n):
        for j in range(n - i):
            if xs[j] > xs[j + 1]:
                xs[j], xs[j + 1] = xs[j + 1], xs[j]
    return xs`,
    bug: [3],
    why: "The inner loop compares xs[j] with xs[j + 1], so j must stop one earlier: range(n - i - 1).",
  },
  {
    symptom: "fib(40) takes forever even though the function is 'memoized'.",
    lang: "python",
    code: `def fib(n, memo=None):
    if memo is None:
        memo = {}
    if n < 2:
        return n
    if n in memo:
        return memo[n]
    result = fib(n - 1, memo) + fib(n - 2, memo)
    return result`,
    bug: [7, 8],
    why: "Results are looked up but never stored, so the memo stays empty and the call tree is still exponential. Save before returning: memo[n] = result.",
  },
];

export const META = {
  rushLabel: "Big-O Rush",
  rushIntro: "Pick the time or space complexity that fits.",
  rushMono: true,
  bugLabel: "Algorithm Bug Hunt",
  bugNoun: "symptom",
};
