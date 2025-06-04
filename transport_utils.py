# === [2] transport_utils.py (使用 Flask 與 requests 實作) ===
import requests
import time

result_cache = {}  # 暫存結果（模擬回傳）

def send_task_to_worker(worker_url, payload):
    try:
        r = requests.post(worker_url + "/compute", json=payload)
        r.raise_for_status()
    except Exception as e:
        print(f"傳送任務至 {worker_url} 失敗：{e}")


def receive_result(module_name, timeout=60):
    # 模擬版本，等待 Flask worker 上傳結果至 /submit_result
    start_time = time.time()
    while time.time() - start_time < timeout:
        if module_name in result_cache:
            return result_cache.pop(module_name)
        time.sleep(1)
    raise TimeoutError(f"等待模組 {module_name} 結果逾時")


def store_result_from_worker(module_name, result):
    result_cache[module_name] = result


def get_available_worker(pool):
    return list(pool.values())[0]  # 簡單版：回傳第一個 worker，可改成輪詢
