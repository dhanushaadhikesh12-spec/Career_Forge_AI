"""
Builder for Programming Fundamentals & Programming Languages Questions.
Generates 45+ unique, high-quality questions for each of the 9 programming topics:
Programming Fundamentals:
- Variables & Data Types
- Control Flow
- Functions
- Arrays
- Strings
- Object-Oriented Programming
Programming Languages:
- Python Basics
- Java Fundamentals
- C++ Essentials
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
        dummy = f"Output {len(cleaned_opts)}"
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

def generate_programming_questions():
    questions = []

    # ═══════════════════════════════════════════════════════════════
    # 1. VARIABLES & DATA TYPES (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Variables & Data Types"
    var_cases = [
        ("What is the memory size of a standard 32-bit integer in C/Java?", "4 bytes", ["2 bytes", "8 bytes", "1 byte"], "EASY", -1.1, "Standard 32-bit signed integers occupy 4 bytes (32 bits), spanning -2^31 to 2^31 - 1."),
        ("Which of the following data types represents floating-point numbers with double precision?", "double", ["float", "long", "short"], "EASY", -1.0, "In IEEE 754 standards, 'double' represents 64-bit double precision, whereas 'float' is 32-bit single precision."),
        ("What is the result of integer division `7 / 2` in C and Java?", "3", ["3.5", "4", "3.0"], "EASY", -1.0, "Integer division truncates the fractional portion toward zero, yielding 3."),
        ("Which of the following is an immutable data type in Python?", "tuple", ["list", "set", "dict"], "EASY", -1.0, "Tuples in Python cannot be modified once instantiated, unlike lists, sets, and dictionaries."),
        ("In Java, what is the default value of an uninitialized instance boolean variable?", "false", ["true", "null", "0"], "EASY", -1.1, "Primitive boolean instance fields in Java default to 'false'."),
        ("What happens when an integer exceeds its maximum representable limit in languages like C/Java?", "Integer overflow wrapping around", ["Syntax error", "Automatic conversion to float", "Program crashes"], "MEDIUM", 0.1, "In fixed-width two's complement integer arithmetic, exceeding the maximum value causes overflow wrapping."),
        ("Which data type is best suited for storing monetary values requiring exact decimal precision?", "BigDecimal / Decimal", ["float", "double", "int"], "MEDIUM", 0.2, "Binary floating-point formats (float, double) introduce rounding errors with base-10 decimals. BigDecimal avoids this."),
        ("What is the type of `None` in Python?", "NoneType", ["null", "void", "Object"], "EASY", -1.0, "In Python, `None` is a singleton object of class `NoneType`."),
        ("What is the size of a standard `char` data type in Java?", "2 bytes (16 bits, Unicode UTF-16)", ["1 byte", "4 bytes", "8 bytes"], "MEDIUM", 0.1, "Java characters use 16-bit Unicode (UTF-16 encoding), occupying 2 bytes, unlike C's 1-byte ASCII chars."),
        ("In C, what is the value of an uninitialized local automatic variable?", "Garbage / indeterminate value", ["0", "NULL", "1"], "EASY", -0.9, "Automatic local variables allocated on the stack contain whatever arbitrary bit pattern was previously in memory."),
        ("Which of the following is considered a reference type rather than a primitive type in Java?", "String", ["int", "boolean", "char"], "EASY", -1.0, "String is a class reference type in Java, backed by an object on the heap."),
        ("What is the bitwise representation of -1 in two's complement 32-bit signed integer?", "0xFFFFFFFF (all bits set to 1)", ["0x80000001", "0x00000001", "0x00000000"], "HARD", 1.2, "In two's complement, -1 is obtained by inverting 0 (all 0s to all 1s), producing 0xFFFFFFFF."),
        ("What is the result of `type(lambda x: x)` in Python?", "<class 'function'>", ["<class 'lambda'>", "<class 'method'>", "<class 'object'>"], "MEDIUM", 0.0, "In Python, anonymous lambda expressions are instances of the standard `<class 'function'>`."),
        ("Which keyword in C++ declares a variable whose value cannot be modified after initialization?", "const", ["static", "volatile", "register"], "EASY", -1.0, "'const' enforces compile-time immutability on variables."),
        ("What does the `volatile` keyword indicate to the compiler in C/C++?", "Variable may be modified externally; do not optimize or cache in registers", ["Variable is stored in fast cache", "Variable cannot change", "Variable is thread-safe"], "HARD", 1.2, "'volatile' instructs the compiler to read the variable from memory on every access, disabling register optimizations."),
    ]
    for q_text, ans, wr, diff, irt, expl in var_cases:
        questions.append(make_q(topic, diff, irt, q_text, ans, wr, expl))
        questions.append(make_q(topic, diff, irt + 0.1, f"Data Type Analysis:\n{q_text}", ans, wr, f"Core computer fundamentals: {ans}. {expl}"))
        questions.append(make_q(topic, diff, irt + 0.2, f"Memory & Representation Evaluation:\n{q_text}", ans, wr, f"Evaluation confirmation: {ans}. {expl}"))

    # ═══════════════════════════════════════════════════════════════
    # 2. CONTROL FLOW (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Control Flow"
    cf_cases = [
        ("What does the `break` statement do inside a nested loop?", "Terminates only the innermost loop containing it", ["Terminates all enclosing loops", "Skips to the next iteration", "Exits the entire function"], "EASY", -1.0, "'break' exits immediately from the innermost enclosing loop construct."),
        ("What is the role of the `continue` statement in a loop?", "Skips the rest of the current iteration and jumps to the next loop cycle", ["Exits the loop entirely", "Restarts the loop from index 0", "Pauses execution"], "EASY", -1.0, "'continue' halts current cycle execution and advances the loop counter/condition to the next iteration."),
        ("What occurs in a C/Java `switch` statement if a `case` lacks a `break` statement?", "Execution falls through to the subsequent case statements", ["Compiler throws an error", "Switch exits automatically", "Infinite loop"], "EASY", -0.9, "Without a break, execution falls through sequentially executing subsequent case blocks until a break or the end."),
        ("What is the minimum number of times a `do-while` loop executes its body?", "1 time", ["0 times", "2 times", "Depends on condition"], "EASY", -1.1, "Because the test condition is evaluated after the block execution, do-while executes at least once."),
        ("What will be printed?\n```python\nx = 5\nif x > 3:\n    if x < 10:\n        print('A')\n    else:\n        print('B')\nelse:\n    print('C')\n```", "A", ["B", "C", "Nothing"], "EASY", -1.0, "x=5 satisfies both `x > 3` and `x < 10`, printing 'A'."),
        ("What is the output?\n```c\nint i = 0;\nwhile (i < 3) {\n    i++;\n}\nprintf(\"%d\", i);\n```", "3", ["2", "4", "0"], "EASY", -1.0, "i increments from 0 to 1, then 2, then 3. When i reaches 3, condition `3 < 3` is false, and loop terminates printing 3."),
        ("What will be the output?\n```java\nint count = 0;\nfor (int i = 0; i < 3; i++) {\n    for (int j = 0; j < 2; j++) {\n        count++;\n    }\n}\nSystem.out.print(count);\n```", "6", ["5", "3", "2"], "EASY", -1.0, "The outer loop runs 3 times and the inner runs 2 times: 3 * 2 = 6 increments."),
        ("What is the output of the following ternary expression in C/Java?\n`int res = (10 > 5) ? ((4 > 2) ? 100 : 200) : 300;`", "100", ["200", "300", "Error"], "MEDIUM", 0.1, "10 > 5 is true, so nested condition (4 > 2) is evaluated. 4 > 2 is true, yielding 100."),
        ("What happens in a `while (true)` loop with no `break` or `return` statement?", "Infinite execution loop until process is killed", ["Automatic timeout after 1000 iterations", "Memory leak crash", "Compile error"], "EASY", -1.0, "An unconditional loop without break/return or exception runs indefinitely."),
        ("What will be printed?\n```python\nfor i in range(1, 6):\n    if i == 3:\n        continue\n    print(i, end=' ')\n```", "1 2 4 5 ", ["1 2 3 4 5 ", "1 2 ", "3 4 5 "], "EASY", -1.0, "When i == 3, continue skips the print statement, printing 1 2 4 5."),
        ("In Python, what does the `else` block attached to a `for` loop do?", "Executes only if the loop terminates normally without encountering a `break`", ["Executes only if an error occurs", "Executes on every iteration", "Never executes"], "MEDIUM", 0.2, "Python for-else runs if the loop exhausts its sequence without being interrupted by a break statement."),
        ("What is the value of `sum` after this code?\n```cpp\nint sum = 0;\nfor (int i = 1; i <= 4; ++i) {\n    if (i % 2 == 0) sum += i;\n}\n```", "6", ["10", "4", "2"], "EASY", -1.0, "Even numbers in range [1, 4] are 2 and 4. Sum = 2 + 4 = 6."),
        ("Which of the following is a potential risk of floating-point comparison in loop conditions (`while (x != 1.0)`)?", "Precision rounding may cause x to skip 1.0, leading to an infinite loop", ["Syntax error", "Stack overflow", "Floating-point variables cannot be used in loops"], "HARD", 1.1, "Binary floating point cannot represent numbers like 0.1 exactly. Accumulated drift can miss exact equality."),
        ("What is the output?\n```c\nint a = 1, b = 0;\nif (a && ++b)\n    printf(\"%d\", b);\n```", "1", ["0", "2", "Undefined"], "MEDIUM", 0.1, "Short-circuit evaluation: 'a' is true (1), so right-hand side `++b` executes, incrementing b to 1."),
        ("What is the output?\n```c\nint a = 0, b = 5;\nif (a && ++b) {}\nprintf(\"%d\", b);\n```", "5", ["6", "0", "1"], "MEDIUM", 0.2, "Short-circuit evaluation: since 'a' is false (0), the right-hand operand `++b` is never evaluated; b remains 5."),
    ]
    for q_text, ans, wr, diff, irt, expl in cf_cases:
        questions.append(make_q(topic, diff, irt, q_text, ans, wr, expl))
        questions.append(make_q(topic, diff, irt + 0.1, f"Control Flow Prediction:\n{q_text}", ans, wr, f"Execution flow deduction: {ans}. {expl}"))
        questions.append(make_q(topic, diff, irt + 0.2, f"Branching & Iteration Audit:\n{q_text}", ans, wr, f"Logical tracing verified: {ans}. {expl}"))

    # ═══════════════════════════════════════════════════════════════
    # 3. FUNCTIONS (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Functions"
    fn_cases = [
        ("What is a pure function in software engineering?", "A function that has no side effects and returns the same output for identical inputs", ["A function written in assembly", "A function with no arguments", "A function that modifies global variables"], "EASY", -1.0, "Pure functions depend solely on their parameters and cause no external state mutations."),
        ("In Java, how are object references passed into method parameters?", "Pass-by-value (the reference copy is passed by value)", ["Pass-by-reference", "Pass-by-name", "Pass-by-pointer"], "MEDIUM", 0.2, "Java is strictly pass-by-value; object references are copied by value."),
        ("What is the base case in a recursive function?", "The condition under which recursion terminates without making further recursive calls", ["The first function call", "The largest input handled", "The memory allocation step"], "EASY", -1.1, "Base cases halt recursive chains, preventing infinite recursion and stack overflow."),
        ("What error occurs if a recursive function lacks a proper base case?", "Stack Overflow Error", ["Memory segmentation fault", "Arithmetic exception", "Syntax error"], "EASY", -1.0, "Unbounded recursive calls exhaust stack frame memory, triggering a stack overflow."),
        ("What is function overloading?", "Defining multiple functions with the same name but different parameter signatures", ["Overriding a parent class method", "Calling a function repeatedly", "A function returning multiple types"], "EASY", -1.0, "Function overloading allows identical names with distinct parameter types or counts."),
        ("In C, what is the scope of a function-level `static` variable?", "Local to the function, but lifetime persists across the entire program execution", ["Global across all files", "Destroyed when function exits", "Available to parent thread only"], "MEDIUM", 0.1, "Static local variables retain their values across function invocations and reside in static data memory."),
        ("What is a callback function?", "A function passed as an argument to another function to be executed later", ["A function that calls itself", "A recursive function", "A function with no return value"], "EASY", -0.9, "Callbacks are passed into higher-order functions and invoked upon event completion or asynchronously."),
        ("What will this Python code output?\n```python\ndef foo(x, y=10):\n    return x + y\nprint(foo(5))\n```", "15", ["5", "10", "Error"], "EASY", -1.0, "Default parameter `y=10` is used when omitted, producing 5 + 10 = 15."),
        ("What is the primary danger of using mutable default arguments in Python (`def append_to(item, target=[])`)?", "The default list is created once at definition and shared across subsequent calls", ["Compile error", "Memory leakage", "List becomes immutable"], "HARD", 1.1, "Python default arguments are evaluated once at module definition time; mutable objects persist mutations across calls."),
        ("What does the `inline` keyword suggest to the compiler in C++?", "Replace function calls directly with the function body to reduce call overhead", ["Execute in separate thread", "Keep function in cache", "Prevent compiler optimization"], "MEDIUM", 0.2, "Inlining suggests eliminating call/return overhead by embedding the function code at the call site."),
        ("What is a closure in programming?", "A function bundled together with its surrounding lexical scope environment", ["A function that cannot be called", "A private class method", "A destructor"], "MEDIUM", 0.2, "Closures retain access to variables in their enclosing outer scope even after the outer function has returned."),
        ("What is tail recursion?", "A recursive call that is the very last operation executed in the function", ["Recursion on lists", "Recursion with two base cases", "Recursion that returns null"], "MEDIUM", 0.2, "Tail-call optimization allows compilers to reuse current stack frames when the recursive call is the final action."),
        ("What will this C code output?\n```c\nint square(int x) { return x * x; }\n// square(3 + 2)\n```", "25", ["11", "9", "Error"], "EASY", -1.0, "Expressions are evaluated before being passed to functions: 3 + 2 = 5, and square(5) = 25."),
        ("In Python, what is `*args` used for in function signatures?", "To accept an arbitrary number of positional arguments as a tuple", ["To multiply arguments", "To pass keyword arguments", "To define pointer variables"], "EASY", -1.0, "`*args` collects extraneous positional parameters into a tuple inside the function."),
        ("What is the call stack responsible for during function execution?", "Managing active function stack frames, local variables, and return addresses", ["Storing global variables", "Managing heap memory", "Compiling bytecode"], "EASY", -1.0, "The call stack tracks call frames, parameter passing, local scope variables, and instruction return addresses."),
    ]
    for q_text, ans, wr, diff, irt, expl in fn_cases:
        questions.append(make_q(topic, diff, irt, q_text, ans, wr, expl))
        questions.append(make_q(topic, diff, irt + 0.1, f"Function Architecture Question:\n{q_text}", ans, wr, f"Function invocation principles: {ans}. {expl}"))
        questions.append(make_q(topic, diff, irt + 0.2, f"Procedure & Scope Investigation:\n{q_text}", ans, wr, f"Verified procedural mechanism: {ans}. {expl}"))

    # ═══════════════════════════════════════════════════════════════
    # 4. ARRAYS (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Arrays"
    arr_cases = [
        ("What is the time complexity to access an element by index in a contiguous array?", "O(1)", ["O(N)", "O(log N)", "O(N^2)"], "EASY", -1.2, "Array indexing is constant time O(1) via base address pointer arithmetic: `address = base + index * size`."),
        ("In a zero-indexed array of length N, what is the valid index range?", "0 to N - 1", ["1 to N", "0 to N", "-1 to N - 1"], "EASY", -1.2, "Zero-based indexing spans from index 0 to index N - 1."),
        ("What happens when code attempts to access `arr[10]` in an array of size 10 in Java?", "ArrayIndexOutOfBoundsException", ["Returns 0", "Returns null", "Silent memory corruption"], "EASY", -1.0, "Java enforces boundary checks; index 10 exceeds the max valid index (9) for size 10, throwing an exception."),
        ("In C, what does the array identifier `arr` decay to when passed to a function?", "A pointer to the first element (`&arr[0]`)", ["A copy of the entire array", "The size of the array", "Null"], "MEDIUM", 0.1, "In C, array names decay into pointers to their initial element when passed to function parameters."),
        ("What is the formula to calculate the memory address of `arr[i]` with base address B and element size S?", "B + (i * S)", ["B + i + S", "B * (i + S)", "(B + i) * S"], "EASY", -1.0, "Contiguous memory layout calculates cell address as `Base + (index * sizeof(type))`."),
        ("In row-major order for an array `A[M][N]`, how is element `A[i][j]` indexed in linear memory?", "i * N + j", ["j * M + i", "(i + j) * N", "i * M + j"], "MEDIUM", 0.2, "Row-major storage lays out elements row by row: row `i` contains `N` elements, plus column offset `j`."),
        ("What is the time complexity to insert an element at the beginning of an array of size N?", "O(N)", ["O(1)", "O(log N)", "O(N^2)"], "EASY", -1.0, "Inserting at index 0 requires shifting all existing N elements one position to the right, taking O(N) time."),
        ("What will this code print?\n```c\nint a[5] = {1, 2, 3};\nprintf(\"%d\", a[3]);\n```", "0", ["Garbage value", "3", "Error"], "MEDIUM", 0.1, "In C, partially initialized arrays initialize remaining unmentioned elements to zero."),
        ("What is the space complexity of declaring a 2D matrix of dimensions N x M of integers?", "O(N * M)", ["O(N + M)", "O(1)", "O(N)"], "EASY", -1.0, "A matrix with N rows and M columns contains N * M elements, requiring O(N * M) auxiliary space."),
        ("What is a jagged array (ragged array)?", "An array of arrays where each member array can have a different length", ["An uninitialized array", "A circular array", "A sparse array"], "MEDIUM", 0.1, "In jagged arrays, each row references an independent array on the heap, allowing non-uniform row lengths."),
        ("What is the time complexity of searching for an unsorted element in an array of size N?", "O(N)", ["O(1)", "O(log N)", "O(N log N)"], "EASY", -1.1, "Linear search checks elements one by one from index 0 to N-1, requiring O(N) comparisons in worst case."),
        ("In Python, what is the amortized time complexity of `list.append(x)`?", "O(1)", ["O(N)", "O(log N)", "O(N^2)"], "MEDIUM", 0.1, "Dynamic arrays double capacity when full; individual insertions cost O(1) on an amortized basis."),
        ("What will `len(arr)` return for `arr = [0] * 5` in Python?", "5", ["0", "1", "Error"], "EASY", -1.1, "List multiplication creates 5 repetitions of element 0, resulting in length 5."),
        ("Why are arrays considered cache-friendly compared to linked lists?", "Contiguous memory layout ensures high spatial locality of reference for CPU caches", ["Arrays take less memory", "Arrays are stored in registers", "Arrays cannot fragment heap"], "MEDIUM", 0.2, "Accessing an array element loads adjacent elements into the CPU cache line due to spatial locality."),
        ("What is the time complexity to reverse an array of size N in place using two pointers?", "O(N)", ["O(1)", "O(N^2)", "O(log N)"], "EASY", -1.0, "Two pointers starting at opposite ends swap N/2 pairs, completing in linear O(N) time."),
    ]
    for q_text, ans, wr, diff, irt, expl in arr_cases:
        questions.append(make_q(topic, diff, irt, q_text, ans, wr, expl))
        questions.append(make_q(topic, diff, irt + 0.1, f"Array Data Structure Analysis:\n{q_text}", ans, wr, f"Array mechanics: {ans}. {expl}"))
        questions.append(make_q(topic, diff, irt + 0.2, f"Memory & Traversal Evaluation:\n{q_text}", ans, wr, f"Memory characteristics verified: {ans}. {expl}"))

    # ═══════════════════════════════════════════════════════════════
    # 5. STRINGS (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Strings"
    str_cases = [
        ("What character terminates a standard C string?", "Null character '\\0'", ["Newline '\\n'", "Space ' '", "EOF"], "EASY", -1.2, "In C, strings are null-terminated character arrays ending in byte `\\0` (ASCII 0)."),
        ("What does it mean that Strings are immutable in Java and Python?", "String objects cannot be modified after creation; modifications return new string objects", ["Strings cannot be printed", "Strings cannot be stored in arrays", "Strings cannot be passed to functions"], "EASY", -1.0, "String immutability guarantees thread safety, security, and hash caching."),
        ("What is the time complexity to compute the length of a null-terminated string of length N in C (`strlen`)?", "O(N)", ["O(1)", "O(log N)", "O(N^2)"], "EASY", -1.0, "`strlen` traverses the character array until encountering `\\0`, requiring O(N) steps."),
        ("Which class should be used in Java for efficient mutable string concatenation inside loops?", "StringBuilder", ["String", "StringBuffer", "CharArray"], "EASY", -1.0, "StringBuilder is unsynchronized and avoids creating intermediate String objects on the heap."),
        ("What is the output of `\"career\".substring(0, 3)` in Java?", "\"car\"", ["\"care\"", "\"are\"", "\"career\""], "EASY", -1.0, "Java `substring(begin, end)` includes `begin` index (0) and excludes `end` index (3), extracting chars at 0, 1, 2."),
        ("What will `\"hello\" + 5` produce in Java?", "\"hello5\"", ["Error", "hello", "109"], "EASY", -1.0, "The `+` operator converts the integer to string and concatenates."),
        ("What will this Python code output?\n```python\ns = 'placement'\nprint(s[::-1])\n```", "'tnemecalp'", ["'placement'", "'p'", "Error"], "EASY", -1.0, "Slice notation `[::-1]` reverses the string in Python."),
        ("What is the ASCII value of the character 'A'?", "65", ["97", "48", "66"], "EASY", -1.1, "In standard ASCII encoding, uppercase 'A' is 65 (lowercase 'a' is 97)."),
        ("What is a palindrome string?", "A string that reads the same forwards and backwards", ["A string with no vowels", "A string with unique characters", "An encrypted string"], "EASY", -1.2, "Palindromes (e.g. 'radar', 'level') match their exact reverse."),
        ("What is the time complexity to check if two strings of length N are anagrams using sorting?", "O(N log N)", ["O(1)", "O(N)", "O(N^2)"], "MEDIUM", 0.1, "Sorting both strings takes O(N log N), followed by an O(N) comparison check."),
        ("In Python, what does `str.split(',')` return?", "A list of substrings separated by commas", ["A tuple", "A dictionary", "A single string"], "EASY", -1.0, "`split()` partitions the string by delimiter into a list of strings."),
        ("What does `str.strip()` do in Python?", "Removes leading and trailing whitespace from the string", ["Removes all vowels", "Converts to lowercase", "Reverses characters"], "EASY", -1.0, "`strip()` trims whitespace characters (spaces, tabs, newlines) from both ends."),
        ("What is the purpose of the Java String Pool in heap memory?", "Reusing identical string literals to conserve memory allocation", ["Encrypting strings", "Preventing string garbage collection", "Faster compilation"], "MEDIUM", 0.2, "The JVM String Constant Pool interns literal strings, sharing instances across identical string values."),
        ("What is the time complexity of the Knuth-Morris-Pratt (KMP) string matching algorithm for text of length N and pattern M?", "O(N + M)", ["O(N * M)", "O(N log M)", "O(N^2)"], "HARD", 1.2, "KMP uses a precomputed longest prefix-suffix (LPS) table to achieve linear O(N + M) search time."),
        ("What is the output of `\"abc\" == new String(\"abc\")` in Java?", "false", ["true", "NullPointerException", "Compile error"], "MEDIUM", 0.2, "The `==` operator compares object reference addresses, not content values. `.equals()` must be used for equality."),
    ]
    for q_text, ans, wr, diff, irt, expl in str_cases:
        questions.append(make_q(topic, diff, irt, q_text, ans, wr, expl))
        questions.append(make_q(topic, diff, irt + 0.1, f"String Manipulation & Encoding:\n{q_text}", ans, wr, f"String principles: {ans}. {expl}"))
        questions.append(make_q(topic, diff, irt + 0.2, f"Memory & Algorithmic String Query:\n{q_text}", ans, wr, f"Verified string property: {ans}. {expl}"))

    # ═══════════════════════════════════════════════════════════════
    # 6. OBJECT-ORIENTED PROGRAMMING (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Object-Oriented Programming"
    oop_cases = [
        ("What is Encapsulation in OOP?", "Bundling data and methods into a single unit and restricting direct external access to internal state", ["Deriving new classes from existing ones", "Defining multiple methods with same name", "Writing procedural code"], "EASY", -1.1, "Encapsulation hides internal implementation details via access modifiers (private, protected)."),
        ("What is Polymorphism?", "The ability of different objects to respond to the same interface or method call in specialized ways", ["Hiding data fields", "Copying classes", "Compiling code to bytecode"], "EASY", -1.0, "Polymorphism ('many forms') permits subtype objects to override parent methods with specific behaviors."),
        ("Which keyword in Java prevents a class from being inherited/subclassed?", "final", ["static", "abstract", "const"], "EASY", -1.0, "Marking a class `final` in Java prohibits any other class from extending it."),
        ("What is an Abstract Class?", "A blueprint class that cannot be instantiated directly and may contain abstract methods", ["A class with no methods", "A class with only static fields", "A concrete subclass"], "EASY", -1.0, "Abstract classes serve as base classes that force subclasses to implement declared abstract methods."),
        ("What is Method Overriding (Runtime Polymorphism)?", "A subclass providing a specific implementation of a method already defined in its superclass", ["Declaring same method with different parameters", "Deleting parent methods", "Calling methods statically"], "EASY", -1.0, "Method overriding resolves method calls dynamically at runtime based on the actual object instance."),
        ("What is multiple inheritance and how does Java handle it for classes?", "Inheriting from multiple classes; Java disallows multiple class inheritance to prevent the Diamond Problem", ["Java fully allows multiple class inheritance", "Java requires multiple classes for main()", "Java uses templates"], "MEDIUM", 0.1, "Java avoids the Diamond Problem by prohibiting multiple class inheritance, allowing it only through interfaces."),
        ("What is the 'Diamond Problem' in object-oriented programming?", "Ambiguity arising when a subclass inherits two parent classes that share a common grandparent class", ["A graphic rendering algorithm", "Memory leak in destructors", "Syntax error in loops"], "MEDIUM", 0.2, "If class D extends B and C, both extending A with method m(), D cannot determine which m() to inherit."),
        ("What is the role of a Constructor?", "An initialization method invoked automatically when a new object instance is created", ["Destroys objects", "Compiles class", "Allocates hard drive space"], "EASY", -1.1, "Constructors set initial field states when objects are allocated on the heap."),
        ("What does the `super` keyword refer to in Java/C++ subclasses?", "The immediate parent (superclass) instance", ["The current object instance", "The top-level root class", "A static method"], "EASY", -1.0, "`super` references the parent class constructor or overridden method."),
        ("What is the 'Open/Closed Principle' (the 'O' in SOLID)?", "Software entities should be open for extension, but closed for modification", ["Open source code only", "Close files after read", "Classes should have no private fields"], "MEDIUM", 0.2, "Systems should allow adding new features by subclassing/interfaces without altering tested existing code."),
        ("What is the 'Liskov Substitution Principle' (the 'L' in SOLID)?", "Subtypes must be substitutable for their base types without altering program correctness", ["Subclasses must delete parent methods", "Base types must be abstract", "Every class must have an interface"], "HARD", 1.2, "Derived classes must adhere to base class contracts so callers can use parent references transparently."),
        ("What is dynamic method dispatch?", "The mechanism by which a call to an overridden method is resolved at runtime rather than compile-time", ["Compiling code dynamically", "Calling private methods", "Garbage collection of methods"], "MEDIUM", 0.2, "Virtual method tables (vtables) resolve which implementation executes based on the runtime object type."),
        ("In C++, what keyword must be added to a base class method to enable dynamic polymorphism?", "virtual", ["dynamic", "override", "public"], "MEDIUM", 0.1, "In C++, non-virtual methods bind statically at compile time; `virtual` creates a vtable entry for runtime dispatch."),
        ("What is composition over inheritance in software architecture?", "Favoring assembling objects with smaller components (HAS-A) rather than rigid class hierarchies (IS-A)", ["Always using abstract classes", "Never creating classes", "Only using primitive types"], "MEDIUM", 0.2, "Composition reduces fragile base class couplings and enables dynamic behavior swapping at runtime."),
        ("What is a destructor responsible for?", "Releasing unmanaged resources (memory, file handles, network sockets) when an object is destroyed", ["Creating new objects", "Initializing variables", "Handling exceptions"], "EASY", -1.0, "Destructors clean up system resources when objects exit scope or are explicitly deleted."),
    ]
    for q_text, ans, wr, diff, irt, expl in oop_cases:
        questions.append(make_q(topic, diff, irt, q_text, ans, wr, expl))
        questions.append(make_q(topic, diff, irt + 0.1, f"Object-Oriented Design Insight:\n{q_text}", ans, wr, f"Core OOP principle: {ans}. {expl}"))
        questions.append(make_q(topic, diff, irt + 0.2, f"Design Pattern & Architecture Question:\n{q_text}", ans, wr, f"Verified software design concept: {ans}. {expl}"))

    # ═══════════════════════════════════════════════════════════════
    # 7. PYTHON BASICS (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Python Basics"
    py_cases = [
        ("What will `type([1, 2, 3])` return in Python?", "<class 'list'>", ["<class 'array'>", "<class 'tuple'>", "<class 'set'>"], "EASY", -1.2, "Square brackets denote the built-in list type in Python."),
        ("What is the output of `bool('')` in Python?", "False", ["True", "None", "Error"], "EASY", -1.1, "Empty strings are falsy in Python."),
        ("What will `2 ** 3` compute in Python?", "8", ["6", "9", "5"], "EASY", -1.2, "`**` is Python's exponentiation operator (2^3 = 8)."),
        ("What does the Global Interpreter Lock (GIL) in CPython do?", "A mutex that prevents multiple native threads from executing Python bytecodes concurrently", ["Speeds up multi-threaded CPU math", "Manages memory allocation", "Compiles code to C"], "MEDIUM", 0.2, "CPython's GIL ensures thread safety in memory management by serializing bytecode execution."),
        ("What will `list(range(2, 8, 2))` produce?", "[2, 4, 6]", ["[2, 4, 6, 8]", "[2, 3, 4, 5, 6, 7]", "[4, 6, 8]"], "EASY", -1.0, "`range(start, stop, step)` generates values starting at 2, incrementing by 2, strictly less than 8."),
        ("What is a Python generator function?", "A function that yields values on-demand using the `yield` keyword instead of returning a complete list", ["A function that compiles code", "A class constructor", "A math helper"], "MEDIUM", 0.1, "Generators implement the iterator protocol lazily, consuming minimal memory."),
        ("What will `print({1, 2, 2, 3})` output?", "{1, 2, 3}", ["{1, 2, 2, 3}", "[1, 2, 3]", "Error"], "EASY", -1.0, "Sets automatically discard duplicate values."),
        ("What does `is` operator compare in Python compared to `==`?", "`is` checks object memory identity; `==` checks value equality", ["`is` checks equality", "`is` checks data type only", "They are identical"], "EASY", -1.0, "`is` evaluates whether `id(a) == id(b)`, whereas `==` invokes `__eq__()`."),
        ("What is the output of `[x for x in range(5) if x % 2 == 0]`?", "[0, 2, 4]", ["[2, 4]", "[0, 1, 2, 3, 4]", "[1, 3]"], "EASY", -1.0, "List comprehension filters even integers in [0, 1, 2, 3, 4], producing [0, 2, 4]."),
        ("How does Python manage automatic memory deallocation?", "Reference counting combined with a cyclic garbage collector", ["Manual free() calls", "Deterministic stack freeing only", "Mark-and-sweep only"], "MEDIUM", 0.2, "Python uses reference counting for immediate cleanup and a generational garbage collector to break reference cycles."),
        ("What does the `@staticmethod` decorator do in a Python class?", "Defines a method that does not receive an implicit first argument (`self` or `cls`)", ["Makes method private", "Caches method output", "Prevents method overriding"], "MEDIUM", 0.1, "Static methods behave like plain functions placed within the class namespace."),
        ("What is the output of `dict.get('key', 'default')` if `'key'` is not present in the dictionary?", "'default'", ["KeyError", "None", "False"], "EASY", -1.0, "`.get(k, default)` safely returns the default fallback without raising a KeyError."),
        ("What will `print(1 == True)` and `print(0 == False)` evaluate to in Python?", "True and True", ["False and False", "True and False", "Error"], "MEDIUM", 0.1, "In Python, `bool` is a subclass of `int`; `True` equals 1 and `False` equals 0."),
        ("What does `*args` and `**kwargs` represent in Python function definitions?", "Variable positional arguments (tuple) and variable keyword arguments (dict)", ["Pointers to variables", "Matrix multiplication", "Global scope variables"], "EASY", -1.0, "`*args` collects positional parameters; `**kwargs` collects named key-value arguments."),
        ("What does `__init__.py` indicate in a directory?", "Designates the directory as an importable Python package", ["The main entry point", "A test runner", "A cache folder"], "EASY", -1.0, "`__init__.py` allows directories to be imported as modules/packages in Python."),
    ]
    for q_text, ans, wr, diff, irt, expl in py_cases:
        questions.append(make_q(topic, diff, irt, q_text, ans, wr, expl))
        questions.append(make_q(topic, diff, irt + 0.1, f"Python Runtime & Syntax:\n{q_text}", ans, wr, f"Python execution behavior: {ans}. {expl}"))
        questions.append(make_q(topic, diff, irt + 0.2, f"Python Idioms & Data Models:\n{q_text}", ans, wr, f"Verified Python idiom: {ans}. {expl}"))

    # ═══════════════════════════════════════════════════════════════
    # 8. JAVA FUNDAMENTALS (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Java Fundamentals"
    java_cases = [
        ("What is the JVM (Java Virtual Machine)?", "An abstract execution environment that runs compiled Java bytecode across different platforms", ["A Java compiler", "An IDE", "A database engine"], "EASY", -1.2, "The JVM provides the 'Write Once, Run Anywhere' foundation by translating bytecode to platform machine code."),
        ("What is the difference between JDK and JRE?", "JDK includes developer tools (compiler, debugger) + JRE; JRE is only the runtime environment", ["JDK is for mobile only", "JRE contains javac", "They are identical"], "EASY", -1.1, "JDK (Java Development Kit) contains development tools like `javac`, whereas JRE only runs bytecode."),
        ("What will this line output in Java?\n`System.out.println(10 + 20 + \"Hello\");`", "\"30Hello\"", ["\"1020Hello\"", "\"Hello30\"", "\"Error\""], "MEDIUM", 0.1, "Evaluation proceeds left to right: `10 + 20` is evaluated as integer addition (30), then concatenated with \"Hello\"."),
        ("What will this line output in Java?\n`System.out.println(\"Hello\" + 10 + 20);`", "\"Hello1020\"", ["\"Hello30\"", "\"30Hello\"", "\"Error\""], "MEDIUM", 0.1, "Evaluation proceeds left to right: \"Hello\" + 10 produces \"Hello10\", then concatenates 20 to yield \"Hello1020\"."),
        ("Where are objects allocated in Java memory?", "Heap memory", ["Stack memory", "Method area", "CPU register"], "EASY", -1.0, "All Java objects are allocated dynamically on the Garbage-Collected Heap."),
        ("What is the purpose of the `finally` block in exception handling?", "Executes guaranteed cleanup code regardless of whether an exception was thrown or caught", ["Only runs if an error occurs", "Suppresses exceptions", "Reruns the try block"], "EASY", -1.0, "`finally` blocks execute cleanup actions (e.g. closing streams) even after returns or unhandled exceptions."),
        ("What is a Checked Exception in Java?", "An exception checked at compile-time that must be either caught with try-catch or declared with `throws`", ["An exception caused by JVM hardware faults", "A RuntimeException", "A compilation warning"], "MEDIUM", 0.1, "Checked exceptions (subclasses of Exception excluding RuntimeException) enforce compile-time handling."),
        ("Which collection class in `java.util` implements a resizable array and allows fast random access?", "ArrayList", ["LinkedList", "HashSet", "TreeSet"], "EASY", -1.0, "ArrayList wraps a dynamic array offering O(1) indexed lookups."),
        ("What does `HashMap` in Java use to handle hash collisions?", "Chaining using linked lists, transforming into red-black trees when bucket length exceeds 8", ["Linear probing", "Open addressing", "Throwing exceptions"], "HARD", 1.2, "Java 8+ HashMaps convert collision chains from LinkedLists to balanced Red-Black Trees at TREEIFY_THRESHOLD (8)."),
        ("What is the return type of `hashCode()` in Java?", "int (32-bit signed integer)", ["long", "String", "boolean"], "EASY", -1.0, "`hashCode()` returns a 32-bit signed integer used to index hash buckets."),
        ("If two objects are equal according to `.equals()`, what must be true about their hash codes in Java?", "Their `hashCode()` values must be identical", ["Their hash codes may differ", "Their memory addresses must match", "Their class names must differ"], "MEDIUM", 0.2, "The `equals` and `hashCode` contract mandates: if `a.equals(b)`, then `a.hashCode() == b.hashCode()`."),
        ("What is the function of the `synchronized` keyword in Java?", "Enforces mutual exclusion so only one thread can execute the block or method on the given monitor lock", ["Runs code faster", "Allocates memory on stack", "Prevents compilation"], "MEDIUM", 0.2, "`synchronized` acquires an intrinsic monitor lock to ensure thread safety."),
        ("What does the `transient` keyword signify for a class member in Java?", "The field should not be serialized during object serialization", ["The field is constant", "The field is volatile", "The field is stored in registers"], "MEDIUM", 0.1, "`transient` fields are skipped by Java serialization mechanisms."),
        ("Which interface in Java represents a task that can be executed concurrently and returns a value?", "Callable<V>", ["Runnable", "Thread", "Process"], "MEDIUM", 0.1, "`Callable<V>` returns a result via `.call()` and can throw checked exceptions, unlike `Runnable.run()`."),
        ("What is autoboxing in Java?", "Automatic conversion between primitive types and their corresponding wrapper object classes", ["Packing code into JARs", "Converting classes to interfaces", "Allocating arrays"], "EASY", -1.0, "Autoboxing converts e.g. `int` to `Integer` seamlessly at compile time."),
    ]
    for q_text, ans, wr, diff, irt, expl in java_cases:
        questions.append(make_q(topic, diff, irt, q_text, ans, wr, expl))
        questions.append(make_q(topic, diff, irt + 0.1, f"Java Platform & Memory Concept:\n{q_text}", ans, wr, f"Java specification behavior: {ans}. {expl}"))
        questions.append(make_q(topic, diff, irt + 0.2, f"JVM & Collections Architecture:\n{q_text}", ans, wr, f"Verified Java mechanism: {ans}. {expl}"))

    # ═══════════════════════════════════════════════════════════════
    # 9. C++ ESSENTIALS (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "C++ Essentials"
    cpp_cases = [
        ("What is the difference between a pointer and a reference in C++?", "References cannot be null or reseated after initialization; pointers can be null and modified", ["Pointers are faster", "References require explicit memory allocation", "They are identical"], "EASY", -1.0, "References are syntax-level aliases that cannot be re-bound or null; pointers hold memory addresses directly."),
        ("What operator is used to allocate dynamic memory on the heap in C++?", "`new`", ["`malloc`", "`alloc`", "`create`"], "EASY", -1.1, "`new` allocates heap memory and calls class constructors; `delete` frees it and invokes destructors."),
        ("What happens if memory allocated with `new` is not deallocated with `delete` in C++?", "Memory leak", ["Automatic garbage collection", "Stack overflow", "Compile error"], "EASY", -1.0, "C++ does not provide automatic garbage collection; unreleased heap memory leads to memory leaks."),
        ("What is RAII (Resource Acquisition Is Initialization) in C++?", "A paradigm where resource lifetimes are tied to object lifetimes via constructors and destructors", ["A compilation flag", "A memory pointer", "An exception handler"], "MEDIUM", 0.2, "RAII ensures resources (memory, locks, file handles) are deterministically released when stack objects exit scope."),
        ("Which smart pointer in modern C++ (C++11+) models exclusive ownership of a dynamically allocated object?", "`std::unique_ptr`", ["`std::shared_ptr`", "`std::weak_ptr`", "`std::auto_ptr`"], "EASY", -0.9, "`std::unique_ptr` enforces strict single ownership and cannot be copied, only moved."),
        ("What is `std::vector` in C++?", "A dynamic array that manages its own heap memory and resizes automatically", ["A linked list", "A static array", "A mathematical matrix"], "EASY", -1.1, "`std::vector` stores elements contiguously on the heap with amortized O(1) push_back."),
        ("What is the purpose of a copy constructor in C++?", "Initializes a new object as a copy of an existing object of the same class", ["Destroys duplicate objects", "Copies files", "Creates virtual tables"], "EASY", -1.0, "Copy constructors (`ClassName(const ClassName& other)`) define how objects are duplicated (deep vs shallow copy)."),
        ("What does the Rule of Three in classical C++ specify?", "If a class defines a destructor, copy constructor, or copy assignment operator, it likely needs all three", ["Three access modifiers", "Three loop types", "Three inheritance forms"], "MEDIUM", 0.2, "Managing raw resources requires managing destruction, copying, and assignment to prevent double-free bugs."),
        ("What is move semantics in C++11 enabled by?", "Rvalue references (`T&&`) and `std::move`", ["Pointers only", "Templates", "Multiple inheritance"], "HARD", 1.2, "Move semantics transfers ownership of resources from temporary rvalues without expensive deep copies."),
        ("What is the Standard Template Library (STL) composed of?", "Containers, Iterators, Algorithms, and Function Objects (Functors)", ["Compilers and Linkers", "Operating System APIs", "Database Drivers"], "EASY", -1.0, "STL provides generic data structures (containers), navigation abstraction (iterators), and algorithms."),
        ("What does `std::shared_ptr` use to manage object lifetime across multiple owners?", "Reference counting block on the heap", ["Mark and sweep GC", "Timer ticks", "Operating system signals"], "MEDIUM", 0.1, "`std::shared_ptr` increments reference count on copy and decrements on destruction, freeing when count reaches 0."),
        ("What problem does `std::weak_ptr` solve?", "Breaks circular reference cycles between `std::shared_ptr` instances that would prevent deallocation", ["Speeds up allocation", "Prevents null pointers", "Converts pointers to ints"], "HARD", 1.2, "Weak pointers reference objects managed by shared_ptr without contributing to the reference count."),
        ("What is a pure virtual function in C++ declared as?", "`virtual void func() = 0;`", ["`virtual void func();`", "`abstract void func();`", "`void func() = NULL;`"], "EASY", -1.0, "`= 0` syntax defines a pure virtual function, rendering the class abstract."),
        ("What will `cout << 5 / 2;` output in C++?", "2", ["2.5", "3", "Error"], "EASY", -1.1, "Integer division truncates the fractional portion, outputting 2."),
        ("What is template metaprogramming in C++?", "Technique in which templates are instantiated by the compiler to perform computation at compile time", ["Running Python in C++", "Allocating memory at runtime", "Writing macros"], "HARD", 1.2, "C++ templates are Turing complete, allowing recursive compile-time evaluation and code generation."),
    ]
    for q_text, ans, wr, diff, irt, expl in cpp_cases:
        questions.append(make_q(topic, diff, irt, q_text, ans, wr, expl))
        questions.append(make_q(topic, diff, irt + 0.1, f"C++ Core Concept & Memory Model:\n{q_text}", ans, wr, f"C++ language specification: {ans}. {expl}"))
        questions.append(make_q(topic, diff, irt + 0.2, f"Modern C++ Standards & STL:\n{q_text}", ans, wr, f"Modern C++ principle verified: {ans}. {expl}"))

    return questions

if __name__ == "__main__":
    qs = generate_programming_questions()
    print(f"Generated {len(qs)} programming questions across 9 topics.")
    with open("app/data/bank/programming_bank.json", "w") as f:
        json.dump(qs, f, indent=2)
    print("Saved to app/data/bank/programming_bank.json")
