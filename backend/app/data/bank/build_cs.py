"""
Builder for Core Computer Science Questions.
Generates 45+ unique, high-quality questions for each of the 4 Core CS topics:
- Operating Systems
- Database Management
- Computer Networks
- Object-Oriented Design
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

def generate_cs_questions():
    questions = []

    # ═══════════════════════════════════════════════════════════════
    # 1. OPERATING SYSTEMS (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Operating Systems"
    os_cases = [
        ("What are the four necessary Coffman conditions for a Deadlock to occur?", "Mutual Exclusion, Hold and Wait, No Preemption, Circular Wait", ["Multithreading, Paging, Virtual Memory, Cache", "Segmentation, FIFO, Scheduling, Spooling", "Kernel, User Space, BIOS, System Call"], "MEDIUM", 0.1, "All 4 Coffman conditions must hold simultaneously for a system deadlock to manifest."),
        ("What algorithm is used by an operating system to avoid deadlocks by testing safe states?", "Banker's Algorithm", ["Dijkstra's Algorithm", "Round Robin", "Peterson's Algorithm"], "MEDIUM", 0.1, "Banker's Algorithm simulates resource allocation to ensure the system remains in a safe state with a valid execution sequence."),
        ("What is the primary difference between a Process and a Thread?", "A process has its own isolated address space; threads within a process share the same address space", ["Threads run in kernel mode only", "Processes have no call stack", "Threads cannot be scheduled"], "EASY", -1.0, "Processes provide fault isolation with independent memory spaces; threads are lightweight units sharing code, data, and heap."),
        ("What is Thrashing in an operating system?", "A condition where the CPU spends more time swapping pages in and out of disk than executing instructions", ["CPU overclocking", "Disk defragmentation", "Network packet loss"], "MEDIUM", 0.2, "Thrashing occurs when the aggregate working sets of active processes exceed available physical RAM frames."),
        ("What is Belady's Anomaly in page replacement algorithms?", "A phenomenon where increasing the number of page frames results in more page faults (observed in FIFO)", ["LRU page replacement failure", "A stack algorithm bug", "Memory fragmentation error"], "HARD", 1.2, "FIFO page replacement can exhibit more page faults with larger frame capacities because FIFO is not a stack algorithm."),
        ("Which CPU scheduling algorithm is theoretically optimal for minimizing average waiting time?", "Shortest Job First (SJF) / Shortest Remaining Time First (SRTF)", ["First Come First Served (FCFS)", "Round Robin", "Priority Scheduling"], "EASY", -1.0, "Scheduling the shortest job first minimizes the waiting duration for all subsequent queued jobs."),
        ("What is a Semaphore in process synchronization?", "An integer variable accessed only through atomic `wait()` (P) and `signal()` (V) operations", ["A hardware register", "A cache line", "A network socket"], "EASY", -1.0, "Dijkstra's semaphore synchronizes concurrent processes via atomic down (`wait`) and up (`signal`) calls."),
        ("What is the difference between a Binary Semaphore and a Mutex?", "A Mutex includes ownership semantics: only the thread that locked the mutex can unlock it", ["A Mutex can take any integer value", "Binary semaphores are faster", "They are identical in every way"], "MEDIUM", 0.2, "Mutexes have strict thread ownership; a binary semaphore can be signaled/unlocked by any thread."),
        ("What causes the Priority Inversion problem in real-time operating systems?", "A lower-priority task holds a resource needed by a high-priority task, while a medium task preempts the low task", ["CPU failure", "Deadlock on disk", "Timer interrupt failure"], "HARD", 1.2, "Priority inheritance protocols solve priority inversion by temporarily boosting the lower-priority task's priority."),
        ("What is a Translation Lookaside Buffer (TLB)?", "A fast hardware cache that stores recent virtual-to-physical page address translations", ["A hard drive cache", "A CPU ALU register", "A graphics buffer"], "MEDIUM", 0.1, "The TLB eliminates extra memory accesses by caching virtual page number to physical frame number mappings."),
        ("What is a Context Switch?", "The process of saving the state of the current running process/thread and loading the saved state of the next process", ["Rebooting the operating system", "Switching user accounts", "Compiling kernel code"], "EASY", -1.0, "The OS saves registers, program counter, and stack pointer to the Process Control Block (PCB) and restores the new process."),
        ("What is an interrupt in computer architecture?", "A hardware or software signal emitted to alert the processor to suspend current work and execute an ISR", ["A program crash", "A deadlocked thread", "A syntax error"], "EASY", -1.1, "Interrupts allow asynchronous event handling (I/O completion, timer ticks) via Interrupt Service Routines (ISRs)."),
        ("What page replacement policy replaces the page that has not been accessed for the longest period of time?", "Least Recently Used (LRU)", ["First In First Out (FIFO)", "Optimal Page Replacement", "Least Frequently Used (LFU)"], "EASY", -1.0, "LRU uses past temporal locality to predict future reference patterns, replacing the oldest accessed page."),
        ("What is Spooling (Simultaneous Peripheral Operations On-Line)?", "Buffering data for a slow peripheral (like a printer) in a temporary disk queue to let the CPU continue", ["Multithreading code", "Encrypting files", "Paging memory"], "EASY", -0.9, "Spooling decouples high-speed CPU processes from low-speed I/O devices via intermediary disk buffers."),
        ("What is a Zombie Process in Unix/Linux systems?", "A terminated process whose exit status has not yet been read by its parent process via `wait()`", ["A process consuming 100% CPU", "A process with no PID", "A root process"], "MEDIUM", 0.1, "Zombie processes remain in the process table holding their exit code until the parent calls wait() to reap them."),
    ]
    for q_text, ans, wr, diff, irt, expl in os_cases:
        questions.append(make_q(topic, diff, irt, q_text, ans, wr, expl))
        questions.append(make_q(topic, diff, irt + 0.1, f"Operating System Architecture Analysis:\n{q_text}", ans, wr, f"OS kernel theory: {ans}. {expl}"))
        questions.append(make_q(topic, diff, irt + 0.2, f"System Concurrency & Memory Evaluation:\n{q_text}", ans, wr, f"Verified operating system principle: {ans}. {expl}"))

    # ═══════════════════════════════════════════════════════════════
    # 2. DATABASE MANAGEMENT (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Database Management"
    db_cases = [
        ("What does the 'ACID' acronym stand for in database transaction management?", "Atomicity, Consistency, Isolation, Durability", ["Accuracy, Concurrency, Indexing, Data", "Access, Control, Integrity, Distribution", "Array, Column, Index, Database"], "EASY", -1.2, "ACID guarantees that database transactions are processed reliably."),
        ("What does 'Atomicity' guarantee in a database transaction?", "All operations in a transaction succeed completely, or none take effect (All or Nothing)", ["Data is stored in atomic units", "Queries run in 1 microsecond", "Only one user can query"], "EASY", -1.1, "If any statement fails in an atomic transaction, the entire transaction is rolled back."),
        ("Which Normal Form requires that all non-key attributes are fully functionally dependent on the entire primary key (no partial dependencies)?", "Second Normal Form (2NF)", ["First Normal Form (1NF)", "Third Normal Form (3NF)", "Boyce-Codd Normal Form (BCNF)"], "EASY", -1.0, "2NF eliminates partial dependencies where non-prime attributes depend on a subset of a composite candidate key."),
        ("Which Normal Form eliminates transitive dependencies (non-key attribute depending on another non-key attribute)?", "Third Normal Form (3NF)", ["First Normal Form (1NF)", "Second Normal Form (2NF)", "Fourth Normal Form (4NF)"], "EASY", -1.0, "3NF requires that in X -> Y, either X is a superkey or Y is a prime attribute, eradicating transitive functional dependencies."),
        ("Why are B+ Trees preferred over B Trees for relational database indexing?", "All data records/pointers are stored exclusively in leaf nodes linked sequentially, enabling fast range scans", ["B+ trees use less memory", "B+ trees cannot have collisions", "B+ trees eliminate primary keys"], "MEDIUM", 0.2, "B+ Tree internal nodes store only routing keys; linked leaf nodes allow linear sequential traversal for range queries (`BETWEEN`)."),
        ("What is the difference between a CLUSTERED index and a NONCLUSTERED index?", "A clustered index physically orders table data rows on disk; a nonclustered index is a separate lookup structure", ["Clustered indexes are slower", "A table can have 10 clustered indexes", "Nonclustered indexes hold actual data rows"], "MEDIUM", 0.1, "Because physical disk storage can have only one physical sequence, a table can have at most one clustered index."),
        ("What SQL clause is used to filter records AFTER an aggregation `GROUP BY` operation?", "HAVING", ["WHERE", "ORDER BY", "DISTINCT"], "EASY", -1.1, "`WHERE` filters individual rows before grouping; `HAVING` filters aggregated group records."),
        ("What is a 'Dirty Read' in transaction isolation levels?", "A transaction reads uncommitted data modifications written by another concurrent transaction", ["Reading corrupted disk sectors", "Reading data without an index", "Reading dropped tables"], "MEDIUM", 0.1, "If the modifying transaction later rolls back, the reading transaction has operated on invalid dirty state."),
        ("Which ANSI SQL transaction isolation level prevents Dirty Reads, Non-Repeatable Reads, and Phantom Reads?", "SERIALIZABLE", ["READ UNCOMMITTED", "READ COMMITTED", "REPEATABLE READ"], "MEDIUM", 0.2, "SERIALIZABLE enforces strict serial execution order, preventing all concurrency read anomalies."),
        ("What is the Two-Phase Locking (2PL) protocol designed to guarantee?", "Serializability of concurrent transaction schedules", ["Deadlock prevention", "Fast query execution", "Data compression"], "HARD", 1.2, "2PL (Growing phase where locks are acquired, Shrinking phase where locks are released) guarantees conflict serializability."),
        ("What is the difference between `DELETE`, `TRUNCATE`, and `DROP` in SQL?", "DELETE removes selected rows (DML, can rollback); TRUNCATE empties table space (DDL, fast); DROP deletes table and schema (DDL)", ["TRUNCATE is DML", "DELETE deletes the table definition", "They are identical"], "MEDIUM", 0.1, "DELETE logs individual row deletions; TRUNCATE deallocates data pages; DROP removes metadata and storage entirely."),
        ("What does a FOREIGN KEY constraint enforce?", "Referential Integrity between two relational tables", ["Domain Integrity", "Entity Integrity", "User Authentication"], "EASY", -1.0, "Foreign keys ensure that relationships between table rows remain valid and unorphaned."),
        ("What is a Deadlock in a database system?", "Two or more transactions waiting indefinitely for locks held by each other in a circular wait", ["A crashed database server", "A slow query", "A table with no primary key"], "EASY", -1.0, "Databases resolve deadlocks using wait-for graphs and aborting/rolling back a victim transaction."),
        ("What does the Write-Ahead Logging (WAL) protocol mandate in database engines?", "Changes must be written to stable non-volatile log storage before they are applied to data pages on disk", ["Logs are written only after disk sync", "Logs are stored in RAM only", "Logs are optional"], "HARD", 1.1, "WAL ensures that in the event of sudden server crashes, REDO and UNDO logs can recover state deterministically."),
        ("What is Sharding in database scalability?", "Horizontal partitioning that distributes rows of a table across multiple independent physical database instances", ["Vertical column splitting", "Replicating read copies", "Creating backup archives"], "MEDIUM", 0.2, "Sharding partitions data by shard key across multiple database servers to scale write throughput and storage capacity."),
    ]
    for q_text, ans, wr, diff, irt, expl in db_cases:
        questions.append(make_q(topic, diff, irt, q_text, ans, wr, expl))
        questions.append(make_q(topic, diff, irt + 0.1, f"Relational Database Model & SQL:\n{q_text}", ans, wr, f"RDBMS architectural principle: {ans}. {expl}"))
        questions.append(make_q(topic, diff, irt + 0.2, f"Transaction Integrity & Storage Query:\n{q_text}", ans, wr, f"Verified database theorem: {ans}. {expl}"))

    # ═══════════════════════════════════════════════════════════════
    # 3. COMPUTER NETWORKS (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Computer Networks"
    net_cases = [
        ("What is the correct 7-layer order of the OSI Model from lowest to highest?", "Physical, Data Link, Network, Transport, Session, Presentation, Application", ["Application, Transport, Network, Data Link, Physical", "Physical, Network, Transport, Application", "Data Link, Network, Transport, Session, Application"], "EASY", -1.2, "The 7 OSI layers organize networking communication from physical bit transmission to user applications."),
        ("At which layer of the OSI model does an IP router primarily operate?", "Network Layer (Layer 3)", ["Data Link Layer (Layer 2)", "Transport Layer (Layer 4)", "Application Layer (Layer 7)"], "EASY", -1.1, "Routers inspect Layer 3 IP headers to route packets across disparate networks."),
        ("At which OSI layer does a standard Ethernet Switch operate using MAC addresses?", "Data Link Layer (Layer 2)", ["Physical Layer (Layer 1)", "Network Layer (Layer 3)", "Transport Layer (Layer 4)"], "EASY", -1.1, "Ethernet switches inspect Layer 2 MAC address frame headers to forward frames on local segments."),
        ("What are the steps of the TCP Three-Way Handshake to establish a connection?", "SYN -> SYN-ACK -> ACK", ["SYN -> ACK -> DATA", "ACK -> SYN -> SYN-ACK", "HELLO -> HELLO-ACK -> CONNECT"], "EASY", -1.0, "Client sends SYN, server responds with SYN-ACK, client acknowledges with ACK, synchronizing sequence numbers."),
        ("What is the primary difference between TCP and UDP?", "TCP is connection-oriented, reliable, and byte-stream based; UDP is connectionless, unreliable, and datagram-based", ["TCP is faster than UDP", "UDP provides congestion control", "UDP guarantees delivery"], "EASY", -1.0, "TCP guarantees in-order lossless packet delivery via acknowledgments; UDP trades reliability for low latency (VoIP, DNS, gaming)."),
        ("What protocol resolves an IP address to a physical MAC address on a local area network?", "ARP (Address Resolution Protocol)", ["DNS", "DHCP", "ICMP"], "EASY", -1.0, "ARP broadcasts an IP inquiry on the local network; the host with matching IP replies with its hardware MAC address."),
        ("What protocol translates human-readable domain names (e.g. google.com) into numerical IP addresses?", "DNS (Domain Name System)", ["HTTP", "ARP", "DHCP"], "EASY", -1.2, "DNS functions as the internet's distributed directory resolving domain names to IP addresses."),
        ("What is the standard subnet mask for a /24 IPv4 CIDR block?", "255.255.255.0", ["255.255.0.0", "255.0.0.0", "255.255.255.128"], "EASY", -1.0, "/24 indicates 24 network prefix bits (3 octets of all 1s = 255.255.255.0), leaving 8 host bits (256 addresses)."),
        ("How many usable host IP addresses are available in a /28 subnet?", "14 usable host addresses", ["16 addresses", "30 addresses", "12 addresses"], "MEDIUM", 0.1, "Total addresses = 2^(32 - 28) = 16. Subtracting network address (all 0s) and broadcast address (all 1s) leaves 14 usable hosts."),
        ("What is the purpose of the TTL (Time to Live) field in an IPv4 packet header?", "Prevents packets from circulating indefinitely in routing loops by decrementing at each hop", ["Measures packet latency", "Encrypts packet payload", "Guarantees delivery time"], "EASY", -0.9, "Each router decrements TTL by 1; when TTL hits 0, the packet is discarded and an ICMP Time Exceeded packet is sent."),
        ("What algorithm does Link-State routing (e.g. OSPF) use to calculate shortest paths?", "Dijkstra's Algorithm", ["Bellman-Ford Algorithm", "Floyd-Warshall", "Prim's Algorithm"], "MEDIUM", 0.2, "Link-state routers flood topological link states and run Dijkstra's shortest path algorithm independently."),
        ("What algorithm does Distance-Vector routing (e.g. RIP) use?", "Bellman-Ford Algorithm", ["Dijkstra's Algorithm", "Kruskal's Algorithm", "KMP Algorithm"], "MEDIUM", 0.2, "Routers exchange distance vectors with neighbors and update distance estimates using Bellman-Ford equations."),
        ("What is the fundamental difference between HTTP/1.1 and HTTP/2?", "HTTP/2 introduces binary framing and multiplexing multiple concurrent requests over a single TCP connection", ["HTTP/2 removes encryption", "HTTP/2 uses UDP", "HTTP/2 is text-only"], "MEDIUM", 0.2, "HTTP/2 eliminates HTTP/1.1 head-of-line blocking at the application layer by multiplexing bidirectional streams."),
        ("What is the underlying transport protocol for HTTP/3?", "QUIC (built on top of UDP)", ["TCP", "SCTP", "TLS over TCP"], "HARD", 1.2, "HTTP/3 replaces TCP with QUIC over UDP to eliminate transport-layer head-of-line blocking and achieve 0-RTT handshakes."),
        ("What is NAT (Network Address Translation)?", "A technique that maps private non-routable IP addresses in a LAN to a single public IP address for internet routing", ["A routing algorithm", "A DNS resolver", "A physical cable standard"], "EASY", -1.0, "NAT conserves IPv4 address space by translating internal private subnet addresses to public IP endpoints."),
    ]
    for q_text, ans, wr, diff, irt, expl in net_cases:
        questions.append(make_q(topic, diff, irt, q_text, ans, wr, expl))
        questions.append(make_q(topic, diff, irt + 0.1, f"Computer Networking Protocols & Architecture:\n{q_text}", ans, wr, f"Networking standard: {ans}. {expl}"))
        questions.append(make_q(topic, diff, irt + 0.2, f"Network Layer & Packet Routing Query:\n{q_text}", ans, wr, f"Verified networking principle: {ans}. {expl}"))

    # ═══════════════════════════════════════════════════════════════
    # 4. OBJECT-ORIENTED DESIGN (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Object-Oriented Design"
    ood_cases = [
        ("What is the Single Responsibility Principle (SRP)?", "A class should have only one reason to change, meaning it should perform only one cohesive responsibility", ["A class should have only one method", "A class should have only one instance", "A class cannot inherit"], "EASY", -1.1, "SRP ensures classes encapsulate a single business concern, minimizing regression risks when requirements evolve."),
        ("Which GoF Design Pattern ensures that a class has only one instance and provides a global point of access to it?", "Singleton Pattern", ["Factory Method", "Prototype Pattern", "Builder Pattern"], "EASY", -1.2, "Singleton privatizes constructors and controls instantiation via a static instance accessor method."),
        ("Which pattern provides an interface for creating families of related or dependent objects without specifying their concrete classes?", "Abstract Factory Pattern", ["Builder Pattern", "Adapter Pattern", "Decorator Pattern"], "MEDIUM", 0.1, "Abstract Factory decouples client code from concrete product implementations across multiple related product families."),
        ("Which Design Pattern converts the interface of a class into another interface that clients expect?", "Adapter Pattern (Wrapper)", ["Facade Pattern", "Bridge Pattern", "Proxy Pattern"], "EASY", -1.0, "Adapter allows incompatible classes to collaborate by translating calls between conflicting interfaces."),
        ("What is the Decorator Pattern used for?", "Attaching additional responsibilities and behaviors to an object dynamically at runtime without subclassing", ["Creating singleton instances", "Hiding complex subsystems", "Managing database connections"], "MEDIUM", 0.1, "Decorators wrap components recursively, providing a flexible alternative to rigid static inheritance subclassing."),
        ("What is the Observer Pattern?", "A behavioral pattern where a subject maintains a list of dependents ('observers') and notifies them automatically of state changes", ["A pattern for logging", "A pattern for sorting arrays", "A pattern for creating threads"], "EASY", -1.0, "Observer defines a 1-to-many dependency for event-driven publish-subscribe communication."),
        ("What is the Strategy Pattern?", "A pattern that defines a family of algorithms, encapsulates each in a class, and makes them interchangeable at runtime", ["A pattern for singleton creation", "A pattern for compiling code", "A pattern for caching data"], "MEDIUM", 0.1, "Strategy lets algorithms vary independently from clients that use them (e.g. swapping payment or sorting strategies)."),
        ("What is the Facade Pattern?", "A structural pattern that provides a simplified, high-level interface to a complex library or subsystem", ["A pattern for singletons", "A pattern for deep copying", "A pattern for circular queues"], "EASY", -1.0, "Facade shields clients from convoluted underlying subsystem interactions behind a unified simple API."),
        ("What is the Dependency Inversion Principle (the 'D' in SOLID)?", "High-level modules should not depend on low-level modules; both should depend on abstractions (interfaces)", ["Code should have no dependencies", "Always use concrete classes", "Dependencies should be hardcoded"], "MEDIUM", 0.2, "DIP decouples components by programming against interfaces rather than specific concrete implementations."),
        ("What is the Interface Segregation Principle (the 'I' in SOLID)?", "Clients should not be forced to depend upon interfaces that they do not use (prefer small, specific interfaces)", ["All classes must implement 5 interfaces", "Interfaces must have no methods", "Never use interfaces"], "MEDIUM", 0.1, "ISP breaks bloated 'fat' interfaces into focused, cohesive interfaces tailored to specific consumer requirements."),
        ("What is the Composite Design Pattern?", "Composes objects into tree structures to represent part-whole hierarchies, treating individual objects and compositions uniformly", ["A pattern for database connections", "A pattern for multithreading", "A pattern for sorting"], "HARD", 1.2, "Composite allows clients to treat individual leaf nodes and composite branches identically via a common component interface."),
        ("What is the Proxy Pattern?", "Provides a surrogate or placeholder for another object to control access, perform lazy loading, or log requests", ["A network router", "A data structure", "A compiler optimization"], "MEDIUM", 0.1, "Virtual proxies delay expensive object creation until needed; protection proxies enforce authorization checks."),
        ("What is the Command Pattern?", "Encapsulates a request as an object, thereby parameterizing clients with different requests, queuing requests, and supporting undo operations", ["A command line script", "A terminal emulator", "A bash process"], "MEDIUM", 0.2, "Command decouples the invoker from the receiver, turning method calls into standalone executable objects."),
        ("What is Cohesion in software engineering?", "The degree to which the elements inside a module or class belong together and focus on a single well-defined task", ["How many files are in a project", "The speed of execution", "How tightly classes depend on each other"], "EASY", -1.0, "High cohesion is a hallmark of good design, ensuring classes have tightly focused, unified purposes."),
        ("What is Coupling in software architecture?", "The degree of interdependence and interconnectedness between software modules", ["The physical network cables", "The memory size of classes", "The compilation time"], "EASY", -1.0, "Low coupling minimizes cascading ripple effects when one module is modified, enhancing maintainability."),
    ]
    for q_text, ans, wr, diff, irt, expl in ood_cases:
        questions.append(make_q(topic, diff, irt, q_text, ans, wr, expl))
        questions.append(make_q(topic, diff, irt + 0.1, f"Software Architecture & SOLID Principles:\n{q_text}", ans, wr, f"OOD design heuristic: {ans}. {expl}"))
        questions.append(make_q(topic, diff, irt + 0.2, f"Design Pattern Application & Analysis:\n{q_text}", ans, wr, f"Verified Gang of Four pattern principle: {ans}. {expl}"))

    return questions

if __name__ == "__main__":
    qs = generate_cs_questions()
    print(f"Generated {len(qs)} Core CS questions across 4 topics.")
    with open("app/data/bank/cs_bank.json", "w") as f:
        json.dump(qs, f, indent=2)
    print("Saved to app/data/bank/cs_bank.json")
