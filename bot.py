import sqlite3
from telebot import TeleBot

TOKEN = "8365236154:AAGB2vNqFiUJuWSFYmASXCHuXTGmKsRoWD8"
DB = "invites.db"

bot = TeleBot(TOKEN, parse_mode="HTML")

# --- database ---
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS invites(
            adder_id INTEGER,
            adder_name TEXT,
            count INTEGER
        )
    """)
    conn.commit()
    conn.close()

def add_count(adder_id, adder_name, n):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT count FROM invites WHERE adder_id=?", (adder_id,))
    row = c.fetchone()
    if row:
        new_count = row[0] + n
        c.execute("UPDATE invites SET count=?, adder_name=? WHERE adder_id=?", (new_count, adder_name, adder_id))
    else:
        c.execute("INSERT INTO invites VALUES(?,?,?)", (adder_id, adder_name, n))
    conn.commit()
    conn.close()

def get_stats():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT adder_name, count FROM invites ORDER BY count DESC")
    rows = c.fetchall()
    conn.close()
    return rows


# --- events ---
@bot.message_handler(content_types=['new_chat_members'])
def on_new_members(msg):
    adder = msg.from_user
    added_list = msg.new_chat_members
    count = len(added_list)

    name = adder.first_name or "Unknown"

    add_count(adder.id, name, count)

    bot.reply_to(msg, f"👥 <b>{name}</b> added {count} member(s).")


# --- commands ---
@bot.message_handler(commands=['stats'])
def stats(msg):
    rows = get_stats()
    if not rows:
        bot.reply_to(msg, "No data yet.")
        return
    
    text = "📊 <b>Invite Stats</b>\n\n"
    for name, c in rows:
        text += f"• {name}: {c}\n"

    bot.reply_to(msg, text)


init_db()
bot.infinity_polling()
