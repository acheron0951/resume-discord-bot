from openai import OpenAI
from dotenv import load_dotenv
import os

# =========================
# 🔧 Setup
# =========================

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY in .env")

if not DISCORD_TOKEN:
    raise ValueError("Missing DISCORD_TOKEN in .env")

client = OpenAI(api_key=OPENAI_API_KEY)


def save_to_file(filename, content):
    os.makedirs("outputs", exist_ok=True)
    filepath = os.path.join("outputs", filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Saved to {filepath}")


# =========================
# 🧩 Base Class
# =========================
class ResumeTailor:
    def __init__(self, client, model="gpt-5"):
        self.client = client
        self.model = model

    def call_model(self, prompt):
        response = self.client.responses.create(
            model=self.model,
            input=prompt
        )

        return response.output_text


# =========================
# 🔍 Analyzer
# =========================
class Analyzer(ResumeTailor):
    def run(self, background, job):
        prompt = f"""
Analyze the candidate and job.

BACKGROUND:
{background}

JOB:
{job}

Return:
- skills_required
- keywords
- seniority_level
- role_type
- company_type
"""

        return self.call_model(prompt)


# =========================
# 🎯 Strategist
# =========================
class Strategist(ResumeTailor):
    def run(self, analysis, background):
        prompt = f"""
You are a career strategist.

ANALYSIS:
{analysis}

BACKGROUND:
{background}

Return:
- best_candidate_positioning
- strengths_to_emphasize
- weaknesses_to_hide
- gaps_with_severity
- resume_strategy
"""

        return self.call_model(prompt)


# =========================
# 🌍 Universal Strategist
# =========================
class UniversalStrategist(ResumeTailor):
    def run(self, background, jobs):

        combined_jobs = "\n\n".join(jobs)

        prompt = f"""
You are a senior career strategist.

BACKGROUND:
{background}

JOB DESCRIPTIONS:
{combined_jobs}

Create a universal resume strategy that maximizes:
- broad ATS compatibility
- recruiter appeal
- adaptability across similar roles

Return:
- target_role_family
- recurring_skills
- strongest_positioning
- transferable_strengths
- weaknesses_to_minimize
- universal_resume_strategy
"""

        return self.call_model(prompt)


# =========================
# 📝 Resume Generator
# =========================
class ResumeGenerator(ResumeTailor):
    def run(self, strategy, background, critique):
        prompt = f"""
Generate a highly polished, ATS-friendly resume.

STRATEGY:
{strategy}

BACKGROUND:
{background}

CRITIQUE:
{critique}

Requirements:
- strong action verbs
- quantified impact where possible
- ATS-friendly formatting
- clean, recruiter-readable structure
- truthful (do not fabricate metrics)
- prioritize most relevant experience first
- rewrite weak bullets for impact
- keep resume to ~1 page

FORMAT EXACTLY LIKE THIS:

1) Tailored Resume

<Full resume with sections:
- Name + Contact
- Professional Summary
- Core Skills
- Experience
- Projects (if applicable)
- Education
- Activities (if applicable)
>

2) Keywords (ATS-friendly)
- bullet list of keywords used

3) Missing Skills
- Must-have gaps
- Nice-to-have gaps

Important:
- Do NOT include "Keywords Used" inside the resume
- Do NOT include analysis explanations
- Keep resume clean and realistic
"""

        return self.call_model(prompt)


# =========================
# 🧪 Critic
# =========================
class Critic(ResumeTailor):
    def run(self, resume, job):
        prompt = f"""
Critique this resume.

RESUME:
{resume}

JOB:
{job}

Return:
1. ATS match score (0-100)
2. Recruiter feedback
3. Hiring manager critique
"""

        return self.call_model(prompt)


# =========================
# 🎛️ PIPELINE
# =========================
class ResumePipeline:
    def __init__(self, client):

        self.client = client

        self.analyzer = Analyzer(client, model="gpt-5-nano")

        self.strategist = Strategist(client, model="gpt-5")

        self.universal_strategist = UniversalStrategist(
            client,
            model="gpt-5"
        )

        self.generator = ResumeGenerator(client, model="gpt-5")

        self.critic = Critic(client, model="gpt-5")

    # -------------------------
    # Tailored Resume Pipeline
    # -------------------------
    def run(self, background, job):

        print("\n🔍 Running analysis...")

        analysis = self.analyzer.run(background, job)

        print("🎯 Building strategy...")

        strategy = self.strategist.run(analysis, background)

        print("📝 Generating resume...")

        resume = self.generator.run(
            strategy,
            background,
            critique="None"
        )

        print("🧪 Critiquing...")

        critique = self.critic.run(resume, job)

        print("🔁 Final pass...")

        final_resume = self.generator.run(
            strategy,
            background,
            critique
        )

        return {
            "analysis": analysis,
            "strategy": strategy,
            "resume": resume,
            "critique": critique,
            "final_resume": final_resume
        }

    # -------------------------
    # Universal Resume Pipeline
    # -------------------------
    def run_universal(self, background, jobs):

        print("\n🌍 Building universal strategy...")

        strategy = self.universal_strategist.run(
            background,
            jobs
        )

        print("📝 Generating universal resume...")

        universal_resume = self.generator.run(
            strategy,
            background,
            critique="Broad ATS optimization"
        )

        return {
            "strategy": strategy,
            "resume": universal_resume
        }


# =========================
# 🧾 MANUAL CLI INPUT
# =========================
def get_user_input():

    def collect_list(label):

        print(f"{label} (type END when done):")

        items = []

        while True:

            line = input()

            if line.strip().upper() == "END":
                break

            items.append(line)

        return items

    # -------------------------
    # Work Experience
    # -------------------------
    work = []

    num_work = int(input("How many work experiences? "))

    for i in range(num_work):

        print(f"\n--- Work Experience {i+1} ---")

        work.append({
            "company": input("Company: "),
            "role": input("Role: "),
            "dates": input("Dates: "),
            "responsibilities": collect_list("Responsibilities"),
            "achievements": collect_list("Achievements"),
            "technologies": input("Technologies: ")
        })

    # -------------------------
    # Projects
    # -------------------------
    projects = []

    num_projects = int(input("\nHow many projects? "))

    for i in range(num_projects):

        print(f"\n--- Project {i+1} ---")

        projects.append({
            "name": input("Name: "),
            "description": collect_list("Description"),
            "impact": collect_list("Impact"),
            "technologies": input("Technologies: ")
        })

    # -------------------------
    # Education
    # -------------------------
    print("\n--- Education ---")

    education = {
        "school": input("School: "),
        "degree": input("Degree: "),
        "grad_date": input("Graduation Date: "),
        "gpa": input("GPA: "),
        "coursework": input("Coursework: ")
    }

    # -------------------------
    # Activities
    # -------------------------
    activities = []

    num_activities = int(input("\nHow many activities? "))

    for i in range(num_activities):

        print(f"\n--- Activity {i+1} ---")

        activities.append({
            "name": input("Name: "),
            "role": input("Role: "),
            "details": collect_list("Details")
        })

    return work, projects, education, activities


# =========================
# 🧾 FORMAT BACKGROUND
# =========================
def format_all(work, projects, education, activities):

    text = ""

    # -------------------------
    # Work
    # -------------------------
    if work:

        text += "\nWORK EXPERIENCE:\n"

        for w in work:

            text += f"""
{w['role']} - {w['company']} ({w['dates']})

Responsibilities:
- """ + "\n- ".join(w['responsibilities']) + f"""

Achievements:
- """ + "\n- ".join(w['achievements']) + f"""

Technologies: {w['technologies']}
"""

    # -------------------------
    # Projects
    # -------------------------
    if projects:

        text += "\nPROJECTS:\n"

        for p in projects:

            text += f"""
{p['name']}

Description:
- """ + "\n- ".join(p['description']) + f"""

Impact:
- """ + "\n- ".join(p['impact']) + f"""

Technologies: {p['technologies']}
"""

    # -------------------------
    # Education
    # -------------------------
    text += f"""

EDUCATION:
{education['degree']} - {education['school']} ({education['grad_date']})

GPA: {education['gpa']}

Coursework: {education['coursework']}
"""

    # -------------------------
    # Activities
    # -------------------------
    if activities:

        text += "\nACTIVITIES:\n"

        for a in activities:

            text += f"""
{a['role']} - {a['name']}

- """ + "\n- ".join(a['details'])

    return text


# =========================
# 🚀 MAIN
# =========================
def main():

    # -------------------------
    # Collect Candidate Info
    # -------------------------
    work, projects, education, activities = get_user_input()

    background = format_all(
        work,
        projects,
        education,
        activities
    )

    # -------------------------
    # Job Descriptions
    # -------------------------
    num_jobs = int(input("\nHow many job descriptions? "))

    jobs = []

    for i in range(num_jobs):

        print(f"\nPaste job description {i+1} (type END):")

        lines = []

        while True:

            line = input()

            if line.strip().upper() == "END":
                break

            lines.append(line)

        jobs.append("\n".join(lines))

    # -------------------------
    # Choose Mode
    # -------------------------
    mode = input("""
Choose mode:

1 = Tailored resumes per job
2 = Universal resume only
3 = Both

Selection: """).strip()

    pipeline = ResumePipeline(client)

    # =====================================================
    # MODE 1 = Tailored Resumes
    # =====================================================
    if mode == "1":

        for i, job in enumerate(jobs, 1):

            print(f"\n\n=== JOB {i} ===\n")

            result = pipeline.run(background, job)

            print("\n=== STRATEGY ===\n")
            print(result["strategy"])

            print("\n=== RESUME ===\n")
            print(result["resume"])

            print("\n=== CRITIQUE ===\n")
            print(result["critique"])

            print("\n=== FINAL RESUME ===\n")
            print(result["final_resume"])

            save_to_file(
                f"resume_job_{i}.txt",
                f"""
=== ANALYSIS ===
{result['analysis']}

=== STRATEGY ===
{result['strategy']}

=== RESUME ===
{result['resume']}

=== CRITIQUE ===
{result['critique']}

=== FINAL RESUME ===
{result['final_resume']}
"""
            )

    # =====================================================
    # MODE 2 = Universal Resume
    # =====================================================
    elif mode == "2":

        result = pipeline.run_universal(background, jobs)

        print("\n=== UNIVERSAL STRATEGY ===\n")
        print(result["strategy"])

        print("\n=== UNIVERSAL RESUME ===\n")
        print(result["resume"])

        save_to_file(
            "universal_resume.txt",
            f"""
=== UNIVERSAL STRATEGY ===
{result['strategy']}

=== UNIVERSAL RESUME ===
{result['resume']}
"""
        )

    # =====================================================
    # MODE 3 = Both
    # =====================================================
    elif mode == "3":

        # -------------------------
        # Universal Resume
        # -------------------------
        universal = pipeline.run_universal(
            background,
            jobs
        )

        print("\n=== UNIVERSAL STRATEGY ===\n")
        print(universal["strategy"])

        print("\n=== UNIVERSAL RESUME ===\n")
        print(universal["resume"])

        save_to_file(
            "universal_resume.txt",
            f"""
=== UNIVERSAL STRATEGY ===
{universal['strategy']}

=== UNIVERSAL RESUME ===
{universal['resume']}
"""
        )

        # -------------------------
        # Tailored Resumes
        # -------------------------
        for i, job in enumerate(jobs, 1):

            print(f"\n\n=== JOB {i} ===\n")

            result = pipeline.run(background, job)

            print("\n=== FINAL RESUME ===\n")
            print(result["final_resume"])

            save_to_file(
                f"resume_job_{i}.txt",
                f"""
=== ANALYSIS ===
{result['analysis']}

=== STRATEGY ===
{result['strategy']}

=== RESUME ===
{result['resume']}

=== CRITIQUE ===
{result['critique']}

=== FINAL RESUME ===
{result['final_resume']}
"""
            )

    # =====================================================
    # Invalid Input
    # =====================================================
    else:
        print("Invalid mode selected.")


# =========================
# ▶️ ENTRY POINT
# =========================
def run_tailored_resume(background, job):
    pipeline = ResumePipeline(client)
    return pipeline.run(background, job)


def run_universal_resume(background, jobs):
    pipeline = ResumePipeline(client)
    return pipeline.run_universal(background, jobs)