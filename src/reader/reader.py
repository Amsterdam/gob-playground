from pandas import pandas

def read_data(input_dir):
    stadsdeel = {}
    read_stadsdeel_data(input_dir, stadsdeel)
    read_stadsdeel_geometrie(input_dir, stadsdeel)
    return list(stadsdeel.values())

def read_stadsdeel_data(input_dir, stadsdeel):
    print("Read Stadsdeel Data")
    names =    ["ID",   "SDL_ID",  "GME_ID", "CODE",  "GBD_ID", "GBD_SUPERID", "NAAM",   "INGANGSDATUM_CYCLUS", "EINDDATUM_CYCLUS", "DOCUMENTNUMMER_MUTATIE", "DOCUMENTDATUM_MUTATIE", "MUTATIEDATUM", "ONTSTAANSDATUM", "IND_VERVALLEN"]
    colspecs = [[0,15], [15,30],   [30,45],  [45,50], [50, 61], [61, 73],      [73,114], [114,134],             [134, 154],         [154, 255],               [255, 277],              [277, 297],     [297, 317],       [317, 330]]
    data = pandas.read_fwf(f"{input_dir}/stadsdeel_data.txt", colspecs=colspecs, names=names, dtype='str')

    for index, row in data.iterrows():
        if index > 0:
            id = row["ID"]
            stadsdeel[id] = stadsdeel.get(id, {})
            for name in names:
                # print("name:", name, "value:", row[name])
                stadsdeel[id][name] = row[name]

def read_stadsdeel_geometrie(input_dir, stadsdeel):
    print("Read Stadsdeel Geometrie")
    names =    ["ID",   "SDC_ID",  "GEOMETRIE"]
    colspecs = [[0,15], [15,30],   [30,9999]]
    data = pandas.read_fwf(f"{input_dir}/stadsdeel_geometrie.txt", colspecs=colspecs, names=names, dtype='str')

    for index, row in data.iterrows():
        if index > 0:
            id = row["SDC_ID"]
            stadsdeel[id] = stadsdeel.get(id, {})
            for name in names:
                # print("name:", name, "value:", row[name])
                stadsdeel[id][name] = row[name]
