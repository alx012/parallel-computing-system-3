from modules_config import get_modules_config
from db_utils import fetch_answers

def run_module(module_name, inputs, user_inputs=None):
    """執行指定模組（含處理依賴），user_inputs 為用戶端傳來的原始輸入資料"""
    user_inputs = user_inputs or {}
    modules = get_modules_config(user_inputs)

    if module_name not in modules:
        raise ValueError(f"❌ 找不到模組：{module_name}")

    module = modules[module_name]

    # 如果模組有依賴，需要補 fetch 值
    if module["requires"]:
        fetched = fetch_answers(module["requires"])
        inputs.update(fetched)

    print(f"➡️ 執行模組 {module_name}，輸入：{inputs}")
    result = module["generator"](inputs)
    print(f"✅ 模組 {module_name} 執行完成，輸出：{result}")
    return result