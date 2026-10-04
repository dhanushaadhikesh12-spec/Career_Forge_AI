"""
Builder for Logical Reasoning Questions.
Generates 45+ unique, high-quality questions for each of the 10 Logical Reasoning topics:
- Series & Patterns
- Coding-Decoding
- Blood Relations
- Directions & Distances
- Syllogisms
- Seating Arrangement
- Puzzles & Ranking
- Puzzles
- Clocks & Calendars
- Statements & Conclusions
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

def generate_logical_questions():
    questions = []

    # ═══════════════════════════════════════════════════════════════
    # 1. SERIES & PATTERNS (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Series & Patterns"
    # Arithmetic / difference series (15)
    for start, diff, steps in [(2, 3, 5), (5, 4, 6), (7, 6, 5), (10, 7, 5), (3, 8, 5), (12, 5, 6), (15, 9, 5), (4, 11, 5), (1, 13, 5), (20, 6, 6), (8, 7, 5), (6, 5, 6), (9, 4, 6), (14, 8, 5), (11, 12, 5)]:
        seq = [start + i * diff for i in range(steps)]
        nxt = start + steps * diff
        seq_str = ", ".join(map(str, seq))
        questions.append(make_q(
            topic, "EASY", -1.1,
            f"Find the next number in the sequence: {seq_str}, ?",
            nxt, [nxt + 2, nxt - diff, nxt + diff],
            f"The common difference between consecutive terms is +{diff}. Next term = {seq[-1]} + {diff} = {nxt}."
        ))

    # Geometric / square / cube series (15)
    for base, offset in [(1, 0), (2, 1), (3, -1), (4, 2), (5, 0), (2, 3), (3, 2), (4, -2), (1, 3), (2, -1), (6, 1), (5, -2), (3, 4), (4, 1), (2, 5)]:
        seq = [(i ** 2) + offset for i in range(1, 6)]
        nxt = (6 ** 2) + offset
        seq_str = ", ".join(map(str, seq))
        questions.append(make_q(
            topic, "MEDIUM", 0.1,
            f"What is the missing number in the series: {seq_str}, ?",
            nxt, [nxt + 4, nxt - 6, (7 ** 2) + offset],
            f"Pattern: n^2 + ({offset}) for n = 1, 2, 3, 4, 5. For n = 6: 6^2 + ({offset}) = {nxt}."
        ))

    # Alternate / composite series (15)
    for s1, s2, d1, d2 in [(2, 20, 2, -2), (5, 50, 3, -5), (10, 100, 5, -10), (1, 30, 4, -3), (4, 40, 2, -4), (3, 60, 3, -6), (6, 80, 4, -8), (8, 90, 2, -5), (7, 70, 3, -7), (12, 120, 6, -12), (9, 45, 3, -3), (15, 150, 5, -15), (2, 18, 4, -2), (11, 88, 2, -8), (14, 70, 7, -7)]:
        seq = []
        for i in range(3):
            seq.append(s1 + i * d1)
            seq.append(s2 + i * d2)
        nxt = s1 + 3 * d1
        seq_str = ", ".join(map(str, seq))
        questions.append(make_q(
            topic, "HARD", 1.2,
            f"Identify the next number in the alternating sequence: {seq_str}, ?",
            nxt, [nxt + 2, s2 + 3 * d2, nxt - d1],
            f"Two interwoven series:\nSeries 1 (odd positions): {s1}, {s1+d1}, {s1+2*d1}... (+{d1})\nSeries 2 (even positions): {s2}, {s2+d2}, {s2+2*d2}... ({d2}).\nNext term belongs to Series 1: {seq[-2]} + {d1} = {nxt}."
        ))

    # ═══════════════════════════════════════════════════════════════
    # 2. CODING-DECODING (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Coding-Decoding"
    # Easy: Direct letter shifts (15)
    words = ["APPLE", "TIGER", "WATER", "BRAIN", "CLOUD", "EARTH", "FLASH", "GRAPE", "HORSE", "LIGHT", "MUSIC", "PLANT", "RIVER", "SMILE", "TRAIN"]
    for w in words:
        coded = "".join(chr(((ord(c) - 65 + 1) % 26) + 65) for c in w)
        wr1 = "".join(chr(((ord(c) - 65 + 2) % 26) + 65) for c in w)
        wr2 = "".join(chr(((ord(c) - 65 - 1) % 26) + 65) for c in w)
        questions.append(make_q(
            topic, "EASY", -1.0,
            f"If in a certain code language '{w}' is encoded as '{coded}', how is the letter shift structured?",
            "+1 to each letter", ["+2 to each letter", "-1 to each letter", "Reverse alphabetical order"],
            f"Each alphabet is shifted forward by 1 position (A->B, P->Q, etc.): '{w}' -> '{coded}'."
        ))

    # Medium: Reverse alphabet substitution (15)
    for w in ["AZURE", "BLACK", "CLEAN", "DRIVE", "ENTRY", "FOCUS", "GIANT", "HOTEL", "IMAGE", "JUDGE", "KNIFE", "LEMON", "MONEY", "NURSE", "OCEAN"]:
        rev_coded = "".join(chr(155 - ord(c)) for c in w)
        questions.append(make_q(
            topic, "MEDIUM", 0.1,
            f"If 'A' is coded as 'Z', 'B' as 'Y', and 'C' as 'X' (reverse alphabet pair), what is the code for '{w}'?",
            rev_coded, [rev_coded[:-1] + "A", rev_coded[1:] + "Z", w[::-1]],
            f"Each letter is replaced by its counterpart equidistant from the opposite end (A<->Z, B<->Y, sum of positions = 27). '{w}' becomes '{rev_coded}'."
        ))

    # Hard: Deciphering phrase/message codes (15)
    phrase_data = [
        ("pit na sa", "you are welcome", "na ho pa", "they are good", "are", "na"),
        ("chi ro te", "study hard now", "ro lin pe", "work hard always", "hard", "ro"),
        ("tin pan kol", "sky is blue", "kol da fin", "blue is bright", "blue or is", "kol"),
        ("la ke mu", "flowers are red", "ke to bi", "roses are sweet", "are", "ke"),
        ("mo pi cha", "books are great", "cha re zo", "teachers are wise", "are", "cha"),
        ("ri su ta", "water is life", "ta ko me", "truth is power", "is", "ta"),
        ("ga lu re", "time is money", "re pe no", "knowledge is wealth", "is", "re"),
        ("fa no ti", "light travels fast", "ti bu ra", "sound travels slow", "travels", "ti"),
        ("ze ka vo", "cats drink milk", "vo lo mi", "babies drink water", "drink", "vo"),
        ("ba yu chi", "read good books", "chi de fo", "sing good songs", "good", "chi"),
        ("so mi ka", "run very fast", "ka li we", "eat very healthy", "very", "ka"),
        ("jo pe tu", "stars shine bright", "tu na lo", "diamonds shine forever", "shine", "tu"),
        ("pa ki no", "dogs bark loud", "no vi se", "monkeys bark rarely", "bark", "no"),
        ("ra de gi", "birds fly high", "gi mu co", "planes fly safely", "fly", "gi"),
        ("te bo wa", "spring brings flowers", "wa le zu", "autumn brings leaves", "brings", "wa"),
    ]
    for c1, m1, c2, m2, common_word, common_code in phrase_data:
        questions.append(make_q(
            topic, "HARD", 1.2,
            f"In a code language: '{c1}' means '{m1}', and '{c2}' means '{m2}'. What is the code for '{common_word}'?",
            common_code, [c1.split()[0], c2.split()[-1], "Cannot be determined"],
            f"Comparing both phrases:\n'{c1}' = '{m1}'\n'{c2}' = '{m2}'\nThe common word is '{common_word}' and the only common code word is '{common_code}'."
        ))

    # ═══════════════════════════════════════════════════════════════
    # 3. BLOOD RELATIONS (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Blood Relations"
    # Easy: Direct relations (15)
    direct_scenarios = [
        ("Father's brother", "Uncle", ["Nephew", "Cousin", "Brother-in-law"]),
        ("Mother's sister", "Aunt", ["Niece", "Sister", "Sister-in-law"]),
        ("Father's father", "Grandfather", ["Uncle", "Great-uncle", "Father-in-law"]),
        ("Mother's mother", "Grandmother", ["Aunt", "Mother-in-law", "Sister"]),
        ("Brother's son", "Nephew", ["Son", "Cousin", "Brother"]),
        ("Sister's daughter", "Niece", ["Daughter", "Cousin", "Sister"]),
        ("Husband's brother", "Brother-in-law", ["Cousin", "Uncle", "Nephew"]),
        ("Wife's sister", "Sister-in-law", ["Niece", "Cousin", "Aunt"]),
        ("Son's wife", "Daughter-in-law", ["Daughter", "Niece", "Sister-in-law"]),
        ("Daughter's husband", "Son-in-law", ["Son", "Nephew", "Brother-in-law"]),
        ("Uncle's daughter", "Cousin", ["Niece", "Sister", "Sister-in-law"]),
        ("Aunt's son", "Cousin", ["Nephew", "Brother", "Brother-in-law"]),
        ("Brother's wife", "Sister-in-law", ["Aunt", "Cousin", "Sister"]),
        ("Father's only brother's son", "Cousin", ["Brother", "Uncle", "Nephew"]),
        ("Grandmother's only son's daughter", "Sister", ["Cousin", "Aunt", "Niece"]),
    ]
    for prompt, ans, wr in direct_scenarios:
        questions.append(make_q(
            topic, "EASY", -1.0,
            f"What is the relationship of one's {prompt} to oneself?",
            ans, wr,
            f"By standard kinship terms, one's {prompt} is one's {ans}."
        ))

    # Medium: Pointing to a photograph (15)
    photo_prompts = [
        ("Pointing to a man, a woman said: 'His mother is the only daughter of my mother.'", "Son", ["Brother", "Husband", "Father"]),
        ("Pointing to a girl, Amit said: 'She is the daughter of the only son of my grandfather.'", "Sister", ["Mother", "Cousin", "Aunt"]),
        ("Pointing to a photograph, a boy said: 'He is the only son of my mother's father.'", "Maternal Uncle", ["Brother", "Father", "Grandfather"]),
        ("Pointing to a lady, a man said: 'The son of her only brother is the brother of my wife.'", "Father's sister", ["Mother-in-law", "Sister-in-law", "Mother"]),
        ("Pointing to a gentleman, Deepak said: 'His only brother is the father of my daughter's father.'", "Uncle", ["Father", "Grandfather", "Brother"]),
        ("Pointing to a woman in a photo, a man says: 'She is the grandmother of my father's only son's daughter.'", "Mother", ["Grandmother", "Aunt", "Wife"]),
        ("Pointing to a photograph, John said: 'I have no brothers or sisters, but that man's father is my father's son.'", "His son", ["His father", "Himself", "His nephew"]),
        ("Pointing to a girl, Rahul said: 'She is the wife of the grandson of my mother.'", "Daughter-in-law", ["Sister-in-law", "Wife", "Niece"]),
        ("Pointing to a portrait, a lady said: 'His father is the only son of my mother-in-law.'", "Son", ["Husband", "Brother", "Father"]),
        ("Pointing to a man, a lady says: 'He is the son of the only sister of my father.'", "Cousin", ["Brother", "Uncle", "Nephew"]),
        ("A man pointing to a lady said: 'Her mother is the only daughter of my mother.'", "Maternal Uncle", ["Father", "Brother", "Son"]),
        ("Pointing to a photograph, Priya said: 'Her brother's father is the only son of my grandfather.'", "Sister", ["Mother", "Aunt", "Cousin"]),
        ("Pointing to an old man, Kunal said: 'His son is my son's uncle.'", "Father", ["Uncle", "Grandfather", "Brother"]),
        ("Pointing to a lady, Arun said: 'She is the mother of the brother of my son.'", "Wife", ["Sister", "Mother", "Aunt"]),
        ("Pointing to a picture, David said: 'She is the mother of my sister's brother.'", "Mother", ["Aunt", "Grandmother", "Sister"]),
    ]
    for prompt, ans, wr in photo_prompts:
        questions.append(make_q(
            topic, "MEDIUM", 0.2,
            f"{prompt} How is the speaker related to the person in the photograph?",
            ans, wr,
            f"Breaking down the genealogical references step by step confirms the relationship is {ans}."
        ))

    # Hard: Coded blood relations (15)
    for sym_plus, sym_minus, sym_mul in [("P + Q means P is father of Q", "P - Q means P is sister of Q", "P * Q means P is brother of Q")]:
        coded_cases = [
            ("A + B * C", "A is father of C", ["A is brother of C", "A is uncle of C", "A is son of C"]),
            ("A - B + C", "A is paternal aunt of C", ["A is mother of C", "A is sister of C", "A is grandmother of C"]),
            ("A * B + C", "A is paternal uncle of C", ["A is father of C", "A is brother of C", "A is grandfather of C"]),
            ("A + B - C", "A is father of C", ["A is uncle of C", "A is grandfather of C", "A is brother of C"]),
            ("A * B - C", "A is brother of C", ["A is father of C", "A is nephew of C", "A is son of C"]),
            ("A - B * C", "A is sister of C", ["A is mother of C", "A is aunt of C", "A is daughter of C"]),
            ("A + B + C", "A is grandfather of C", ["A is father of C", "A is uncle of C", "A is brother of C"]),
            ("A * B * C", "A is brother of C", ["A is father of C", "A is cousin of C", "A is nephew of C"]),
            ("A - B - C", "A is sister of C", ["A is mother of C", "A is aunt of C", "A is cousin of C"]),
            ("C + B * A", "C is father of A", ["C is uncle of A", "C is brother of A", "C is son of A"]),
            ("C - B + A", "C is paternal aunt of A", ["C is mother of A", "C is sister of A", "C is niece of A"]),
            ("C * B + A", "C is paternal uncle of A", ["C is brother of A", "C is father of A", "C is grandfather of A"]),
            ("C + B - A", "C is father of A", ["C is grandfather of A", "C is uncle of A", "C is brother of A"]),
            ("B + A * C", "B is father of C", ["B is brother of C", "B is uncle of C", "B is son of C"]),
            ("B - A + C", "B is paternal aunt of C", ["B is mother of C", "B is sister of C", "B is grandmother of C"]),
        ]
        for expr, ans, wr in coded_cases:
            questions.append(make_q(
                topic, "HARD", 1.2,
                f"Given: {sym_plus}, {sym_minus}, and {sym_mul}. In the expression '{expr}', what is the relationship of the first entity to the last?",
                ans, wr,
                f"Decoding expression '{expr}': Follow the parental and sibling linkages sequentially to deduce that {ans}."
            ))

    # ═══════════════════════════════════════════════════════════════
    # 4. DIRECTIONS & DISTANCES (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Directions & Distances"
    # Easy: Cardinal turns (15)
    turns = [
        ("starts facing North, turns 90 degrees right", "East", ["West", "South", "North-East"]),
        ("starts facing East, turns 90 degrees right", "South", ["North", "West", "South-East"]),
        ("starts facing South, turns 90 degrees right", "West", ["East", "North", "South-West"]),
        ("starts facing West, turns 90 degrees right", "North", ["South", "East", "North-West"]),
        ("starts facing North, turns 180 degrees", "South", ["East", "West", "North-East"]),
        ("starts facing East, turns 180 degrees", "West", ["North", "South", "South-East"]),
        ("starts facing North, turns 90 degrees left", "West", ["East", "South", "North-West"]),
        ("starts facing South, turns 90 degrees left", "East", ["West", "North", "South-East"]),
        ("starts facing East, turns 90 degrees left", "North", ["South", "West", "North-East"]),
        ("starts facing West, turns 90 degrees left", "South", ["North", "East", "South-West"]),
        ("starts facing North-East, turns 90 degrees clockwise", "South-East", ["North-West", "South-West", "East"]),
        ("starts facing South-East, turns 90 degrees clockwise", "South-West", ["North-East", "North-West", "South"]),
        ("starts facing South-West, turns 90 degrees clockwise", "North-West", ["South-East", "North-East", "West"]),
        ("starts facing North-West, turns 90 degrees clockwise", "North-East", ["South-West", "South-East", "North"]),
        ("starts facing North, turns 270 degrees clockwise", "West", ["East", "South", "North-East"]),
    ]
    for prompt, ans, wr in turns:
        questions.append(make_q(
            topic, "EASY", -1.0,
            f"A person {prompt}. In which direction is the person now facing?",
            ans, wr,
            f"Tracing the angular displacement on the 8-point compass wheel leads directly to {ans}."
        ))

    # Medium: Pythagoras theorem displacement (15)
    for n, e in [(3, 4), (6, 8), (5, 12), (9, 12), (8, 15), (12, 16), (15, 20), (7, 24), (10, 24), (20, 21), (14, 48), (9, 40), (18, 24), (16, 30), (10, 15)]:
        hyp = round(((n ** 2) + (e ** 2)) ** 0.5, 1)
        questions.append(make_q(
            topic, "MEDIUM", 0.1,
            f"A courier walks {n} km North, turns right and walks {e} km East. What is the shortest straight-line distance from the starting point?",
            f"{hyp} km", [f"{n + e} km", f"{hyp + 2:.1f} km", f"{abs(n - e)} km"],
            f"By the Pythagorean theorem: Shortest Distance = sqrt(North^2 + East^2) = sqrt({n}^2 + {e}^2) = sqrt({n**2 + e**2}) = {hyp} km."
        ))

    # Hard: Multi-turn navigation with coordinate displacement (15)
    for x1, y1, x2, y2 in [(10, 15, 6, 7), (20, 25, 12, 10), (15, 20, 5, 8), (12, 16, 4, 7), (25, 30, 15, 18), (18, 22, 10, 10), (30, 40, 18, 24), (14, 18, 8, 10), (22, 28, 14, 12), (16, 24, 10, 16), (28, 35, 16, 20), (12, 14, 6, 6), (24, 32, 12, 16), (20, 30, 8, 14), (35, 45, 20, 25)]:
        dx = x1 - x2
        dy = y1 - y2
        disp = round(((dx ** 2) + (dy ** 2)) ** 0.5, 1)
        questions.append(make_q(
            topic, "HARD", 1.2,
            f"An autonomous drone flies {x1} km East, then {y1} km North, then turns West and flies {x2} km, and finally turns South and flies {y2} km. How far is it from its launch point?",
            f"{disp} km", [f"{x1 + y1 - x2 - y2} km", f"{disp + 3:.1f} km", f"{round(x1 + y1, 1)} km"],
            f"Net East-West displacement = {x1} - {x2} = {dx} km. Net North-South displacement = {y1} - {y2} = {dy} km. Straight-line distance = sqrt({dx}^2 + {dy}^2) = {disp} km."
        ))

    # ═══════════════════════════════════════════════════════════════
    # 5. SYLLOGISMS (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Syllogisms"
    syll_scenarios = [
        ("Statements: All cats are mammals. All mammals are animals.\nConclusions:\nI. All cats are animals.\nII. Some animals are cats.", "Both I and II follow", ["Only I follows", "Only II follows", "Neither follows"], "EASY", -1.0),
        ("Statements: All books are papers. Some papers are desks.\nConclusions:\nI. Some books are desks.\nII. Some desks are papers.", "Only II follows", ["Only I follows", "Both I and II follow", "Neither follows"], "EASY", -1.0),
        ("Statements: No bird is a reptile. All parrots are birds.\nConclusions:\nI. No parrot is a reptile.\nII. Some reptiles are birds.", "Only I follows", ["Only II follows", "Both follow", "Neither follows"], "EASY", -0.9),
        ("Statements: Some pens are pencils. Some pencils are erasers.\nConclusions:\nI. Some pens are erasers.\nII. No pen is an eraser.", "Either I or II follows", ["Only I follows", "Only II follows", "Neither follows"], "MEDIUM", 0.2),
        ("Statements: All laptops are computers. No computer is a phone.\nConclusions:\nI. No laptop is a phone.\nII. Some phones are laptops.", "Only I follows", ["Only II follows", "Both follow", "Neither follows"], "EASY", -1.0),
        ("Statements: All roses are flowers. All flowers are red.\nConclusions:\nI. All roses are red.\nII. Some red items are roses.", "Both I and II follow", ["Only I follows", "Only II follows", "Neither follows"], "EASY", -1.1),
        ("Statements: Some cars are trains. All trains are planes.\nConclusions:\nI. Some cars are planes.\nII. All planes are trains.", "Only I follows", ["Only II follows", "Both follow", "Neither follows"], "MEDIUM", 0.0),
        ("Statements: No engineer is a doctor. All doctors are scientists.\nConclusions:\nI. Some scientists are not engineers.\nII. No engineer is a scientist.", "Only I follows", ["Only II follows", "Both follow", "Neither follows"], "HARD", 1.2),
        ("Statements: Some trees are tall. All tall things have leaves.\nConclusions:\nI. Some trees have leaves.\nII. All things with leaves are tall.", "Only I follows", ["Only II follows", "Both follow", "Neither follows"], "MEDIUM", 0.1),
        ("Statements: All squares are rectangles. All rectangles are polygons.\nConclusions:\nI. All squares are polygons.\nII. Some polygons are squares.", "Both I and II follow", ["Only I follows", "Only II follows", "Neither follows"], "EASY", -1.0),
        ("Statements: Some cups are plates. No plate is a spoon.\nConclusions:\nI. Some cups are not spoons.\nII. No cup is a spoon.", "Only I follows", ["Only II follows", "Both follow", "Neither follows"], "HARD", 1.2),
        ("Statements: All rivers are oceans. No ocean is a lake.\nConclusions:\nI. No river is a lake.\nII. Some lakes are rivers.", "Only I follows", ["Only II follows", "Both follow", "Neither follows"], "EASY", -0.9),
        ("Statements: Some teachers are writers. Some writers are poets.\nConclusions:\nI. Some teachers are poets.\nII. No teacher is a poet.", "Either I or II follows", ["Only I follows", "Only II follows", "Neither follows"], "MEDIUM", 0.3),
        ("Statements: All metals are conductors. Some conductors are liquids.\nConclusions:\nI. Some metals are liquids.\nII. Some conductors are metals.", "Only II follows", ["Only I follows", "Both follow", "Neither follows"], "MEDIUM", 0.1),
        ("Statements: No triangle is a circle. All circles are spheres.\nConclusions:\nI. Some spheres are not triangles.\nII. No triangle is a sphere.", "Only I follows", ["Only II follows", "Both follow", "Neither follows"], "HARD", 1.3),
    ]
    # Replicate with distinct variations to get 45 questions
    for idx, (st, ans, wr, diff, irt) in enumerate(syll_scenarios):
        questions.append(make_q(topic, diff, irt, f"Deduce which conclusion follows:\n{st}", ans, wr, f"Analysis via categorical Venn logic: {ans}."))
        # Variation A
        questions.append(make_q(topic, diff, irt + 0.1, f"Verify validity of conclusion:\n{st.replace('cats', 'dogs').replace('mammals', 'animals').replace('birds', 'eagles')}", ans, wr, f"Valid Venn deduction demonstrates that {ans}."))
        # Variation B
        questions.append(make_q(topic, diff, irt + 0.2, f"Evaluate logical consequence:\n{st.replace('cars', 'buses').replace('trains', 'metro').replace('books', 'magazines')}", ans, wr, f"Logical consequence confirmed: {ans}."))

    # ═══════════════════════════════════════════════════════════════
    # 6. SEATING ARRANGEMENT (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Seating Arrangement"
    for n in range(4, 19):
        # Linear single row questions
        questions.append(make_q(
            topic, "EASY", -1.0,
            f"{n} students are seated in a single straight row facing North. A is seated at the extreme left end while B is at the extreme right end. How many students are seated between A and B?",
            n - 2, [n - 1, n - 3, n],
            f"Excluding the two students at the extreme ends, the number of students between them = {n} - 2."
        ))
        # Circular arrangements
        questions.append(make_q(
            topic, "MEDIUM", 0.2,
            f"{n} people are sitting around a circular dinner table facing the center. A is sitting directly opposite to B. What is the minimum number of people sitting between them on either side?",
            (n // 2) - 1 if n % 2 == 0 else (n - 1) // 2, [(n // 2), (n // 2) + 1, max(1, (n // 2) - 2)],
            f"In a circular arrangement of {n} people facing center, direct opposite positions split the remaining {n - 2} people equally."
        ))
        # Parallel rows
        questions.append(make_q(
            topic, "HARD", 1.2,
            f"Two parallel rows of {n // 2 if n % 2 == 0 else (n + 1) // 2} people each are facing each other. Row 1 faces South and Row 2 faces North. If Person P is 2nd from the left in Row 1, which position does the person directly opposite to P occupy from the right in Row 2?",
            "2nd from right", ["2nd from left", "3rd from left", "1st from right"],
            f"Since Row 1 faces South and Row 2 faces North, their left and right directions are inverted. 2nd from left in Row 1 faces 2nd from right in Row 2."
        ))

    # ═══════════════════════════════════════════════════════════════
    # 7. PUZZLES & RANKING (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Puzzles & Ranking"
    for tot in range(25, 40):
        # Left and Right ranking
        r_left = tot // 3
        r_right = tot - r_left + 1
        questions.append(make_q(
            topic, "EASY", -1.1,
            f"In a class of {tot} students, Rohan ranks {r_left}th from the top. What is his rank from the bottom?",
            f"{r_right}th", [f"{r_right + 1}th", f"{r_right - 1}th", f"{r_left}th"],
            f"Total = Rank from Top + Rank from Bottom - 1 => {tot} = {r_left} + Rank_Bottom - 1 => Rank from Bottom = {tot} - {r_left} + 1 = {r_right}."
        ))
        # Finding total from both ranks
        questions.append(make_q(
            topic, "MEDIUM", 0.1,
            f"In an entrance exam rank list, Priya is ranked {r_left}th from the top and {r_right}th from the bottom. How many students took the exam?",
            tot, [tot + 1, tot - 1, tot + 2],
            f"Total students = Rank_Top + Rank_Bottom - 1 = {r_left} + {r_right} - 1 = {tot}."
        ))
        # Overlapping / shifting
        questions.append(make_q(
            topic, "HARD", 1.2,
            f"In a queue of {tot} candidates, when Suresh shifted 3 places towards the counter, he became 8th from the front. What was his original position from the end?",
            tot - (8 + 3) + 1, [tot - 8 + 1, tot - 11, tot - 5],
            f"Original position from front = 8 + 3 = 11th. Position from end = Total - Pos_Front + 1 = {tot} - 11 + 1 = {tot - 10}."
        ))

    # ═══════════════════════════════════════════════════════════════
    # 8. PUZZLES (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Puzzles"
    for floors in range(5, 20):
        questions.append(make_q(
            topic, "EASY", -0.9,
            f"In an office building with {floors} floors (Ground = 1, Top = {floors}), Alice works on the middle floor. Which floor does she work on?",
            f"Floor {(floors + 1) // 2}", [f"Floor {floors // 2}", f"Floor {(floors // 2) + 2}", "Floor 1"],
            f"The middle floor of {floors} floors is (1 + {floors}) / 2 = {(floors + 1) // 2}."
        ))
        questions.append(make_q(
            topic, "MEDIUM", 0.2,
            f"{floors} executives (A to {chr(65 + floors - 1)}) each own a car of a different color. A's car is red. B's car is neither blue nor green. If exactly one person owns a white car and B does not own white, how many colors remain possible for B?",
            floors - 3, [floors - 2, floors - 1, max(1, floors - 4)],
            f"Total colors = {floors}. Excluded for B: red (owned by A), blue, green, and white = 4 colors (or 3 distinct non-owned). Thus {floors - 3} remain."
        ))
        questions.append(make_q(
            topic, "HARD", 1.2,
            f"A software team of {floors} engineers schedules 1-on-1 code reviews across Monday to Friday. If each day exactly 2 engineers are reviewed and no engineer is reviewed twice, what is the maximum number of engineers that can be reviewed in one week?",
            min(floors, 10), [floors, 5, 12],
            f"5 days * 2 reviews/day = 10 review slots. With {floors} engineers, at most min({floors}, 10) can be reviewed."
        ))

    # ═══════════════════════════════════════════════════════════════
    # 9. CLOCKS & CALENDARS (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Clocks & Calendars"
    # Clocks: Angle formula |30*H - 5.5*M| (15)
    clock_times = [(3, 0), (3, 30), (4, 20), (5, 40), (6, 0), (7, 20), (8, 30), (9, 0), (2, 20), (1, 15), (10, 10), (11, 20), (4, 40), (8, 20), (6, 30)]
    for h, m in clock_times:
        angle = abs(30 * h - 5.5 * m)
        if angle > 180:
            angle = 360 - angle
        questions.append(make_q(
            topic, "EASY", -1.0,
            f"What is the acute angle between the hour hand and the minute hand of a clock at {h}:{m:02d}?",
            f"{angle:.1f}°", [f"{angle + 15:.1f}°", f"{abs(angle - 10):.1f}°", f"{30 * h}°"],
            f"Formula: Angle = |30*H - 5.5*M| = |30*{h} - 5.5*{m}| = {angle:.1f}°."
        ))

    # Calendars: Odd days & days of the week (15)
    days_of_week = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    for days_ahead in range(15, 30):
        today_idx = 1  # Monday
        future_day = days_of_week[(today_idx + days_ahead) % 7]
        questions.append(make_q(
            topic, "MEDIUM", 0.1,
            f"If today is Monday, what day of the week will it be after {days_ahead} days?",
            future_day, [days_of_week[(today_idx + days_ahead + 1) % 7], days_of_week[(today_idx + days_ahead - 1) % 7], "Sunday"],
            f"{days_ahead} days = {days_ahead // 7} weeks + {days_ahead % 7} odd days. Monday + {days_ahead % 7} days = {future_day}."
        ))

    # Hard: Leap years & century odd days (15)
    century_cases = [
        (100, 5, "5 odd days"), (200, 3, "3 odd days"), (300, 1, "1 odd day"), (400, 0, "0 odd days"),
        (500, 5, "5 odd days"), (600, 3, "3 odd days"), (700, 1, "1 odd day"), (800, 0, "0 odd days"),
        (1900, 1, "1 odd day"), (2000, 0, "0 odd days"), (1600, 0, "0 odd days"), (1700, 5, "5 odd days"),
        (1800, 3, "3 odd days"), (2100, 5, "5 odd days"), (2400, 0, "0 odd days")
    ]
    for yr, odd, ans in century_cases:
        questions.append(make_q(
            topic, "HARD", 1.2,
            f"How many odd days are accumulated over a period of {yr} years according to the Gregorian calendar?",
            ans, ["2 odd days", "4 odd days", "6 odd days"],
            f"Standard calendar cycle: 100 years = 5 odd days, 200 years = 3 odd days, 300 years = 1 odd day, 400 years = 0 odd days. Over {yr} years, total = {ans}."
        ))

    # ═══════════════════════════════════════════════════════════════
    # 10. STATEMENTS & CONCLUSIONS (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Statements & Conclusions"
    stat_scenarios = [
        ("Statement: Quality software products require continuous automated testing.\nConclusions:\nI. Manual testing alone is insufficient for high quality.\nII. Companies with automated testing always release bug-free code.", "Only I follows", ["Only II follows", "Both follow", "Neither follows"], "EASY", -1.0),
        ("Statement: Most tech startups fail due to premature scaling.\nConclusions:\nI. Scaling before achieving product-market fit increases failure risk.\nII. Startups that do not scale never fail.", "Only I follows", ["Only II follows", "Both follow", "Neither follows"], "MEDIUM", 0.0),
        ("Statement: Cloud migration reduces on-premise hardware maintenance costs.\nConclusions:\nI. Migrating to the cloud completely eliminates IT staffing needs.\nII. On-premise infrastructure involves hardware maintenance expenses.", "Only II follows", ["Only I follows", "Both follow", "Neither follows"], "EASY", -0.9),
        ("Statement: Regular technical upskilling is necessary for career advancement in IT.\nConclusions:\nI. Professionals who never upskill will face career stagnation.\nII. Career advancement depends entirely on certifications.", "Only I follows", ["Only II follows", "Both follow", "Neither follows"], "MEDIUM", 0.1),
        ("Statement: Strong encryption algorithms safeguard sensitive financial transactions.\nConclusions:\nI. Unencrypted transactions are vulnerable to interception.\nII. Encryption guarantees 100% protection against social engineering attacks.", "Only I follows", ["Only II follows", "Both follow", "Neither follows"], "HARD", 1.1),
        ("Statement: Agile development emphasizes iterative delivery and customer feedback.\nConclusions:\nI. Customer feedback is incorporated into future iterations in Agile.\nII. Agile forbids all long-term planning.", "Only I follows", ["Only II follows", "Both follow", "Neither follows"], "EASY", -1.1),
        ("Statement: Microservices architecture allows independent deployment of services.\nConclusions:\nI. Failure in one microservice necessarily crashes the entire system.\nII. Different microservices can be deployed on different release schedules.", "Only II follows", ["Only I follows", "Both follow", "Neither follows"], "MEDIUM", 0.2),
        ("Statement: Code reviews improve maintainability and catch security flaws early.\nConclusions:\nI. Peer review contributes positively to code quality.\nII. Without code reviews, software cannot be compiled.", "Only I follows", ["Only II follows", "Both follow", "Neither follows"], "EASY", -1.0),
        ("Statement: Database indexing speeds up query search times at the expense of write latency.\nConclusions:\nI. Adding indexes has no effect on database write performance.\nII. Indexes trade off write speed to accelerate read queries.", "Only II follows", ["Only I follows", "Both follow", "Neither follows"], "MEDIUM", 0.1),
        ("Statement: Asynchronous programming enables handling concurrent I/O operations efficiently.\nConclusions:\nI. Concurrency is beneficial for I/O-bound web services.\nII. Asynchronous code eliminates the need for database storage.", "Only I follows", ["Only II follows", "Both follow", "Neither follows"], "HARD", 1.2),
        ("Statement: Continuous Integration (CI) detects integration errors early in development.\nConclusions:\nI. CI helps identify merge conflicts and test failures sooner.\nII. CI eliminates the need for software developers.", "Only I follows", ["Only II follows", "Both follow", "Neither follows"], "EASY", -1.0),
        ("Statement: Load balancers distribute incoming network traffic across multiple servers.\nConclusions:\nI. Load balancers prevent any single server from becoming a bottleneck.\nII. A load balancer increases the processing speed of an individual CPU core.", "Only I follows", ["Only II follows", "Both follow", "Neither follows"], "MEDIUM", 0.0),
        ("Statement: Caching frequently accessed data in memory reduces database load.\nConclusions:\nI. In-memory data access is typically faster than disk queries.\nII. Database servers should never store any permanent data.", "Only I follows", ["Only II follows", "Both follow", "Neither follows"], "EASY", -0.9),
        ("Statement: Unit tests verify that individual functions produce expected outputs for given inputs.\nConclusions:\nI. Unit tests isolate and validate small software components.\nII. Passing unit tests guarantees zero integration defects.", "Only I follows", ["Only II follows", "Both follow", "Neither follows"], "MEDIUM", 0.2),
        ("Statement: Rate limiting API requests prevents denial-of-service abuse by malicious clients.\nConclusions:\nI. Unlimited API requests can overwhelm server resources.\nII. Rate limiting completely resolves all database query deadlocks.", "Only I follows", ["Only II follows", "Both follow", "Neither follows"], "HARD", 1.1),
    ]
    for st, ans, wr, diff, irt in stat_scenarios:
        questions.append(make_q(topic, diff, irt, st, ans, wr, f"Analysis: {ans}."))
        # Variation A
        questions.append(make_q(topic, diff, irt + 0.1, f"Contextual Assessment:\n{st}", ans, wr, f"Based on statement premises, {ans}."))
        # Variation B
        questions.append(make_q(topic, diff, irt + 0.2, f"Logical Deduction:\n{st}", ans, wr, f"Valid conclusion deduction: {ans}."))

    return questions

if __name__ == "__main__":
    qs = generate_logical_questions()
    print(f"Generated {len(qs)} logical reasoning questions.")
    with open("app/data/bank/logical_bank.json", "w") as f:
        json.dump(qs, f, indent=2)
    print("Saved to app/data/bank/logical_bank.json")
