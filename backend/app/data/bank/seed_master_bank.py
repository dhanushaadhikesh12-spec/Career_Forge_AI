"""
Master Seeding & Migration script for CareerForge AI.
Safely and idempotently populates all 52 topics in PostgreSQL to 40+ questions each,
and expands the coding problem bank to 66+ problems.
"""
import asyncio
import json
import os
import re
from datetime import datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.db.database import AsyncSessionLocal
from app.models.content import Topic, Question, QuestionOption, QuestionType, DifficultyLevel
from app.models.coding import CodingQuestion, TestCase
from app.models.user import User

def normalize_text(text: str) -> str:
    return re.sub(r'\s+', ' ', text.strip().lower())

async def seed_master_bank():
    print("🚀 Starting Master Question Bank & Coding Bank Migration...")
    bank_dir = os.path.dirname(__file__)

    async with AsyncSessionLocal() as session:
        # 1. Map all topics
        topic_res = await session.execute(select(Topic))
        all_topics = topic_res.scalars().all()
        topic_map = {t.name.strip().lower(): t for t in all_topics}
        # Also store original name mapping
        for t in all_topics:
            topic_map[t.name.strip()] = t

        print(f"Loaded {len(all_topics)} curriculum topics from PostgreSQL.")

        # 2. Existing question texts for duplicate detection
        existing_res = await session.execute(select(Question.text))
        existing_texts = {normalize_text(txt) for txt in existing_res.scalars().all() if txt}
        print(f"Found {len(existing_texts)} existing questions in database.")

        # 3. Load all MCQ banks
        bank_files = [
            "quant_bank.json",
            "logical_bank.json",
            "verbal_bank.json",
            "programming_bank.json",
            "dsa_bank.json",
            "cs_bank.json",
        ]

        total_inserted = 0
        total_skipped = 0

        for b_file in bank_files:
            b_path = os.path.join(bank_dir, b_file)
            if not os.path.exists(b_path):
                print(f"Warning: {b_file} not found, skipping.")
                continue

            with open(b_path, "r", encoding="utf-8") as f:
                questions = json.load(f)

            inserted_in_file = 0
            for q_data in questions:
                raw_topic = q_data["topic"].strip()
                norm_topic = raw_topic.lower()
                topic = topic_map.get(norm_topic) or topic_map.get(raw_topic)
                if not topic:
                    # Try partial match
                    for k, t in topic_map.items():
                        if k in norm_topic or norm_topic in k:
                            topic = t
                            break

                if not topic:
                    print(f"Warning: Topic '{raw_topic}' not mapped.")
                    continue

                norm_q = normalize_text(q_data["text"])
                if norm_q in existing_texts:
                    total_skipped += 1
                    continue

                diff = q_data["difficulty"].upper()
                diff_enum = getattr(DifficultyLevel, diff, DifficultyLevel.MEDIUM)

                q_obj = Question(
                    topic_id=topic.id,
                    text=q_data["text"],
                    difficulty=diff_enum,
                    irt_difficulty=float(q_data.get("irt", 0.0)),
                    explanation=q_data.get("explanation"),
                    question_type=QuestionType.MCQ,
                    points=1,
                    created_at=datetime.now(timezone.utc),
                )
                session.add(q_obj)
                await session.flush()

                # Add options
                for idx, (opt_text, is_corr) in enumerate(q_data["options"]):
                    opt = QuestionOption(
                        question_id=q_obj.id,
                        text=str(opt_text),
                        is_correct=bool(is_corr),
                        order_index=idx,
                    )
                    session.add(opt)

                existing_texts.add(norm_q)
                inserted_in_file += 1
                total_inserted += 1

            print(f"  {b_file}: inserted {inserted_in_file} new questions.")
            await session.commit()

        print(f"✅ Finished MCQ seeding: {total_inserted} new questions inserted ({total_skipped} skipped duplicates).")

        # 4. Seed Additional Coding Questions
        admin_res = await session.execute(select(User.id).limit(1))
        author_id = admin_res.scalar() or 1

        coding_file = os.path.join(bank_dir, "additional_coding_bank.json")
        inserted_coding = 0
        if os.path.exists(coding_file):
            with open(coding_file, "r", encoding="utf-8") as f:
                cqs = json.load(f)

            for cd in cqs:
                cq_ex = await session.execute(
                    select(CodingQuestion).where(CodingQuestion.slug == cd["slug"])
                )
                if cq_ex.scalar_one_or_none():
                    continue

                cq_obj = CodingQuestion(
                    title=cd["title"],
                    slug=cd["slug"],
                    difficulty=cd["difficulty"],
                    problem_statement=cd["problem_statement"],
                    constraints=cd.get("constraints"),
                    input_format=cd.get("input_format"),
                    output_format=cd.get("output_format"),
                    examples=cd.get("examples"),
                    explanation=cd.get("explanation"),
                    supported_languages=cd.get("supported_languages", ["python", "javascript", "cpp", "java"]),
                    time_limit_ms=cd.get("time_limit_ms", 2000),
                    memory_limit_mb=cd.get("memory_limit_mb", 256),
                    marks=cd.get("marks", 15),
                    tags=cd.get("tags", []),
                    created_by=author_id,
                    is_active=True,
                    created_at=datetime.now(timezone.utc),
                )
                session.add(cq_obj)
                await session.flush()

                for tc_data in cd.get("test_cases", []):
                    tc = TestCase(
                        coding_question_id=cq_obj.id,
                        input=tc_data["input"],
                        expected_output=tc_data["expected_output"],
                        is_sample=tc_data.get("is_sample", False),
                        order_index=tc_data.get("order_index", 0),
                    )
                    session.add(tc)

                inserted_coding += 1

            await session.commit()
            print(f"✅ Inserted {inserted_coding} additional coding problems with test cases.")

        # 5. Final verification count
        tot_q = (await session.execute(select(func.count(Question.id)))).scalar() or 0
        tot_cq = (await session.execute(select(func.count(CodingQuestion.id)))).scalar() or 0
        print(f"\n🎉 DATABASE TOTALS: {tot_q} MCQs across all topics | {tot_cq} Coding Problems.")

if __name__ == "__main__":
    asyncio.run(seed_master_bank())
