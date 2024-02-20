import discord

CATEGORY_NAME = 0
CONTENT = 1
COST = 2
REASON = 3
ID = 4

NAME = 0
AVATAR = 1

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

def create_embed_expense_resist(expense_data, author_data):
    description = ''
    description += f'カテゴリ：{expense_data[CATEGORY_NAME]}\n'
    description += f'内容：{expense_data[CONTENT]}\n'
    description += f'代金：{expense_data[COST]}円\n'
    if expense_data[REASON] != None:
        description += f'理由：{expense_data[REASON]}\n'
    description += f'出費ID：{expense_data[ID]}\n'

    embed = discord.Embed(title = '出費登録コマンド', 
                          description = description,
                          color = 0xc0fc8a) 
    
    embed.set_author(
        name=author_data[NAME], 
        icon_url=author_data[AVATAR] 
    )
    return embed

def create_embed_monthly_goal_resist(monthly_goal_data, author_data):
    description = f'{monthly_goal_data[MONTH]}月の目標\n'
    description += f'飲食(自炊)：{monthly_goal_data[FOOD_1]}円\n'
    description += f'飲食(外食)：{monthly_goal_data[FOOD_2]}円\n'
    description += f'日用品：{monthly_goal_data[DAILY_NECESSITIES]}円\n'
    description += f'服飾：{monthly_goal_data[CLOTHING]}円\n'
    description += f'カード：{monthly_goal_data[CARD]}円\n'
    description += f'娯楽：{monthly_goal_data[AMUSEMENT]}円\n'
    description += f'交通費：{monthly_goal_data[FARE]}円\n'
    description += f'合計：{monthly_goal_data[SUM]}円\n'

    embed = discord.Embed(title = '1ヶ月目標登録コマンド', 
                          description = description,
                          color = 0xc0fc8a) 
    
    embed.set_author(
        name=author_data[NAME], 
        icon_url=author_data[AVATAR] 
    )
    return embed

def create_embed_monthly_goal_resist_2(inserted_data, monthly_goal_data, author_data):
    description = f'{monthly_goal_data[MONTH]}月の目標は既に存在しています。\n以下のように更新しますか？\n\n'
    description += f'飲食(自炊)：{inserted_data[FOOD_1]}円→{monthly_goal_data[FOOD_1]}円\n'
    description += f'飲食(外食)：{inserted_data[FOOD_2]}円→{monthly_goal_data[FOOD_2]}円\n'
    description += f'日用品：{inserted_data[DAILY_NECESSITIES]}円→{monthly_goal_data[DAILY_NECESSITIES]}円\n'
    description += f'服飾：{inserted_data[CLOTHING]}円→{monthly_goal_data[CLOTHING]}円\n'
    description += f'カード：{inserted_data[CARD]}円→{monthly_goal_data[CARD]}円\n'
    description += f'娯楽：{inserted_data[AMUSEMENT]}円→{monthly_goal_data[AMUSEMENT]}円\n'
    description += f'交通費：{inserted_data[FARE]}円→{monthly_goal_data[FARE]}円\n'
    description += f'合計：{inserted_data[SUM]}円→{monthly_goal_data[SUM]}円\n'

    embed = discord.Embed(title = '1ヶ月目標登録コマンド', 
                          description = description,
                          color = 0xc0fc8a) 
    
    embed.set_author(
        name=author_data[NAME], 
        icon_url=author_data[AVATAR] 
    )
    return embed

def create_embed_info_view_m_g(monthly_goal_data, author_data):
    description = f'{monthly_goal_data[MONTH]}月の目標\n'
    description += f'飲食(自炊)：{monthly_goal_data[FOOD_1]}円\n'
    description += f'飲食(外食)：{monthly_goal_data[FOOD_2]}円\n'
    description += f'日用品：{monthly_goal_data[DAILY_NECESSITIES]}円\n'
    description += f'服飾：{monthly_goal_data[CLOTHING]}円\n'
    description += f'カード：{monthly_goal_data[CARD]}円\n'
    description += f'娯楽：{monthly_goal_data[AMUSEMENT]}円\n'
    description += f'交通費：{monthly_goal_data[FARE]}円\n'
    description += f'合計：{monthly_goal_data[SUM]}円\n'

    embed = discord.Embed(title = '情報閲覧コマンド', 
                          description = description,
                          color = 0xc0fc8a) 
    
    embed.set_author(
        name=author_data[NAME], 
        icon_url=author_data[AVATAR] 
    )
    return embed

def create_embed_simple(title, description, author_data):
    embed = discord.Embed(title = title, 
                          description = description,
                          color = 0xc0fc8a) 
    embed.set_author(
        name=author_data[NAME], 
        icon_url=author_data[AVATAR] 
    )
    return embed

def create_embed_error(msg):
    embed = discord.Embed(title = 'エラーが発生したのだ！', 
                          description = msg,
                          color = 0xff0000) 
    return embed
