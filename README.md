# CareerForge AI — Placement Readiness Platform

CareerForge AI is an integrated, production-oriented placement readiness platform that unifies adaptive aptitude learning, proctored coding assessments, automated anti-malpractice tracking, machine learning analytics, and a local Gemma 12B AI assistant for trainers.

---

## 🧠 The Three Intelligence Layers of CareerForge AI

CareerForge AI separates intelligence into three explicit layers:

### Layer 1: Adaptive Aptitude Engine (Psychometric / IRT + Elo)
- **Continuous Skill Tracking**: Dynamic Elo rating updates per student per topic based on response correctness and item difficulty.
- **1PL Rasch IRT Scaling**: Questions are dynamically surfaced to match candidate ability; weak topics are prioritized to rebuild foundation, and strong topics escalate in difficulty to challenge high performers.
- **Exploration vs. Exploitation**: New candidates receive a balanced diagnostic distribution before transitioning into targeted adaptive recommendations.

### Layer 2: Machine Learning Intelligence Layer
- **XGBoost Placement Readiness Prediction** (`app.ml.readiness_model`):
  - Predicts placement readiness probability across 10 tabular performance features (`aptitude_accuracy`, `topic_mastery`, `coding_score`, `assessment_score`, `coding_problem_solving_rate`, `improvement_trend`, `test_completion_rate`, `avg_response_time`, `practice_frequency`, `difficulty_performance`).
  - Classifies students into: `NEEDS_IMPROVEMENT`, `DEVELOPING`, or `PLACEMENT_READY`.
  - Computes top positive strengths and areas for improvement.
  - **Graceful Insufficient Data State**: Returns a safe, uninflated `INSUFFICIENT_DATA` status when candidate records are insufficient, preventing fabricated certainty.
- **K-Means Student Grouping** (`app.ml.clustering`):
  - Discovers natural cohort performance tiers with dynamically evaluated centroid ordering (*High Performer*, *Developing*, *Needs Attention*).
- **Isolation Forest Behavioral Anomaly Detection** (`app.ml.anomaly`):
  - Identifies rapid assessment velocity, suspicious submission spikes, and proctoring telemetry outliers.
- **Structural Code Plagiarism Detection** (`app.ml.plagiarism`):
  - Code normalization, comment/whitespace stripping, identifier anonymization (`$V1`, `$V2`), and sequence + 4-gram Jaccard similarity.
- **Bayesian IRT Difficulty Calibration** (`app.ml.irt_calibration`):
  - Empirical Laplace-smoothed log-odds recalibration of question difficulties using actual student attempt histories.

### Layer 3: Gemma 12B AI Assistant (LLM via Ollama)
- **Local Model**: Powered exclusively by **Gemma 12B** (`gemma4:12b-mlx`) served locally via **Ollama**. (No remote dependencies or external API costs required).
- **FastAPI LLM Provider Abstraction** (`LLMProvider` / `OllamaProvider`):
  - Clean separation allowing seamless future swaps between models/backends.
  - The frontend never communicates directly with Ollama.
- **Safe Parameter-Validated Tool Calling**:
  - The LLM cannot access PostgreSQL directly, has no SQL execution tools, and cannot execute arbitrary shell commands.
  - LLM queries are grounded via approved backend tools:
    - `get_weak_students(topic, batch_id)`
    - `get_batch_summary(batch_id)`
    - `get_student_performance(student_id)`
    - `get_placement_readiness(student_id, batch_id)`
    - `get_at_risk_students(batch_id)`
    - `get_coding_performance(batch_id)`
    - `get_malpractice_summary(test_id)`
    - `get_anomaly_results(batch_id)`
- **Strict Trainer Data Isolation & RBAC**:
  - All tool executions validate that queried students and batches belong to the trainer's authorized cohort. Cross-batch data requests return access denied.
- **Prompt-Injection Defense**:
  - Treats user prompts as untrusted. Strictly refuses attempts to dump database credentials, override instructions, or execute unauthorized operations.
- **Resilience**:
  - If Ollama is offline or loading, CareerForge detects this gracefully and keeps all other platform features fully operational.

---

## 🏗 System Architecture

```
[Student / Trainer React Frontend (Vite + TypeScript)]
       │
       ├── Monaco Code Editor & Public Test Runner
       ├── Anti-Malpractice Telemetry (Tab / Blur / Fullscreen / Clipboard)
       ├── Trainer Analytics Hub (K-Means, Readiness, Anomalies, Plagiarism)
       └── Trainer AI Assistant Chat (Gemma 12B Grounded UI)
       │
       ▼ (REST API + JWT Auth + Strict RBAC)
[FastAPI Backend Application]
       │
       ├── Layer 1: Adaptive IRT & Elo Engine
       ├── Layer 2: ML Engine (XGBoost, Isolation Forest, K-Means, Plagiarism)
       ├── Layer 3: AI Assistant Service (Ollama Provider + Tool Execution)
       ├── Isolated Judge0 Client ───► [Judge0 Sandbox / Mock] (Zero Host Execution)
       ▼
[PostgreSQL Database (careerforge_db)]
       ├── Users, Profiles, Batches, Memberships
       ├── Subjects, Topics, Lessons, Questions, Options, TopicProgress
       ├── Coding Questions, Test Cases, Code Submissions
       ├── Tests, Test Questions, Test Attempts, Proctoring Events
       └── ML Readiness Model Artifacts (`app/ml/artifacts/`)
```

---

## ⚙️ Environment Variables

Configure in `backend/.env` (see `backend/.env.example`):

```bash
# Application
APP_NAME="CareerForge AI"
APP_ENV=development
DEBUG=true
SECRET_KEY=change_this_to_a_long_random_secret_key_in_production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database (PostgreSQL active on port 5433 or 5432)
DATABASE_URL=postgresql+asyncpg://careerforge:password@localhost:5433/careerforge_db
DATABASE_URL_SYNC=postgresql://careerforge:password@localhost:5433/careerforge_db

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Judge0 (Code Execution)
JUDGE0_BASE_URL=https://judge0-ce.p.rapidapi.com
JUDGE0_API_KEY=your_judge0_api_key_here
JUDGE0_HOST=judge0-ce.p.rapidapi.com

# AI Assistant (Gemma 12B via Ollama)
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma4:12b-mlx
AI_MAX_TOKENS=2048
AI_TEMPERATURE=0.2
```

---

## 🚀 Running Locally

### 1. PostgreSQL Database
Ensure PostgreSQL is running:
```bash
# Connects to careerforge_db as defined in backend/.env
```

### 2. Ollama & Gemma 12B
Verify that Ollama is serving the model:
```bash
ollama list
# Expected: gemma4:12b-mlx
ollama serve
```

### 3. Backend (FastAPI)
```bash
cd backend
source venv/bin/activate

# Seed demo database (creates demo trainers, students, questions, tests)
python seed.py

# Start uvicorn server
uvicorn app.main:app --port 8000 --host 127.0.0.1 --reload
```
Swagger API docs: `http://127.0.0.1:8000/docs`

### 4. Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```
Open browser: `http://localhost:5173`

---

## 🧪 Running Automated Tests

Run the complete test suite (Steps 1, 2, and 3):
```bash
cd backend
source venv/bin/activate
pytest tests/test_step1.py tests/test_adaptive_engine.py tests/test_step2_coding.py tests/test_step3_ai_ml.py -v
```

Build the frontend bundle:
```bash
cd frontend
npm run build
```

---

## 🔑 Demo Credentials
| Role | Email | Password |
|---|---|---|
| Trainer | `trainer@careerforge.ai` | `Trainer@1234` |
| Student | `student@careerforge.ai` | `Student@1234` |
| Student | `alice@example.com` | `Student@1234` |
| Admin | `admin@careerforge.ai` | `Admin@1234` |
