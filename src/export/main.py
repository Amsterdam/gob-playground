from reader import read_data
from processor import process_data
from writer import write_data

def main(input_dir, output_dir, entity):
    cur_file= f"{input_dir}/{entity.lower()}.json"
    cur_data = read_data(cur_file)

    labels, lines = process_data(cur_data=cur_data)

    write_data(labels, lines, output_dir)

main(input_dir="../api/output_data",
     output_dir="./output_data",
     entity="Stadsdeel")
