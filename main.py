import discord
from discord import app_commands 
from discord.ext import tasks
import configparser
from enum import Enum 
from datetime import datetime
import mysql.connector
import kakeibo_db
import create_embed
import asyncio
import gspread
import os
import dict

intents = discord.Intents.all()
intents.message_content = True
intents.members = True

config_ini = configparser.ConfigParser()
config_ini.read('config.ini', encoding='utf-8')

db=mysql.connector.connect(host=config_ini.get('MYSQL', 'host'), user=config_ini.get('MYSQL', 'user'), password=config_ini.get('MYSQL', 'pass'))
cursor=db.cursor()
db_name = 'kakeibo_db'
kakeibo_db.use_db(cursor, db, db_name)

try:
    # ここにクエリの実行などの処理を書く
    cursor.execute("SELECT * FROM expense_tb")
    result = cursor.fetchall()
    db.commit()
    cursor.execute("SELECT * FROM monthly_goal_tb")
    result = cursor.fetchall()
    db.commit()
    print(result)
except mysql.connector.Error as err:
    # エラーが発生した場合、再接続を試みる
    if err.errno == mysql.connector.errorcode.CR_SERVER_LOST:
        print("Connection to MySQL server lost. Reconnecting...")
        db.reconnect(attempts=3, delay=2)
    else:
        print(f"Error: {err}")

dir_path = os.path.dirname(__file__)
gc = gspread.oauth(
                   credentials_filename=os.path.join(dir_path, "client_secret.json"),
                   authorized_user_filename=os.path.join(dir_path, "authorized_user.json"),
                   )
wb_id = config_ini.get('GSPREAD', 'id')

MONTH = 1
YEAR = 2
FOOD_1 = 3
FOOD_2 = 4
DAILY_NECESSITIES = 5
CLOTHING = 6
CARD = 7
AMUSEMENT = 8
FARE = 9
SUM = 10


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
    # await channel.send('自動メッセージ')

class category(Enum):
    飲食_自炊 = 1
    飲食_外食 = 2
    日用品 = 3
    服飾 = 4
    カード = 5
    娯楽 = 6
    交通費 = 7

# 出費登録コマンド
@client.tree.command(
    name="出費登録コマンド",
    description="出費を登録します。")
@app_commands.describe(
    カテゴリ='出費のカテゴリを入力してください。',
    内容='出費の内容を入力してください。',
    代金='出費の代金を入力してください。',
    コメント='出費のコメントを入力してください。',
    年月日='例(2024/2/1)の通りに出費の年月日を入力してください。'
)
async def expense_resist(
    interaction: discord.Interaction, 
    カテゴリ:category, 
    内容:str,
    代金:int,
    コメント:str=None,
    年月日:str=None,
):
    is_error = False
    user_id = interaction.user.id
    category_value = カテゴリ.value
    category_name = カテゴリ.name
    content = 内容
    cost = 代金
    comment = コメント 
    iso_formated_time = ''
    if 年月日==None:
        iso_formated_time = datetime.now().isoformat()
    else:
        try:
            original_date = 年月日.split("/")
            year, month, day = map(int, original_date)
            formated_date = datetime(year, month, day)
            iso_formated_time = formated_date.isoformat()
        except :
            is_error = True
    
    if is_error:
        msg = '年月日は 2024/2/1 のように入力してください。'
        embed = create_embed.create_embed_error(msg)
        await interaction.response.send_message(embed=embed)
    else:
        if category_name in dict.food_category_dict:
            category_name = dict.food_category_dict[category_name]

        insert_expense = "INSERT INTO expense_tb (user_id, category, content, cost, comment, datetime) VALUES (%s, %s, %s, %s, %s, %s);"
        expense = (user_id, category_value, content, cost, comment, iso_formated_time)
        cursor.execute(insert_expense, expense)
        db.commit()
        last_inserted_id = cursor.lastrowid
        expense_data=[category_name, content, cost, comment, last_inserted_id]

        cursor.execute('SELECT * FROM expense_tb WHERE MONTH(datetime) = 2')
        rows = cursor.fetchall()
        db.commit()
        
        # 出力
        for i in rows:
            print(i)
        db.commit()

        name = interaction.user.display_name
        avatar = interaction.user.display_avatar
        author_data = [name, avatar]
        embed = create_embed.create_embed_expense_resist(expense_data, author_data)

        wb = gc.open_by_key(wb_id) # household-account-book-botのファイルを開く(キーから)
        ws = wb.get_worksheet(0) # 最初のシートを開く(idは0始まりの整数)
        data = [
                [last_inserted_id, name, category_name, content, cost, comment, iso_formated_time]
                ]
        ws.append_rows(data)

        month_data = datetime.now().month # 今月を代入
        year_data = datetime.now().year
        query = """
            SELECT SUM(cost) 
            FROM expense_tb 
            WHERE user_id = %s 
            AND MONTH(datetime) = %s
            AND YEAR(datetime) = %s
            AND category = %s
        """
        filter = (user_id, month_data, year_data, category_value)
        cursor.execute(query, filter)
        category_cost_sum = cursor.fetchone()[0]
        db.commit()

        query = f"""
            SELECT {dict.category_dict[category_value]} 
            FROM monthly_goal_tb 
            WHERE month = {month_data} 
            AND year = {year_data}
            AND user_id = {user_id}
        """
        cursor.execute(query,)
        monthly_goal = cursor.fetchone()
        print(monthly_goal)
        db.commit()

        msg= '出費を登録したのだ！\n'
        
        
        if monthly_goal:
            monthly_goal_value = monthly_goal[0]
            usable_money = monthly_goal_value - category_cost_sum
            if usable_money < 0:
                msg += f'{month_data}月の{category_name}は{-usable_money}円超過してるのだ>< \nもうやめるのだ!!'
            elif usable_money == 0:
                msg += f'{month_data}月はもう{category_name}に0円も使えないのだ><'
            else: 
                msg += f'{month_data}月の{category_name}はあと{usable_money}円使えるのだ^^'
        else:
            msg += f'{month_data}月の目標が未登録なのだ\n早く登録してほしいのだ'

        await interaction.response.send_message(embed=embed)
        await interaction.channel.send(msg)

class month(Enum):
    今月 = 1
    来月 = 2

# 1ヶ月目標登録コマンド
@client.tree.command(
    name="1ヶ月目標登録コマンド",
    description="カテゴリ別に1ヶ月の予算を登録します。")
@app_commands.describe(
    月 = '今月か来月か入力してください。',
    飲食_自炊 = '飲食_自炊の予算を入力してください。',
    飲食_外食 = '飲食_外食の予算を入力してください。',
    日用品 = '日用品の予算を入力してください。',
    服飾 = '服飾の予算を入力してください。',
    カード = 'カードの予算を入力してください。',
    娯楽 = '娯楽の予算を入力してください。',
    交通費 = '交通費の予算を入力してください。',
)
async def monthly_goal_resist(
    interaction: discord.Interaction, 
    月:month,
    飲食_自炊:int,
    飲食_外食:int,
    日用品:int,
    服飾:int,
    カード:int,
    娯楽:int,
    交通費:int,
):
    name = interaction.user.display_name
    avatar = interaction.user.display_avatar
    author_data = [name, avatar]
    user_id = interaction.user.id
    month_data = datetime.now().month # 今月を代入
    year_data = datetime.now().year # 今年を代入
    new_m_g_data = [user_id, month_data , year_data, 飲食_自炊, 飲食_外食, 日用品, 服飾, カード, 娯楽, 交通費]
    m_g_sum = sum(new_m_g_data[3:])
    new_m_g_data.append(m_g_sum)
    
    if 月 == '来月':
        if month_data == 12:
            year_data =+ 1
            month_data = 1
        else :
            month_data +=1
    
    query = f"""
        SELECT *
        FROM monthly_goal_tb 
        WHERE month = {month_data} 
        AND year = {year_data}
        AND user_id = {user_id}
    """
    cursor.execute(query,)
    result = cursor.fetchone()
    db.commit()

    if result:
        inserted_m_g_data = result
        embed = create_embed.create_embed_monthly_goal_resist_2(
            inserted_m_g_data, new_m_g_data, author_data
            )
        
        insert_monthly_goal = f'''INSERT INTO monthly_goal_tb (
            user_id, month, year, food_1, food_2, daily_necessities, clothing, card, amusement, fare, sum, is_edit_data) 
            VALUES ({user_id}, {month_data}, {year_data}, 
                {new_m_g_data[FOOD_1]}, {new_m_g_data[FOOD_2]}, {new_m_g_data[DAILY_NECESSITIES]}, 
                {new_m_g_data[CLOTHING]}, {new_m_g_data[CARD]}, {new_m_g_data[AMUSEMENT]}, 
                {new_m_g_data[FARE]}, {new_m_g_data[SUM]}, TRUE
            );'''
        cursor.execute(insert_monthly_goal,)
        db.commit()

        query = f"""
                SELECT *
                FROM monthly_goal_tb 
                WHERE is_edit_data = TRUE
                """
        cursor.execute(query,)
        result = cursor.fetchone()
        db.commit()
        print(result)

        button_yes = discord.ui.Button(label="はい",style=discord.ButtonStyle.primary,custom_id="monthly_goal_edit_yes")
        button_no  = discord.ui.Button(label="いいえ", style=discord.ButtonStyle.secondary, custom_id="monthly_goal_edit_no")
        view = discord.ui.View()
        view.add_item(button_yes)
        view.add_item(button_no)
        await interaction.response.send_message(embed=embed ,view=view)
    else:
        insert_monthly_goal = f'''INSERT INTO monthly_goal_tb (
            user_id, month, year, food_1, food_2, daily_necessities, clothing, card, amusement, fare, sum, is_edit_data) 
            VALUES ({user_id}, {month_data}, {year_data}, 
                {new_m_g_data[FOOD_1]}, {new_m_g_data[FOOD_2]}, {new_m_g_data[DAILY_NECESSITIES]}, 
                {new_m_g_data[CLOTHING]}, {new_m_g_data[CARD]}, {new_m_g_data[AMUSEMENT]}, 
                {new_m_g_data[FARE]}, {new_m_g_data[SUM]}, FALSE
            );'''
        cursor.execute(insert_monthly_goal,)
        db.commit()

        # データを取得
        cursor.execute('SELECT * FROM monthly_goal_tb')
        rows = cursor.fetchall()
        db.commit()
        # 出力
        for i in rows:
            print(i)
        
        embed = create_embed.create_embed_monthly_goal_resist(new_m_g_data, author_data)

        wb = gc.open_by_key(wb_id) # household-account-book-botのファイルを開く(キーから)
        ws = wb.get_worksheet(1) # 最初のシートを開く(idは0始まりの整数)
        data = [
                [name, month_data, year_data, 飲食_自炊, 飲食_外食, 日用品, 服飾, カード, 娯楽, 交通費, sum]
                ]
        ws.append_rows(data)

        await interaction.response.send_message(embed=embed)
        await interaction.channel.send(f'{月.name}の目標を登録したのだ！')

# 情報閲覧コマンド
@client.tree.command(
    name="情報閲覧コマンド",
    description="様々な情報を表示します。")
async def info_view(interaction: discord.Interaction, ):
    name = interaction.user.display_name
    avatar = interaction.user.display_avatar
    author_data = [name, avatar]
    user_id = interaction.user.id
    button_1 = discord.ui.Button(label="今月の目標",style=discord.ButtonStyle.blurple,custom_id="info_view_m_g")
    button_2  = discord.ui.Button(label="今月の出費", style=discord.ButtonStyle.blurple, custom_id="info_view_ex")
    view = discord.ui.View()
    view.add_item(button_1)
    view.add_item(button_2)
    title = '情報閲覧コマンド'
    description = '閲覧したい情報のボタンを押してください。'
    embed = create_embed.create_embed_simple(title, description, author_data)
    await interaction.response.send_message(embed=embed ,view=view)

#全てのインタラクションを取得
@client.event
async def on_interaction(inter:discord.Interaction):
    try:
        if inter.data['component_type'] == 2:
            await on_button_click(inter)
        elif inter.data['component_type'] == 3:
            await on_dropdown(inter)
    except KeyError:
        pass

# Button
async def on_button_click(inter:discord.Interaction):
    custom_id = inter.data["custom_id"]
    print(custom_id)
    user_id = inter.user.id
    name = inter.user.display_name
    avatar = inter.user.display_avatar
    author_data = [name, avatar]
    current_month = datetime.now().month 
    current_year = datetime.now().year
    if custom_id == 'monthly_goal_edit_yes':
        query = f"""
        SELECT *
        FROM monthly_goal_tb 
        WHERE is_edit_data = TRUE
        """
        cursor.execute(query,)
        result = cursor.fetchone()
        db.commit()

        if not result:
            msg = 'はいを何回も押すのはやめるのだ！'
            embed = create_embed.create_embed_error(msg)
            await inter.response.send_message(embed=embed)
            return
        update_monthly_goal = f'''
            UPDATE monthly_goal_tb 
            SET 
                food_1 = {result[FOOD_1]},
                food_2 = {result[FOOD_2]},
                daily_necessities = {result[DAILY_NECESSITIES]},
                clothing = {result[CLOTHING]},
                card = {result[CARD]},
                amusement = {result[AMUSEMENT]},
                fare = {result[FARE]},
                sum = {result[SUM]}
            WHERE 
                user_id = {user_id} AND
                month = {result[MONTH]} AND
                year = {result[YEAR]} AND
                is_edit_data = 0
        '''

        cursor.execute(update_monthly_goal)
        db.commit()

        # 確認 2つあればOK
        query = f"""
        SELECT *
        FROM monthly_goal_tb
        """
        cursor.execute(query,)
        result = cursor.fetchall()
        db.commit()
        print(result)

        delete_query = f"""
            DELETE FROM monthly_goal_tb
            WHERE is_edit_data = TRUE
        """
        cursor.execute(delete_query)
        db.commit()

        title = ''
        description = '1ヶ月目標を更新したのだ'
        embed = create_embed.create_embed_simple(title, description, author_data)
        await inter.response.send_message(embed=embed)
    elif custom_id == 'monthly_goal_edit_no':
        title = ''
        description = '更新は行われなかったのだ'
        embed = create_embed.create_embed_simple(title, description, author_data)
        await inter.response.send_message(embed=embed)
    elif custom_id == 'info_view_m_g':
        query = f"""
        SELECT *
        FROM monthly_goal_tb 
        WHERE user_id = {user_id} AND
              month = {current_month} AND
              year = {current_year} AND
        """
        cursor.execute(query,)
        result = cursor.fetchone()
        db.commit()
        print(result)
        title = ''
        description = 'a'
        embed = create_embed.create_embed_simple(title, description, author_data)
        await inter.response.send_message(embed=embed)



# Select
async def on_dropdown(inter:discord.Interaction):
    custom_id = inter.data["custom_id"]
    user_id = inter.user.id
    name = inter.user.display_name
    avatar = inter.user.display_avatar
    author_data = [name, avatar]

    if custom_id == 'info_view_m_g':
        button_1 = discord.ui.Button(label="今月の目標",style=discord.ButtonStyle.blurple,custom_id="info_view_m_g_current_month")
        button_2  = discord.ui.Button(label="今月の目標", style=discord.ButtonStyle.blurple, custom_id="info_view_m_g_next_month")
        view = discord.ui.View()
        view.add_item(button_1)
        view.add_item(button_2)
        title = '情報閲覧コマンド'
        description = '閲覧したい情報のボタンを押してください。'
        embed = create_embed.create_embed_simple(title, description, author_data)
        await inter.response.send_message(embed=embed ,view=view)
    elif custom_id == 'info_view_ex':
        a=1
    # select_values = inter.data["values"]
    # print(custom_id, select_values)
    await inter.response.send_message("Select!",ephemeral=True)

client.run(config_ini.get('TOKEN', 'token')) 