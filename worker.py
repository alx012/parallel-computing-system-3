# worker.py
from transport_utils import listen_for_task, send_result_to_master
from module_runner import run_module
from db_utils import save_result

def main():
    while True:
        module_name, inputs = listen_for_task()
        result = run_module(module_name, inputs)
        save_result(module_name, result)
        send_result_to_master(module_name, result)

if __name__ == "__main__":
    main()
    