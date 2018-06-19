from reader import read_data
from processor import process_data
from writer import write_data

def main(mutations_file, data_dir):
    mutations = read_data(mutations_file)
    entity = mutations["entity"]

    cur_file=f"{data_dir}/{entity.lower()}.json"
    cur_data = read_data(cur_file)

    new_data = process_data(cur_data=cur_data, mutations=mutations)

    out_file = cur_file
    write_data(new_data, out_file)

main(mutations_file="../processor/output_data/mutations.json", data_dir="./data")
