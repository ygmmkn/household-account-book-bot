import discord

CATEGORY_NAME = 0
CONTENT = 1
COST = 2
REASON = 3
NAME = 0
AVATAR = 1

def create_embed_expense_resist(expense_data, author_data):
    embed = discord.Embed(title = '出費登録',
                          description = 'desc', 
                          color = 0xc0fc8a)
    embed.set_author(
        name=author_data[NAME], 
        icon_url=author_data[AVATAR] 
    )
    return embed