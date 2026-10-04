"""
Plagiarism / code similarity detection engine.
Uses structural tokenization, comment stripping, identifier normalization,
and n-gram Jaccard similarity to detect copied code patterns.
"""
from __future__ import annotations
import re
import difflib
from typing import List, Dict, Any, Tuple


PYTHON_KEYWORDS = {
    "def", "class", "return", "if", "elif", "else", "for", "while", "in", "break",
    "continue", "pass", "import", "from", "as", "try", "except", "finally", "with",
    "lambda", "yield", "raise", "assert", "global", "nonlocal", "True", "False", "None",
    "and", "or", "not", "is", "len", "range", "print", "int", "float", "str", "list", "dict", "set"
}

CPP_JAVA_KEYWORDS = {
    "int", "float", "double", "char", "void", "bool", "boolean", "public", "private",
    "protected", "class", "struct", "for", "while", "do", "if", "else", "switch",
    "case", "break", "continue", "return", "new", "delete", "this", "static", "const",
    "virtual", "override", "import", "package", "namespace", "using", "include", "vector",
    "string", "cout", "cin", "endl", "System", "out", "println"
}

ALL_KEYWORDS = PYTHON_KEYWORDS.union(CPP_JAVA_KEYWORDS)


def strip_comments_and_whitespace(code: str, language: str = "python") -> str:
    """Strips block and inline comments and normalizes whitespace."""
    if language.lower() in ["python", "py", "python3"]:
        # Remove Python comments
        code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
        # Remove docstrings
        code = re.sub(r'""".*?"""', '', code, flags=re.DOTALL)
        code = re.sub(r"'''.*?'''", '', code, flags=re.DOTALL)
    else:
        # C++, Java, JS comments
        code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)

    # Normalize multiple whitespace to single space
    lines = [line.strip() for line in code.splitlines() if line.strip()]
    return "\n".join(lines)


def normalize_code_identifiers(code: str) -> List[str]:
    """
    Tokenizes code and renames user-defined identifiers sequentially
    (e.g., first variable -> $V1, second -> $V2) while keeping language keywords intact.
    This neutralizes simple variable renaming attempts.
    """
    tokens = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*|[^\s\w]', code)
    normalized: List[str] = []
    id_map: Dict[str, str] = {}
    id_counter = 1

    for token in tokens:
        if token in ALL_KEYWORDS:
            normalized.append(token)
        elif re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', token):
            if token not in id_map:
                id_map[token] = f"$V{id_counter}"
                id_counter += 1
            normalized.append(id_map[token])
        else:
            normalized.append(token)

    return normalized


def compute_token_ngrams(tokens: List[str], n: int = 4) -> set:
    """Generates set of token n-grams."""
    if len(tokens) < n:
        return {tuple(tokens)}
    return {tuple(tokens[i:i+n]) for i in range(len(tokens) - n + 1)}


def calculate_code_similarity(code_a: str, code_b: str, language: str = "python") -> Dict[str, Any]:
    """
    Calculates structural similarity between two code submissions.
    Returns:
    {
        "similarity_score": float (0-100),
        "is_flagged": bool (>= 80%),
        "risk_level": "LOW" | "MEDIUM" | "HIGH",
        "details": "..."
    }
    """
    clean_a = strip_comments_and_whitespace(code_a, language)
    clean_b = strip_comments_and_whitespace(code_b, language)

    if not clean_a or not clean_b:
        return {"similarity_score": 0.0, "is_flagged": False, "risk_level": "LOW", "details": "Empty code submission"}

    # Exact cleaned match
    if clean_a == clean_b:
        return {"similarity_score": 100.0, "is_flagged": True, "risk_level": "HIGH", "details": "Identical normalized code"}

    tokens_a = normalize_code_identifiers(clean_a)
    tokens_b = normalize_code_identifiers(clean_b)

    # 1. Normalized Token Sequence Matcher Ratio
    seq_ratio = difflib.SequenceMatcher(None, tokens_a, tokens_b).ratio()

    # 2. Token N-Gram Jaccard Index (n=4)
    ngrams_a = compute_token_ngrams(tokens_a, n=4)
    ngrams_b = compute_token_ngrams(tokens_b, n=4)

    intersection = len(ngrams_a.intersection(ngrams_b))
    union = len(ngrams_a.union(ngrams_b))
    jaccard = (intersection / union) if union > 0 else 0.0

    # Weighted composite similarity
    composite_similarity = (seq_ratio * 0.6 + jaccard * 0.4) * 100.0
    score = round(min(100.0, max(0.0, composite_similarity)), 1)

    is_flagged = score >= 80.0
    if score >= 85.0:
        risk = "HIGH"
    elif score >= 70.0:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    return {
        "similarity_score": score,
        "is_flagged": is_flagged,
        "risk_level": risk,
        "sequence_similarity": round(seq_ratio * 100, 1),
        "structural_ngram_similarity": round(jaccard * 100, 1),
    }


def analyze_submission_pool(submissions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Analyzes a pool of student submissions for a single question or assessment.
    Returns flagged pairs with similarity >= 75% for trainer review.
    """
    flagged_pairs = []
    n = len(submissions)

    for i in range(n):
        for j in range(i + 1, n):
            sub_a = submissions[i]
            sub_b = submissions[j]

            # Don't compare same student against themselves
            if sub_a.get("student_id") == sub_b.get("student_id"):
                continue

            sim = calculate_code_similarity(
                sub_a.get("source_code", ""),
                sub_b.get("source_code", ""),
                language=sub_a.get("language", "python")
            )

            if sim["similarity_score"] >= 70.0:
                flagged_pairs.append({
                    "student_a_id": sub_a.get("student_id"),
                    "student_a_name": sub_a.get("student_name", "Student A"),
                    "submission_a_id": sub_a.get("submission_id"),
                    "student_b_id": sub_b.get("student_id"),
                    "student_b_name": sub_b.get("student_name", "Student B"),
                    "submission_b_id": sub_b.get("submission_id"),
                    "similarity_score": sim["similarity_score"],
                    "risk_level": sim["risk_level"],
                    "is_flagged": sim["is_flagged"],
                    "language": sub_a.get("language"),
                })

    # Sort descending by similarity
    flagged_pairs.sort(key=lambda x: x["similarity_score"], reverse=True)
    return flagged_pairs
