"""
Core Computer Science & Data Structures / Algorithms question bank for campus technical placements.
Covers:
- Core CS: Operating Systems, Database Management, Computer Networks, Object-Oriented Design.
- DSA: Arrays & Strings, Linked Lists, Stacks & Queues, Trees & Graphs, Sorting & Searching, Dynamic Programming, Recursion & Complexity.
"""
from app.models.content import DifficultyLevel

CS_DSA_QUESTIONS = [
    # ═══════════════════════════════════════════════════════════════
    # OPERATING SYSTEMS (15 Questions)
    # ═══════════════════════════════════════════════════════════════
    {
        "topic": "Operating Systems", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "What is the primary difference between a process and a thread?",
        "explanation": "A process has its own isolated address space, while threads within the same process share the process's code, data, and address space.",
        "options": [("Threads do not have execution context", False), ("Threads within a process share the same address space", True), ("Processes share memory by default", False), ("Threads cannot be scheduled by OS", False)],
    },
    {
        "topic": "Operating Systems", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "Which CPU scheduling algorithm gives the minimum average waiting time for a given set of processes?",
        "explanation": "Shortest Job First (SJF) is proven optimal in terms of minimizing average waiting time.",
        "options": [("First-Come, First-Served (FCFS)", False), ("Shortest Job First (SJF)", True), ("Round Robin (RR)", False), ("Priority Scheduling", False)],
    },
    {
        "topic": "Operating Systems", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "What is 'thrashing' in an operating system?",
        "explanation": "Thrashing occurs when the CPU spends significantly more time swapping pages into and out of memory than executing actual process instructions.",
        "options": [("Excessive disk fragmentation", False), ("CPU spending excessive time swapping pages rather than executing instructions", True), ("Deadlock between two processes", False), ("Corrupted partition table", False)],
    },
    {
        "topic": "Operating Systems", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "Which of the following is NOT a necessary condition for deadlock (Coffman conditions)?",
        "explanation": "The four Coffman conditions are: Mutual Exclusion, Hold and Wait, No Preemption, and Circular Wait. Preemption breaks deadlock.",
        "options": [("Mutual Exclusion", False), ("Circular Wait", False), ("Hold and Wait", False), ("Preemption", True)],
    },
    {
        "topic": "Operating Systems", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "What mechanism does the CPU use to transition from user mode to kernel mode?",
        "explanation": "A system call or hardware interrupt triggers a mode bit switch from user mode (1) to kernel mode (0).",
        "options": [("Context switch", False), ("System call or interrupt", True), ("Direct memory access", False), ("Paging fault", False)],
    },
    {
        "topic": "Operating Systems", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "In demand paging, what happens when a process references a page that is marked invalid in the page table?",
        "explanation": "The memory management unit (MMU) raises a Page Fault interrupt, transferring control to the OS page fault handler.",
        "options": [("Segmentation Fault", False), ("Page Fault interrupt", True), ("System reboot", False), ("Bus error", False)],
    },
    {
        "topic": "Operating Systems", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "What is the difference between a binary semaphore and a mutex?",
        "explanation": "A mutex has ownership (the thread that locks it must unlock it), whereas a binary semaphore can be signaled/unlocked by any thread.",
        "options": [("Semaphores only support spin-waiting", False), ("A mutex has ownership semantics; only the locking thread can unlock it", True), ("Binary semaphores allow count up to 10", False), ("There is no difference in OS theory", False)],
    },
    {
        "topic": "Operating Systems", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "What is the Belady's Anomaly in page replacement algorithms?",
        "explanation": "Belady's Anomaly is the phenomenon where increasing the number of page frames results in an increase in the number of page faults (observable in FIFO).",
        "options": [("LRU performance degrades with large frames", False), ("More page frames lead to more page faults under FIFO", True), ("Cache hit ratio drops to zero", False), ("Deadlock occurs during paging", False)],
    },
    {
        "topic": "Operating Systems", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "Which algorithm is used in operating systems for deadlock avoidance?",
        "explanation": "Banker's Algorithm tests for safety by simulating the allocation of predetermined maximum possible amounts of all resources.",
        "options": [("Round Robin", False), ("Banker's Algorithm", True), ("Dijkstra's Shortest Path", False), ("Kruskal's Algorithm", False)],
    },
    {
        "topic": "Operating Systems", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "In a 32-bit virtual address space with 4 KB page size, how many entries are present in a single-level page table?",
        "explanation": "Page size = 4 KB = 2^12 bytes, so offset = 12 bits. Page number = 32 - 12 = 20 bits. Number of entries = 2^20 = 1,048,576 (1M entries).",
        "options": [("4,096", False), ("65,536", False), ("1,048,576 (2^20)", True), ("4,194,304", False)],
    },

    # ═══════════════════════════════════════════════════════════════
    # DATABASE MANAGEMENT (15 Questions)
    # ═══════════════════════════════════════════════════════════════
    {
        "topic": "Database Management", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "What does the 'A' in the ACID properties of database transactions stand for?",
        "explanation": "A stands for Atomicity: either all operations in a transaction succeed, or the entire transaction is rolled back.",
        "options": [("Availability", False), ("Atomicity", True), ("Authorization", False), ("Authentication", False)],
    },
    {
        "topic": "Database Management", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "Which SQL clause is used to filter groups created by the GROUP BY clause?",
        "explanation": "HAVING filters groups of rows, whereas WHERE filters individual rows before grouping.",
        "options": [("WHERE", False), ("HAVING", True), ("ORDER BY", False), ("LIMIT", False)],
    },
    {
        "topic": "Database Management", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "What is a Foreign Key in a relational database?",
        "explanation": "A foreign key is a field (or collection of fields) in one table that uniquely identifies a row of another table (referential integrity).",
        "options": [("A key that encrypts data", False), ("A field linking to the Primary Key of another table to maintain referential integrity", True), ("A secondary index for text search", False), ("A unique timestamp field", False)],
    },
    {
        "topic": "Database Management", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "A relation is in Boyce-Codd Normal Form (BCNF) if and only if for every functional dependency X -> Y:",
        "explanation": "In BCNF, for every non-trivial functional dependency X -> Y, X must be a superkey.",
        "options": [("Y is a prime attribute", False), ("X is a superkey", True), ("X is not a candidate key", False), ("Y is functionally dependent on all keys", False)],
    },
    {
        "topic": "Database Management", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "Why are B+ Trees preferred over B-Trees for database indexing on disk storage?",
        "explanation": "In B+ Trees, internal nodes only store keys (higher fanout/less disk I/O), and all data pointers are stored in leaf nodes linked sequentially for fast range scans.",
        "options": [("B+ Trees take less RAM", False), ("B+ Trees store all records at leaves linked for efficient sequential range queries", True), ("B-Trees cannot store strings", False), ("B+ Trees do not require rebalancing", False)],
    },
    {
        "topic": "Database Management", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "Which isolation level prevents 'Dirty Read', 'Non-Repeatable Read', and 'Phantom Read' anomalies?",
        "explanation": "SERIALIZABLE is the highest ANSI SQL isolation level and eliminates all three concurrency phenomena.",
        "options": [("READ UNCOMMITTED", False), ("READ COMMITTED", False), ("REPEATABLE READ", False), ("SERIALIZABLE", True)],
    },
    {
        "topic": "Database Management", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "In relational algebra, what is the equivalent of the SQL 'CROSS JOIN'?",
        "explanation": "A Cartesian Product (X) computes all possible ordered pairs of tuples from two relations.",
        "options": [("Theta join", False), ("Natural join", False), ("Cartesian Product", True), ("Projection", False)],
    },

    # ═══════════════════════════════════════════════════════════════
    # COMPUTER NETWORKS (15 Questions)
    # ═══════════════════════════════════════════════════════════════
    {
        "topic": "Computer Networks", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "At which layer of the OSI model does the Internet Protocol (IP) operate?",
        "explanation": "IP operates at Layer 3: Network Layer, handling logical addressing and packet routing.",
        "options": [("Data Link Layer", False), ("Network Layer", True), ("Transport Layer", False), ("Application Layer", False)],
    },
    {
        "topic": "Computer Networks", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "What protocol is used to map an IP address to a physical MAC address on a local network?",
        "explanation": "Address Resolution Protocol (ARP) translates an IPv4 address into a physical MAC hardware address.",
        "options": [("DHCP", False), ("ARP", True), ("DNS", False), ("ICMP", False)],
    },
    {
        "topic": "Computer Networks", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "What are the three packets exchanged in a standard TCP Three-Way Handshake to establish a connection?",
        "explanation": "The sequence is: SYN (from client) -> SYN-ACK (from server) -> ACK (from client).",
        "options": [("ACK, SYN, FIN", False), ("SYN, SYN-ACK, ACK", True), ("SYN, ACK, DATA", False), ("RST, SYN, ACK", False)],
    },
    {
        "topic": "Computer Networks", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "How many usable host IP addresses are available in a subnet with CIDR notation /26?",
        "explanation": "A /26 subnet has 32 - 26 = 6 host bits => 2^6 = 64 total addresses. Excluding network and broadcast address yields 64 - 2 = 62 usable hosts.",
        "options": [("30", False), ("62", True), ("64", False), ("126", False)],
    },
    {
        "topic": "Computer Networks", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "In TCP Congestion Control, what happens to the congestion window (cwnd) when a packet loss is detected via 3 duplicate ACKs (Fast Retransmit)?",
        "explanation": "Under TCP Reno Fast Recovery, ssthresh is set to cwnd / 2 and cwnd is reduced to ssthresh + 3 (multiplicative decrease), avoiding a reset to 1 MSS.",
        "options": [("Reset to 1 MSS", False), ("Halved (cwnd = cwnd / 2) entering Fast Recovery", True), ("Doubled immediately", False), ("Unchanged", False)],
    },

    # ═══════════════════════════════════════════════════════════════
    # OBJECT-ORIENTED DESIGN (15 Questions)
    # ═══════════════════════════════════════════════════════════════
    {
        "topic": "Object-Oriented Design", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "Which OOP principle emphasizes wrapping data and the methods that operate on that data into a single unit while restricting direct external access?",
        "explanation": "Encapsulation bundles data and methods together and protects internal state via access specifiers.",
        "options": [("Inheritance", False), ("Encapsulation", True), ("Polymorphism", False), ("Association", False)],
    },
    {
        "topic": "Object-Oriented Design", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "What does the 'L' in the SOLID design principles stand for?",
        "explanation": "L stands for Liskov Substitution Principle: objects of a superclass should be replaceable with objects of its subclasses without breaking application behavior.",
        "options": [("Layered Architecture", False), ("Liskov Substitution Principle", True), ("Loose Coupling", False), ("Late Binding", False)],
    },
    {
        "topic": "Object-Oriented Design", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "Which design pattern ensures that a class has only one instance and provides a global access point to it?",
        "explanation": "Singleton Pattern restricts instantiation to one object.",
        "options": [("Factory Pattern", False), ("Singleton Pattern", True), ("Observer Pattern", False), ("Decorator Pattern", False)],
    },
    {
        "topic": "Object-Oriented Design", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "Which design pattern dynamically attaches additional responsibilities to an object as an alternative to subclassing?",
        "explanation": "Decorator Pattern attaches flexible responsibilities dynamically by wrapping the original component.",
        "options": [("Adapter Pattern", False), ("Decorator Pattern", True), ("Strategy Pattern", False), ("Composite Pattern", False)],
    },

    # ═══════════════════════════════════════════════════════════════
    # DATA STRUCTURES: ARRAYS & STRINGS (15 Questions)
    # ═══════════════════════════════════════════════════════════════
    {
        "topic": "Arrays & Strings", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "What is the time complexity to access an element at index i in a contiguous array?",
        "explanation": "Array memory address is base_address + (i * element_size), which is calculated in O(1) constant time.",
        "options": [("O(1)", True), ("O(log n)", False), ("O(n)", False), ("O(n^2)", False)],
    },
    {
        "topic": "Arrays & Strings", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "What is the time and space complexity of Kadane's algorithm for finding the Maximum Subarray Sum?",
        "explanation": "Kadane's algorithm computes the maximum subarray sum in a single pass O(N) using O(1) auxiliary space.",
        "options": [("O(N log N) time, O(N) space", False), ("O(N) time, O(1) space", True), ("O(N^2) time, O(1) space", False), ("O(N) time, O(N) space", False)],
    },
    {
        "topic": "Arrays & Strings", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "Which string searching algorithm precomputes a Prefix Function (pi array) to achieve O(N + M) worst-case search time?",
        "explanation": "Knuth-Morris-Pratt (KMP) algorithm computes longest proper prefix which is also suffix (pi array) avoiding redundant comparisons.",
        "options": [("Rabin-Karp", False), ("Knuth-Morris-Pratt (KMP)", True), ("Boyer-Moore", False), ("Aho-Corasick", False)],
    },

    # ═══════════════════════════════════════════════════════════════
    # LINKED LISTS, STACKS & QUEUES (15 Questions)
    # ═══════════════════════════════════════════════════════════════
    {
        "topic": "Linked Lists", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "What is the time complexity to insert a new node at the head of a singly linked list?",
        "explanation": "Inserting at the head requires creating a node, pointing its next to the current head, and updating the head pointer: O(1).",
        "options": [("O(1)", True), ("O(log n)", False), ("O(n)", False), ("O(n log n)", False)],
    },
    {
        "topic": "Linked Lists", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "How does Floyd's Cycle-Finding Algorithm (Tortoise and Hare) detect a loop in a linked list?",
        "explanation": "It advances two pointers: slow by 1 node and fast by 2 nodes. If a cycle exists, they are guaranteed to meet inside the loop.",
        "options": [("Hashing node values", False), ("Moving two pointers at different speeds (1 step and 2 steps); they meet if a cycle exists", True), ("Reversing the list", False), ("Checking if tail equals head", False)],
    },
    {
        "topic": "Stacks & Queues", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "Which data structure follows the Last-In-First-Out (LIFO) order?",
        "explanation": "A Stack operates on the LIFO principle: elements pushed last are popped first.",
        "options": [("Queue", False), ("Stack", True), ("Deque", False), ("Priority Queue", False)],
    },
    {
        "topic": "Stacks & Queues", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "What data structure is typically used to efficiently find the 'Next Greater Element' for all elements in an array in O(N) total time?",
        "explanation": "A Monotonic Decreasing Stack keeps candidates for the next greater element in O(N) aggregate time.",
        "options": [("Priority Queue", False), ("Monotonic Stack", True), ("Circular Queue", False), ("Hash Map only", False)],
    },

    # ═══════════════════════════════════════════════════════════════
    # TREES, GRAPHS, SORTING & SEARCHING (20 Questions)
    # ═══════════════════════════════════════════════════════════════
    {
        "topic": "Trees & Graphs", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "In a Binary Search Tree (BST), which traversal produces values in strictly ascending sorted order?",
        "explanation": "Inorder traversal visits Left Subtree -> Root -> Right Subtree, yielding sorted keys in a BST.",
        "options": [("Preorder", False), ("Inorder", True), ("Postorder", False), ("Level order", False)],
    },
    {
        "topic": "Trees & Graphs", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "What is the time complexity of Breadth-First Search (BFS) on a graph represented using an adjacency list?",
        "explanation": "BFS visits each vertex once and traverses each edge once: O(V + E).",
        "options": [("O(V * E)", False), ("O(V + E)", True), ("O(V^2)", False), ("O(E log V)", False)],
    },
    {
        "topic": "Trees & Graphs", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "Which algorithm is capable of finding single-source shortest paths in a directed graph containing negative edge weights (and detects negative weight cycles)?",
        "explanation": "Bellman-Ford algorithm relaxes all edges V-1 times and detects negative cycles in O(V * E). Dijkstra's algorithm fails with negative weights.",
        "options": [("Dijkstra's Algorithm", False), ("Bellman-Ford Algorithm", True), ("Floyd-Warshall", False), ("Prim's Algorithm", False)],
    },
    {
        "topic": "Sorting & Searching", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "What is the time complexity of Binary Search on a sorted array of size N?",
        "explanation": "Binary search halves the search space at each comparison: O(log N).",
        "options": [("O(1)", False), ("O(log N)", True), ("O(N)", False), ("O(N log N)", False)],
    },
    {
        "topic": "Sorting & Searching", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "Which of the following sorting algorithms is stable and guarantees O(N log N) worst-case time complexity?",
        "explanation": "Merge Sort guarantees O(N log N) time in all cases (worst, average, best) and is a stable sort.",
        "options": [("Quick Sort", False), ("Heap Sort", False), ("Merge Sort", True), ("Selection Sort", False)],
    },

    # ═══════════════════════════════════════════════════════════════
    # DYNAMIC PROGRAMMING & RECURSION (15 Questions)
    # ═══════════════════════════════════════════════════════════════
    {
        "topic": "Dynamic Programming", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "What two key characteristics indicate that a problem can be solved using Dynamic Programming?",
        "explanation": "Dynamic Programming applies to problems with: 1. Optimal Substructure and 2. Overlapping Subproblems.",
        "options": [("Greedy choice and sorted input", False), ("Optimal Substructure and Overlapping Subproblems", True), ("Divide and Conquer with independent subproblems", False), ("Linear growth and logarithmic height", False)],
    },
    {
        "topic": "Dynamic Programming", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "What is the time complexity of solving the 0/1 Knapsack Problem with N items and maximum capacity W using dynamic programming?",
        "explanation": "The DP table has dimensions (N+1) x (W+1), filled in O(N * W) pseudo-polynomial time.",
        "options": [("O(N log W)", False), ("O(N * W)", True), ("O(2^N)", False), ("O(N + W)", False)],
    },
    {
        "topic": "Recursion & Complexity", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "What condition must every recursive function have to prevent infinite recursion and stack overflow?",
        "explanation": "A base case specifies the terminating condition where the function returns without making further recursive calls.",
        "options": [("Global variable", False), ("Base case", True), ("Loop invariant", False), ("Static memory allocation", False)],
    },
    {
        "topic": "Recursion & Complexity", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "Using the Master Theorem, what is the asymptotic time complexity of the recurrence relation T(N) = 2T(N/2) + O(N)?",
        "explanation": "Here a=2, b=2, k=1. Since log_b(a) = log_2(2) = 1 = k, Case 2 applies: T(N) = O(N log N) (classic Merge Sort).",
        "options": [("O(N)", False), ("O(N log N)", True), ("O(N^2)", False), ("O(log N)", False)],
    },
    {
        "topic": "Recursion & Complexity", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "What is the worst-case space complexity of recursive Depth-First Search on a graph with V vertices due to call stack depth?",
        "explanation": "In a degenerate tree or linear chain graph, the recursion call stack can reach a depth of V frames: O(V).",
        "options": [("O(1)", False), ("O(log V)", False), ("O(V)", True), ("O(V^2)", False)],
    },
]
