import mysql.connector
import configparser

config_ini = configparser.ConfigParser()
config_ini.read('config.ini', encoding='utf-8')

db=mysql.connector.connect(host=config_ini.get('MYSQL', 'host'), user=config_ini.get('MYSQL', 'user'), password=config_ini.get('MYSQL', 'pass'))
cursor=db.cursor()

db_name = 'kakeibo_db'

# DBの削除
# cursor.execute("DROP DATABASE slum_spla_draft_cup_db")
# db.commit()

cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")
result = cursor.fetchone()

def create_db(cursor, db, db_name):
    if not result:
        cursor.execute(f"CREATE DATABASE {db_name}")
        db.commit()
        print('dbをクリエイトしました')

def use_db(cursor, db, db_name):
    cursor.execute(f"USE {db_name}")
    db.commit()
    print('dbをユーズしました')

create_db(cursor, db, db_name)
use_db(cursor, db, db_name)
#
# ここまで完成------------------------------------------------------
#

def create_expense_tb(cursor, db):

    cursor.execute("""CREATE TABLE IF NOT EXISTS expense_tb(
                    expense_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                    user_id BIGINT,
                    category INT,
                    content VARCHAR(32),
                    cost INT,
                    reason VARCHAR(32),
                    datetime datetime
                   )""")
    db.commit()
    print('expense_tbをクリエイトしました')

create_expense_tb(cursor, db)


def create_user_tb(cursor, db):

    cursor.execute("""CREATE TABLE IF NOT EXISTS user_tb(
                    user_id INT PRIMARY KEY,
                    food_1 INT,
                    food_2 INT,
                    daily_necessities INT,
                    clothing INT,
                    card INT,
                    amusement INT,
                    fare INT,
                    
                   )""")
    db.commit()
    print('expense_tbをクリエイトしました')

create_expense_tb(cursor, db)

# # データを挿入
# insert_player = "INSERT INTO player_tb (p_name, d_id, color) VALUES (%s, %s, %s);"
 
# player_list = [
#     ("apple", 100, 1),
#     ("orange", 80, 2),
#     ("melon", 500, 3),
#     ("pineapple", 700, 4) 
# ]
 
# for player in player_list:
#     cursor.execute(insert_player, player)
 
# db.commit()
 
# # データを取得
# cursor.execute('SELECT * FROM expense_tb')
# rows = cursor.fetchall()
 
# # 出力
# for i in rows:
#     print(i)

# # DBの削除
# cursor.execute("DROP TABLE expense_tb")
# db.commit()

# 接続をクローズする
cursor.close()
db.close()