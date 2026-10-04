"""
Curriculum definition: Subjects, Topics, and Lessons for CareerForge AI.
"""
from app.models.content import SubjectCategory

SUBJECTS_DATA = [
    {
        "name": "Quantitative Aptitude",
        "category": SubjectCategory.APTITUDE,
        "icon": "📐",
        "description": "Master numerical computation, commercial arithmetic, algebraic logic, and modern math for placement rounds.",
        "topics": [
            ("Percentages", "Calculation of percentages, successive percentage change, population formula, and expenditure balancing."),
            ("Profit & Loss", "Cost price, selling price, marked price, successive discounts, and dishonest dealer tricks."),
            ("Ratio & Proportion", "Direct and inverse proportions, compound ratios, partnership investments, and share distributions."),
            ("Averages", "Arithmetic mean, weighted averages, age problems, and replacement problems in cohorts."),
            ("Simple & Compound Interest", "Simple interest, compound interest compounded annually/half-yearly, difference between CI and SI."),
            ("Time & Work", "Work equivalence, man-days formula, efficiency ratios, and alternating work schedules."),
            ("Speed, Distance & Time", "Relative speed, average speed, problems on trains, and river boat/stream problems."),
            ("Number System", "Divisibility rules, unit digits, remainders, factors, prime numbers, and HCF/LCM applications."),
            ("Permutation & Combination", "Fundamental counting principle, linear and circular arrangements, and selection combinations."),
            ("Probability", "Classical probability, independent events, mutually exclusive events, conditional probability, and dice/cards."),
            ("Data Interpretation", "Tables, bar graphs, pie charts, and line graphs analysis for campus aptitude tests."),
            ("Ages & Mixtures", "Linear age ratios, alligation rule, replacement of liquids, and multi-component mixtures."),
        ]
    },
    {
        "name": "Logical Reasoning",
        "category": SubjectCategory.APTITUDE,
        "icon": "🧩",
        "description": "Develop critical deduction, abstract patterns, relational logic, and analytical problem-solving.",
        "topics": [
            ("Series & Patterns", "Number series, alphabet series, alternate series, difference of differences, and missing terms."),
            ("Coding-Decoding", "Letter shifting, reverse letter substitution, matrix coding, and deciphering message codes."),
            ("Blood Relations", "Family trees, coded relations, pointing to photographs, and multi-generational relationship trees."),
            ("Directions & Distances", "Cardinal compass navigation, turns, shortest displacement, shadow problems, and coordinate tracking."),
            ("Syllogisms", "Venn diagram deductions, categorical propositions, some/all/no statements, and possibility conclusions."),
            ("Seating Arrangement", "Linear single-row, double-row facing rows, circular arrangements, and complex tabular constraints."),
            ("Puzzles & Ranking", "Floor puzzles, day-month scheduling, comparison ranking, and box placement logic puzzles."),
            ("Clocks & Calendars", "Angle between clock hands, gains/losses in clocks, odd days in calendars, and day of any given date."),
            ("Statements & Conclusions", "Statement assumptions, course of action, strong/weak arguments, and cause-and-effect reasoning."),
        ]
    },
    {
        "name": "Verbal Ability",
        "category": SubjectCategory.APTITUDE,
        "icon": "📝",
        "description": "Strengthen technical business communication, vocabulary depth, grammar rules, and reading comprehension.",
        "topics": [
            ("Vocabulary & Usage", "High-frequency placement synonyms, antonyms, contextual vocabulary, and idiomatic expressions."),
            ("Sentence Completion", "Single and double blank completions testing contextual nuance, tone, and transitional words."),
            ("Error Detection", "Subject-verb agreement, pronoun antecedents, misplaced modifiers, tense consistency, and parallel structure."),
            ("Reading Comprehension", "Passage inference, central theme, tone of the author, and factual recall under timed conditions."),
            ("Grammar & Mechanics", "Active vs passive voice, direct to indirect speech transformations, prepositions, and conjunctions."),
            ("Para Jumbles", "Coherent paragraph ordering, mandatory pairs, opening/concluding sentences, and pronoun references."),
        ]
    },
    {
        "name": "Core Computer Science",
        "category": SubjectCategory.PROGRAMMING,
        "icon": "💻",
        "description": "Core computer science fundamentals frequently tested in technical MCQs and placement interview rounds.",
        "topics": [
            ("Operating Systems", "Process scheduling, threads, virtual memory, paging, deadlocks, semaphores, and file systems."),
            ("Database Management", "ER models, relational algebra, SQL queries, normalization (1NF to BCNF), indexing, and ACID transactions."),
            ("Computer Networks", "OSI & TCP/IP layers, routing algorithms, IP addressing & CIDR, TCP vs UDP, DNS, and HTTP/HTTPS."),
            ("Object-Oriented Design", "Encapsulation, inheritance, polymorphism, abstraction, design patterns, and SOLID principles."),
        ]
    },
    {
        "name": "Data Structures & Algorithms",
        "category": SubjectCategory.PROGRAMMING,
        "icon": "🌳",
        "description": "Algorithmic thinking, complexity analysis, and mastery of fundamental data structures.",
        "topics": [
            ("Arrays & Strings", "Contiguous storage, sliding window, two-pointer methods, prefix sums, and string matching."),
            ("Linked Lists", "Singly, doubly, and circular linked lists, pointer manipulation, cycle detection, and merge operations."),
            ("Stacks & Queues", "LIFO/FIFO paradigms, monotonic stacks, expression evaluation, circular queues, and BFS queues."),
            ("Trees & Graphs", "Binary trees, BST properties, tree traversals, DFS/BFS graph traversals, and shortest paths."),
            ("Sorting & Searching", "Binary search variants, quicksort, mergesort, heapsort, and stability analysis."),
            ("Dynamic Programming", "Memoization vs tabulation, optimal substructure, knapsack patterns, and longest common subsequence."),
            ("Recursion & Complexity", "Recurrence relations, Master theorem, recursion tree analysis, and asymptotic space/time complexity."),
        ]
    }
]

LESSONS_DATA = {
    "Percentages": [
        ("Fundamentals of Percentages", "Percentage means 'per hundred'. The symbol % denotes a fraction with denominator 100. To convert a fraction a/b to a percentage, multiply by 100: (a/b) * 100%.\n\nKey Fraction-to-Percentage Equivalence:\n- 1/2 = 50%\n- 1/3 = 33.33%\n- 1/4 = 25%\n- 1/5 = 20%\n- 1/6 = 16.67%\n- 1/8 = 12.5%\n- 1/9 = 11.11%\n- 1/12 = 8.33%", "Example: Express 3/8 as a percentage: (3/8)*100 = 37.5%."),
        ("Successive Percentage Changes", "When a value changes by a% and then further changes by b%, the net effective percentage change is:\nNet Change = [a + b + (ab / 100)]%\n\nNote: Use positive values for increases and negative values for decreases.\nIf price increases by 20% (+20) and then decreases by 10% (-10):\nNet Change = 20 - 10 + (20 * -10)/100 = 10 - 2 = +8% increase.", "Example: A car price rises by 25% then falls by 20%. Net = 25 - 20 - (500/100) = 0%. No net change."),
        ("Price, Consumption & Expenditure", "Expenditure = Price * Consumption.\nIf the price of a commodity increases by r%, to keep the expenditure constant, the consumption must be reduced by:\nReduction% = [r / (100 + r)] * 100%\n\nIf price decreases by r%:\nIncrease in consumption% = [r / (100 - r)] * 100%", "Example: If sugar price rises by 25%, consumption must reduce by (25/125)*100 = 20% to keep expenditure unchanged."),
    ],
    "Profit & Loss": [
        ("Cost Price, Selling Price & Margins", "Profit = SP - CP (when SP > CP)\nLoss = CP - SP (when CP > SP)\nProfit% = (Profit / CP) * 100\nLoss% = (Loss / CP) * 100\nAlways remember: Profit% and Loss% are calculated on the Cost Price (CP) unless explicitly stated otherwise.", "Example: Bought for $400, sold for $500. Profit = 100. Profit% = (100/400)*100 = 25%."),
        ("Marked Price & Successive Discounts", "Marked Price (MP) or List Price is the tag price before discount.\nDiscount = MP - SP\nDiscount% = (Discount / MP) * 100\nIf two successive discounts of d1% and d2% are offered:\nSingle Equivalent Discount = [d1 + d2 - (d1 * d2 / 100)]%", "Example: Successive discounts of 20% and 10% give equivalent discount = 20 + 10 - (200/100) = 28%."),
        ("Dishonest Merchants & False Weights", "When a merchant sells goods claiming to be at CP but uses a false weight:\nGain% = [Error / (True Value - Error)] * 100%\nOr: Gain% = [(True Weight - False Weight) / False Weight] * 100%", "Example: Using 900g for 1000g: Gain% = (100/900)*100 = 11.11%."),
    ],
    "Ratio & Proportion": [
        ("Properties of Ratios", "A ratio is a comparison of two quantities of the same kind by division: a:b = a/b.\nIf a:b = c:d, then a, b, c, d are in proportion, and product of extremes = product of means: a*d = b*c.\nTo combine A:B = x:y and B:C = p:q, scale so that B matches: A:B:C = (x*p) : (y*p) : (y*q).", "Example: A:B = 2:3, B:C = 4:5. Multiply first by 4, second by 3: A:B:C = 8:12:15."),
        ("Partnership & Investment Sharing", "Profit earned in a business partnership is directly proportional to the product of investment amount and the investment duration:\nProfit_A / Profit_B = (Capital_A * Time_A) / (Capital_B * Time_B)", "Example: A invests $1000 for 12 months, B invests $2000 for 6 months. Ratio = 12000 : 12000 = 1:1."),
    ],
    "Averages": [
        ("Arithmetic Mean & Weighted Averages", "Average = (Sum of all observations) / (Total number of observations).\nWeighted Average = (w1*x1 + w2*x2 + ... + wn*xn) / (w1 + w2 + ... + wn).\nWhen an existing member of value X is replaced by a new member of value Y, change in total = Y - X.", "Example: 10 students average 50kg. One replaces 60kg student and average rises to 52kg. New = 60 + (2*10) = 80kg."),
    ],
    "Simple & Compound Interest": [
        ("Simple Interest Formulas", "SI = (P * R * T) / 100, where P = Principal, R = Rate percent per annum, T = Time in years.\nAmount A = P + SI = P(1 + RT/100).", "Example: P = $10,000, R = 8%, T = 3 yrs. SI = (10000*8*3)/100 = $2,400."),
        ("Compound Interest & CI vs SI Difference", "A = P * (1 + R/100)^T\nCI = A - P = P * [(1 + R/100)^T - 1]\nFor 2 years, difference between CI and SI:\nCI - SI = P * (R / 100)^2", "Example: For $5,000 at 10% for 2 years, CI - SI = 5000 * (10/100)^2 = $50."),
    ],
    "Time & Work": [
        ("Unitary Work & Man-Days Equivalence", "If A can do a work in n days, work done by A in 1 day = 1/n.\nTotal work is conventionally taken as 1 unit, or the LCM of the days taken by individual workers.\nFormula: (M1 * D1 * H1) / W1 = (M2 * D2 * H2) / W2", "Example: 12 men complete a work in 10 days. 15 men take: (12*10)/15 = 8 days."),
        ("Pipes & Cisterns", "An inlet pipe fills in X hours => rate = +1/X.\nAn outlet/leak empties in Y hours => rate = -1/Y.\nNet filling rate = 1/X - 1/Y.", "Example: Pipe A fills in 6 hrs, Pipe B empties in 9 hrs. Combined = 1/6 - 1/9 = 1/18 => 18 hours to fill."),
    ],
    "Speed, Distance & Time": [
        ("Speed, Distance & Units", "Speed = Distance / Time.\nTo convert km/h to m/s: multiply by 5/18.\nTo convert m/s to km/h: multiply by 18/5.\nAverage Speed for equal distances: 2xy / (x + y).", "Example: 72 km/h in m/s = 72 * (5/18) = 20 m/s."),
        ("Relative Speed & Train Problems", "When two bodies move in opposite directions, Relative Speed = S1 + S2.\nWhen moving in the same direction, Relative Speed = |S1 - S2|.\nTime for a train of length L1 to pass a platform of length L2 = (L1 + L2) / Speed.", "Example: 150m train crosses a 250m bridge at 20 m/s. Time = (150+250)/20 = 20 seconds."),
    ],
    "Number System": [
        ("Divisibility & Remainder Theorems", "Divisibility by 3: sum of digits divisible by 3.\nDivisibility by 4: last two digits divisible by 4.\nDivisibility by 8: last three digits divisible by 8.\nDivisibility by 9: sum of digits divisible by 9.\nDivisibility by 11: difference between sum of digits at odd places and even places is 0 or multiple of 11.", "Example: In 48327*8, for divisibility by 11: (8+7+3+4) - (*+2+8) = 22 - (10+*) = 12 - *. Thus * = 1."),
    ],
    "Permutation & Combination": [
        ("Permutations vs Combinations", "Permutation = Arranging items where order matters: nPr = n! / (n - r)!\nCombination = Selecting items where order does not matter: nCr = n! / (r! * (n - r)!)\nKey relation: nPr = r! * nCr", "Example: Select 3 students from 10: 10C3 = (10*9*8)/(3*2*1) = 120 ways."),
    ],
    "Probability": [
        ("Probability Axioms & Events", "Probability P(E) = (Favorable outcomes) / (Total sample space outcomes).\n0 <= P(E) <= 1.\nP(A or B) = P(A) + P(B) - P(A and B).\nFor independent events: P(A and B) = P(A) * P(B).", "Example: Rolling two dice, probability of sum = 7 is 6/36 = 1/6."),
    ],
    "Data Interpretation": [
        ("Interpreting Charts & Graphs", "In tabular, bar, and pie charts, read axes and labels carefully. Calculate base year percentages accurately: % increase = [(New - Old) / Old] * 100%. In pie charts, 360 degrees corresponds to 100%.", "Example: An angle of 72 degrees in a pie chart represents (72/360)*100 = 20%."),
    ],
    "Ages & Mixtures": [
        ("Alligation Rule & Weighted Mixtures", "When two ingredients of prices c and d are mixed to produce a mixture of mean price m:\n(Quantity of Cheaper) / (Quantity of Dearer) = (d - m) / (m - c).", "Example: Mixing wheat at $15/kg and $20/kg for $18/kg: Ratio = (20-18)/(18-15) = 2:3."),
    ],
    "Series & Patterns": [
        ("Number & Letter Series Logic", "Inspect arithmetic differences, geometric multiples, square/cube sequences, prime series, and alternating operations (+3, -1, +3, -1).", "Example: 2, 5, 10, 17, 26, ? Sequence is n^2 + 1. Next is 6^2 + 1 = 37."),
    ],
    "Coding-Decoding": [
        ("Substitution & Shifting Ciphers", "Write the alphabet with positions 1-26 and reversed 26-1. Check forward shifts, backward shifts, and opposing letter pairs (A-Z, B-Y, C-X, etc.).", "Example: If SHIFT is TJJGU, each letter advances by +1. CODE becomes DPEF."),
    ],
    "Blood Relations": [
        ("Family Tree Mapping", "Use standard diagram conventions: Squares for males (+), Circles for females (-), Horizontal lines for siblings, Double horizontal lines for spouses (=), and Vertical drops for children.", "Example: 'The brother of my mother's husband is my...' Mother's husband = father. Father's brother = Paternal Uncle."),
    ],
    "Directions & Distances": [
        ("Compass & Vector Displacements", "North is up, South is down, East is right, West is left. Right turn from North is East. Right turn from South is West. Use Pythagoras theorem a^2 + b^2 = c^2 for shortest distance.", "Example: Walks 3km East, then 4km North. Distance from origin = sqrt(3^2 + 4^2) = 5km."),
    ],
    "Syllogisms": [
        ("Venn Diagrams for Deductive Logic", "Translate statements into circles: 'All A are B' (A circle inside B), 'Some A are B' (overlapping circles), 'No A are B' (disjoint circles). If a conclusion does not hold in ANY valid diagram, it does not follow.", "Example: All cats are animals. All animals breathe. Valid: All cats breathe."),
    ],
    "Seating Arrangement": [
        ("Linear & Circular Constraints", "In circular seating facing center: Right is counter-clockwise, Left is clockwise. In linear rows facing North: Right is to your right, Left is to your left. Lock absolute positions first.", "Example: 6 people around a table. A opposite B, C between A and D. Draw layout step by step."),
    ],
    "Puzzles & Ranking": [
        ("Analytical Constraint Satisfaction", "Build a matrix grid with attributes (Name, City, Profession). Place confirmed positive clues first, eliminate negatives, and resolve remaining cells.", "Example: 5 boxes stacked P to T. Q is 2 above S, T is at bottom. Fill known layers systematically."),
    ],
    "Clocks & Calendars": [
        ("Clock Angles & Calendar Odd Days", "Minute hand moves 6 deg/min. Hour hand moves 0.5 deg/min. Relative speed = 5.5 deg/min. Angle between hands at H:M is |30*H - (11/2)*M|.\nNormal year = 1 odd day, Leap year = 2 odd days.", "Example: Angle at 3:30 = |30(3) - 5.5(30)| = |90 - 165| = 75 degrees."),
    ],
    "Statements & Conclusions": [
        ("Logical Inference & Validity", "A conclusion must follow directly and unambiguously from the stated premises without assuming unstated external facts.", "Example: Statement: Most tech workers use laptops. Conclusion: Every tech worker owns a laptop (Invalid)."),
    ],
    "Vocabulary & Usage": [
        ("Contextual Words & Tone", "Identify root words (Latin/Greek prefixes like 'bene', 'mal', 'hyper', 'omni') to deduce meanings of unfamiliar vocabulary in placement rounds.", "Example: 'Benevolent' combines 'bene' (good) and 'vol' (wish) -> kindly and well-meaning."),
    ],
    "Sentence Completion": [
        ("Transition Clues & Nuance", "Look for transition markers: Contrast ('however', 'although', 'despite'), Continuation ('moreover', 'furthermore'), Cause-and-Effect ('consequently', 'therefore').", "Example: Despite his ____ demeanor, he had a fierce determination. (Contrasting word: calm/placid)."),
    ],
    "Error Detection": [
        ("Common Grammatical Traps", "Watch out for: Subject-Verb agreement when phrases separate them ('The box of apples was (not were) fresh'), dangling participles, and neither...nor using closest subject.", "Example: Neither the teacher nor the students were present."),
    ],
    "Reading Comprehension": [
        ("Active Skimming & Theme Extraction", "Read the first and last sentence of each paragraph for structure. Distinguish between explicitly stated facts and reasonable inferences.", "Example: Focus on the author's primary argument and main purpose."),
    ],
    "Grammar & Mechanics": [
        ("Voice, Mood & Speech Rules", "In passive voice: Subject receives action. Object + auxiliary verb + past participle + by + agent.\nIn indirect speech: Present tenses shift back to past tense when reporting verb is in past.", "Example: 'She said, \"I work here\"' -> She said that she worked there."),
    ],
    "Para Jumbles": [
        ("Paragraph Reconstruction Techniques", "Find the opening sentence (independent subject, introduces concept). Identify noun-pronoun pairs. Match chronological sequences and concluding thoughts.", "Example: Intro statement first, elaboration second, contrast third, summary fourth."),
    ],
    "Operating Systems": [
        ("Processes, Threads & Scheduling", "A process is a program in execution with its own virtual address space. A thread is a lightweight unit of execution sharing the process's code, data, and open files. Scheduling algorithms include FCFS, SJF, Round Robin, and Priority.", "Example: In Round Robin with time quantum q, if q is very large it degrades to FCFS."),
        ("Deadlocks & Synchronization", "Four Coffman conditions for deadlock: Mutual Exclusion, Hold and Wait, No Preemption, Circular Wait. Synchronization primitives include mutexes, semaphores, and condition variables.", "Example: Banker's algorithm avoids deadlock by checking for safe states before resource allocation."),
    ],
    "Database Management": [
        ("Relational Schema, Keys & Normalization", "Primary Key uniquely identifies a row. Foreign Key establishes referential integrity. Normal forms eliminate redundancy: 1NF (atomic values), 2NF (no partial dependency), 3NF (no transitive dependency), BCNF (every determinant is a candidate key).", "Example: A -> B where A is not a superkey violates BCNF."),
        ("ACID Properties & SQL Indexing", "ACID: Atomicity (all or nothing), Consistency (preserves invariants), Isolation (concurrent transactions don't interfere), Durability (persisted after commit). B-Tree indexes speed up lookups from O(N) to O(log N).", "Example: Use EXPLAIN ANALYZE in PostgreSQL to view query execution plans and index usage."),
    ],
    "Computer Networks": [
        ("OSI Layers & TCP/IP Model", "7 layers: Physical, Data Link, Network (IP, ICMP), Transport (TCP, UDP), Session, Presentation, Application (HTTP, DNS). TCP is connection-oriented with 3-way handshake (SYN, SYN-ACK, ACK); UDP is connectionless and low-latency.", "Example: DNS uses UDP port 53 for fast single-packet queries."),
    ],
    "Object-Oriented Design": [
        ("Four Pillars & SOLID Principles", "Encapsulation (data hiding), Inheritance (code reuse), Polymorphism (dynamic dispatch), Abstraction (hiding implementation). SOLID: Single responsibility, Open/Closed, Liskov substitution, Interface segregation, Dependency inversion.", "Example: Programming to interfaces rather than concrete classes satisfies Dependency Inversion."),
    ],
    "Arrays & Strings": [
        ("Contiguous Memory & Two-Pointer Strategies", "Arrays allow O(1) random access by memory offset calculation. Two-pointer technique solves sorted two-sum in O(N) time and O(1) space instead of O(N^2).", "Example: Left pointer at 0, right at N-1. If sum > target, decrement right; else increment left."),
    ],
    "Linked Lists": [
        ("Pointers & Node Traversal", "Linked list nodes store value and next pointer. Non-contiguous allocation allows O(1) insertion at head. Floyd's cycle-finding algorithm uses slow (1 step) and fast (2 steps) pointers.", "Example: If slow and fast pointers meet, a cycle exists in the linked list."),
    ],
    "Stacks & Queues": [
        ("LIFO and FIFO Abstractions", "Stack: Last-In-First-Out (push, pop, peek - O(1)). Queue: First-In-First-Out (enqueue, dequeue - O(1)). Monotonic stack maintains elements in strictly increasing/decreasing order for Next Greater Element.", "Example: Balanced parentheses matching uses a stack to match incoming closing brackets."),
    ],
    "Trees & Graphs": [
        ("Hierarchical & Graph Structures", "Binary Tree traversals: Preorder (Root, Left, Right), Inorder (Left, Root, Right - yields sorted order for BST), Postorder (Left, Right, Root). Graph representations: Adjacency Matrix O(V^2) or Adjacency List O(V + E).", "Example: BFS explores level-by-level using a queue; DFS explores branch-by-branch using a stack/recursion."),
    ],
    "Sorting & Searching": [
        ("Search Algorithms & Comparison Sorts", "Binary Search operates on sorted sequences in O(log N). Merge Sort guarantees O(N log N) worst-case time with O(N) auxiliary space. Quick Sort achieves O(N log N) average with O(1) extra space.", "Example: Binary search checks midpoint; if key < mid, search left half."),
    ],
    "Dynamic Programming": [
        ("Overlapping Subproblems & Optimal Substructure", "Dynamic programming solves problems by caching solutions to subproblems. Two styles: Top-down with Memoization (recursion + cache) and Bottom-up with Tabulation (iterative table filling).", "Example: Fibonacci DP avoids O(2^N) exponential explosion by storing dp[i] = dp[i-1] + dp[i-2]."),
    ],
    "Recursion & Complexity": [
        ("Base Cases & Asymptotic Analysis", "Every recursive algorithm requires a terminating base case. Big-O notation characterizes upper-bound growth: O(1) < O(log N) < O(N) < O(N log N) < O(N^2) < O(2^N) < O(N!).", "Example: Merging two sorted arrays of length N takes O(N) time."),
    ],
}
