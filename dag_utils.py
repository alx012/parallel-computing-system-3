import networkx as nx
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor, wait
from db_utils import fetch_answers, save_result

from dask.distributed import Client, wait
from concurrent.futures import as_completed
import sqlite3
import importlib

def build_dag(modules):
    """建構 DAG 並做拓撲排序（支援 dict）"""
    dag = nx.DiGraph()
    answer_to_module = {}

    for module_id, module in modules.items():
        dag.add_node(module_id)
        for out in module["outputs"]:
            answer_to_module[out] = module_id

    for module_id, module in modules.items():
        for req in module["requires"]:
            if req in answer_to_module:
                dag.add_edge(answer_to_module[req], module_id)

    return dag, list(nx.topological_sort(dag))

def draw_dag(modules):
    """DAG 圖形繪製 - 簡單版本但顯示平行結構"""
    dag, sorted_nodes = build_dag(modules)
    
    # 構建層級信息
    levels = {}
    max_level = 0
    
    # 為每個節點分配層級（基於拓撲排序）
    level_map = {}
    for node in sorted_nodes:
        # 獲取所有前驅節點
        predecessors = list(dag.predecessors(node))
        if not predecessors:  # 如果沒有前驅，層級為0
            level_map[node] = 0
        else:
            # 層級為最大前驅層級+1
            level_map[node] = max([level_map[p] for p in predecessors]) + 1
        
        # 將節點添加到對應層級
        if level_map[node] not in levels:
            levels[level_map[node]] = []
        levels[level_map[node]].append(node)
        
        # 更新最大層級
        if level_map[node] > max_level:
            max_level = level_map[node]
    
    # 設置圖形大小
    plt.figure(figsize=(10, 6))
    
    # 使用自定義布局，基於層級
    pos = {}
    for level, nodes in levels.items():
        # 該層有多少個節點
        nodes_count = len(nodes)
        # 在該層均勻分布節點
        for i, node in enumerate(nodes):
            # X坐標基於層級，Y坐標在層中均勻分布
            x = level
            y = i / max(1, nodes_count - 1) if nodes_count > 1 else 0.5
            pos[node] = (x, y)
    
    # 繪製節點和邊
    nx.draw(dag, pos, with_labels=True, node_color="skyblue", node_size=2000, 
            font_size=10, font_weight="bold", arrows=True)
    
    # 添加平行執行信息
    for level, nodes in levels.items():
        if len(nodes) > 1:  # 有多個節點的層可以平行執行
            # 計算該層的平均Y坐標
            y_avg = sum(pos[node][1] for node in nodes) / len(nodes)
            # 添加文本
            plt.text(level, -0.1, f"平行層 {level}: 模組 {', '.join(map(str, nodes))}", 
                    horizontalalignment='center', 
                    bbox=dict(facecolor='lightgreen', alpha=0.7, edgecolor='green'))
    
    plt.title("模組依賴圖（DAG）- 平行架構", fontsize=14)
    plt.axis('off')  # 隱藏坐標軸
    plt.tight_layout()
    plt.show()

def run_module(module, inputs):
    """執行模組邏輯"""
    print(f"模組 {module['id']} 開始執行，需要: {module['requires']}")
    # 呼叫對應的模組函數
    result = module["generator"](inputs)
    print(f"模組 {module['id']} 完成，輸出: {result}")
    save_result(module["id"], result)


def execute_modules(modules: dict):
    """依據模組依賴關係執行所有模組（簡化版本）"""
    # 先用拓撲排序確定執行順序
    dag, execution_order = build_dag(modules)
    
    print(f"執行順序: {execution_order}")
    
    # 依照順序執行每個模組
    for module_id in execution_order:
        module = modules[module_id]
        
        # 準備輸入數據
        inputs = {}
        
        # 如果模組需要其他答案，從資料庫中獲取
        if module["requires"]:
            inputs = fetch_answers(module["requires"])
        
        # 執行模組
        print(f"\n正在執行模組 {module['id']}...")
        result = module["generator"](inputs)
        
        # 保存結果
        save_result(module["id"], result)
        print(f"模組 {module['id']} 執行完成")
    
    print("\n所有模組執行完畢！")