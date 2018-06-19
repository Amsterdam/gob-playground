from reader import read_data
from processor import process_data
from writer import write_data

def main(new_file, cur_dir, out_dir):
    new_data = read_data(new_file)
    entity = new_data["entity"]

    cur_file=f"{cur_dir}/{entity.lower()}.json"
    cur_data = read_data(cur_file)

    mutations = process_data(cur_data=cur_data, new_data=new_data)

    out_file = f"{out_dir}/mutations.json"
    write_data(mutations, out_file)

main(
    new_file="../reader/output_data/stadsdeel.json",
    cur_dir="../writer/data",
    out_dir="./output_data")
