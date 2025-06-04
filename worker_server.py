from flask import Flask, request, jsonify
from module_runner import run_module
from db_utils import save_result
from transport_utils import store_result_from_worker
from module5_merge import submit_partial_trace

app = Flask(__name__)

@app.route("/compute", methods=["POST"])
def compute():
    try:
        data = request.get_json()
        module = data["module_name"]
        inputs = data["input_data"]
        exec_id = data.get("execution_id", "unknown")

        print(f"[WORKER] 收到任務 {module} (執行 ID: {exec_id})，輸入：{inputs}")

        if module == "module5_sub":
            # 執行子區塊計算
            trace_val = compute_trace_block(inputs)  # 使用 Dask 模擬子計算
            submit_partial_trace(trace_val)
            print(f"[WORKER] 子區塊 trace={trace_val} 已提交")
            return jsonify({"status": "submitted trace", "trace": trace_val})
        else:
            # ✅ 將 inputs 傳給 run_module 作為 user_inputs
            result = run_module(module, inputs.copy(), user_inputs=inputs.copy())
            save_result(module, result)
            store_result_from_worker(module, result)
            print(f"[WORKER] 模組 {module} 計算完成，結果：{result}")
            return jsonify({"status": "ok", "result": result})

    except Exception as e:
        print(f"[WORKER] 錯誤：{e}")
        return jsonify({"status": "error", "message": str(e)}), 500


def compute_trace_block(inputs):
    import dask.array as da
    i = inputs["block_row"]
    j = inputs["block_col"]
    chunk = inputs["chunk_size"]
    base = inputs["base_size"]

    A = da.random.random((chunk, base), chunks=(chunk, chunk))
    B = da.random.random((base, chunk), chunks=(chunk, chunk))
    C = da.dot(A, B)
    trace_block = da.trace(C).compute()
    return trace_block

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5001
    app.run(host="0.0.0.0", port=port)