import json

def write_data(mutations, outfile):
    print('Write data')
    with open(outfile, "w") as f:
        json.dump(mutations, f, indent=4)
