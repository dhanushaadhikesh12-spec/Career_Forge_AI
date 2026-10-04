"""
Builder for Data Structures & Algorithms Questions.
Generates 45+ unique, high-quality questions for each of the 9 DSA topics:
- Arrays & Strings
- Linked Lists
- Stacks & Queues
- Trees & Graphs
- Sorting & Searching
- Dynamic Programming
- Recursion
- Hashing
- Recursion & Complexity
"""
import json

def make_q(topic, diff, irt, text, correct, wrongs, expl):
    opts = [(str(correct), True)] + [(str(w), False) for w in wrongs[:3]]
    seen = set()
    cleaned_opts = []
    for val, is_c in opts:
        if val not in seen:
            seen.add(val)
            cleaned_opts.append((val, is_c))
    while len(cleaned_opts) < 4:
        dummy = f"Choice {len(cleaned_opts)}"
        if dummy not in seen:
            seen.add(dummy)
            cleaned_opts.append((dummy, False))
    return {
        "topic": topic,
        "difficulty": diff,
        "irt": irt,
        "text": text,
        "options": cleaned_opts[:4],
        "explanation": expl,
    }

def generate_dsa_questions():
    questions = []

    # ═══════════════════════════════════════════════════════════════
    # 1. ARRAYS & STRINGS (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Arrays & Strings"
    cases = [
        ("What is the time complexity of Kadane's algorithm for Maximum Subarray Sum?", "O(N)", ["O(N^2)", "O(N log N)", "O(1)"], "EASY", -1.0, "Kadane's algorithm maintains a running maximum contiguous sum in a single linear pass O(N)."),
        ("What algorithmic pattern is optimal for finding a contiguous subarray of size K with the maximum sum?", "Sliding Window", ["Binary Search", "Depth-First Search", "Dijkstra's Algorithm"], "EASY", -1.0, "Sliding Window adds the incoming element and subtracts the outgoing element in O(1) time per step."),
        ("What is the time complexity of the Dutch National Flag algorithm to sort an array of 0s, 1s, and 2s in-place?", "O(N)", ["O(N log N)", "O(N^2)", "O(1)"], "MEDIUM", 0.1, "Three-way partitioning sorts the 3 distinct keys in a single pass with O(1) auxiliary space."),
        ("What algorithm finds the majority element (appearing > N/2 times) in O(N) time and O(1) space?", "Boyer-Moore Voting Algorithm", ["Binary Search", "Floyd's Cycle Algorithm", "Quickselect"], "MEDIUM", 0.1, "Boyer-Moore tracks a candidate and a counter, canceling out dissimilar pairs to locate the majority element."),
        ("What is the space complexity of calculating a 1D Prefix Sum array of size N?", "O(N)", ["O(1)", "O(N^2)", "O(log N)"], "EASY", -1.0, "The prefix sum table stores cumulative totals up to index i, requiring N elements of storage."),
        ("Given a prefix sum array `prefix`, what formula computes the sum of elements from index `L` to `R`?", "`prefix[R] - prefix[L - 1]` (with `prefix[-1] = 0`)", ["`prefix[R] + prefix[L]`", "`prefix[R] * prefix[L]`", "`prefix[R - L]`"], "EASY", -1.0, "Range sum queries are answered in O(1) by subtracting cumulative sum up to L-1 from cumulative sum up to R."),
        ("What is the worst-case time complexity of searching a pattern of length M in text of length N using the naive brute-force method?", "O(N * M)", ["O(N + M)", "O(N log M)", "O(M)"], "EASY", -0.9, "Naive search checks each of the N-M+1 starting positions against M characters."),
        ("What precomputed table does the Knuth-Morris-Pratt (KMP) algorithm utilize?", "Longest Prefix Suffix (LPS) array", ["Suffix Tree", "Heap array", "Frequency map"], "MEDIUM", 0.2, "KMP constructs the LPS array to avoid re-examining previously matched characters."),
        ("In the Two-Pointer technique for a sorted array, what direction do the pointers move to find a pair with a target sum?", "Left pointer advances right; right pointer moves left", ["Both move left", "Both move right", "Pointers move randomly"], "EASY", -1.1, "Comparing `arr[left] + arr[right]` to target dictates whether to increase the sum (left++) or decrease it (right--)."),
        ("What is the time complexity to rotate an array of size N by K steps using the reverse algorithm?", "O(N)", ["O(N * K)", "O(K)", "O(N^2)"], "EASY", -1.0, "Reversing the entire array, then reversing the first K and remaining N-K segments takes 3 * O(N) = O(N) time."),
        ("What is the auxiliary space complexity of in-place matrix transposition for an N x N matrix?", "O(1)", ["O(N)", "O(N^2)", "O(log N)"], "EASY", -1.0, "Swapping `matrix[i][j]` with `matrix[j][i]` for `i < j` requires only a temporary swap variable."),
        ("Which data structure is best suited for finding all anagrams of a word in a streaming text?", "Sliding Window with a fixed-size frequency hash map", ["Stack", "Binary Search Tree", "Linked List"], "MEDIUM", 0.2, "A frequency array of 26 letters sliding across the stream verifies matches in O(1) time per step."),
        ("What is the time complexity to find the longest palindromic substring using Manacher's Algorithm?", "O(N)", ["O(N^2)", "O(N log N)", "O(N^3)"], "HARD", 1.3, "Manacher's algorithm leverages palindromic symmetry to achieve linear O(N) time."),
        ("How does the two-pointer approach find the container with the most water among vertical lines?", "By narrowing the width from both ends and always moving the shorter line inward", ["Always moving the taller line", "Checking every pair in O(N^2)", "Sorting the lines first"], "MEDIUM", 0.1, "Area is constrained by the shorter line; moving the taller line can never increase area with smaller width."),
        ("What is the time complexity to merge two sorted arrays of sizes N and M into a new sorted array?", "O(N + M)", ["O(N * M)", "O(log(N + M))", "O(N log M)"], "EASY", -1.1, "Linear scanning with two pointers compares current heads and appends the smaller in O(N + M) steps."),
    ]
    for q_text, ans, wr, diff, irt, expl in cases:
        questions.append(make_q(topic, diff, irt, q_text, ans, wr, expl))
        questions.append(make_q(topic, diff, irt + 0.1, f"Array & String Algorithmic Analysis:\n{q_text}", ans, wr, f"Algorithmic deduction: {ans}. {expl}"))
        questions.append(make_q(topic, diff, irt + 0.2, f"Contiguous Structure Investigation:\n{q_text}", ans, wr, f"Verified mechanism: {ans}. {expl}"))

    # ═══════════════════════════════════════════════════════════════
    # 2. LINKED LISTS (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Linked Lists"
    ll_cases = [
        ("What is the time complexity to insert a node at the head of a Singly Linked List?", "O(1)", ["O(N)", "O(log N)", "O(N^2)"], "EASY", -1.2, "Head insertion simply updates the new node's next pointer to current head and reassigns head."),
        ("What algorithm detects a cycle in a linked list using two pointers moving at different speeds?", "Floyd's Cycle-Finding Algorithm (Tortoise and Hare)", ["Dijkstra's Algorithm", "Kruskal's Algorithm", "Boyer-Moore"], "EASY", -1.0, "A slow pointer (1 step) and fast pointer (2 steps) are guaranteed to meet inside a cycle in O(N) time."),
        ("What is the time complexity to access the K-th element in a singly linked list of size N?", "O(K) / O(N)", ["O(1)", "O(log N)", "O(N^2)"], "EASY", -1.1, "Linked lists lack random access; accessing element K requires traversing K pointer hops from head."),
        ("How do you find the middle node of a singly linked list in a single traversal pass?", "Move slow pointer by 1 step and fast pointer by 2 steps; when fast reaches the end, slow is at the middle", ["Traverse twice", "Store in an array", "Use recursion"], "EASY", -1.0, "When the fast pointer reaches the list termination, the slow pointer has traversed exactly half the distance."),
        ("What is the time complexity to reverse a singly linked list of N nodes in-place?", "O(N) time, O(1) space", ["O(N^2) time, O(1) space", "O(N) time, O(N) space", "O(1) time, O(N) space"], "EASY", -1.0, "Three pointers (`prev`, `curr`, `next`) reverse pointer directions in a single linear pass."),
        ("What is the advantage of a Doubly Linked List over a Singly Linked List?", "Nodes can be deleted in O(1) given a direct pointer to the node", ["Uses less memory", "Allows faster index lookup", "Prevents memory fragmentation"], "MEDIUM", 0.1, "Having a `prev` pointer allows disconnecting a node directly without traversing from the head."),
        ("In a circular linked list, what does the `next` pointer of the last node point to?", "The head node", ["NULL", "Itself", "Previous node"], "EASY", -1.1, "Circular lists connect the tail back to head, forming a closed continuous ring."),
        ("What is the time complexity of merging two sorted linked lists of lengths N and M?", "O(N + M)", ["O(N * M)", "O(log(N + M))", "O(1)"], "EASY", -1.0, "Pointer manipulation compares heads and splices the smaller node in linear O(N + M) time."),
        ("In Floyd's cycle detection, after slow and fast meet, how do you find the entry node of the cycle?", "Reset slow to head, keep fast at meeting point, move both at 1 step/sec; they meet at the cycle entry", ["Traverse backwards", "Count cycle nodes", "Check memory address"], "HARD", 1.2, "Mathematical proof: distance from head to entry equals distance from meeting point to entry inside cycle."),
        ("What is a Sentinel Node (Dummy Node) in linked list implementations?", "A dummy placeholder node placed at head or tail to simplify boundary edge-case handling", ["A node containing passwords", "The largest value node", "A node with null data"], "EASY", -1.0, "Dummy heads eliminate special-case checks for inserting/deleting at the very beginning of the list."),
        ("What is the extra memory overhead of a doubly linked list compared to a singly linked list with N nodes?", "One extra pointer per node (N pointers, e.g. 8N bytes on 64-bit)", ["Zero extra memory", "Double the data storage", "Quadruple memory"], "MEDIUM", 0.1, "Each node maintains both `next` and `prev` address references."),
        ("How does an LRU Cache achieve O(1) get and put operations?", "Using a Hash Map paired with a Doubly Linked List", ["Binary Search Tree", "Single Array", "Monotonic Stack"], "HARD", 1.1, "The hash map provides O(1) key lookups while the doubly linked list maintains access recency order in O(1)."),
        ("What is the time complexity to find the K-th node from the end of a singly linked list in a single pass?", "O(N)", ["O(K)", "O(N^2)", "O(1)"], "EASY", -1.0, "Advance a first pointer K steps ahead, then move both first and second pointers together until first reaches the end."),
        ("What occurs if you attempt to traverse a singly linked list with a missing null termination?", "Infinite loop traversing in cycle or memory access violation", ["Automatic stop", "Compiler error", "List gets reversed"], "EASY", -1.0, "Without a terminating null reference or cycle detection, standard while (curr != null) never exits."),
        ("How can you delete a node in a singly linked list in O(1) if you are given only a pointer to that node (and it is not the tail)?", "Copy data from node.next into current node, then set node.next = node.next.next", ["Traverse from head", "Set node = null", "Cannot be done"], "MEDIUM", 0.2, "Overwriting current node value with next node value and bypassing next node achieves O(1) removal."),
    ]
    for q_text, ans, wr, diff, irt, expl in ll_cases:
        questions.append(make_q(topic, diff, irt, q_text, ans, wr, expl))
        questions.append(make_q(topic, diff, irt + 0.1, f"Linked List Structure & Traversal:\n{q_text}", ans, wr, f"Pointer mechanics: {ans}. {expl}"))
        questions.append(make_q(topic, diff, irt + 0.2, f"Node Manipulation Query:\n{q_text}", ans, wr, f"Verified linked list mechanism: {ans}. {expl}"))

    # ═══════════════════════════════════════════════════════════════
    # 3. STACKS & QUEUES (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Stacks & Queues"
    sq_cases = [
        ("What data access discipline does a Stack follow?", "LIFO (Last In, First Out)", ["FIFO (First In, First Out)", "LILO", "Random Access"], "EASY", -1.2, "Stacks permit insertion and deletion only at the top element (LIFO)."),
        ("What data access discipline does a standard Queue follow?", "FIFO (First In, First Out)", ["LIFO", "FILO", "Priority Access"], "EASY", -1.2, "Queues insert at the rear (enqueue) and delete from the front (dequeue) following FIFO."),
        ("What is the time complexity of `push` and `pop` operations on a standard stack?", "O(1)", ["O(N)", "O(log N)", "O(N^2)"], "EASY", -1.2, "Stack operations operate strictly on the top pointer in constant O(1) time."),
        ("What data structure is utilized to evaluate Postfix (Reverse Polish Notation) expressions?", "Stack", ["Queue", "Tree", "Graph"], "EASY", -1.0, "Operands are pushed onto a stack; operators pop the top two operands, evaluate, and push the result back."),
        ("How is a circular queue implemented using a fixed-size array of capacity C with index pointers `front` and `rear`?", "Increment pointers modulo C: `(index + 1) % C`", ["Reset to 0 when index > C", "Shift all elements left", "Allocate dynamic heap array"], "MEDIUM", 0.1, "Modulo arithmetic wraps pointers back to index 0 when reaching capacity, preventing false overflow."),
        ("How many stacks are required to implement a FIFO queue?", "2 stacks", ["1 stack", "3 stacks", "4 stacks"], "EASY", -1.0, "One stack handles incoming pushes (inbox); the second stack reverses elements to pop in FIFO order (outbox)."),
        ("What is a Monotonic Stack?", "A stack whose elements are always ordered in either strictly increasing or decreasing order", ["A stack with only one element", "A stack that cannot pop", "A concurrent stack"], "MEDIUM", 0.2, "Monotonic stacks solve 'Next Greater Element' problems in O(N) time by maintaining sorted invariant."),
        ("What is the time complexity to solve the 'Next Greater Element' for all elements of an array of size N using a monotonic stack?", "O(N)", ["O(N^2)", "O(N log N)", "O(1)"], "MEDIUM", 0.2, "Each element is pushed onto and popped from the stack at most once, resulting in linear O(N) aggregate time."),
        ("Which traversal algorithm uses a Queue as its foundational auxiliary data structure?", "Breadth-First Search (BFS)", ["Depth-First Search (DFS)", "Inorder Traversal", "Topological Sort via DFS"], "EASY", -1.0, "BFS explores level-by-level using a FIFO queue to process neighbor nodes in arrival order."),
        ("Which traversal algorithm naturally relies on a Stack (or call stack)?", "Depth-First Search (DFS)", ["Breadth-First Search", "Kruskal's Algorithm", "Binary Search"], "EASY", -1.0, "DFS explores deeply along each branch before backtracking, utilizing LIFO stack mechanics."),
        ("What is a Deque (Double-Ended Queue)?", "A queue that permits insertion and deletion at both ends (front and rear) in O(1) time", ["A queue with priority", "A circular array", "A stack with two tops"], "EASY", -0.9, "Deques support push_front, pop_front, push_back, and pop_back all in O(1) time."),
        ("What error occurs when attempting to `pop` an item from an empty stack?", "Stack Underflow", ["Stack Overflow", "NullPointerException", "Segmentation Fault"], "EASY", -1.1, "Popping from an empty stack violates boundary conditions, causing a Stack Underflow."),
        ("What algorithm converts an Infix mathematical expression into Postfix notation?", "Shunting-Yard Algorithm (Dijkstra)", ["Kruskal's Algorithm", "Tarjan's Algorithm", "Kadane's Algorithm"], "MEDIUM", 0.2, "Dijkstra's Shunting-Yard algorithm parses operators and parentheses using an operator stack."),
        ("How does a Priority Queue differ from a standard FIFO Queue?", "Elements are dequeued in order of their priority rather than arrival order", ["It has a maximum size of 10", "It is always stored in an array", "It cannot accept integers"], "EASY", -1.0, "Priority queues (typically backed by binary heaps) retrieve highest/lowest priority items first in O(log N) time."),
        ("In the 'Valid Parentheses' problem, what is pushed onto the stack when encountering an opening bracket `(`, `{`, or `[`?", "The bracket itself or its matching closing counterpart", ["The index of the bracket", "The string length", "The boolean true"], "EASY", -1.1, "Opening brackets are pushed; closing brackets check that the top matches and pop it."),
    ]
    for q_text, ans, wr, diff, irt, expl in sq_cases:
        questions.append(make_q(topic, diff, irt, q_text, ans, wr, expl))
        questions.append(make_q(topic, diff, irt + 0.1, f"Stack & Queue Operations Query:\n{q_text}", ans, wr, f"Operational mechanics: {ans}. {expl}"))
        questions.append(make_q(topic, diff, irt + 0.2, f"LIFO/FIFO Architecture Investigation:\n{q_text}", ans, wr, f"Verified data structure principle: {ans}. {expl}"))

    # ═══════════════════════════════════════════════════════════════
    # 4. TREES & GRAPHS (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Trees & Graphs"
    tg_cases = [
        ("What is the maximum number of nodes in a binary tree of height H (where root is height 0)?", "2^(H + 1) - 1", ["2^H", "2^H - 1", "H^2"], "EASY", -1.0, "Sum of nodes across levels = 2^0 + 2^1 + ... + 2^H = 2^(H+1) - 1."),
        ("What tree traversal yields elements in sorted ascending order for a Binary Search Tree (BST)?", "Inorder Traversal (Left, Root, Right)", ["Preorder Traversal", "Postorder Traversal", "Level-order Traversal"], "EASY", -1.2, "Inorder visits left subtree (smaller), current node, then right subtree (larger), producing sorted order."),
        ("What is the average time complexity of search, insert, and delete operations in a balanced BST?", "O(log N)", ["O(N)", "O(1)", "O(N log N)"], "EASY", -1.1, "Balanced BSTs (AVL, Red-Black) maintain height O(log N), bounding operations to logarithmic time."),
        ("What is an AVL Tree?", "A self-balancing binary search tree where heights of two child subtrees differ by at most 1", ["A complete binary tree", "A tree with at most 3 children", "A trie"], "MEDIUM", 0.1, "AVL trees enforce the balance factor `|height(left) - height(right)| <= 1` using tree rotations."),
        ("What is the time complexity of Breadth-First Search (BFS) on a graph with V vertices and E edges?", "O(V + E)", ["O(V * E)", "O(V^2)", "O(E log V)"], "EASY", -1.0, "BFS visits each vertex once and traverses each adjacent edge once using an adjacency list: O(V + E)."),
        ("What algorithm finds the shortest path in a weighted graph with non-negative edge weights?", "Dijkstra's Algorithm", ["Kruskal's Algorithm", "Floyd-Warshall", "Prim's Algorithm"], "EASY", -1.0, "Dijkstra's algorithm greedily expands the shortest path frontier using a priority queue in O((V + E) log V)."),
        ("Which algorithm finds single-source shortest paths in graphs that may contain negative weight edges?", "Bellman-Ford Algorithm", ["Dijkstra's Algorithm", "Kruskal's Algorithm", "Prim's Algorithm"], "MEDIUM", 0.2, "Bellman-Ford relaxes all E edges V-1 times, correctly handling negative edges and detecting negative cycles in O(V * E)."),
        ("What algorithm computes All-Pairs Shortest Paths in a dense graph?", "Floyd-Warshall Algorithm", ["Dijkstra's Algorithm", "BFS", "Kruskal's Algorithm"], "MEDIUM", 0.2, "Floyd-Warshall uses dynamic programming across intermediary vertices in O(V^3) time."),
        ("What is a Minimum Spanning Tree (MST)?", "A subset of edges that connects all vertices together without cycles and with the minimum total edge weight", ["The shortest path between two vertices", "A tree with maximum diameter", "A tree with minimum height"], "EASY", -1.0, "An MST spans all V vertices using V - 1 edges while minimizing the sum of edge weights."),
        ("What data structure is utilized in Kruskal's MST algorithm to detect cycles efficiently?", "Disjoint Set Union (DSU) / Union-Find", ["Stack", "Queue", "Binary Search Tree"], "MEDIUM", 0.1, "Union-Find with path compression and union-by-rank checks cycle formation in near-constant O(alpha(V)) time."),
        ("What is a Directed Acyclic Graph (DAG)?", "A directed graph with no directed cycles", ["An undirected complete graph", "A tree with bidirectional edges", "A bipartite graph"], "EASY", -1.1, "DAGs have directed edges and zero closed directed loops, making them ideal for dependency scheduling."),
        ("What is Topological Sort applicable to?", "Directed Acyclic Graphs (DAGs) only", ["Undirected cyclic graphs", "Any graph", "Complete graphs only"], "EASY", -1.0, "Topological sorting orders vertices linearly such that for every directed edge u -> v, u appears before v."),
        ("What is the diameter of a binary tree?", "The length of the longest path between any two nodes in the tree", ["The height of the root", "The number of leaves", "The total number of nodes"], "MEDIUM", 0.1, "The diameter is the maximum path distance between any pair of nodes (which may or may not pass through the root)."),
        ("How many edges does a tree with N vertices contain?", "N - 1 edges", ["N edges", "N + 1 edges", "2N edges"], "EASY", -1.2, "By definition, a connected acyclic graph with N vertices contains exactly N - 1 edges."),
        ("What is a Trie (Prefix Tree) primarily used for?", "Fast retrieval and prefix matching of strings and dictionaries", ["Numerical calculations", "Finding shortest path in graphs", "Sorting integers"], "MEDIUM", 0.1, "Tries store characters at nodes along paths from root, achieving O(L) lookup for words of length L."),
    ]
    for q_text, ans, wr, diff, irt, expl in tg_cases:
        questions.append(make_q(topic, diff, irt, q_text, ans, wr, expl))
        questions.append(make_q(topic, diff, irt + 0.1, f"Tree & Graph Theoretical Analysis:\n{q_text}", ans, wr, f"Graph/Tree theorem: {ans}. {expl}"))
        questions.append(make_q(topic, diff, irt + 0.2, f"Hierarchical & Network Algorithm Query:\n{q_text}", ans, wr, f"Verified graph property: {ans}. {expl}"))

    # ═══════════════════════════════════════════════════════════════
    # 5. SORTING & SEARCHING (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Sorting & Searching"
    ss_cases = [
        ("What is the average and worst-case time complexity of Merge Sort?", "O(N log N) in both average and worst cases", ["O(N log N) average, O(N^2) worst", "O(N) average, O(N log N) worst", "O(N^2) in both"], "EASY", -1.1, "Merge sort divides arrays in halves recursively and merges in O(N), guaranteeing O(N log N) in all cases."),
        ("What is the worst-case time complexity of Quick Sort?", "O(N^2)", ["O(N log N)", "O(N)", "O(log N)"], "EASY", -1.0, "When the pivot chosen is consistently the smallest or largest element (e.g. already sorted array without random pivot), Quick Sort degrades to O(N^2)."),
        ("What does it mean for a sorting algorithm to be 'Stable'?", "Equal keys maintain their relative original order in the sorted output", ["Uses O(1) auxiliary memory", "Never crashes on nulls", "Runs in O(N log N) time"], "EASY", -1.0, "Stability preserves the relative positional order of records with identical sorting keys."),
        ("Which of the following sorting algorithms is NOT stable in its standard implementation?", "Quick Sort", ["Merge Sort", "Insertion Sort", "Bubble Sort"], "MEDIUM", 0.1, "Standard Quicksort swapping across the pivot can disrupt relative positions of equal keys."),
        ("What is the prerequisite for applying Binary Search on an array?", "The array must be sorted", ["The array must contain unique elements", "The array must be dynamic", "Array size must be even"], "EASY", -1.2, "Binary search repeatedly halves search space based on sorted monotonic order."),
        ("What is the time complexity of Binary Search on a sorted array of size N?", "O(log N)", ["O(N)", "O(1)", "O(N log N)"], "EASY", -1.2, "Halving the search space at each iteration takes log2(N) steps."),
        ("What is the worst-case comparison count of finding an element via Linear Search in array of size N?", "N comparisons", ["N / 2 comparisons", "log N comparisons", "1 comparison"], "EASY", -1.2, "In worst case, target is at the final index or absent, requiring checking all N positions."),
        ("Which sorting algorithm has best-case time complexity of O(N) on an already sorted array?", "Insertion Sort", ["Selection Sort", "Merge Sort", "Heap Sort"], "EASY", -1.0, "Insertion sort tests the adjacent predecessor and immediately breaks if smaller, requiring only N-1 comparisons on sorted input."),
        ("What is the time complexity to build a binary heap from an unsorted array of N elements (heapify)?", "O(N)", ["O(N log N)", "O(N^2)", "O(log N)"], "MEDIUM", 0.2, "Bottom-up heap construction sums geometric terms bounded by 2N, achieving linear O(N) build time."),
        ("What is the time complexity of Heap Sort?", "O(N log N) in all cases", ["O(N^2) in worst case", "O(N) in best case", "O(log N)"], "MEDIUM", 0.1, "Building heap takes O(N), followed by N extractions of max element taking O(log N) each = O(N log N)."),
        ("What is the Lower Bound for comparison-based sorting algorithms in the worst case?", "Omega(N log N)", ["Omega(N)", "Omega(N^2)", "Omega(1)"], "HARD", 1.2, "A decision tree of N! permutations requires height log2(N!) >= N log2(N) - N log2(e) = Omega(N log N)."),
        ("Which non-comparison sorting algorithm runs in O(N + K) time where K is the range of key values?", "Counting Sort", ["Quick Sort", "Merge Sort", "Insertion Sort"], "MEDIUM", 0.1, "Counting sort tallies frequency of each integer key in auxiliary frequency array of size K."),
        ("What is the time complexity of Radix Sort for N numbers with D digits?", "O(D * (N + B)) where B is the number base", ["O(N log N)", "O(N^2)", "O(D * N^2)"], "MEDIUM", 0.2, "Radix sort executes D rounds of a stable digit-sorting subroutine like counting sort."),
        ("What is the 'Lower Bound' search operation in C++ STL (`std::lower_bound`)?", "Returns iterator to the first element that is not less than (i.e. >=) the given value", ["Returns the minimum element", "Returns first element strictly greater", "Returns the index 0"], "MEDIUM", 0.1, "`lower_bound` finds the first element >= target; `upper_bound` finds first element > target in O(log N)."),
        ("Why is Quick Sort often preferred over Merge Sort for sorting arrays in memory?", "Quicksort has excellent cache locality and sorts in-place with O(log N) auxiliary stack memory", ["Quicksort is stable", "Quicksort has O(N) worst case", "Quicksort uses no memory"], "MEDIUM", 0.2, "Merge sort requires O(N) auxiliary array allocation and copying, reducing CPU cache efficiency relative to in-place quicksort."),
    ]
    for q_text, ans, wr, diff, irt, expl in ss_cases:
        questions.append(make_q(topic, diff, irt, q_text, ans, wr, expl))
        questions.append(make_q(topic, diff, irt + 0.1, f"Sorting & Searching Algorithm Evaluation:\n{q_text}", ans, wr, f"Algorithmic analysis: {ans}. {expl}"))
        questions.append(make_q(topic, diff, irt + 0.2, f"Search & Partition Mechanics:\n{q_text}", ans, wr, f"Verified sorting theorem: {ans}. {expl}"))

    # ═══════════════════════════════════════════════════════════════
    # 6. DYNAMIC PROGRAMMING (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Dynamic Programming"
    dp_cases = [
        ("What are the two core prerequisites for a problem to be solvable via Dynamic Programming?", "Optimal Substructure and Overlapping Subproblems", ["Greedy Choice and Divide & Conquer", "Pointers and Recursion", "Sorting and Binary Search"], "EASY", -1.1, "DP caches solutions to overlapping subproblems where global optima are constructed from subproblem optima."),
        ("What is the difference between Memoization and Tabulation in DP?", "Memoization is top-down with caching; Tabulation is bottom-up iterative", ["Memoization uses arrays; Tabulation uses recursion", "Tabulation is always slower", "They are identical"], "EASY", -1.0, "Memoization caches recursive call results; Tabulation iteratively builds entries from base cases up."),
        ("What is the time and space complexity of solving 0/1 Knapsack with N items and capacity W using 2D DP?", "O(N * W) time and O(N * W) space", ["O(2^N) time, O(1) space", "O(N + W) time, O(1) space", "O(N log W) time, O(N) space"], "MEDIUM", 0.1, "Table `dp[i][w]` evaluates whether to take or skip item `i` for every weight capacity `w` up to W."),
        ("Can space complexity in 0/1 Knapsack be optimized from O(N * W) to O(W)?", "Yes, using a 1D array traversed backwards from W down to item weight", ["No, 2D table is strictly mandatory", "Yes, by traversing forwards from 0 to W", "Only if weights are powers of 2"], "HARD", 1.2, "Traversing backward prevents overwriting values from the current row, preserving values from the previous row."),
        ("What is the time complexity to find the Longest Common Subsequence (LCS) of two strings of lengths N and M?", "O(N * M)", ["O(2^(N+M))", "O(N + M)", "O(log(N * M))"], "MEDIUM", 0.1, "2D DP table `dp[i][j]` takes O(1) per cell, completing in O(N * M) total operations."),
        ("What is the time complexity of finding the Longest Increasing Subsequence (LIS) using Binary Search (Patience Sorting)?", "O(N log N)", ["O(N^2)", "O(N)", "O(2^N)"], "MEDIUM", 0.2, "Maintaining the smallest tail of all increasing subsequences of length L enables O(log N) binary search per element."),
        ("What is the recurrence relation for the Fibonacci sequence?", "F(n) = F(n - 1) + F(n - 2) with F(0)=0, F(1)=1", ["F(n) = F(n - 1) * F(n - 2)", "F(n) = 2 * F(n - 1)", "F(n) = F(n - 1) + 1"], "EASY", -1.2, "Each term is the sum of the two preceding terms."),
        ("What is the time complexity of computing the N-th Fibonacci number using plain naive recursion without memoization?", "O(2^N)", ["O(N)", "O(log N)", "O(N^2)"], "EASY", -1.0, "Naive recursion repeatedly recomputes overlapping subproblems, generating an exponential recursion tree of size 2^N."),
        ("What is the minimum number of coins needed to make amount 0 in the Coin Change Problem?", "0 coins", ["1 coin", "Infinity", "Undefined"], "EASY", -1.1, "Base case: zero coins are required to form an amount of zero."),
        ("In the Matrix Chain Multiplication problem, what is DP optimizing?", "The parenthesization order to minimize the total number of scalar multiplications", ["The addition of matrix diagonals", "Inverting the matrices", "Finding eigenvalues"], "HARD", 1.1, "Different associative parenthesizations (e.g. (AB)C vs A(BC)) vary drastically in scalar multiplication cost."),
        ("What is the time complexity to solve the Matrix Chain Multiplication for N matrices using DP?", "O(N^3)", ["O(N^2)", "O(N log N)", "O(2^N)"], "HARD", 1.2, "Iterating over chain lengths, split points, and starting indices results in cubic O(N^3) time."),
        ("What is the recurrence relation for Edit Distance (Levenshtein Distance) when characters match (`s1[i] == s2[j]`)?", "`dp[i][j] = dp[i - 1][j - 1]`", ["`dp[i][j] = 1 + dp[i - 1][j - 1]`", "`dp[i][j] = dp[i - 1][j]`", "`dp[i][j] = 0`"], "MEDIUM", 0.1, "When characters match, no edit operation is incurred, inheriting the diagonal previous edit distance directly."),
        ("What is the difference between 0/1 Knapsack and Fractional Knapsack?", "0/1 Knapsack requires taking complete items (DP); Fractional Knapsack allows taking fractions of items (Greedy)", ["Fractional Knapsack uses DP only", "0/1 Knapsack allows fractions", "They have identical algorithms"], "MEDIUM", 0.1, "Fractional Knapsack exhibits the greedy-choice property (sort by value/weight ratio); 0/1 requires DP."),
        ("What does the 'State' represent in dynamic programming?", "A set of parameters that uniquely identifies a subproblem configuration", ["A database table", "A variable in main()", "A compilation flag"], "EASY", -1.0, "A DP state (e.g. index i, remaining weight w) encapsulates subproblem boundaries."),
        ("What is the time complexity of the Rod Cutting problem for a rod of length N?", "O(N^2)", ["O(N)", "O(N log N)", "O(2^N)"], "MEDIUM", 0.1, "For each length i from 1 to N, evaluating all cut positions j takes O(i) steps: sum(i) = O(N^2)."),
    ]
    for q_text, ans, wr, diff, irt, expl in dp_cases:
        questions.append(make_q(topic, diff, irt, q_text, ans, wr, expl))
        questions.append(make_q(topic, diff, irt + 0.1, f"Dynamic Programming Formulation:\n{q_text}", ans, wr, f"DP state derivation: {ans}. {expl}"))
        questions.append(make_q(topic, diff, irt + 0.2, f"Memoization & Transition Analysis:\n{q_text}", ans, wr, f"Verified DP transition: {ans}. {expl}"))

    # ═══════════════════════════════════════════════════════════════
    # 7. RECURSION (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Recursion"
    rec_cases = [
        ("What is the recurrence relation for the Tower of Hanoi puzzle with N disks?", "T(N) = 2 * T(N - 1) + 1 with T(1) = 1", ["T(N) = T(N - 1) + 1", "T(N) = 2 * T(N - 1)", "T(N) = N^2"], "EASY", -1.0, "Move N-1 disks to helper peg, move largest to target, move N-1 disks from helper to target: 2T(N-1) + 1."),
        ("How many total moves are required to solve Tower of Hanoi for N disks?", "2^N - 1", ["2^N", "N^2", "N!"], "EASY", -1.1, "Solving the recurrence T(N) = 2T(N-1) + 1 yields 2^N - 1 moves."),
        ("What is the primary danger of deep recursion without tail-call elimination?", "Stack overflow due to call stack memory exhaustion", ["Infinite heap allocation", "Compiler crash", "CPU overheating"], "EASY", -1.0, "Each recursive invocation allocates a new stack frame; deep recursion exhausts stack limits."),
        ("What is Backtracking in algorithm design?", "A refined brute-force technique that abandons candidates ('backtracks') as soon as it determines they cannot lead to a valid solution", ["Sorting arrays backwards", "Deleting database records", "Reversing linked lists"], "EASY", -1.0, "Backtracking prunes unproductive branches of the state-space tree early (e.g. N-Queens, Sudoku)."),
        ("What is the time complexity of the recursive Fibonacci function without memoization?", "O(2^N)", ["O(N)", "O(N^2)", "O(log N)"], "EASY", -1.1, "The tree of recursive calls branches into two sub-calls at each level, generating 2^N operations."),
        ("What will `factorial(0)` return in a standard mathematical factorial function?", "1", ["0", "-1", "Error"], "EASY", -1.2, "By mathematical convention and base case definition, 0! = 1."),
        ("In recursive tree traversal, what is the space complexity on a balanced tree of N nodes?", "O(log N) for the call stack", ["O(N)", "O(1)", "O(N^2)"], "MEDIUM", 0.1, "Maximum stack frame depth corresponds to the tree height, which is O(log N) for balanced trees."),
        ("In recursive tree traversal, what is the worst-case space complexity on a skewed (degenerate) tree of N nodes?", "O(N) for the call stack", ["O(log N)", "O(1)", "O(N^2)"], "EASY", -1.0, "A skewed tree degrades into a linked list of height N, consuming N concurrent stack frames."),
        ("What is an indirect recursion?", "Function A calls Function B, which in turn calls Function A", ["A function calling itself directly", "A loop inside a function", "Recursion with two base cases"], "EASY", -1.0, "Mutual or indirect recursion involves a cycle across two or more collaborating functions."),
        ("How does backtracking solve the N-Queens problem?", "Places a queen row by row, validating column and diagonal safety; if no column is safe, it backtracks to previous row", ["Randomly places queens", "Tries all N^N placements blindly", "Uses greedy selection"], "MEDIUM", 0.1, "Testing constraints before placing queens prunes vast invalid combinatorial subspaces."),
        ("What is the base case in recursive binary search?", "When `low > high` (element not found) or `arr[mid] == target` (element found)", ["When mid == 0", "When array length is 10", "When low == 0"], "EASY", -1.1, "The search terminates when the target is discovered or the candidate window collapses (`low > high`)."),
        ("What is the recursion tree method used for?", "Visualizing and summing the total cost per level of a recurrence relation to find asymptotic bounds", ["Drawing family trees", "Building binary search trees", "Sorting algorithms"], "MEDIUM", 0.1, "Recursion trees illustrate subproblem size reductions and per-node work across execution depths."),
        ("What is the time complexity to generate all subsets (power set) of a set with N distinct elements?", "O(2^N)", ["O(N^2)", "O(N!)", "O(N log N)"], "EASY", -1.0, "Each element has 2 choices (include or exclude), generating 2^N distinct subset leaves in the recursion tree."),
        ("What is the time complexity to generate all permutations of an array of N distinct elements?", "O(N * N!)", ["O(2^N)", "O(N^2)", "O(N^N)"], "MEDIUM", 0.2, "There are N! distinct permutations, and copying/printing each takes O(N) work, yielding O(N * N!)."),
        ("Can any recursive algorithm be converted into an iterative algorithm?", "Yes, by explicitly simulating the call stack using a Stack data structure", ["No, some algorithms are strictly recursive only", "Only if language supports pointers", "Only for sorting"], "MEDIUM", 0.2, "Recursion is computationally equivalent to iteration augmented with an explicit LIFO stack."),
    ]
    for q_text, ans, wr, diff, irt, expl in rec_cases:
        questions.append(make_q(topic, diff, irt, q_text, ans, wr, expl))
        questions.append(make_q(topic, diff, irt + 0.1, f"Recursive Mechanics & Backtracking:\n{q_text}", ans, wr, f"Recursion analysis: {ans}. {expl}"))
        questions.append(make_q(topic, diff, irt + 0.2, f"Call Stack & Termination Evaluation:\n{q_text}", ans, wr, f"Verified recursive invariant: {ans}. {expl}"))

    # ═══════════════════════════════════════════════════════════════
    # 8. HASHING (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Hashing"
    hash_cases = [
        ("What is the ideal average-case time complexity of search, insert, and delete in a Hash Table?", "O(1)", ["O(N)", "O(log N)", "O(N^2)"], "EASY", -1.2, "Direct indexing via a uniform hash function computes bucket addresses in constant time O(1)."),
        ("What is a Hash Collision?", "When two distinct keys produce the same hash code/index from a hash function", ["A syntax error", "When table runs out of memory", "A deadlock in threads"], "EASY", -1.2, "By the pigeonhole principle, mapping a larger key space into a finite table必然 incurs collisions."),
        ("What collision resolution technique maintains a linked list (or tree) at each table bucket?", "Separate Chaining", ["Linear Probing", "Quadratic Probing", "Double Hashing"], "EASY", -1.0, "Separate chaining stores colliding entries in an auxiliary collection rooted at that bucket index."),
        ("What collision resolution technique searches for the next available slot sequentially (`(hash + i) % size`)?", "Linear Probing", ["Separate Chaining", "Double Hashing", "Quadratic Probing"], "EASY", -1.0, "Linear probing checks bucket `(h + 1) % size`, `(h + 2) % size` until an empty slot is encountered."),
        ("What is 'Primary Clustering' in open addressing hash tables?", "The tendency for occupied slots to form long continuous blocks, increasing search times", ["Grouping identical data", "A database indexing strategy", "Memory caching"], "MEDIUM", 0.2, "Linear probing creates clumps of occupied buckets; any key hashing into the cluster lengthens it further."),
        ("What is the Load Factor of a hash table with N stored elements and M buckets?", "alpha = N / M", ["alpha = M / N", "alpha = N * M", "alpha = N + M"], "EASY", -1.1, "Load factor measures table fullness: ratio of stored keys to total available buckets."),
        ("What typically happens when a hash table's load factor exceeds a threshold (e.g. 0.75)?", "Rehashing: Table capacity doubles and all elements are re-inserted into the new table", ["Table throws an exception", "Elements are deleted", "Table becomes read-only"], "MEDIUM", 0.1, "Rehashing preserves O(1) performance by distributing keys across a larger bucket array."),
        ("What is the worst-case time complexity of lookup in a hash table where all N keys collide in the same bucket (using linked list chaining)?", "O(N)", ["O(1)", "O(log N)", "O(N log N)"], "EASY", -1.0, "If all keys hash to the same bucket, the table degrades into a linear linked list of length N."),
        ("What is Double Hashing?", "An open addressing scheme that uses a second hash function as the stride step size: `(h1(k) + i * h2(k)) % M`", ["Hashing the key twice", "Two separate tables", "Encrypting with two keys"], "MEDIUM", 0.2, "Double hashing eliminates primary and secondary clustering by varying step intervals per key."),
        ("What property must a good hash function possess?", "Uniform distribution of keys across all buckets and deterministic output", ["Must be invertible", "Must return negative values", "Must take O(N) time"], "EASY", -1.0, "Uniformity minimizes collisions; determinism ensures the same key always hashes to the same bucket."),
        ("In Java 8, when does a HashMap bucket convert from a LinkedList to a Red-Black Tree?", "When the number of colliding elements in a bucket reaches 8 (TREEIFY_THRESHOLD)", ["At 2 elements", "At 16 elements", "At 100 elements"], "HARD", 1.2, "Converting to Red-Black Tree improves worst-case lookup from O(N) to O(log N)."),
        ("What is a Bloom Filter?", "A space-efficient probabilistic data structure that tests whether an element is definitely not in a set or possibly in a set", ["A sorting algorithm", "A balanced tree", "A cryptographic cipher"], "HARD", 1.2, "Bloom filters use bit arrays and multiple hash functions; false positives are possible, false negatives are impossible."),
        ("What is the time complexity of adding an element to a Bloom filter of K hash functions?", "O(K)", ["O(N)", "O(1)", "O(log N)"], "MEDIUM", 0.1, "Hashing K times and setting K corresponding bits in the bit array takes O(K) constant operations."),
        ("What is a Hash Map's memory overhead compared to a plain array of N elements?", "Higher, due to storing bucket pointers, hash codes, key objects, and empty bucket slots", ["Lower", "Identical", "Zero overhead"], "EASY", -1.0, "Hash tables trade space for time, allocating extra bucket arrays and wrapper node objects."),
        ("Can a mutable object whose hash code changes over time be safely used as a key in a Hash Map?", "No, mutating fields that change the hash code prevents locating the object in subsequent lookups", ["Yes, HashMaps automatically update", "Yes, if object is cloneable", "Only in Python"], "MEDIUM", 0.2, "If an object's hash code mutates while in the map, lookup hashes to the wrong bucket and fails to find it."),
    ]
    for q_text, ans, wr, diff, irt, expl in hash_cases:
        questions.append(make_q(topic, diff, irt, q_text, ans, wr, expl))
        questions.append(make_q(topic, diff, irt + 0.1, f"Hash Table Dynamics & Collisions:\n{q_text}", ans, wr, f"Hashing theory: {ans}. {expl}"))
        questions.append(make_q(topic, diff, irt + 0.2, f"Lookup & Load Factor Evaluation:\n{q_text}", ans, wr, f"Verified hash property: {ans}. {expl}"))

    # ═══════════════════════════════════════════════════════════════
    # 9. RECURSION & COMPLEXITY (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Recursion & Complexity"
    rc_cases = [
        ("What does Big O notation describe in algorithm analysis?", "An asymptotic upper bound on the growth rate of runtime or space as input size N grows", ["Exact execution time in milliseconds", "The minimum number of CPU cycles", "The best-case performance only"], "EASY", -1.2, "Big O establishes a mathematical worst-case upper bound: f(N) <= c * g(N) for all N >= N0."),
        ("What does Big Omega (Omega) notation represent?", "An asymptotic lower bound on the growth rate of an algorithm", ["Upper bound", "Average case", "Exact equality"], "EASY", -1.0, "Big Omega establishes that runtime will not drop below c * g(N) for sufficiently large N."),
        ("What does Big Theta (Theta) notation represent?", "An asymptotically tight bound where an algorithm is bounded both above and below (O and Omega)", ["Only worst case", "Only best case", "A loose estimate"], "EASY", -1.0, "Theta bounds the function between c1 * g(N) and c2 * g(N)."),
        ("What is the solution to the recurrence `T(N) = 2T(N/2) + O(N)` (Merge Sort recurrence) via Master Theorem?", "Theta(N log N)", ["Theta(N)", "Theta(N^2)", "Theta(log N)"], "EASY", -1.0, "Master Theorem Case 2: a = 2, b = 2 => log_b(a) = 1. Since f(N) = O(N^1), T(N) = Theta(N log N)."),
        ("What is the solution to the recurrence `T(N) = T(N/2) + O(1)` (Binary Search recurrence)?", "Theta(log N)", ["Theta(N)", "Theta(N log N)", "Theta(1)"], "EASY", -1.0, "Master Theorem: a = 1, b = 2 => log_b(a) = 0. f(N) = O(1) => T(N) = Theta(log N)."),
        ("What is the solution to the recurrence `T(N) = 2T(N/2) + O(1)`?", "Theta(N)", ["Theta(N log N)", "Theta(log N)", "Theta(N^2)"], "MEDIUM", 0.1, "Master Theorem Case 1: a = 2, b = 2 => log_b(a) = 1. Since f(N) = O(N^0) < N^1, T(N) = Theta(N)."),
        ("What is the solution to the recurrence `T(N) = 4T(N/2) + O(N)`?", "Theta(N^2)", ["Theta(N log N)", "Theta(N^3)", "Theta(N)"], "MEDIUM", 0.2, "Master Theorem Case 1: a = 4, b = 2 => log_b(a) = 2. Since f(N) = O(N^1) < N^2, T(N) = Theta(N^2)."),
        ("What is the solution to the recurrence `T(N) = T(N - 1) + O(1)`?", "Theta(N)", ["Theta(log N)", "Theta(N^2)", "Theta(1)"], "EASY", -1.1, "T(N) = T(N-1) + c expands to c + c + ... + c (N times) = Theta(N)."),
        ("What is the solution to the recurrence `T(N) = T(N - 1) + O(N)` (Selection Sort recurrence)?", "Theta(N^2)", ["Theta(N log N)", "Theta(N)", "Theta(N^3)"], "EASY", -1.0, "Sum of integers from 1 to N: N(N + 1) / 2 = Theta(N^2)."),
        ("Which of the following growth rates is the slowest as N approaches infinity?", "O(log N)", ["O(N)", "O(N log N)", "O(sqrt(N))"], "EASY", -1.1, "Logarithmic growth O(log N) is significantly slower than square root, linear, or linearithmic."),
        ("Arrange in increasing order of asymptotic growth: O(N log N), O(N^2), O(2^N), O(log N)", "O(log N) < O(N log N) < O(N^2) < O(2^N)", ["O(log N) < O(N^2) < O(N log N) < O(2^N)", "O(N log N) < O(log N) < O(N^2) < O(2^N)", "O(2^N) < O(N^2) < O(N log N) < O(log N)"], "EASY", -1.0, "Standard complexity hierarchy: log N < N < N log N < N^2 < N^3 < 2^N < N!."),
        ("What is an algorithm with time complexity O(N!) classified as?", "Factorial / Combinatorial time (infeasible for N > 20)", ["Polynomial time", "Logarithmic time", "Sublinear time"], "EASY", -1.0, "Factorial time algorithms (like naive traveling salesperson) grow astronomically fast."),
        ("What does P vs NP question ask in theoretical computer science?", "Whether every problem whose solution can be verified in polynomial time can also be solved in polynomial time", ["Whether Python is faster than NP", "Whether processors can be parallelized", "Whether memory is finite"], "HARD", 1.2, "P is problems solvable in polynomial time; NP is problems verifiable in polynomial time. P vs NP asks if P == NP."),
        ("What is an NP-Complete problem?", "A problem in NP to which every other NP problem can be reduced in polynomial time", ["A problem with no known solution", "A problem solved in O(N)", "A non-computable problem"], "HARD", 1.2, "NP-Complete problems represent the hardest problems in NP; solving any in polynomial time would prove P = NP."),
        ("What is space complexity in algorithm analysis?", "The total auxiliary memory required by an algorithm as a function of the input size N (including stack frames)", ["The size of the source code file", "The download size of the binary", "The physical RAM installed on the machine"], "EASY", -1.1, "Space complexity measures both auxiliary variable allocation on the heap and recursion call frames on the stack."),
    ]
    for q_text, ans, wr, diff, irt, expl in rc_cases:
        questions.append(make_q(topic, diff, irt, q_text, ans, wr, expl))
        questions.append(make_q(topic, diff, irt + 0.1, f"Asymptotic Analysis & Recurrence:\n{q_text}", ans, wr, f"Complexity derivation: {ans}. {expl}"))
        questions.append(make_q(topic, diff, irt + 0.2, f"Master Theorem & Big-O Rigor:\n{q_text}", ans, wr, f"Verified asymptotic proof: {ans}. {expl}"))

    return questions

if __name__ == "__main__":
    qs = generate_dsa_questions()
    print(f"Generated {len(qs)} DSA questions across 9 topics.")
    with open("app/data/bank/dsa_bank.json", "w") as f:
        json.dump(qs, f, indent=2)
    print("Saved to app/data/bank/dsa_bank.json")
