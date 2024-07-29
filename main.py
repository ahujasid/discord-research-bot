import discord
from discord import app_commands
from openai import OpenAI
import os
from flask import Flask
from threading import Thread
# Set up Discord bot
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
# Set up OpenAI API
# openai.api_key = os.getenv('OPENAI_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openaiclient = OpenAI(api_key=OPENAI_API_KEY)


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    await tree.sync()  # Sync slash commands


@tree.command(name="wake", description="Wake up the bot")
async def wake(interaction: discord.Interaction):
    await interaction.response.send_message("I'm awake and ready to help!")


@tree.command(name="research", description="Research a company")
async def research(interaction: discord.Interaction, company: str):
    await interaction.response.defer(
    )  # Defer the response as research might take time
    try:
        response = openaiclient.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role":
                "system",
                "content":
                "I run a product strategy consultancy. You are the best researcher. Provide detailed information about the given company. Go beyond the surface level and give me key insights, and useful links for further research, specifically by reputable third parties. Be opinionated, find things no one else finds. Talk about impact & reach, competitors, program or product areas, partnerships and collaboration, funding and more. Use statistics where possible. And provide full URLs for the links. Keep it short to few impactful, insightful sentences for each."
            }, {
                "role": "user",
                "content": f"Research this company: {company}"
            }])
        research_result = response.choices[0].message.content.strip()
        # Split the response into chunks to avoid Discord's message length limit
        chunks = [
            research_result[i:i + 1900]
            for i in range(0, len(research_result), 1900)
        ]
        await interaction.followup.send(f"Research results for {company}:")
        for chunk in chunks:
            await interaction.followup.send(chunk)
    except Exception as e:
        await interaction.followup.send(f"An error occurred: {str(e)}")


# Flask server for keeping the bot alive
app = Flask('')


@app.route('/')
def home():
    return "Hello. I am alive!"


def run():
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    t = Thread(target=run)
    t.start()
    # Print the public URL
    repl_slug = os.getenv('REPL_SLUG')
    repl_owner = os.getenv('REPL_OWNER')
    if repl_slug and repl_owner:
        public_url = f"https://{repl_slug}.{repl_owner}.repl.co"
        print(f"Public URL for UptimeRobot: {public_url}")
    else:
        print(
            "Couldn't determine the public URL. Please check your Replit project settings."
        )


# Keep the bot alive
keep_alive()
# Run the bot
client.run(os.getenv('DISCORD_TOKEN'))
