// ─── Auth & User Types ─────────────────────────────────────────────────────

export type UserRole = 'STUDENT' | 'TRAINER' | 'ADMIN';

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface StudentProfile {
  id: number;
  user_id: number;
  college?: string;
  department?: string;
  graduation_year?: number;
  phone?: string;
  bio?: string;
  total_score: number;
  aptitude_score: number;
  coding_score: number;
  streak_days: number;
  last_active?: string;
}

export interface TrainerProfile {
  id: number;
  user_id: number;
  specialization?: string;
  experience_years?: number;
  phone?: string;
  bio?: string;
}

// ─── Batch Types ─────────────────────────────────────────────────────────────

export interface Batch {
  id: number;
  name: string;
  description?: string;
  is_active: boolean;
  start_date?: string;
  end_date?: string;
  created_at: string;
  member_count?: number;
}

// ─── Content Types ────────────────────────────────────────────────────────────

export type SubjectCategory = 'APTITUDE' | 'PROGRAMMING';
export type Difficulty = 'EASY' | 'MEDIUM' | 'HARD';
export type QuestionType = 'MCQ' | 'TRUE_FALSE';

export interface Subject {
  id: number;
  name: string;
  category: SubjectCategory;
  description?: string;
  icon?: string;
  order_index: number;
}

export interface Topic {
  id: number;
  subject_id: number;
  name: string;
  description?: string;
  order_index: number;
  total_lessons?: number;
  total_questions?: number;
}

export interface Lesson {
  id: number;
  topic_id: number;
  title: string;
  content: string;
  examples?: string;
  order_index: number;
  estimated_minutes: number;
}

export interface QuestionOption {
  id: number;
  text: string;
  order_index: number;
  is_correct?: boolean; // only present after submission
}

export interface Question {
  id: number;
  topic_id?: number;
  text: string;
  question_type: QuestionType;
  difficulty: Difficulty;
  explanation?: string;
  points: number;
  options: QuestionOption[];
}

export interface PracticeAnswerResult {
  question_id: number;
  selected_option_id: number;
  is_correct: boolean;
  correct_option_id: number;
  explanation?: string;
  points_earned: number;
  old_skill_rating?: number;
  new_skill_rating?: number;
  skill_delta?: number;
  old_theta?: number;
  new_theta?: number;
  streak?: number;
  topic_accuracy?: number;
  adaptive_message?: string;
  recommended_next_difficulty?: string;
}

export interface AdaptiveTopicMetric {
  topic_id: number;
  topic_name: string;
  questions_attempted: number;
  questions_correct: number;
  questions_incorrect: number;
  accuracy: number | null;
  recent_accuracy: number;
  skill_rating: number;
  irt_ability: number;
  avg_response_time_seconds: number;
  streak: number;
  category: 'EXPLORING' | 'WEAK' | 'DEVELOPING' | 'STRONG';
  category_label: string;
}

export interface AdaptiveTip {
  type: 'WARNING' | 'SUCCESS' | 'TRENDING';
  title: string;
  description: string;
  topic_id: number;
}

export interface AdaptiveInsights {
  recommendation_banner: string;
  recommended_topic_id: number;
  weak_topics: AdaptiveTopicMetric[];
  strong_topics: AdaptiveTopicMetric[];
  improving_topics: AdaptiveTopicMetric[];
  unexplored_count: number;
  tips: AdaptiveTip[];
  topic_analytics: AdaptiveTopicMetric[];
}

export interface TopicProgress {
  topic_id: number;
  topic_name?: string;
  lessons_completed: number;
  total_lessons: number;
  questions_attempted: number;
  questions_correct: number;
  skill_rating: number;
  irt_ability?: number;
  recent_accuracy?: number;
  avg_response_time_seconds?: number;
  streak?: number;
  accuracy?: number;
  last_practiced?: string;
}

// ─── Test Types ───────────────────────────────────────────────────────────────

export type TestType = 'APTITUDE' | 'CODING' | 'MIXED';
export type TestStatus = 'DRAFT' | 'PUBLISHED' | 'ARCHIVED';
export type AttemptStatus = 'IN_PROGRESS' | 'SUBMITTED' | 'TIMED_OUT' | 'GRADED';

export interface Test {
  id: number;
  title: string;
  description?: string;
  test_type: TestType;
  status: TestStatus;
  batch_id?: number;
  duration_minutes: number;
  total_marks: number;
  passing_marks: number;
  instructions?: string;
  randomize_questions: boolean;
  show_results_immediately: boolean;
  scheduled_at?: string;
  created_at: string;
  question_count?: number;
}

export interface TestStartResponse {
  attempt_id: number;
  test_id: number;
  expires_at: string;
  questions: Question[];
}

export interface TestAttemptResult {
  id: number;
  test_id: number;
  student_id: number;
  status: AttemptStatus;
  started_at: string;
  submitted_at?: string;
  score?: number;
  max_score?: number;
  percentage?: number;
  passed?: boolean;
}

export interface TestHistoryItem {
  attempt_id: number;
  test_id: number;
  test_title: string;
  score?: number;
  max_score?: number;
  percentage?: number;
  status: AttemptStatus;
  submitted_at?: string;
}

// ─── Dashboard Types ──────────────────────────────────────────────────────────

export interface StudentDashboard {
  student: {
    id: number;
    full_name: string;
    total_score: number;
    aptitude_score: number;
    coding_score: number;
    streak_days: number;
  };
  recent_tests: Array<{
    attempt_id: number;
    test_title: string;
    score?: number;
    percentage?: number;
    submitted_at?: string;
  }>;
  weak_topics: Array<{
    topic_id: number;
    topic_name: string;
    accuracy: number;
    skill_rating: number;
    questions_attempted?: number;
    questions_correct?: number;
    category_label?: string;
  }>;
  practice_count: number;
  tests_taken: number;
  topic_progress_count: number;
}

export interface TrainerDashboard {
  trainer: {
    id: number;
    full_name: string;
    specialization?: string;
  };
  batch_count: number;
  student_count: number;
  recent_tests: Array<{
    id: number;
    title: string;
    status: TestStatus;
    created_at: string;
  }>;
  batch_performance: Array<{
    batch_id: number;
    batch_name: string;
    avg_score: number;
    student_count: number;
  }>;
}

// ─── Proctoring Types ─────────────────────────────────────────────────────────

export interface ProctoringEvent {
  id: number;
  event_type: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH';
  description?: string;
  occurred_at: string;
}

// ─── Step 2: Coding & Execution Types ─────────────────────────────────────────

export interface CodingTestCase {
  id: number;
  is_sample: boolean;
  order_index: number;
  input?: string;
  expected_output?: string;
}

export interface CodingQuestionSummary {
  id: number;
  title: string;
  slug: string;
  difficulty: 'EASY' | 'MEDIUM' | 'HARD';
  topic_id?: number;
  topic_name?: string;
  marks: number;
  tags: string[];
  attempt_count: number;
  accept_count: number;
  acceptance_rate?: number;
  supported_languages: string[];
}

export interface CodingQuestionDetail {
  id: number;
  title: string;
  slug: string;
  difficulty: 'EASY' | 'MEDIUM' | 'HARD';
  topic_id?: number;
  topic_name?: string;
  problem_statement: string;
  constraints?: string;
  input_format?: string;
  output_format?: string;
  examples?: Array<{ input: string; output: string; explanation?: string }>;
  explanation?: string;
  supported_languages: string[];
  time_limit_ms: number;
  memory_limit_mb: number;
  marks: number;
  tags: string[];
  sample_test_cases: CodingTestCase[];
}

export interface TestCaseExecutionResult {
  test_case_id: number;
  is_sample: boolean;
  status: string;
  passed: boolean;
  runtime_ms: number;
  memory_kb: number;
  stdout?: string;
  stderr?: string;
  compile_output?: string;
  input?: string;
  expected_output?: string;
}

export interface CodeRunResponse {
  verdict: string;
  total_tests: number;
  passed_tests: number;
  execution_time_ms: number;
  memory_kb: number;
  compile_output?: string;
  stdout?: string;
  stderr?: string;
  test_results: TestCaseExecutionResult[];
}

export interface CodeSubmission {
  id: number;
  student_id: number;
  coding_question_id: number;
  question_title?: string;
  attempt_id?: number;
  language: string;
  source_code: string;
  verdict: string;
  score: number;
  test_cases_passed: number;
  test_cases_total: number;
  runtime_ms?: number;
  memory_kb?: number;
  compile_output?: string;
  submitted_at: string;
  test_results: TestCaseExecutionResult[];
}

export interface CodingAssessmentQuestion extends CodingQuestionDetail {
  user_submission?: CodeSubmission;
}

export interface CodingAssessmentDetail {
  test_id: number;
  attempt_id: number;
  title: string;
  description?: string;
  duration_minutes: number;
  total_marks: number;
  passing_marks: number;
  instructions?: string;
  remaining_seconds: number;
  is_expired: boolean;
  started_at: string;
  expires_at?: string;
  questions: CodingAssessmentQuestion[];
}

// ─── Step 2: Trainer Analytics Types ─────────────────────────────────────────

export interface TrainerAnalyticsOverview {
  student_count: number;
  avg_aptitude_score: number;
  avg_coding_score: number;
  avg_test_score: number;
  completion_rate: number;
  at_risk_count: number;
  at_risk_students: Array<{
    student_id: number;
    full_name: string;
    email: string;
    total_score: number;
    aptitude_score: number;
    coding_score: number;
    primary_risk: string;
  }>;
}

export interface TrainerStudentProfile {
  student: {
    id: number;
    full_name: string;
    email: string;
    aptitude_score: number;
    coding_score: number;
    total_score: number;
    streak_days: number;
  };
  weak_topics: Array<{ topic_id: number; topic_name: string; attempted: number; accuracy: number; skill_rating: number; irt_ability: number }>;
  strong_topics: Array<{ topic_id: number; topic_name: string; attempted: number; accuracy: number; skill_rating: number; irt_ability: number }>;
  topic_metrics: Array<{ topic_id: number; topic_name: string; attempted: number; accuracy: number; skill_rating: number; irt_ability: number; recent_accuracy: number; streak: number }>;
  test_history: Array<{ attempt_id: number; test_title: string; score?: number; max_score?: number; percentage?: number; status: string; violations_count: number; date: string }>;
  coding_history: Array<{ submission_id: number; question_title: string; language: string; verdict: string; score: number; passed_tests: number; total_tests: number; runtime_ms?: number; submitted_at: string }>;
}

export interface MalpracticeReport {
  test_id: number;
  total_attempts: number;
  high_risk_count: number;
  medium_risk_count: number;
  low_risk_count: number;
  student_reports: Array<{
    attempt_id: number;
    student_id: number;
    student_name: string;
    score?: number;
    percentage?: number;
    status: string;
    risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
    total_violations: number;
    weighted_severity: number;
    breakdown: Record<string, number>;
    events_timeline: Array<{ event_type: string; severity: string; occurred_at: string; description?: string }>;
  }>;
}

export interface StudentClusterResult {
  status: 'SUCCESS' | 'INSUFFICIENT_DATA';
  message?: string;
  clusters: Array<{
    cluster_id: number;
    label: string;
    student_count: number;
    avg_aptitude: number;
    avg_coding: number;
    avg_test_score: number;
    avg_completion: number;
    avg_streak: number;
  }>;
  students: Array<{
    student_id: number;
    full_name: string;
    email: string;
    cluster_id: number;
    performance_group: string;
    aptitude_score: number;
    coding_score: number;
    avg_test_score: number;
  }>;
}

export interface PlagiarismReport {
  total_analyzed: number;
  flagged_pairs_count: number;
  flagged_pairs: Array<{
    student_a_id: number;
    student_a_name: string;
    submission_a_id: number;
    student_b_id: number;
    student_b_name: string;
    submission_b_id: number;
    similarity_score: number;
    risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
    is_flagged: boolean;
    language: string;
  }>;
}

export interface AnomalyReport {
  status: 'SUCCESS' | 'INSUFFICIENT_DATA';
  message?: string;
  anomalies: Array<{
    attempt_id: number;
    student_id: number;
    student_name: string;
    test_id: number;
    test_title: string;
    duration_seconds: number;
    score_percentage: number;
    violation_count: number;
    anomaly_score: number;
    risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
    detected_signals: string[];
  }>;
  total_evaluated: number;
  anomaly_count?: number;
}

// ─── API Response Types ───────────────────────────────────────────────────────

export interface ApiError {
  detail: string;
}

export interface MessageResponse {
  message: string;
}

// ─── Step 3 AI Assistant & Placement Readiness Types ─────────────────────────

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface AIAssistantResponse {
  reply: string;
  tool_called?: string;
  tool_arguments?: Record<string, any>;
  structured_data?: any;
  model_used: string;
  status: string;
  session_id?: number;
  error?: string;
  intent?: string;
}

export interface AIChatSessionSummary {
  id: number;
  trainer_id: number;
  title: string;
  created_at: string;
  updated_at: string;
  message_count?: number;
}

export interface AIChatMessageItem {
  id: number;
  session_id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  tool_name?: string;
  tool_result_metadata?: any;
  created_at: string;
}

export interface AIChatSessionDetail extends AIChatSessionSummary {
  messages: AIChatMessageItem[];
}

export interface AIAssistantStatus {
  available: boolean;
  provider: string;
  model: string;
  base_url?: string;
}

export interface StudentReadiness {
  student_id: number;
  full_name: string;
  email: string;
  readiness_score: number;
  readiness_category: 'NEEDS_IMPROVEMENT' | 'DEVELOPING' | 'PLACEMENT_READY';
  confidence: number;
  status: string;
  contributing_factors?: {
    strengths: string[];
    areas_for_improvement: string[];
  };
  probabilities?: {
    needs_improvement: number;
    developing: number;
    placement_ready: number;
  };
}

export interface BatchReadinessReport {
  status: 'SUCCESS' | 'INSUFFICIENT_DATA';
  message?: string;
  total_students: number;
  readiness_summary: {
    placement_ready_count: number;
    developing_count: number;
    needs_improvement_count: number;
  };
  students: StudentReadiness[];
}

// ─── Student AI Placement Coach Types ─────────────────────────────────────────

export interface StudentCoachMessage {
  id: number;
  session_id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  tool_name?: string;
  tool_result_metadata?: any;
  created_at: string;
}

export interface StudentCoachSessionSummary {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface StudentCoachSessionDetail {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
  messages: StudentCoachMessage[];
}

export interface StudentCoachResponse {
  reply: string;
  tool_called?: string;
  structured_data?: any;
  intent: string;
  model_used: string;
  status: string;
  session_id?: number;
  error?: string;
}
