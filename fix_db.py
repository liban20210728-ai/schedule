import sqlite3

# 连接数据库
conn = sqlite3.connect('schedule.db')

try:
    # 尝试添加time_slot字段
    conn.execute('ALTER TABLE tasks ADD COLUMN time_slot TEXT DEFAULT "上午"')
    conn.commit()
    print("time_slot字段添加成功")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("time_slot字段已存在")
    else:
        print(f"添加字段时出错: {e}")

# 检查字段
cursor = conn.execute('PRAGMA table_info(tasks)')
columns = [col[1] for col in cursor.fetchall()]
print("当前表字段:", columns)

conn.close()