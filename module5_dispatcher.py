import math
import json
import requests

def dispatch_module5(inputs, worker_urls):
    """
    拆分模組5的矩陣乘法子任務並分派給多個worker

    inputs: dict，包含 answer1、answer4
    worker_urls: list，worker 的API URL

    回傳：子任務結果清單
    """

    # 計算矩陣大小
    answer1 = inputs["answer1"]
    answer4 = abs(inputs["answer4"])  # 取絕對值避免負數
    base_size = 15000 + int((answer1 + answer4) % 50)  # 大約 15000 x 15000

    # 我們將矩陣切成 n 個小塊，假設每個子矩陣大小是 chunk_size
    chunk_size = 3000  # 依需求調整
    num_chunks = math.ceil(base_size / chunk_size)

    # 依 worker 數量均分子任務數
    num_workers = len(worker_urls)
    tasks = []

    for i in range(num_chunks):
        for j in range(num_chunks):
            # 分派給 worker (i*num_chunks + j) % num_workers
            worker_index = (i * num_chunks + j) % num_workers

            task_data = {
                "answer1": answer1,
                "answer4": answer4,
                "block_row": i,
                "block_col": j,
                "chunk_size": chunk_size,
                "base_size": base_size
            }

            tasks.append((worker_urls[worker_index], task_data))

    # 發送子任務給 workers，取得結果
    results = []
    for url, task in tasks:
        resp = requests.post(url + "/compute_module5_block", json=task)
        if resp.status_code == 200:
            result = resp.json()
            results.append(result["partial_trace"])
        else:
            print(f"Worker {url} 任務失敗，狀態碼：{resp.status_code}")

    return results