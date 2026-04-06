import json
import config
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

ADMIN_ID = 1109352172  # mee Telegram ID

# Load & Save
def load_movies():
    with open("movies.json") as f:
        return json.load(f)

def save_movies(data):
    with open("movies.json", "w") as f:
        json.dump(data, f, indent=4)

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    movies = load_movies()

    keyboard = []
    for key, movie in movies.items():
        keyboard.append([InlineKeyboardButton(movie["title"], callback_data=key)])

    await update.message.reply_text(
        "🎬 Choose movie:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# BUTTON
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    movies = load_movies()
    movie_id = query.data

    if movie_id in movies:
        await query.message.reply_video(
            video=movies[movie_id]["file"],
            caption=movies[movie_id]["title"]
        )

# ADD
async def add_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("❌ Not admin")

    try:
        movie_id = context.args[0]
        title = context.args[1]
        link = context.args[2]

        movies = load_movies()
        movies[movie_id] = {"title": title, "file": link}
        save_movies(movies)

        await update.message.reply_text("✅ Added")
    except:
        await update.message.reply_text("Usage:\n/add id title link")

# LIST
async def list_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    movies = load_movies()
    text = "\n".join([f"{k} - {v['title']}" for k, v in movies.items()])
    await update.message.reply_text(text or "No movies")

# GEN LINK
async def generate_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("❌ Not admin")

    try:
        movie_id = context.args[0]
        bot_username = (await context.bot.get_me()).username
        link = f"https://t.me/{bot_username}?start={movie_id}"

        await update.message.reply_text(f"🔗 {link}")
    except:
        await update.message.reply_text("Usage:\n/gen movie_id")

# RUN
app = ApplicationBuilder().token(config.TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("add", add_movie))
app.add_handler(CommandHandler("list", list_movies))
app.add_handler(CommandHandler("gen", generate_link))
app.add_handler(CallbackQueryHandler(button))

print("Bot running 🚀")
app.run_polling()
