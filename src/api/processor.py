def process_data(cur_data):
    for item in cur_data["contents"]:
        del item["_source"]
        del item["_source_id"]

    print(f"Aantal entiteiten: {len(cur_data['contents'])}")
    return cur_data
