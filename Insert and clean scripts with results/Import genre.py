import pandas as pd
import mysql.connector

# Read data
file_path = "D:\Desktop\Data Management\Final Project\Genres, Dataset.csv"  # 替换为您的 CSV 文件路径
data = pd.read_csv(file_path)

# Clean Genres
data['Genres'] = data['Genres'].fillna('')
data['Genres'] = data['Genres'].str.strip()
data['Genres'] = data['Genres'].str.replace(r'\s*,\s*', ',', regex=True)  # 去掉逗号前后的多余空格

# 1. Create genres table
genres_list = data['Genres'].str.split(',').explode().drop_duplicates().reset_index(drop=True)  # 分解并去重
genres_df = genres_list.reset_index()
genres_df.columns = ['genre_id', 'genre_name']
genres_df['genre_id'] += 1  

# 2. 创建 games_and_genres 表数据
games_and_genres = data[['GameID', 'Genres']].copy()
games_and_genres['Genres'] = games_and_genres['Genres'].fillna('')  # 填充空值
games_and_genres = games_and_genres.assign(genre_name=games_and_genres['Genres'].str.split(',')).explode('genre_name')
games_and_genres['genre_name'] = games_and_genres['genre_name'].str.strip()  # 去除空格
games_and_genres = games_and_genres.merge(genres_df, on='genre_name', how='inner')[['GameID', 'genre_id']]  # 匹配 genre_id

db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'Code',
    'database': 'steam_games_data'
}


try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # check and create genres table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS genres (
        genre_id INT PRIMARY KEY,
        genre_name VARCHAR(255) NOT NULL
    );
    """)

    # 检查并创建 games_and_genres 表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS games_and_genres (
        gameid INT NOT NULL,
        genre_id INT NOT NULL,
        FOREIGN KEY (genre_id) REFERENCES genres(genre_id)
    );
    """)

    # 插入 genres 数据
    cursor.execute("DELETE FROM genres;")  # 清空原表数据以避免重复
    for _, row in genres_df.iterrows():
        cursor.execute("INSERT INTO genres (genre_id, genre_name) VALUES (%s, %s)", tuple(row))

    # 插入 games_and_genres 数据
    cursor.execute("DELETE FROM games_and_genres;")  # 清空原表数据以避免重复
    for _, row in games_and_genres.iterrows():
        cursor.execute("INSERT INTO games_and_genres (gameid, genre_id) VALUES (%s, %s)", tuple(row))

    # 提交事务
    conn.commit()
    print("数据已成功插入到数据库！")

except mysql.connector.Error as err:
    print(f"数据库错误: {err}")

finally:
    if conn.is_connected():
        cursor.close()
        conn.close()

