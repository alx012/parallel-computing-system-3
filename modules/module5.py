import math
import numpy as np

def module5_function(inputs):
    """
    模組5：模擬大型矩陣運算，使用 answer1 和 answer4 影響矩陣結構
    
    Args:
        inputs: 包含 answer1 和 answer4 的字典
        
    Returns:
        包含 answer7 的字典
    """
    print("\n===== 模組5：執行大型矩陣運算中 =====")
    answer1 = inputs["answer1"]
    answer4 = inputs["answer4"]

    # 處理可能的負值
    if answer4 < 0:
        print("警告：answer4 為負，使用其絕對值進行矩陣初始化")
        answer4 = abs(answer4)

    # 決定矩陣大小（受 answer1 和 answer4 影響）
    base_size = 15000 + int((answer1 + answer4) % 50)  # 大約在 100~150 之間
    print(f"模擬矩陣大小為 {base_size} x {base_size}，開始乘法計算...")

    # 建立隨機矩陣
    A = np.random.rand(base_size, base_size)
    B = np.random.rand(base_size, base_size)

    # 矩陣乘法
    C = np.dot(A, B)

    # 簡單取結果：回傳主對角線 trace 作為數值代表
    trace = float(np.trace(C))

    print(f"模組5計算完成：answer7 = 矩陣乘積主對角線總和 ≈ {trace:.4f}")
    
    return {
        "answer7": trace
    }