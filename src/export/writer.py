from datetime import datetime
import csv

CSV_DELIMITER = ";"

def write_data(labels, lines, output_dir):
    print('Write data')
    now = datetime.now().strftime("%Y%d%m")
    out_file= f"{output_dir}/SDL_{now}_N_{now}_{now}.UVA2"

    with open(out_file, "w", newline='') as f:
        f.write(f"VAN;{now}\n")
        f.write(f"TM;{now}\n")
        f.write("HISTORISCHE_CYCLI;N\n")
        for index, label in enumerate(labels):
            if index > 0:
                f.write(CSV_DELIMITER)
            f.write(label)
        linewriter = csv.writer(f, delimiter=CSV_DELIMITER, quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for line in lines:
            linewriter.writerow(line)
