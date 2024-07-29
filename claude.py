import discord
from discord import app_commands
import os
from flask import Flask
from threading import Thread
import anthropic

# Set up Discord bot
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Set up Anthropic client
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY environment variable is not set")

# Initialize Anthropic client
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


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
    )  # De fer the response as research might take time
    try:
        response = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1024,
            system=
            "I run a product strategy consultancy. You are the best market research. Provide a brief market research about the given company. Then, go beyond the surface level and give me key insights, and useful links for further research, especially by reputable third parties. Be opinionated, find things no one else finds. Talk about positioning, target market, impact, key features, competitors, funding and more. Use statistics where possible. And provide full URLs for the links. Keep it to a few impactful, insightful sentences for each.",
            messages=[{
                "role": "user",
                "content": f"Research this company: {company}"
            }])

        # Extract the text content from the response
        research_result = ""
        for content_item in response.content:
            if content_item.type == "text":
                research_result += content_item.text

        # Split the response into chunks to avoid Discord's message length limit
        chunks = [
            research_result[i:i + 1900]
            for i in range(0, len(research_result), 1900)
        ]
        await interaction.followup.send(f"Research results for {company}:")
        for chunk in chunks:
            await interaction.followup.send(chunk)

        # Optionally, you can log or use other response information
        print(f"Model used: {response.model}")
        print(
            f"Usage: Input tokens: {response.usage.input_tokens}, Output tokens: {response.usage.output_tokens}"
        )

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
