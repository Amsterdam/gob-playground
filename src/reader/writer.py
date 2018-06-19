import json

def write_data(stadsdelen, output_file):
    print('Write data')
    with open(output_file, "w") as f:
        json.dump({
            "entity": "Stadsdeel",
            "version": "1",
            "source": "DIVA",
            "contents": stadsdelen
        }, f, indent=4)
