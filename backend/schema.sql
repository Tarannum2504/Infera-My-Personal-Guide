-- Users
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) DEFAULT 'Ishara',
    location VARCHAR(100) DEFAULT 'Jodhpur',
    year_of_study INTEGER DEFAULT 3,
    branch VARCHAR(100) DEFAULT 'CSE AI/ML',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- User profiles with skills
CREATE TABLE IF NOT EXISTS user_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    skills JSONB DEFAULT '{
        "SQL": 80, "Python": 65, "Power BI": 20,
        "Statistics": 40, "Business Analytics": 35,
        "Azure": 15, "Databricks": 5, "DSA": 30,
        "DBMS": 72, "OOP": 68, "Communication": 55
    }'::jsonb,
    target_companies JSONB DEFAULT '["Celebal Technologies","TCS Digital","Optum"]'::jsonb,
    current_sprint_week INTEGER DEFAULT 1,
    placement_readiness INTEGER DEFAULT 70,
    projects JSONB DEFAULT '[]'::jsonb,
    certifications JSONB DEFAULT '[]'::jsonb,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chat sessions
CREATE TABLE IF NOT EXISTS chat_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) DEFAULT 'New Chat',
    session_type VARCHAR(50) DEFAULT 'chat',
    company_context VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chat messages
CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'infera')),
    content TEXT NOT NULL,
    message_type VARCHAR(50) DEFAULT 'text',
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Mock interviews
CREATE TABLE IF NOT EXISTS mock_interviews (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    company VARCHAR(100),
    interview_round VARCHAR(100),
    questions JSONB DEFAULT '[]'::jsonb,
    answers JSONB DEFAULT '[]'::jsonb,
    scores JSONB DEFAULT '[]'::jsonb,
    overall_score DECIMAL(5,2),
    feedback_summary TEXT,
    weak_areas JSONB DEFAULT '[]'::jsonb,
    status VARCHAR(50) DEFAULT 'in_progress',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Quiz sessions
CREATE TABLE IF NOT EXISTS quiz_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    topic VARCHAR(100),
    company VARCHAR(100),
    difficulty VARCHAR(50) DEFAULT 'medium',
    questions JSONB DEFAULT '[]'::jsonb,
    user_answers JSONB DEFAULT '[]'::jsonb,
    scores JSONB DEFAULT '[]'::jsonb,
    overall_score DECIMAL(5,2),
    feedback TEXT,
    weak_topics JSONB DEFAULT '[]'::jsonb,
    status VARCHAR(50) DEFAULT 'in_progress',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Resume analyses
CREATE TABLE IF NOT EXISTS resumes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content_text TEXT,
    parsed_data JSONB DEFAULT '{}'::jsonb,
    ats_score DECIMAL(5,2),
    company_optimized_for VARCHAR(100),
    feedback JSONB DEFAULT '{}'::jsonb,
    before_after_examples JSONB DEFAULT '[]'::jsonb,
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Skill progression over time
CREATE TABLE IF NOT EXISTS skill_progression (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    skill_name VARCHAR(100),
    score INTEGER,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Decision log
CREATE TABLE IF NOT EXISTS decisions_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    question TEXT,
    recommendation TEXT,
    reason TEXT,
    opportunity_cost TEXT,
    expected_outcome TEXT,
    confidence_score INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_messages_user ON chat_messages(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_session ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_messages_created ON chat_messages(created_at);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_interviews_user ON mock_interviews(user_id);
CREATE INDEX IF NOT EXISTS idx_quizzes_user ON quiz_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_skills_user ON skill_progression(user_id);
