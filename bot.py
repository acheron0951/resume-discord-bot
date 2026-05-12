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

    background = "User background placeholder"

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
    background = "User background placeholder"

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
# ▶️ RUN BOT
# =========================
bot.run(TOKEN)