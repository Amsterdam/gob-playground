def process_data(cur_data, mutations):

    id_field = "_source_id"
    timestamp = mutations["timestamp"]

    cur_values = { data[id_field]: data for data in cur_data["contents"] if data["_source"] == mutations["source"] }

    mutation_list = mutations["mutations"]
    for mutation in mutation_list:
        contents = mutation["contents"]

        if mutation["action"] == "ADD":
            _set_dates(contents, { "date_created": timestamp })
            cur_data["contents"].append(contents)
        elif mutation["action"] == "MODIFIED":
            id = contents[id_field]
            cur_value = cur_values[id]
            for modification in contents["modifications"]:
                cur_value[modification["key"]] = modification["new_value"]
            _set_dates(cur_value, { "date_last_modified": timestamp })
        else:
            # CONFIRMED or DELETED
            id = contents
            cur_value = cur_values[id]
            if mutation["action"] == "DELETED":
                _set_dates(cur_value, { "date_deleted": timestamp })
            else:
                # CONFIRMED
                _set_dates(cur_value, { "date_last_confirmed": timestamp })

    print(f"Aantal mutaties: {len(mutation_list)}")
    for action in ["ADD", "MODIFIED", "CONFIRMED", "DELETED"]:
        actions = [mutation for mutation in mutation_list if mutation['action'] == action]
        if len(actions) > 0:
            print(f"- {action}: {len(actions)}")

    return cur_data


def _set_dates(item, dates):
    item_dates = ["date_created", "date_last_modified", "date_deleted", "date_last_confirmed"]
    for item_date in item_dates:
        name = f"_{item_date}"
        item[name] = dates.get(item_date, item.get(name))
