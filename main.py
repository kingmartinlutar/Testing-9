import os
import asyncio
from pyrogram import Client, filters
from motor.motor_asyncio import AsyncIOMotorClient

# Load environment variables
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("5969730414")
BOT_TOKEN = os.getenv("8056263089:AAHMI88zp5GyHzeaQS82BKNzGFzEI_5DAPs")
ADMINS = list(map(int, os.getenv("ADMINS", "5969730414").split()))
DB_URI = os.getenv("DB_URI")
ERROR_MESSAGE = os.getenv("ERROR_MESSAGE", "False").lower() == "true"

# Initialize bot
bot = Client("RestrictedBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# MongoDB Client
db_client = AsyncIOMotorClient(DB_URI)
db = db_client["telegram_bot"]
users_db = db["users"]

# Start Command
@bot.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("Hello! I am your Restricted Content Bot. Use /help to see commands.")

# Help Command
@bot.on_message(filters.command("help"))
async def help_command(client, message):
    help_text = """
Commands:
/start - Check bot is working
/help - Get usage instructions
/login - Login with your session
/logout - Logout your session
/cancel - Cancel ongoing tasks
/broadcast - Send messages to users (Admin Only)
"""
    await message.reply_text(help_text)

# Login Command
@bot.on_message(filters.command("login"))
async def login(client, message):
    await message.reply_text("Send your session string:")
    user_id = message.from_user.id

    async def session_collector(_, received_message):
        session_string = received_message.text
        await users_db.update_one({"_id": user_id}, {"$set": {"session": session_string}}, upsert=True)
        await received_message.reply_text("Session stored successfully!")

    bot.add_handler(filters.text & filters.user(user_id), session_collector)

# Logout Command
@bot.on_message(filters.command("logout"))
async def logout(client, message):
    user_id = message.from_user.id
    await users_db.delete_one({"_id": user_id})
    await message.reply_text("Logged out successfully!")

# Broadcast (Admin Only)
@bot.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def broadcast(client, message):
    text = message.text.split("/broadcast", 1)[-1].strip()
    if not text:
        return await message.reply_text("Usage: /broadcast <message>")

    users = users_db.find()
    sent, failed = 0, 0

    async for user in users:
        try:
            await bot.send_message(user["_id"], text)
            sent += 1
        except:
            failed += 1

    await message.reply_text(f"Broadcast completed: Sent={sent}, Failed={failed}")

# Handling Restricted Content
@bot.on_message(filters.regex(r"https:\/\/t\.me\/(c\/)?\d+\/\d+"))
async def fetch_restricted_content(client, message):
    # Placeholder for fetching logic
    await message.reply_text("Fetching restricted content... (Implementation needed)")

bot.run()
