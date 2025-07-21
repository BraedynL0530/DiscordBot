import discord
from discord.ext import commands
import asyncio
import threading

ALLOWED_USERS = [725124616019902507, 1168400364488380468]

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=":3", intents=intents)

def is_allowed():
    def predicate(ctx):
        return ctx.author.id in ALLOWED_USERS
    return commands.check(predicate)

@bot.event
async def on_ready():
    print(f"🔥 Logged in as {bot.user} 🔥")
    print("✅ Bot ready! You can now type commands in terminal.")
    threading.Thread(target=run_terminal_input, daemon=True).start()

@bot.command()
@is_allowed()
async def say(ctx, *, msg):
    try:
        await ctx.message.delete()
    except:
        pass
    await ctx.channel.send(msg)

@bot.command()
@is_allowed()
async def mute(ctx, member: discord.Member, *, reason=None):
    mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not mute_role:
        mute_role = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(mute_role, speak=False, send_messages=False)
    await member.add_roles(mute_role, reason=reason)
    await ctx.send(f"🔇 {member.mention} was muted. Reason: {reason or 'No reason given'}")

@bot.command()
@is_allowed()
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f"👢 {member.mention} was kicked. Reason: {reason or 'No reason given'}")

@bot.command()
@is_allowed()
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.message.delete()
    await ctx.send(f"👋 {member.mention} left the server. Reason: {reason or 'No reason given'}")

# === Fix for terminal commands permissions ===

class FakeAuthor:
    def __init__(self, user_id):
        self.id = user_id

class FakeChannel:
    async def send(self, content=None, **kwargs):
        print(f"BOT SENDS (channel): {content}")

class FakeMessage:
    def __init__(self, content):
        self.content = content
        # Change this line to your actual user ID to pass is_allowed()
        self.author = FakeAuthor(ALLOWED_USERS[0])
        self.channel = FakeChannel()
        # For terminal, guild is None - commands needing guild won't work here
        self.guild = None
        self._state = bot._connection
        self.attachments = []

    async def delete(self):
        print("FakeMessage.delete() called - ignoring")

async def run_command(cmd_line):
    if not cmd_line.startswith(bot.command_prefix):
        cmd_line = bot.command_prefix + cmd_line
    msg = FakeMessage(cmd_line)
    ctx = await bot.get_context(msg)
    if ctx.command is None:
        print("❌ Command not found.")
        return
    try:
        await bot.invoke(ctx)
    except Exception as e:
        print(f"❌ Error executing command: {e}")

def run_terminal_input():
    while True:
        try:
            cmd_line = input("Terminal command > ")
        except UnicodeDecodeError:
            print("⚠️ Unicode decode error, try again.")
            continue
        if not cmd_line.strip():
            continue
        future = asyncio.run_coroutine_threadsafe(run_command(cmd_line), bot.loop)
        try:
            future.result()
        except Exception as e:
            print(f"❌ Error executing command: {e}")

if __name__ == "__main__":
