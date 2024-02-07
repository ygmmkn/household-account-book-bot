import discord
from discord import app_commands 
from discord.ext import tasks
import configparser
from enum import Enum 
import datetime
from datetime import date
import mysql.connector
import kakeibo_db
import create_embed

intents = discord.Intents.all()
intents.message_content = True
intents.members = True
config_ini = configparser.ConfigParser()
config_ini.read('config.ini', encoding='utf-8')
db=mysql.connector.connect(host=config_ini.get('MYSQL', 'host'), user=config_ini.get('MYSQL', 'user'), password=config_ini.get('MYSQL', 'pass'))
cursor=db.cursor()
db_name = 'kakeibo_db'
kakeibo_db.use_db(cursor, db, db_name)

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

class category(Enum):
    飲食_自炊 = 1
    飲食_外食 = 2
    日用品 = 3
    服飾 = 4
    カード = 5
    娯楽 = 6
    交通費 = 7

@client.tree.command(
    name="出費登録コマンド",
    description="出費を登録します。")
@app_commands.describe(
    カテゴリ='出費のカテゴリを入力してください。',
    内容='出費の内容を入力してください。',
    代金='出費の代金を入力してください。',
    理由='出費の理由を入力してください。',
)
async def expense_resist(
    interaction: discord.Interaction, 
    カテゴリ:category, 
    内容:str,
    代金:int,
    理由:str=None,
):
    user_id = interaction.user.id
    category_value = カテゴリ.value
    category_name = カテゴリ.name
    content = 内容
    cost = 代金
    reason = 理由 
    time = datetime.datetime.now()
     
    expense_data=[category_name, content, cost, reason]

    insert_expense = "INSERT INTO expense_tb (user_id, category, content, cost, reason, datetime) VALUES (%s, %s, %s, %s, %s, %s);"
    expense_data =(user_id, category_value, content, cost, reason, time)
    cursor.execute(insert_expense, expense_data)
    db.commit()

    cursor.execute('SELECT * FROM expense_tb WHERE MONTH(datetime) = 2')
    rows = cursor.fetchall()
    
    # 出力
    for i in rows:
        print(i)
    db.commit()
    name = interaction.user.display_name
    avatar = interaction.user.display_avatar
    author_data = [name, avatar]
    embed = create_embed.create_embed_expense_resist(expense_data, author_data)
    await interaction.response.send_message(
        embed=embed
    )

client.run(config_ini.get('TOKEN', 'token')) 