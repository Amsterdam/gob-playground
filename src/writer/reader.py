import json

def read_data(filename):
    print(f"Read Data {filename}")
    with open(filename) as f:
        data = json.loads(f.read())
    return data
