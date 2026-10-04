"""
Personalized Adaptive Aptitude Engine.
Implements:
1. Item Response Theory (1PL Rasch Model) + Elo Skill Rating
2. Dynamic topic prioritization (weakness weighting + exploration of unpracticed topics)
3. Zone of Proximal Development (ZPD) difficulty calibration
4. Previous attempt tracking to eliminate unnecessary repetition
5. Continuous Bayesian/moving-average skill updates
6. Actionable personalization insights & diagnostic feedback
"""
import math
import random
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.models.user import StudentProfile, TopicProgress
from app.models.content import (
    Topic, Question, QuestionOption, PracticeAttempt, DifficultyLevel, StudentQuestionHistory
)


# Difficulty IRT calibration mappings
DIFFICULTY_TO_IRT = {
    DifficultyLevel.EASY: -1.2,
    DifficultyLevel.MEDIUM: 0.0,
    DifficultyLevel.HARD: 1.4,
}

IRT_TO_DIFFICULTY = [
    (-0.5, DifficultyLevel.EASY),
    (0.6, DifficultyLevel.MEDIUM),
    (99.0, DifficultyLevel.HARD),
]


class AdaptiveEngine:
    """
    Intelligent Adaptive Engine for placement aptitude learning and practice.
    """

    @staticmethod
    def calculate_irt_probability(theta: float, b: float) -> float:
        """
        1PL Rasch Model probability: P(correct | theta, b) = 1 / (1 + exp(-(theta - b)))
        theta = student ability, b = item difficulty
        """
        try:
            return 1.0 / (1.0 + math.exp(-(theta - b)))
        except OverflowError:
            return 1.0 if (theta - b) > 0 else 0.0

    @staticmethod
    def calculate_elo_expected(player_rating: float, question_rating: float) -> float:
        """Standard Elo expected score between student and question."""
        return 1.0 / (1.0 + 10.0 ** ((question_rating - player_rating) / 400.0))

    @classmethod
    def difficulty_for_ability(cls, theta: float, accuracy: float, streak: int) -> DifficultyLevel:
        """
        Determines the optimal difficulty level in the student's Zone of Proximal Development.
        - If weak (accuracy < 50% or low theta): EASY (build foundational competence)
        - If strong (accuracy >= 80% or streak >= 3 or high theta): HARD (continual challenge)
        - Otherwise: MEDIUM
        """
        if streak >= 3 or (accuracy >= 0.80 and theta >= 0.5):
            return DifficultyLevel.HARD
        elif accuracy < 0.50 or theta < -0.4:
            return DifficultyLevel.EASY
        else:
            return DifficultyLevel.MEDIUM

    @classmethod
    async def get_student_topic_analytics(
        cls, db: AsyncSession, student_id: int
    ) -> List[Dict[str, Any]]:
        """
        Fetches topic-level metrics for all topics:
        - Accuracy percentage
        - Questions attempted, correct, incorrect
        - Elo skill rating
        - IRT ability (theta)
        - Average response time
        - Recent accuracy trend
        - Performance category
        """
        # Fetch all topics
        t_result = await db.execute(select(Topic).order_by(Topic.order_index))
        all_topics = t_result.scalars().all()

        # Fetch progress records
        p_result = await db.execute(
            select(TopicProgress)
            .where(TopicProgress.student_id == student_id)
            .options(selectinload(TopicProgress.topic))
        )
        progress_map = {p.topic_id: p for p in p_result.scalars().all()}

        results = []
        for t in all_topics:
            prog = progress_map.get(t.id)
            attempted = prog.questions_attempted if prog else 0
            correct = prog.questions_correct if prog else 0
            incorrect = attempted - correct
            accuracy = (correct / attempted * 100.0) if attempted > 0 else None
            skill = prog.skill_rating if prog else 1000.0
            theta = prog.irt_ability if prog else 0.0
            avg_time = prog.avg_response_time_seconds if prog else 30.0
            recent_acc = prog.recent_accuracy if prog else 0.5
            streak = prog.streak if prog else 0

            # Categorization
            if attempted < 3:
                category = "EXPLORING"
                category_label = "Insufficient Data"
            elif accuracy < 50.0:
                category = "WEAK"
                category_label = "Needs Urgent Practice"
            elif accuracy < 75.0:
                category = "DEVELOPING"
                category_label = "Steady Progress"
            else:
                category = "STRONG"
                category_label = "Mastered"

            results.append({
                "topic_id": t.id,
                "topic_name": t.name,
                "questions_attempted": attempted,
                "questions_correct": correct,
                "questions_incorrect": incorrect,
                "accuracy": round(accuracy, 1) if accuracy is not None else None,
                "recent_accuracy": round(recent_acc * 100, 1),
                "skill_rating": round(skill, 1),
                "irt_ability": round(theta, 2),
                "avg_response_time_seconds": round(avg_time, 1),
                "streak": streak,
                "category": category,
                "category_label": category_label,
                "last_practiced": prog.last_practiced if prog else None,
            })

        return results

    @classmethod
    async def select_topic_weighted(
        cls, db: AsyncSession, student_id: int, candidate_topic_ids: Optional[List[int]] = None
    ) -> int:
        """
        Dynamically selects a topic balancing:
        1. Weakness prioritization (higher weight for lower accuracy)
        2. Exploration bonus (topics with < 3 attempts get elevated weight)
        3. Challenge factor (strong topics still selected occasionally for advanced testing)
        """
        analytics = await cls.get_student_topic_analytics(db, student_id)
        if candidate_topic_ids:
            analytics = [a for a in analytics if a["topic_id"] in candidate_topic_ids]

        if not analytics:
            # Fallback to any topic
            first_t = await db.execute(select(Topic.id).limit(1))
            return first_t.scalar() or 1

        weighted_choices = []
        for a in analytics:
            attempted = a["questions_attempted"]
            acc = a["accuracy"]

            if attempted < 3:
                # Exploration bonus for topics without enough data
                weight = 3.0
            elif acc is not None and acc < 50.0:
                # Weak topic: high priority
                weight = 4.0 * (1.0 - (acc / 100.0))
            elif acc is not None and acc < 75.0:
                # Moderate topic
                weight = 2.0
            else:
                # Strong topic: reduced frequency
                weight = 0.6

            weighted_choices.append((a["topic_id"], weight))

        # Sample based on weight distribution
        topic_ids = [w[0] for w in weighted_choices]
        weights = [w[1] for w in weighted_choices]
        return random.choices(topic_ids, weights=weights, k=1)[0]

    @classmethod
    async def record_question_exposure(
        cls, db: AsyncSession, student_id: int, question_id: int
    ) -> StudentQuestionHistory:
        """Records that a student has been exposed to / presented with a question."""
        res = await db.execute(
            select(StudentQuestionHistory)
            .where(StudentQuestionHistory.student_id == student_id)
            .where(StudentQuestionHistory.question_id == question_id)
        )
        hist = res.scalar_one_or_none()
        now = datetime.now(timezone.utc)
        if not hist:
            hist = StudentQuestionHistory(
                student_id=student_id,
                question_id=question_id,
                first_seen_at=now,
                last_seen_at=now,
                times_seen=1,
                times_correct=0,
                times_incorrect=0,
            )
            db.add(hist)
        else:
            hist.times_seen += 1
            hist.last_seen_at = now
        await db.flush()
        return hist

    @classmethod
    async def update_question_exposure_result(
        cls, db: AsyncSession, student_id: int, question_id: int, is_correct: bool
    ) -> None:
        """Updates correctness metrics for question exposure history upon submission."""
        res = await db.execute(
            select(StudentQuestionHistory)
            .where(StudentQuestionHistory.student_id == student_id)
            .where(StudentQuestionHistory.question_id == question_id)
        )
        hist = res.scalar_one_or_none()
        now = datetime.now(timezone.utc)
        if not hist:
            hist = StudentQuestionHistory(
                student_id=student_id,
                question_id=question_id,
                first_seen_at=now,
                last_seen_at=now,
                times_seen=1,
                times_correct=1 if is_correct else 0,
                times_incorrect=0 if is_correct else 1,
            )
            db.add(hist)
        else:
            if is_correct:
                hist.times_correct += 1
            else:
                hist.times_incorrect += 1
            hist.last_seen_at = now
        await db.flush()

    @classmethod
    async def select_adaptive_question(
        cls,
        db: AsyncSession,
        student_id: int,
        topic_id: Optional[int] = None,
        exclude_question_ids: Optional[List[int]] = None,
    ) -> Optional[Question]:
        """
        Selects the single most optimal, personalized question for the student.
        1. Identifies target topic (if not specified).
        2. Determines student skill (theta) and target difficulty (ZPD).
        3. Loads student exposure history from `student_question_history`.
        4. Priority 1: Selects from unseen eligible questions.
        5. Priority 2 & 3: When unseen pool is exhausted:
           - Excludes questions currently in the session
           - Prefers least recently seen questions (oldest last_seen_at)
           - Prefers questions answered incorrectly for reinforcement
           - Prefers target difficulty
        6. Applies controlled exploration and shuffling.
        7. Records exposure in `student_question_history`.
        """
        if topic_id is None:
            topic_id = await cls.select_topic_weighted(db, student_id)

        # Get student's progress in this topic
        p_res = await db.execute(
            select(TopicProgress)
            .where(TopicProgress.student_id == student_id)
            .where(TopicProgress.topic_id == topic_id)
        )
        prog = p_res.scalar_one_or_none()

        theta = prog.irt_ability if prog else 0.0
        attempted = prog.questions_attempted if prog else 0
        correct = prog.questions_correct if prog else 0
        accuracy = (correct / attempted) if attempted > 0 else 0.5
        streak = prog.streak if prog else 0

        target_diff = cls.difficulty_for_ability(theta, accuracy, streak)

        # Query all questions for this topic
        q_query = (
            select(Question)
            .where(Question.topic_id == topic_id)
            .options(selectinload(Question.options))
        )
        all_topic_questions = (await db.execute(q_query)).scalars().all()
        if not all_topic_questions:
            return None

        # Fetch student question history for this student
        hist_res = await db.execute(
            select(StudentQuestionHistory)
            .where(StudentQuestionHistory.student_id == student_id)
        )
        history_map = {h.question_id: h for h in hist_res.scalars().all()}

        exclude_set = set(exclude_question_ids or [])

        # Priority 1: Unseen questions
        unseen_questions = [
            q for q in all_topic_questions
            if q.id not in history_map and q.id not in exclude_set
        ]

        now = datetime.now(timezone.utc)
        selected_question: Optional[Question] = None

        if unseen_questions:
            # Match target difficulty first
            matching_diff = [q for q in unseen_questions if q.difficulty == target_diff]
            candidate_pool = matching_diff if matching_diff else unseen_questions

            # Sort by Fisher information (proximity of IRT difficulty to student ability theta)
            sorted_candidates = sorted(candidate_pool, key=lambda q: abs(q.irt_difficulty - theta))
            # Pick from top 3 closest with controlled randomization / shuffle
            top_k = sorted_candidates[:min(3, len(sorted_candidates))]
            selected_question = random.choice(top_k)

        else:
            # Pool Exhaustion: All questions in this topic have been seen by this student.
            # Filter out questions already in the current session
            eligible_seen = [q for q in all_topic_questions if q.id not in exclude_set]
            if not eligible_seen:
                eligible_seen = list(all_topic_questions)

            # Score each seen question:
            # 1. Least recently seen (seconds since last seen)
            # 2. Reinforcement bonus if answered incorrectly
            # 3. Target difficulty bonus
            def exhaustion_score(q: Question) -> float:
                h = history_map.get(q.id)
                if not h:
                    return 1e9  # treated as unseen
                
                # Seconds since last seen (higher is older / preferred)
                if h.last_seen_at:
                    seen_at = h.last_seen_at if h.last_seen_at.tzinfo else h.last_seen_at.replace(tzinfo=timezone.utc)
                    seconds_ago = max(0.0, (now - seen_at).total_seconds())
                else:
                    seconds_ago = 999999.0

                # Reinforcement preference: questions answered incorrectly
                reinforce_bonus = 0.0
                if h.times_incorrect > h.times_correct or h.times_correct == 0:
                    reinforce_bonus = 86400.0  # +1 day weight
                elif h.times_incorrect > 0:
                    reinforce_bonus = 43200.0  # +12 hours weight

                # ZPD difficulty alignment
                diff_bonus = 21600.0 if q.difficulty == target_diff else 0.0

                return seconds_ago + reinforce_bonus + diff_bonus

            # Sort descending by exhaustion score
            sorted_seen = sorted(eligible_seen, key=exhaustion_score, reverse=True)
            top_seen = sorted_seen[:min(3, len(sorted_seen))]
            selected_question = random.choice(top_seen)

        if selected_question:
            # Record exposure
            await cls.record_question_exposure(db, student_id, selected_question.id)

        return selected_question


    @classmethod
    async def generate_adaptive_session(
        cls,
        db: AsyncSession,
        student_id: int,
        topic_id: Optional[int] = None,
        count: int = 5,
    ) -> Tuple[List[Question], Dict[str, Any]]:
        """
        Generates an adaptive practice set of questions.
        If topic_id is provided, focuses on that topic adapting difficulty.
        If topic_id is None, generates a multi-topic diagnostic mix prioritizing weak topics.
        """
        selected_questions: List[Question] = []
        selected_ids: List[int] = []

        for _ in range(count):
            q = await cls.select_adaptive_question(
                db=db,
                student_id=student_id,
                topic_id=topic_id,
                exclude_question_ids=selected_ids,
            )
            if q and q.id not in selected_ids:
                selected_questions.append(q)
                selected_ids.append(q.id)

        # Diagnostic overview
        insights = await cls.get_personalization_insights(db, student_id)

        return selected_questions, insights


    @classmethod
    async def record_attempt_and_update_state(
        cls,
        db: AsyncSession,
        student_id: int,
        question_id: int,
        selected_option_id: int,
        time_taken_seconds: int,
    ) -> Dict[str, Any]:
        """
        Records attempt and updates:
        - Elo rating (+/- based on expected vs actual)
        - Standardized IRT theta ability
        - Moving average accuracy
        - Response time smoothing
        - Adaptive streak
        - Returns adaptive feedback message & updated ratings
        """
        # Load question with options
        q_res = await db.execute(
            select(Question)
            .where(Question.id == question_id)
            .options(selectinload(Question.options))
        )
        question = q_res.scalar_one_or_none()
        if not question:
            raise ValueError("Question not found")

        correct_opt = next((o for o in question.options if o.is_correct), None)
        if not correct_opt:
            raise ValueError("Question has no correct option")

        is_correct = selected_option_id == correct_opt.id
        now = datetime.now(timezone.utc)

        # 1. Record practice attempt
        attempt = PracticeAttempt(
            student_id=student_id,
            question_id=question_id,
            selected_option_id=selected_option_id,
            is_correct=is_correct,
            time_taken_seconds=time_taken_seconds,
            attempted_at=now,
        )
        db.add(attempt)

        # 2. Update Question stats
        question.attempt_count += 1
        if is_correct:
            question.correct_count += 1

        # 3. Update TopicProgress
        topic_id = question.topic_id
        prog_res = await db.execute(
            select(TopicProgress)
            .where(TopicProgress.student_id == student_id)
            .where(TopicProgress.topic_id == topic_id)
        )
        prog = prog_res.scalar_one_or_none()
        if not prog:
            prog = TopicProgress(
                student_id=student_id,
                topic_id=topic_id,
                skill_rating=1000.0,
                irt_ability=0.0,
                recent_accuracy=0.5,
                avg_response_time_seconds=float(time_taken_seconds),
                streak=0,
            )
            db.add(prog)
            await db.flush()

        old_skill = prog.skill_rating
        old_theta = prog.irt_ability
        prog.questions_attempted += 1
        if is_correct:
            prog.questions_correct += 1
            prog.streak += 1
        else:
            prog.streak = 0

        # Calculate question Elo rating equivalent from IRT difficulty
        # b = 0.0 maps to 1000, b = +1.4 maps to 1250, b = -1.2 maps to 750
        q_rating = 1000.0 + (question.irt_difficulty * 200.0)

        # Elo update
        expected_elo = cls.calculate_elo_expected(old_skill, q_rating)
        actual_score = 1.0 if is_correct else 0.0
        k_factor = 32.0 if prog.questions_attempted < 20 else 16.0
        delta_elo = k_factor * (actual_score - expected_elo)
        prog.skill_rating = max(400.0, old_skill + delta_elo)

        # IRT theta ability update (gradient step)
        p_irt = cls.calculate_irt_probability(old_theta, question.irt_difficulty)
        delta_theta = 0.3 * (actual_score - p_irt)
        prog.irt_ability = max(-3.0, min(3.0, old_theta + delta_theta))

        # Recent accuracy exponential smoothing (alpha = 0.3)
        prog.recent_accuracy = (0.7 * prog.recent_accuracy) + (0.3 * actual_score)

        # Response time smoothing
        if time_taken_seconds > 0:
            prog.avg_response_time_seconds = (0.8 * prog.avg_response_time_seconds) + (0.2 * time_taken_seconds)

        prog.last_practiced = now

        # Generate Adaptive Feedback Message
        acc_pct = (prog.questions_correct / prog.questions_attempted) * 100.0
        feedback_messages = []

        if is_correct:
            if prog.streak >= 3:
                feedback_messages.append(
                    f"🔥 {prog.streak} in a row! Difficulty elevated to HARD."
                )
            elif delta_elo > 15:
                feedback_messages.append(
                    f"🎯 High-difficulty problem solved! Skill rating boosted by +{round(delta_elo)}."
                )
            else:
                feedback_messages.append("✅ Correct answer! Skill rating updated.")
        else:
            if acc_pct < 50.0:
                feedback_messages.append(
                    "📉 Topic identified as a focus area. Re-calibrating to foundational questions."
                )
            else:
                feedback_messages.append("❌ Incorrect. Explanation provided below.")

        if time_taken_seconds < 10 and is_correct:
            feedback_messages.append("⚡ Excellent speed! Demonstrating strong mastery.")
        elif time_taken_seconds > 90 and not is_correct:
            feedback_messages.append("⏱️ High time spent. Recommend reviewing theory notes.")

        adaptive_message = " ".join(feedback_messages)

        await cls.update_question_exposure_result(db, student_id, question_id, is_correct)

        # Commit practice attempt first so scoring engine incorporates it
        await db.commit()

        # Update student profile stats dynamically with authoritative scoring engine
        prof_res = await db.execute(select(StudentProfile).where(StudentProfile.id == student_id))
        prof = prof_res.scalar_one_or_none()
        if prof:
            from app.services.scoring import calculate_and_sync_student_scores
            await calculate_and_sync_student_scores(db, prof)


        return {
            "question_id": question_id,
            "selected_option_id": selected_option_id,
            "correct_option_id": correct_opt.id,
            "is_correct": is_correct,
            "points_earned": question.points if is_correct else 0,
            "explanation": question.explanation,
            "old_skill_rating": round(old_skill, 1),
            "new_skill_rating": round(prog.skill_rating, 1),
            "skill_delta": round(delta_elo, 1),
            "old_theta": round(old_theta, 2),
            "new_theta": round(prog.irt_ability, 2),
            "streak": prog.streak,
            "topic_accuracy": round(acc_pct, 1),
            "adaptive_message": adaptive_message,
            "recommended_next_difficulty": cls.difficulty_for_ability(prog.irt_ability, acc_pct / 100.0, prog.streak).value,
        }

    @classmethod
    async def get_personalization_insights(
        cls, db: AsyncSession, student_id: int
    ) -> Dict[str, Any]:
        """
        Produces actionable personalization insights for the student dashboard & practice hub.
        """
        analytics = await cls.get_student_topic_analytics(db, student_id)
        practiced = [a for a in analytics if a["questions_attempted"] >= 3]
        unexplored = [a for a in analytics if a["questions_attempted"] < 3]

        weak_topics = sorted([a for a in practiced if (a["accuracy"] or 0) < 50.0], key=lambda x: x["accuracy"] or 0)
        strong_topics = sorted([a for a in practiced if (a["accuracy"] or 0) >= 75.0], key=lambda x: -(x["accuracy"] or 0))
        improving_topics = [
            a for a in practiced
            if a["recent_accuracy"] > (a["accuracy"] or 0) + 10.0
        ]

        # Determine top recommendation
        if weak_topics:
            rec_topic = weak_topics[0]
            recommendation_banner = f"Your weakest topic: {rec_topic['topic_name']} ({rec_topic['accuracy']}% accuracy). Foundational practice recommended."
            recommended_topic_id = rec_topic["topic_id"]
        elif unexplored:
            rec_topic = unexplored[0]
            recommendation_banner = f"Explore new topic: {rec_topic['topic_name']}. Take a diagnostic session to calibrate your readiness."
            recommended_topic_id = rec_topic["topic_id"]
        elif strong_topics:
            rec_topic = strong_topics[0]
            recommendation_banner = f"You're excelling in {rec_topic['topic_name']} ({rec_topic['accuracy']}%). Advanced questions recommended to push your percentile."
            recommended_topic_id = rec_topic["topic_id"]
        else:
            recommendation_banner = "Complete introductory practice sessions to unlock personalized AI recommendations."
            recommended_topic_id = analytics[0]["topic_id"] if analytics else 1

        # Formulate actionable diagnostic tips
        tips = []
        if weak_topics:
            tips.append({
                "type": "WARNING",
                "title": f"Weak Area: {weak_topics[0]['topic_name']}",
                "description": f"Accuracy is {weak_topics[0]['accuracy']}%. The engine has reduced difficulty to help you master core concepts before re-attempting hard problems.",
                "topic_id": weak_topics[0]["topic_id"],
            })
        if strong_topics:
            tips.append({
                "type": "SUCCESS",
                "title": f"Strong Mastery: {strong_topics[0]['topic_name']}",
                "description": f"Accuracy is {strong_topics[0]['accuracy']}%. Engine has promoted your question bank to HARD difficulty problems.",
                "topic_id": strong_topics[0]["topic_id"],
            })
        if improving_topics:
            tips.append({
                "type": "TRENDING",
                "title": f"Upward Momentum: {improving_topics[0]['topic_name']}",
                "description": f"Recent accuracy is {improving_topics[0]['recent_accuracy']}%, showing significant improvement over earlier attempts.",
                "topic_id": improving_topics[0]["topic_id"],
            })

        return {
            "recommendation_banner": recommendation_banner,
            "recommended_topic_id": recommended_topic_id,
            "weak_topics": weak_topics[:3],
            "strong_topics": strong_topics[:3],
            "improving_topics": improving_topics[:3],
            "unexplored_count": len(unexplored),
            "tips": tips,
            "topic_analytics": analytics,
        }
