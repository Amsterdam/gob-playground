import re
from datetime import datetime

def process_data(raw_stadsdelen):
    print('Process data')
    stadsdelen = []
    for raw_stadsdeel in raw_stadsdelen:
        if raw_stadsdeel["IND_VERVALLEN"] == "N":
            stadsdeel = {
                "stadsdeelidentificatie": raw_stadsdeel["SDL_ID"],
                "naam": raw_stadsdeel["NAAM"],
                "code": raw_stadsdeel["CODE"],
                "datum_begin_geldigheid": _parse_date(raw_stadsdeel["INGANGSDATUM_CYCLUS"]),
                "datum_einde_geldigheid": _parse_date(raw_stadsdeel["EINDDATUM_CYCLUS"]),
                "documentatiedatum_mutatie": _parse_date(raw_stadsdeel["DOCUMENTDATUM_MUTATIE"]),
                "documentnummer_mutatie": raw_stadsdeel["DOCUMENTNUMMER_MUTATIE"],
                "geometrie": _parse_geometrie(raw_stadsdeel["GEOMETRIE"]),
                "geometrie_type": "urn:ogc:def:crs:EPSG::28992",
                "ligt_in": raw_stadsdeel["GME_ID"],

                "_source": "DIVA",
            }
            stadsdeel["_source_id"] =_get_id(stadsdeel)
            stadsdelen.append(stadsdeel)

    print(f"Geimporteerde stadsdelen: {len(stadsdelen)}")
    return stadsdelen


def _get_id(stadsdeel):
    return ".".join([stadsdeel[attr] for attr in ["stadsdeelidentificatie", "datum_begin_geldigheid"]])


def _parse_geometrie(geometrie):
    match = re.search(r'\((((\d+,\d+)(; )?)+)\)', geometrie)
    xys = match.group(1).replace(",", ".").split("; ")
    coords = []
    for i in range(0, len(xys), 2):
        coords.append([float(xys[i]), float(xys[i+1])])
    return coords

def _parse_date(date):
    try:
        match = re.search(r'^\d+-\d+-\d+', date)
        return datetime.strptime(match.group(0), "%d-%m-%Y").strftime("%d-%m-%Y")
    except AttributeError:
        # Missing date
        return None
