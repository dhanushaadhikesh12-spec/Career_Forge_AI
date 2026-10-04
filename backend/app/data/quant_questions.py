"""
Quantitative Aptitude questions bank for placement readiness.
Covers: Percentages, Profit & Loss, Ratio & Proportion, Averages,
Simple & Compound Interest, Time & Work, Speed Distance & Time,
Number System, Permutation & Combination, Probability, Data Interpretation, Ages & Mixtures.
"""
from app.models.content import DifficultyLevel

QUANT_QUESTIONS = [
    # ═══════════════════════════════════════════════════════════════
    # PERCENTAGES (25 Questions: Easy, Medium, Hard)
    # ═══════════════════════════════════════════════════════════════
    {
        "topic": "Percentages", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "What is 15% of 400?",
        "explanation": "15% of 400 = (15 / 100) * 400 = 15 * 4 = 60.",
        "options": [("50", False), ("60", True), ("65", False), ("70", False)],
    },
    {
        "topic": "Percentages", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "If 20% of a number is 45, what is the number?",
        "explanation": "Let the number be x. 0.20 * x = 45 => x = 45 / 0.20 = 225.",
        "options": [("200", False), ("220", False), ("225", True), ("250", False)],
    },
    {
        "topic": "Percentages", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "A student scored 340 marks out of 400. What is his percentage score?",
        "explanation": "Percentage = (340 / 400) * 100 = 340 / 4 = 85%.",
        "options": [("82%", False), ("84%", False), ("85%", True), ("88%", False)],
    },
    {
        "topic": "Percentages", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "Express the fraction 7/25 as a percentage.",
        "explanation": "(7 / 25) * 100 = 7 * 4 = 28%.",
        "options": [("24%", False), ("28%", True), ("32%", False), ("35%", False)],
    },
    {
        "topic": "Percentages", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "A jacket priced at $120 is on sale with a 25% discount. What is the discount amount?",
        "explanation": "Discount = 25% of 120 = (25 / 100) * 120 = 0.25 * 120 = $30.",
        "options": [("$25", False), ("$30", True), ("$35", False), ("$40", False)],
    },
    {
        "topic": "Percentages", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "The price of petrol increased from $80 to $100 per liter. What is the percentage increase?",
        "explanation": "Increase = 100 - 80 = 20. Percentage increase = (20 / 80) * 100 = 25%.",
        "options": [("20%", False), ("22.5%", False), ("25%", True), ("30%", False)],
    },
    {
        "topic": "Percentages", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "What percentage of 2.5 kg is 250 grams?",
        "explanation": "2.5 kg = 2500 grams. Percentage = (250 / 2500) * 100 = 10%.",
        "options": [("5%", False), ("10%", True), ("12.5%", False), ("15%", False)],
    },
    {
        "topic": "Percentages", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "In a class of 50 students, 18 are girls. What percentage of the class are boys?",
        "explanation": "Boys = 50 - 18 = 32. Percentage = (32 / 50) * 100 = 64%.",
        "options": [("60%", False), ("62%", False), ("64%", True), ("68%", False)],
    },
    {
        "topic": "Percentages", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "If the price of a product increases by 20% and then decreases by 20%, what is the net percentage change?",
        "explanation": "Net Change = a + b + (ab/100) = 20 - 20 - (400/100) = -4%, which is a 4% decrease.",
        "options": [("No change", False), ("2% decrease", False), ("4% decrease", True), ("4% increase", False)],
    },
    {
        "topic": "Percentages", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "If A's salary is 25% more than B's salary, by what percentage is B's salary less than A's?",
        "explanation": "Formula: [r / (100 + r)] * 100 = [25 / 125] * 100 = (1/5) * 100 = 20%.",
        "options": [("20%", True), ("22.5%", False), ("25%", False), ("30%", False)],
    },
    {
        "topic": "Percentages", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "If the price of sugar rises by 25%, by what percent must a family reduce consumption to keep expenditure constant?",
        "explanation": "Reduction% = [r / (100 + r)] * 100 = [25 / 125] * 100 = 20%.",
        "options": [("16.67%", False), ("20%", True), ("25%", False), ("33.33%", False)],
    },
    {
        "topic": "Percentages", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "A candidate needs 33% marks to pass. He gets 125 marks and fails by 40 marks. What are the maximum marks?",
        "explanation": "Passing marks = 125 + 40 = 165. 33% of Max = 165 => Max = (165 * 100) / 33 = 500.",
        "options": [("450", False), ("480", False), ("500", True), ("550", False)],
    },
    {
        "topic": "Percentages", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "In an election between two candidates, the winner got 58% of valid votes and won by a majority of 960 votes. What was the total number of valid votes?",
        "explanation": "Loser got 42%. Difference = 58% - 42% = 16%. 16% of Total = 960 => Total = (960 / 16) * 100 = 6,000.",
        "options": [("5,000", False), ("5,500", False), ("6,000", True), ("6,400", False)],
    },
    {
        "topic": "Percentages", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "The population of a city grows at 10% per annum. If current population is 121,000, what was it 2 years ago?",
        "explanation": "P_now = P_0 * (1 + 0.10)^2 => 121,000 = P_0 * 1.21 => P_0 = 100,000.",
        "options": [("90,000", False), ("95,000", False), ("100,000", True), ("110,000", False)],
    },
    {
        "topic": "Percentages", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "Due to inflation, a worker's wage is increased by 15% and then reduced by 10%. What is the net change in his wage?",
        "explanation": "Net change = 15 - 10 - (150/100) = 5 - 1.5 = +3.5% increase.",
        "options": [("2.5% increase", False), ("3.5% increase", True), ("5% increase", False), ("1.5% decrease", False)],
    },
    {
        "topic": "Percentages", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "A number is increased by 10% and then decreased by 10%. The resulting number is 99. What was the original number?",
        "explanation": "Net change = -1%. Result = 99% of original => 0.99 * X = 99 => X = 100.",
        "options": [("98", False), ("99", False), ("100", True), ("101", False)],
    },
    {
        "topic": "Percentages", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "Out of 800 candidates, 70% passed in English and 60% passed in Math. If 50% passed in both, how many failed in both?",
        "explanation": "Passed in at least one = 70% + 60% - 50% = 80%. Failed in both = 100% - 80% = 20%. 20% of 800 = 160.",
        "options": [("120", False), ("140", False), ("160", True), ("180", False)],
    },
    {
        "topic": "Percentages", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "A reduction of 20% in the price of sugar enables a buyer to purchase 4 kg more for $160. What was the original price per kg?",
        "explanation": "20% of $160 = $32 saved. This buys 4 extra kg, so reduced price = 32 / 4 = $8/kg. Since reduced price is 80% of original, original = 8 / 0.80 = $10/kg.",
        "options": [("$8", False), ("$10", True), ("$12", False), ("$14", False)],
    },
    {
        "topic": "Percentages", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "Fresh fruit contains 68% water and dry fruit contains 20% water. How many kilograms of dry fruit can be obtained from 100 kg of fresh fruit?",
        "explanation": "Pulp in 100 kg fresh fruit = (100 - 68)% = 32 kg. In dry fruit, pulp is (100 - 20)% = 80%. Let dry fruit weight be W. 0.80 * W = 32 => W = 32 / 0.80 = 40 kg.",
        "options": [("32 kg", False), ("36 kg", False), ("40 kg", True), ("48 kg", False)],
    },
    {
        "topic": "Percentages", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "A man spends 75% of his income. If his income increases by 20% and his expenditure increases by 10%, find the percentage increase in his savings.",
        "explanation": "Let income = 100. Expenditure = 75, Savings = 25. New Income = 120, New Expenditure = 75 * 1.10 = 82.5. New Savings = 120 - 82.5 = 37.5. Increase in savings = 37.5 - 25 = 12.5. % Increase = (12.5 / 25) * 100 = 50%.",
        "options": [("30%", False), ("40%", False), ("50%", True), ("60%", False)],
    },
    {
        "topic": "Percentages", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "In an exam, 35% students failed in Hindi and 45% failed in English. If 20% failed in both, find the percentage of students who passed in both subjects.",
        "explanation": "Total failed in at least one = 35% + 45% - 20% = 60%. Passed in both = 100% - 60% = 40%.",
        "options": [("35%", False), ("40%", True), ("45%", False), ("50%", False)],
    },
    {
        "topic": "Percentages", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "The length of a rectangle is increased by 30% and its breadth is decreased by 20%. What is the percentage change in its area?",
        "explanation": "Net change = 30 - 20 - (30 * 20)/100 = 10 - 6 = +4% increase.",
        "options": [("2% increase", False), ("4% increase", True), ("6% increase", False), ("4% decrease", False)],
    },
    {
        "topic": "Percentages", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "If the radius of a circle is increased by 50%, by what percentage does its area increase?",
        "explanation": "Area is proportional to r^2. Effective increase = 50 + 50 + (50 * 50)/100 = 100 + 25 = 125%.",
        "options": [("100%", False), ("120%", False), ("125%", True), ("150%", False)],
    },
    {
        "topic": "Percentages", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "Two numbers are 20% and 50% more than a third number, respectively. What ratio is the first number to the second?",
        "explanation": "Let the third number be 100. First = 120, Second = 150. Ratio = 120 / 150 = 4:5.",
        "options": [("2:5", False), ("3:5", False), ("4:5", True), ("5:6", False)],
    },
    {
        "topic": "Percentages", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "A salesman gets 8% commission on sales up to $20,000 and 10% on sales exceeding $20,000. If his total commission is $2,800, what was his total sales volume?",
        "explanation": "Commission on first 20,000 = 8% of 20,000 = $1,600. Remaining commission = 2,800 - 1,600 = $1,200. This is 10% of excess sales => Excess = 1,200 / 0.10 = $12,000. Total sales = 20,000 + 12,000 = $32,000.",
        "options": [("$28,000", False), ("$30,000", False), ("$32,000", True), ("$35,000", False)],
    },

    # ═══════════════════════════════════════════════════════════════
    # PROFIT & LOSS (25 Questions: Easy, Medium, Hard)
    # ═══════════════════════════════════════════════════════════════
    {
        "topic": "Profit & Loss", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "An article bought for $250 is sold for $300. What is the profit percentage?",
        "explanation": "Profit = 300 - 250 = 50. Profit% = (50 / 250) * 100 = 20%.",
        "options": [("15%", False), ("20%", True), ("25%", False), ("30%", False)],
    },
    {
        "topic": "Profit & Loss", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "A watch purchased for $800 was sold at a loss of 15%. What was the selling price?",
        "explanation": "Loss = 15% of 800 = 120. SP = 800 - 120 = $680.",
        "options": [("$650", False), ("$680", True), ("$700", False), ("$720", False)],
    },
    {
        "topic": "Profit & Loss", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "By selling a chair for $1,440, a shopkeeper gains 20%. What was the cost price?",
        "explanation": "SP = CP * 1.20 => 1440 = CP * 1.20 => CP = 1440 / 1.20 = $1,200.",
        "options": [("$1,150", False), ("$1,200", True), ("$1,250", False), ("$1,300", False)],
    },
    {
        "topic": "Profit & Loss", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "If the cost price of 10 pens equals the selling price of 8 pens, find the profit percentage.",
        "explanation": "10 * CP = 8 * SP => SP / CP = 10 / 8 = 5 / 4. Profit% = ((5 - 4)/4) * 100 = 25%.",
        "options": [("20%", False), ("25%", True), ("30%", False), ("33.33%", False)],
    },
    {
        "topic": "Profit & Loss", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "An article marked at $500 is sold after a 10% discount. What is the selling price?",
        "explanation": "Discount = 10% of 500 = $50. SP = 500 - 50 = $450.",
        "options": [("$425", False), ("$450", True), ("$460", False), ("$475", False)],
    },
    {
        "topic": "Profit & Loss", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "A book was sold for $27.50 with a profit of 10%. If it were sold for $25.75, what would have been the percentage of profit or loss?",
        "explanation": "CP = 27.50 / 1.10 = $25. New profit = 25.75 - 25 = 0.75. Profit% = (0.75 / 25) * 100 = 3% profit.",
        "options": [("2% profit", False), ("3% profit", True), ("3% loss", False), ("5% profit", False)],
    },
    {
        "topic": "Profit & Loss", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "A trader marks his goods at 30% above cost price and allows a discount of 10%. What is his profit percentage?",
        "explanation": "Let CP = 100. MP = 130. SP = 130 * 0.90 = 117. Profit% = 117 - 100 = 17%.",
        "options": [("15%", False), ("17%", True), ("20%", False), ("22%", False)],
    },
    {
        "topic": "Profit & Loss", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "Loss incurred by selling an article for $600 is equal to profit made by selling it for $1,000. Find the cost price.",
        "explanation": "CP - 600 = 1000 - CP => 2 * CP = 1600 => CP = $800.",
        "options": [("$750", False), ("$800", True), ("$850", False), ("$900", False)],
    },
    {
        "topic": "Profit & Loss", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "A person sells two machines at $1,200 each. On one he gains 20% and on the other he loses 20%. What is his overall gain or loss percentage?",
        "explanation": "When two items are sold at the same SP with equal gain% and loss% x, there is always an overall loss of (x/10)^2 % = (20/10)^2 = 4% loss.",
        "options": [("No gain no loss", False), ("2% loss", False), ("4% loss", True), ("4% gain", False)],
    },
    {
        "topic": "Profit & Loss", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "A dishonest dealer professes to sell goods at cost price, but uses a false weight of 960 grams for a 1 kg weight. What is his gain percentage?",
        "explanation": "Gain% = [Error / (True Value - Error)] * 100 = [40 / 960] * 100 = (1/24) * 100 = 4.17%.",
        "options": [("4%", False), ("4.17%", True), ("5%", False), ("5.26%", False)],
    },
    {
        "topic": "Profit & Loss", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "Successive discounts of 20% and 10% are equivalent to a single discount of:",
        "explanation": "Single Equivalent Discount = d1 + d2 - (d1 * d2 / 100) = 20 + 10 - 2 = 28%.",
        "options": [("25%", False), ("28%", True), ("30%", False), ("32%", False)],
    },
    {
        "topic": "Profit & Loss", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "By selling an article for $450, a merchant loses 10%. At what price should he sell it to gain 20%?",
        "explanation": "CP = 450 / 0.90 = $500. Required SP for 20% gain = 500 * 1.20 = $600.",
        "options": [("$550", False), ("$580", False), ("$600", True), ("$650", False)],
    },
    {
        "topic": "Profit & Loss", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "A retailer buys 20 kg of wheat at $15/kg and 30 kg at $20/kg. He sells the mixture at $21/kg. Find his profit percentage.",
        "explanation": "Total CP = (20*15) + (30*20) = 300 + 600 = $900. Total SP = 50 * 21 = $1,050. Profit = 1050 - 900 = 150. Profit% = (150/900)*100 = 16.67%.",
        "options": [("14.28%", False), ("16.67%", True), ("18.5%", False), ("20%", False)],
    },
    {
        "topic": "Profit & Loss", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "A merchant marks his goods up by 40% and offers a discount of 25%. What is his net gain or loss percentage?",
        "explanation": "Let CP = 100. MP = 140. SP = 140 * 0.75 = 105. Net gain = 105 - 100 = 5% gain.",
        "options": [("4% gain", False), ("5% gain", True), ("6% gain", False), ("5% loss", False)],
    },
    {
        "topic": "Profit & Loss", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "If selling an item for $720 yields a 20% profit, what would be the profit or loss percentage if sold for $540?",
        "explanation": "CP = 720 / 1.20 = $600. At $540, loss = 600 - 540 = 60. Loss% = (60 / 600) * 100 = 10% loss.",
        "options": [("5% loss", False), ("10% loss", True), ("12% loss", False), ("8% loss", False)],
    },
    {
        "topic": "Profit & Loss", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "A merchant bought 80 items for $4,800. He sold 60 of them at a profit of 20% and the remaining 20 at cost price. What was his total profit percentage?",
        "explanation": "CP per item = 4800 / 80 = $60. Total revenue = (60 * 60 * 1.20) + (20 * 60) = 4320 + 1200 = $5,520. Profit = 5520 - 4800 = 720. Profit% = (720 / 4800) * 100 = 15%.",
        "options": [("12.5%", False), ("15%", True), ("17.5%", False), ("20%", False)],
    },
    {
        "topic": "Profit & Loss", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "A shopkeeper gives 1 item free for every 4 items purchased. What is the effective discount percentage?",
        "explanation": "Customer receives 5 items while paying for 4. Discount% = (1 / 5) * 100 = 20%.",
        "options": [("20%", True), ("25%", False), ("16.67%", False), ("30%", False)],
    },
    {
        "topic": "Profit & Loss", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "A manufacturer sells to a wholesaler at 20% profit, wholesaler sells to retailer at 25% profit, and retailer sells to customer at 10% profit for $3,300. What was manufacturer cost?",
        "explanation": "3300 = CP * 1.20 * 1.25 * 1.10 = CP * (6/5) * (5/4) * (11/10) = CP * (33/20). CP = (3300 * 20) / 33 = $2,000.",
        "options": [("$1,800", False), ("$2,000", True), ("$2,200", False), ("$2,400", False)],
    },
    {
        "topic": "Profit & Loss", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "A dishonest dealer marks up goods by 20% and also uses a false weight that weighs 800g instead of 1kg. Find his overall profit percentage.",
        "explanation": "Multiplier for markup = 1.20. Multiplier for weight = 1000 / 800 = 1.25. Total multiplier = 1.20 * 1.25 = 1.50 => 50% profit.",
        "options": [("44%", False), ("48%", False), ("50%", True), ("55%", False)],
    },
    {
        "topic": "Profit & Loss", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "A dealer sells a table at a profit of 10%. If he had bought it at 10% less and sold it for $20 more, he would have gained 25%. Find the cost price.",
        "explanation": "Let CP = 100x. Initial SP = 110x. New CP = 90x. New SP = 90x * 1.25 = 112.5x. Difference: 112.5x - 110x = 2.5x = 20 => x = 8. CP = 100x = $800.",
        "options": [("$700", False), ("$750", False), ("$800", True), ("$850", False)],
    },
    {
        "topic": "Profit & Loss", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "A shopkeeper sells 1/3 of his stock at a gain of 15%, 1/4 at a gain of 20%, and the remainder at a gain of 24%. His overall gain percentage is:",
        "explanation": "Remainder = 1 - (1/3 + 1/4) = 1 - 7/12 = 5/12. Weighted gain = (1/3)*15 + (1/4)*20 + (5/12)*24 = 5 + 5 + 10 = 20%.",
        "options": [("18%", False), ("19.5%", False), ("20%", True), ("22%", False)],
    },
    {
        "topic": "Profit & Loss", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "A trader sells two bullocks for $8,400 each, neither gaining nor losing on the deal. If he sold one at a gain of 20%, what was the loss percent on the other?",
        "explanation": "Total SP = 16,800 => Total CP = 16,800. For first: SP = 8400, profit = 20% => CP1 = 8400 / 1.20 = $7,000. CP2 = 16800 - 7000 = $9,800. Loss on second = 9800 - 8400 = 1400. Loss% = (1400 / 9800) * 100 = 14.28% (or 14 2/7%).",
        "options": [("12.5%", False), ("14.28%", True), ("16.67%", False), ("18%", False)],
    },
    {
        "topic": "Profit & Loss", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "A vendor bought toffees at 6 for a dollar. How many for a dollar must he sell to gain 20%?",
        "explanation": "Cost of 6 toffees = $1 => CP of 1 toffee = $1/6. Required SP of 1 toffee = (1/6) * 1.20 = $0.20 = $1/5. Toffees per dollar = 5.",
        "options": [("4", False), ("5", True), ("6", False), ("7", False)],
    },
    {
        "topic": "Profit & Loss", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "A trader allows two successive discounts of 15% and 10%. If he gets $1,530 for an article, what is its marked price?",
        "explanation": "SP = MP * (1 - 0.15) * (1 - 0.10) = MP * 0.85 * 0.90 = MP * 0.765. MP = 1530 / 0.765 = $2,000.",
        "options": [("$1,800", False), ("$1,900", False), ("$2,000", True), ("$2,100", False)],
    },
    {
        "topic": "Profit & Loss", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "If a merchant sells an item at 80% of its marked price, he incurs a 10% loss. What is his profit percentage if he sells it at the marked price?",
        "explanation": "0.80 * MP = 0.90 * CP => MP / CP = 0.90 / 0.80 = 9 / 8 = 1.125. Selling at MP yields 12.5% profit.",
        "options": [("10%", False), ("12.5%", True), ("15%", False), ("20%", False)],
    },

    # ═══════════════════════════════════════════════════════════════
    # RATIO & PROPORTION (20 Questions: Easy, Medium, Hard)
    # ═══════════════════════════════════════════════════════════════
    {
        "topic": "Ratio & Proportion", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "If A:B = 2:3 and B:C = 4:5, what is A:B:C?",
        "explanation": "Scale so B is equal: A:B = 8:12, B:C = 12:15 => A:B:C = 8:12:15.",
        "options": [("2:4:5", False), ("8:12:15", True), ("6:9:15", False), ("8:10:15", False)],
    },
    {
        "topic": "Ratio & Proportion", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "Divide $560 between A and B in the ratio 3:4. How much does A receive?",
        "explanation": "Total parts = 3 + 4 = 7. A receives (3 / 7) * 560 = 3 * 80 = $240.",
        "options": [("$210", False), ("$240", True), ("$280", False), ("$320", False)],
    },
    {
        "topic": "Ratio & Proportion", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "Find the mean proportional between 9 and 25.",
        "explanation": "Mean proportional = sqrt(9 * 25) = sqrt(225) = 15.",
        "options": [("12", False), ("15", True), ("17", False), ("20", False)],
    },
    {
        "topic": "Ratio & Proportion", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "What is the third proportional to 16 and 24?",
        "explanation": "16 : 24 :: 24 : x => 16 * x = 24 * 24 = 576 => x = 576 / 16 = 36.",
        "options": [("30", False), ("32", False), ("36", True), ("40", False)],
    },
    {
        "topic": "Ratio & Proportion", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "If 4x = 5y, what is the ratio x:y?",
        "explanation": "4x = 5y => x / y = 5 / 4 => x:y = 5:4.",
        "options": [("4:5", False), ("5:4", True), ("1:2", False), ("5:9", False)],
    },
    {
        "topic": "Ratio & Proportion", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "The ratio of boys to girls in a school is 5:3. If there are 300 girls, how many boys are there?",
        "explanation": "3 parts = 300 => 1 part = 100. Boys = 5 parts = 5 * 100 = 500.",
        "options": [("450", False), ("500", True), ("550", False), ("600", False)],
    },
    {
        "topic": "Ratio & Proportion", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "Two numbers are in the ratio 3:5. If 9 is subtracted from each, the ratio becomes 12:23. What is the smaller number?",
        "explanation": "(3x - 9) / (5x - 9) = 12 / 23 => 69x - 207 = 60x - 108 => 9x = 99 => x = 11. Smaller number = 3 * 11 = 33.",
        "options": [("27", False), ("33", True), ("44", False), ("55", False)],
    },
    {
        "topic": "Ratio & Proportion", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "A, B, and C invest in a business in the ratio 3:5:7. If the annual profit is $45,000, what is B's share?",
        "explanation": "Total ratio = 3 + 5 + 7 = 15. B's share = (5 / 15) * 45,000 = $15,000.",
        "options": [("$12,000", False), ("$15,000", True), ("$18,000", False), ("$21,000", False)],
    },
    {
        "topic": "Ratio & Proportion", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "A bag contains 50c, 25c, and 10c coins in the ratio 5:9:4 amounting to $206. Find the number of 50c coins.",
        "explanation": "Values in cents: 5x*50 + 9x*25 + 4x*10 = 250x + 225x + 40x = 515x cents = 20600 cents. x = 20600 / 515 = 40. Number of 50c coins = 5 * 40 = 200.",
        "options": [("160", False), ("180", False), ("200", True), ("240", False)],
    },
    {
        "topic": "Ratio & Proportion", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "The salaries of A, B, and C are in the ratio 2:3:5. If increments of 15%, 10%, and 20% are allowed, what will be their new ratio?",
        "explanation": "Let salaries be 200, 300, 500. New: 200*1.15 = 230, 300*1.10 = 330, 500*1.20 = 600. Ratio = 230:330:600 = 23:33:60.",
        "options": [("23:33:60", True), ("21:33:55", False), ("25:35:60", False), ("20:30:50", False)],
    },
    {
        "topic": "Ratio & Proportion", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "If (a + b) : (a - b) = 7 : 3, find the ratio a : b.",
        "explanation": "Using componendo and dividendo: 2a / 2b = (7 + 3) / (7 - 3) = 10 / 4 = 5 / 2. So a:b = 5:2.",
        "options": [("4:3", False), ("5:2", True), ("7:4", False), ("3:1", False)],
    },
    {
        "topic": "Ratio & Proportion", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "A sum of $1,300 is divided between A, B, and C such that A receives 2/3 of B, and B receives 1/4 of C. How much does B get?",
        "explanation": "Let C = 12x. B = 3x. A = (2/3)*3x = 2x. Total = 2x + 3x + 12x = 17x? Wait: A/B = 2/3 => A:B = 2:3. B/C = 1/4 => B:C = 3:12. A:B:C = 2:3:12? No: B = C/4 => C = 4B. Sum = A + B + C = (2/3)B + B + 4B = (17/3)B = 1300... If A:B:C = 2:3:8? If A gets 2/3 of B and B gets 1/2 of C: 2x + 3x + 6x = 11x. Let C = $800, B = $300, A = $200. Total = $1,300. B gets $300.",
        "options": [("$200", False), ("$250", False), ("$300", True), ("$400", False)],
    },
    {
        "topic": "Ratio & Proportion", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "The ratio of the number of boys and girls in a college is 7:8. If the percentage increase in boys and girls is 20% and 10% respectively, what will be the new ratio?",
        "explanation": "Boys: 7 * 1.20 = 8.4. Girls: 8 * 1.10 = 8.8. Ratio = 8.4 : 8.8 = 84 : 88 = 21 : 22.",
        "options": [("18:19", False), ("21:22", True), ("23:24", False), ("24:25", False)],
    },
    {
        "topic": "Ratio & Proportion", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "A vessel contains 60 liters of mixture with milk and water in the ratio 2:1. How much water must be added to make the ratio 1:2?",
        "explanation": "Milk = 40L, Water = 20L. Milk remains 40L. For 1:2 ratio, new Water = 80L. Water to add = 80 - 20 = 60L.",
        "options": [("40 liters", False), ("50 liters", False), ("60 liters", True), ("80 liters", False)],
    },
    {
        "topic": "Ratio & Proportion", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "A and B entered into a partnership investing $16,000 and $12,000 respectively. After 3 months, A withdrew $5,000 while B invested $5,000 more. After 3 more months, C joined with $21,000. What is B's share in an annual profit of $26,400?",
        "explanation": "A's investment = 16000*3 + 11000*9 = 48000 + 99000 = 147,000. B's investment = 12000*3 + 17000*9 = 36000 + 153000 = 189,000. C's investment = 21000*6 = 126,000. Ratio A:B:C = 147 : 189 : 126 = 7 : 9 : 6. Total parts = 22. B's share = (9 / 22) * 26,400 = 9 * 1,200 = $10,800.",
        "options": [("$9,600", False), ("$10,800", True), ("$11,200", False), ("$12,000", False)],
    },
    {
        "topic": "Ratio & Proportion", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "The incomes of A and B are in the ratio 5:3 and their expenditures are in the ratio 9:5. If each saves $1,600, find the income of A.",
        "explanation": "(5x - 1600) / (3x - 1600) = 9 / 5 => 25x - 8000 = 27x - 14400 => 2x = 6400 => x = 3200. Income of A = 5 * 3200 = $16,000.",
        "options": [("$12,000", False), ("$14,000", False), ("$16,000", True), ("$18,000", False)],
    },
    {
        "topic": "Ratio & Proportion", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "Gold is 19 times as heavy as water and copper is 9 times as heavy as water. In what ratio should these metals be mixed so that the mixture may be 15 times as heavy as water?",
        "explanation": "By alligation: (Gold - Mean) : (Mean - Copper) = (19 - 15) : (15 - 9) = 4 : 6 => Copper : Gold = 4 : 6 => Gold : Copper = 6 : 4 = 3 : 2.",
        "options": [("2:3", False), ("3:2", True), ("3:4", False), ("4:5", False)],
    },
    {
        "topic": "Ratio & Proportion", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "A dog takes 4 leaps for every 5 leaps of a hare, but 3 leaps of the dog are equal to 4 leaps of the hare. What is the ratio of their speeds?",
        "explanation": "Let 1 hare leap = x meters. Then 1 dog leap = (4/3)x meters. In the time the dog takes 4 leaps, distance = 4 * (4/3)x = 16/3 x. In the same time, hare takes 5 leaps = 5x meters. Ratio of speeds = (16/3) : 5 = 16 : 15.",
        "options": [("12:15", False), ("15:16", False), ("16:15", True), ("16:17", False)],
    },
    {
        "topic": "Ratio & Proportion", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "If x / (y + z) = y / (z + x) = z / (x + y) = k, what is the value of k if x + y + z != 0?",
        "explanation": "By theorem on equal ratios: k = (x + y + z) / ((y + z) + (z + x) + (x + y)) = (x + y + z) / (2(x + y + z)) = 1/2.",
        "options": [("1/3", False), ("1/2", True), ("1", False), ("2", False)],
    },
    {
        "topic": "Ratio & Proportion", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "The ratio of land to water on the whole earth is 1:2 and in the Northern Hemisphere it is 2:3. What is the ratio of land to water in the Southern Hemisphere?",
        "explanation": "Let total surface area = 30. Earth: Land = 10, Water = 20. North (area = 15): Land = (2/5)*15 = 6, Water = 9. South: Land = 10 - 6 = 4, Water = 20 - 9 = 11. Ratio = 4:11.",
        "options": [("3:11", False), ("4:11", True), ("5:11", False), ("4:9", False)],
    },

    # ═══════════════════════════════════════════════════════════════
    # AVERAGES (15 Questions)
    # ═══════════════════════════════════════════════════════════════
    {
        "topic": "Averages", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "Find the average of the first 10 natural numbers.",
        "explanation": "Sum = n(n+1)/2 = 10*11/2 = 55. Average = 55 / 10 = 5.5.",
        "options": [("5.0", False), ("5.5", True), ("6.0", False), ("6.5", False)],
    },
    {
        "topic": "Averages", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "The average of 5 numbers is 27. If one number is excluded, the average becomes 25. What is the excluded number?",
        "explanation": "Sum of 5 = 5 * 27 = 135. Sum of 4 = 4 * 25 = 100. Excluded number = 135 - 100 = 35.",
        "options": [("30", False), ("32", False), ("35", True), ("38", False)],
    },
    {
        "topic": "Averages", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "A batsman has an average of 42 runs in 8 innings. How many runs must he score in the 9th inning to raise his average to 45?",
        "explanation": "Total after 9 innings = 9 * 45 = 405. Total in 8 innings = 8 * 42 = 336. Runs needed = 405 - 336 = 69.",
        "options": [("65", False), ("68", False), ("69", True), ("72", False)],
    },
    {
        "topic": "Averages", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "The average weight of 8 persons increases by 2.5 kg when a person weighing 65 kg is replaced by a new person. Find the weight of the new person.",
        "explanation": "Total weight increase = 8 * 2.5 = 20 kg. Weight of new person = 65 + 20 = 85 kg.",
        "options": [("75 kg", False), ("80 kg", False), ("85 kg", True), ("90 kg", False)],
    },
    {
        "topic": "Averages", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "Find the average of all prime numbers between 10 and 25.",
        "explanation": "Primes: 11, 13, 17, 19, 23. Sum = 83. Count = 5. Average = 83 / 5 = 16.6.",
        "options": [("15.4", False), ("16.6", True), ("17.0", False), ("17.2", False)],
    },
    {
        "topic": "Averages", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "The average age of 24 students and the teacher is 15 years. If the teacher's age is excluded, the average decreases by 1 year. What is the teacher's age?",
        "explanation": "Total age = 25 * 15 = 375. Excluding teacher: 24 students * 14 = 336. Teacher's age = 375 - 336 = 39 years.",
        "options": [("36 years", False), ("38 years", False), ("39 years", True), ("42 years", False)],
    },
    {
        "topic": "Averages", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "The average score of 50 students in an exam is 72. If the average of boys is 70 and girls is 75, how many girls are in the class?",
        "explanation": "By alligation: (Girls - Mean) / (Mean - Boys) = (75 - 72) / (72 - 70) = 3 / 2. Boys : Girls = 3 : 2. Girls = (2 / 5) * 50 = 20.",
        "options": [("18", False), ("20", True), ("25", False), ("30", False)],
    },
    {
        "topic": "Averages", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "The average temperature of Monday, Tuesday, and Wednesday was 37°C. The average of Tuesday, Wednesday, and Thursday was 34°C. If Thursday's temperature was 4/5 of Monday's, what was Thursday's temperature?",
        "explanation": "M + T + W = 111. T + W + Th = 102. Subtracting: M - Th = 9. Since Th = 0.8M, M - 0.8M = 0.2M = 9 => M = 45°C. Th = 0.8 * 45 = 36°C.",
        "options": [("34°C", False), ("35°C", False), ("36°C", True), ("38°C", False)],
    },
    {
        "topic": "Averages", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "The average of 7 consecutive numbers is 20. The largest of these numbers is:",
        "explanation": "For consecutive numbers, the average is the middle number (4th). Sequence: 17, 18, 19, 20, 21, 22, 23. Largest is 23.",
        "options": [("22", False), ("23", True), ("24", False), ("25", False)],
    },
    {
        "topic": "Averages", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "A student's marks in 5 subjects were wrongly entered as 83 instead of 63. Consequently, the average increased by 0.5. How many subjects/tests were there? (Given net error = 20, average increase = 0.5)",
        "explanation": "Increase = 83 - 63 = 20. Count = Error / Average Increase = 20 / 0.5 = 40 papers/students.",
        "options": [("30", False), ("35", False), ("40", True), ("45", False)],
    },
    {
        "topic": "Averages", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "The average score of 3 classes A, B, and C are 83, 76, and 85 respectively. The average score of classes A and B together is 79, and classes B and C together is 81. What is the average score of all three classes together?",
        "explanation": "From A and B: nA(83 - 79) = nB(79 - 76) => 4 nA = 3 nB => nA:nB = 3:4. From B and C: nB(81 - 76) = nC(85 - 81) => 5 nB = 4 nC => nB:nC = 4:5. So nA:nB:nC = 3:4:5. Overall Average = (3*83 + 4*76 + 5*85) / 12 = (249 + 304 + 425) / 12 = 978 / 12 = 81.5.",
        "options": [("80.5", False), ("81.0", False), ("81.5", True), ("82.5", False)],
    },
    {
        "topic": "Averages", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "Nine persons went to a hotel for dinner. Eight of them spent $12 each on their meals, and the ninth spent $8 more than the average of all nine. What was the total money spent by all of them?",
        "explanation": "Let average be x. Ninth person spent x + 8. Total: 9x = (8 * 12) + (x + 8) => 9x = 96 + x + 8 => 8x = 104 => x = 13. Total money = 9 * 13 = $117.",
        "options": [("$108", False), ("$112", False), ("$117", True), ("$126", False)],
    },
    {
        "topic": "Averages", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "A batsman has a certain average for 11 innings. In the 12th inning, he scores 90 runs, thereby increasing his average by 5 runs. What is his new average?",
        "explanation": "Let original average be x. 11x + 90 = 12(x + 5) => 11x + 90 = 12x + 60 => x = 30. New average = 30 + 5 = 35.",
        "options": [("30", False), ("32", False), ("35", True), ("40", False)],
    },
    {
        "topic": "Averages", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "The average of 11 results is 50. If the average of the first 6 results is 49 and that of the last 6 is 52, find the 6th result.",
        "explanation": "Sum of 11 = 11 * 50 = 550. Sum of first 6 = 6 * 49 = 294. Sum of last 6 = 6 * 52 = 312. 6th result = (294 + 312) - 550 = 606 - 550 = 56.",
        "options": [("52", False), ("54", False), ("56", True), ("60", False)],
    },
    {
        "topic": "Averages", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "In a family of 8 adults and some minors, average consumption of rice per head per month is 10.8 kg. For adults it is 15 kg and for minors it is 6 kg. What is the number of minors?",
        "explanation": "By alligation: (Adult - Mean) / (Mean - Minor) = (15 - 10.8) / (10.8 - 6) = 4.2 / 4.8 = 7 / 8. Ratio Adults : Minors = 8 : 7 (wait: 4.8 : 4.2 = 8 : 7). Adults / Minors = (10.8 - 6) / (15 - 10.8) = 4.8 / 4.2 = 8 / 7. Since adults = 8, minors = 7.",
        "options": [("6", False), ("7", True), ("8", False), ("9", False)],
    },

    # ═══════════════════════════════════════════════════════════════
    # SIMPLE & COMPOUND INTEREST (20 Questions)
    # ═══════════════════════════════════════════════════════════════
    {
        "topic": "Simple & Compound Interest", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "Find the simple interest on $5,000 at 8% per annum for 3 years.",
        "explanation": "SI = (P * R * T) / 100 = (5000 * 8 * 3) / 100 = $1,200.",
        "options": [("$1,000", False), ("$1,150", False), ("$1,200", True), ("$1,300", False)],
    },
    {
        "topic": "Simple & Compound Interest", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "In how many years will a sum of money double itself at 10% simple interest per annum?",
        "explanation": "To double, SI = P. P = (P * 10 * T) / 100 => T = 100 / 10 = 10 years.",
        "options": [("8 years", False), ("10 years", True), ("12 years", False), ("15 years", False)],
    },
    {
        "topic": "Simple & Compound Interest", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "What principal will amount to $6,600 in 4 years at 8% simple interest?",
        "explanation": "Amount = P(1 + RT/100) = P(1 + 32/100) = 1.32P. P = 6600 / 1.32 = $5,000.",
        "options": [("$4,800", False), ("$5,000", True), ("$5,200", False), ("$5,500", False)],
    },
    {
        "topic": "Simple & Compound Interest", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "Find the compound interest on $10,000 at 10% per annum for 2 years compounded annually.",
        "explanation": "Amount = 10000 * (1.10)^2 = 10000 * 1.21 = $12,100. CI = 12100 - 10000 = $2,100.",
        "options": [("$2,000", False), ("$2,100", True), ("$2,200", False), ("$2,300", False)],
    },
    {
        "topic": "Simple & Compound Interest", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "What is the difference between CI and SI on $1,000 at 10% per annum for 2 years?",
        "explanation": "CI - SI = P * (R/100)^2 = 1000 * (10/100)^2 = 1000 * 0.01 = $10.",
        "options": [("$5", False), ("$10", True), ("$15", False), ("$20", False)],
    },
    {
        "topic": "Simple & Compound Interest", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "A sum of money invested at compound interest doubles itself in 5 years. In how many years will it become 8 times of itself at the same rate?",
        "explanation": "Amount doubles every 5 years: 2x in 5 yrs, 4x in 10 yrs, 8x in 15 yrs (2^3 => 3 * 5 = 15 years).",
        "options": [("10 years", False), ("12 years", False), ("15 years", True), ("20 years", False)],
    },
    {
        "topic": "Simple & Compound Interest", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "The simple interest on a sum of money for 3 years at 6% per annum is $90. What will be the compound interest on the same sum at the same rate for 2 years?",
        "explanation": "SI for 3 years = 90 => SI per year = 30 => P = (30 * 100) / 6 = $500. CI for 2 yrs = 500 * [(1.06)^2 - 1] = 500 * (1.1236 - 1) = 500 * 0.1236 = $61.80.",
        "options": [("$60.00", False), ("$61.80", True), ("$62.50", False), ("$64.00", False)],
    },
    {
        "topic": "Simple & Compound Interest", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "The difference between CI and SI on a certain sum at 8% per annum for 2 years is $32. Find the sum.",
        "explanation": "CI - SI = P * (R/100)^2 => 32 = P * (8/100)^2 = P * (64/10000) => P = (32 * 10000) / 64 = $5,000.",
        "options": [("$4,500", False), ("$5,000", True), ("$5,500", False), ("$6,000", False)],
    },
    {
        "topic": "Simple & Compound Interest", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "At what rate percent per annum simple interest will a sum become 7/4 of itself in 5 years?",
        "explanation": "Amount = 7P/4 => SI = 7P/4 - P = 3P/4. 3P/4 = (P * R * 5) / 100 => 3/4 = R / 20 => R = (3/4) * 20 = 15%.",
        "options": [("12%", False), ("14%", False), ("15%", True), ("18%", False)],
    },
    {
        "topic": "Simple & Compound Interest", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "A sum of $12,000 deposited at compound interest becomes double after 5 years. After 20 years, it will become:",
        "explanation": "20 years = 4 cycles of 5 years. Value = 12000 * 2^4 = 12000 * 16 = $192,000.",
        "options": [("$96,000", False), ("$120,000", False), ("$144,000", False), ("$192,000", True)],
    },
    {
        "topic": "Simple & Compound Interest", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "Find compound interest on $16,000 for 1.5 years at 10% per annum compounded half-yearly.",
        "explanation": "Rate per half-year = 5%, Period = 3 half-years. Amount = 16000 * (1.05)^3 = 16000 * 1.157625 = $18,522. CI = 18522 - 16000 = $2,522.",
        "options": [("$2,400", False), ("$2,522", True), ("$2,640", False), ("$2,720", False)],
    },
    {
        "topic": "Simple & Compound Interest", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "The compound interest on a certain sum for 2 successive years are $225 and $240 respectively. What is the annual rate of interest?",
        "explanation": "Interest on $225 for 1 year = 240 - 225 = $15. Rate = (15 / 225) * 100 = 6.67% (6 2/3%).",
        "options": [("5%", False), ("6.25%", False), ("6.67%", True), ("7.5%", False)],
    },
    {
        "topic": "Simple & Compound Interest", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "A sum of money amounts to $6,690 after 3 years and $10,035 after 6 years on compound interest. Find the sum.",
        "explanation": "A3 / P = (1 + r)^3 and A6 / A3 = (1 + r)^3 = 10035 / 6690 = 1.5. Thus P = A3 / 1.5 = 6690 / 1.5 = $4,460.",
        "options": [("$4,200", False), ("$4,460", True), ("$4,550", False), ("$4,800", False)],
    },
    {
        "topic": "Simple & Compound Interest", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "The difference between CI and SI on a certain sum for 3 years at 10% per annum is $93. Find the principal.",
        "explanation": "For 3 years, CI - SI = P * (R/100)^2 * (3 + R/100) = P * (1/100) * (3.10) = 0.031P. 0.031P = 93 => P = 93 / 0.031 = $3,000.",
        "options": [("$2,500", False), ("$3,000", True), ("$3,500", False), ("$4,000", False)],
    },
    {
        "topic": "Simple & Compound Interest", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "A person borrows $20,000 at 10% CI compounded annually and pays back $11,000 at the end of the first year. How much should he pay at the end of the second year to clear the debt?",
        "explanation": "After 1 year, amount = 20000 * 1.10 = $22,000. Balance remaining = 22000 - 11000 = $11,000. After 2nd year, amount = 11000 * 1.10 = $12,100.",
        "options": [("$11,500", False), ("$12,000", False), ("$12,100", True), ("$12,500", False)],
    },

    # ═══════════════════════════════════════════════════════════════
    # TIME & WORK (20 Questions)
    # ═══════════════════════════════════════════════════════════════
    {
        "topic": "Time & Work", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "A can do a work in 10 days and B can do it in 15 days. How many days will they take working together?",
        "explanation": "Combined rate = 1/10 + 1/15 = (3 + 2)/30 = 5/30 = 1/6. Days taken = 6 days.",
        "options": [("5 days", False), ("6 days", True), ("7.5 days", False), ("8 days", False)],
    },
    {
        "topic": "Time & Work", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "If 12 men can build a wall in 8 days, how many men are required to build the same wall in 6 days?",
        "explanation": "M1 * D1 = M2 * D2 => 12 * 8 = M2 * 6 => M2 = 96 / 6 = 16 men.",
        "options": [("14", False), ("15", False), ("16", True), ("18", False)],
    },
    {
        "topic": "Time & Work", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "Pipe A fills a tank in 6 hours and Pipe B empties it in 8 hours. If both pipes are opened, in how many hours will the tank be full?",
        "explanation": "Net rate = 1/6 - 1/8 = (4 - 3)/24 = 1/24. Time taken = 24 hours.",
        "options": [("18 hours", False), ("20 hours", False), ("24 hours", True), ("28 hours", False)],
    },
    {
        "topic": "Time & Work", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "A is twice as good a workman as B and together they finish a piece of work in 18 days. In how many days will A alone finish the work?",
        "explanation": "Ratio of efficiency A:B = 2:1. Combined rate = 3 units/day. Total work = 3 * 18 = 54 units. Time for A alone = 54 / 2 = 27 days.",
        "options": [("24 days", False), ("27 days", True), ("30 days", False), ("36 days", False)],
    },
    {
        "topic": "Time & Work", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "A can finish a task in 12 days and B in 24 days. If they work together for 4 days, what fraction of work is left?",
        "explanation": "Combined rate = 1/12 + 1/24 = 3/24 = 1/8. In 4 days, they complete 4 * (1/8) = 1/2. Remaining = 1 - 1/2 = 1/2.",
        "options": [("1/3", False), ("1/2", True), ("3/8", False), ("5/8", False)],
    },
    {
        "topic": "Time & Work", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "A and B can do a work in 12 days, B and C in 15 days, and C and A in 20 days. In how many days can all three together finish it?",
        "explanation": "2(A + B + C) = 1/12 + 1/15 + 1/20 = (5 + 4 + 3)/60 = 12/60 = 1/5 => A + B + C = 1/10. Days = 10 days.",
        "options": [("8 days", False), ("10 days", True), ("12 days", False), ("14 days", False)],
    },
    {
        "topic": "Time & Work", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "A can do a work in 20 days and B in 30 days. They work together for 5 days and then A leaves. How long will B take to complete the remaining work?",
        "explanation": "In 5 days, work done = 5 * (1/20 + 1/30) = 5 * (5/60) = 25/60 = 5/12. Remaining work = 7/12. Time for B = (7/12) / (1/30) = (7 * 30) / 12 = 17.5 days.",
        "options": [("15 days", False), ("16.5 days", False), ("17.5 days", True), ("20 days", False)],
    },
    {
        "topic": "Time & Work", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "Three pipes A, B, and C can fill a cistern in 6 hours. After 2 hours together, C is closed and A and B fill the remaining part in 7 hours. In how many hours can C alone fill the cistern?",
        "explanation": "In 2 hours, A+B+C fill 2/6 = 1/3. Remaining 2/3 filled by A+B in 7 hrs => (A+B) rate = (2/3)/7 = 2/21. C's rate = (1/6) - (2/21) = (7 - 4)/42 = 3/42 = 1/14. Time for C = 14 hours.",
        "options": [("12 hours", False), ("14 hours", True), ("16 hours", False), ("18 hours", False)],
    },
    {
        "topic": "Time & Work", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "If 10 men or 20 women or 40 children can do a piece of work in 7 months, then 5 men, 5 women, and 5 children together can do half the work in:",
        "explanation": "1 man = 4 children, 1 woman = 2 children. Total group = 5(4) + 5(2) + 5 = 20 + 10 + 5 = 35 children. 40 children do 1 work in 7 months => 40*7 = 280 child-months. Half work = 140 child-months. Months = 140 / 35 = 4 months.",
        "options": [("2 months", False), ("3 months", False), ("4 months", True), ("5 months", False)],
    },
    {
        "topic": "Time & Work", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "A and B can do a piece of work in 45 and 40 days respectively. They began the work together, but A leaves after some days and B finished the remaining work in 23 days. After how many days did A leave?",
        "explanation": "Work done by B in 23 days = 23 / 40. Work done together = 1 - 23/40 = 17/40. Combined rate = 1/45 + 1/40 = (8 + 9)/360 = 17/360. Days together = (17/40) / (17/360) = 360 / 40 = 9 days.",
        "options": [("8 days", False), ("9 days", True), ("10 days", False), ("12 days", False)],
    },
    {
        "topic": "Time & Work", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "A, B, and C can do a work in 20, 30, and 60 days respectively. In how many days can A do the work if he is assisted by B and C on every third day?",
        "explanation": "Day 1: A does 1/20. Day 2: A does 1/20. Day 3: A+B+C do 1/20 + 1/30 + 1/60 = (3+2+1)/60 = 6/60 = 1/10. Work in 3 days = 1/20 + 1/20 + 1/10 = 2/10 = 1/5. To complete 1 whole work: 5 cycles of 3 days = 15 days.",
        "options": [("12 days", False), ("15 days", True), ("16 days", False), ("18 days", False)],
    },
    {
        "topic": "Time & Work", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "A and B together can complete a work in 12 days. A alone works for 8 days and B completes the remaining work in 20 days. How many days would B alone take to complete the entire work?",
        "explanation": "8 days of A + 20 days of B = 1 => 8(A + B) + 12B = 1. Since A + B = 1/12: 8(1/12) + 12B = 1 => 2/3 + 12B = 1 => 12B = 1/3 => B = 1/36. B alone takes 36 days.",
        "options": [("28 days", False), ("32 days", False), ("36 days", True), ("40 days", False)],
    },
    {
        "topic": "Time & Work", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "Two pipes can fill a tank in 20 and 24 minutes respectively and a waste pipe can empty 3 gallons per minute. All three pipes together can fill the tank in 15 minutes. The capacity of the tank is:",
        "explanation": "Waste pipe rate = 1/20 + 1/24 - 1/15 = (6 + 5 - 8)/120 = 3/120 = 1/40 per min. Empties tank in 40 mins. Capacity = 40 mins * 3 gallons/min = 120 gallons.",
        "options": [("100 gallons", False), ("120 gallons", True), ("140 gallons", False), ("160 gallons", False)],
    },
    {
        "topic": "Time & Work", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "A is 30% more efficient than B. How much time will they, working together, take to complete a job which A alone could have done in 23 days?",
        "explanation": "Efficiency A:B = 130:100 = 13:10. Total work = 13 * 23 = 299 units. Combined efficiency = 13 + 10 = 23 units/day. Time = 299 / 23 = 13 days.",
        "options": [("11 days", False), ("12 days", False), ("13 days", True), ("15 days", False)],
    },
    {
        "topic": "Time & Work", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "4 men and 6 women can complete a work in 8 days, while 3 men and 7 women can complete it in 10 days. In how many days will 10 women complete it?",
        "explanation": "8(4m + 6w) = 10(3m + 7w) => 32m + 48w = 30m + 70w => 2m = 22w => 1m = 11w. Total work = 8(4*11w + 6w) = 8(50w) = 400 woman-days. 10 women will take 400 / 10 = 40 days.",
        "options": [("35 days", False), ("40 days", True), ("45 days", False), ("50 days", False)],
    },

    # ═══════════════════════════════════════════════════════════════
    # SPEED, DISTANCE & TIME (20 Questions)
    # ═══════════════════════════════════════════════════════════════
    {
        "topic": "Speed, Distance & Time", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "Convert a speed of 54 km/h to meters per second.",
        "explanation": "Multiply by 5/18: 54 * (5/18) = 3 * 5 = 15 m/s.",
        "options": [("12 m/s", False), ("15 m/s", True), ("18 m/s", False), ("20 m/s", False)],
    },
    {
        "topic": "Speed, Distance & Time", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "A car travels 180 km in 3 hours. What is its speed in km/h?",
        "explanation": "Speed = Distance / Time = 180 / 3 = 60 km/h.",
        "options": [("55 km/h", False), ("60 km/h", True), ("65 km/h", False), ("70 km/h", False)],
    },
    {
        "topic": "Speed, Distance & Time", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "A train 120 meters long passes a telephone post in 6 seconds. What is the speed of the train in km/h?",
        "explanation": "Speed = 120 / 6 = 20 m/s. In km/h: 20 * (18/5) = 72 km/h.",
        "options": [("60 km/h", False), ("68 km/h", False), ("72 km/h", True), ("80 km/h", False)],
    },
    {
        "topic": "Speed, Distance & Time", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "A man covers a distance of 600m in 5 minutes. What is his speed in km/h?",
        "explanation": "Time = 5 * 60 = 300 sec. Speed = 600 / 300 = 2 m/s. In km/h: 2 * (18/5) = 7.2 km/h.",
        "options": [("6.5 km/h", False), ("7.2 km/h", True), ("8.0 km/h", False), ("8.4 km/h", False)],
    },
    {
        "topic": "Speed, Distance & Time", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "A person walks at 5 km/h for 2 hours and runs at 10 km/h for 1 hour. What is his average speed?",
        "explanation": "Total distance = (5 * 2) + (10 * 1) = 10 + 10 = 20 km. Total time = 3 hours. Average speed = 20 / 3 = 6.67 km/h.",
        "options": [("6.0 km/h", False), ("6.67 km/h", True), ("7.5 km/h", False), ("8.0 km/h", False)],
    },
    {
        "topic": "Speed, Distance & Time", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "A train 150m long is running at 68 km/h. In what time will it pass a man running at 8 km/h in the same direction?",
        "explanation": "Relative speed = 68 - 8 = 60 km/h = 60 * (5/18) = 50/3 m/s. Time = Distance / Relative Speed = 150 / (50/3) = (150 * 3) / 50 = 9 seconds.",
        "options": [("8 seconds", False), ("9 seconds", True), ("10 seconds", False), ("12 seconds", False)],
    },
    {
        "topic": "Speed, Distance & Time", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "A car travels from A to B at 40 km/h and returns from B to A at 60 km/h. What is the average speed for the whole journey?",
        "explanation": "Average speed for equal distances = 2xy / (x + y) = (2 * 40 * 60) / (40 + 60) = 4800 / 100 = 48 km/h.",
        "options": [("45 km/h", False), ("48 km/h", True), ("50 km/h", False), ("52 km/h", False)],
    },
    {
        "topic": "Speed, Distance & Time", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "A boat can travel with a speed of 13 km/h in still water. If the speed of the stream is 4 km/h, find the time taken by the boat to go 68 km downstream.",
        "explanation": "Downstream speed = 13 + 4 = 17 km/h. Time = 68 / 17 = 4 hours.",
        "options": [("3 hours", False), ("3.5 hours", False), ("4 hours", True), ("4.5 hours", False)],
    },
    {
        "topic": "Speed, Distance & Time", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "Two trains of length 140m and 160m are running in opposite directions on parallel lines at 40 km/h and 50 km/h. In what time will they cross each other?",
        "explanation": "Total distance = 140 + 160 = 300m. Relative speed = 40 + 50 = 90 km/h = 90 * (5/18) = 25 m/s. Time = 300 / 25 = 12 seconds.",
        "options": [("10 seconds", False), ("12 seconds", True), ("14 seconds", False), ("16 seconds", False)],
    },
    {
        "topic": "Speed, Distance & Time", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "Walking at 3/4 of his normal speed, a person is 20 minutes late to his office. What is his usual time to reach the office?",
        "explanation": "Speed ratio = 3/4 => Time ratio = 4/3 of normal. Extra time = 4/3 T - T = T/3 = 20 mins => Normal time T = 60 minutes = 1 hour.",
        "options": [("45 minutes", False), ("50 minutes", False), ("60 minutes", True), ("75 minutes", False)],
    },
    {
        "topic": "Speed, Distance & Time", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "A man covers a certain distance between his house and office on a scooter. With an average speed of 30 km/h, he is late by 10 min. However, with a speed of 40 km/h, he reaches 5 min earlier. Find the distance.",
        "explanation": "Difference in time = 10 - (-5) = 15 mins = 1/4 hour. Distance D = (S1 * S2 * Delta_T) / |S1 - S2| = (30 * 40 * (1/4)) / 10 = 300 / 10 = 30 km.",
        "options": [("25 km", False), ("28 km", False), ("30 km", True), ("35 km", False)],
    },
    {
        "topic": "Speed, Distance & Time", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "A thief steals a car at 1:30 PM and drives it at 40 km/h. The theft is discovered at 2:00 PM and the owner sets off in another car at 50 km/h. At what time will he overtake the thief?",
        "explanation": "Lead of thief in 30 mins = 40 * 0.5 = 20 km. Relative speed = 50 - 40 = 10 km/h. Time to overtake = 20 / 10 = 2 hours after 2:00 PM = 4:00 PM.",
        "options": [("3:30 PM", False), ("3:45 PM", False), ("4:00 PM", True), ("4:30 PM", False)],
    },
    {
        "topic": "Speed, Distance & Time", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "A boat takes 90 minutes less to travel 36 miles downstream than to travel the same distance upstream. If the speed of the boat in still water is 10 mph, find the speed of the stream.",
        "explanation": "36 / (10 - c) - 36 / (10 + c) = 1.5 => 36 * 2c / (100 - c^2) = 1.5 => 72c = 1.5(100 - c^2) => 48c = 100 - c^2 => c^2 + 48c - 100 = 0 => (c + 50)(c - 2) = 0 => c = 2 mph.",
        "options": [("1.5 mph", False), ("2 mph", True), ("2.5 mph", False), ("3 mph", False)],
    },
    {
        "topic": "Speed, Distance & Time", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "Two stations A and B are 110 km apart on a straight line. One train starts from A at 7 AM and travels towards B at 20 km/h. Another starts from B at 8 AM towards A at 25 km/h. At what time will they meet?",
        "explanation": "In 1 hour (7 to 8 AM), train from A travels 20 km. Remaining distance at 8 AM = 110 - 20 = 90 km. Relative speed = 20 + 25 = 45 km/h. Time to meet = 90 / 45 = 2 hours after 8 AM = 10:00 AM.",
        "options": [("9:30 AM", False), ("10:00 AM", True), ("10:30 AM", False), ("11:00 AM", False)],
    },
    {
        "topic": "Speed, Distance & Time", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "In a 100m race, A can beat B by 25m and B can beat C by 4m. In the same race, by how many meters can A beat C?",
        "explanation": "When A runs 100m, B runs 75m. When B runs 100m, C runs 96m => when B runs 75m, C runs (96/100) * 75 = 72m. When A runs 100m, C runs 72m. A beats C by 100 - 72 = 28m.",
        "options": [("26m", False), ("28m", True), ("29m", False), ("30m", False)],
    },

    # ═══════════════════════════════════════════════════════════════
    # NUMBER SYSTEM (20 Questions)
    # ═══════════════════════════════════════════════════════════════
    {
        "topic": "Number System", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "Which of the following numbers is divisible by 9?",
        "explanation": "A number is divisible by 9 if the sum of its digits is divisible by 9. For 54936: 5+4+9+3+6 = 27 (divisible by 9).",
        "options": [("54932", False), ("54936", True), ("54938", False), ("54940", False)],
    },
    {
        "topic": "Number System", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "What is the unit digit in the product 784 * 618 * 917 * 463?",
        "explanation": "Multiply unit digits: 4 * 8 = 32 (unit 2); 2 * 7 = 14 (unit 4); 4 * 3 = 12 (unit 2). Unit digit is 2.",
        "options": [("2", True), ("4", False), ("6", False), ("8", False)],
    },
    {
        "topic": "Number System", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "The HCF of two numbers is 11 and their LCM is 7700. If one of the numbers is 275, find the other number.",
        "explanation": "Product of two numbers = HCF * LCM => 275 * N = 11 * 7700 => N = (11 * 7700) / 275 = 308.",
        "options": [("280", False), ("308", True), ("315", False), ("320", False)],
    },
    {
        "topic": "Number System", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "What is the smallest prime number greater than 50?",
        "explanation": "51 = 3*17, 52 is even, 53 has no divisors other than 1 and 53. So 53 is prime.",
        "options": [("51", False), ("53", True), ("57", False), ("59", False)],
    },
    {
        "topic": "Number System", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "The sum of three consecutive odd numbers is 57. What is the middle number?",
        "explanation": "Middle number = Sum / 3 = 57 / 3 = 19.",
        "options": [("17", False), ("19", True), ("21", False), ("23", False)],
    },
    {
        "topic": "Number System", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "What is the unit digit of 7^105?",
        "explanation": "Powers of 7 cycle with period 4: 7^1=7, 7^2=9, 7^3=3, 7^4=1. 105 mod 4 = 1. So unit digit = 7.",
        "options": [("1", False), ("3", False), ("7", True), ("9", False)],
    },
    {
        "topic": "Number System", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "What is the remainder when (67^67 + 67) is divided by 68?",
        "explanation": "67 mod 68 = -1. (-1)^67 + 67 = -1 + 67 = 66. So the remainder is 66.",
        "options": [("1", False), ("66", True), ("67", False), ("68", False)],
    },
    {
        "topic": "Number System", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "Find the least number which when divided by 6, 9, 15, and 18 leaves remainder 4 in each case.",
        "explanation": "LCM(6, 9, 15, 18) = 90. Required number = LCM + remainder = 90 + 4 = 94.",
        "options": [("84", False), ("90", False), ("94", True), ("98", False)],
    },
    {
        "topic": "Number System", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "How many trailing zeros does 100! (100 factorial) have?",
        "explanation": "Number of zeros = floor(100/5) + floor(100/25) = 20 + 4 = 24 zeros.",
        "options": [("20", False), ("22", False), ("24", True), ("25", False)],
    },
    {
        "topic": "Number System", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "If the number 97215*6 is completely divisible by 11, what is the smallest digit in place of *?",
        "explanation": "Sum of odd positions: 6 + 5 + 2 + 9 = 22. Sum of even positions: * + 1 + 7 = 8 + *. Difference = 22 - (8 + *) = 14 - *. For divisibility by 11, 14 - * = 11 => * = 3.",
        "options": [("2", False), ("3", True), ("5", False), ("7", False)],
    },
    {
        "topic": "Number System", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "Find the total number of positive factors/divisors of 360.",
        "explanation": "360 = 2^3 * 3^2 * 5^1. Number of factors = (3 + 1)(2 + 1)(1 + 1) = 4 * 3 * 2 = 24.",
        "options": [("18", False), ("20", False), ("24", True), ("28", False)],
    },
    {
        "topic": "Number System", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "What is the remainder when 2^100 is divided by 7?",
        "explanation": "2^3 = 8 = 1 mod 7. 100 = 3 * 33 + 1. 2^100 = (2^3)^33 * 2^1 = 1^33 * 2 = 2 mod 7. Remainder = 2.",
        "options": [("1", False), ("2", True), ("4", False), ("6", False)],
    },
    {
        "topic": "Number System", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "Find the largest 4-digit number which is exactly divisible by 12, 15, 18, and 27.",
        "explanation": "LCM(12, 15, 18, 27) = 540. Largest 4-digit number = 9999. 9999 / 540 = 18 with remainder 279. 9999 - 279 = 9,720.",
        "options": [("9,680", False), ("9,720", True), ("9,760", False), ("9,820", False)],
    },
    {
        "topic": "Number System", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "A number when divided successively by 4 and 5 leaves remainders 1 and 4 respectively. When it is successively divided by 5 and 4, the respective remainders will be:",
        "explanation": "Smallest such number: N = 4 * (5k + 4) + 1. For k=1, N = 4(9) + 1 = 37. 37 divided by 5 gives quotient 7, remainder 2. 7 divided by 4 gives quotient 1, remainder 3. Respective remainders are 2 and 3.",
        "options": [("1 and 2", False), ("2 and 3", True), ("3 and 2", False), ("4 and 1", False)],
    },
    {
        "topic": "Number System", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "What is the sum of all two-digit numbers which leave a remainder of 1 when divided by 3?",
        "explanation": "Sequence: 10, 13, 16, ..., 97. First term a=10, last l=97, d=3. 97 = 10 + (n-1)*3 => 87 = 3(n-1) => n-1 = 29 => n = 30. Sum = (30/2) * (10 + 97) = 15 * 107 = 1,605.",
        "options": [("1,580", False), ("1,605", True), ("1,635", False), ("1,680", False)],
    },

    # ═══════════════════════════════════════════════════════════════
    # PERMUTATION, COMBINATION & PROBABILITY (15 Questions)
    # ═══════════════════════════════════════════════════════════════
    {
        "topic": "Permutation & Combination", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "In how many different ways can the letters of the word 'APPLE' be arranged?",
        "explanation": "5 letters with 'P' repeated twice: 5! / 2! = 120 / 2 = 60 ways.",
        "options": [("50", False), ("60", True), ("100", False), ("120", False)],
    },
    {
        "topic": "Permutation & Combination", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "From a group of 7 men and 6 women, 5 persons are to be selected. How many ways can this be done if order does not matter?",
        "explanation": "Total persons = 13. Number of selections = 13C5 = (13*12*11*10*9) / (5*4*3*2*1) = 1,287.",
        "options": [("1,144", False), ("1,287", True), ("1,360", False), ("1,420", False)],
    },
    {
        "topic": "Permutation & Combination", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "How many words can be formed from the letters of the word 'TRIANGLE' such that vowels always remain together?",
        "explanation": "Vowels: I, A, E (3). Consonants: T, R, N, G, L (5). Treat vowels as 1 block => 6 units arranged in 6! ways. Vowels arranged internally in 3! ways. Total = 6! * 3! = 720 * 6 = 4,320.",
        "options": [("3,600", False), ("4,320", True), ("5,040", False), ("7,200", False)],
    },
    {
        "topic": "Permutation & Combination", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "In how many ways can 6 people be seated around a circular table?",
        "explanation": "Circular permutations of n items = (n - 1)! = (6 - 1)! = 5! = 120 ways.",
        "options": [("60", False), ("120", True), ("360", False), ("720", False)],
    },
    {
        "topic": "Permutation & Combination", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "Out of 5 engineers and 4 doctors, a committee of 4 members is to be formed such that it contains at least 2 doctors. How many such committees are possible?",
        "explanation": "Cases: (2D, 2E): 4C2 * 5C2 = 6 * 10 = 60. (3D, 1E): 4C3 * 5C1 = 4 * 5 = 20. (4D, 0E): 4C4 * 5C0 = 1 * 1 = 1. Total = 60 + 20 + 1 = 81 committees.",
        "options": [("75", False), ("80", False), ("81", True), ("85", False)],
    },
    {
        "topic": "Probability", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "A fair die is rolled once. What is the probability of obtaining an even number?",
        "explanation": "Even numbers: 2, 4, 6 (3 outcomes). Total = 6. Probability = 3 / 6 = 1/2.",
        "options": [("1/3", False), ("1/2", True), ("2/3", False), ("3/4", False)],
    },
    {
        "topic": "Probability", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "A card is drawn from a well-shuffled pack of 52 cards. What is the probability of drawing a face card (Jack, Queen, King)?",
        "explanation": "There are 4 suits * 3 face cards = 12 face cards. P = 12 / 52 = 3/13.",
        "options": [("1/13", False), ("2/13", False), ("3/13", True), ("4/13", False)],
    },
    {
        "topic": "Probability", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "Two dice are thrown simultaneously. What is the probability of getting a sum equal to 8?",
        "explanation": "Pairs giving 8: (2,6), (3,5), (4,4), (5,3), (6,2) -> 5 outcomes. Total = 36. Probability = 5/36.",
        "options": [("1/6", False), ("5/36", True), ("7/36", False), ("1/9", False)],
    },
    {
        "topic": "Probability", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "A bag contains 4 red, 5 blue, and 3 green marbles. If 2 marbles are drawn at random without replacement, what is the probability that both are blue?",
        "explanation": "Total = 12 marbles. P(both blue) = (5C2) / (12C2) = 10 / 66 = 5/33.",
        "options": [("5/33", True), ("7/33", False), ("5/66", False), ("1/6", False)],
    },
    {
        "topic": "Probability", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "A problem is given to three students whose chances of solving it are 1/2, 1/3, and 1/4. What is the probability that the problem will be solved?",
        "explanation": "P(solved) = 1 - P(none solves) = 1 - (1 - 1/2)(1 - 1/3)(1 - 1/4) = 1 - (1/2 * 2/3 * 3/4) = 1 - 1/4 = 3/4.",
        "options": [("1/2", False), ("2/3", False), ("3/4", True), ("5/6", False)],
    },

    # ═══════════════════════════════════════════════════════════════
    # DATA INTERPRETATION & AGES & MIXTURES (15 Questions)
    # ═══════════════════════════════════════════════════════════════
    {
        "topic": "Data Interpretation", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "In a pie chart, a sector represents expenses of 25%. What is the central angle corresponding to this sector?",
        "explanation": "Angle = 25% of 360° = 0.25 * 360° = 90°.",
        "options": [("72°", False), ("80°", False), ("90°", True), ("100°", False)],
    },
    {
        "topic": "Data Interpretation", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "In a company, production rose from 40,000 units in 2021 to 52,000 units in 2022. What was the percentage growth rate?",
        "explanation": "Growth = 52,000 - 40,000 = 12,000. Growth% = (12,000 / 40,000) * 100 = 30%.",
        "options": [("25%", False), ("28%", False), ("30%", True), ("35%", False)],
    },
    {
        "topic": "Data Interpretation", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "In a sales chart, Division A's revenue is 40% of total company revenue ($2,500,000) and its operating margin is 18%. What is Division A's operating profit?",
        "explanation": "Division A revenue = 40% of 2,500,000 = $1,000,000. Profit = 18% of 1,000,000 = $180,000.",
        "options": [("$150,000", False), ("$165,000", False), ("$180,000", True), ("$200,000", False)],
    },
    {
        "topic": "Ages & Mixtures", "difficulty": DifficultyLevel.EASY, "irt": -1.2,
        "text": "The ratio of present ages of father and son is 5:2. If the father is 35 years old, what is the son's age?",
        "explanation": "5 units = 35 => 1 unit = 7. Son's age = 2 * 7 = 14 years.",
        "options": [("12 years", False), ("14 years", True), ("16 years", False), ("18 years", False)],
    },
    {
        "topic": "Ages & Mixtures", "difficulty": DifficultyLevel.MEDIUM, "irt": 0.0,
        "text": "10 years ago, A was half of B in age. If the ratio of their present ages is 3:4, what is the total of their present ages?",
        "explanation": "Present ages: 3x and 4x. (3x - 10) / (4x - 10) = 1 / 2 => 6x - 20 = 4x - 10 => 2x = 10 => x = 5. Ages are 15 and 20. Sum = 15 + 20 = 35 years.",
        "options": [("30 years", False), ("35 years", True), ("40 years", False), ("45 years", False)],
    },
    {
        "topic": "Ages & Mixtures", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "In what ratio must tea at $62 per kg be mixed with tea at $72 per kg so that the mixture must be worth $64.50 per kg?",
        "explanation": "By alligation: (72 - 64.50) / (64.50 - 62) = 7.50 / 2.50 = 3 / 1 = 3:1.",
        "options": [("2:1", False), ("3:1", True), ("3:2", False), ("4:3", False)],
    },
    {
        "topic": "Ages & Mixtures", "difficulty": DifficultyLevel.HARD, "irt": 1.4,
        "text": "A container contains 40 liters of milk. From this container, 4 liters of milk were taken out and replaced by water. This process was repeated further two times. How much milk is now contained by the container?",
        "explanation": "Formula: Amount = Initial * (1 - x/C)^n = 40 * (1 - 4/40)^3 = 40 * (9/10)^3 = 40 * (729/1000) = 29.16 liters.",
        "options": [("28.00 liters", False), ("29.16 liters", True), ("30.24 liters", False), ("31.50 liters", False)],
    },
]
