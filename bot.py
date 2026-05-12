import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import io
import json
from datetime import datetime

# =========================
# 💾 DATA STORAGE
# =========================
DATA_FILE = "data.json"


def load_data():
    if not os.path.exists(DATA_FILE):
        return {}

    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# =========================
# 👤 GET USER PROFILE
# =========================
def get_user_profile(user_id):

    data = load_data()

    user_id = str(user_id)

    if user_id not in data:

        data[user_id] = {
            "profile": {
                "work": [],
                "projects": [],
                "education": {},
                "activities": []
            },
            "jobs": []
        }

        save_data(data)

    # Create profile if missing
    if "profile" not in data[user_id]:

        data[user_id]["profile"] = {
            "work": [],
            "projects": [],
            "education": {},
            "activities": []
        }

        save_data(data)

    return data[user_id]["profile"]


# =========================
# 💾 SAVE USER PROFILE
# =========================
def save_user_profile(user_id, profile):

    data = load_data()

    user_id = str(user_id)

    if user_id not in data:

        data[user_id] = {
            "profile": profile,
            "jobs": []
        }

    else:
        data[user_id]["profile"] = profile

    save_data(data)


# =========================
# 🧾 BUILD BACKGROUND
# =========================
def build_background(profile):

    text = ""

    # -------------------------
    # WORK EXPERIENCE
    # -------------------------
    if profile["work"]:

        text += "\nWORK EXPERIENCE:\n"

        for w in profile["work"]:

            text += f"""
{w['role']} - {w['company']} ({w['dates']})

Responsibilities:
- """ + "\n- ".join(w["responsibilities"]) + f"""

Achievements:
- """ + "\n- ".join(w["achievements"]) + f"""

Technologies: {w['technologies']}
"""

    # -------------------------
    # PROJECTS
    # -------------------------
    if profile["projects"]:

        text += "\nPROJECTS:\n"

        for p in profile["projects"]:

            text += f"""
{p['name']}

Description:
- """ + "\n- ".join(p["description"]) + f"""

Impact:
- """ + "\n- ".join(p["impact"]) + f"""

Technologies: {p['technologies']}
"""

    # -------------------------
    # EDUCATION
    # -------------------------
    education = profile["education"]

    if education:

        text += f"""

EDUCATION:
{education.get('degree', '')} - {education.get('school', '')}

Graduation: {education.get('grad_date', '')}

GPA: {education.get('gpa', '')}

Coursework: {education.get('coursework', '')}
"""

    # -------------------------
    # ACTIVITIES
    # -------------------------
    if profile["activities"]:

        text += "\nACTIVITIES:\n"

        for a in profile["activities"]:

            text += f"""
{a['role']} - {a['name']}

- """ + "\n- ".join(a["details"])

    return text

# =========================
# 🔧 LOAD ENV
# =========================
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("DISCORD_TOKEN missing in .env")

# =========================
# 🔒 PRIVATE BOT ACCESS
# =========================
ALLOWED_USERS = {
    104808415020261376
}

# =========================
# 🤖 DISCORD SETUP
# =========================
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# =========================
# 🧠 IMPORT AI PIPELINE
# =========================
from resume_pipeline import ResumePipeline, client

pipeline = ResumePipeline(client)

# =========================
# 📌 BOT READY EVENT
# =========================
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# =========================
# 🔐 ACCESS CHECK HELPER
# =========================
def is_authorized(ctx):
    return ctx.author.id in ALLOWED_USERS

# =========================
# 🧪 TEST COMMAND
# =========================
@bot.command()
async def ping(ctx):

    if not is_authorized(ctx):
        await ctx.send("Unauthorized.")
        return

    await ctx.send("pong")

# =========================
# 🚀 MAIN RESUME COMMAND
# =========================
@bot.command()
async def tailor(ctx, *, job: str):

    if not is_authorized(ctx):
        await ctx.send("Unauthorized.")
        return

    # =========================
    # 👤 LOAD USER PROFILE
    # =========================
    profile = get_user_profile(ctx.author.id)

    background = build_background(profile)

    await ctx.send("Generating resume... ⏳")

    try:
        async with ctx.typing():

            result = await asyncio.to_thread(
                pipeline.run,
                background,
                job
            )

        final_resume = result["final_resume"]

        data = load_data()
        user_id = str(ctx.author.id)

        if user_id not in data:
            data[user_id] = {"jobs": []}

        data[user_id]["jobs"].append({
            "job": job,
            "resume": final_resume,
            "timestamp": datetime.utcnow().isoformat()
        })

        save_data(data)

        file_buffer = io.BytesIO(final_resume.encode("utf-8"))

        await ctx.send(
            file=discord.File(
                fp=file_buffer,
                filename=f"user_{ctx.author.id}_resume.txt"
            )
        )

    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

# =========================
# 📜 HISTORY COMMAND
# =========================
@bot.command()
async def history(ctx):

    if not is_authorized(ctx):
        await ctx.send("Unauthorized.")
        return

    data = load_data()
    user_id = str(ctx.author.id)

    if user_id not in data or not data[user_id]["jobs"]:
        await ctx.send("No history found.")
        return

    jobs = data[user_id]["jobs"][-5:]

    msg = "**Recent Jobs:**\n\n"

    for i, j in enumerate(jobs, 1):
        msg += f"{i}. {j['job'][:80]}...\n"

    await ctx.send(msg)

# =========================
# 📄 LAST RESUME COMMAND
# =========================
@bot.command()
async def last(ctx):

    if not is_authorized(ctx):
        await ctx.send("Unauthorized.")
        return

    data = load_data()
    user_id = str(ctx.author.id)

    if user_id not in data or not data[user_id]["jobs"]:
        await ctx.send("No history found.")
        return

    last_resume = data[user_id]["jobs"][-1]["resume"]

    file_buffer = io.BytesIO(last_resume.encode("utf-8"))

    await ctx.send(
        file=discord.File(
            fp=file_buffer,
            filename=f"last_resume_{ctx.author.id}.txt"
        )
    )

# =========================
# 🔁 REGEN COMMAND
# =========================
@bot.command()
async def regen(ctx, index: int):

    if not is_authorized(ctx):
        await ctx.send("Unauthorized.")
        return

    data = load_data()
    user_id = str(ctx.author.id)

    if user_id not in data or not data[user_id]["jobs"]:
        await ctx.send("No history found.")
        return

    jobs = data[user_id]["jobs"]

    if index < 1 or index > len(jobs):
        await ctx.send("Invalid job number.")
        return

    selected_job = jobs[index - 1]["job"]

    # =========================
    # 👤 LOAD USER PROFILE
    # =========================
    profile = get_user_profile(ctx.author.id)

    background = build_background(profile)

    await ctx.send(f"Regenerating resume for job #{index}... ⏳")

    try:
        async with ctx.typing():

            result = await asyncio.to_thread(
                pipeline.run,
                background,
                selected_job
            )

        final_resume = result["final_resume"]

        file_buffer = io.BytesIO(final_resume.encode("utf-8"))

        await ctx.send(
            file=discord.File(
                fp=file_buffer,
                filename=f"regen_{ctx.author.id}_job{index}.txt"
            )
        )

        jobs.append({
            "job": selected_job,
            "resume": final_resume,
            "timestamp": datetime.utcnow().isoformat()
        })

        save_data(data)

    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

# =========================
# 🔍 SEARCH COMMAND
# =========================
@bot.command()
async def search(ctx, *, keyword: str):

    if not is_authorized(ctx):
        await ctx.send("Unauthorized.")
        return

    data = load_data()
    user_id = str(ctx.author.id)

    if user_id not in data or not data[user_id]["jobs"]:
        await ctx.send("No history found.")
        return

    keyword_lower = keyword.lower()
    matches = []

    for i, job_entry in enumerate(data[user_id]["jobs"], 1):

        job_text = job_entry["job"].lower()

        if keyword_lower in job_text:
            matches.append((i, job_entry["job"]))

    if not matches:
        await ctx.send(f"No matches found for '{keyword}'.")
        return

    msg = f"**Search results for '{keyword}':**\n\n"

    for idx, job_text in matches:
        msg += f"{idx}. {job_text[:80]}...\n"

    await ctx.send(msg)

# =========================
# 👤 SET PROFILE COMMAND
# =========================
@bot.command()
async def setprofile(ctx):

    if not is_authorized(ctx):
        await ctx.send("Unauthorized.")
        return

    await ctx.send("Let's build your profile. Reply to each prompt.")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:

        # =========================
        # WORK EXPERIENCE
        # =========================
        await ctx.send("How many work experiences?")
        msg = await bot.wait_for("message", check=check)
        num_work = int(msg.content)

        work = []

        for i in range(num_work):

            await ctx.send(f"Company #{i+1}:")
            company = (await bot.wait_for("message", check=check)).content

            await ctx.send("Role:")
            role = (await bot.wait_for("message", check=check)).content

            await ctx.send("Dates:")
            dates = (await bot.wait_for("message", check=check)).content

            await ctx.send("Responsibilities (comma separated):")
            responsibilities = (await bot.wait_for("message", check=check)).content.split(",")

            await ctx.send("Achievements (comma separated):")
            achievements = (await bot.wait_for("message", check=check)).content.split(",")

            await ctx.send("Technologies (comma separated):")
            technologies = (await bot.wait_for("message", check=check)).content

            work.append({
                "company": company,
                "role": role,
                "dates": dates,
                "responsibilities": [r.strip() for r in responsibilities],
                "achievements": [a.strip() for a in achievements],
                "technologies": technologies
            })

        # =========================
        # PROJECTS
        # =========================
        await ctx.send("How many projects?")
        num_projects = int((await bot.wait_for("message", check=check)).content)

        projects = []

        for i in range(num_projects):

            await ctx.send(f"Project name #{i+1}:")
            name = (await bot.wait_for("message", check=check)).content

            await ctx.send("Description (comma separated):")
            description = (await bot.wait_for("message", check=check)).content.split(",")

            await ctx.send("Impact (comma separated):")
            impact = (await bot.wait_for("message", check=check)).content.split(",")

            await ctx.send("Technologies:")
            tech = (await bot.wait_for("message", check=check)).content

            projects.append({
                "name": name,
                "description": [d.strip() for d in description],
                "impact": [i.strip() for i in impact],
                "technologies": tech
            })

        # =========================
        # EDUCATION
        # =========================
        await ctx.send("School:")
        school = (await bot.wait_for("message", check=check)).content

        await ctx.send("Degree:")
        degree = (await bot.wait_for("message", check=check)).content

        await ctx.send("Graduation date:")
        grad_date = (await bot.wait_for("message", check=check)).content

        await ctx.send("GPA:")
        gpa = (await bot.wait_for("message", check=check)).content

        await ctx.send("Coursework:")
        coursework = (await bot.wait_for("message", check=check)).content

        education = {
            "school": school,
            "degree": degree,
            "grad_date": grad_date,
            "gpa": gpa,
            "coursework": coursework
        }

        # =========================
        # ACTIVITIES
        # =========================
        await ctx.send("How many activities?")
        num_activities = int((await bot.wait_for("message", check=check)).content)

        activities = []

        for i in range(num_activities):

            await ctx.send(f"Activity name #{i+1}:")
            name = (await bot.wait_for("message", check=check)).content

            await ctx.send("Role:")
            role = (await bot.wait_for("message", check=check)).content

            await ctx.send("Details (comma separated):")
            details = (await bot.wait_for("message", check=check)).content.split(",")

            activities.append({
                "name": name,
                "role": role,
                "details": [d.strip() for d in details]
            })

        # =========================
        # SAVE PROFILE
        # =========================
        profile = {
            "work": work,
            "projects": projects,
            "education": education,
            "activities": activities
        }

        save_user_profile(ctx.author.id, profile)

        await ctx.send("✅ Profile saved successfully!")

    except Exception as e:
        await ctx.send(f"❌ Error building profile: {str(e)}")

# =========================
# ▶️ RUN BOT
# =========================
bot.run(TOKEN)