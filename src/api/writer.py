import json

def write_data(data, out_file):
    print('Write data')
    with open(out_file, "w") as f:
        json.dump(data, f, indent=4)
