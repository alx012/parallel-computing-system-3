# ============================================
# master.py
# ============================================
import uuid
from transport_utils import send_task_to_worker, receive_result, get_available_worker
from dag_utils import build_dag
from modules_config import get_modules_config
from db_utils import register_result_location, init_db
from module5_dispatcher import generate_subtasks
from module5_merge import reset_merge_state

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
    print("\n🔄 初始化資料庫 ...")
    init_db()

    print("\n🧩 載入模組與建構 DAG ...")
    modules = get_modules_config(user_inputs)
    dag, execution_order = build_dag(modules)
    result_map = {}

    print(f"\n🚀 模組執行順序為：{execution_order}\n")

    for idx, module in enumerate(execution_order):
        print(f"\n=== 🟡 執行模組 {module} ===")

        # 準備輸入資料
        if module == "module1":
            inputs = user_inputs.copy()
        else:
            inputs = {}
            for dep in modules[module]["requires"]:
                if dep in result_map:
                    inputs.update(result_map[dep])

        exec_id = str(uuid.uuid4())

        if module == "module5_dispatcher":
            subtasks = generate_subtasks(inputs)
            reset_merge_state(len(subtasks))

            for sub_idx, subtask in enumerate(subtasks):
                worker = get_available_worker(worker_pool, sub_idx)
                print(f"📤 傳送子任務 {sub_idx} 至 {worker}")
                send_task_to_worker(worker, {
                    "module_name": "module5_sub",
                    "input_data": subtask,
                    "execution_id": f"{exec_id}_{sub_idx}",
                    "user_inputs": user_inputs
                })

            print("⏳ 等待 module5_merge 合併結果...")
            result = receive_result("module5_merge")
            result_map["module5_merge"] = result
            register_result_location("module5_merge", result, worker)
            print(f"✅ module5_merge 合併結果：{result}")
            continue

        elif module == "module5_merge":
            print("⚠️ module5_merge 由 dispatcher 控制，不需此處執行")
            continue

        # 一般模組：傳送任務到 worker
        worker = get_available_worker(worker_pool, idx)
        task_packet = {
            "module_name": module,
            "input_data": inputs,
            "execution_id": exec_id,
            "user_inputs": user_inputs
        }

        print(f"📤 發送 {module} 到 {worker}")
        send_response = send_task_to_worker(worker, task_packet)

        if send_response is None:
            print(f"❌ 無法傳送模組 {module}，跳過此模組")
            continue

        # 等待該模組結果
        try:
            print(f"⏳ 等待模組 {module} 執行結果 ...")
            result = receive_result(module)
            result_map[module] = result
            register_result_location(module, result, worker)
            print(f"✅ 模組 {module} 完成，結果為：{result}")
        except Exception as e:
            print(f"❌ 模組 {module} 執行失敗或超時：{e}")

    print("\n🎉 所有模組執行完畢")
    if "module7" in result_map:
        print(f"\n📦 最終結果：{result_map['module7']}")
    else:
        print("\n⚠️ 未找到最終結果，可能執行中途失敗")

if __name__ == "__main__":
    user_inputs = ask_user_inputs()
    main(user_inputs)