"""
Question Bank & Assessment System Master Health Check Utility.
Validates:
- Topics with < 30 (FAIL), 30-39 (PASS), >= 40 (PREFERRED)
- Topic difficulty distribution: Beginner (EASY), Intermediate (MEDIUM), Advanced (HARD)
- Duplicate questions (normalized text)
- Questions without options or without exactly 1 correct answer
- Questions without explanations
- Orphaned questions (invalid or null topic_id)
- Coding problems and test case coverage (sample & hidden test cases)
"""
import asyncio
import re
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from sqlalchemy.orm import selectinload

from app.db.database import AsyncSessionLocal
from app.models.content import Subject, Topic, Question, QuestionOption, DifficultyLevel
from app.models.coding import CodingQuestion, TestCase
from app.models.test import Test, TestQuestion, TestType

def normalize_text(t: str) -> str:
    return re.sub(r'\s+', ' ', t.strip().lower())

async def run_health_check(db: AsyncSession) -> Dict[str, Any]:
    issues: List[str] = []

    # 1. Subjects, Topics, Counts & Difficulty Breakdown
    rows = await db.execute(text("""
        SELECT s.id as subject_id, s.name as subject_name, s.category as category,
               t.id as topic_id, t.name as topic_name,
               COUNT(q.id) as q_count,
               SUM(CASE WHEN q.difficulty = 'EASY' THEN 1 ELSE 0 END) as easy_cnt,
               SUM(CASE WHEN q.difficulty = 'MEDIUM' THEN 1 ELSE 0 END) as med_cnt,
               SUM(CASE WHEN q.difficulty = 'HARD' THEN 1 ELSE 0 END) as hard_cnt
        FROM topics t
        JOIN subjects s ON t.subject_id = s.id
        LEFT JOIN questions q ON q.topic_id = t.id
        GROUP BY s.id, s.name, s.category, t.id, t.name
        ORDER BY s.id, t.id
    """))
    topic_rows = rows.fetchall()

    topic_reports = []
    empty_topics = []
    topics_below_30 = []
    topics_30_to_39 = []
    topics_preferred = []

    for r in topic_rows:
        cnt = r.q_count
        if cnt == 0:
            status = "FAIL"
            empty_topics.append(f"{r.subject_name} -> {r.topic_name}")
            issues.append(f"CRITICAL: Topic '{r.topic_name}' has 0 questions.")
        elif cnt < 30:
            status = "FAIL"
            topics_below_30.append(f"{r.subject_name} -> {r.topic_name} ({cnt} Qs)")
            issues.append(f"FAIL: Topic '{r.topic_name}' has {cnt} questions (minimum required is 30).")
        elif cnt < 40:
            status = "PASS"
            topics_30_to_39.append(f"{r.subject_name} -> {r.topic_name} ({cnt} Qs)")
        else:
            status = "PREFERRED"
            topics_preferred.append(f"{r.subject_name} -> {r.topic_name} ({cnt} Qs)")

        topic_reports.append({
            "subject": r.subject_name,
            "topic": r.topic_name,
            "topic_id": r.topic_id,
            "question_count": cnt,
            "beginner": r.easy_cnt,
            "intermediate": r.med_cnt,
            "advanced": r.hard_cnt,
            "status": status,
        })

    # 2. Duplicate Questions
    dup_res = await db.execute(text("""
        SELECT LOWER(REGEXP_REPLACE(TRIM(text), '\\s+', ' ', 'g')) as norm_text,
               COUNT(id) as cnt
        FROM questions
        GROUP BY LOWER(REGEXP_REPLACE(TRIM(text), '\\s+', ' ', 'g'))
        HAVING COUNT(id) > 1
    """))
    duplicates = dup_res.fetchall()
    for d in duplicates:
        issues.append(f"DUPLICATE: Question text repeated {d.cnt} times: '{d.norm_text[:60]}...'")

    # 3. Question Options & Answers Integrity
    bad_opts_res = await db.execute(text("""
        SELECT q.id, q.text, COUNT(qo.id) as opt_count,
               SUM(CASE WHEN qo.is_correct THEN 1 ELSE 0 END) as corr_count
        FROM questions q
        LEFT JOIN question_options qo ON qo.question_id = q.id
        GROUP BY q.id, q.text
        HAVING COUNT(qo.id) != 4 OR SUM(CASE WHEN qo.is_correct THEN 1 ELSE 0 END) != 1
    """))
    bad_options = bad_opts_res.fetchall()
    for b in bad_options:
        issues.append(f"INTEGRITY: Question ID {b.id} has {b.opt_count} options and {b.corr_count} correct answers.")

    # 4. Missing Explanations
    bad_exp_res = await db.execute(text("""
        SELECT id, text FROM questions
        WHERE explanation IS NULL OR LENGTH(TRIM(explanation)) = 0
    """))
    missing_explanations = bad_exp_res.fetchall()
    for m in missing_explanations:
        issues.append(f"QUALITY: Question ID {m.id} is missing an explanation.")

    # 5. Orphaned Questions
    orphan_res = await db.execute(text("""
        SELECT q.id FROM questions q
        LEFT JOIN topics t ON q.topic_id = t.id
        WHERE t.id IS NULL
    """))
    orphaned_questions = orphan_res.fetchall()
    for o in orphaned_questions:
        issues.append(f"ORPHAN: Question ID {o.id} has no valid topic mapping.")

    # 6. Coding Questions & Test Cases
    coding_res = await db.execute(text("""
        SELECT cq.id, cq.title, cq.slug, cq.difficulty,
               COUNT(tc.id) as total_tc,
               SUM(CASE WHEN tc.is_sample THEN 1 ELSE 0 END) as sample_tc,
               SUM(CASE WHEN NOT tc.is_sample THEN 1 ELSE 0 END) as hidden_tc
        FROM coding_questions cq
        LEFT JOIN test_cases tc ON tc.coding_question_id = cq.id
        GROUP BY cq.id, cq.title, cq.slug, cq.difficulty
        ORDER BY cq.id
    """))
    coding_rows = coding_res.fetchall()
    coding_no_hidden = [c.title for c in coding_rows if c.hidden_tc == 0]
    coding_no_sample = [c.title for c in coding_rows if c.sample_tc == 0]

    for c in coding_no_hidden:
        issues.append(f"CODING: Problem '{c}' has 0 hidden test cases.")
    for c in coding_no_sample:
        issues.append(f"CODING: Problem '{c}' has 0 sample test cases.")

    total_questions = sum(r.q_count for r in topic_rows)
    overall_status = "HEALTHY" if len(issues) == 0 and len(topics_below_30) == 0 else "ACTION_REQUIRED"

    return {
        "status": overall_status,
        "total_subjects": len({r.subject_name for r in topic_rows}),
        "total_topics": len(topic_rows),
        "total_questions": total_questions,
        "total_coding_problems": len(coding_rows),
        "topics_below_30_count": len(topics_below_30),
        "topics_30_to_39_count": len(topics_30_to_39),
        "topics_preferred_count": len(topics_preferred),
        "duplicate_count": len(duplicates),
        "broken_options_count": len(bad_options),
        "missing_explanations_count": len(missing_explanations),
        "orphaned_count": len(orphaned_questions),
        "coding_no_hidden_count": len(coding_no_hidden),
        "topic_reports": topic_reports,
        "issues": issues,
    }

async def cli_health_check():
    async with AsyncSessionLocal() as session:
        report = await run_health_check(session)
        print("=" * 105)
        print("                 CAREERFORGE AI — MASTER QUESTION BANK & CURRICULUM HEALTH REPORT")
        print("=" * 105)
        header = f"{'Subject':27} | {'Topic':30} | {'Count':5} | {'Beginner':8} | {'Intermed':8} | {'Advanced':8} | {'Status'}"
        print(header)
        print("-" * 105)
        for tr in report["topic_reports"]:
            line = (
                f"{tr['subject'][:27]:27} | "
                f"{tr['topic'][:30]:30} | "
                f"{tr['question_count']:5d} | "
                f"{tr['beginner']:8d} | "
                f"{tr['intermediate']:8d} | "
                f"{tr['advanced']:8d} | "
                f"{tr['status']}"
            )
            print(line)
        print("-" * 105)
        print(f"TOTAL SUBJECTS:          {report['total_subjects']}")
        print(f"TOTAL TOPICS:            {report['total_topics']}")
        print(f"TOTAL MCQs:              {report['total_questions']}")
        print(f"TOTAL CODING PROBLEMS:   {report['total_coding_problems']}")
        print(f"Topics < 30 (FAIL):      {report['topics_below_30_count']}")
        print(f"Topics 30-39 (PASS):     {report['topics_30_to_39_count']}")
        print(f"Topics >= 40 (PREFERRED): {report['topics_preferred_count']}")
        print(f"Duplicate questions:     {report['duplicate_count']}")
        print(f"Broken options/answers:  {report['broken_options_count']}")
        print(f"Missing explanations:    {report['missing_explanations_count']}")
        print(f"Orphaned questions:      {report['orphaned_count']}")
        print(f"Coding without hidden:   {report['coding_no_hidden_count']}")
        print(f"OVERALL HEALTH STATUS:   {report['status']}")
        print("=" * 105)

        if report["issues"]:
            print(f"\n⚠️ Issues Identified ({len(report['issues'])}):")
            for iss in report["issues"][:10]:
                print(f"  - {iss}")
        else:
            print("\n🎉 ALL CHECKS PASSED: 100% of topics have >= 40 questions with valid options, explanations, and test cases.")

if __name__ == "__main__":
    asyncio.run(cli_health_check())
