<div align="center">
  <h1>🚀 Infera</h1>
  <p><strong>Your AI-Powered Personal Career Guide & Interview Coach</strong></p>

  <p>
    <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI" />
    <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React" />
    <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
    <img src="https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
    <img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind" />
  </p>
</div>

---

## 🌟 Overview

**Infera** is an intelligent career assistant designed to help you prepare for technical interviews, analyze your resume, and track your learning progress. Built with a modern tech stack, it provides actionable insights to get you hired faster.

### ✨ Key Features

- **🤖 AI Interview Coach:** Practice mock interviews with dynamic questioning based on your target company.
- **📄 Resume Analyzer:** Upload your PDF or DOCX resume. Infera scans for missing keywords, weak action verbs, and ATS optimization.
- **📊 Dynamic Dashboard:** Track your real mock interview scores, sprint progress, and technical skill gaps all in one place.
- **🗣️ Hinglish Support:** Natural conversational support built directly into the AI engine.

---

## 🏗️ Architecture

- **Frontend:** React, TypeScript, TailwindCSS, Recharts
- **Backend:** FastAPI, SQLAlchemy, pdfplumber
- **Database:** PostgreSQL
- **AI Integration:** Hugging Face Inference API (`Qwen/Qwen2.5-72B-Instruct`)

---

## 🚀 Getting Started

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- Git

### 🛠️ Local Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Tarannum2504/Infera-My-Personal-Guide.git
   cd Infera-My-Personal-Guide
   ```

2. **Run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   - **Frontend UI:** [http://localhost:5173](http://localhost:5173) (or `http://localhost:3000` depending on Vite configuration)
   - **Backend API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## ☁️ Deployment

Infera is designed to be easily deployable on platforms like **Railway** or **Render**. Simply link this repository and let Docker Compose handle the rest! Make sure to provide your `HF_API_KEY` in the production environment variables.

---
<div align="center">
  <i>Built to accelerate your career.</i>
</div>
