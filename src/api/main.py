from reader import read_data
from processor import process_data
from writer import write_data

def main(input_dir, output_dir, entity):
    cur_file= f"{input_dir}/{entity.lower()}.json"
    cur_data = read_data(cur_file)

    new_data = process_data(cur_data=cur_data)

    out_file= f"{output_dir}/{entity.lower()}.json"
    write_data(new_data, out_file)

main(input_dir="../writer/data", output_dir="./output_data", entity="Stadsdeel")
