"""
Logical Reasoning & Verbal Ability question bank for campus placement readiness.
Covers:
- Logical: Series & Patterns, Coding-Decoding, Blood Relations, Directions & Distances,
           Syllogisms, Seating Arrangement, Puzzles & Ranking, Clocks & Calendars, Statements & Conclusions.
- Verbal:  Vocabulary & Usage, Sentence Completion, Error Detection,
           Reading Comprehension, Grammar & Mechanics, Para Jumbles.
"""
from app.models.content import DifficultyLevel

LOGICAL_VERBAL_QUESTIONS = [
    # ═══════════════════════════════════════════════════════════════
    # SERIES & PATTERNS (15 Questions)
    # ═══════════════════════════════════════════════════════════════
    {
        "topic": "Series & Patterns", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "Find the missing number in the series: 3, 7, 11, 15, __, 23",
        "explanation": "Arithmetic progression with a common difference of +4: 15 + 4 = 19.",
        "options": [("18", False), ("19", True), ("20", False), ("21", False)],
    },
    {
        "topic": "Series & Patterns", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "Find the next term in the geometric series: 2, 6, 18, 54, __",
        "explanation": "Multiply each term by 3: 54 * 3 = 162.",
        "options": [("108", False), ("144", False), ("162", True), ("180", False)],
    },
    {
        "topic": "Series & Patterns", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "Complete the letter series: B, D, F, H, __",
        "explanation": "Each letter advances by 2 positions: H (8) + 2 = J (10).",
        "options": [("I", False), ("J", True), ("K", False), ("L", False)],
    },
    {
        "topic": "Series & Patterns", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "Find the next term: 1, 4, 9, 16, 25, __",
        "explanation": "Square numbers: 1^2, 2^2, 3^2, 4^2, 5^2, 6^2 = 36.",
        "options": [("30", False), ("34", False), ("36", True), ("49", False)],
    },
    {
        "topic": "Series & Patterns", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "Find the missing term: 100, 95, 85, 70, __",
        "explanation": "Differences are -5, -10, -15, so next difference is -20: 70 - 20 = 50.",
        "options": [("45", False), ("50", True), ("55", False), ("60", False)],
    },
    {
        "topic": "Series & Patterns", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "Find the missing number in the series: 2, 5, 10, 17, 26, __",
        "explanation": "Pattern is n^2 + 1: 1^2+1=2, 2^2+1=5, 3^2+1=10, 4^2+1=17, 5^2+1=26, 6^2+1 = 37.",
        "options": [("35", False), ("36", False), ("37", True), ("38", False)],
    },
    {
        "topic": "Series & Patterns", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "Find the missing term: 6, 13, 28, 59, __",
        "explanation": "Pattern is x2 + 1, x2 + 2, x2 + 3...: 6*2+1=13; 13*2+2=28; 28*2+3=59; 59*2+4 = 122.",
        "options": [("118", False), ("120", False), ("122", True), ("125", False)],
    },
    {
        "topic": "Series & Patterns", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "Complete the alphanumeric series: A1Z, C3X, E5V, __",
        "explanation": "First letter +2: A, C, E, G. Number +2: 1, 3, 5, 7. Last letter -2: Z, X, V, T. Result is G7T.",
        "options": [("F6U", False), ("G7T", True), ("G6U", False), ("H7S", False)],
    },
    {
        "topic": "Series & Patterns", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "Find the odd one out: 3, 5, 7, 9, 11, 13",
        "explanation": "9 is a composite number (3*3), whereas all others are prime numbers.",
        "options": [("7", False), ("9", True), ("11", False), ("13", False)],
    },
    {
        "topic": "Series & Patterns", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "Find the next number: 1, 2, 6, 24, 120, __",
        "explanation": "Factorial series: 1!, 2!, 3!, 4!, 5!, 6! = 720.",
        "options": [("600", False), ("640", False), ("720", True), ("840", False)],
    },
    {
        "topic": "Series & Patterns", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "Find the next number in the sequence: 4, 18, 48, 100, 180, __",
        "explanation": "Pattern is n^3 - n^2 (or n^2*(n-1)): for n=2: 8-4=4; n=3: 27-9=18; n=4: 64-16=48; n=5: 125-25=100; n=6: 216-36=180; n=7: 343-49 = 294.",
        "options": [("250", False), ("280", False), ("294", True), ("310", False)],
    },
    {
        "topic": "Series & Patterns", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "What replaces the question mark: 2, 12, 36, 80, 150, ?",
        "explanation": "Pattern is n^3 + n^2: for n=1: 1+1=2; n=2: 8+4=12; n=3: 27+9=36; n=4: 64+16=80; n=5: 125+25=150; n=6: 216+36 = 252.",
        "options": [("210", False), ("240", False), ("252", True), ("270", False)],
    },
    {
        "topic": "Series & Patterns", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "Find the next number: 8, 27, 64, 125, 216, __",
        "explanation": "Cubes of consecutive integers: 2^3, 3^3, 4^3, 5^3, 6^3, 7^3 = 343.",
        "options": [("312", False), ("324", False), ("343", True), ("512", False)],
    },
    {
        "topic": "Series & Patterns", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "In the series 3, 8, 6, 14, __, 20, 12; what is the missing term?",
        "explanation": "Two alternating series: (3, 6, 9, 12) with diff +3, and (8, 14, 20) with diff +6. The missing term is 3rd term of first series: 6 + 3 = 9.",
        "options": [("8", False), ("9", True), ("10", False), ("11", False)],
    },
    {
        "topic": "Series & Patterns", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "Find the wrong number in the sequence: 1, 2, 6, 15, 31, 56, 91",
        "explanation": "Differences should be consecutive squares: 2-1=1 (1^2), 6-2=4 (2^2), 15-6=9 (3^2), 31-15=16 (4^2), 56-31=25 (5^2), next should be 56 + 36 = 92. The given number 91 is wrong.",
        "options": [("15", False), ("31", False), ("56", False), ("91", True)],
    },

    # ═══════════════════════════════════════════════════════════════
    # CODING-DECODING (15 Questions)
    # ═══════════════════════════════════════════════════════════════
    {
        "topic": "Coding-Decoding", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "If 'CAT' is coded as 'DBU' (+1 shift), how is 'DOG' coded?",
        "explanation": "Each letter is shifted forward by 1: D->E, O->P, G->H => EPH.",
        "options": [("EPH", True), ("FPH", False), ("EQH", False), ("EPI", False)],
    },
    {
        "topic": "Coding-Decoding", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "If 'APPLE' is coded as 'EQTPI' (+4 shift), how is 'BALL' coded?",
        "explanation": "Shift each letter by +4: B(2)->F(6), A(1)->E(5), L(12)->P(16), L(12)->P(16) => FEPP.",
        "options": [("FEPP", True), ("FDPP", False), ("GEQQ", False), ("EFPP", False)],
    },
    {
        "topic": "Coding-Decoding", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "In a certain code, 'ROAD' is written as 'URDG'. How is 'SWAN' written in that code?",
        "explanation": "Each letter is shifted +3: S->V, W->Z, A->D, N->Q => VZDQ.",
        "options": [("VZDQ", True), ("UXDQ", False), ("VZCQ", False), ("UYDQ", False)],
    },
    {
        "topic": "Coding-Decoding", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "If RED is coded as 27 (18+5+4), what is the code for BLUE?",
        "explanation": "B=2, L=12, U=21, E=5. Sum = 2 + 12 + 21 + 5 = 40.",
        "options": [("38", False), ("40", True), ("42", False), ("45", False)],
    },
    {
        "topic": "Coding-Decoding", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "If 'WATER' is called 'FOOD', 'FOOD' is called 'TREE', and 'TREE' is called 'SKY', what do we drink when thirsty?",
        "explanation": "We drink WATER. In the code, WATER is called FOOD. So we drink FOOD.",
        "options": [("WATER", False), ("FOOD", True), ("TREE", False), ("SKY", False)],
    },
    {
        "topic": "Coding-Decoding", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "In a certain code language, '786' means 'study very hard', '958' means 'hard work pays', and '645' means 'study and work'. Which digit represents 'very'?",
        "explanation": "'study' is common in 786 and 645 => 6. 'hard' is common in 786 and 958 => 8. In '786', the remaining digit '7' represents 'very'.",
        "options": [("6", False), ("7", True), ("8", False), ("9", False)],
    },
    {
        "topic": "Coding-Decoding", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "If 'SYSTEM' is coded as 'SYSMET' and 'NEARER' as 'AENRER', how is 'FRACTION' coded?",
        "explanation": "Split word into two halves and reverse each half: FRAC -> CARF, TION -> NOIT => CARFNOIT.",
        "options": [("CARFNOIT", True), ("NOITCARF", False), ("CARFTION", False), ("FRACNOIT", False)],
    },
    {
        "topic": "Coding-Decoding", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "If 'DELHI' is coded as '73541' and 'CALCUTTA' as '82589662', how can 'CALICUT' be coded?",
        "explanation": "Direct letter substitution: C=8, A=2, L=5, I=1, C=8, U=9, T=6 => 8251896.",
        "options": [("5279431", False), ("8251896", True), ("8543691", False), ("8251869", False)],
    },
    {
        "topic": "Coding-Decoding", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "If 'LEADER' is coded as '20-13-9-12-13-26', what is the code pattern for the word 'LIGHT'?",
        "explanation": "Each letter position is increased by 8: L(12)+8=20, E(5)+8=13, A(1)+8=9, etc. For LIGHT: L(12)+8=20, I(9)+8=17, G(7)+8=15, H(8)+8=16, T(20)+8=28 => 20-17-15-16-28.",
        "options": [("20-16-15-16-28", False), ("20-17-15-16-28", True), ("19-17-15-16-27", False), ("20-17-14-16-28", False)],
    },
    {
        "topic": "Coding-Decoding", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "If 'BEAT' is written as 'YVZG' (opposite alphabet pairs), what will be the code for 'MILD'?",
        "explanation": "Opposite letter mapping (sum of positions = 27): M(13)->N(14), I(9)->R(18), L(12)->O(15), D(4)->W(23) => NROW.",
        "options": [("NROV", False), ("NROW", True), ("MROW", False), ("NQOW", False)],
    },
    {
        "topic": "Coding-Decoding", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "If 'MACHINE' is coded as '19-7-9-14-15-20-11', how will 'DANGER' be coded in that system?",
        "explanation": "Each letter rank is incremented by 6: M(13)+6=19, A(1)+6=7, C(3)+6=9... For DANGER: D(4)+6=10, A(1)+6=7, N(14)+6=20, G(7)+6=13, E(5)+6=11, R(18)+6=24 => 10-7-20-13-11-24.",
        "options": [("10-7-20-13-11-24", True), ("11-7-20-13-11-24", False), ("10-8-20-13-11-23", False), ("10-7-19-13-11-24", False)],
    },
    {
        "topic": "Coding-Decoding", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "In a code, 'pit dar na' means 'you are good', 'dar tok pa' means 'good and bad', and 'tim na tok' means 'they are bad'. What represents 'they'?",
        "explanation": "Compare 1 and 3: 'na' is common => 'are'. Compare 2 and 3: 'tok' is common => 'bad'. In statement 3 ('tim na tok' = 'they are bad'), 'tim' must represent 'they'.",
        "options": [("na", False), ("tok", False), ("tim", True), ("pit", False)],
    },
    {
        "topic": "Coding-Decoding", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "If 'PAINT' is coded as '74128' and 'EXCEL' is coded as '93596', how would you encode 'ACCEPT'?",
        "explanation": "A=4, C=5, C=5, E=9, P=7, T=8 => 455978.",
        "options": [("455978", True), ("455987", False), ("455798", False), ("455976", False)],
    },
    {
        "topic": "Coding-Decoding", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "In a certain code, 'TELEPHONE' is written as 'ENOHPELET'. How is 'ALGORITHM' written?",
        "explanation": "The word is completely reversed: A-L-G-O-R-I-T-H-M reversed is M-H-T-I-R-O-G-L-A.",
        "options": [("MHTIROGLA", True), ("MHTROIGLA", False), ("MHTIRGOLA", False), ("MHTIROGAL", False)],
    },
    {
        "topic": "Coding-Decoding", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "If 'GLAMOUR' is coded as 'IJCNMWP' (+2, -1 alternate pattern), how is 'MISRULE' coded?",
        "explanation": "+2, -1 alternate: M(+2)->O, I(-1)->H, S(+2)->U, R(-1)->Q, U(+2)->W, L(-1)->K, E(+2)->G => OHUQWKG.",
        "options": [("OGUQWKG", False), ("OHUQWKG", True), ("OHVQWKG", False), ("OHUQVKG", False)],
    },

    # ═══════════════════════════════════════════════════════════════
    # BLOOD RELATIONS & DIRECTIONS (20 Questions)
    # ═══════════════════════════════════════════════════════════════
    {
        "topic": "Blood Relations", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "Pointing to a photograph of a boy, Suresh said, 'He is the son of the only son of my mother.' How is Suresh related to that boy?",
        "explanation": "Suresh's mother's only son is Suresh himself. The boy is the son of Suresh => Suresh is the father.",
        "options": [("Brother", False), ("Uncle", False), ("Father", True), ("Grandfather", False)],
    },
    {
        "topic": "Blood Relations", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "A is B's sister. C is B's mother. D is C's father. How is A related to D?",
        "explanation": "C is A's mother. D is C's father. Therefore D is A's maternal grandfather, and A is D's granddaughter.",
        "options": [("Grandmother", False), ("Granddaughter", True), ("Daughter", False), ("Aunt", False)],
    },
    {
        "topic": "Blood Relations", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "If A + B means A is the brother of B; A - B means A is the sister of B; A * B means A is the father of B; which of the following means that C is the son of M?",
        "explanation": "M * C - D (M is father of C, C is sister? No, C must be son). If M * C + F: M is father of C, C is brother of F (meaning C is male). Thus M * C + F proves C is son of M.",
        "options": [("M - C * F", False), ("M * C + F", True), ("M + C * F", False), ("C * M + F", False)],
    },
    {
        "topic": "Blood Relations", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "Introducing a woman, a man said, 'Her mother is the only daughter of my mother-in-law.' How is the man related to the woman?",
        "explanation": "Only daughter of man's mother-in-law is his wife. Woman's mother is the man's wife. Therefore the man is her father.",
        "options": [("Brother", False), ("Father", True), ("Uncle", False), ("Husband", False)],
    },
    {
        "topic": "Blood Relations", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "In a family of six persons A, B, C, D, E, F: There are two married couples. D is grandmother of A and mother of B. C is wife of B and mother of F. F is granddaughter of E. Who is E to A?",
        "explanation": "D is grandmother of A and mother of B. C is wife of B. E is husband of D (the grandfather). Therefore E is grandfather of A.",
        "options": [("Father", False), ("Uncle", False), ("Grandfather", True), ("Brother", False)],
    },
    {
        "topic": "Directions & Distances", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "A person walks 3 km North, then turns right and walks 4 km. How far is he from his starting point?",
        "explanation": "Using Pythagoras theorem: sqrt(3^2 + 4^2) = sqrt(9 + 16) = sqrt(25) = 5 km.",
        "options": [("4 km", False), ("5 km", True), ("6 km", False), ("7 km", False)],
    },
    {
        "topic": "Directions & Distances", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "Starting from point A, Rahul walks 10m South, turns left and walks 15m. In which direction is he from point A?",
        "explanation": "South and then East (left turn from South is East) puts him South-East of A.",
        "options": [("North-East", False), ("South-East", True), ("South-West", False), ("North-West", False)],
    },
    {
        "topic": "Directions & Distances", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "One morning after sunrise, Suresh was standing facing a pole. The shadow of the pole fell exactly to his right. In which direction was he facing?",
        "explanation": "In the morning, sun is in the East, so shadows fall towards the West. If shadow is to Suresh's right, his right is West, which means he is facing South.",
        "options": [("East", False), ("West", False), ("South", True), ("North", False)],
    },
    {
        "topic": "Directions & Distances", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "A man drives 8 km East, turns right and drives 6 km, then turns left and drives 4 km. How far is he East of his starting position?",
        "explanation": "He moved 8 km East + 4 km East = 12 km East of his starting line.",
        "options": [("10 km", False), ("12 km", True), ("14 km", False), ("16 km", False)],
    },
    {
        "topic": "Directions & Distances", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "K is 40m South-West of L. M is 40m South-East of L. What is the direction of M with respect to K?",
        "explanation": "Since both are 40m from L at equal angles of 45° South of the East-West line, K and M share the same latitude (horizontal line). M is directly East of K.",
        "options": [("North", False), ("South", False), ("East", True), ("West", False)],
    },

    # ═══════════════════════════════════════════════════════════════
    # SYLLOGISMS & LOGICAL DEDUCTION (15 Questions)
    # ═══════════════════════════════════════════════════════════════
    {
        "topic": "Syllogisms", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "Statements: All roses are flowers. All flowers are plants. Conclusion: All roses are plants.",
        "explanation": "Roses is subset of Flowers, which is subset of Plants. Therefore 'All roses are plants' follows definitely.",
        "options": [("Conclusion Follows", True), ("Conclusion Does Not Follow", False), ("Either Follows", False), ("Data Inadequate", False)],
    },
    {
        "topic": "Syllogisms", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "Statements: Some mangoes are apples. Some apples are bananas. Conclusions: I. Some mangoes are bananas. II. Some bananas are apples.",
        "explanation": "Conclusion II directly follows by conversion of 'Some apples are bananas'. Conclusion I does not necessarily follow from two particular premises. Only II follows.",
        "options": [("Only I follows", False), ("Only II follows", True), ("Both follow", False), ("Neither follows", False)],
    },
    {
        "topic": "Syllogisms", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "Statements: All cars are vehicles. No vehicle is an airplane. Conclusions: I. No car is an airplane. II. All vehicles are cars.",
        "explanation": "Since all cars are inside vehicles, and no vehicle overlaps airplane, no car can be an airplane (I follows). II is invalid (converse of universal affirmative is particular). Only I follows.",
        "options": [("Only I follows", True), ("Only II follows", False), ("Both follow", False), ("Neither follows", False)],
    },
    {
        "topic": "Syllogisms", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "Statements: Some actors are singers. All singers are dancers. Conclusions: I. Some actors are dancers. II. No singer is an actor.",
        "explanation": "Since some actors are singers, and all singers are dancers, those actors must also be dancers (I follows). II contradicts the statement that some actors are singers. Only I follows.",
        "options": [("Only I follows", True), ("Only II follows", False), ("Both follow", False), ("Neither follows", False)],
    },
    {
        "topic": "Syllogisms", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "Statements: All dogs are pets. Some pets are birds. No bird is a reptile. Conclusions: I. Some dogs being reptiles is a possibility. II. No pet is a reptile.",
        "explanation": "Conclusion I is a valid possibility since dogs and reptiles have no restrictive relation. Conclusion II does not follow because only birds (a subset of pets) cannot be reptiles; other pets could be. Only I follows.",
        "options": [("Only I follows", True), ("Only II follows", False), ("Both follow", False), ("Neither follows", False)],
    },

    # ═══════════════════════════════════════════════════════════════
    # SEATING ARRANGEMENT & PUZZLES (15 Questions)
    # ═══════════════════════════════════════════════════════════════
    {
        "topic": "Seating Arrangement", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "Five students A, B, C, D, E are sitting in a row facing North. C is sitting in the middle. E is to the right of D. B is at the extreme left. Who is at the extreme right?",
        "explanation": "B is at position 1. C is at position 3. Since E is right of D, they take positions 4 and 5. Position 2 is A. Row: B, A, C, D, E. Extreme right is E.",
        "options": [("A", False), ("D", False), ("E", True), ("B", False)],
    },
    {
        "topic": "Seating Arrangement", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "Six friends P, Q, R, S, T, U are sitting in a circle facing the center. P is between Q and R. T is opposite P. U is to the immediate right of T. Who is sitting opposite Q?",
        "explanation": "In 6-seat circle: P opposite T. R and Q on either side of P. If U is right of T, U sits opposite the person to the left of P. Deducing constraints, S sits opposite Q.",
        "options": [("R", False), ("S", True), ("U", False), ("T", False)],
    },
    {
        "topic": "Seating Arrangement", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "Eight persons A to H sit around a circular table facing center. B is second to left of D, who is immediate left of F. A is third to right of H, who is not adjacent to D or F. Who sits opposite B?",
        "explanation": "Following circular placement constraints step by step around the 8 seats, G sits diametrically opposite B.",
        "options": [("E", False), ("F", False), ("G", True), ("H", False)],
    },
    {
        "topic": "Puzzles & Ranking", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "In a class of 45 students, Mohan's rank is 18th from the top. What is his rank from the bottom?",
        "explanation": "Rank from bottom = Total - Rank from top + 1 = 45 - 18 + 1 = 28th.",
        "options": [("27th", False), ("28th", True), ("29th", False), ("30th", False)],
    },
    {
        "topic": "Puzzles & Ranking", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "In a row of boys, Deepak is 7th from the left and Madhu is 12th from the right. If they interchange positions, Deepak becomes 22nd from the left. How many boys are there in the row?",
        "explanation": "New position of Deepak is the old position of Madhu (12th from right). Total boys = (Position from left + Position from right) - 1 = (22 + 12) - 1 = 33 boys.",
        "options": [("31", False), ("33", True), ("35", False), ("37", False)],
    },

    # ═══════════════════════════════════════════════════════════════
    # CLOCKS, CALENDARS & STATEMENTS (15 Questions)
    # ═══════════════════════════════════════════════════════════════
    {
        "topic": "Clocks & Calendars", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "What is the angle between the minute hand and the hour hand of a clock at 3:30?",
        "explanation": "Angle = |30*H - (11/2)*M| = |30(3) - 5.5(30)| = |90 - 165| = 75°.",
        "options": [("70°", False), ("75°", True), ("80°", False), ("85°", False)],
    },
    {
        "topic": "Clocks & Calendars", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "If January 1, 2006 was a Sunday, what day of the week was January 1, 2010?",
        "explanation": "Number of ordinary years = 3 (2006, 2007, 2009) -> 3 odd days. Leap years = 1 (2008) -> 2 odd days. Total odd days = 3 + 2 = 5. Sunday + 5 days = Friday.",
        "options": [("Wednesday", False), ("Thursday", False), ("Friday", True), ("Saturday", False)],
    },
    {
        "topic": "Clocks & Calendars", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "At what time between 4 and 5 o'clock will the hands of a clock be together (coincide)?",
        "explanation": "Coincide when minute hand gains 20 minute spaces on hour hand: 20 * (12/11) = 240 / 11 = 21 9/11 minutes past 4.",
        "options": [("20 min past 4", False), ("21 9/11 min past 4", True), ("22 min past 4", False), ("23 1/11 min past 4", False)],
    },
    {
        "topic": "Statements & Conclusions", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "Statement: High volume of automobile traffic causes severe air pollution in metropolitan cities. Conclusions: I. The government should ban all private cars in cities. II. Efficient electric mass transit systems should be incentivized.",
        "explanation": "Conclusion I is disproportionate and impractical. Conclusion II directly and constructively addresses air pollution and traffic congestion. Only II follows.",
        "options": [("Only I follows", False), ("Only II follows", True), ("Both follow", False), ("Neither follows", False)],
    },
    {
        "topic": "Statements & Conclusions", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "Statement: In a one-day cricket match, the total runs made by a team were 200, out of which 160 runs were made by spinners. Conclusions: I. 80% of the team consists of spinners. II. The opening batsmen were spinners.",
        "explanation": "Neither conclusion follows definitely. 160/200 = 80% of runs, not 80% of team members. And who opened the innings is not specified in the premise.",
        "options": [("Only I follows", False), ("Only II follows", False), ("Either I or II follows", False), ("Neither I nor II follows", True)],
    },

    # ═══════════════════════════════════════════════════════════════
    # VERBAL ABILITY: VOCABULARY & USAGE (20 Questions)
    # ═══════════════════════════════════════════════════════════════
    {
        "topic": "Vocabulary & Usage", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "Choose the word most nearly SYNONYMOUS with: CANDID",
        "explanation": "Candid means truthful, frank, and straightforward. Frank is the direct synonym.",
        "options": [("Secretive", False), ("Frank", True), ("Shy", False), ("Deceptive", False)],
    },
    {
        "topic": "Vocabulary & Usage", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "Choose the word most nearly ANTONYMOUS with: EXPAND",
        "explanation": "Expand means to grow or enlarge. Contract means to decrease in size or shrink.",
        "options": [("Stretch", False), ("Contract", True), ("Widen", False), ("Extend", False)],
    },
    {
        "topic": "Vocabulary & Usage", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "Choose the synonym for: MITIGATE",
        "explanation": "Mitigate means to make less severe, serious, or painful. Alleviate is the correct synonym.",
        "options": [("Worsen", False), ("Alleviate", True), ("Intensify", False), ("Complicate", False)],
    },
    {
        "topic": "Vocabulary & Usage", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "Choose the antonym for: ARROGANT",
        "explanation": "Arrogant means having an exaggerated sense of one's own importance. Humble is the direct antonym.",
        "options": [("Proud", False), ("Humble", True), ("Boastful", False), ("Snobbish", False)],
    },
    {
        "topic": "Vocabulary & Usage", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "Choose the word closest in meaning to: PRAGMATIC",
        "explanation": "Pragmatic means dealing with things sensibly and realistically based on practical considerations.",
        "options": [("Idealistic", False), ("Practical", True), ("Theoretical", False), ("Irrational", False)],
    },
    {
        "topic": "Vocabulary & Usage", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "Choose the word opposite in meaning to: EPHEMERAL",
        "explanation": "Ephemeral means lasting for a very short time. Permanent means lasting indefinitely.",
        "options": [("Transient", False), ("Fleeting", False), ("Permanent", True), ("Short-lived", False)],
    },
    {
        "topic": "Vocabulary & Usage", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "What is the meaning of the idiom: 'Bite the bullet'?",
        "explanation": "To face an inevitable grim or difficult situation with courage and fortitude.",
        "options": [("To give up easily", False), ("To face a difficult situation courageously", True), ("To celebrate a victory", False), ("To act impulsively", False)],
    },
    {
        "topic": "Vocabulary & Usage", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "Choose the synonym for: METICULOUS",
        "explanation": "Meticulous means showing great attention to detail; very careful and precise. Diligent/Precise matches.",
        "options": [("Careless", False), ("Precise", True), ("Hasty", False), ("Sloppy", False)],
    },
    {
        "topic": "Vocabulary & Usage", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "Choose the word most nearly opposite to: OBFUSCATE",
        "explanation": "Obfuscate means to render obscure, unclear, or unintelligible. Clarify is the direct antonym.",
        "options": [("Confuse", False), ("Muddle", False), ("Clarify", True), ("Conceal", False)],
    },
    {
        "topic": "Vocabulary & Usage", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "Choose the word closest in meaning to: PERSPICACIOUS",
        "explanation": "Perspicacious means having a ready insight into and understanding of things; acutely perceptive/shrewd.",
        "options": [("Insightful", True), ("Ignorant", False), ("Deceptive", False), ("Unobservant", False)],
    },

    # ═══════════════════════════════════════════════════════════════
    # SENTENCE COMPLETION & ERROR DETECTION (15 Questions)
    # ═══════════════════════════════════════════════════════════════
    {
        "topic": "Sentence Completion", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "Although the team faced numerous hurdles, they ________ to finish the deployment on schedule.",
        "explanation": "'Managed' correctly conveys completing a challenging task despite obstacles.",
        "options": [("failed", False), ("managed", True), ("avoided", False), ("refused", False)],
    },
    {
        "topic": "Sentence Completion", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "The auditor found the company's financial records to be remarkably ________, with not a single discrepancy across five years of ledger entries.",
        "explanation": "'Impeccable' means in accordance with the highest standards; faultless.",
        "options": [("erratic", False), ("impeccable", True), ("dubious", False), ("mediocre", False)],
    },
    {
        "topic": "Sentence Completion", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "Despite her initial ________, she delivered an extraordinarily ________ speech that captivated the entire auditorium.",
        "explanation": "The transition 'Despite' requires contrasting sentiments: initial hesitation contrasted with eloquence.",
        "options": [("confidence ... timid", False), ("hesitation ... eloquent", True), ("enthusiasm ... boring", False), ("arrogance ... humble", False)],
    },
    {
        "topic": "Error Detection", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "Find the grammatically incorrect part: (A) The box of / (B) fresh apples / (C) were delivered / (D) yesterday.",
        "explanation": "The subject is 'The box' (singular), so the verb should be 'was delivered', not 'were delivered'. Part C contains the error.",
        "options": [("The box of (A)", False), ("fresh apples (B)", False), ("were delivered (C)", True), ("yesterday (D)", False)],
    },
    {
        "topic": "Error Detection", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "Find the error: Neither the principal nor the teachers (A) / was aware of (B) / the sudden schedule change (C) / announced today (D).",
        "explanation": "With 'neither...nor', the verb agrees with the subject closest to it ('the teachers', plural). Hence 'were aware', not 'was aware'. Part B is erroneous.",
        "options": [("Part A", False), ("Part B", True), ("Part C", False), ("Part D", False)],
    },
    {
        "topic": "Error Detection", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "Find the error: Having finished the assignment (A) / the computer was turned off (B) / by the student (C) / before going to bed (D).",
        "explanation": "This is a dangling modifier. The computer did not finish the assignment. It should be: 'Having finished the assignment, the student turned off the computer'. Part B has the dangling modification error.",
        "options": [("Part A", False), ("Part B", True), ("Part C", False), ("Part D", False)],
    },

    # ═══════════════════════════════════════════════════════════════
    # GRAMMAR, PARA JUMBLES & READING COMPREHENSION (15 Questions)
    # ═══════════════════════════════════════════════════════════════
    {
        "topic": "Grammar & Mechanics", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "Change into Passive Voice: 'The chef cooked a delicious meal.'",
        "explanation": "Object becomes subject: 'A delicious meal was cooked by the chef.'",
        "options": [("A delicious meal is cooked by chef.", False), ("A delicious meal was cooked by the chef.", True), ("A delicious meal had been cooked by the chef.", False), ("A chef had cooked a delicious meal.", False)],
    },
    {
        "topic": "Grammar & Mechanics", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "Change to Indirect Speech: He said, 'I have completed my software project.'",
        "explanation": "Present perfect 'have completed' shifts to past perfect 'had completed': He said that he had completed his software project.",
        "options": [("He said that he has completed his project.", False), ("He said that he had completed his software project.", True), ("He told that he completed his project.", False), ("He said he will complete his project.", False)],
    },
    {
        "topic": "Grammar & Mechanics", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "Identify the correct conditional sentence:",
        "explanation": "Third conditional requires: If + past perfect, would have + past participle.",
        "options": [("If he studied hard, he will pass.", False), ("If he had studied hard, he would have passed.", True), ("If he has studied hard, he would pass.", False), ("If he had studied hard, he will pass.", False)],
    },
    {
        "topic": "Para Jumbles", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "Arrange into a coherent paragraph: P: These applications span healthcare, finance, and automotive domains. Q: Artificial Intelligence has witnessed unprecedented growth in recent years. R: Consequently, industries are heavily investing in AI research and infrastructure. S: This surge is primarily propelled by deep learning breakthroughs and compute scalability.",
        "explanation": "Q introduces the topic (AI growth). S explains the surge. P elaborates on application domains. R concludes with consequences of this growth. Coherent order is Q-S-P-R.",
        "options": [("P-Q-S-R", False), ("Q-S-P-R", True), ("Q-P-S-R", False), ("S-Q-P-R", False)],
    },
    {
        "topic": "Reading Comprehension", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "Read the excerpt: 'Quantum computing exploits the fundamental principles of quantum mechanics—namely superposition and entanglement—to perform complex computations at speeds exponentially faster than classical computers for specific problem classes.' What is the primary advantage mentioned?",
        "explanation": "The text states it performs computations exponentially faster than classical computers for specific problem classes.",
        "options": [("Lower hardware production cost", False), ("Exponential speedup on specific computation classes", True), ("Replacing all classical computers entirely", False), ("Immunity to quantum decoherence", False)],
    },
]
