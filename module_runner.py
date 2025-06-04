# module_runner.py
from modules_config import MODULES

def run_module(module_name, inputs):
    func = MODULES.get(module_name)
    return func(**inputs)
