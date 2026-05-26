# 📄 Resume Tailor AI

### 🧠 AI-powered Discord bot that generates ATS-optimized resumes from job descriptions

---

## 🚀 Overview

Resume Tailor AI is a Discord-based system that transforms raw job descriptions into **structured, ATS-optimized resumes** using a multi-stage AI pipeline.

It allows users to build a persistent profile and generate tailored resumes instantly through simple commands.

---

## ✨ Key Features

- 🧠 Multi-stage AI resume generation pipeline
- 📄 Structured user profile system (work, projects, education, activities)
- 🔁 Resume regeneration for multiple job descriptions
- 💬 Discord command-based interface
- 🗂 Persistent JSON storage (no database required)
- 🔍 Job history tracking + search
- 🔐 Private access via Discord ID whitelist

---

## 🧱 System Architecture

```text
User (Discord)
     ↓
Discord Bot (discord.py)
     ↓
Command Layer (!tailor, !profile, !regen)
     ↓
User Profile + Job History (JSON Storage)
     ↓
AI Resume Pipeline (multi-stage processing)
     ↓
OpenAI API (analysis + generation)
     ↓
Final ATS-Optimized Resume
```

---

## ⚙️ Tech Stack

- Python 3.10+
- discord.py
- OpenAI API
- python-dotenv
- asyncio
- JSON persistence (lightweight storage)

---

## 📌 Bot Commands

### 👤 Profile System

!setprofile      → Guided profile builder  
!profile         → View stored profile  
!profileclear    → Reset profile  
!profilesummary  → Profile stats  

---

### 📄 Resume Generation

!tailor <job description>  
!regen <index>  

---

### 🔍 History & Search

!history  
!search <keyword>  

---

## 🧠 How It Works

User inputs data through Discord commands  
↓  
Profile is stored in JSON  
↓  
Job description is parsed and structured  
↓  
Resume pipeline processes job + profile  
↓  
OpenAI generates optimized resume  
↓  
Result is stored + returned to user

---

## 📘 How to Format Job Descriptions

To get the best results from `!tailor`, you should format job descriptions before sending them.

This improves:
- Resume quality
- ATS keyword matching
- Accuracy of generated resumes

---

## 📥 Step 1 — Copy Job Description

Copy the full job description from:
- Indeed
- LinkedIn
- Company career pages

---

## 🧠 Step 2 — Format Using ChatGPT

Paste the job description into ChatGPT using this prompt:

```text
Format this job description into a structured resume input.

Rules:
- Extract only key responsibilities and skills
- Remove salary, benefits, and marketing language
- Use bullet points only
- Keep it concise and ATS-friendly

Return format:

<Job Title> – <Company>

Responsibilities:
- bullet points

Skills:
- bullet points

Preferred:
- bullet points (if applicable)

Here is the job description:
[PASTE HERE]
```

---

## 🚀 STEP 3 — USE WITH BOT

Take the formatted result and run:

```bash
!tailor <FORMATTED JOB DESCRIPTION>
```

---

## 💡 EXAMPLE

Level 1 Technical Support Technician – Company

**Responsibilities:**
- Respond to support requests via ticketing system
- Troubleshoot Windows and Microsoft 365 issues
- Manage user accounts and access
- Escalate complex issues

**Skills:**
- Windows OS
- Microsoft 365
- Networking fundamentals (DNS, DHCP, IP)

**Preferred:**
- MSP/help desk experience
- ConnectWise / Autotask
- CompTIA A+

---

## 📁 Project Structure

resume-discord-bot/
├── bot.py
├── resume_pipeline.py
├── data.json
├── requirements.txt
├── .env (excluded)
└── venv/ (excluded)

---

## 🔐 Security Model

- Discord ID whitelist access control
- No public API endpoints
- No external database required
- Environment variables used for secrets
- Local JSON storage only

---

## 📈 Future Improvements

- 🌐 Web dashboard (React / FastAPI)
- 🐘 PostgreSQL migration
- 🐳 Docker deployment
- 📊 Resume comparison tool
- 👥 Multi-user role system
- ☁️ CI/CD cloud deployment

---

## 👨‍💻 Author

Built by Alec Ygnacio  
Focus: Backend systems, AI pipelines, automation tools
