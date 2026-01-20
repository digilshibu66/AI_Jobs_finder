# Freelance Mailer - Automated Job Application System

An intelligent automated tool that scrapes job websites, generates **personalized application emails** using **OpenRouter AI**, attaches your resume and **AI-generated motivational letters**, and sends them via SMTP. Features **smart company filtering** and **clean, human-like output**.

## 🎯 Key Features

- ✅ **Multi-Platform Job Scraping**: Scrapes from Freelancer, RemoteOK, Guru, LinkedIn, and Google Jobs.
- ✅ **Clean AI Output**: Generates professional emails without markdown artifacts (`**`, `__`) or placeholders.
- ✅ **OpenRouter Integration**: Access to premium AI models for free (Llama 3.3 70B, Qwen3, Mistral).
- ✅ **AI Motivational Letters**: Generates tailored PDF motivational letters for each application.
- ✅ **Smart Email Discovery**: Finds and validates company contact emails (with relaxed validation for maximum reach).
- ✅ **Local Company Priority**: Scoring system to prioritize local/regional companies over FAANG.
- ✅ **Excel Activity Logging**: Tracks all jobs, emails, and statuses in `email_log.xlsx`.
- ✅ **Dockerized**: Easy deployment with Docker Compose.

---

## 🏗️ System Architecture

```mermaid
graph TD
    A[User] --> B[Web Dashboard / CLI]
    B --> C[Main Controller]
    C --> D[Job Scraper]
    C --> E[Resume Embedder]
    C --> F[AI Engine]
    C --> G[Result Handler]
    
    D --> J[LinkedIn]
    D --> K[Indeed]
    D --> L[Google/Other]
    
    F --> M[OpenRouter API]
    M --> N[Llama 3.3 / Qwen / Mistral]
    
    G --> O[Email Sender (SMTP)]
    G --> P[Excel Logger]
    G --> Q[PDF Generator]
```

---

## 🚀 Quick Start (Docker)

The easiest way to run the application is using Docker.

### 1. Prerequisites

- Docker & Docker Compose installed
- OpenRouter API Key (Get a free key from [openrouter.ai](https://openrouter.ai/))
- Gmail Account (with [App Password](https://myaccount.google.com/apppasswords) enabled)
- PDF Resume

### 2. Setup

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd freelance_mailer_package
   ```

2. **Configure Environment:**
   Copy `.env.example` to `.env` and fill in your details:

   ```bash
   cp .env.example .env
   ```

   **Required `.env` settings:**

   ```ini
   OPENROUTER_API_KEY=sk-or-v1-xxxxxxxx...
   SMTP_EMAIL=your_email@gmail.com
   SMTP_PASSWORD=xxxx xxxx xxxx xxxx  # 16-char App Password
   RESUME_PATH=./resume.pdf           # Place resume.pdf in project root
   AI_MODEL=meta-llama/llama-3.3-70b-instruct:free
   ```

3. **Place Resume:**
   Put your `resume.pdf` in the root directory.

### 3. Run

```bash
docker-compose up -d --build
```

Access the dashboard at: **<http://localhost:3000>** (or port defined in docker-compose)

---

## ⚙️ Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `AI_PROVIDER` | `openrouter` | AI provider to use (`openrouter` or `gemini`) |
| `AI_MODEL` | `meta-llama/llama-3.3-70b-instruct:free` | The specific model ID to use |
| `JOB_IT_LIMIT` | `30` | Max jobs to scrape per run |
| `LOCATION` | (Empty) | Target city/region (e.g., "New York") |
| `Generate_Motivational_Letter` | `true` | Create specific PDF letters |
| `SEND_EMAILS` | `false` | Set to `true` to actually send emails |

---

## 🤖 Supported Free Models (Verified Jan 2026)

| Model ID | Description | Best For |
|----------|-------------|----------|
| `meta-llama/llama-3.3-70b-instruct:free` | **Result**: Recommended Default | Professional, high quality |
| `qwen/qwen3-coder:free` | **Result**: Excellent for Code | Developer/Technical roles |
| `mistralai/devstral-2512:free` | **Result**: Agentic Coder | General purpose |
| `nousresearch/hermes-3-llama-3.1-405b:free` | **Result**: Massive Model | Complex reasoning |

---

## 💻 Manual Installation (No Docker)

If you prefer running locally without Docker:

1. **Install Dependencies:**

   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt

   # Frontend
   cd ../frontend
   npm install
   ```

2. **Run Backend:**

   ```bash
   python backend/server.py
   ```

3. **Run Frontend:**

   ```bash
   cd frontend
   npm run dev
   ```

---

## 🛠️ Troubleshooting

### 1. SMTP Authentication Error (535, 5.7.8)

**Cause:** Using main Gmail password or expired App Password.
**Fix:** Generate a NEW App Password at [Google Account Security](https://myaccount.google.com/apppasswords) and update `.env`.

### 2. "name 'time' is not defined"

**Cause:** Missing import in older versions.
**Fix:** Fixed in latest build. Run `docker-compose build` to update.

### 3. Rate Limits / Quota Exceeded

**Cause:** Using a paid model or hitting free tier limits.
**Fix:** Switch `AI_MODEL` to one of the verified free models listed above.

### 4. Valid Emails Rejected

**Cause:** Email doesn't appear in Google Search results.
**Fix:** The system now logs a warning but **accepts** the email to prevent blocking valid addresses.

### 5. Markdown in Emails (`**Hi Sir**`)

**Cause:** AI formatting.
**Fix:** The system now automatically strips markdown artifacts from the final email body.

---

## 📄 License

MIT License.

---
**Happy Job Hunting! 🚀**
