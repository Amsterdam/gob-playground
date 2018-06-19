from reader import read_data
from processor import process_data
from writer import write_data

def main(input_dir, output_file):
    raw_stadsdelen = read_data(input_dir=input_dir)
    stadsdelen = process_data(raw_stadsdelen)
    write_data(stadsdelen, output_file=output_file)

main(
    input_dir="./input_data",
    output_file="./output_data/stadsdeel.json")
