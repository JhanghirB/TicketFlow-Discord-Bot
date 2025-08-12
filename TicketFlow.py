import nextcord
from nextcord.ext import commands
from nextcord import ButtonStyle, Interaction, Embed, ui
import json
import os

# INSERT BOT AND SERVER ID
TESTING_GUILD_ID = 0
TICKET_MANAGER_ROLE = 0

# Enable intents for members and message content
intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True

# Pass intents when creating the bot instance
bot = commands.Bot(intents=intents)

# Dictionary of car names with their possible aliases
# 
cars_with_aliases = {

    'Gintani SVJ Twin Turbo': ['gintani svj twin turbo','gintani svj', 'svj', 'twin turbo svj'],
    'Leo Mansory Escalade V ESV': ['leo mansory escalade v esv','leo escalade', 'mansory escalade', 'escalade v', 'leo mansory'],
    'Mansory Escalade V ESV': ['mansory escalade v esv','mansory escalade', 'escalade v', 'esv'],
    'Custom Big Turbo M340i': ['custom big turbo m340i', 'm340i', '340i', 'big turbo m340i', 'bmw340i']

}

# global stage variable
ticket_states = {}

STATE_FILE = "ticket_states.json"

# Load ticket states from file
def load_states():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as file:
            return json.load(file)
    return {}

# Save ticket states to file
def save_states():
    with open(STATE_FILE, "w") as file:
        json.dump(ticket_states, file)

ticket_states = load_states()





def messageContainsCar(msg: str):
    msg = msg.lower()
    matched_cars = []

    for car, aliases in cars_with_aliases.items():
        # Check if any alias matches the message
        if any(alias in msg for alias in aliases):
            matched_cars.append(car)
    
    return matched_cars if matched_cars else None

def messageYes(msg: str):
    msg = msg.lower()[0]
    return msg == 'y'

def messageNo(msg: str):
    msg = msg.lower()[0]
    return msg == 'n'












# Confirmation view to close the ticket
class ConfirmCloseView(ui.View):
    def __init__(self, ticket_channel, user):
        super().__init__(timeout=None)
        self.ticket_channel = ticket_channel
        self.user = user

    @ui.button(label="Close", style=ButtonStyle.red, emoji="✅")
    async def confirm_close(self, button: ui.Button, interaction: Interaction):
        """Restrict the ticket channel visibility to the ticket manager role."""
        guild = interaction.guild
        ticket_manager_role = guild.get_role(TICKET_MANAGER_ROLE)
        if not ticket_manager_role:
            await interaction.response.send_message("Ticket manager role not found.", ephemeral=True)
            return

        # Update channel permissions
        overwrites = {
            self.user: nextcord.PermissionOverwrite(read_messages=False),  # Remove user access
            guild.default_role: nextcord.PermissionOverwrite(read_messages=False),  # Default hidden
            ticket_manager_role: nextcord.PermissionOverwrite(read_messages=True, send_messages=True)  # Manager visible
        }

        await self.ticket_channel.edit(overwrites=overwrites, reason="Ticket closed and restricted to managers.")
        
        # Update state
        if self.ticket_channel.id in ticket_states:
            del ticket_states[self.ticket_channel.id]
            save_states()

        await interaction.response.send_message("The ticket has been closed.", ephemeral=True)

    @ui.button(label="Cancel", style=ButtonStyle.grey, emoji="❌")
    async def cancel_close(self, button: ui.Button, interaction: Interaction):
        """Cancels the ticket closure."""
        await interaction.response.send_message("Ticket closure cancelled.", ephemeral=True)


# Close button in the ticket channel
class CloseTicketView(ui.View):
    def __init__(self, user):
        super().__init__(timeout=None)
        self.user = user

    @ui.button(label="Close Ticket", style=ButtonStyle.red, emoji="🔒")
    async def close_ticket(self, button: ui.Button, interaction: Interaction):
        """Prompts the user with a confirmation message to close the ticket."""
        await interaction.response.send_message(
            "Are you sure you want to close the ticket?",
            view=ConfirmCloseView(interaction.channel, self.user),
            ephemeral=True
        )


# Button to create tickets
class TicketButton(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Create Ticket", style=ButtonStyle.green, emoji="📩")
    async def create_ticket(self, button: ui.Button, interaction: Interaction):
        """Creates a new ticket channel for the user."""
        guild = interaction.guild
        user = interaction.user

        # Check for existing ticket
        for channel in guild.text_channels:
            if channel.name == f"purchase-ticket-{user.name.lower()}":
                await interaction.response.send_message(
                    f"You already have an open ticket: {channel.mention}", ephemeral=True
                )
                return

        # Set up permissions for the ticket channel
        overwrites = {
            guild.default_role: nextcord.PermissionOverwrite(read_messages=False),
            user: nextcord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: nextcord.PermissionOverwrite(read_messages=True, send_messages=True),
        }

        # Create the ticket channel
        ticket_channel = await guild.create_text_channel(
            name=f"purchase-ticket-{user.name.lower()}",
            overwrites=overwrites,
            reason="New purchase ticket"
        )

        # Save ticket state
        ticket_states[ticket_channel.id] = {"stage": 0, "confirmed": False}
        save_states()

        # Send a welcome message with the "Close Ticket" button
        await ticket_channel.send(
            f"Hello {user.mention}, please enter the vehicles you would like to purchase.",
            view=CloseTicketView(user)
        )

        await interaction.response.send_message(
            f"Ticket created: {ticket_channel.mention}", ephemeral=True
        )


# Slash command to setup the ticket system
@bot.slash_command(description="Setup the ticket creation message", guild_ids=[TESTING_GUILD_ID])
async def setup_ticket(interaction: nextcord.Interaction):
    """Sends the ticket creation embed."""
    embed = Embed(
        title="Purchase Ticket",
        description="To purchase any of the debadged or lore builds, create a ticket by clicking the button below.",
        color=0x57F287
    )
    embed.set_footer(text="TicketTool.xyz")

    # Send the embed with the ticket creation button
    await interaction.response.send_message(embed=embed, view=TicketButton())










@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.event
async def on_message(message):

    # Avoid responding to the bot's own messages
    if message.author == bot.user:
        return


    channel_id = message.channel.id

    if channel_id not in ticket_states:
        return

    Stage = ticket_states[channel_id]["stage"]


    
    if message.content.lower() =="refresh":
        ticket_states[channel_id]["stage"] = 0
        save_states()
        await message.channel.send("Please enter the vehicles you would like to purchase.")
        return

    if message.content.lower()== "i agree" and Stage == 20:
        await message.channel.send("Await further DMs from Im-Potato. Waiting times may vary based on availability.")
        del ticket_states[channel_id]  # Remove state after completion
        save_states()
        return



    if Stage == 5:
        if messageYes(message.content):
            confirmation_message = f"""
            *By purchasing any assets from Potato-Mods you {message.author.mention}*
            *agree to the rules of the discord server and the following:*\n
            **I POTATO - MODS AM NOT RESPONSIBLE FOR ANYTHING THAT HAPPENS AFTER THE PURCHASE OF ANY DEBADGED VEHICLES, YOU ARE BUYING KNOWING THESE ARE SIMPLY DEBADGED IRL VEHICLES**\n
            If you {message.author.mention} agree to these Terms And Conditions type **I AGREE** below
            """
            await message.channel.send(confirmation_message)
            ticket_states[channel_id]["stage"] = 20  # Move to Stage 20
            save_states()


        elif messageNo(message.content):
            await message.channel.send("Please let us know what you'd like instead.")
            ticket_states[channel_id]["stage"] = 0  # Reset to Stage 0
            save_states()
        return

    # Check if the message contains any car alias
    if Stage==0:
        matched_cars = messageContainsCar(message.content)
        if matched_cars:
            sendback = f"You requested: {', '.join(matched_cars)}. Is this correct? (y/n)"
            await message.channel.send(sendback)
            ticket_states[channel_id]["stage"] = 5  # Move to Stage 5
            save_states()
        return
    

    
    

    # Ensure commands still work
    await bot.process_commands(message)

# bot id
bot.run('')
