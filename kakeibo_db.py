import mysql.connector
import configparser

config_ini = configparser.ConfigParser()
config_ini.read('config.ini', encoding='utf-8')

db=mysql.connector.connect(host=config_ini.get('MYSQL', 'host'), user=config_ini.get('MYSQL', 'user'), password=config_ini.get('MYSQL', 'pass'))
cursor=db.cursor()

db_name = 'kakeibo_db'

def drop_db(cursor, db):
    cursor.execute(f"DROP DATABASE {db_name}")
    db.commit()

def create_db(cursor, db, db_name):
    cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")
    result = cursor.fetchone()
    if not result:
        cursor.execute(f"CREATE DATABASE {db_name}")
        print('dbをcreateしました')
    db.commit()

def use_db(cursor, db, db_name):
    cursor.execute(f"USE {db_name}")
    db.commit()
    print('dbをuseしました')

def create_expense_tb(cursor, db):
    cursor.execute(f"SHOW TABLES LIKE 'expense_tb'")
    result = cursor.fetchone()
    if not result:
        cursor.execute("""CREATE TABLE IF NOT EXISTS expense_tb(
                        expense_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                        user_id BIGINT,
                        category INT,
                        content VARCHAR(32),
                        cost INT,
                        comment VARCHAR(32),
                        datetime datetime
                    );""")
        print('expense_tbをクリエイトしました')
    db.commit()

def create_monthly_goal_tb(cursor, db):
    cursor.execute(f"SHOW TABLES LIKE 'monthly_goal_tb'")
    result = cursor.fetchone()
    if not result:
        cursor.execute("""CREATE TABLE IF NOT EXISTS monthly_goal_tb(
                        user_id BIGINT,
                        month INT,
                        year INT,
                        food_1 INT,
                        food_2 INT,
                        daily_necessities INT,
                        clothing INT,
                        card INT,
                        amusement INT,
                        fare INT,
                        sum INT,
                        is_edit_data BOOLEAN
                    );""")
        print('monthly_goal_tbをクリエイトしました')
    db.commit()

def drop_tb(tb, cursor, db):
    cursor.execute(f"DROP TABLE {tb}")
    db.commit()

tb_name_1 = 'expense_tb'
tb_name_2 = 'monthly_goal_tb'
# drop_db(cursor, db)
create_db(cursor, db, db_name)
use_db(cursor, db, db_name)
# drop_tb(tb_name_1, cursor, db)
# drop_tb(tb_name_2, cursor, db)
create_expense_tb(cursor, db)
create_monthly_goal_tb(cursor, db)

# query = f"""
#         SELECT *
#         FROM monthly_goal_tb 
#         WHERE is_edit_data = true
#         """
# cursor.execute(query,)
# result = cursor.fetchone()
# db.commit()

query = f"""
        SELECT *
        FROM monthly_goal_tb
        """
cursor.execute(query,)
result = cursor.fetchall()
db.commit()
print(result)


# 接続をクローズする
cursor.close()
db.close()