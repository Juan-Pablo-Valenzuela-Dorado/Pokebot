import os

COUNTER_FILE = "id_counter.txt"

def load_counter():
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, "r") as f:
            return int(f.read().strip())
    return 0

def save_counter(value):
    with open(COUNTER_FILE, "w") as f:
        f.write(str(value))

global_id = load_counter()

def get_new_id():
    global global_id
    global_id += 1
    save_counter(global_id)
    return global_id
