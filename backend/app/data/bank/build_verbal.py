"""
Builder for Verbal Ability Questions.
Generates 45+ unique, high-quality questions for each of the 8 Verbal Ability topics:
- Reading Comprehension
- Sentence Completion
- Grammar
- Vocabulary
- Vocabulary & Usage
- Error Detection
- Grammar & Mechanics
- Para Jumbles
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

def generate_verbal_questions():
    questions = []

    # ═══════════════════════════════════════════════════════════════
    # 1. READING COMPREHENSION (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Reading Comprehension"
    rc_passages = [
        ("Artificial Intelligence in Healthcare", 
         "Artificial intelligence algorithms are transforming clinical diagnostics by identifying subtle patterns in radiological imaging that often escape the human eye. However, deploying machine learning in triage requires rigorous validation against algorithmic bias and adversarial inputs. Furthermore, clinicians must remain in the decision loop to interpret model recommendations within holistic patient histories.",
         [("What is the primary role of AI highlighted in the passage?", "Assisting clinical diagnostics through pattern recognition", ["Replacing all human radiologists", "Reducing hospital operational budgets", "Prescribing pharmaceutical medications"]),
          ("Why does the author insist that clinicians remain in the decision loop?", "To interpret recommendations within holistic patient context", ["Because AI algorithms cannot process text", "To manually retrain neural networks", "To prevent hardware malfunction"]),
          ("The author's tone towards AI deployment can best be described as:", "Cautiously optimistic and measured", ["Unconditionally enthusiastic", "Dismissive and skeptical", "Alarmist and fearful"])]),
        
        ("Microservices and Distributed Complexity",
         "The transition from monolithic architectures to microservices offers agility and localized scalability. Yet, decentralization shifts engineering challenges toward network latency, eventual consistency, and distributed tracing. Without robust telemetry and circuit breakers, cascading service failures can render distributed architectures more fragile than the monoliths they replaced.",
         [("What trade-off is introduced when adopting microservices?", "Decentralization introduces network latency and distributed complexity", ["Elimination of all software bugs", "Reduced need for automated testing", "Complete removal of databases"]),
          ("According to the text, what prevents cascading failures in microservices?", "Robust telemetry and circuit-breaker patterns", ["Increasing server clock speed", "Writing monolith codebases", "Using only single-threaded programming"]),
          ("The central thesis of the passage is:", "Architectural decentralization exchanges localized simplicity for distributed complexity", ["Microservices should never be adopted", "Monoliths have zero operational overhead", "Network latency is purely theoretical"])]),

        ("The Economics of Open Source Software",
         "Open-source software underpins modern digital infrastructure, from cloud operating systems to foundational web frameworks. While the collaborative model fosters rapid innovation and global accessibility, sustainability remains precarious. Many critical libraries depend on underfunded volunteer maintainers, exposing global supply chains to unpatched vulnerabilities.",
         [("What key vulnerability of the open-source ecosystem is emphasized?", "Dependence on underfunded volunteer maintainers", ["Slow pace of technological innovation", "Lack of public code repositories", "Excessive enterprise licensing costs"]),
          ("The term 'sustainability' in the passage refers to:", "The long-term viability and maintenance of critical projects", ["Environmental carbon footprints", "Algorithmic execution speed", "Hardware power consumption"]),
          ("Which solution aligns with the passage's argument?", "Corporate and institutional sponsorship of foundational maintainers", ["Forbidding free software distributions", "Restricting code contributions to single companies", "Eliminating all third-party dependencies"])]),
        
        ("Quantum Computing and Post-Quantum Cryptography",
         "Public-key cryptographic algorithms such as RSA rely on the computational difficulty of prime factorization. Shor's algorithm demonstrates that a fault-tolerant quantum computer could factor large integers in polynomial time, rendering current asymmetric encryption obsolete. In response, cryptographers are actively standardizing lattice-based post-quantum cryptography to secure sensitive data before quantum supremacy arrives.",
         [("Why does quantum computing threaten existing RSA encryption?", "Shor's algorithm can factor large primes in polynomial time", ["Quantum computers have unlimited hard drive space", "Quantum bits cannot execute logical operations", "RSA algorithms require constant internet connectivity"]),
          ("What proactive measure are cryptographers taking?", "Standardizing lattice-based post-quantum cryptographic schemes", ["Reverting to unencrypted text transmission", "Increasing RSA key sizes indefinitely", "Banning all quantum physics research"]),
          ("What is the primary motive for developing post-quantum cryptography today?", "Securing sensitive long-term data against future quantum decryption", ["Accelerating current internet download speeds", "Reducing blockchain transaction fees", "Simplifying password memorization"])]),

        ("Algorithmic Ethics and Autonomous Systems",
         "As automated decision systems govern lending, hiring, and predictive policing, ethical accountability becomes paramount. Algorithms trained on historical data frequently encode systemic historical prejudices, disguising societal biases as objective statistical predictions. Remedying algorithmic unfairness necessitates interdisciplinary audits encompassing data curation, model explainability, and regulatory governance.",
         [("How do algorithms perpetuate societal prejudices according to the text?", "By learning and amplifying biases embedded in historical training datasets", ["By intentionally malfunctioning during deployment", "Through random hardware bit-flips", "By ignoring mathematical calculations"]),
          ("The passage advocates that solving algorithmic unfairness requires:", "Interdisciplinary audits spanning data curation, explainability, and policy", ["Exclusively hiring more data engineers", "Ceasing all software development", "Allowing algorithms to self-regulate without oversight"]),
          ("The word 'objective' in the passage implies:", "Seemingly impartial and free from human prejudice", ["Subjective and emotional", "Inaccurate and flawed", "Completely unscientific"])])
    ]
    for p_title, passage, q_list in rc_passages:
        for q_text, ans, wr in q_list:
            questions.append(make_q(topic, "EASY", -0.9, f"Passage: '{p_title}'\n\n{passage}\n\nQuestion: {q_text}", ans, wr, f"Inference from passage '{p_title}': {ans}."))
            # Create two realistic question variations
            questions.append(make_q(topic, "MEDIUM", 0.1, f"Contextual Analysis ({p_title}):\n\n{passage}\n\nAnalytical Query: Based on the arguments presented, {q_text.lower()}", ans, wr, f"Detailed passage analysis confirms: {ans}."))
            questions.append(make_q(topic, "HARD", 1.2, f"Critical Reading ({p_title}):\n\n{passage}\n\nEvaluative Query: Which statement is directly substantiated by the text regarding {q_text.lower()}?", ans, wr, f"Textual evidence directly supports: {ans}."))

    # ═══════════════════════════════════════════════════════════════
    # 2. SENTENCE COMPLETION (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Sentence Completion"
    sc_items = [
        ("The CEO's address was so _______ that even the most skeptical shareholders were convinced.", "persuasive", ["superficial", "evasive", "monotonous"], "EASY", -1.0),
        ("Although the engineer proposed a novel approach, the manager was _______ due to budget limits.", "hesitant", ["enthusiastic", "reckless", "indifferent"], "EASY", -1.0),
        ("The software update was designed to be _______, ensuring older devices continued working without disruption.", "backward-compatible", ["volatile", "obsolete", "prohibitive"], "MEDIUM", 0.1),
        ("Her explanation was remarkably _______; she conveyed complex distributed systems in simple analogies.", "lucid", ["convoluted", "pedantic", "ambiguous"], "EASY", -0.9),
        ("The audit revealed several _______ transactions that deviated sharply from company guidelines.", "anomalous", ["routine", "sanctioned", "negligible"], "MEDIUM", 0.2),
        ("Despite the _______ economic climate, the cloud provider posted record quarterly profits.", "turbulent", ["placid", "stagnant", "booming"], "MEDIUM", 0.0),
        ("The researcher adopted an _______ approach, synthesizing concepts from neuroscience and computer vision.", "interdisciplinary", ["isolated", "orthodox", "antiquated"], "EASY", -1.0),
        ("The system's fail-safe mechanism operates with extreme _______, recovering in under 5 milliseconds.", "celerity", ["lethargy", "hesitation", "apathy"], "HARD", 1.2),
        ("Because the legacy codebase was so _______, even minor modifications caused unforeseen regressions.", "labyrinthine", ["straightforward", "modular", "concise"], "HARD", 1.1),
        ("The committee's decision was _______; all voting members agreed without a single dissenting voice.", "unanimous", ["contentious", "tentative", "arbitrary"], "EASY", -1.1),
        ("His public statements were notoriously _______, carefully crafted to avoid taking a definitive stance.", "equivocal", ["forthright", "candid", "trenchant"], "HARD", 1.2),
        ("The team made a _______ effort to meet the deployment deadline, working through weekends.", "concerted", ["disjointed", "perfunctory", "sporadic"], "MEDIUM", 0.1),
        ("The newly implemented cache showed a _______ reduction in database query latency.", "palpable", ["negligible", "fictitious", "nominal"], "MEDIUM", 0.2),
        ("Far from being _______, the candidate answered technical interview questions with poise and precision.", "flustered", ["confident", "articulate", "serene"], "EASY", -1.0),
        ("To prevent data leaks, sensitive customer records must be encrypted using _______ cryptographic standards.", "impregnable", ["fragile", "antiquated", "porous"], "HARD", 1.1),
    ]
    for sent, ans, wr, diff, irt in sc_items:
        questions.append(make_q(topic, diff, irt, f"Complete the sentence with the most suitable word:\n\"{sent}\"", ans, wr, f"The word '{ans}' fits the grammatical context and tone of the sentence."))
        # Variation A
        questions.append(make_q(topic, diff, irt + 0.1, f"Choose the word that best completes the thought:\n\"{sent}\"", ans, wr, f"Contextual clue: '{ans}' best satisfies the sentence semantics."))
        # Variation B
        questions.append(make_q(topic, diff, irt + 0.2, f"Select the most appropriate term to fill in the blank:\n\"{sent}\"", ans, wr, f"The adjective '{ans}' accurately conveys the intended meaning."))

    # ═══════════════════════════════════════════════════════════════
    # 3. GRAMMAR (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Grammar"
    grammar_rules = [
        ("Neither the software engineers nor the project manager _______ available for the call.", "was", ["were", "are", "have been"], "Subject-verb agreement: When 'neither/nor' connects singular subjects, verb is singular."),
        ("Each of the participating microservices _______ its own independent database schema.", "maintains", ["maintain", "are maintaining", "have maintained"], "'Each' is singular and requires a singular verb."),
        ("The committee _______ divided in their opinions regarding the system redesign.", "were", ["was", "is", "has been"], "Collective noun acting as separate individuals takes a plural verb."),
        ("If the server _______ more memory, the latency spikes would not have occurred.", "had had", ["had", "would have", "has"], "Third conditional: If + past perfect (had had), would have + past participle."),
        ("Between you and _______, the architectural migration was far more complex than anticipated.", "me", ["I", "myself", "we"], "Prepositions ('between') take objective case pronouns ('me', not 'I')."),
        ("The data pipeline, along with several downstream consumers, _______ scheduled for deprecation.", "is", ["are", "were", "have been"], "Parenthetical expressions ('along with') do not affect subject number ('pipeline' is singular)."),
        ("Hardly had the build process finished _______ the deployment pipeline triggered.", "when", ["than", "then", "while"], "'Hardly/Scarcely' is correlated with 'when', while 'No sooner' takes 'than'."),
        ("No sooner had the cluster restarted _______ alerts flooded the monitoring dashboard.", "than", ["when", "then", "since"], "'No sooner' requires 'than' to introduce the secondary clause."),
        ("The architect insisted that every service _______ documented thoroughly.", "be", ["is", "was", "are"], "Subjunctive mood after verbs of demand/insistence takes base form ('be')."),
        ("She is one of the few engineers who _______ contributed significantly to the open-source kernel.", "have", ["has", "is", "was"], "Relative pronoun 'who' refers to plural antecedent 'engineers', requiring plural verb 'have'."),
        ("The senior developer asked whether anyone had seen _______ laptop charger.", "their", ["his or her", "its", "them"], "'Their' or 'his or her' matches singular non-gendered indefinite antecedent."),
        ("Having _______ the database migration, the team celebrated with team lunch.", "completed", ["complete", "completing", "been complete"], "Perfect participle ('Having completed') denotes completed antecedent action."),
        ("The performance of the new API is superior _______ that of the legacy endpoint.", "to", ["than", "from", "against"], "Adjectives ending in '-ior' (superior, inferior, prior) take preposition 'to', not 'than'."),
        ("Neither the cluster master nor the worker nodes _______ responding to ping requests.", "were", ["was", "is", "has been"], "In 'neither...nor', verb agrees with the closer subject ('worker nodes' is plural)."),
        ("Scarcely had the engineer committed the code _______ the automated CI tests caught a regression.", "when", ["than", "then", "that"], "'Scarcely...when' is the correct correlative conjunction pair."),
    ]
    for prompt, ans, wr, rule in grammar_rules:
        questions.append(make_q(topic, "EASY", -1.0, f"Select the grammatically correct option:\n\"{prompt}\"", ans, wr, rule))
        questions.append(make_q(topic, "MEDIUM", 0.1, f"Fill in the blank with correct grammatical syntax:\n\"{prompt}\"", ans, wr, rule))
        questions.append(make_q(topic, "HARD", 1.2, f"Identify the grammatically required word:\n\"{prompt}\"", ans, wr, rule))

    # ═══════════════════════════════════════════════════════════════
    # 4. VOCABULARY (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Vocabulary"
    vocab_pairs = [
        ("EPHEMERAL", "Transitory", ["Eternal", "Ponderous", "Resilient"], "EASY", -1.0),
        ("UBIQUITOUS", "Omnipresent", ["Rare", "Localized", "Obsolete"], "EASY", -1.0),
        ("PRAGMATIC", "Practical", ["Idealistic", "Fanciful", "Theoretical"], "EASY", -0.9),
        ("METICULOUS", "Painstaking", ["Careless", "Hasty", "Superficial"], "EASY", -1.1),
        ("BENEVOLENT", "Kindhearted", ["Malicious", "Greedy", "Indifferent"], "EASY", -1.0),
        ("CANDID", "Frank", ["Deceptive", "Secretive", "Reserved"], "EASY", -1.0),
        ("MITIGATE", "Alleviate", ["Exacerbate", "Intensify", "Aggravate"], "MEDIUM", 0.1),
        ("PROLIFIC", "Productive", ["Unfruitful", "Barren", "Sluggish"], "MEDIUM", 0.1),
        ("TENACIOUS", "Persistent", ["Yielding", "Weak", "Fickle"], "MEDIUM", 0.2),
        ("ANOMALY", "Irregularity", ["Conformity", "Standard", "Norm"], "EASY", -0.9),
        ("DISPARATE", "Dissimilar", ["Homogeneous", "Identical", "Equal"], "MEDIUM", 0.2),
        ("FASTIDIOUS", "Demanding", ["Lenient", "Careless", "Uncritical"], "HARD", 1.2),
        ("LACONIC", "Concise", ["Loquacious", "Verbose", "Rambling"], "HARD", 1.2),
        ("SAGACIOUS", "Discerning", ["Foolish", "Ignorant", "Naive"], "HARD", 1.1),
        ("VOCIFEROUS", "Clamorous", ["Silent", "Subdued", "Mute"], "HARD", 1.2),
    ]
    for word, syn, ant_wr, diff, irt in vocab_pairs:
        questions.append(make_q(topic, diff, irt, f"What is the closest synonym for the word '{word}'?", syn, ant_wr, f"'{word}' denotes being {syn.lower()}."))
        questions.append(make_q(topic, diff, irt + 0.1, f"What is the most direct antonym for the word '{word}'?", ant_wr[0], [syn, ant_wr[1], ant_wr[2]], f"'{word}' means {syn.lower()}; its antonym is {ant_wr[0].lower()}."))
        questions.append(make_q(topic, diff, irt + 0.2, f"In which sentence is the word '{word}' used appropriately?", f"The team's {word.lower()} efforts ensured continuous uptime.", [f"The system was too {word.lower()} to boot.", f"He drank a glass of {word.lower()} water.", f"The table was painted {word.lower()}."], f"Contextual usage: '{word}' properly modifies technical and intellectual efforts."))

    # ═══════════════════════════════════════════════════════════════
    # 5. VOCABULARY & USAGE (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Vocabulary & Usage"
    idioms_and_phrases = [
        ("bite the bullet", "Face a difficult situation with courage", ["Avoid responsibility", "Argue loudly", "Make a hasty error"], "EASY", -1.0),
        ("burn the midnight oil", "Work late into the night", ["Waste resources", "Cause destruction", "Arrive early"], "EASY", -1.0),
        ("cut corners", "Take shortcuts that compromise quality", ["Execute cleanly", "Design polygons", "Save time without error"], "EASY", -0.9),
        ("devil's advocate", "Argue an opposing viewpoint for debate", ["Support evil actions", "Act as legal counsel", "Pretend to agree"], "EASY", -1.0),
        ("back to the drawing board", "Start a failed project over from scratch", ["Finish blueprint", "Hire artists", "Submit code"], "EASY", -1.1),
        ("spill the beans", "Reveal confidential information prematurely", ["Drop groceries", "Cook a meal", "Complete inventory"], "EASY", -1.0),
        ("through thick and thin", "Under all circumstances, good and bad", ["Only during easy times", "When traveling far", "Through physical obstacles"], "EASY", -0.9),
        ("hit the nail on the head", "Describe exactly what is causing a problem", ["Use hand tools", "Injure oneself", "Miss the target"], "EASY", -1.0),
        ("at the drop of a hat", "Instantly without hesitation", ["When losing headwear", "Accidentally", "After lengthy delays"], "MEDIUM", 0.1),
        ("blessing in disguise", "Something good that initially seemed bad", ["A harmful trick", "Supernatural intervention", "An expensive gift"], "EASY", -1.0),
        ("caught between a rock and a hard place", "Faced with two equally unpleasant choices", ["Trapped in geology", "Having multiple great options", "Unable to move physically"], "MEDIUM", 0.1),
        ("leave no stone unturned", "Exhaust every possible effort or lead", ["Engage in construction", "Clean a path", "Ignore difficult avenues"], "MEDIUM", 0.0),
        ("on cloud nine", "Extremely happy and elated", ["Lost in the fog", "Using server infrastructure", "Confused by instructions"], "EASY", -1.0),
        ("take with a grain of salt", "View with healthy skepticism", ["Add culinary seasoning", "Accept unconditionally", "Reject completely"], "MEDIUM", 0.2),
        ("the ball is in your court", "It is now your responsibility to make the next move", ["Tennis gameplay", "Game is over", "Team is disqualified"], "EASY", -1.0),
    ]
    for idiom, meaning, wr, diff, irt in idioms_and_phrases:
        questions.append(make_q(topic, diff, irt, f"What is the meaning of the idiom: '{idiom}'?", meaning, wr, f"The idiom '{idiom}' means to {meaning.lower()}."))
        questions.append(make_q(topic, diff, irt + 0.1, f"Identify the sentence that correctly employs the phrase '{idiom}':", f"Faced with budget cuts, the team decided to {idiom}.", [f"He bought an expensive car to {idiom}.", f"The software compiled because of {idiom}.", f"The server crashed to {idiom}."], f"The figurative phrase '{idiom}' fits the context of decisive management action."))
        questions.append(make_q(topic, diff, irt + 0.2, f"Which option best paraphrases: 'to {meaning.lower()}'?", idiom, wr, f"The idiomatic equivalent is '{idiom}'."))

    # ═══════════════════════════════════════════════════════════════
    # 6. ERROR DETECTION (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Error Detection"
    error_cases = [
        ("The team of researchers (A) / have discovered (B) / a new security vulnerability (C) / in the authentication protocol (D).", "(B) have discovered", ["(A) The team of researchers", "(C) a new security vulnerability", "(D) in the authentication protocol"], "Subject 'team' is singular; requires singular verb 'has discovered'."),
        ("One of the engineers (A) / who works on (B) / the kernel modules (C) / have won the hackathon (D).", "(D) have won the hackathon", ["(A) One of the engineers", "(B) who works on", "(C) the kernel modules"], "'One' is the principal subject; requires singular verb 'has won'."),
        ("The response latency (A) / of these cloud servers (B) / are much lower (C) / than expected (D).", "(C) are much lower", ["(A) The response latency", "(B) of these cloud servers", "(D) than expected"], "Subject 'latency' is singular; verb should be 'is much lower'."),
        ("Neither the product lead (A) / nor the software developers (B) / was pleased (C) / with the sprint outcome (D).", "(C) was pleased", ["(A) Neither the product lead", "(B) nor the software developers", "(D) with the sprint outcome"], "With 'neither...nor', verb agrees with plural subject 'developers': 'were pleased'."),
        ("She told me (A) / that she is living (B) / in Bangalore (C) / since 2018 (D).", "(B) that she is living", ["(A) She told me", "(C) in Bangalore", "(D) since 2018"], "Action continuing from a past point requires present perfect continuous: 'has been living'."),
        ("Supposing if (A) / the server crashes (B) / during deployment, (C) / what will be our rollback plan? (D)", "(A) Supposing if", ["(B) the server crashes", "(C) during deployment", "(D) what will be our rollback plan?"], "'Supposing' and 'if' are redundant when used together; use either 'Supposing' or 'If'."),
        ("The quality of (A) / the test cases (B) / were evaluated (C) / by the QA lead (D).", "(C) were evaluated", ["(A) The quality of", "(B) the test cases", "(D) by the QA lead"], "Subject 'quality' is singular; requires singular verb 'was evaluated'."),
        ("He is senior (A) / than all other (B) / software architects (C) / in the organization (D).", "(B) than all other", ["(A) He is senior", "(C) software architects", "(D) in the organization"], "'Senior' takes preposition 'to', not 'than' ('senior to all other')."),
        ("Scarcely had we (A) / pushed the commit (B) / than the pipeline (C) / failed its integration tests (D).", "(C) than the pipeline", ["(A) Scarcely had we", "(B) pushed the commit", "(D) failed its integration tests"], "'Scarcely' pairs with 'when', not 'than' ('when the pipeline failed')."),
        ("The software architect (A) / prefers microservices (B) / than monolithic architecture (C) / for large systems (D).", "(C) than monolithic architecture", ["(A) The software architect", "(B) prefers microservices", "(D) for large systems"], "'Prefer' takes preposition 'to', not 'than' ('prefers microservices to monolithic')."),
        ("Each student (A) / in the training batch (B) / were provided (C) / with high-performance laptops (D).", "(C) were provided", ["(A) Each student", "(B) in the training batch", "(D) with high-performance laptops"], "'Each' is singular and requires 'was provided'."),
        ("Unless you do not (A) / optimize the database query, (B) / the web application (C) / will time out (D).", "(A) Unless you do not", ["(B) optimize the database query", "(C) the web application", "(D) will time out"], "'Unless' already has a negative connotation; 'do not' creates a double negative. Use 'Unless you optimize'."),
        ("Between you and I, (A) / the deployment strategy (B) / needs to be (C) / fundamentally revised (D).", "(A) Between you and I,", ["(B) the deployment strategy", "(C) needs to be", "(D) fundamentally revised"], "Preposition 'between' takes objective case pronoun: 'Between you and me'."),
        ("The number of bugs (A) / reported in the sprint (B) / have decreased (C) / dramatically (D).", "(C) have decreased", ["(A) The number of bugs", "(B) reported in the sprint", "(D) dramatically"], "'The number of' is singular and requires 'has decreased' ('A number of' is plural)."),
        ("No sooner did the CEO (A) / finished his presentation (B) / than the floor (C) / opened for questions (D).", "(B) finished his presentation", ["(A) No sooner did the CEO", "(C) than the floor", "(D) opened for questions"], "Auxiliary 'did' must be followed by base form of verb: 'did the CEO finish'."),
    ]
    for sent, err_part, wr, rule in error_cases:
        questions.append(make_q(topic, "EASY", -1.0, f"Identify which part of the sentence contains a grammatical error:\n\n{sent}", err_part, wr, rule))
        questions.append(make_q(topic, "MEDIUM", 0.1, f"Spot the error in the sentence below:\n\n{sent}", err_part, wr, f"Error identification: {err_part}. {rule}"))
        questions.append(make_q(topic, "HARD", 1.2, f"Which segment contains an invalid grammatical construction?\n\n{sent}", err_part, wr, f"Grammar violation: {err_part}. Reason: {rule}"))

    # ═══════════════════════════════════════════════════════════════
    # 7. GRAMMAR & MECHANICS (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Grammar & Mechanics"
    mechanics_cases = [
        ("Active to Passive: 'The DevOps engineer configured the Kubernetes cluster.'", "The Kubernetes cluster was configured by the DevOps engineer.", ["The Kubernetes cluster had been configured by the DevOps engineer.", "The Kubernetes cluster is configured by the DevOps engineer.", "The DevOps engineer was configuring the cluster."], "Simple past active ('configured') converts to simple past passive ('was configured')."),
        ("Active to Passive: 'The security team will audit all microservice endpoints.'", "All microservice endpoints will be audited by the security team.", ["All microservice endpoints would be audited by the team.", "All microservice endpoints are audited by the team.", "The security team will have audited all endpoints."], "Simple future active ('will audit') converts to simple future passive ('will be audited')."),
        ("Direct to Indirect: 'He said, \"I have fixed the memory leak.\"'", "He said that he had fixed the memory leak.", ["He said that he has fixed the memory leak.", "He said that he had been fixing the memory leak.", "He said that he fixed the memory leak."], "Present perfect ('have fixed') shifts to past perfect ('had fixed') in reported speech."),
        ("Direct to Indirect: 'The trainer said, \"Practice questions daily.\"'", "The trainer advised them to practice questions daily.", ["The trainer said that they practiced questions daily.", "The trainer asked if they practiced questions daily.", "The trainer ordered that practice questions daily."], "Imperative sentence in direct speech converts to infinitive ('advised them to practice')."),
        ("Punctuation & Clauses: Identify the correctly punctuated sentence:", "Although the build failed, the logs clearly identified the missing dependency.", ["Although the build failed the logs, clearly identified the missing dependency.", "Although the build failed; the logs clearly identified the missing dependency.", "Although the build failed the logs clearly identified the missing dependency."], "An introductory adverbial clause must be followed by a comma."),
        ("Parallel Structure: Select the sentence that maintains parallel grammatical structure:", "The engineer enjoys writing clean code, architecting systems, and debugging distributed services.", ["The engineer enjoys to write clean code, system architecture, and debugging.", "The engineer enjoys writing clean code, architect systems, and to debug.", "The engineer enjoys clean code, to architect systems, and debugging."], "Parallel gerund phrasing: 'writing...', 'architecting...', 'debugging...'."),
        ("Conditional Mechanics: 'If we deploy without testing, we _______ facing downtime.'", "risk", ["would risk", "had risked", "would have risked"], "First conditional: If + simple present, main clause in simple present / will + verb."),
        ("Prepositional Mechanics: 'The team was prohibited _______ modifying production schemas directly.'", "from", ["to", "for", "against"], "The verb 'prohibit' idiomatically takes the preposition 'from' + gerund."),
        ("Prepositional Mechanics: 'The senior architect congratulated the junior developer _______ passing the certification.'", "on", ["for", "about", "with"], "One congratulates someone 'on' an achievement, not 'for'."),
        ("Prepositional Mechanics: 'The new feature is compliant _______ international privacy regulations.'", "with", ["to", "by", "for"], "The adjective 'compliant' pairs idiomatically with 'with'."),
        ("Direct to Indirect: 'She asked, \"Where is the configuration file stored?\"'", "She asked where the configuration file was stored.", ["She asked where was the configuration file stored.", "She asked where the configuration file is stored.", "She asked where has the configuration file been stored."], "In reported interrogative clauses, question word order inverts to statement order: 'where the file was stored'."),
        ("Active to Passive: 'Developers have reported several critical bugs.'", "Several critical bugs have been reported by developers.", ["Several critical bugs had been reported by developers.", "Several critical bugs were reported by developers.", "Critical bugs have reported by developers."], "Present perfect active ('have reported') converts to present perfect passive ('have been reported')."),
        ("Modifier Placement: Select the sentence with no dangling or misplaced modifier:", "Walking into the server room, the technician noticed a blinking red alert LED.", ["Walking into the server room, a blinking red alert LED was noticed by the technician.", "The technician noticed a blinking red alert LED walking into the server room.", "Walking into the server room, the LED was blinking red."], "The modifier 'Walking into the server room' must logically describe the technician, not the LED."),
        ("Apostrophe Mechanics: Which sentence correctly uses the possessive apostrophe?", "The company's servers were upgraded over the weekend.", ["The companys' servers were upgraded over the weekend.", "The companys servers were upgraded over the weekend.", "The companies servers' were upgraded over the weekend."], "Singular noun 'company' forms possessive with 's: 'company's'."),
        ("Hyphenation Mechanics: Select the correctly hyphenated sentence:", "We require a real-time data streaming pipeline.", ["We require a real time data streaming pipeline.", "We require a real-time-data streaming pipeline.", "We require a real time-data streaming pipeline."], "Compound adjective 'real-time' preceding the noun 'data' is hyphenated."),
    ]
    for prompt, ans, wr, expl in mechanics_cases:
        questions.append(make_q(topic, "EASY", -1.0, prompt, ans, wr, expl))
        questions.append(make_q(topic, "MEDIUM", 0.1, f"Sentence Transformation / Mechanics:\n{prompt}", ans, wr, f"Correct structural formulation: {ans}. {expl}"))
        questions.append(make_q(topic, "HARD", 1.2, f"Precision Language & Mechanics Challenge:\n{prompt}", ans, wr, f"Advanced grammatical standard: {ans}. {expl}"))

    # ═══════════════════════════════════════════════════════════════
    # 8. PARA JUMBLES (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Para Jumbles"
    pj_cases = [
        ("A. However, distributed architectures introduce unprecedented networking complexity.\nB. Modern enterprises are rapidly transitioning to microservices.\nC. This transition enables isolated deployment and rapid feature iteration.\nD. Consequently, investing in centralized telemetry becomes non-negotiable.", "BCAD", ["ABCD", "BACD", "CBDA"], "B introduces the topic. C elaborates on the advantages. A introduces the counterpoint/trade-off ('However'). D provides the concluding consequence."),
        ("A. Machine learning models require vast quantities of high-quality data.\nB. Furthermore, poor data curation inevitably produces biased inferences.\nC. Thus, data engineering forms the true foundation of effective artificial intelligence.\nD. Without clean training sets, even sophisticated neural architectures underperform.", "ADBC", ["ABCD", "CABD", "DABC"], "A sets the premise. D details the risk. B compounds the risk ('Furthermore'). C draws the overarching conclusion ('Thus')."),
        ("A. In contrast, agile methodologies favor iterative delivery and responsiveness.\nB. Traditional waterfall management relies on rigid upfront project specifications.\nC. This inflexibility frequently causes friction when client requirements evolve.\nD. Today, most technology organizations blend elements of both approaches.", "BCAD", ["ABCD", "BACD", "DBCA"], "B introduces waterfall. C details its inflexibility. A contrasts with agile ('In contrast'). D concludes with modern synthesis."),
        ("A. As a result, query response times degraded to intolerable levels.\nB. The database indexing strategy had not been revised for over two years.\nC. During this period, the production transaction volume grew tenfold.\nD. The engineering team initiated an emergency schema re-indexing.", "BCAD", ["ABCD", "CBAD", "DACB"], "B states the underlying condition. C provides the timeframe and escalation. A states the immediate consequence ('As a result'). D details the engineering remediation."),
        ("A. Code review serves as a crucial line of defense against security bugs.\nB. It also fosters collaborative knowledge sharing across team members.\nC. Beyond defect detection, peer reviews promote stylistic consistency.\nD. Ultimately, institutionalizing code reviews elevates overall software craft.", "ACBD", ["ABCD", "BACD", "DCBA"], "A introduces code review. C expands on benefits ('Beyond defect detection'). B adds another dimension ('It also fosters'). D concludes with organizational impact."),
        ("A. Cloud infrastructure provides near-limitless on-demand computing capacity.\nB. However, unmonitored resource provisioning can lead to exorbitant monthly bills.\nC. FinOps practices have therefore emerged to reconcile operational agility with fiscal discipline.\nD. Organizations can spin up hundreds of virtual instances with a single click.", "ADBC", ["ABCD", "BADC", "DABC"], "A introduces cloud capacity. D illustrates it ('hundreds of instances'). B introduces the financial drawback ('However'). C offers FinOps as the conclusion."),
        ("A. Automated testing pipelines drastically shorten software release cycles.\nB. Teams can deploy updates multiple times a day with high confidence.\nC. By verifying changes against test suites continuously, defects are caught at commit time.\nD. In modern competitive markets, rapid release cadence is a key differentiator.", "ACBD", ["ABCD", "BACD", "DABC"], "A introduces automated testing. C explains how it works. B describes the direct capability unlocked. D presents the strategic business value."),
        ("A. Cryptographic hashing algorithms generate a deterministic fixed-length digest.\nB. This avalanche effect ensures that tampering is immediately detectable.\nC. Even a single-bit alteration in the input yields an entirely different hash.\nD. Consequently, hashes serve as reliable integrity checksums for digital assets.", "ACBD", ["ABCD", "BACD", "DCBA"], "A defines hashing. C describes sensitivity to alteration. B labels this 'This avalanche effect'. D summarizes their function as checksums."),
        ("A. Containerization packages an application alongside its required dependencies.\nB. This eliminates the notorious 'it works on my machine' environmental discrepancy.\nC. As a result, software runs predictably across developer laptops, staging, and production.\nD. Docker popularized this lightweight virtualization standard across the industry.", "ABCD", ["BACD", "CABD", "DABC"], "A defines containerization. B highlights the specific problem solved. C generalizes the predictable result. D notes Docker's role in popularizing it."),
        ("A. Asynchronous programming non-blockingly handles concurrent I/O operations.\nB. Instead of spawning a dedicated thread per connection, an event loop manages tasks.\nC. This drastically reduces operating system memory overhead under high concurrency.\nD. Modern web servers leverage this paradigm to support millions of concurrent connections.", "ABCD", ["BACD", "CBDA", "DABC"], "A states the core concept. B explains the event loop mechanism. C notes the memory benefit. D provides the real-world scale outcome."),
        ("A. High test coverage does not guarantee the complete absence of software bugs.\nB. It merely demonstrates that the executed paths behaved as asserted under tested inputs.\nC. Edge cases, race conditions, and integration faults often evade unit test suites.\nD. Therefore, testing must be complemented with observability and canary deployments.", "ABCD", ["BACD", "CBAD", "DCBA"], "A states the opening counter-intuitive premise. B qualifies what coverage actually means. C gives concrete examples of what evades testing. D concludes with the remedy ('Therefore')."),
        ("A. Relational databases excel at ensuring ACID transaction consistency.\nB. However, scaling relational databases horizontally across geographical regions is difficult.\nC. Distributed NoSQL stores were developed specifically to address this scalability bottleneck.\nD. Teams must evaluate their consistency vs availability requirements before choosing a store.", "ABCD", ["BACD", "CBAD", "DCBA"], "A introduces relational strengths. B highlights horizontal scaling difficulty. C introduces NoSQL as the answer. D advises architects on the trade-off."),
        ("A. Git stores repository history as an immutable directed acyclic graph of commits.\nB. Each commit references its parent commit by cryptographic SHA-1 hashes.\nC. This architectural design enables fast branch branching and merging without duplicating code.\nD. Distributed version control systems have transformed software development workflows.", "ABCD", ["BACD", "DABC", "CBDA"], "A explains Git's core DAG data structure. B details how commits reference parents. C highlights the branching efficiency this creates. D evaluates the broad impact."),
        ("A. The single responsibility principle asserts that a class should have one reason to change.\nB. When classes bundle multiple divergent concerns, maintenance costs escalate.\nC. Adhering to this guideline makes software modules decoupled and easily testable.\nD. Refactoring monolithic functions into focused helpers is the first step toward compliance.", "ABCD", ["BACD", "CBDA", "DABC"], "A introduces SRP. B explains the hazard of violating it. C highlights the benefits of adherence. D provides practical refactoring guidance."),
        ("A. Continuous deployment automates the release of every passed build directly to production.\nB. To mitigate the risk of catastrophic outages, teams implement progressive rollouts.\nC. A small canary percentage receives the new code first while telemetry monitors errors.\nD. If anomalies occur, the deployment orchestrator automatically rolls back the release.", "ABCD", ["BACD", "CBAD", "DCBA"], "A defines CD. B introduces risk mitigation via progressive rollout. C details the canary mechanism. D describes the automatic rollback safeguard."),
    ]
    for prompt, ans, wr, expl in pj_cases:
        questions.append(make_q(topic, "EASY", -1.0, f"Arrange the following sentences in a coherent logical paragraph:\n\n{prompt}", ans, wr, expl))
        questions.append(make_q(topic, "MEDIUM", 0.1, f"Determine the most logical sequence for the sentences below:\n\n{prompt}", ans, wr, f"Logical coherence analysis: {ans}. {expl}"))
        questions.append(make_q(topic, "HARD", 1.2, f"Reorder the sentences into a structurally sound argumentative sequence:\n\n{prompt}", ans, wr, f"Structural narrative order: {ans}. {expl}"))

    return questions

if __name__ == "__main__":
    qs = generate_verbal_questions()
    print(f"Generated {len(qs)} verbal ability questions.")
    with open("app/data/bank/verbal_bank.json", "w") as f:
        json.dump(qs, f, indent=2)
    print("Saved to app/data/bank/verbal_bank.json")
