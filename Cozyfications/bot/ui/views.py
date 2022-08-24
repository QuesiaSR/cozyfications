import discord

class ConfirmDialog(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None
    
    def set_value(self, new: bool): self.value = new
    
    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.set_value(True)
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction): 
        self.set_value(False)
        self.stop()
