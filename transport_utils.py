# transport_utils.py（簡化版：socket 例子）
import socket
import pickle

def send_task_to_worker(ip, module_name, data):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ip, 8000))
        msg = pickle.dumps((module_name, data))
        s.sendall(msg)

def listen_for_task():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 8000))
        s.listen()
        conn, _ = s.accept()
        with conn:
            data = b""
            while chunk := conn.recv(4096):
                data += chunk
            return pickle.loads(data)

def send_result_to_master(module_name, result):
    # 類似 send_task_to_worker 發回 master（可固定 IP）
    pass

def receive_result(module_name):
    # 等待對應 module 結果回傳
    pass
