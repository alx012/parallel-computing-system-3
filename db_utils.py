import sqlite3
import json
import time

DB_FILE = 'dag_result.db'

def init_db():
    """初始化資料庫，並清空現有結果"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS module_result (
                module_id INTEGER PRIMARY KEY,
                result_json TEXT
            )
        ''')
        # 清空現有結果
        c.execute('DELETE FROM module_result')
        conn.commit()

def save_result(module_id, result_dict):
    """儲存模組輸出結果（JSON 格式）"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        result_json = json.dumps(result_dict)
        c.execute('INSERT OR REPLACE INTO module_result (module_id, result_json) VALUES (?, ?)', 
                 (module_id, result_json))
        conn.commit()

def fetch_answers(required_keys):
    """取得所需答案"""
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
    """獲取所有模組結果"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT module_id, result_json FROM module_result ORDER BY module_id')
        return [(module_id, json.loads(result_json)) for module_id, result_json in c.fetchall()]

def get_final_result():
    """獲取最終結果（模組7的結果）"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT result_json FROM module_result WHERE module_id = 7')
        result = c.fetchone()
        if result:
            return json.loads(result[0])
        return None