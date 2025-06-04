# ============================================
# module_runner.py
# ============================================
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
        try:
            fetched = fetch_answers(module["requires"])
            inputs.update(fetched)
        except Exception as e:
            print(f"⚠️ 警告：無法獲取依賴資料 {module['requires']}，錯誤：{e}")
            # 繼續執行，使用現有的 inputs

    print(f"➡️ 執行模組 {module_name}，輸入：{inputs}")
    
    try:
        result = module["generator"](inputs)
        print(f"✅ 模組 {module_name} 執行完成，輸出：{result}")
        return result
    except Exception as e:
        print(f"❌ 模組 {module_name} 執行失敗：{e}")
        import traceback
        traceback.print_exc()
        raise
