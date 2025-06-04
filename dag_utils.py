# dag_utils.py

import networkx as nx
from collections import defaultdict, deque

def build_dag(modules):
    """建構 DAG 並回傳 DAG 與拓撲排序的模組執行順序"""
    dag = nx.DiGraph()
    answer_to_module = {}

    for module_id, module in modules.items():
        dag.add_node(module_id)
        for out in module.get("outputs", []):
            answer_to_module[out] = module_id

    for module_id, module in modules.items():
        for req in module.get("requires", []):
            if req in answer_to_module:
                dag.add_edge(answer_to_module[req], module_id)

    return dag, list(nx.topological_sort(dag))

def get_execution_order(modules_config):
    """傳回模組的執行順序（依據 requires 欄位）"""
    graph = defaultdict(list)
    indegree = defaultdict(int)

    for name, config in modules_config.items():
        for dep in config["requires"]:
            graph[dep].append(name)
            indegree[name] += 1
        indegree.setdefault(name, 0)

    queue = deque([name for name in modules_config if indegree[name] == 0])
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)

    if len(order) != len(modules_config):
        raise Exception("模組之間存在循環依賴，無法進行拓撲排序")

    return order