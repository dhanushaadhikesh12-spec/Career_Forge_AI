"""
Fast Zero-LLM Student Intent Classifier.
Categorizes student queries BEFORE calling the database or Gemma.
Skips PostgreSQL & tool calls for greetings and pure conceptual/educational questions.
Enables ~1-2s latency on conversational queries.
"""
from __future__ import annotations
import re
import logging
from enum import Enum
from typing import Tuple, Dict, Any, Optional

logger = logging.getLogger(__name__)


class StudentQueryIntent(str, Enum):
    GENERAL_CHAT = "general_chat"
    GENERAL_LEARNING = "general_learning"
    PERSONAL_PERFORMANCE = "personal_performance"
    WEAK_TOPICS = "weak_topics"
    STRONG_TOPICS = "strong_topics"
    READINESS = "readiness"
    RECOMMENDATION = "recommendation"
    STUDY_PLAN = "study_plan"
    PRACTICE = "practice"
    CODING_PERFORMANCE = "coding_performance"
    QUESTION_EXPLANATION = "question_explanation"
    DATA_QUERY = "data_query"


# ─────────────────────────────────────────────────────────────────────────────
# Regex Patterns
# ─────────────────────────────────────────────────────────────────────────────

# Pure greeting / pleasantries / identity
_GREETING_PATTERNS = [
    r"^(hi|hello|hey|greetings|howdy|yo)(\b|[!.,\s])",
    r"^good (morning|afternoon|evening|day)\b",
    r"^how are you\b",
    r"^what('s| is) up\b",
    r"^thank(s| you)\b",
    r"^(bye|goodbye|see you)\b",
    r"\bwho are you\b",
    r"\bwhat can you do\b",
    r"\bwhat is your name\b",
]

# Conceptual / educational definitions (not asking about personal student data)
_GENERAL_LEARNING_PATTERNS = [
    r"\bwhat is (a |an )?(binary search|quicksort|mergesort|linked list|stack|queue|hash table|tree|graph|heap|trie|dynamic programming|greedy|recursion|bfs|dfs|oop|polymorphism|inheritance|encapsulation|abstraction|interface|abstract class|database normalization|sql join|acid|deadlock|thread|process|rest api|http|tcp|udp|pointer|memory leak|big.?o|time complexity|space complexity)\b",
    r"\b(teach|explain)\b.*(binary search|quicksort|mergesort|linked list|stack|queue|hash table|tree|graph|dynamic programming|recursion|bfs|dfs|oop|polymorphism|inheritance|encapsulation|abstraction|interface|abstract class|sql join|rest api|time complexity)",
    r"\bdifference between\b",
    r"\bhow does\b.*(binary search|quicksort|mergesort|linked list|stack|queue|hash table|recursion|dynamic programming|sql join)\b",
    r"\bcan you explain (how|what|why)\b",
]

# Readiness
_READINESS_PATTERNS = [
    r"\bread(y|iness)\b",
    r"\bplacement ready\b",
    r"\bam i ready\b",
    r"\bchance of placement\b",
    r"\bpredict.*readiness\b",
    r"\bwhat.*readiness\b",
    r"\bwill i get (placed|a job)\b",
]

# Weak topics
_WEAK_PATTERNS = [
    r"\bweak(est|ness|nesses|er)?\b",
    r"\bstruggl(ing|e|es)\b",
    r"\bwhere am i (lagging|behind|failing|lacking)\b",
    r"\bworst topic(s)?\b",
    r"\blowest score(s)?\b",
    r"\bneed(s)? improvement\b",
    r"\bare(as)? for improvement\b",
]

# Strong topics
_STRONG_PATTERNS = [
    r"\bstrong(est)?\b",
    r"\bmaster(ed|y)?\b",
    r"\bwhat am i (good|best) at\b",
    r"\btop topic(s)?\b",
    r"\bhighest score(s)?\b",
    r"\bmy strengths\b",
]

# Study plan
_STUDY_PLAN_PATTERNS = [
    r"\bstudy plan\b",
    r"\b(day|week|month) plan\b",
    r"\b(7|14|30).?day\b",
    r"\bpreparation plan\b",
    r"\bhow should i prepare\b",
    r"\bmake me a plan\b",
    r"\brodmap\b",
    r"\broadmap\b",
    r"\bschedule\b",
    r"\btimetable\b",
    r"\bweeks before placement\b",
]

# Practice request
_PRACTICE_PATTERNS = [
    r"\bgive me (some |\d+ )?(question|problem|mcq)(s)?\b",
    r"\bpractice (some |\d+ )?(question|problem)(s)?\b",
    r"\btest me on\b",
    r"\bquiz me on\b",
    r"\bpractice my weak\b",
    r"\bgive me practice\b",
    r"\b5 questions\b",
    r"\b10 questions\b",
]

# Coding performance
_CODING_PATTERNS = [
    r"\bhow.*(in |at )coding\b",
    r"\bcoding performance\b",
    r"\bcoding (score|accuracy|stats|pass rate|problems)\b",
    r"\balgorithm(ic)? performance\b",
    r"\bleetcode\b",
    r"\bcode submissions\b",
    r"\bmy coding\b",
]

# Question explanation / why wrong
_QUESTION_EXPLANATION_PATTERNS = [
    r"\bwhy (is|was) (my |this )?answer wrong\b",
    r"\bwhy did i get this wrong\b",
    r"\bexplain this question\b",
    r"\bwhy (is|was) option\b",
    r"\bwhy is the correct answer\b",
    r"\bexplain my mistake\b",
]

# Recommendation / what to study today
_RECOMMENDATION_PATTERNS = [
    r"\bwhat should i study\b",
    r"\bwhat should i practice (today|next|now)\b",
    r"\bwhat to study (today|next|now)\b",
    r"\bwhat to practice (today|next|now)\b",
    r"\brecommend(ation|ations|ed)?\b",
    r"\bnext step(s)?\b",
    r"\bwhere to start\b",
]

# General personal performance
_PERFORMANCE_PATTERNS = [
    r"\bhow am i doing\b",
    r"\bhow am i performing\b",
    r"\bmy score(s)?\b",
    r"\bmy performance\b",
    r"\bmy accuracy\b",
    r"\bmy progress\b",
    r"\bam i improving\b",
    r"\boverall stats\b",
    r"\bmy stats\b",
    r"\bperformance overview\b",
    r"\banalyze my performance\b",
]


def classify_student_intent(
    query: str, has_question_context: bool = False
) -> StudentQueryIntent:
    """
    Classifies a student's prompt into a specific action intent.
    Deterministic, fast, zero network overhead.
    """
    clean_q = query.strip().lower()

    if has_question_context:
        for p in _QUESTION_EXPLANATION_PATTERNS:
            if re.search(p, clean_q, re.IGNORECASE):
                return StudentQueryIntent.QUESTION_EXPLANATION

    # 1. Greetings (fastest exit)
    for p in _GREETING_PATTERNS:
        if re.search(p, clean_q, re.IGNORECASE):
            return StudentQueryIntent.GENERAL_CHAT

    # 2. Question explanation
    for p in _QUESTION_EXPLANATION_PATTERNS:
        if re.search(p, clean_q, re.IGNORECASE):
            return StudentQueryIntent.QUESTION_EXPLANATION

    # 3. Practice requests
    for p in _PRACTICE_PATTERNS:
        if re.search(p, clean_q, re.IGNORECASE):
            return StudentQueryIntent.PRACTICE

    # 4. Study plan
    for p in _STUDY_PLAN_PATTERNS:
        if re.search(p, clean_q, re.IGNORECASE):
            return StudentQueryIntent.STUDY_PLAN

    # 5. Readiness
    for p in _READINESS_PATTERNS:
        if re.search(p, clean_q, re.IGNORECASE):
            return StudentQueryIntent.READINESS

    # 6. Weak topics
    for p in _WEAK_PATTERNS:
        if re.search(p, clean_q, re.IGNORECASE):
            return StudentQueryIntent.WEAK_TOPICS

    # 7. Strong topics
    for p in _STRONG_PATTERNS:
        if re.search(p, clean_q, re.IGNORECASE):
            return StudentQueryIntent.STRONG_TOPICS

    # 8. Recommendation
    for p in _RECOMMENDATION_PATTERNS:
        if re.search(p, clean_q, re.IGNORECASE):
            return StudentQueryIntent.RECOMMENDATION

    # 9. Coding performance
    for p in _CODING_PATTERNS:
        if re.search(p, clean_q, re.IGNORECASE):
            return StudentQueryIntent.CODING_PERFORMANCE

    # 10. General performance
    for p in _PERFORMANCE_PATTERNS:
        if re.search(p, clean_q, re.IGNORECASE):
            return StudentQueryIntent.PERSONAL_PERFORMANCE

    # 11. General learning (educational concept)
    for p in _GENERAL_LEARNING_PATTERNS:
        if re.search(p, clean_q, re.IGNORECASE):
            return StudentQueryIntent.GENERAL_LEARNING

    # Check if query contains personal pronouns ("i", "my", "me") with stats words
    has_self_ref = bool(re.search(r"\b(i|my|me|mine)\b", clean_q, re.IGNORECASE))
    if has_self_ref:
        return StudentQueryIntent.DATA_QUERY

    # If general question without self-reference, treat as educational learning
    if any(q_word in clean_q for q_word in ["what is", "how to", "explain", "why does", "difference", "define"]):
        return StudentQueryIntent.GENERAL_LEARNING

    # Fallback to general conversational or data query
    return StudentQueryIntent.GENERAL_CHAT if len(clean_q.split()) <= 4 else StudentQueryIntent.DATA_QUERY
