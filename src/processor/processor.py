import re
from datetime import datetime

def process_data(cur_data, new_data):
    print("Process Data")

    if new_data["version"] != cur_data["version"]:
        new_data = migrate(new_data, new_data_version=new_data["version"], cur_data_version=cur_data["version"])

    id_field = "_source_id"

    # Get current values for this data source
    cur_values = { data[id_field]: data for data in cur_data["contents"] if data["_source"] == new_data["source"]}
    new_values = { data[id_field]: data for data in new_data["contents"] }

    cur_ids = [ value for value in cur_values.keys() ]
    new_ids = [ value for value in new_values.keys() ]

    mutations = []

    for id in set(cur_ids + new_ids):
        new_value = new_values.get(id)
        cur_value = cur_values.get(id)

        if cur_value is None:
            mutation = {
                "action": "ADD",
                "contents": new_value
            }
        elif new_value is None:
            if cur_value["_date_deleted"] is None:
                mutation = {
                    "action": "DELETED",
                    "contents": id
                }
            else:
                # Do not delete twice
                continue
        else:
            # Modified or Confirmed entry
            modifications = []
            for attr, value in cur_value.items():
                if not re.search('^_', attr) and new_value.get(attr) != cur_value.get(attr):
                    modifications.append({
                        "key": attr,
                        "new_value": new_value.get(attr),
                        "old_value": cur_value.get(attr)
                    })
            if len(modifications) == 0:
                mutation = {
                    "action": "CONFIRMED",
                    "contents": id
                }
            else:
                mutation = {
                    "action": "MODIFIED",
                    "contents": {
                        "_source_id": id,
                        "modifications": modifications
                    }
                }

        mutations.append(mutation)

    print(f"Aantal mutaties: {len(mutations)}")
    for action in ["ADD", "MODIFIED", "CONFIRMED", "DELETED"]:
        actions = [mutation for mutation in mutations if mutation['action'] == action]
        if len(actions) > 0:
            print(f"- {action}: {len(actions)}")

    return {
        "entity": new_data["entity"],
        "timestamp": datetime.now().isoformat(),
        "source": new_data["source"],
        "mutations": mutations,
    }

def migrate(data, new_data_version, cur_data_version):
    # Left empty for now
    print(f"Migrate from version {new_data_version} to current version {cur_data_version}")
    return data