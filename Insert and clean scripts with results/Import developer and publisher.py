import pandas as pd
import mysql.connector

# 1. Read Excel
file_path = "D:\Desktop\Data Management\Final Project\Dataset.csv"
try:
    data = pd.read_csv(file_path, encoding='utf-8')  # 如果文件是 utf-8
except UnicodeDecodeError:
    data = pd.read_csv(file_path, encoding='ISO-8859-1')  # ISO-8859-1 编码

# 2. Deal with Developer Data
unique_developers = data['Developers'].drop_duplicates().reset_index(drop=True)
unique_developers = unique_developers.reset_index()
unique_developers.columns = ['Developer_ID', 'Developers']
unique_developers['Developer_ID'] += 1  #

# 3. Deal with Publisher Data
unique_publishers = data['Publishers'].drop_duplicates().reset_index(drop=True)
unique_publishers = unique_publishers.reset_index()
unique_publishers.columns = ['Publisher_ID', 'Publishers']
unique_publishers['Publisher_ID'] += 1

# 4. Delete duplicates
unique_developers.to_csv("unique_developers.csv", index=False)
unique_publishers.to_csv("unique_publishers.csv", index=False)

# 5. Insert data to the base
db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'Code',
    'database': 'steam_games_data'
}

try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    create_developers_table = """
    CREATE TABLE IF NOT EXISTS developers (
        Developer_ID INT PRIMARY KEY,
        Developer VARCHAR(255) NOT NULL
    );
    """
    cursor.execute(create_developers_table)

    create_publishers_table = """
    CREATE TABLE IF NOT EXISTS publishers (
        Publisher_ID INT PRIMARY KEY,
        Publisher VARCHAR(255) NOT NULL
    );
    """
    cursor.execute(create_publishers_table)

    insert_developers_query = "INSERT INTO developers (Developer_ID, Developer) VALUES (%s, %s)"
    for _, row in unique_developers.iterrows():
        cursor.execute(insert_developers_query, tuple(row))

    insert_publishers_query = "INSERT INTO publishers (Publisher_ID, Publisher) VALUES (%s, %s)"
    for _, row in unique_publishers.iterrows():
        cursor.execute(insert_publishers_query, tuple(row))

    conn.commit()
    print("Developer 和 Publisher data are successfully uploaded！")

except mysql.connector.Error as err:
    print(f"error: {err}")
finally:
    if conn.is_connected():
        cursor.close()
        conn.close()

