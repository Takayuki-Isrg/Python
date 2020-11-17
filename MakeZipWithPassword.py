import pyminizip, os

# カレントディレクトリを 'c:\\pdf_storage' に変更
os.chdir('c:\\pdf_storage')

# 圧縮対象のファイルをリストに格納
files = ['Word_Collection - Auth & Security.pdf', 'Word_Collection - Database.pdf']

# 圧縮処理実行
pyminizip.compress_multiple(files, ['\\', '\\'], 'c:\\TestForMacro\\PDF_Storage.zip', 'Comac-Z234', 5)