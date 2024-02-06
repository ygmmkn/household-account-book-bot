import discord
from discord import app_commands 
from discord.ext import tasks
import configparser

intents = discord.Intents.all()
intents.message_content = True
intents.members = True
config_ini = configparser.ConfigParser()
config_ini.read('config.ini', encoding='utf-8')

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self) 
    async def setup_hook(self):
        for id in MY_GUILDS:
            self.tree.copy_global_to(guild=id)
            await self.tree.sync(guild=id)

MY_GUILDS = [discord.Object(id=config_ini.getint('GUILD', 'guild_id'))]

client = MyClient(intents=intents)

@client.event
async def on_ready(): #botログイン完了時に実行
    print('on_ready') 
    my_background_task.start()

@tasks.loop(seconds=10)  # 10秒ごとに実行
async def my_background_task():
    channel = client.get_channel(config_ini.getint('CHANNEL_ID', 'channel_id'))
    await channel.send('自動メッセージ')

@client.tree.command(
    name="command",
    description="description")
async def remove_roles(interaction: discord.Interaction):
    await interaction.response.send_message('スラッシュコマンド')

client.run(config_ini.get('TOKEN', 'token')) 