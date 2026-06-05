# Infera - My Personal Guide

An AI-powered career assistant system built with FastAPI, React, and PostgreSQL.

## Prerequisites
- Docker Desktop installed and running
- Git

## How to Run

1. Clone the repository
2. Open terminal in the `Infera-My-Personal-Guide` folder
3. Run the following command:
   ```bash
   docker-compose up --build
   ```
4. Access the application:
   - Frontend: `http://localhost:5173`
   - Backend API: `http://localhost:8000/docs`

## Architecture
- **Frontend**: React + TypeScript + TailwindCSS + Recharts
- **Backend**: FastAPI + SQLAlchemy + pdfplumber
- **Database**: PostgreSQL
- **AI Integration**: Hugging Face Inference API
