"""
AI Intent Classifier / Mode Router.

A lightweight, zero-LLM classifier that categorises incoming trainer queries
into one of two modes BEFORE the main pipeline runs:

  - CONVERSATIONAL: greetings, general education questions, small-talk
  - DATA_QUERY: analytics / student data questions that require a backend tool

By detecting CONVERSATIONAL intents early, we skip the expensive Ollama tool-call
round-trip entirely, reducing typical response time from ~8s → ~2s for simple
queries.

This classifier uses regex pattern matching and keyword heuristics only — no LLM,
no database access. It is intentionally conservative: if in doubt it classifies
as DATA_QUERY so the full pipeline always handles ambiguous queries correctly.
"""
from __future__ import annotations

import re
import logging
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Intent categories
# ─────────────────────────────────────────────────────────────────────────────

class QueryIntent(str, Enum):
    CONVERSATIONAL = "conversational"   # Can be answered without any tool
    DATA_QUERY     = "data_query"       # Must go through the full tool pipeline


# ─────────────────────────────────────────────────────────────────────────────
# Pattern banks
# ─────────────────────────────────────────────────────────────────────────────

# Strings that clearly indicate the trainer wants live student / batch data
_DATA_KEYWORDS: list[str] = [
    # Student / cohort references
    r"\bstudent(s)?\b", r"\bbatch\b", r"\bcohort\b", r"\bcandidate(s)?\b",
    r"\blearner(s)?\b", r"\btrainee(s)?\b",
    # Performance metrics & activity
    r"\bperform(ance|ing|ed|s)?\b", r"\bscore(s)?\b", r"\baccurac(y|ies)\b",
    r"\bprogress\b", r"\bimprovement\b", r"\btrend(s)?\b",
    r"\brank(ing|ed|s)?\b", r"\bleaderboard\b",
    r"\bdoing\b", r"\bfaring\b",
    # Superlatives & comparative
    r"\btop\b", r"\bbest\b", r"\bworst\b", r"\bhighest\b", r"\blowest\b",
    r"\bstrong(est)?\b", r"\bweak(est|er)?\b", r"\bpoor(ly)?\b",
    r"\bhelp\b", r"\battention\b", r"\bneed(s)?\b",
    # Outcome / placement
    r"\bplacement\b", r"\bread(y|iness)\b", r"\bright now\b", r"\btoday\b",
    r"\bcurrent\b", r"\blatest\b", r"\brecent\b", r"\blast (week|month)\b",
    # Risk / concern categories
    r"\bat.?risk\b", r"\bstruggling\b", r"\bbehind\b",
    r"\bfailing\b", r"\bbottom\b",
    # Topic / assessment analytics
    r"\btopic\b", r"\bsubject\b", r"\bapt(itude)?\b", r"\bdsa\b",
    r"\barray(s)?\b", r"\btree(s)?\b", r"\bgraph(s)?\b",
    r"\btest(s)?\b", r"\bassessment(s)?\b", r"\bexam(s)?\b", r"\bquiz(zes)?\b",
    r"\bcodng?\b", r"\bcoding\b", r"\bpass rate\b", r"\bfail rate\b",
    r"\bsubmission(s)?\b", r"\battempt(s)?\b",
    # Proctoring / malpractice
    r"\bmalpractic(e|es)\b", r"\bproctor(ing)?\b", r"\bviolation(s)?\b",
    r"\btab switch(es)?\b", r"\bcheating?\b", r"\bsuspicious\b",
    r"\banomaly\b", r"\banomalies\b",
    # Aggregates & identification
    r"\baverage\b", r"\bmean\b", r"\bmedian\b", r"\bdistribution\b",
    r"\bbreakdown\b", r"\bsummary\b", r"\boverview\b", r"\breport\b",
    r"\banalytics\b", r"\binsight(s)?\b", r"\bstatistic(s)?\b",
    r"\bwho\b", r"\bwhich\b", r"\bhow many\b",
    r"\bhow is \b", r"\bhow are \b",
    r"\blist\b", r"\bshow me\b", r"\bgive me\b", r"\btell me about\b",
    r"\bcompare\b",
]

# Strings that clearly indicate a CONVERSATIONAL / general-knowledge query
_CONVERSATIONAL_KEYWORDS: list[str] = [
    # Greetings / pleasantries
    r"^hi\b", r"^hello\b", r"^hey\b", r"^good (morning|afternoon|evening|day)\b",
    r"\bhow are you\b", r"\bwhat('s| is) up\b", r"\bhow('s| is) it going\b",
    r"\bthank(s| you)\b", r"\bthanks?\b", r"\bbye\b", r"\bgoodbye\b",
    r"\bsee you\b", r"\bnice to meet\b",
    # Identity / meta
    r"\bwho are you\b", r"\bwhat are you\b", r"\bwhat can you do\b",
    r"\byour name\b", r"\byour purpose\b", r"\bhow do you work\b",
    r"\bwhat (is|are) (your )?capabilities\b",
    # Pure educational definitions (no mention of *our* students)
    r"\bwhat is (a |an )?(elo|irt|k.?means|algorithm|data structure|sorting)\b",
    r"\bexplain (the )?(concept|algorithm|technique|method|approach|theory)\b",
    r"\bdefine\b.*\b(algorithm|complexity|recursion|dynamic programming|greedy)\b",
    r"\bhow does\b.*(algorithm|technique|method|sorting|searching|hashing)\b",
    r"\bdifference between\b",
    r"\bwhat is (big.?o|time complexity|space complexity)\b",
    r"\bcan you (help|assist|explain|clarify|describe)\b",
    # Tips / best practices (general, not data-dependent)
    r"\bbest practice(s)?\b.*\btraining\b",
    r"\bhow to (teach|improve|help) (students?|learners?|candidates?)\b",
    r"\btip(s)? for\b",
    r"\badvice\b",
    r"\bsuggestion(s)?\b",
    r"\bstrateg(y|ies) for\b",
    # Platform questions
    r"\bhow do i (use|navigate|access|view|check)\b",
    r"\bwhere (can i|do i)\b",
    r"\bfeature(s)?\b",
]

# Pre-compile patterns for speed
_DATA_PATTERNS     = [re.compile(p, re.IGNORECASE) for p in _DATA_KEYWORDS]
_CONV_PATTERNS     = [re.compile(p, re.IGNORECASE) for p in _CONVERSATIONAL_KEYWORDS]

# Very short queries (<= this many words) with no data keywords → conversational
_SHORT_QUERY_WORD_LIMIT = 6


# ─────────────────────────────────────────────────────────────────────────────
# Public classifier
# ─────────────────────────────────────────────────────────────────────────────

def classify_intent(query: str) -> QueryIntent:
    """
    Classify a trainer query as CONVERSATIONAL or DATA_QUERY.

    Rules (applied in order, first match wins):
    1. If any DATA keyword is found → DATA_QUERY (highest priority).
    2. If any CONVERSATIONAL keyword is found → CONVERSATIONAL.
    3. If query is very short (≤ N words) and no data keyword → CONVERSATIONAL.
    4. Default → DATA_QUERY (safe fallback).
    """
    q = query.strip()

    # Rule 1: data keyword takes precedence
    for pat in _DATA_PATTERNS:
        if pat.search(q):
            logger.debug("IntentClassifier: DATA_QUERY (matched '%s')", pat.pattern)
            return QueryIntent.DATA_QUERY

    # Rule 2: explicit conversational pattern
    for pat in _CONV_PATTERNS:
        if pat.search(q):
            logger.debug("IntentClassifier: CONVERSATIONAL (matched '%s')", pat.pattern)
            return QueryIntent.CONVERSATIONAL

    # Rule 3: very short queries with no data keywords are typically conversational
    word_count = len(q.split())
    if word_count <= _SHORT_QUERY_WORD_LIMIT:
        logger.debug("IntentClassifier: CONVERSATIONAL (short query, %d words)", word_count)
        return QueryIntent.CONVERSATIONAL

    # Rule 4: safe default
    logger.debug("IntentClassifier: DATA_QUERY (default fallback)")
    return QueryIntent.DATA_QUERY


def get_conversational_system_prompt() -> str:
    """
    Lighter system prompt used for pure conversational / educational responses
    that do NOT require tool calling or student data access.
    Skips all tool-related instructions to reduce token overhead.
    """
    return (
        "You are CareerForge AI, an expert technical training assistant. "
        "Help trainers and educators with general questions about placement preparation, "
        "training strategies, technical concepts, algorithms, data structures, and best practices. "
        "Be concise, friendly, and professional. "
        "Do NOT mention student data, analytics, or attempt to access any database — "
        "those queries are handled separately."
    )
