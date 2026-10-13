import axios, { AxiosError, AxiosInstance } from 'axios';
import type {
  TokenResponse, User, StudentDashboard, TrainerDashboard,
  Subject, Topic, Lesson, Question, PracticeAnswerResult,
  TopicProgress, Test, TestStartResponse, TestAttemptResult,
  TestHistoryItem, Batch, MessageResponse, AdaptiveInsights,
  CodingQuestionSummary, CodingQuestionDetail, CodeRunResponse,
  CodeSubmission, CodingAssessmentDetail, TrainerAnalyticsOverview,
  TrainerStudentProfile, MalpracticeReport, StudentClusterResult,
  PlagiarismReport, AnomalyReport, ChatMessage, AIAssistantResponse,
  AIAssistantStatus, BatchReadinessReport, StudentReadiness,
  AIChatSessionSummary, AIChatSessionDetail,
  StudentCoachMessage, StudentCoachSessionSummary, StudentCoachSessionDetail, StudentCoachResponse,
} from '@/types';

const BASE_URL = '/api';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: BASE_URL,
      headers: { 'Content-Type': 'application/json' },
      timeout: 15000,
    });

    // Attach JWT on every request
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Handle 401 — token expired
    this.client.interceptors.response.use(
      (r) => r,
      async (error: AxiosError) => {
        if (error.response?.status === 401) {
          const refreshToken = localStorage.getItem('refresh_token');
          if (refreshToken && !error.config?.url?.includes('/auth/refresh')) {
            try {
              const res = await axios.post(`${BASE_URL}/auth/refresh`, {
                refresh_token: refreshToken,
              });
              const data: TokenResponse = res.data;
              localStorage.setItem('access_token', data.access_token);
              localStorage.setItem('refresh_token', data.refresh_token);
              if (error.config) {
                error.config.headers.Authorization = `Bearer ${data.access_token}`;
                return this.client(error.config);
              }
            } catch {
              this.clearAuth();
              window.location.href = '/login';
            }
          } else {
            this.clearAuth();
            window.location.href = '/login';
          }
        }
        return Promise.reject(error);
      }
    );
  }

  private clearAuth() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  }

  extractError(err: unknown): string {
    if (axios.isAxiosError(err)) {
      return err.response?.data?.detail || err.message || 'Request failed';
    }
    return 'An unexpected error occurred';
  }

  // ── Auth ──────────────────────────────────────────────────────────────────

  async register(email: string, password: string, full_name: string, role = 'STUDENT'): Promise<TokenResponse> {
    const res = await this.client.post('/auth/register', { email, password, full_name, role });
    return res.data;
  }

  async login(email: string, password: string): Promise<TokenResponse> {
    const res = await this.client.post('/auth/login', { email, password });
    return res.data;
  }

  async logout(): Promise<MessageResponse> {
    const res = await this.client.post('/auth/logout');
    return res.data;
  }

  async getMe(): Promise<User> {
    const res = await this.client.get('/auth/me');
    return res.data;
  }

  // ── Student Dashboard ─────────────────────────────────────────────────────

  async getStudentDashboard(): Promise<StudentDashboard> {
    const res = await this.client.get('/students/dashboard');
    return res.data;
  }

  async getStudentProfile() {
    const res = await this.client.get('/students/profile');
    return res.data;
  }

  // ── Learning Hub ──────────────────────────────────────────────────────────

  async getSubjects(): Promise<Subject[]> {
    const res = await this.client.get('/students/subjects');
    return res.data;
  }

  async getTopics(subjectId: number): Promise<Topic[]> {
    const res = await this.client.get(`/students/subjects/${subjectId}/topics`);
    return res.data;
  }

  async getLessons(topicId: number): Promise<Lesson[]> {
    const res = await this.client.get(`/students/topics/${topicId}/lessons`);
    return res.data;
  }

  async completeLesson(lessonId: number, timeSpentSeconds: number): Promise<MessageResponse> {
    const res = await this.client.post(`/students/lessons/${lessonId}/complete`, null, {
      params: { time_spent_seconds: timeSpentSeconds },
    });
    return res.data;
  }

  // ── Practice ──────────────────────────────────────────────────────────────

  async startPracticeSession(topicId?: number, difficulty?: string, count = 10): Promise<Question[]> {
    const res = await this.client.post('/students/practice/session', {
      topic_id: topicId,
      difficulty,
      count,
    });
    return res.data;
  }

  async submitPracticeAnswer(
    questionId: number,
    selectedOptionId: number,
    timeTakenSeconds: number
  ): Promise<PracticeAnswerResult> {
    const res = await this.client.post('/students/practice/submit', {
      question_id: questionId,
      selected_option_id: selectedOptionId,
      time_taken_seconds: timeTakenSeconds,
    });
    return res.data;
  }

  async getAdaptiveInsights(): Promise<AdaptiveInsights> {
    const res = await this.client.get('/students/adaptive/insights');
    return res.data;
  }

  // ── Tests ─────────────────────────────────────────────────────────────────

  async getAvailableTests(): Promise<Test[]> {
    const res = await this.client.get('/students/tests');
    return res.data;
  }

  async startTest(testId: number): Promise<TestStartResponse> {
    const res = await this.client.post(`/students/tests/${testId}/start`);
    return res.data;
  }

  async submitTest(
    attemptId: number,
    answers: Array<{ question_id: number; selected_option_id: number; time_taken_seconds: number }>
  ): Promise<TestAttemptResult> {
    const res = await this.client.post('/students/tests/submit', {
      attempt_id: attemptId,
      answers,
    });
    return res.data;
  }

  async getTestHistory(): Promise<TestHistoryItem[]> {
    const res = await this.client.get('/students/tests/history');
    return res.data;
  }

  async getTestAttemptReview(attemptId: number): Promise<any> {
    const res = await this.client.get(`/students/tests/attempts/${attemptId}`);
    return res.data;
  }

  async getProgress(): Promise<TopicProgress[]> {
    const res = await this.client.get('/students/progress');
    return res.data;
  }

  // ── Proctoring ─────────────────────────────────────────────────────────────

  async logProctoringEvent(
    attemptId: number,
    eventType: string,
    severity: string,
    description?: string,
    eventMetadata?: Record<string, unknown>
  ) {
    await this.client.post('/proctoring/event', {
      attempt_id: attemptId,
      event_type: eventType,
      severity,
      description,
      event_metadata: eventMetadata,
    });
  }

  // ── Trainer ───────────────────────────────────────────────────────────────

  async getTrainerDashboard(): Promise<TrainerDashboard> {
    const res = await this.client.get('/trainers/dashboard');
    return res.data;
  }

  async getTrainerBatches(): Promise<Batch[]> {
    const res = await this.client.get('/trainers/batches');
    return res.data;
  }

  async createBatch(name: string, description?: string): Promise<Batch> {
    const res = await this.client.post('/trainers/batches', { name, description });
    return res.data;
  }

  async getBatchStudents(batchId: number) {
    const res = await this.client.get(`/trainers/batches/${batchId}/students`);
    return res.data;
  }

  async getTrainerTests(): Promise<Test[]> {
    const res = await this.client.get('/trainers/tests');
    return res.data;
  }

  async createTest(payload: {
    title: string; description?: string; test_type: string;
    batch_id?: number; duration_minutes: number; total_marks: number;
    passing_marks: number; instructions?: string; question_ids: number[];
  }): Promise<Test> {
    const res = await this.client.post('/trainers/tests', payload);
    return res.data;
  }

  async publishTest(testId: number): Promise<MessageResponse> {
    const res = await this.client.post(`/trainers/tests/${testId}/publish`);
    return res.data;
  }

  async getTestResults(testId: number) {
    const res = await this.client.get(`/trainers/tests/${testId}/results`);
    return res.data;
  }

  async getQuestions(topicId?: number) {
    const res = await this.client.get('/trainers/questions', {
      params: topicId ? { topic_id: topicId } : undefined,
    });
    return res.data;
  }

  // ── Step 2: Coding Practice & Assessments ──────────────────────────────────

  async getCodingQuestions(params?: { difficulty?: string; topic_id?: number; search?: string }): Promise<CodingQuestionSummary[]> {
    const res = await this.client.get('/students/coding/questions', { params });
    return res.data;
  }

  async getCodingQuestion(idOrSlug: string): Promise<CodingQuestionDetail> {
    const res = await this.client.get(`/students/coding/questions/${idOrSlug}`);
    return res.data;
  }

  async runCode(questionId: number, sourceCode: string, language: string): Promise<CodeRunResponse> {
    const res = await this.client.post(`/students/coding/questions/${questionId}/run`, {
      source_code: sourceCode,
      language,
    });
    return res.data;
  }

  async submitCode(questionId: number, sourceCode: string, language: string, attemptId?: number): Promise<CodeSubmission> {
    const res = await this.client.post(`/students/coding/questions/${questionId}/submit`, {
      source_code: sourceCode,
      language,
      attempt_id: attemptId,
    });
    return res.data;
  }

  async getCodingSubmissions(questionId?: number): Promise<CodeSubmission[]> {
    const res = await this.client.get('/students/coding/submissions', {
      params: questionId ? { question_id: questionId } : undefined,
    });
    return res.data;
  }

  async getCodingSubmission(submissionId: number): Promise<CodeSubmission> {
    const res = await this.client.get(`/students/coding/submissions/${submissionId}`);
    return res.data;
  }

  async startCodingAssessment(testId: number): Promise<CodingAssessmentDetail> {
    const res = await this.client.post(`/students/coding/assessments/${testId}/start`);
    return res.data;
  }

  async finalizeCodingAssessment(testId: number) {
    const res = await this.client.post(`/students/coding/assessments/${testId}/finalize`);
    return res.data;
  }

  async getCodingAssessmentTime(testId: number): Promise<{ attempt_id: number; remaining_seconds: number; is_expired: boolean }> {
    const res = await this.client.get(`/students/coding/assessments/${testId}/time`);
    return res.data;
  }

  // ── Step 2: Trainer Analytics & ML ─────────────────────────────────────────

  async getTrainerAnalyticsOverview(): Promise<TrainerAnalyticsOverview> {
    const res = await this.client.get('/trainers/analytics/overview');
    return res.data;
  }

  async getTrainerStudentProfile(studentId: number): Promise<TrainerStudentProfile> {
    const res = await this.client.get(`/trainers/analytics/students/${studentId}`);
    return res.data;
  }

  async getTrainerCodingAnalytics() {
    const res = await this.client.get('/trainers/analytics/coding');
    return res.data;
  }

  async getTrainerTopicsAnalytics() {
    const res = await this.client.get('/trainers/analytics/topics');
    return res.data;
  }

  async getTrainerMalpracticeReport(testId: number): Promise<MalpracticeReport> {
    const res = await this.client.get(`/trainers/analytics/malpractice/${testId}`);
    return res.data;
  }

  async getTrainerClustering(batchId?: number): Promise<StudentClusterResult> {
    const res = await this.client.get('/trainers/analytics/clustering', {
      params: batchId ? { batch_id: batchId } : undefined,
    });
    return res.data;
  }

  async getTrainerPlagiarismReport(questionId?: number, testId?: number): Promise<PlagiarismReport> {
    const res = await this.client.get('/trainers/analytics/plagiarism', {
      params: { question_id: questionId, test_id: testId },
    });
    return res.data;
  }

  async getTrainerAnomaliesReport(testId: number): Promise<AnomalyReport> {
    const res = await this.client.get(`/trainers/analytics/anomalies/${testId}`);
    return res.data;
  }

  // ─── Step 3 AI Assistant & Placement Readiness ─────────────────────────────

  async getTrainerChatSessions(): Promise<AIChatSessionSummary[]> {
    const res = await this.client.get('/trainers/assistant/sessions');
    return res.data;
  }

  async createTrainerChatSession(title?: string): Promise<AIChatSessionSummary> {
    const res = await this.client.post('/trainers/assistant/sessions', { title });
    return res.data;
  }

  async getTrainerChatSession(sessionId: number): Promise<AIChatSessionDetail> {
    const res = await this.client.get(`/trainers/assistant/sessions/${sessionId}`);
    return res.data;
  }

  async deleteTrainerChatSession(sessionId: number): Promise<{ message: string }> {
    const res = await this.client.delete(`/trainers/assistant/sessions/${sessionId}`);
    return res.data;
  }

  async sendAIAssistantChat(query: string, history?: ChatMessage[], sessionId?: number): Promise<AIAssistantResponse> {
    const res = await this.client.post(
      '/trainers/assistant/chat',
      { query, conversation_history: history, session_id: sessionId },
      { timeout: 95000 } // Extended timeout for local Gemma 12B inference
    );
    return res.data;
  }

  async getAIAssistantStatus(): Promise<AIAssistantStatus> {
    const res = await this.client.get('/trainers/assistant/status');
    return res.data;
  }

  async getBatchReadiness(batchId?: number): Promise<BatchReadinessReport> {
    const res = await this.client.get('/trainers/analytics/readiness', {
      params: batchId ? { batch_id: batchId } : undefined,
    });
    return res.data;
  }

  async getStudentReadiness(studentId: number): Promise<{ student_id: number; full_name: string; email: string; prediction: any }> {
    const res = await this.client.get(`/trainers/analytics/readiness/${studentId}`);
    return res.data;
  }

  async retrainReadinessModel(): Promise<any> {
    const res = await this.client.post('/trainers/analytics/retrain-readiness');
    return res.data;
  }

  // ── Student AI Placement Coach ─────────────────────────────────────────────

  async getStudentCoachStatus(): Promise<{ available: boolean; provider: string; model: string; mode: string }> {
    const res = await this.client.get('/students/coach/status');
    return res.data;
  }

  async getStudentCoachSessions(): Promise<StudentCoachSessionSummary[]> {
    const res = await this.client.get('/students/coach/sessions');
    return res.data;
  }

  async createStudentCoachSession(title?: string): Promise<StudentCoachSessionSummary> {
    const res = await this.client.post('/students/coach/sessions', { title });
    return res.data;
  }

  async getStudentCoachSession(sessionId: number): Promise<StudentCoachSessionDetail> {
    const res = await this.client.get(`/students/coach/sessions/${sessionId}`);
    return res.data;
  }

  async updateStudentCoachSession(sessionId: number, title: string): Promise<StudentCoachSessionSummary> {
    const res = await this.client.patch(`/students/coach/sessions/${sessionId}`, { title });
    return res.data;
  }

  async deleteStudentCoachSession(sessionId: number): Promise<{ message: string }> {
    const res = await this.client.delete(`/students/coach/sessions/${sessionId}`);
    return res.data;
  }

  async sendStudentCoachChat(params: {
    query: string;
    sessionId?: number;
    history?: { role: string; content: string }[];
    questionContext?: { question_id?: number; attempt_id?: number };
  }): Promise<StudentCoachResponse> {
    const res = await this.client.post(
      '/students/coach/chat',
      {
        query: params.query,
        session_id: params.sessionId,
        conversation_history: params.history,
        question_context: params.questionContext,
      },
      { timeout: 95000 }
    );
    return res.data;
  }
}

export const api = new ApiClient();
export default api;
