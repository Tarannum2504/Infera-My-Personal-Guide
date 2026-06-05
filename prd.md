# Product Requirements Document (PRD): Infera

## 1. Product Overview
**Product Name:** Infera
**Description:** An AI-powered personal career guide and interview coach designed to help users prepare for technical interviews, analyze resumes, and track their upskilling journey.
**Target Audience:** Job seekers, freshers, and professionals aiming for technical roles in data analytics, software engineering, and consulting (specifically targeting companies like Celebal, TCS, and Optum).

## 2. Key Objectives
- **Interview Readiness:** Improve user performance through dynamic, role-specific mock interviews.
- **Resume Optimization:** Analyze and optimize resumes for ATS (Applicant Tracking Systems) to consistently score 85+/100.
- **Progress Tracking:** Provide a clear, actionable dashboard for tracking sprint progress, skill gaps, and project completions.
- **Accessible Support:** Offer conversational AI support in both English and Hinglish to cater to a broader demographic.

## 3. Features & Requirements

### 3.1. AI Interview Coach
- **Functionality:** Conduct text-based mock interviews with dynamic questioning based on the user's target company.
- **Requirements:** 
  - Support conversational cross-questioning and follow-ups.
  - Detect user knowledge gaps in real-time.
  - Provide direct, concise answers (hard-capped at ~200-250 words) to prevent "Wikipedia-style" info dumps.

### 3.2. Resume Analyzer
- **Functionality:** Ingest PDF and DOCX files to extract text and analyze against company-specific rubrics.
- **Requirements:** 
  - Identify missing technical keywords (e.g., Azure, Databricks, Power BI).
  - Detect weak language and suggest high-impact action verb replacements.
  - Score the resume out of 100 based on format, impact, and keyword density.
  - Retain analysis history in the database for conversational follow-ups (e.g., "Why is my score low?").

### 3.3. Dynamic Dashboard
- **Functionality:** Provide real-time metrics of the user's progress.
- **Requirements:** 
  - Display radar charts for granular technical skills (SQL, Python, Power BI, Azure, etc.).
  - Display bar charts tracking mock interview score trends over time.
  - Track structured sprint progress (e.g., Week 4 of 12).
  - Manage a checklist of required portfolio projects with trackable statuses (Not Started, In Progress, Built).

### 3.4. Hinglish Support
- **Functionality:** Allow users to ask questions using Hindi-English mixed vocabulary.
- **Requirements:** 
  - Detect Hinglish markers (e.g., "kya", "kaise", "samjhao").
  - Formulate and return responses in a natural, helpful Hinglish dialect.

## 4. Technical Architecture
- **Frontend:** React, TypeScript, Tailwind CSS, Recharts (for data visualization).
- **Backend:** FastAPI, SQLAlchemy, `pdfplumber` & `python-docx` (for file parsing).
- **Database:** PostgreSQL.
- **AI Integration:** Hugging Face Inference API utilizing large language models (e.g., `Qwen/Qwen2.5-72B-Instruct`).
- **Deployment:** Fully containerized utilizing Docker Compose, designed for easy cloud deployment on platforms like Railway or Render.

## 5. Future Scope
- Voice-based mock interviews with real-time speech-to-text.
- Direct integrations with job boards like LinkedIn and Indeed.
- Expanded target company rubrics to cover FAANG and other major tech firms.
- Automated technical quiz generation based on user weak points.
