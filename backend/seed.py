"""
Database seed script — populates comprehensive curriculum, large question bank,
placement-ready mock assessments, and demo accounts for CareerForge AI.

Demo credentials:
  Admin:   admin@careerforge.ai / Admin@1234
  Trainer: trainer@careerforge.ai / Trainer@1234
  Student: student@careerforge.ai / Student@1234
  Student: alice@example.com / Student@1234
  Student: bob@example.com / Student@1234
"""
import asyncio
import sys
import os
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select as sa_select, delete as sa_delete
from app.core.config import settings
from app.core.security import hash_password
from app.models.user import User, UserRole, StudentProfile, TrainerProfile, Batch, BatchMembership
from app.models.content import (
    Subject, Topic, Lesson, Question, QuestionOption,
    SubjectCategory, DifficultyLevel, QuestionType
)
from app.models.test import Test, TestQuestion, TestStatus, TestType, TestAttempt, AttemptStatus, ProctoringEvent
from app.models.coding import CodingQuestion, TestCase, CodeSubmission, SubmissionVerdict
from app.db.database import Base

from app.data.curriculum import SUBJECTS_DATA, LESSONS_DATA
from app.data.quant_questions import QUANT_QUESTIONS
from app.data.logical_verbal_questions import LOGICAL_VERBAL_QUESTIONS
from app.data.cs_programming_questions import CS_DSA_QUESTIONS
from app.data.programming_questions import PROGRAMMING_QUESTIONS
from app.data.coding_questions import CODING_QUESTIONS_BANK





def now_utc():
    return datetime.now(timezone.utc)


async def seed():
    engine_kwargs = {"echo": False}
    if "sqlite" in settings.DATABASE_URL:
        engine_kwargs["connect_args"] = {"check_same_thread": False}
    engine = create_async_engine(settings.DATABASE_URL, **engine_kwargs)

    async with engine.begin() as conn:
        from app.models import user, content, test, coding, analytics, chat  # noqa
        await conn.run_sync(Base.metadata.create_all)

    Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with Session() as db:
        print("🌱 Seeding CareerForge AI database...")

        # ── 1. Users ──────────────────────────────────────────────────────────
        users_data = [
            ("admin@careerforge.ai", "Admin@1234", "Admin User", UserRole.ADMIN),
            ("trainer@careerforge.ai", "Trainer@1234", "Rajesh Kumar", UserRole.TRAINER),
            ("student@careerforge.ai", "Student@1234", "Demo Student", UserRole.STUDENT),
            ("alice@example.com", "Student@1234", "Alice Johnson", UserRole.STUDENT),
            ("bob@example.com", "Student@1234", "Bob Smith", UserRole.STUDENT),
        ]
        created_users = {}
        for email, pwd, name, role in users_data:
            existing = await db.execute(sa_select(User).where(User.email == email))
            u = existing.scalar_one_or_none()
            if not u:
                u = User(email=email, hashed_password=hash_password(pwd), full_name=name, role=role, is_active=True)
                db.add(u)
                await db.flush()
                print(f"  Created user: {email} ({role.value})")
            created_users[email] = u

            if role == UserRole.STUDENT:
                sp_ex = await db.execute(sa_select(StudentProfile).where(StudentProfile.user_id == u.id))
                sp = sp_ex.scalar_one_or_none()
                if not sp:
                    sp = StudentProfile(
                        user_id=u.id,
                        college="National Institute of Technology",
                        department="Computer Science",
                        graduation_year=2025,
                    )
                    db.add(sp)
                    await db.flush()
                created_users[f"sp_{email}"] = sp
            elif role == UserRole.TRAINER:
                tp_ex = await db.execute(sa_select(TrainerProfile).where(TrainerProfile.user_id == u.id))
                tp = tp_ex.scalar_one_or_none()
                if not tp:
                    tp = TrainerProfile(user_id=u.id, specialization="Data Structures & Algorithms", experience_years=5)
                    db.add(tp)
                    await db.flush()
                created_users[f"tp_{email}"] = tp

        await db.commit()

        # ── 2. Demo Batch & Memberships ───────────────────────────────────────
        trainer_profile = created_users.get("tp_trainer@careerforge.ai")
        batch_ex = await db.execute(sa_select(Batch).where(Batch.name == "Placement Batch 2025-A"))
        batch = batch_ex.scalar_one_or_none()
        if not batch and trainer_profile:
            batch = Batch(
                name="Placement Batch 2025-A",
                description="Elite campus placement preparation cohort for tech giants.",
                trainer_id=trainer_profile.id,
            )
            db.add(batch)
            await db.flush()
            print(f"  Created batch: {batch.name}")

            # Add demo students to batch
            for email in ["student@careerforge.ai", "alice@example.com", "bob@example.com"]:
                sp = created_users.get(f"sp_{email}")
                if sp:
                    db.add(BatchMembership(batch_id=batch.id, student_id=sp.id))
            await db.commit()

        # ── 3. Subjects & Topics ───────────────────────────────────────────────
        topic_map = {}  # topic_name -> Topic object
        for subj_idx, sdata in enumerate(SUBJECTS_DATA):
            subj_name = sdata["name"]
            existing_s = await db.execute(sa_select(Subject).where(Subject.name == subj_name))
            subj = existing_s.scalar_one_or_none()
            if not subj:
                subj = Subject(
                    name=subj_name,
                    category=sdata["category"],
                    icon=sdata["icon"],
                    description=sdata["description"],
                    order_index=subj_idx,
                )
                db.add(subj)
                await db.flush()
                print(f"  Created subject: {subj.name}")

            # Seed topics
            for top_idx, (tname, tdesc) in enumerate(sdata["topics"]):
                existing_t = await db.execute(
                    sa_select(Topic).where(Topic.subject_id == subj.id).where(Topic.name == tname)
                )
                t = existing_t.scalar_one_or_none()
                if not t:
                    t = Topic(
                        subject_id=subj.id,
                        name=tname,
                        description=tdesc,
                        order_index=top_idx,
                    )
                    db.add(t)
                    await db.flush()
                topic_map[tname] = t

        await db.commit()
        print(f"  Mapped {len(topic_map)} topics across all subjects.")

        # ── 4. Lessons ────────────────────────────────────────────────────────
        total_lessons = 0
        for tname, l_list in LESSONS_DATA.items():
            if tname not in topic_map:
                continue
            topic = topic_map[tname]
            for l_idx, (ltitle, lcontent, lexamples) in enumerate(l_list):
                ex_l = await db.execute(
                    sa_select(Lesson).where(Lesson.topic_id == topic.id).where(Lesson.title == ltitle)
                )
                if not ex_l.scalar_one_or_none():
                    lesson = Lesson(
                        topic_id=topic.id,
                        title=ltitle,
                        content=lcontent,
                        examples=lexamples,
                        order_index=l_idx,
                        estimated_minutes=10,
                    )
                    db.add(lesson)
                    total_lessons += 1
        await db.commit()
        print(f"  Seeded {total_lessons} study lessons.")

        # Populate all existing topics from database
        all_db_topics = (await db.execute(sa_select(Topic))).scalars().all()
        for t in all_db_topics:
            topic_map[t.name] = t

        # ── 5. Question Bank (Quant + Logical/Verbal + CS/DSA + Programming) ──
        all_mcqs = QUANT_QUESTIONS + LOGICAL_VERBAL_QUESTIONS + CS_DSA_QUESTIONS + PROGRAMMING_QUESTIONS
        seeded_mcqs = 0
        for q_data in all_mcqs:
            tname = q_data["topic"]
            if tname not in topic_map:
                continue
            topic = topic_map[tname]


            # Check if this exact question text already exists
            existing_q = await db.execute(
                sa_select(Question).where(Question.text == q_data["text"])
            )
            q = existing_q.scalar_one_or_none()
            if not q:
                q = Question(
                    topic_id=topic.id,
                    text=q_data["text"],
                    difficulty=q_data["difficulty"],
                    irt_difficulty=q_data.get("irt", 0.0),
                    explanation=q_data.get("explanation"),
                    question_type=QuestionType.MCQ,
                    points=1,
                )
                db.add(q)
                await db.flush()
                seeded_mcqs += 1

                for opt_idx, (opt_text, is_corr) in enumerate(q_data["options"]):
                    db.add(QuestionOption(
                        question_id=q.id,
                        text=opt_text,
                        is_correct=is_corr,
                        order_index=opt_idx,
                    ))

        await db.commit()
        print(f"  Seeded {seeded_mcqs} new MCQs into question bank.")

        # ── 6. Coding Questions & Test Cases ──────────────────────────────────
        trainer_user = created_users.get("trainer@careerforge.ai")
        trainer_uid = trainer_user.id if trainer_user else 2
        created_cqs = []
        seeded_cq_count = 0

        for cd in CODING_QUESTIONS_BANK:
            existing_cq = await db.execute(
                sa_select(CodingQuestion).where(CodingQuestion.slug == cd["slug"])
            )
            cq = existing_cq.scalar_one_or_none()
            if not cq:
                cq = CodingQuestion(
                    title=cd["title"],
                    slug=cd["slug"],
                    difficulty=cd["difficulty"],
                    problem_statement=cd["problem_statement"],
                    constraints=cd["constraints"],
                    input_format=cd["input_format"],
                    output_format=cd["output_format"],
                    examples=cd["examples"],
                    explanation=cd["explanation"],
                    supported_languages=cd["supported_languages"],
                    time_limit_ms=cd["time_limit_ms"],
                    memory_limit_mb=cd["memory_limit_mb"],
                    marks=cd["marks"],
                    tags=cd["tags"],
                    created_by=trainer_uid,
                    is_active=True,
                )
                db.add(cq)
                await db.flush()
                seeded_cq_count += 1

                for tc_data in cd["test_cases"]:
                    tc = TestCase(
                        coding_question_id=cq.id,
                        input=tc_data["input"],
                        expected_output=tc_data["expected_output"],
                        is_sample=tc_data["is_sample"],
                        order_index=tc_data["order_index"],
                    )
                    db.add(tc)

            created_cqs.append(cq)

        await db.commit()
        print(f"  Seeded {seeded_cq_count} new coding questions with test cases.")

        # ── 7. Placement Assessment Mock Test 1 (30 Qs / 30 Marks / 30 Mins) ──
        # Find 12 Quant, 10 Logical, 8 Verbal questions
        quant_topics = [
            "Percentages", "Profit & Loss", "Ratio & Proportion", "Averages",
            "Simple & Compound Interest", "Time & Work", "Speed, Distance & Time", "Number System"
        ]
        logical_topics = [
            "Series & Patterns", "Coding-Decoding", "Blood Relations", "Directions & Distances",
            "Syllogisms", "Seating Arrangement", "Puzzles & Ranking", "Clocks & Calendars"
        ]
        verbal_topics = [
            "Vocabulary & Usage", "Sentence Completion", "Error Detection", "Grammar & Mechanics"
        ]

        def get_topic_ids(topic_names):
            return [topic_map[t].id for t in topic_names if t in topic_map]

        quant_ids = get_topic_ids(quant_topics)
        logical_ids = get_topic_ids(logical_topics)
        verbal_ids = get_topic_ids(verbal_topics)

        # Query questions
        quant_qs_res = await db.execute(
            sa_select(Question).where(Question.topic_id.in_(quant_ids)).limit(12)
        )
        quant_qs = quant_qs_res.scalars().all()

        logical_qs_res = await db.execute(
            sa_select(Question).where(Question.topic_id.in_(logical_ids)).limit(10)
        )
        logical_qs = logical_qs_res.scalars().all()

        verbal_qs_res = await db.execute(
            sa_select(Question).where(Question.topic_id.in_(verbal_ids)).limit(8)
        )
        verbal_qs = verbal_qs_res.scalars().all()

        all_mock_qs = list(quant_qs) + list(logical_qs) + list(verbal_qs)

        # Upsert Test 1: "Placement Aptitude Mock Test 1" (or "Aptitude Mock Test 1")
        ex_mock = await db.execute(
            sa_select(Test).where(Test.test_type == TestType.APTITUDE).limit(1)
        )
        aptitude_test = ex_mock.scalar_one_or_none()
        if not aptitude_test:
            aptitude_test = Test(
                title="Placement Aptitude Mock Test 1",
                description="Comprehensive 30-minute campus placement mock test evaluating Quantitative Aptitude (12), Logical Reasoning (10), and Verbal Ability (8).",
                test_type=TestType.APTITUDE,
                batch_id=batch.id if batch else None,
                created_by=trainer_uid,
                duration_minutes=30,
                total_marks=30,
                passing_marks=18,
                instructions="Answer all 30 MCQs in 30 minutes. 1 mark per question. Proctoring is active. Switching tabs or loss of focus will be flagged.",
                status=TestStatus.PUBLISHED,
                randomize_questions=True,
            )
            db.add(aptitude_test)
            await db.flush()
        else:
            aptitude_test.title = "Placement Aptitude Mock Test 1"
            aptitude_test.description = "Comprehensive 30-minute campus placement mock test evaluating Quantitative Aptitude (12), Logical Reasoning (10), and Verbal Ability (8)."
            aptitude_test.duration_minutes = 30
            aptitude_test.total_marks = 30
            aptitude_test.passing_marks = 18
            aptitude_test.status = TestStatus.PUBLISHED
            aptitude_test.randomize_questions = True
            await db.flush()

        # Update test_questions mapping for Aptitude Mock Test to ensure exactly 30 questions
        await db.execute(sa_delete(TestQuestion).where(TestQuestion.test_id == aptitude_test.id))
        for idx, q in enumerate(all_mock_qs):
            db.add(TestQuestion(
                test_id=aptitude_test.id,
                question_id=q.id,
                order_index=idx,
                marks=1,
            ))
        await db.commit()
        print(f"  Configured '{aptitude_test.title}': {len(all_mock_qs)} questions, {aptitude_test.duration_minutes} mins, {aptitude_test.total_marks} marks.")

        # ── 8. Placement Coding Assessment 1 (3 Problems / 45 Mins / 35 Marks) ──
        ex_coding_test = await db.execute(
            sa_select(Test).where(Test.test_type == TestType.CODING).limit(1)
        )
        coding_test = ex_coding_test.scalar_one_or_none()

        # Select 3 high-value coding questions (e.g., Two Sum, Merge Intervals, Coin Change)
        slugs_to_map = ["two-sum", "merge-intervals", "coin-change"]
        mapped_cqs = []
        for slug in slugs_to_map:
            cq_res = await db.execute(sa_select(CodingQuestion).where(CodingQuestion.slug == slug))
            c = cq_res.scalar_one_or_none()
            if c:
                mapped_cqs.append(c)

        if not mapped_cqs and created_cqs:
            mapped_cqs = created_cqs[:3]

        if not coding_test:
            coding_test = Test(
                title="Placement Coding Assessment 1",
                description="Timed technical coding assessment evaluating arrays, stacks, and dynamic programming.",
                test_type=TestType.CODING,
                batch_id=batch.id if batch else None,
                created_by=trainer_uid,
                duration_minutes=45,
                total_marks=sum(c.marks for c in mapped_cqs),
                passing_marks=20,
                instructions="Solve 3 algorithmic problems in 45 minutes using Python, JavaScript, C++, or Java. Anti-malpractice telemetry is enabled.",
                status=TestStatus.PUBLISHED,
                randomize_questions=False,
            )
            db.add(coding_test)
            await db.flush()
        else:
            coding_test.title = "Placement Coding Assessment 1"
            coding_test.duration_minutes = 45
            coding_test.total_marks = sum(c.marks for c in mapped_cqs)
            coding_test.passing_marks = 20
            coding_test.status = TestStatus.PUBLISHED
            await db.flush()

        # Map the 3 coding questions
        await db.execute(sa_delete(TestQuestion).where(TestQuestion.test_id == coding_test.id))
        for idx, cq in enumerate(mapped_cqs):
            db.add(TestQuestion(
                test_id=coding_test.id,
                coding_question_id=cq.id,
                order_index=idx,
                marks=cq.marks,
            ))
        await db.commit()
        print(f"  Configured '{coding_test.title}': {len(mapped_cqs)} problems, {coding_test.duration_minutes} mins, {coding_test.total_marks} marks.")

    await engine.dispose()
    print("\n🎉 Seed complete! All subjects, topics, questions, and assessments are live in PostgreSQL.")


if __name__ == "__main__":
    asyncio.run(seed())
