"""
Programming fundamentals, language basics (Python, Java, C++), and remaining topic questions.
"""
from app.models.content import DifficultyLevel

PROGRAMMING_QUESTIONS = [
    # ═══════════════════════════════════════════════════════════════
    # VARIABLES & DATA TYPES (10 Questions)
    # ═══════════════════════════════════════════════════════════════
    {
        "topic": "Variables & Data Types", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "What is the size of a standard 32-bit integer in memory?",
        "explanation": "A 32-bit signed/unsigned integer occupies exactly 4 bytes (32 bits / 8 bits per byte = 4 bytes).",
        "options": [("2 bytes", False), ("4 bytes", True), ("8 bytes", False), ("16 bytes", False)],
    },
    {
        "topic": "Variables & Data Types", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "In Python, which of the following data types is IMMUTABLE?",
        "explanation": "Tuples, strings, and integers are immutable in Python. Lists, dictionaries, and sets are mutable.",
        "options": [("List", False), ("Dictionary", False), ("Tuple", True), ("Set", False)],
    },
    {
        "topic": "Variables & Data Types", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "What is the default value of a boolean variable in Java when declared as an uninitialized class field?",
        "explanation": "In Java, instance boolean variables default to false.",
        "options": [("true", False), ("false", True), ("null", False), ("0", False)],
    },
    {
        "topic": "Variables & Data Types", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "In C/C++, what does the 'volatile' keyword signify when preceding a variable declaration?",
        "explanation": "'volatile' instructs the compiler that the variable may change unexpectedly (e.g. by hardware or another thread), preventing optimization/caching in registers.",
        "options": [("The variable is stored on the GPU", False), ("Tells compiler not to optimize or cache reads because it can change externally", True), ("Makes the variable immutable", False), ("Allocates memory on heap", False)],
    },
    {
        "topic": "Variables & Data Types", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "What happens when integer overflow occurs in an unsigned 8-bit integer holding 255 when 1 is added?",
        "explanation": "An unsigned 8-bit integer wraps around modulo 256: (255 + 1) mod 256 = 0.",
        "options": [("Throws runtime exception", False), ("Wraps around to 0", True), ("Clamps to 255", False), ("Becomes -1", False)],
    },
    {
        "topic": "Variables & Data Types", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "According to the IEEE 754 standard for single-precision floating-point numbers, how many bits are allocated for sign, exponent, and mantissa respectively?",
        "explanation": "IEEE 754 32-bit float: 1 sign bit, 8 exponent bits, 23 mantissa (fraction) bits.",
        "options": [("1, 8, 23", True), ("1, 11, 52", False), ("1, 7, 24", False), ("2, 8, 22", False)],
    },

    # ═══════════════════════════════════════════════════════════════
    # CONTROL FLOW & FUNCTIONS (10 Questions)
    # ═══════════════════════════════════════════════════════════════
    {
        "topic": "Control Flow", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "What happens in a C/Java 'switch' statement if a 'break' statement is omitted from a matching case?",
        "explanation": "Execution falls through to the subsequent cases until a break is encountered or the switch terminates.",
        "options": [("A compile-time error occurs", False), ("Execution falls through into the next case statements", True), ("The switch restarts from the top", False), ("The loop breaks", False)],
    },
    {
        "topic": "Control Flow", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "What is the key difference between a 'while' loop and a 'do-while' loop?",
        "explanation": "A do-while loop evaluates its condition at the bottom, guaranteeing that the loop body executes at least once.",
        "options": [("while loop executes at least once", False), ("do-while loop always executes the body at least once", True), ("do-while cannot use break", False), ("while loops run faster", False)],
    },
    {
        "topic": "Functions", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "What is the difference between 'Pass by Value' and 'Pass by Reference'?",
        "explanation": "Pass by value passes a copy of the actual parameter, whereas pass by reference passes an alias/memory address so modifications affect the original argument.",
        "options": [("Pass by value modifies the caller variable", False), ("Pass by value passes a copy, while pass by reference passes the memory address allowing modification of the caller's variable", True), ("Pass by reference creates a deep copy", False), ("There is no difference in modern compilers", False)],
    },
    {
        "topic": "Functions", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "What is a 'Pure Function' in functional programming?",
        "explanation": "A pure function always returns the same output for the same inputs and produces no observable side effects (like modifying global state or I/O).",
        "options": [("A function written in C", False), ("A function with no return value", False), ("A function that returns the same output for identical arguments with no side effects", True), ("A recursive function", False)],
    },

    # ═══════════════════════════════════════════════════════════════
    # ARRAYS & STRINGS (10 Questions)
    # ═══════════════════════════════════════════════════════════════
    {
        "topic": "Arrays", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "What is the time complexity to insert an element at the beginning of a standard dynamic array of size N?",
        "explanation": "All N existing elements must be shifted one position to the right: O(N).",
        "options": [("O(1)", False), ("O(log N)", False), ("O(N)", True), ("O(N^2)", False)],
    },
    {
        "topic": "Arrays", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "What is the memory overhead of a 2D array allocated in row-major vs column-major order?",
        "explanation": "Both orderings take the same total memory; the difference lies in memory layout and CPU cache locality during row-wise vs column-wise traversal.",
        "options": [("Row-major uses double the memory", False), ("Total memory is identical; access performance depends on cache line locality", True), ("Column-major requires heap allocation", False), ("Row-major cannot be indexed in O(1)", False)],
    },
    {
        "topic": "Strings", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "In Java, why are String objects immutable?",
        "explanation": "String immutability ensures security, thread-safety, caching of hash codes, and enables String Interning in the String Pool.",
        "options": [("To reduce CPU clock cycles", False), ("For security, thread safety, and string pool memory sharing", True), ("Because Java has no pointers", False), ("To prevent string concatenation", False)],
    },
    {
        "topic": "Strings", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "What is the time complexity of checking if a string of length N is a palindrome using two pointers?",
        "explanation": "Two pointers move from opposite ends towards the center, comparing characters in N/2 steps: O(N).",
        "options": [("O(1)", False), ("O(log N)", False), ("O(N)", True), ("O(N^2)", False)],
    },

    # ═══════════════════════════════════════════════════════════════
    # PYTHON BASICS, JAVA & C++ (15 Questions)
    # ═══════════════════════════════════════════════════════════════
    {
        "topic": "Python Basics", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "What is the output of `bool([])` and `bool([0])` in Python?",
        "explanation": "An empty list is falsy (`False`), whereas a non-empty list `[0]` evaluates to truthy (`True`).",
        "options": [("True, False", False), ("False, True", True), ("False, False", False), ("True, True", False)],
    },
    {
        "topic": "Python Basics", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "What is the Global Interpreter Lock (GIL) in CPython?",
        "explanation": "The GIL is a mutex that prevents multiple native threads from executing Python bytecodes simultaneously, ensuring memory safety in CPython's reference counting.",
        "options": [("A compiler optimization tool", False), ("A mutex protecting CPython memory by allowing only one native thread to execute Python bytecode at a time", True), ("A security sandbox", False), ("A garbage collector algorithm", False)],
    },
    {
        "topic": "Python Basics", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "What is the difference between `@classmethod` and `@staticmethod` in Python?",
        "explanation": "`@classmethod` takes the class `cls` as its implicit first parameter, while `@staticmethod` takes no implicit first argument (neither self nor cls).",
        "options": [("Static methods can access instance variables", False), ("Class methods receive 'cls' as their first argument; static methods receive no implicit first argument", True), ("Class methods cannot be overridden", False), ("Static methods cannot be called on instances", False)],
    },
    {
        "topic": "Java Fundamentals", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "What is the difference between `==` and `.equals()` when comparing two String objects in Java?",
        "explanation": "`==` checks for reference identity (same memory address), whereas `.equals()` checks for value/character sequence equivalence.",
        "options": [("They are completely identical", False), ("`==` checks object reference address equality, whereas `.equals()` compares string content", True), ("`.equals()` only works on numbers", False), ("`==` compares content, `.equals()` compares address", False)],
    },
    {
        "topic": "Java Fundamentals", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "In Java, what does the `final` keyword indicate when applied to a class?",
        "explanation": "A `final` class cannot be extended or subclassed (e.g. `java.lang.String`).",
        "options": [("It cannot be instantiated", False), ("It cannot be inherited or subclassed", True), ("All its methods are static", False), ("It cannot implement interfaces", False)],
    },
    {
        "topic": "C++ Essentials", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "What is the difference between `malloc()` in C and `new` in C++?",
        "explanation": "`malloc()` allocates raw memory without invoking constructors, whereas `new` allocates memory and calls the class constructor (type-safe).",
        "options": [("malloc calls constructor", False), ("`new` calls class constructor and is type-safe; malloc allocates raw bytes without constructor", True), ("`new` allocates on stack", False), ("There is no difference", False)],
    },
    {
        "topic": "C++ Essentials", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "What is a 'Virtual Destructor' in C++ and why is it important?",
        "explanation": "If a base class has a virtual destructor, deleting a derived object via a base pointer invokes the derived class destructor first, preventing resource leaks.",
        "options": [("Prevents object destruction", False), ("Ensures the derived class destructor is called when deleting an object through a base pointer", True), ("Destroys objects automatically like garbage collection", False), ("Required for all static classes", False)],
    },

    # ═══════════════════════════════════════════════════════════════
    # HASHING & PUZZLES (10 Questions)
    # ═══════════════════════════════════════════════════════════════
    {
        "topic": "Hashing", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "What is the average time complexity of insertion, deletion, and lookup in a Hash Table with a good hash function?",
        "explanation": "With uniform distribution and low load factor, hash table operations execute in average O(1) time.",
        "options": [("O(1)", True), ("O(log N)", False), ("O(N)", False), ("O(N log N)", False)],
    },
    {
        "topic": "Hashing", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "What are the two common collision resolution techniques used in hash tables?",
        "explanation": "Separate Chaining (linked lists at bucket) and Open Addressing (Linear Probing, Quadratic Probing, Double Hashing).",
        "options": [("Divide and conquer & dynamic programming", False), ("Separate Chaining and Open Addressing", True), ("Quick sort and merge sort", False), ("Binary search and linear scan", False)],
    },
    {
        "topic": "Puzzles", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "You have 8 balls of identical look, but one is slightly heavier. What is the minimum number of weighings on a balance scale to guarantee finding the heavy ball?",
        "explanation": "Divide into 3 groups: 3, 3, 2. Weigh 3 vs 3. If equal, weigh remaining 2. If unequal, take the heavier 3 and weigh 1 vs 1. In all cases, 2 weighings suffice.",
        "options": [("1", False), ("2", True), ("3", False), ("4", False)],
    },
    {
        "topic": "Puzzles", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "A rope burns completely in 60 minutes, but burns non-uniformly. You have 2 such ropes. How can you measure exactly 45 minutes?",
        "explanation": "Light rope 1 at both ends and rope 2 at one end. When rope 1 finishes (30 min), light the other end of rope 2. Rope 2 burns out in another 15 min. Total = 30 + 15 = 45 min.",
        "options": [("Cut rope in half", False), ("Light rope 1 at both ends and rope 2 at one end; when 1 finishes, light other end of 2", True), ("Measure length with a ruler", False), ("Burn ropes sequentially", False)],
    },

    # ═══════════════════════════════════════════════════════════════
    # VOCABULARY & GRAMMAR (LEGACY TOPIC MAPPINGS) (10 Questions)
    # ═══════════════════════════════════════════════════════════════
    {
        "topic": "Vocabulary", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "Choose the synonym for: ADVERSITY",
        "explanation": "Adversity means difficulties or misfortune. Hardship is the direct synonym.",
        "options": [("Prosperity", False), ("Hardship", True), ("Happiness", False), ("Luxury", False)],
    },
    {
        "topic": "Vocabulary", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "Choose the antonym for: PROLIFIC",
        "explanation": "Prolific means producing much fruit or foliage or many works. Unproductive is its direct antonym.",
        "options": [("Productive", False), ("Abundant", False), ("Unproductive", True), ("Fertile", False)],
    },
    {
        "topic": "Grammar", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "Fill in the blank: She has been living in London ________ 2018.",
        "explanation": "'Since' is used with a specific point in time (2018). 'For' is used for a duration.",
        "options": [("for", False), ("since", True), ("from", False), ("during", False)],
    },
    {
        "topic": "Grammar", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "Choose the correct sentence:",
        "explanation": "'Between' is followed by objective case pronouns: 'between you and me', not 'between you and I'.",
        "options": [("This matter is between you and I.", False), ("This matter is between you and me.", True), ("This matter is between he and she.", False), ("This matter is among you and I.", False)],
    },
]
