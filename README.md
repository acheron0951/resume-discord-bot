📄 Resume Tailor AI (Discord Bot + AI Pipeline)

An AI-powered resume generation system that transforms raw job descriptions into tailored, ATS-optimized resumes using a structured multi-stage pipeline.

Built as a Discord bot interface for real-time interaction and persistent user profiles.

🚀 Key Features
🧠 Multi-stage AI resume generation pipeline
📄 Structured user profile system (work, projects, education, activities)
🔁 Resume regeneration for multiple job targets
💬 Discord command-based interface
🗂 Persistent JSON storage (no external database required)
🔍 Job history tracking and search functionality
🔐 Access-controlled private bot (Discord ID whitelist)
🧱 System Architecture
Discord User
     ↓
Discord Bot (discord.py)
     ↓
Command Layer (!tailor, !profile, !regen)
     ↓
Profile + Job History (JSON storage)
     ↓
Resume Pipeline (multi-stage processing)
     ↓
OpenAI API (analysis + generation)
     ↓
ATS-Optimized Resume Output

⚙️ Tech Stack
Python 3.10+
discord.py
OpenAI API
dotenv
asyncio
JSON-based persistence

📌 Commands
Profile System
!setprofile      → Guided profile builder
!profile         → View stored profile
!profileclear    → Reset profile
!profilesummary  → Profile statistics
Resume Generation
!tailor <job description>
!regen <index>
History & Search
!history
!search <keyword>

========================================
📘 HOW TO FORMAT JOB DESCRIPTIONS
========================================

To get the best results from the !tailor command, you should first
format your job description into a clean structure.

This improves:

Resume quality
Keyword matching (ATS)
Overall accuracy of the generated resume
STEP 1 — COPY THE JOB DESCRIPTION

Copy the full job description from sites like:

Indeed
LinkedIn
Company career pages
STEP 2 — FORMAT USING CHATGPT

Paste the job description into ChatGPT using this prompt:

Format this job description into a clean, structured summary for a resume generator.

Rules:
- Keep it concise and readable
- Extract only the most important responsibilities and skills
- Use bullet points
- Remove fluff, benefits, and company marketing language
- Do NOT include salary, perks, or long paragraphs

Return format:

<Job Title> – <Company>

Responsibilities:
- bullet points

Skills:
- bullet points

Preferred:
- bullet points (if applicable)

Here is the job description:
[PASTE JOB DESCRIPTION HERE]
STEP 3 — USE WITH THE BOT

Take the formatted result and run:

!tailor <PASTE FORMATTED JOB HERE>
EXAMPLE

Formatted Output:

Level 1 Technical Support Technician – All-Access Infotech

Responsibilities:
- Respond to support requests via phone, email, and ticketing systems
- Troubleshoot Windows, Microsoft 365, printers, and network issues
- Manage and document tickets
- Escalate complex issues

Skills:
- Windows OS
- Microsoft 365
- Networking fundamentals (DNS, DHCP, IP)
- Communication

Preferred:
- MSP/help desk experience
- ConnectWise/Autotask
- CompTIA A+

💡 NOTES
You CAN paste raw job descriptions into !tailor,
but results will be worse.
Clean input = better resumes.
This step also reduces unnecessary token usage.

🧠 How It Works
User builds structured profile via Discord prompts
Job description is analyzed by AI pipeline
System extracts skills + responsibilities
Resume is generated with ATS optimization
Output is returned + stored in history

🔐 Security Model
Discord ID whitelist access control
No public endpoints
No external database required
Environment-based secrets (.env)

📁 Project Structure
resume-discord-bot/
│
├── bot.py
├── resume_pipeline.py
├── data.json
├── .env (excluded)
├── venv/ (excluded)
├── requirements.txt
└── README.md

📈 Future Improvements
Web UI dashboard (React / FastAPI)
PostgreSQL migration
Docker deployment
Resume comparison tool
Multi-user role system
CI/CD cloud deployment

👨‍💻 Author
Built by Alec Ygnacio
Focus: Backend systems, AI pipelines, automation tools
