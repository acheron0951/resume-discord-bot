# 📄 Resume Tailor AI

### 🧠 AI-powered Discord bot that generates ATS-optimized resumes using a multi-stage AI pipeline

---

## 🚀 Overview

Resume Tailor AI is a private Discord bot that transforms job descriptions into tailored, ATS-friendly resumes using OpenAI. The bot maintains persistent user profiles, supports multiple named resumes, tracks resume history, and can generate both job-specific and universal resumes through a modular AI pipeline.

Designed as a backend-focused portfolio project, Resume Tailor AI emphasizes clean architecture, automation, and extensibility rather than a graphical interface.

---

# ✨ Features

### 📄 Resume Generation

- Generate ATS-optimized resumes from job descriptions
- Generate universal resumes from multiple job descriptions
- Regenerate previous resumes from history
- Support multiple resume writing styles:
  - Direct
  - Detailed

---

### 👤 Named Profile System

Maintain multiple resume profiles such as:

- Help Desk
- IT Support
- Software Engineering
- Biomedical Equipment

Each profile stores:

- Work experience
- Projects
- Education
- Activities

Switch between profiles instantly without re-entering information.

---

### 📂 Resume History

- Stores previous resumes
- Search previous job descriptions
- Regenerate resumes
- Preserve resume style with history

---

### 🤖 Multi-Stage AI Pipeline

Each resume passes through multiple AI agents:

```text
Analyzer
      ↓
Strategist
      ↓
Resume Generator
      ↓
Critic
      ↓
Final Resume
```

This separation allows each AI stage to focus on a single responsibility.

---

### 🔐 Security

- Discord whitelist authorization
- Local JSON storage
- No public API
- Environment variables for secrets

---

# 🏗️ Architecture

```text
Discord User
      │
      ▼
Discord Bot (discord.py)
      │
      ▼
Command Layer
      │
      ▼
BotContext
      │
      ├───────────────┐
      ▼               ▼
Named Profiles     Resume History
(JSON)             (JSON)
      │
      ▼
Resume Pipeline
      │
      ├── Analyzer
      ├── Strategist
      ├── Generator
      └── Critic
      │
      ▼
OpenAI API
      │
      ▼
Tailored Resume
```

---

# ⚙️ Tech Stack

- Python 3.10+
- discord.py
- OpenAI API
- asyncio
- python-dotenv
- JSON persistence


---

# 📌 Bot Commands

## Resume Generation

```text
!tailor direct — Generates a concise, ATS-friendly resume tailored to a single job description.

!tailor detailed — Generates a more detailed, ATS-friendly resume tailored to a single job description.

!tailorbatch direct — Generates a concise universal resume using multiple job descriptions to identify shared skills and qualifications.

!tailorbatch detailed — Generates a more detailed universal resume using multiple job descriptions to identify shared skills and qualifications.
```

---

## Profile Management

```text
!setprofile — Creates or updates a professional profile containing work experience, projects, education, and activities.

!profile — Displays the currently active professional profile.

!profilesummary — Summarizes the active profile and its stored information.

!loadprofile <name> — Switches to a previously saved profile.

!activeprofile — Displays the name of the currently active profile.
```

## Resume History & Search

```text
!history — Displays previously generated resumes and their associated job entries.

!last — Retrieves the most recently generated resume.

!regen <index> — Regenerates a resume from a previously stored job entry.

!search <keyword> — Searches saved resume history for matching entries.
```

## Utilities
```text
!ping — Checks whether the bot is responsive.
```

## Planned Features

```text
The following commands are planned but not yet implemented:

!profiles — Lists all saved profiles.

!renameprofile <old name> <new name> — Renames a saved profile.

!cloneprofile <name> — Creates a copy of an existing profile.

!deleteprofile <name> — Deletes a saved profile.
```

---

# 🧠 Resume Styles

### Direct

- Concise
- Recruiter-friendly
- Minimal wording
- Fast to scan

### Detailed

- Richer descriptions
- Greater project detail
- Stronger technical explanations
- Better for experienced candidates

---

# 📁 Project Structure

```text
resume-discord-bot/
│
├── bot.py
├── resume_pipeline.py
├── data.json
├── outputs/
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

---

# 🔐 Security Model

- Private Discord whitelist
- OpenAI API key stored in `.env`
- Local JSON persistence
- No external database

---

# 🚧 Roadmap

- AWS deployment
- Public GitHub release
- Resume comparison
- PDF generation
- Web dashboard
- PostgreSQL backend
- Docker support
- CI/CD pipeline

---

# 👨‍💻 About

Built by **Alec Ygnacio**

Resume Tailor AI was created as a portfolio project to demonstrate backend software engineering, AI pipeline design, automation, and Discord bot development.

The project focuses on clean architecture, modular components, and practical AI-assisted workflow automation.
