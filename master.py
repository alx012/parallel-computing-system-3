import uuid
from transport_utils import send_task_to_worker, receive_result, get_available_worker
from dag_utils import build_dag
from modules_config import get_modules_config
from db_utils import register_result_location, init_db
from module5_dispatcher import generate_subtasks
from module5_merge import reset_merge_state

# 啟動時請使用者輸入數據
def ask_user_inputs():
    num1 = int(input("請輸入 num1："))
    num2 = int(input("請輸入 num2："))
    num3 = int(input("請輸入 num3："))
    return {"num1": num1, "num2": num2, "num3": num3}

# Worker Pool 註冊
worker_pool = {
    "worker1": "http://localhost:5001",
    "worker2": "http://localhost:5002",
    "worker3": "http://localhost:5003",
    "worker4": "http://localhost:5004",
    "worker5": "http://localhost:5005"
}

def main(user_inputs):
    init_db()
    modules = get_modules_config(user_inputs)
    dag, execution_order = build_dag(modules)
    result_map = {}

    for module in execution_order:
        if module == "module1":
            inputs = user_inputs
        else:
            inputs = {}
            for dep in modules[module]["requires"]:
                inputs.update(result_map[dep])

        exec_id = str(uuid.uuid4())

        if module == "module5_dispatcher":
            subtasks = generate_subtasks(inputs)
            reset_merge_state(len(subtasks))
            for idx, subtask in enumerate(subtasks):
                worker = get_available_worker(worker_pool, idx)
                send_task_to_worker(worker, {
                    "module_name": "module5_sub",
                    "input_data": subtask,
                    "execution_id": f"{exec_id}_{idx}"
                })
            result = receive_result("module5_merge")
            result_map["module5_merge"] = result
            register_result_location("module5_merge", result, worker)

        elif module == "module5_merge":
            continue

        else:
            worker = get_available_worker(worker_pool)
            task_packet = {
                "module_name": module,
                "input_data": inputs,
                "execution_id": exec_id
            }
            send_task_to_worker(worker, task_packet)
            result = receive_result(module)
            result_map[module] = result
            register_result_location(module, result, worker)

if __name__ == "__main__":
    user_inputs = ask_user_inputs()
    main(user_inputs)
