# 從各模組文件導入模組計算函數
from modules.module1 import module1_function
from modules.module2 import module2_function
from modules.module3 import module3_function
from modules.module4 import module4_function
from modules.module5 import module5_function
from modules.module6 import module6_function
from modules.module7 import module7_function

# 用戶輸入全局變數
user_inputs = {
    "num1": 0,
    "num2": 0,
    "num3": 0
}

# 創建一個包含所有模組配置的函數，接收用戶輸入
def get_modules_config(user_inputs):
    """獲取模組配置，加入用戶輸入"""

    def module1_wrapper(inputs):
        return module1_function(inputs, user_inputs)

    # 回傳 dict（使用模組 id 當 key）
    return {
        "module1": {
            "id": 1,
            "requires": [],
            "outputs": ["answer1", "answer2", "answer3"],
            "generator": module1_wrapper
        },
        "module2": {
            "id": 2,
            "requires": ["answer1"],
            "outputs": ["answer4"],
            "generator": module2_function
        },
        "module3": {
            "id": 3,
            "requires": ["answer1", "answer2"],
            "outputs": ["answer5"],
            "generator": module3_function
        },
        "module4": {
            "id": 4,
            "requires": ["answer2", "answer3"],
            "outputs": ["answer6"],
            "generator": module4_function
        },
        "module5": {
            "id": 5,
            "requires": ["answer1", "answer4"],
            "outputs": ["answer7"],
            "generator": module5_function
        },
        "module6": {
            "id": 6,
            "requires": ["answer2", "answer3", "answer6"],
            "outputs": ["answer8"],
            "generator": module6_function
        },
        "module7": {
            "id": 7,
            "requires": ["answer7", "answer8"],
            "outputs": ["final_result"],
            "generator": module7_function
        }
    }