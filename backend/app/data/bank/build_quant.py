"""
Builder for Quantitative Aptitude Questions.
Generates 45+ unique, high-quality questions for each of the 12 Quant topics:
- Percentages
- Profit & Loss
- Ratio & Proportion
- Averages
- Simple & Compound Interest
- Time & Work
- Speed, Distance & Time
- Number System
- Permutation & Combination
- Probability
- Data Interpretation
- Ages & Mixtures
"""
import json
import math

def make_q(topic, diff, irt, text, correct, wrongs, expl):
    opts = [(str(correct), True)] + [(str(w), False) for w in wrongs[:3]]
    # Ensure options are distinct
    seen = set()
    cleaned_opts = []
    for val, is_c in opts:
        if val not in seen:
            seen.add(val)
            cleaned_opts.append((val, is_c))
    while len(cleaned_opts) < 4:
        dummy = f"{float(correct) + len(cleaned_opts) * 2:.1f}" if isinstance(correct, (int, float)) else f"Option {len(cleaned_opts)}"
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

def generate_quant_questions():
    questions = []

    # ═══════════════════════════════════════════════════════════════
    # 1. NUMBER SYSTEM (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Number System"
    # Easy (15)
    for a, b in [(12, 18), (15, 25), (14, 21), (24, 36), (16, 24), (20, 30), (28, 42), (18, 27), (35, 49), (32, 48), (45, 60), (40, 50), (25, 35), (22, 33), (50, 75)]:
        g = math.gcd(a, b)
        l = (a * b) // g
        questions.append(make_q(
            topic, "EASY", -1.2,
            f"What is the Highest Common Factor (HCF) of {a} and {b}?",
            g, [g + 2, max(1, g - 1), g * 2],
            f"Prime factorization: {a} and {b}. The greatest common divisor is {g}."
        ))
        questions.append(make_q(
            topic, "EASY", -1.1,
            f"What is the Least Common Multiple (LCM) of {a} and {b}?",
            l, [l + a, l - g, l * 2],
            f"LCM({a}, {b}) = ({a} * {b}) / HCF = {l}."
        ))

    # Divisibility and unit digits (Medium, 15)
    for n, p in [(2, 35), (3, 42), (7, 65), (8, 93), (4, 51), (9, 27), (6, 44), (5, 83), (7, 39), (3, 55), (8, 47), (2, 79), (7, 101), (3, 89), (9, 45)]:
        cycles = {2: [2, 4, 8, 6], 3: [3, 9, 7, 1], 4: [4, 6], 5: [5], 6: [6], 7: [7, 9, 3, 1], 8: [8, 4, 2, 6], 9: [9, 1]}
        cyc = cycles[n]
        u = cyc[(p - 1) % len(cyc)]
        wrongs = [x for x in [1, 2, 3, 4, 6, 7, 8, 9] if x != u]
        questions.append(make_q(
            topic, "MEDIUM", 0.0,
            f"Find the unit digit of the expression ({n})^{{{p}}}.",
            u, wrongs[:3],
            f"The unit digit cycle of {n} has length {len(cyc)}: {cyc}. Since {p} mod {len(cyc)} corresponds to index {(p - 1) % len(cyc)}, unit digit is {u}."
        ))

    # Hard: Remainders & Factors (15)
    for div, num in [(7, 342), (9, 785), (11, 1452), (13, 529), (17, 853), (19, 400), (23, 560), (29, 900), (31, 1000), (37, 1150), (11, 2589), (13, 1695), (7, 2401), (17, 1024), (23, 729)]:
        rem = num % div
        questions.append(make_q(
            topic, "HARD", 1.2,
            f"What is the remainder when {num} is divided by {div}?",
            rem, [(rem + 1) % div, (rem + 2) % div, (rem + 3) % div],
            f"Dividing {num} by {div} gives quotient {num // div} and remainder {rem}."
        ))

    # ═══════════════════════════════════════════════════════════════
    # 2. PERCENTAGES (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Percentages"
    # Easy (15)
    for val, pct in [(250, 20), (400, 15), (500, 30), (600, 25), (800, 12), (150, 40), (350, 10), (450, 20), (750, 16), (900, 35), (1200, 15), (850, 10), (640, 25), (550, 20), (320, 50)]:
        ans = (val * pct) // 100
        questions.append(make_q(
            topic, "EASY", -1.2,
            f"What is {pct}% of {val}?",
            ans, [ans + 10, max(5, ans - 15), ans + 25],
            f"{pct}% of {val} = ({pct}/100) * {val} = {ans}."
        ))

    # Medium: Successive percentage & expenditure (15)
    for p1, p2 in [(20, 10), (25, 20), (30, 20), (10, 10), (20, 20), (15, 10), (25, 10), (40, 20), (50, 20), (30, 10), (20, 5), (15, 15), (25, 25), (35, 10), (40, 10)]:
        net = p1 + p2 + (p1 * p2) / 100
        questions.append(make_q(
            topic, "MEDIUM", 0.1,
            f"If the price of an article increases successively by {p1}% and then by {p2}%, what is the net percentage increase?",
            f"{net:.1f}%", [f"{net - 3:.1f}%", f"{net + 2:.1f}%", f"{p1 + p2:.1f}%"],
            f"Net change = [a + b + (ab/100)]% = {p1} + {p2} + ({p1 * p2}/100) = {net:.1f}%."
        ))

    # Hard: Population and election problems (15)
    for pop, rate, yrs in [(10000, 10, 2), (20000, 5, 2), (50000, 4, 2), (12000, 10, 2), (80000, 5, 2), (25000, 8, 2), (40000, 10, 2), (60000, 5, 2), (15000, 20, 2), (30000, 10, 2), (50000, 10, 2), (75000, 4, 2), (100000, 5, 2), (16000, 25, 2), (45000, 10, 2)]:
        final_pop = int(pop * ((1 + rate / 100) ** yrs))
        questions.append(make_q(
            topic, "HARD", 1.1,
            f"The population of a town is {pop}. If it grows at an annual rate of {rate}%, what will be the population after {yrs} years?",
            final_pop, [final_pop - 200, final_pop + 350, final_pop + 500],
            f"Population after {yrs} years = P * (1 + R/100)^{yrs} = {pop} * (1 + {rate}/100)^{yrs} = {final_pop}."
        ))

    # ═══════════════════════════════════════════════════════════════
    # 3. PROFIT & LOSS (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Profit & Loss"
    # Easy (15)
    for cp, p_pct in [(200, 20), (300, 25), (400, 15), (500, 30), (600, 10), (700, 20), (800, 25), (900, 15), (1000, 12), (1200, 20), (1500, 10), (450, 20), (350, 30), (250, 40), (850, 10)]:
        sp = cp + (cp * p_pct) // 100
        questions.append(make_q(
            topic, "EASY", -1.1,
            f"An item with cost price ${cp} is sold at a profit of {p_pct}%. What is its selling price?",
            f"${sp}", [f"${sp - 20}", f"${sp + 25}", f"${sp + 40}"],
            f"SP = CP * (1 + Profit%/100) = {cp} * (1 + {p_pct}/100) = ${sp}."
        ))

    # Medium: Discounts on Marked Price (15)
    for mp, d1, d2 in [(1000, 20, 10), (2000, 25, 10), (1500, 20, 20), (800, 10, 10), (1200, 15, 10), (2500, 20, 5), (3000, 30, 10), (1800, 20, 15), (4000, 25, 20), (1600, 25, 10), (2200, 10, 5), (1400, 20, 10), (3500, 20, 10), (5000, 30, 20), (2800, 15, 10)]:
        eff_d = d1 + d2 - (d1 * d2) / 100
        sp = round(mp * (1 - eff_d / 100))
        questions.append(make_q(
            topic, "MEDIUM", 0.2,
            f"A retailer offers successive discounts of {d1}% and {d2}% on a marked price of ${mp}. What is the final selling price?",
            f"${sp}", [f"${sp + 30}", f"${sp - 40}", f"${sp + 60}"],
            f"Single equivalent discount = {d1} + {d2} - ({d1}*{d2}/100) = {eff_d:.1f}%. Final SP = ${mp} * (1 - {eff_d:.1f}/100) = ${sp}."
        ))

    # Hard: Dishonest dealer & false weights (15)
    for true_w, false_w in [(1000, 900), (1000, 800), (1000, 950), (1000, 850), (1000, 750), (500, 450), (500, 400), (1000, 920), (1000, 880), (1000, 960), (1000, 840), (500, 480), (1000, 910), (1000, 820), (1000, 780)]:
        gain = round(((true_w - false_w) / false_w) * 100, 2)
        questions.append(make_q(
            topic, "HARD", 1.2,
            f"A dishonest shopkeeper professes to sell goods at cost price, but uses a false weight of {false_w}g for {true_w}g. What is his gain percentage?",
            f"{gain}%", [f"{gain - 1.5:.2f}%", f"{gain + 2.0:.2f}%", f"{round(100 - (false_w/true_w)*100, 2)}%"],
            f"Gain% = [Error / False Weight] * 100 = [({true_w} - {false_w}) / {false_w}] * 100 = {gain}%."
        ))

    # ═══════════════════════════════════════════════════════════════
    # 4. TIME & WORK (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Time & Work"
    # Easy: Two person joint work (15)
    for a, b in [(10, 15), (12, 24), (20, 30), (15, 30), (12, 18), (14, 28), (16, 48), (20, 60), (25, 50), (18, 36), (15, 60), (24, 48), (30, 60), (12, 60), (10, 40)]:
        lcm = (a * b) // math.gcd(a, b)
        eff_a = lcm // a
        eff_b = lcm // b
        days = round(lcm / (eff_a + eff_b), 1)
        questions.append(make_q(
            topic, "EASY", -1.0,
            f"A can finish a task in {a} days and B can finish the same task in {b} days. How many days will they take working together?",
            f"{days} days", [f"{days + 2} days", f"{max(1, days - 1.5)} days", f"{round((a + b) / 2, 1)} days"],
            f"1 day work = 1/{a} + 1/{b} = ({eff_a} + {eff_b})/{lcm} = {eff_a + eff_b}/{lcm}. Total days = {lcm}/{eff_a + eff_b} = {days} days."
        ))

    # Medium: Three workers & wages (15)
    for a, b, c in [(10, 12, 15), (12, 15, 20), (15, 20, 30), (12, 18, 36), (20, 30, 60), (10, 15, 30), (15, 25, 75), (8, 12, 24), (12, 16, 48), (14, 21, 42), (16, 24, 48), (18, 36, 72), (10, 20, 30), (15, 30, 45), (12, 24, 36)]:
        g1 = math.gcd(a, b)
        l1 = (a * b) // g1
        g2 = math.gcd(l1, c)
        lcm = (l1 * c) // g2
        eff_tot = (lcm // a) + (lcm // b) + (lcm // c)
        days = round(lcm / eff_tot, 2)
        questions.append(make_q(
            topic, "MEDIUM", 0.2,
            f"A, B, and C can complete a project in {a}, {b}, and {c} days respectively. If they all work together, how long will it take?",
            f"{days} days", [f"{days + 1.2:.2f} days", f"{max(1, days - 0.8):.2f} days", f"{round((a+b+c)/3, 2)} days"],
            f"Combined 1-day work = 1/{a} + 1/{b} + 1/{c}. Total work = LCM({a},{b},{c}) = {lcm} units. Total days = {lcm}/{eff_tot} = {days} days."
        ))

    # Hard: Pipes and cisterns with leaks (15)
    for p, leak in [(6, 12), (8, 16), (10, 15), (12, 18), (15, 20), (6, 9), (8, 12), (10, 20), (12, 24), (14, 21), (15, 30), (16, 24), (18, 36), (20, 30), (9, 18)]:
        lcm = (p * leak) // math.gcd(p, leak)
        net_rate = (lcm // p) - (lcm // leak)
        time_to_fill = lcm // net_rate
        questions.append(make_q(
            topic, "HARD", 1.2,
            f"An inlet pipe can fill a reservoir in {p} hours, but due to a leak at the bottom it takes longer. The leak alone can empty the full reservoir in {leak} hours. How many hours will it take to fill the reservoir with the leak open?",
            f"{time_to_fill} hours", [f"{time_to_fill + 3} hours", f"{max(1, time_to_fill - 4)} hours", f"{p + leak} hours"],
            f"Inlet rate = 1/{p}, Leak rate = -1/{leak}. Net rate = 1/{p} - 1/{leak} = ({lcm // p} - {lcm // leak})/{lcm} = {net_rate}/{lcm}. Time = {lcm}/{net_rate} = {time_to_fill} hours."
        ))

    # ═══════════════════════════════════════════════════════════════
    # 5. SPEED, DISTANCE & TIME (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Speed, Distance & Time"
    # Easy: Basic km/h and average speed (15)
    for s1, s2 in [(40, 60), (30, 60), (20, 30), (50, 75), (60, 90), (45, 90), (36, 54), (48, 72), (24, 36), (40, 80), (50, 100), (30, 45), (45, 60), (60, 120), (35, 70)]:
        avg = round((2 * s1 * s2) / (s1 + s2), 1)
        questions.append(make_q(
            topic, "EASY", -1.0,
            f"A commuter drives from city A to B at {s1} km/h and returns along the same route at {s2} km/h. What is the average speed for the round trip?",
            f"{avg} km/h", [f"{(s1 + s2) / 2:.1f} km/h", f"{avg - 3.5:.1f} km/h", f"{avg + 4.0:.1f} km/h"],
            f"Average speed for equal distances = 2xy / (x + y) = (2 * {s1} * {s2}) / ({s1} + {s2}) = {avg} km/h."
        ))

    # Medium: Trains passing platforms (15)
    for t_len, p_len, speed_kmh in [(150, 250, 72), (180, 220, 54), (200, 300, 90), (120, 180, 72), (250, 350, 108), (140, 260, 72), (160, 240, 90), (220, 280, 54), (300, 200, 72), (150, 150, 54), (180, 320, 90), (210, 290, 72), (100, 200, 54), (240, 360, 108), (280, 220, 90)]:
        speed_ms = speed_kmh * (5 / 18)
        tot_dist = t_len + p_len
        time_sec = round(tot_dist / speed_ms, 1)
        questions.append(make_q(
            topic, "MEDIUM", 0.2,
            f"A train {t_len} meters long travels at {speed_kmh} km/h. How many seconds does it take to cross a platform of length {p_len} meters?",
            f"{time_sec} s", [f"{time_sec + 4:.1f} s", f"{max(1, time_sec - 3):.1f} s", f"{round(t_len / speed_ms, 1)} s"],
            f"Speed in m/s = {speed_kmh} * (5/18) = {speed_ms:.1f} m/s. Total distance = {t_len} + {p_len} = {tot_dist}m. Time = {tot_dist} / {speed_ms:.1f} = {time_sec} seconds."
        ))

    # Hard: Boats and streams (15)
    for b_speed, s_speed in [(12, 3), (15, 5), (18, 6), (20, 4), (16, 4), (14, 2), (24, 6), (15, 3), (21, 7), (18, 3), (25, 5), (10, 2), (22, 4), (16, 2), (28, 7)]:
        down = b_speed + s_speed
        up = b_speed - s_speed
        dist = down * 2
        time_up = round(dist / up, 1)
        questions.append(make_q(
            topic, "HARD", 1.2,
            f"A boat's speed in still water is {b_speed} km/h and stream speed is {s_speed} km/h. If it travels {dist} km upstream, how many hours does it take?",
            f"{time_up} hrs", [f"{time_up + 1.5:.1f} hrs", f"{round(dist / down, 1)} hrs", f"{time_up - 1.0:.1f} hrs"],
            f"Upstream speed = Boat - Stream = {b_speed} - {s_speed} = {up} km/h. Time = Distance / Speed = {dist} / {up} = {time_up} hours."
        ))

    # ═══════════════════════════════════════════════════════════════
    # 6. PERMUTATION & COMBINATION (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Permutation & Combination"
    # Easy: nPr and nCr basics (15)
    for n, r in [(5, 2), (6, 2), (7, 2), (8, 2), (5, 3), (6, 3), (7, 3), (8, 3), (9, 2), (10, 2), (6, 4), (7, 4), (8, 4), (9, 3), (10, 3)]:
        ncr = math.comb(n, r)
        npr = math.perm(n, r)
        questions.append(make_q(
            topic, "EASY", -1.0,
            f"In how many different ways can a committee of {r} members be chosen from a group of {n} candidates?",
            ncr, [ncr + 5, max(1, ncr - 4), npr],
            f"Selection where order does not matter is a combination: {n}C{r} = {n}! / ({r}! * ({n}-{r})!) = {ncr}."
        ))

    # Medium: Word arrangements with and without repetition (15)
    words = [("LEADER", 6, [("E", 2)]), ("APPLE", 5, [("P", 2)]), ("BANANA", 6, [("A", 3), ("N", 2)]),
             ("COMMITTEE", 9, [("M", 2), ("T", 2), ("E", 2)]), ("SUCCESS", 7, [("S", 3), ("C", 2)]),
             ("MATHEMATICS", 11, [("M", 2), ("A", 2), ("T", 2)]), ("ENGINEERING", 11, [("E", 3), ("N", 3), ("G", 2), ("I", 2)]),
             ("COLLEGE", 7, [("L", 2), ("E", 2)]), ("INSTITUTE", 9, [("I", 2), ("T", 3)]),
             ("PROGRAM", 7, [("R", 2)]), ("PENCIL", 6, []), ("ORANGE", 6, []), ("STUDY", 5, []),
             ("FLOWER", 6, []), ("MASTER", 6, [])]
    for w, length, reps in words:
        tot = math.factorial(length)
        denom = 1
        for _, cnt in reps:
            denom *= math.factorial(cnt)
        ans = tot // denom
        questions.append(make_q(
            topic, "MEDIUM", 0.3,
            f"How many distinct words can be formed by rearranging the letters of the word '{w}'?",
            ans, [ans + 30, ans // 2, ans * 2],
            f"Total letters = {length}. Accounting for repeated letters, distinct arrangements = {length}! / ({' * '.join(f'{c}!' for _, c in reps) or '1'}) = {ans}."
        ))

    # Hard: Circular permutations & restricted arrangements (15)
    for n in range(4, 19):
        circ = math.factorial(n - 1)
        questions.append(make_q(
            topic, "HARD", 1.3,
            f"In how many ways can {n} executives be seated around a circular conference table?",
            circ, [circ * n, circ // 2, math.factorial(n)],
            f"Circular arrangements of n distinct items = (n - 1)! = ({n} - 1)! = {circ}."
        ))

    # ═══════════════════════════════════════════════════════════════
    # 7. PROBABILITY (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Probability"
    # Easy: Dice and coins (15)
    for target in range(2, 13):
        # 2 dice sum
        fav = sum(1 for i in range(1, 7) for j in range(1, 7) if i + j == target)
        g = math.gcd(fav, 36)
        prob_str = f"{fav // g}/{36 // g}"
        questions.append(make_q(
            topic, "EASY", -1.0,
            f"Two standard 6-sided dice are rolled simultaneously. What is the probability that the sum of the numbers is {target}?",
            prob_str, [f"{(fav + 1) // math.gcd(fav + 1, 36)}/{36 // math.gcd(fav + 1, 36)}", f"{max(1, fav - 1)}/36", "1/12"],
            f"Total outcomes = 6 * 6 = 36. Pairs giving sum {target} total {fav}. Probability = {fav}/36 = {prob_str}."
        ))
    for heads in range(1, 5):
        tot = 16
        fav = math.comb(4, heads)
        g = math.gcd(fav, tot)
        questions.append(make_q(
            topic, "EASY", -0.9,
            f"A fair coin is tossed 4 times. What is the probability of getting exactly {heads} heads?",
            f"{fav // g}/{tot // g}", ["1/2", "3/8", "1/4"],
            f"Total outcomes = 2^4 = 16. Favorable outcomes = 4C{heads} = {fav}. Probability = {fav}/16 = {fav // g}/{tot // g}."
        ))

    # Medium: Cards from a standard deck of 52 (15)
    card_scenarios = [
        ("drawing a King or a Queen", 8, "2/13"),
        ("drawing a spade", 13, "1/4"),
        ("drawing a red Ace", 2, "1/26"),
        ("drawing a face card (Jack, Queen, or King)", 12, "3/13"),
        ("drawing a diamond or a heart", 26, "1/2"),
        ("drawing an even-numbered card (2, 4, 6, 8, 10) of any suit", 20, "5/13"),
        ("drawing an Ace or a heart", 16, "4/13"),
        ("drawing a black King", 2, "1/26"),
        ("drawing a club face card", 3, "3/52"),
        ("drawing a card that is neither a spade nor a heart", 26, "1/2"),
        ("drawing a 7 or an 8", 8, "2/13"),
        ("drawing a red 10", 2, "1/26"),
        ("drawing a black card with a prime number (2, 3, 5, 7)", 8, "2/13"),
        ("drawing a non-face card", 40, "10/13"),
        ("drawing a picture card of hearts", 3, "3/52"),
    ]
    for desc, fav, ans in card_scenarios:
        questions.append(make_q(
            topic, "MEDIUM", 0.1,
            f"A card is drawn at random from a well-shuffled standard deck of 52 cards. What is the probability of {desc}?",
            ans, ["1/13", "1/2", "3/26"],
            f"Total cards = 52. Favorable outcomes for {desc} = {fav}. Probability = {fav}/52 = {ans}."
        ))

    # Hard: Urn / colored balls without replacement (15)
    for r, b, g in [(4, 5, 3), (3, 4, 5), (5, 3, 2), (6, 4, 2), (2, 3, 4), (4, 4, 4), (5, 5, 2), (3, 6, 3), (4, 6, 2), (2, 5, 5), (6, 3, 3), (4, 3, 5), (5, 4, 3), (3, 5, 4), (4, 5, 6)]:
        tot = r + b + g
        # Prob of drawing 2 red balls without replacement
        fav = r * (r - 1)
        denom = tot * (tot - 1)
        gcd_v = math.gcd(fav, denom)
        ans = f"{fav // gcd_v}/{denom // gcd_v}"
        questions.append(make_q(
            topic, "HARD", 1.2,
            f"A bag contains {r} red, {b} blue, and {g} green balls. If 2 balls are drawn at random without replacement, what is the probability that both are red?",
            ans, [f"{fav // gcd_v + 1}/{denom // gcd_v}", "1/6", f"{(r*b) // math.gcd(r*b, denom)}/{denom // math.gcd(r*b, denom)}"],
            f"P(Both red) = ({r}/{tot}) * ({r - 1}/{tot - 1}) = {fav}/{denom} = {ans}."
        ))

    # ═══════════════════════════════════════════════════════════════
    # 8. RATIO & PROPORTION (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Ratio & Proportion"
    # Easy: Ratio division (15)
    for tot, r1, r2 in [(600, 2, 3), (800, 3, 5), (900, 4, 5), (1000, 7, 3), (1200, 5, 7), (1500, 2, 3), (1400, 3, 4), (1600, 5, 3), (1800, 4, 5), (2000, 3, 7), (2100, 2, 5), (2400, 5, 3), (2500, 3, 2), (2700, 4, 5), (3000, 2, 3)]:
        share1 = (tot * r1) // (r1 + r2)
        share2 = tot - share1
        questions.append(make_q(
            topic, "EASY", -1.1,
            f"A sum of ${tot} is divided between Alice and Bob in the ratio {r1}:{r2}. What is Alice's share?",
            f"${share1}", [f"${share2}", f"${share1 + 50}", f"${share1 - 40}"],
            f"Alice's share = {r1}/({r1} + {r2}) * ${tot} = ({r1}/{r1+r2}) * ${tot} = ${share1}."
        ))

    # Medium: Combining ratios A:B and B:C (15)
    for a, b, c, d in [(2, 3, 4, 5), (3, 4, 5, 6), (1, 2, 3, 4), (2, 5, 3, 4), (4, 5, 2, 3), (3, 5, 2, 7), (1, 3, 2, 5), (3, 2, 4, 5), (5, 4, 3, 2), (2, 3, 5, 6), (4, 3, 2, 5), (3, 4, 2, 3), (5, 2, 3, 4), (1, 4, 3, 2), (2, 7, 3, 5)]:
        # A:B = a:b, B:C = c:d => A:B:C = (a*c) : (b*c) : (b*d)
        A = a * c
        B = b * c
        C = b * d
        g = math.gcd(A, math.gcd(B, C))
        ans = f"{A // g}:{B // g}:{C // g}"
        questions.append(make_q(
            topic, "MEDIUM", 0.1,
            f"If A:B = {a}:{b} and B:C = {c}:{d}, what is the combined ratio A:B:C?",
            ans, [f"{a}:{b}:{d}", f"{a*d}:{b*c}:{c*d}", f"{A//g + 1}:{B//g}:{C//g}"],
            f"Make B common: multiply first ratio by {c} and second ratio by {b}. A:B:C = ({a}*{c}) : ({b}*{c}) : ({b}*{d}) = {A}:{B}:{C} = {ans}."
        ))

    # Hard: Partnership with varying investments and times (15)
    for inv_a, time_a, inv_b, time_b, tot_profit in [(2000, 12, 3000, 8, 4800), (4000, 10, 5000, 6, 7000), (3000, 12, 6000, 6, 7200), (5000, 8, 4000, 12, 8800), (6000, 9, 8000, 6, 10200), (2500, 12, 5000, 6, 6000), (3500, 10, 7000, 5, 7000), (4500, 8, 3000, 12, 7200), (8000, 6, 6000, 8, 9600), (5000, 12, 10000, 6, 12000), (3000, 10, 4000, 5, 5000), (7000, 6, 6000, 7, 8400), (2000, 9, 3000, 6, 3600), (4000, 12, 8000, 6, 9600), (6000, 10, 5000, 12, 12000)]:
        w_a = inv_a * time_a
        w_b = inv_b * time_b
        profit_a = round((w_a / (w_a + w_b)) * tot_profit)
        questions.append(make_q(
            topic, "HARD", 1.2,
            f"A invests ${inv_a} for {time_a} months and B invests ${inv_b} for {time_b} months in a venture. If the total annual profit is ${tot_profit}, what is A's share?",
            f"${profit_a}", [f"${tot_profit - profit_a}", f"${profit_a + 200}", f"${profit_a - 150}"],
            f"Profit sharing ratio = (Capital_A * Time_A) : (Capital_B * Time_B) = ({inv_a} * {time_a}) : ({inv_b} * {time_b}) = {w_a} : {w_b}. A's share = ({w_a}/{w_a + w_b}) * ${tot_profit} = ${profit_a}."
        ))

    # ═══════════════════════════════════════════════════════════════
    # 9. AVERAGES (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Averages"
    # Easy (15)
    for n, avg, new_val in [(10, 50, 61), (12, 40, 53), (15, 60, 76), (8, 45, 54), (20, 30, 51), (14, 25, 40), (16, 35, 52), (18, 55, 74), (25, 60, 86), (30, 40, 71), (9, 20, 30), (11, 48, 60), (13, 32, 46), (17, 50, 68), (19, 42, 62)]:
        new_avg = round(((n * avg) + new_val) / (n + 1), 2)
        questions.append(make_q(
            topic, "EASY", -1.0,
            f"The average weight of {n} students is {avg} kg. If a new student weighing {new_val} kg joins the group, what is the new average weight?",
            f"{new_avg} kg", [f"{new_avg + 1.2:.2f} kg", f"{new_avg - 1.5:.2f} kg", f"{avg + 1:.2f} kg"],
            f"Total weight initially = {n} * {avg} = {n * avg} kg. New total = {n * avg} + {new_val} = {(n * avg) + new_val} kg. New average = {(n * avg) + new_val} / {n + 1} = {new_avg} kg."
        ))

    # Medium: Replacement problems (15)
    for n, inc, old_w in [(10, 2, 60), (12, 1.5, 55), (15, 2, 70), (8, 3, 50), (20, 1, 65), (14, 2, 58), (16, 1.5, 62), (18, 2, 72), (25, 1, 80), (30, 0.5, 75), (9, 2, 48), (11, 3, 54), (13, 2, 66), (17, 1, 70), (19, 2, 64)]:
        new_w = round(old_w + (n * inc))
        questions.append(make_q(
            topic, "MEDIUM", 0.1,
            f"The average weight of a group of {n} people increases by {inc} kg when a person weighing {old_w} kg is replaced by a new person. What is the weight of the new person?",
            f"{new_w} kg", [f"{new_w - 5} kg", f"{new_w + 6} kg", f"{old_w + inc} kg"],
            f"Change in total weight = n * increase = {n} * {inc} = {n * inc} kg. Weight of new person = Old weight + Total increase = {old_w} + {n * inc} = {new_w} kg."
        ))

    # Hard: Batting & Bowling averages (15)
    for inngs, avg, runs in [(10, 42, 86), (15, 36, 84), (12, 45, 97), (18, 50, 107), (20, 35, 77), (14, 40, 85), (16, 48, 99), (22, 52, 121), (25, 30, 82), (30, 45, 107), (8, 55, 91), (11, 38, 74), (13, 44, 96), (17, 46, 100), (19, 54, 114)]:
        new_avg = round(((inngs * avg) + runs) / (inngs + 1), 2)
        questions.append(make_q(
            topic, "HARD", 1.1,
            f"A cricketer has an average of {avg} runs in {inngs} innings. In his next innings, he scores {runs} runs. What is his new batting average?",
            f"{new_avg}", [f"{new_avg + 2.5:.2f}", f"{new_avg - 1.8:.2f}", f"{avg + 3:.2f}"],
            f"Total runs = ({inngs} * {avg}) + {runs} = {(inngs * avg) + runs}. New average = {(inngs * avg) + runs} / {inngs + 1} = {new_avg}."
        ))

    # ═══════════════════════════════════════════════════════════════
    # 10. SIMPLE & COMPOUND INTEREST (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Simple & Compound Interest"
    # Easy: Simple Interest (15)
    for p, r, t in [(1000, 5, 2), (2000, 6, 3), (5000, 8, 2), (8000, 5, 4), (10000, 7, 3), (12000, 6, 2), (15000, 5, 3), (4000, 10, 2), (6000, 7.5, 2), (9000, 8, 3), (11000, 6, 2), (14000, 5, 4), (7000, 9, 3), (3000, 12, 2), (16000, 5, 2)]:
        si = round((p * r * t) / 100)
        questions.append(make_q(
            topic, "EASY", -1.1,
            f"What is the Simple Interest on a principal of ${p} at an annual rate of {r}% for {t} years?",
            f"${si}", [f"${si + 40}", f"${max(10, si - 30)}", f"${si + 80}"],
            f"SI = (P * R * T) / 100 = ({p} * {r} * {t}) / 100 = ${si}."
        ))

    # Medium: Compound Interest (15)
    for p, r in [(1000, 10), (2000, 10), (5000, 10), (8000, 10), (10000, 10), (4000, 5), (6000, 5), (10000, 5), (12000, 5), (20000, 5), (3000, 20), (5000, 20), (8000, 20), (10000, 20), (15000, 10)]:
        amt = round(p * ((1 + r / 100) ** 2))
        ci = amt - p
        questions.append(make_q(
            topic, "MEDIUM", 0.2,
            f"Find the Compound Interest compounded annually on ${p} at {r}% per annum for 2 years.",
            f"${ci}", [f"${ci - 25}", f"${ci + 30}", f"${p * r * 2 // 100}"],
            f"Amount A = P * (1 + R/100)^2 = {p} * (1 + {r}/100)^2 = ${amt}. CI = A - P = ${ci}."
        ))

    # Hard: Difference between CI and SI for 2 years (15)
    for p, r in [(1000, 5), (2000, 5), (4000, 5), (5000, 6), (8000, 6), (10000, 8), (12000, 8), (15000, 10), (20000, 10), (25000, 10), (30000, 12), (16000, 5), (18000, 10), (22000, 8), (35000, 6)]:
        diff = round(p * ((r / 100) ** 2), 2)
        questions.append(make_q(
            topic, "HARD", 1.2,
            f"What is the difference between Compound Interest and Simple Interest on a principal of ${p} for 2 years at {r}% per annum?",
            f"${diff:.2f}", [f"${diff + 4.50:.2f}", f"${max(0.5, diff - 3.20):.2f}", f"${diff * 2:.2f}"],
            f"For 2 years, CI - SI = P * (R / 100)^2 = {p} * ({r}/100)^2 = ${diff:.2f}."
        ))

    # ═══════════════════════════════════════════════════════════════
    # 11. DATA INTERPRETATION (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Data Interpretation"
    # Easy: Percentage share and proportions (15)
    for yr, base, val in [(2020, 500, 125), (2021, 600, 150), (2022, 800, 240), (2023, 1000, 350), (2024, 1200, 480), (2019, 400, 100), (2018, 500, 175), (2017, 750, 225), (2016, 900, 270), (2015, 650, 195), (2014, 850, 255), (2013, 950, 285), (2012, 1100, 330), (2011, 700, 210), (2010, 450, 135)]:
        pct = round((val / base) * 100, 1)
        questions.append(make_q(
            topic, "EASY", -1.0,
            f"In a corporate division summary for {yr}, total department expenditure was ${base}k while R&D spent ${val}k. What percentage of total expenditure was allocated to R&D?",
            f"{pct}%", [f"{pct + 5:.1f}%", f"{pct - 4:.1f}%", f"{pct * 1.2:.1f}%"],
            f"R&D percentage = (R&D expenditure / Total expenditure) * 100 = ({val} / {base}) * 100 = {pct}%."
        ))

    # Medium: Growth Rate between periods (15)
    for item, v1, v2 in [("Software sales", 200, 250), ("Cloud revenue", 400, 520), ("Hardware units", 150, 180), ("Consulting contracts", 300, 375), ("Subscription ARR", 500, 650), ("Mobile users", 800, 960), ("Ad impressions", 600, 750), ("Active developers", 250, 350), ("API calls", 450, 540), ("Support tickets", 120, 156), ("Server count", 350, 455), ("Database reads", 700, 840), ("Network bandwidth", 550, 715), ("Data pipeline jobs", 220, 297), ("Security audits", 180, 225)]:
        growth = round(((v2 - v1) / v1) * 100, 1)
        questions.append(make_q(
            topic, "MEDIUM", 0.1,
            f"{item} grew from {v1} million to {v2} million over a fiscal year. What was the annual growth rate?",
            f"{growth}%", [f"{growth - 4:.1f}%", f"{growth + 5:.1f}%", f"{round(v2 / v1 * 10, 1)}%"],
            f"Growth rate = [(New Value - Old Value) / Old Value] * 100 = [({v2} - {v1}) / {v1}] * 100 = {growth}%."
        ))

    # Hard: Pie Chart Angle Conversions & Multi-attribute Data (15)
    for deg, tot_rev in [(72, 500), (54, 800), (90, 1200), (108, 1500), (36, 600), (144, 2000), (45, 1600), (60, 900), (120, 2400), (150, 1800), (30, 1200), (80, 1800), (100, 3600), (40, 900), (75, 2400)]:
        val = round((deg / 360) * tot_rev)
        questions.append(make_q(
            topic, "HARD", 1.2,
            f"In a company revenue pie chart, North American sales correspond to a central angle of {deg} degrees. If total company revenue is ${tot_rev} million, what is the North American revenue?",
            f"${val}M", [f"${val + 25}M", f"${val - 30}M", f"${round((deg/100)*tot_rev)}M"],
            f"In a pie chart, 360 degrees = 100%. Revenue = (Central Angle / 360) * Total Revenue = ({deg} / 360) * ${tot_rev}M = ${val}M."
        ))

    # ═══════════════════════════════════════════════════════════════
    # 12. AGES & MIXTURES (45 questions)
    # ═══════════════════════════════════════════════════════════════
    topic = "Ages & Mixtures"
    # Easy: Linear Age Ratios (15)
    for r1, r2, yrs, sum_after in [(3, 4, 5, 45), (2, 3, 4, 38), (4, 5, 6, 66), (1, 2, 5, 40), (3, 5, 4, 48), (2, 5, 7, 56), (3, 7, 5, 60), (4, 7, 3, 50), (5, 6, 4, 52), (1, 3, 6, 48), (2, 7, 4, 44), (3, 8, 5, 65), (5, 8, 3, 45), (4, 9, 2, 56), (3, 5, 6, 52)]:
        # Let ages be r1*x, r2*x. In yrs years, (r1*x + yrs) + (r2*x + yrs) = sum_after
        # (r1 + r2)*x + 2*yrs = sum_after => x = (sum_after - 2*yrs)/(r1 + r2)
        rem = sum_after - 2 * yrs
        if rem > 0 and rem % (r1 + r2) == 0:
            x = rem // (r1 + r2)
            age1 = r1 * x
            questions.append(make_q(
                topic, "EASY", -1.0,
                f"The present ages of two siblings are in the ratio {r1}:{r2}. In {yrs} years, the sum of their ages will be {sum_after} years. What is the present age of the younger sibling?",
                f"{age1} years", [f"{age1 + 3} years", f"{age1 - 2} years", f"{r2 * x} years"],
                f"Let ages be {r1}x and {r2}x. ({r1}x + {yrs}) + ({r2}x + {yrs}) = {sum_after} => ({r1+r2})x + {2*yrs} = {sum_after} => x = {x}. Younger sibling = {r1} * {x} = {age1} years."
            ))
        else:
            # Fallback direct age
            questions.append(make_q(
                topic, "EASY", -1.0,
                f"A father is currently {r1 * 10} years old and his son is {r2 * 5} years old. What was the father's age when the son was born?",
                f"{(r1 * 10) - (r2 * 5)} years", [f"{(r1 * 10) - (r2 * 5) + 4} years", f"{(r1 * 10) - (r2 * 5) - 3} years", "25 years"],
                f"Father's age at son's birth = Father's age - Son's age = {r1 * 10} - {r2 * 5} = {(r1 * 10) - (r2 * 5)} years."
            ))

    # Medium: Alligation rule for mixing two substances (15)
    for c1, c2, mean_p in [(15, 25, 21), (10, 20, 16), (12, 18, 14), (20, 30, 24), (25, 40, 30), (30, 50, 38), (14, 28, 20), (18, 30, 26), (16, 24, 21), (22, 34, 30), (28, 42, 32), (15, 35, 25), (40, 60, 48), (35, 55, 43), (20, 45, 30)]:
        diff_d = c2 - mean_p
        diff_c = mean_p - c1
        g = math.gcd(diff_d, diff_c)
        ratio_str = f"{diff_d // g}:{diff_c // g}"
        questions.append(make_q(
            topic, "MEDIUM", 0.2,
            f"In what ratio must a grocery merchant mix two varieties of tea costing ${c1}/kg and ${c2}/kg so that the resulting mixture is worth ${mean_p}/kg?",
            ratio_str, [f"{diff_c // g}:{diff_d // g}", "1:2", "3:2"],
            f"Using the Rule of Alligation:\n(Quantity of Cheaper) / (Quantity of Dearer) = (Dearer Price - Mean Price) / (Mean Price - Cheaper Price) = ({c2} - {mean_p}) / ({mean_p} - {c1}) = {diff_d} / {diff_c} = {ratio_str}."
        ))

    # Hard: Repeated replacement of liquid in container (15)
    for tot_vol, take_out in [(40, 4), (50, 5), (60, 6), (80, 8), (100, 10), (50, 10), (60, 12), (80, 16), (100, 20), (40, 8), (70, 7), (90, 9), (120, 12), (150, 15), (200, 20)]:
        # 2 replacements
        final_pure = round(tot_vol * ((1 - take_out / tot_vol) ** 2), 2)
        questions.append(make_q(
            topic, "HARD", 1.3,
            f"A container contains {tot_vol} liters of pure milk. From this container, {take_out} liters of milk is taken out and replaced by water. This process is repeated one more time. How much pure milk is left in the container?",
            f"{final_pure} L", [f"{final_pure - 2.5:.2f} L", f"{final_pure + 3.0:.2f} L", f"{tot_vol - 2 * take_out} L"],
            f"After n operations, Quantity of pure liquid = Initial * [1 - (x / Initial)]^n = {tot_vol} * [1 - ({take_out}/{tot_vol})]^2 = {final_pure} liters."
        ))

    return questions

if __name__ == "__main__":
    qs = generate_quant_questions()
    print(f"Generated {len(qs)} quant questions across topics.")
    with open("app/data/bank/quant_bank.json", "w") as f:
        json.dump(qs, f, indent=2)
    print("Saved to app/data/bank/quant_bank.json")
