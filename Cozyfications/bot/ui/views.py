import discord

class ConfirmDialog(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="ok", style=discord.ButtonStyle.green, custom_id="confirm:confirm")
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        return await interaction.response.send_message("hi")
