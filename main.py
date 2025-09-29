import discord
from discord.ext import commands, tasks
from translate import Translator
import random
import datetime
import os
from dotenv import load_dotenv, dotenv_values
from webserver import keep_alive

ADMIN_ROLE = 1291481484187795487
ADMIN_CHANNEL = 1291653440111644716
GENERAL = 1291506155411079178

PRAYS = {
    "imádott jézusom": 0,
    "reggeli": 1,
    "esti": 2,
    "animátor1": 3,
    "animátor2": 4
}

translator = Translator(to_lang="HU")

f = open("quotes.txt", "r", encoding="UTF-8")
quotes = f.readlines()
f.close()

f = open("Bosco.txt", "r", encoding="UTF-8")
Boscos = f.readlines()
f.close()

f = open("baji_quotes.txt", "r", encoding="UTF-8")
baji_q = f.readlines()
f.close()

f = open("prays.txt", "r", encoding="UTF-8")
prays = f.readlines()
f.close()

nextMeet = False

def control_minutes(minutes):
    new_minutes = minutes - 10

    if new_minutes < 0:
        new_minutes = 60 + new_minutes

    return new_minutes

class Client(commands.Bot):
    async def on_ready(self):
        print(f"{self.user} started!")
        await client.change_presence(activity=discord.Game(name="/segítség - és mindenre kapsz választ!"))

        try:
            guild = discord.Object(id=1291455463208255579)
            synced = await self.tree.sync(guild=guild)
            print(f"Synced {len(synced)} commands to guild {guild.id}")

        except Exception as e:
            print(f"Error syncign commands {e}")

    async def on_member_join(self, member):
        embed = discord.Embed(title="Üdv Néked!", description=f"Mindenki üdvözölje {member.mention}!")
        channels = self.get_all_channels()

        for channel in channels:
            if channel.id == GENERAL:
                await channel.send(embed=embed)

    async def on_guild_emojis_update(self, guild, before, after):
        for emoji in before:
            if emoji not in after:

                embed = discord.Embed(title="Emoji törölve!", description=f"Emoji törölve lett a szerverről!")
                embed.set_image(url=emoji.url)

                channels = self.get_all_channels()

                for channel in channels:
                    if channel.id == ADMIN_CHANNEL:
                        await channel.send(embed=embed)

        for emoji in after:
            if emoji not in before:

                embed = discord.Embed(title="Emoji hozzáadva!", description=f"Emoji hozzá lett adva a szerverhez!")
                embed.set_image(url=emoji.url)

                channels = self.get_all_channels()

                for channel in channels:
                    if channel.id == ADMIN_CHANNEL:
                        await channel.send(embed=embed)
            else:
                old_emoji = next((e for e in before if e == emoji), None)
                if old_emoji and old_emoji.name != emoji.name:

                    embed = discord.Embed(title=f"Emoji módosítva!",
                                          description=f"Emoji módosítva lett! {old_emoji.name} -> {emoji.name}")
                    embed.set_image(url=emoji.url)

                    channels = self.get_all_channels()

                    for channel in channels:
                        if channel.id == ADMIN_CHANNEL:
                            await channel.send(embed=embed)

    async def on_reaction_add(self, reaction, user):
        if reaction.message.embeds and "Meet" in reaction.message.embeds[0].footer.text:
            i = open("meet.txt", "r", encoding="UTF-8")
            text = i.readlines()
            id_m = text[0].replace("\n", "")
            i.close()
            if id_m in reaction.message.embeds[
                0].footer.text and user.name not in text and user.discriminator not in text:
                a = open("meet.txt", "a", encoding="UTF-8")
                a.write("\n" + user.name)
                a.close()

    async def on_reaction_remove(self, reaction, user):
        if reaction.message.embeds and "Meet" in reaction.message.embeds[0].footer.text:
            i = open("meet.txt", "r", encoding="UTF-8")
            id_m = i.readlines()[0].replace("\n", "")
            i.close()
            if id_m in reaction.message.embeds[0].footer.text:
                t = open("meet.txt", "r", encoding="UTF-8")
                text = t.read()
                t.close()
                text = text.replace("\n" + str(user.name), "")
                a = open("meet.txt", "w", encoding="UTF-8")
                a.write(text)
                a.close()


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.emojis = True

client = Client(command_prefix="!", intents=intents)

GUILD_ID = discord.Object(id=1291455463208255579)

@tasks.loop(seconds=1)
async def send_alert():
    global nextMeet
    if nextMeet:
        meet = open("meet.txt", "r", encoding="UTF-8")
        text = meet.readlines()
        meet.close()

        date = text[1].replace("\n", "").split(";")
        target_date = datetime.datetime(datetime.datetime.now().year, int(date[0]), int(date[1]), int(date[2]), control_minutes(int(date[3])))

        if datetime.datetime.now() >= target_date:
            people = text[2:]

            for person in people:
                person = person.replace("\n", "")
                for member in client.guilds[0].members:
                    if member.name == person:
                        await member.send("10 perc múlva meet!!!")

            nextMeet = False
            send_alert.stop()

@client.tree.command(name="idézet", description="Ír egy idézetet!", guild=GUILD_ID)
async def quote_f(interaction: discord.Interaction, quote_type: str | None):
    if quote_type is not None:
        if quote_type.lower() == "bosco":
            bosco_q = random.choice(Boscos)

            embed = discord.Embed(title=bosco_q, description="~ Don Bosco", color=0xfec350)
            await interaction.response.send_message(embed=embed)

        elif quote_type.lower() == "baj":
            raw_quote_b = random.choice(baji_q)
            quote_b = raw_quote_b.split(";")

            embed = discord.Embed(title=quote_b[1], description=f"~ {quote_b[0]}", color=0xfec350)
            await interaction.response.send_message(embed=embed)

        else:
            embed = discord.Embed(title=f"Hiba!", description=f"Hibás paraméter!", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        raw_quote = random.choice(quotes)
        quote = raw_quote.split("\t")

        embed = discord.Embed(title=translator.translate(quote[1]), description=f"~ {quote[0]}", color=0xfec350)
        await interaction.response.send_message(embed=embed)


def test_time(hour, minutes):
    if not (0 <= hour <= 24):
        return False
    if not (0 <= minutes <= 59):
        return False
    else:
        return True


def test_date(month, day):
    if not (1 <= month <= 12):
        return False
    elif not (1 <= day <= 31):
        return False
    else:
        return True



@client.tree.command(name="emlékeztető", description="Küld egy emlékeztetőt azoknak, akik erre az üzenetre reagáltak.",
                     guild=GUILD_ID)
async def alert(interaction: discord.Interaction, month: int, day: int, hour: int, minutes: int | None):
    global nextMeet
    if minutes is None:
        minutes = 0
    if test_time(hour, minutes) and test_date(month, day):
        if minutes != 0:
            id_m = str(random.randint(111111111, 999999999)) + str(random.randint(999999999, 9999999999))
            embed = discord.Embed(title=f"Emlékeztető a {month:02}. {day:02}., {hour}:{minutes:02}-kor kezdődő meetről!",
                description=f"Ha erre nyomsz egy reakciót, akkor kapni fogsz egy emlékeztetőt a meet előtt 10 perccel.",
                                  color=0x88c9f1)
            embed.set_footer(text=f"Meet #{id_m}")
            await interaction.response.send_message(embed=embed)
        else:
            id_m = str(random.randint(111111111, 999999999)) + str(random.randint(999999999, 9999999999))
            embed = discord.Embed(title=f"Emlékeztető a {month:02}. {day:02}., {hour}:00-kor kezdődő meetről!",
                description=f"Ha erre nyomsz egy reakciót, akkor kapni fogsz egy emlékeztetőt a meet előtt 10 perccel.",
                                  color=0x88c9f1)
            embed.set_footer(text=f"Meet #{id_m}")
            await interaction.response.send_message(embed=embed)

        nextMeet = True

        send_alert.start()

        m = open("meet.txt", "w", encoding="UTF-8")
        m.write(f"#{id_m}\n{month};{day};{hour};{minutes}")
        m.close()

    else:
        embed = discord.Embed(title=f"Hiba!", description=f"Hibás idő formátum!", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)

@client.tree.command(name="csatorna-ürítés", description="Létrehoz egy ugyanilyen, teljesen üres csatornát.",
                     guild=GUILD_ID)
async def clear(interaction: discord.Interaction):
    if interaction.user.get_role(ADMIN_ROLE):
        channel = interaction.channel

        new_channel = await interaction.guild.create_text_channel(
            name=channel.name,
            topic=channel.topic,
            position=channel.position,
            slowmode_delay=channel.slowmode_delay,
            nsfw=channel.nsfw,
            overwrites=channel.overwrites,
            category=channel.category
        )

        await channel.delete()

    else:
        embed = discord.Embed(title=f"Hiba!", description=f"Sajnos ehhez a parancshoz magasabb szintű rang kell!", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)

@client.tree.command(name="érme-dobás", description="Feldob egy érmét.",
                     guild=GUILD_ID)
async def coinflip(interaction: discord.Interaction):
    result = random.randint(0, 2)

    if result == 0:
        head = discord.File("head.png")

        await interaction.response.send_message(file=head)
    else:
        tail = discord.File("tail.png")

        await interaction.response.send_message(file=tail)

@client.tree.command(name="ima", description="Küld egy imát a rendelkezésre álló imákból.",
                     guild=GUILD_ID)
async def pray_f(interaction: discord.Interaction, pray: str):
    if pray in PRAYS.keys():
        selected_pray = prays[PRAYS[pray.lower()]].replace(";", "\n")
        embed = discord.Embed(title="Imádkozzunk együtt!", description=selected_pray, color=discord.Color.gold())
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(title="Hiba!", description="Sajnos ilyen ima nem található!", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)

@client.tree.command(name="segítség", description="Részletes leírást ad a parancsokról.",
                     guild=GUILD_ID)
async def command_help(interaction: discord.Interaction):
    embed = discord.Embed(title="Segítség",
                          description="A [] zárójelben lévő paraméterek kötelezőek, a () zárójelben pedig az opcionálisak vannak.",
                          colour=0x205288)

    embed.add_field(name="/idézet (quote_type)",
                    value="Ez a parancs egy számodra kiválasztott idézetet küld, ami éppen Neked szól! Ha a \"quote_type\" paraméternek megadod a \"Bosco\" kulcsszót, akkor mindenképpen egy Don Bosco idézetet kapsz, ha pedig azt, hogy \"Baj\", akkor egy saját baji aranyköpést.",
                    inline=False)
    embed.add_field(name="/emlékeztető [month] [day] [hour] (minutes)",
                    value="Ezzel a paranccsal egy meet időpontját tudod beállítani \"hónap\", \"nap\", \"óra\" és \"perc\" paraméterekkel. Ezt használva, ha a felhasználók raknak egy reakciót a bot üzenetére, akkor a meet előtt 10 perccel küld nekik a bot egy privát üzenetet emlékeztetőül.",
                    inline=False)
    embed.add_field(name="/csatorna-ürítés",
                    value="Ez a parancs létrehozza annak a csatornának a másolatát, ahova a parancs beírásra került és törli az eredeti csatornát, ezzel egy új, teljesen üres csatornát hoz létre a régi beállításaival és nevével. Csak \"Szerver kezelő\" ranggal használható!",
                    inline=False)
    embed.add_field(name="/érme-dobás",
                    value="Ez a parancs feldob egy érmét és a végeredmény fej vagy írás.",
                    inline=False)
    embed.add_field(name="/ima [pray]",
                    value="Ez a parancs küld egy imát a rendelkezére állókból. (imádott jézusom, reggeli, esti, \"animátor1\", animátor2)",
                    inline=False)

    embed.set_footer(text="Kritikákat, problémákat, hálákat, imákat Tihamér 📖-nak (NBM) lehet küldei. 🥰💖")

    await interaction.response.send_message(embed=embed)

keep_alive()

load_dotenv()

client.run(os.getenv("TOKEN"))
