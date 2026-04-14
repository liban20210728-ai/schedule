from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime, timedelta
import os

# 创建Flask应用实例
app = Flask(__name__)

# 数据库连接函数
def get_db_connection():
    conn = sqlite3.connect('schedule.db')
    conn.row_factory = sqlite3.Row
    return conn

# 初始化数据库表
def init_db():
    conn = get_db_connection()
    # 直接在代码中创建表，不需要依赖外部文件
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            date TEXT NOT NULL,
            time_slot TEXT NOT NULL DEFAULT '上午',
            priority TEXT NOT NULL,
            category TEXT NOT NULL,
            completed INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

# 获取一周的日期列表
def get_week_dates(base_date=None):
    if base_date is None:
        base_date = datetime.now()
    else:
        base_date = datetime.strptime(base_date, '%Y-%m-%d')
    
    week_dates = []
    for i in range(-6, 1):  # 从6天前到今天
        date = base_date - timedelta(days=-i)
        week_dates.append(date.strftime('%Y-%m-%d'))
    return week_dates

# 首页路由
@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()
    
    # 处理添加日程的POST请求
    if request.method == 'POST':
        # 检查是否是添加日程的表单
        if 'content' in request.form:
            content = request.form['content']
            date = request.form['date']
            time_slot = request.form.get('time_slot', '上午')
            priority = request.form['priority']
            category = request.form['category']
            
            # 插入新日程到数据库
            conn.execute('INSERT INTO tasks (content, date, time_slot, priority, category, completed) VALUES (?, ?, ?, ?, ?, ?)',
                        (content, date, time_slot, priority, category, 0))
            conn.commit()
        
        # 检查是否是更新完成状态的请求
        elif 'task_id' in request.form:
            task_id = request.form['task_id']
            completed = request.form['completed'] == 'true'
            
            # 更新任务完成状态
            conn.execute('UPDATE tasks SET completed = ? WHERE id = ?',
                        (1 if completed else 0, task_id))
            conn.commit()
        
        # 检查是否是删除任务的请求
        elif 'delete_id' in request.form:
            delete_id = request.form['delete_id']
            conn.execute('DELETE FROM tasks WHERE id = ?', (delete_id,))
            conn.commit()
    
    # 获取所有任务，按日期排序
    tasks = conn.execute('SELECT * FROM tasks ORDER BY date').fetchall()
    conn.close()
    
    # 将Row对象转换为字典列表，以便JSON序列化
    tasks_list = []
    for task in tasks:
        # 手动构建字典，处理可能不存在的字段
        task_dict = {}
        try:
            task_dict['id'] = task['id']
            task_dict['content'] = task['content']
            task_dict['date'] = task['date']
            task_dict['priority'] = task['priority']
            task_dict['category'] = task['category']
            task_dict['completed'] = task['completed']
            # 尝试获取time_slot，如果不存在则使用默认值
            if hasattr(task, '__getitem__'):
                try:
                    task_dict['time_slot'] = task['time_slot']
                except (KeyError, IndexError):
                    task_dict['time_slot'] = '上午'
            else:
                task_dict['time_slot'] = getattr(task, 'time_slot', '上午')
        except (KeyError, IndexError) as e:
            # 如果有其他字段缺失，记录错误但继续处理
            print(f"Error processing task: {e}")
            continue
        tasks_list.append(task_dict)
    
    # 渲染首页模板
    return render_template('index.html', tasks=tasks_list, datetime=datetime, timedelta=timedelta)

# 主函数
if __name__ == '__main__':
    # 初始化数据库
    init_db()
    # 获取 PORT 环境变量，如果没有设置则默认使用 5000（本地开发时）
    port = int(os.environ.get('PORT', 5000))
    # 确保监听所有网络接口 (0.0.0.0)
    app.run(host='0.0.0.0', port=port)
