import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import json
import PokebotClasses as Pb
import random
import datetime
import uuid

# -------------------- DATA --------------------
trainers = {}  # user_id -> Trainer object
user_last_play = {}  # user_id -> date of last play
user_guesses = {}  # user_id -> guesses & hints
daily_pokemon = None
daily_date = None
ADMIN_USER_IDS = ["414854337987215380"]
active_trades = {}
# Structure:
# active_trades[trade_id] = {
#     "trainer1": trainer1_id,
#     "pokemon1_uid": uid,
#     "trainer2": trainer2_id,
#     "pokemon2_uid": uid,
#     "status": "pending"  # or "accepted"
# }
active_trades = {}  
# key: trainer_id (str), value: trade info dict

# -------------------- HELPERS --------------------
def slot_list(self):
    return [getattr(self, f"slot{i}") for i in range(1,7) if getattr(self, f"slot{i}")]

def format_pokemon(p):
    """Format a Pokémon for display."""
    return f"{p.name} (Lvl {p.level}) | Nature: {p.nature} | Shiny: {'Yes' if p.isShiny else 'No'} | UID: `{p.uid}`"

def save_trainers():
    with open("trainers.json", "w", encoding="utf-8") as f:
        json.dump({uid: t.to_dict() for uid, t in trainers.items()}, f, indent=4)

def load_trainers():
    global trainers
    try:
        with open("trainers.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            trainers = {uid: Pb.Trainer.from_dict(td) for uid, td in data.items()}
    except FileNotFoundError:
        trainers = {}

def pick_daily_pokemon():
    global daily_pokemon, daily_date, user_guesses
    daily_date = datetime.date.today()
    user_guesses = {}
    poke_id = random.choice(list(Pb.Pokemon.BaseStats.keys()))
    daily_pokemon = Pb.Pokemon(poke_id, level=1)

def get_all_hints(pokemon):
    # Build all possible hint strings
    return [
        f"First letter: {pokemon.name[0]}",
        f"Last letter: {pokemon.name[-1]}",
        f"Type: {random.choice(pokemon.types)}",
        f"Ability: {random.choice(pokemon.abilities)}"
    ]

def start_trade(proposer_id, partner_id, your_pokemon_uid, partner_pokemon_uid):
    trade_data = {
        "proposer_id": proposer_id,
        "partner_id": partner_id,
        "your_pokemon_uid": your_pokemon_uid,
        "partner_pokemon_uid": partner_pokemon_uid
    }
    active_trades[proposer_id] = trade_data
    active_trades[partner_id] = trade_data  # same object for both

def get_pokemon_by_uid(trainer, uid):
    for slot in range(1, 7):
        p = getattr(trainer, f"slot{slot}")
        if p and p.uid == uid:
            return p, f"slot{slot}"
    for i, p in enumerate(trainer.box):
        if p.uid == uid:
            return p, ("box", i)
    return None, None

def swap_pokemon(trainer, old_pokemon, new_pokemon):
    # Check slots
    for i in range(1, 7):
        slot_name = f"slot{i}"
        if getattr(trainer, slot_name) == old_pokemon:
            setattr(trainer, slot_name, new_pokemon)
            return
    # If not in slots, check box
    for idx, p in enumerate(trainer.box):
        if p == old_pokemon:
            trainer.box[idx] = new_pokemon
            return

# -------------------- BOT SETUP --------------------
load_trainers()
load_dotenv()
token = os.getenv('DISCORD_TOKEN')
ALLOWED_CHANNEL_ID = 1414709434298531891
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
secretrole = "Pokemon Trainer"
# -------------------- HELP ----------------------
# Remove the default help command
bot.remove_command("help")

@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="Help Menu",
        description="Here are the commands you can use:",
        color=discord.Color.blue()
    )
    embed.add_field(name="!trainer 🧑‍🎓", value="Creates your Trainer if you don’t have one yet, or shows your Trainer ID, Pokémon team, and box if you already do.", inline=False)
    embed.add_field(name="!daily 🔍", value="Get up to 2 hints about today’s mystery Pokémon.", inline=False)
    embed.add_field(name="!daily <name> ✏️", value="Use it to guess (you have 3 attempts). If you’re correct, send the answer to the bot via DM.", inline=False)
    embed.add_field(name="!stats <UID> 📊", value="Shows detailed stats for a specific Pokémon in your team or box.", inline=False)
    embed.add_field(name="!trade @partner your_pokemon_uid their_pokemon_uid 🔄", value="Propose Pokémon trades with other trainers. You can ONLY have 1 trade active.", inline=False)
    embed.add_field(name="!trade summary 📝", value="View the details of your current active trade.", inline=False)
    embed.add_field(name="!accept ✅", value="Accept a trade proposal sent to you.", inline=False)



    await ctx.send(embed=embed)

# -------------------- EVENTS --------------------
@bot.event
async def on_ready():
    print(f"We are ready to go in, {bot.user.name}")

@bot.event
async def on_message(message):
    global daily_pokemon
    if message.author.bot:
        return

    # Check daily Pokémon guesses and delete if name is said
    if daily_pokemon and message.channel.id == ALLOWED_CHANNEL_ID:
        if daily_pokemon.name.lower() in message.content.lower():
            await message.delete()
            await message.author.send("❌ You cannot reveal the daily Pokémon's name publicly! If you want to catch it, DM me **_daily answer**")
            return

    await bot.process_commands(message)

# -------------------- COMMANDS --------------------
@bot.command(name="trainer")
async def trainer_command(ctx):
    if ctx.author.bot:
        return
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        return

    unique_id = str(ctx.author.id)

    # If trainer doesn't exist, create one and assign role
    if unique_id not in trainers:
        trainers[unique_id] = Pb.Trainer(unique_id)
        save_trainers()

        # Give secret role if it exists
        role = discord.utils.get(ctx.guild.roles, name=secretrole)
        if role:
            await ctx.author.add_roles(role)
            await ctx.author.send(
                "Congrats! You are now on the road to become the very best ^-^!\n"
                "Write **_help** to see the commands."
            )

        await ctx.send(f"{ctx.author.name}, your trainer has been created!")
        return

    # Trainer exists, show info with Pokémon UIDs
    trainer = trainers[unique_id]
    msg = f"**Trainer UID:** {trainer.UID}\n**Your Pokémon:**\n"
    has_pokemon = False

    for i in range(1, 7):
        slot = getattr(trainer, f"slot{i}")
        if slot:
            has_pokemon = True
            msg += f"• Slot {i}: {slot.name} (Lvl {slot.level}) | Nature: {slot.nature} | Shiny: {'Yes' if slot.isShiny else 'No'} | UID: `{slot.uid}`\n"

    if trainer.box:
        has_pokemon = True
        msg += "\n**Box Pokémon:**\n"
        for p in trainer.box:
            msg += f"• {p.name} (Lvl {p.level}) | Nature: {p.nature} | Shiny: {'Yes' if p.isShiny else 'No'} | UID: `{p.uid}`\n"

    if not has_pokemon:
        msg += "You don't have any Pokémon yet. Use `_daily` to catch one!"

    await ctx.send(msg)


@bot.command()
async def daily(ctx, *, guess: str = None):
    global daily_pokemon, daily_date, user_guesses
    user_id = str(ctx.author.id)
    today = datetime.date.today()

    # Pick a new daily Pokémon if needed
    if daily_date != today or daily_pokemon is None:
        pick_daily_pokemon()

    # Initialize user data if not already there
    if user_id not in user_guesses:
        user_guesses[user_id] = {"hints": [], "guesses": 0, "caught": False}

    # Check if user is admin (ID only)
    is_admin = user_id in ADMIN_USER_IDS

    # Check guess limit (admins ignore this)
    if not is_admin and user_guesses[user_id]["guesses"] >= 3:
        await ctx.send(f"{ctx.author.mention}, you have used all 3 guesses for today!")
        return

    if guess is None:
        # Give hints
        available_hints = get_all_hints(daily_pokemon)

        # Filter hints the user hasn't already received
        remaining_hints = [h for h in available_hints if h not in user_guesses[user_id]["hints"]]

        if not is_admin:
            # Limit to 2 hints total for normal users
            if len(user_guesses[user_id]["hints"]) >= 2:
                await ctx.send(f"{ctx.author.mention}, you've already received your 2 hints for today! Make a guess!")
                return

            # Pick a random hint from remaining ones
            new_hint = random.choice(remaining_hints)
            user_guesses[user_id]["hints"].append(new_hint)
            await ctx.send(f"{ctx.author.mention} Hint: {new_hint}")

        else:
            # Admins can get all hints (no limit)
            if remaining_hints:
                new_hint = random.choice(remaining_hints)
                user_guesses[user_id]["hints"].append(new_hint)
                await ctx.send(f"🔑 {ctx.author.mention} Admin Hint: {new_hint}")
            else:
                await ctx.send(f"🔑 {ctx.author.mention} You have seen all possible hints for today.")

    else:
        # Handle guessing
        user_guesses[user_id]["guesses"] += 1

        if guess.lower() == daily_pokemon.name.lower():
            if user_guesses[user_id]["caught"]:
                await ctx.send(f"{ctx.author.mention}, you've already caught today's Pokémon! Come back tomorrow!")
                return

            # ✅ Player hasn't caught yet, so catch it now
            unique_id = str(ctx.author.id)
            if unique_id not in trainers:
                trainers[unique_id] = Pb.Trainer(unique_id)

            trainer = trainers[unique_id]
            added = False
            for i in range(1, 7):
                slot = getattr(trainer, f"slot{i}")
                if slot is None:
                    setattr(trainer, f"slot{i}", Pb.Pokemon(daily_pokemon.id, level=1))
                    added = True
                    break
            if not added:
                trainer.box.append(Pb.Pokemon(daily_pokemon.id, level=1))

            # Mark as caught
            user_guesses[user_id]["caught"] = True
            save_trainers()
            user_last_play[user_id] = today

            await ctx.author.send(f"🎉 Congrats! You caught **{daily_pokemon.name}** at level 1!")
            await ctx.send(f"{ctx.author.mention} got it right! Check your DMs for your new Pokémon!")
        else:
            if daily_pokemon.name.lower() in guess.lower():
                await ctx.message.delete()
            remaining = 3 - user_guesses[user_id]["guesses"]
            await ctx.send(f"{ctx.author.mention} Incorrect! You have {remaining} guesses left.")
@bot.command(name="stats")
async def stats(ctx, *, pokemon_uid: str = None):
    unique_id = str(ctx.author.id)
    if unique_id not in trainers:
        await ctx.send("You don’t have a trainer yet! Use `!trainer` first.")
        return

    trainer = trainers[unique_id]
    all_pokemon = [getattr(trainer, f"slot{i}") for i in range(1,7) if getattr(trainer, f"slot{i}")] + trainer.box

    target = None
    for p in all_pokemon:
        if p.uid == pokemon_uid:
            target = p
            break

    if not target:
        await ctx.send("Pokémon not found. Make sure you use the **unique ID** for your Pokémon.")
        return

    msg = (
        f"**{target.name}** (Lvl {target.level}) | Nature: {target.nature} | Shiny: {'Yes' if target.isShiny else 'No'}\n"
        f"**Type:** {', '.join(target.types)}\n"
        f"**Ability:** {target.ability}\n\n"
        f"**Stats:**\n"
        f"HP: {target.hp}\n"
        f"ATK: {target.att}\n"
        f"DEF: {target.defe}\n"
        f"SP.ATK: {target.spatt}\n"
        f"SP.DEF: {target.spdef}\n"
        f"SPEED: {target.spe}\n"
        f"**UID:** {target.uid}"
    )

    await ctx.send(msg)


# TRADE COMMAND GROUP
@bot.group(invoke_without_command=True)
async def trade(ctx, partner: discord.Member = None, your_pokemon_uid: str = None, their_pokemon_uid: str = None):
    if ctx.invoked_subcommand is not None:
        return

    proposer_id = str(ctx.author.id)
    if proposer_id in active_trades:
        await ctx.send("You already have an active trade!")
        return

    if partner is None or your_pokemon_uid is None or their_pokemon_uid is None:
        await ctx.send("Usage: !trade @partner your_pokemon_uid their_pokemon_uid")
        return

    partner_id = str(partner.id)
    if partner_id in active_trades:
        await ctx.send(f"{partner.name} already has an active trade!")
        return

    # Check trainers exist
    if proposer_id not in trainers or partner_id not in trainers:
        await ctx.send("Both trainers must exist!")
        return

    t1 = trainers[proposer_id]
    t2 = trainers[partner_id]

    p1, _ = get_pokemon_by_uid(t1, your_pokemon_uid)
    p2, _ = get_pokemon_by_uid(t2, their_pokemon_uid)

    if not p1 or not p2:
        await ctx.send("Error: Pokémon not found. One of you might have released it.")
        return

    # Store active trade
    active_trades[proposer_id] = {
        "partner_id": partner_id,
        "your_pokemon_uid": your_pokemon_uid,
        "their_pokemon_uid": their_pokemon_uid
    }

    await ctx.send(f"Trade proposal sent! {partner.mention}, type `!accept` to accept the trade or `!trade summary` to see details.")

# TRADE SUMMARY
@trade.command()
async def summary(ctx):
    user_id = str(ctx.author.id)

    # Find trade involving this user
    trade = None
    proposer = None
    for pid, t in active_trades.items():
        if user_id == pid or user_id == t["partner_id"]:
            trade = t
            proposer = pid
            break

    if not trade:
        await ctx.send("❌ No active trade found.")
        return

    t1 = trainers[proposer]
    t2 = trainers[trade["partner_id"]]

    p1, _ = get_pokemon_by_uid(t1, trade["your_pokemon_uid"])
    p2, _ = get_pokemon_by_uid(t2, trade["their_pokemon_uid"])

    if not p1 or not p2:
        await ctx.send("⚠️ Error: Pokémon not found. One of you might have released it.")
        return

    
    msg = (
        f"🔄 **TRADE SUMMARY** 🔄\n\n"
        f"🧑 <@{t1.UID}>\n"
        f"• Pokémon: **{p1.name}**\n"
        f"• Level: {p1.level}\n"
        f"• Nature: {p1.nature}\n"
        f"• Shiny: {'✨ Yes' if p1.isShiny else 'No'}\n\n"
        f"🧑 <@{t2.UID}>\n"
        f"• Pokémon: **{p2.name}**\n"
        f"• Level: {p2.level}\n"
        f"• Nature: {p2.nature}\n"
        f"• Shiny: {'✨ Yes' if p2.isShiny else 'No'}"
    )

    await ctx.send(msg)

# ACCEPT TRADE
@bot.command()
async def accept(ctx):
    user_id = str(ctx.author.id)

    # Find trade where user is partner
    trade = None
    proposer_id = None
    for pid, t in active_trades.items():
        if t["partner_id"] == user_id:
            trade = t
            proposer_id = pid
            break

    if not trade:
        await ctx.send("No active trade to accept.")
        return

    t1 = trainers[proposer_id]
    t2 = trainers[user_id]

    p1, loc1 = get_pokemon_by_uid(t1, trade["your_pokemon_uid"])
    p2, loc2 = get_pokemon_by_uid(t2, trade["their_pokemon_uid"])

    if not p1 or not p2:
        await ctx.send("Error: Pokémon not found. One of you might have released it.")
        del active_trades[proposer_id]
        return

    # Swap Pokémon
    def swap(trainer, loc, new_pokemon):
        if isinstance(loc, str):  # slot
            setattr(trainer, loc, new_pokemon)
        else:  # box
            trainer.box[loc[1]] = new_pokemon

    swap(t1, loc1, p2)
    swap(t2, loc2, p1)

    save_trainers()
    del active_trades[proposer_id]

    await ctx.send(f"Trade completed! {t1.UID} and {t2.UID} have swapped Pokémon.")
# -------------------- RUN --------------------
bot.run(token, log_handler=handler, log_level=logging.DEBUG)
