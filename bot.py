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


def get_user_profile(data, user_id):
    if user_id not in data:
        data[user_id] = {}

    if "profile" not in data[user_id]:
        data[user_id]["profile"] = {
            "work": [],
            "projects": [],
            "education": {},
            "activities": []
        }

    return data[user_id]["profile"]


def get_profiles(data):

    if "profiles" not in data:
        data["profiles"] = {}

    return data["profiles"]


def get_active_profile(data):

    profiles = get_profiles(data)

    if "active_profile" not in data:

        if profiles:
            data["active_profile"] = next(iter(profiles))
        else:
            data["active_profile"] = None

    return data["active_profile"]


def load_active_profile(data):

    active = get_active_profile(data)

    if active is None:
        return None

    profiles = get_profiles(data)

    return profiles.get(active)


def get_allowed_users(data):
    if "config" not in data:
        data["config"] = {"allowed_users": []}

    if "allowed_users" not in data["config"]:
        data["config"]["allowed_users"] = []

    return set(data["config"]["allowed_users"])


def build_background_from_profile(profile):
    text = ""

    # Work Experience
    if profile["work"]:
        text += "\nWORK EXPERIENCE:\n"
        for w in profile["work"]:
            text += f"""
{w.get('role','')} - {w.get('company','')} ({w.get('dates','')})

Responsibilities:
- """ + "\n- ".join(w.get("responsibilities", [])) + f"""

Achievements:
- """ + "\n- ".join(w.get("achievements", [])) + f"""

Technologies: {w.get('technologies','')}
"""

    # Projects
    if profile["projects"]:
        text += "\nPROJECTS:\n"
        for p in profile["projects"]:
            text += f"""
{p.get('name','')}

Description:
- """ + "\n- ".join(p.get("description", [])) + f"""

Impact:
- """ + "\n- ".join(p.get("impact", [])) + f"""

Technologies: {p.get('technologies','')}
"""

    # Education
    if profile["education"]:
        edu = profile["education"]
        text += f"""

EDUCATION:
{edu.get('degree','')} - {edu.get('school','')} ({edu.get('grad_date','')})

GPA: {edu.get('gpa','')}
Coursework: {edu.get('coursework','')}
"""

    # Activities
    if profile["activities"]:
        text += "\nACTIVITIES:\n"
        for a in profile["activities"]:
            text += f"""
{a.get('role','')} - {a.get('name','')}

- """ + "\n- ".join(a.get("details", []))

    return text if text.strip() else "No background provided."


# =========================
# 🧠 BOT CONTEXT
# =========================
class BotContext:
    def __init__(self):
        self.data = load_data()
        self.profiles = get_profiles(self.data)
        self.active_profile_name = get_active_profile(self.data)
        self.profile = load_active_profile(self.data)

        self.background = (
            build_background_from_profile(self.profile)
            if self.profile is not None
            else None
        )

    def has_profile(self):
        return self.profile is not None

    def save(self):
        save_data(self.data)


# =========================
# 🧩 INPUT HELPERS
# =========================
async def collect_list(ctx, bot, check, prompt):
    await ctx.send(f"{prompt} (type END when done):")

    items = []

    while True:
        msg = await bot.wait_for("message", check=check)
        content = msg.content.strip()

        if content.upper() == "END":
            break

        items.append(content)

    return items


# =========================
# 📎 MESSAGE TEXT HELPER
# =========================
async def get_message_text(message):
    content = message.content.strip()

    if content:
        return content

    if not message.attachments:
        return None

    attachment = message.attachments[0]

    if not attachment.filename.lower().endswith(".txt"):
        return None

    file_bytes = await attachment.read()

    try:
        return file_bytes.decode("utf-8").strip()
    except UnicodeDecodeError:
        return None


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
    data = load_data()
    allowed_users = get_allowed_users(data)
    return ctx.author.id in allowed_users


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
# 🛡️ ACCESS CONTROL (ADMIN)
# =========================
@bot.command()
async def adduser(ctx, user_id: int):

    if not is_authorized(ctx):
        await ctx.send("Unauthorized.")
        return

    data = load_data()

    if "config" not in data:
        data["config"] = {"allowed_users": []}

    if user_id not in data["config"]["allowed_users"]:
        data["config"]["allowed_users"].append(user_id)

    save_data(data)

    await ctx.send(f"Added user {user_id}")

@bot.command()
async def removeuser(ctx, user_id: int):

    if not is_authorized(ctx):
        await ctx.send("Unauthorized.")
        return

    data = load_data()

    if "config" in data and user_id in data["config"]["allowed_users"]:
        data["config"]["allowed_users"].remove(user_id)

    save_data(data)

    await ctx.send(f"Removed user {user_id}")


# =========================
# 🚀 MAIN RESUME COMMAND
# =========================
@bot.command()
async def tailor(ctx, *, job: str):

    if not is_authorized(ctx):
        await ctx.send("Unauthorized.")
        return

    context = BotContext()
    user_id = str(ctx.author.id)

    if not context.has_profile():
        await ctx.send(
            "No active profile. Use !setprofile or !loadprofile first."
        )
        return

    await ctx.send("Generating resume... ⏳")

    try:
        async with ctx.typing():

            result = await asyncio.to_thread(
                pipeline.run,
                context.background,
                job
            )

        final_resume = result["final_resume"]

        data = context.data

        if user_id not in data:
            data[user_id] = {"jobs": []}

        data[user_id]["jobs"].append({
            "job": job,
            "resume": final_resume,
            "timestamp": datetime.utcnow().isoformat()
        })

        context.save()

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
# 🌍 UNIVERSAL RESUME COMMAND
# =========================
@bot.command()
async def tailorbatch(ctx):

    if not is_authorized(ctx):
        await ctx.send("Unauthorized.")
        return

    await ctx.send(
        "Paste your first formatted job description.\n\n"
        "Type ENDJOB when finished.\n"
        "Type DONE when you have entered all jobs."
    )

    def check(m):
        return (
                m.author == ctx.author
                and m.channel == ctx.channel
        )

    jobs = []

    while True:

        msg = await bot.wait_for(
            "message",
            check=check
        )

        content = await get_message_text(msg)

        if msg.content.strip().upper() == "DONE":
            break

        if not content:
            await ctx.send(
                "❌ I could not read that job description.\n"
                "Paste the text directly or upload a UTF-8 .txt file."
            )
            continue

        jobs.append(content)

        await ctx.send(
            f"✅ Job #{len(jobs)} saved "
            f"({len(content):,} characters).\n"
            "Paste another job description, upload a .txt file, or type DONE."
        )

    context = BotContext()
    user_id = str(ctx.author.id)

    if not context.has_profile():
        await ctx.send(
            "No active profile. Use !setprofile or !loadprofile first."
        )
        return

    await ctx.send("Generating universal resume... ⏳")

    try:

        async with ctx.typing():

            result = await asyncio.to_thread(
                pipeline.run_universal,
                context.background,
                jobs
            )

        universal_resume = result["resume"]

        data = context.data

        if user_id not in data:
            data[user_id] = {"jobs": []}

        data[user_id]["jobs"].append({
            "job": f"Universal Resume ({len(jobs)} jobs)",
            "resume": universal_resume,
            "timestamp": datetime.utcnow().isoformat()
        })

        context.save()

        file_buffer = io.BytesIO(
            universal_resume.encode("utf-8")
        )

        await ctx.send(
            file=discord.File(
                fp=file_buffer,
                filename=f"user_{ctx.author.id}_universal_resume.txt"
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

    context = BotContext()
    data = context.data
    user_id = str(ctx.author.id)

    if user_id not in data or not data[user_id]["jobs"]:
        await ctx.send("No history found.")
        return

    jobs = data[user_id]["jobs"]

    if index < 1 or index > len(jobs):
        await ctx.send("Invalid job number.")
        return

    selected_job = jobs[index - 1]["job"]

    if not context.has_profile():
        await ctx.send("No active profile loaded.")
        return

    await ctx.send(f"Regenerating resume for job #{index}... ⏳")

    try:
        async with ctx.typing():

            result = await asyncio.to_thread(
                pipeline.run,
                context.background,
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

        # Save regenerated version
        jobs.append({
            "job": selected_job,
            "resume": final_resume,
            "timestamp": datetime.utcnow().isoformat()
        })

        context.save()

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
# 👤 PROFILE VIEW
# =========================
@bot.command()
async def profile(ctx):

    if not is_authorized(ctx):
        await ctx.send("Unauthorized.")
        return

    context = BotContext()

    if not context.has_profile():
        await ctx.send("No active profile loaded.")
        return

    profile = context.profile
    active = context.active_profile_name

    msg = f"**📄 Active Profile: {active}**\n\n"

    msg += "**Work Experience:**\n"
    if profile["work"]:
        for w in profile["work"]:
            msg += f"- {w.get('role','')} @ {w.get('company','')}\n"
    else:
        msg += "- None\n"

    msg += "\n**Projects:**\n"
    if profile["projects"]:
        for p in profile["projects"]:
            msg += f"- {p.get('name','')}\n"
    else:
        msg += "- None\n"

    msg += "\n**Education:**\n"
    if profile["education"]:
        msg += f"- {profile['education'].get('degree','N/A')} @ {profile['education'].get('school','N/A')}\n"
    else:
        msg += "- None\n"

    msg += "\n**Activities:**\n"
    if profile["activities"]:
        for a in profile["activities"]:
            msg += f"- {a.get('name','')}\n"
    else:
        msg += "- None\n"

    await ctx.send(msg)


# =========================
# 🧹 PROFILE CLEAR
# =========================
@bot.command()
async def profileclear(ctx):
    await ctx.send(
        "This command has been replaced by the upcoming profile management system."
    )


# =========================
# 📊 PROFILE SUMMARY
# =========================
@bot.command()
async def profilesummary(ctx):

    if not is_authorized(ctx):
        await ctx.send("Unauthorized.")
        return

    context = BotContext()

    if not context.has_profile():
        await ctx.send("No active profile loaded.")
        return

    profile = context.profile

    summary = f"""
    PROFILE SUMMARY: {context.active_profile_name}

    Work Experience: {len(profile['work'])}
    Projects: {len(profile['projects'])}
    Education: {'Yes' if profile['education'] else 'No'}
    Activities: {len(profile['activities'])}
    """

    await ctx.send(summary)

# =========================
# 🧾 PROFILE INPUT (GUIDED)
# =========================
@bot.command()
async def setprofile(ctx, profile_name: str):

    if not is_authorized(ctx):
        await ctx.send("Unauthorized.")
        return

    await ctx.send("Let's build your profile. Reply to each prompt.")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    context = BotContext()

    profile = {
        "work": [],
        "projects": [],
        "education": {},
        "activities": []
    }

    # -------------------------
    # WORK EXPERIENCE
    # -------------------------
    await ctx.send("How many work experiences?")
    msg = await bot.wait_for("message", check=check)
    try:
        num_work = int(msg.content)
    except ValueError:
        await ctx.send("Please enter a valid number.")
        return

    for i in range(num_work):
        await ctx.send(f"Company #{i + 1}:")
        company = (await bot.wait_for("message", check=check)).content

        await ctx.send("Role:")
        role = (await bot.wait_for("message", check=check)).content

        await ctx.send("Dates:")
        dates = (await bot.wait_for("message", check=check)).content

        responsibilities = await collect_list(
            ctx, bot, check, "Enter responsibilities"
        )

        achievements = await collect_list(
            ctx, bot, check, "Enter achievements"
        )

        await ctx.send("Technologies (comma separated):")
        technologies = (await bot.wait_for("message", check=check)).content.strip()

        profile["work"].append({
            "company": company,
            "role": role,
            "dates": dates,
            "responsibilities": responsibilities,
            "achievements": achievements,
            "technologies": technologies
        })

    # -------------------------
    # PROJECTS
    # -------------------------
    await ctx.send("How many projects?")
    msg = await bot.wait_for("message", check=check)
    num_projects = int(msg.content)

    for i in range(num_projects):
        await ctx.send(f"Project name #{i + 1}:")
        name = (await bot.wait_for("message", check=check)).content

        description = await collect_list(
            ctx, bot, check, "Enter project description"
        )

        impact = await collect_list(
            ctx, bot, check, "Enter project impact"
        )

        await ctx.send("Technologies:")
        technologies = (await bot.wait_for("message", check=check)).content.strip()

        profile["projects"].append({
            "name": name,
            "description": description,
            "impact": impact,
            "technologies": technologies
        })

    # -------------------------
    # EDUCATION
    # -------------------------
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

    profile["education"] = {
        "school": school,
        "degree": degree,
        "grad_date": grad_date,
        "gpa": gpa,
        "coursework": coursework
    }

    # -------------------------
    # ACTIVITIES
    # -------------------------
    await ctx.send("How many activities?")
    msg = await bot.wait_for("message", check=check)
    num_activities = int(msg.content)

    for i in range(num_activities):
        await ctx.send(f"Activity name #{i + 1}:")
        name = (await bot.wait_for("message", check=check)).content

        await ctx.send("Role:")
        role = (await bot.wait_for("message", check=check)).content

        details = await collect_list(
            ctx, bot, check, "Enter activity details"
        )

        profile["activities"].append({
            "name": name,
            "role": role,
            "details": details
        })

    # -------------------------
    # SAVE PROFILE
    # -------------------------
    if profile_name in context.profiles:
        await ctx.send(
            f"⚠️ Profile '{profile_name}' already exists and will be overwritten."
        )

    context.profiles[profile_name] = profile
    context.data["active_profile"] = profile_name
    context.save()

    await ctx.send(
        f"✅ Profile '{profile_name}' saved and loaded."
    )


# =========================
# 📂 LOAD PROFILE
# =========================
@bot.command()
async def loadprofile(ctx, profile_name: str):

    if not is_authorized(ctx):
        await ctx.send("Unauthorized.")
        return

    context = BotContext()

    if profile_name not in context.profiles:
        await ctx.send(
            f"❌ Profile '{profile_name}' does not exist."
        )
        return

    context.data["active_profile"] = profile_name
    context.save()

    await ctx.send(
        f"✅ Active profile set to '{profile_name}'."
    )


# =========================
# 📌 ACTIVE PROFILE
# =========================
@bot.command()
async def activeprofile(ctx):

    if not is_authorized(ctx):
        await ctx.send("Unauthorized.")
        return

    context = BotContext()
    active = context.active_profile_name

    if active is None:
        await ctx.send("No active profile.")
        return

    await ctx.send(f"📄 Active profile: **{active}**")


# =========================
# ▶️ RUN BOT
# =========================
bot.run(TOKEN)