import sqlite3

# 连接数据库
conn = sqlite3.connect('schedule.db')
conn.row_factory = sqlite3.Row

# 查询所有任务
tasks = conn.execute('SELECT * FROM tasks ORDER BY date, time_slot').fetchall()

print("数据库中的任务：")
print("-" * 50)

if len(tasks) == 0:
    print("数据库中没有任务")
else:
    for task in tasks:
        status = "已完成" if task['completed'] else "待完成"
        print(f"ID: {task['id']}")
        print(f"内容: {task['content']}")
        print(f"日期: {task['date']}")
        # 处理可能缺失的time_slot字段
        try:
            time_slot = task['time_slot']
        except (KeyError, IndexError):
            time_slot = '上午'
        print(f"时间段: {time_slot}")
        print(f"类别: {task['category']}")
        print(f"优先级: {task['priority']}")
        print(f"状态: {status}")
        print("-" * 50)

conn.close()
