def module4_function(inputs):
    """
    模組4：使用 answer2 和 answer3 進行模擬最佳化計算
    
    Args:
        inputs: 包含 answer2 和 answer3 的字典
        
    Returns:
        包含 answer6 的字典
    """
    print("\n===== 模組4：模擬複雜計算中 =====")
    answer2 = inputs["answer2"]
    answer3 = inputs["answer3"]
    
    if answer3 == 0:
        print("警告：除數為零，使用預設值 1 以繼續模擬")
        answer3 = 1

    # 定義一個模擬的損失函數（此處只是用 answer2 和 answer3 產生參數）
    a = answer2
    b = answer3

    def loss(x):
        # 假設是一個複雜函數，這裡簡單模擬為二次函數
        return (a * x**2 + b * x + 10)**2 + x * 0.5

    # 模擬暴力搜尋最佳解（耗時計算）
    best_x = None
    best_loss = float("inf")
    for i in range(-50000, 50000):  # 模擬大量迭代
        x = i / 1000.0
        current_loss = loss(x)
        if current_loss < best_loss:
            best_loss = current_loss
            best_x = x

    answer6 = best_x

    print(f"模組4計算完成：answer6 = 最小值位置 x ≈ {answer6:.4f}，對應損失 ≈ {best_loss:.4f}")
    
    return {
        "answer6": answer6
    }