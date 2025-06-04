import sqlite3
import json
import time

DB_FILE = 'dag_result.db'

def init_db():
    """初始化資料庫與結果索引表"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        # 模組結果表
        c.execute('''
            CREATE TABLE IF NOT EXISTS module_result (
                module_id TEXT PRIMARY KEY,
                result_json TEXT
            )
        ''')
        # 模組位置索引表
        c.execute('''
            CREATE TABLE IF NOT EXISTS result_index (
                module TEXT PRIMARY KEY,
                location TEXT,
                result_json TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # 清空現有結果
        c.execute('DELETE FROM module_result')
        c.execute('DELETE FROM result_index')
        conn.commit()

def save_result(module_id, result_dict):
    """儲存模組輸出結果（僅資料）"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        result_json = json.dumps(result_dict, ensure_ascii=False)
        c.execute('INSERT OR REPLACE INTO module_result (module_id, result_json) VALUES (?, ?)',
                  (str(module_id), result_json))  # <-- 確保 module_id 是 str
        conn.commit()

def register_result_location(module_name, result, worker_url):
    """記錄模組結果與其執行位置"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        result_json = json.dumps(result, ensure_ascii=False)
        c.execute('''
            INSERT OR REPLACE INTO result_index (module, location, result_json)
            VALUES (?, ?, ?)
        ''', (str(module_name), worker_url, result_json))  # <-- 確保 module_name 是 str
        conn.commit()

def fetch_answers(required_keys):
    """從 module_result 取得前驅模組的輸出值"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        collected = {}
        while True:
            c.execute('SELECT result_json FROM module_result')
            for row in c.fetchall():
                data = json.loads(row[0])
                for key in required_keys:
                    if key in data and key not in collected:
                        collected[key] = data[key]
            if all(k in collected for k in required_keys):
                return collected
            time.sleep(0.1)

def get_all_results():
    """取得所有結果（module_result）"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT module_id, result_json FROM module_result ORDER BY module_id')
        return [(module_id, json.loads(result_json)) for module_id, result_json in c.fetchall()]

def get_final_result():
    """取得模組7的最終結果"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT result_json FROM module_result WHERE module_id = ?', ("7",))
        result = c.fetchone()
        return json.loads(result[0]) if result else None

def get_execution_order(modules_config):
    """
    根據模組依賴關係（requires），使用拓撲排序回傳正確執行順序。
    modules_config: 由 get_modules_config(user_inputs) 回傳的模組設定
    """
    from collections import defaultdict, deque

    # 建立 DAG 圖形與入度統計
    graph = defaultdict(list)
    indegree = defaultdict(int)

    for name, config in modules_config.items():
        for dep in config["requires"]:
            graph[dep].append(name)
            indegree[name] += 1
        indegree.setdefault(name, 0)  # 確保所有節點都存在

    # 拓撲排序：從沒有前置模組的開始
    queue = deque([name for name in modules_config if indegree[name] == 0])
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)

    if len(order) != len(modules_config):
        raise Exception("DAG 模組定義出現循環，無法排序")

    return order
