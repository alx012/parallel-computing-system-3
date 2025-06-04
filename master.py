# master.py
from transport_utils import send_task_to_worker, receive_result
from dag_utils import get_execution_order
from modules_config import MODULES
import json

# 任務 DAG 與資料起始點
dag = {
    "module1": [],
    "module2": ["module1"],
    "module3": ["module1"],
    "module4": ["module1"],
    "module5_dispatcher": ["module2", "module3"],
    "module6": ["module4"],
    "module5_merge": ["module5_dispatcher"],
    "module7": ["module6", "module5_merge"]
}
initial_inputs = {"module1": {"param_a": 123}}

# 多台 worker IP 對應
worker_pool = {
    "worker1": "192.168.0.101",
    "worker2": "192.168.0.102",
    "worker3": "192.168.0.103",
}

def main():
    execution_order = get_execution_order(dag)
    results = {}

    for module in execution_order:
        inputs = {dep: results[dep] for dep in dag[module]} if module in initial_inputs else {}
        if module in initial_inputs:
            inputs = initial_inputs[module]

        if module == "module5_dispatcher":
            sub_tasks = MODULES[module](**inputs)  # 返回分割子任務清單
            for i, task in enumerate(sub_tasks):
                send_task_to_worker(worker_pool[f"worker{i+1}"], "module5_sub", task)
            merged = receive_result("module5_merge")
            results["module5_merge"] = merged
        else:
            # 單模組執行（派給某台）
            worker_ip = select_worker_for(module)
            send_task_to_worker(worker_ip, module, inputs)
            result = receive_result(module)
            results[module] = result

def select_worker_for(module):
    # 簡單策略：module 名稱對應 worker（可替換成 queue-based）
    return worker_pool["worker1"]  # 暫定全派 worker1

if __name__ == "__main__":
    main()