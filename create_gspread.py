import gspread
import os

dir_path = os.path.dirname(__file__)
gc = gspread.oauth(
                   credentials_filename=os.path.join(dir_path, "client_secret.json"),
                   authorized_user_filename=os.path.join(dir_path, "authorized_user.json"),
                   )

wb_id = '1JYFoMvN-7d9_6UTEVfICNVxI6Hm8T5FQQBVYNgLnGq0'


# スプレッドシートに書き込み
wb = gc.open_by_key(wb_id) # household-account-book-botのファイルを開く(キーから)
ws = wb.get_worksheet(0) # 最初のシートを開く(idは0始まりの整数)

data = [
        ['出費ID', 'ユーザID', 'カテゴリ', '内容', '代金', 'コメント', '日時']
        ]

# 複数行一括書き込み
ws.append_rows(data)

# # 単行書き込み
# ws.append_row([0, -11, '2023/05/04', '単行書き込み'])