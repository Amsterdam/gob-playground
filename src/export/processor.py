from datetime import datetime

def process_data(cur_data):
    labels = [
        "sleutelVerzendend",
        "Stadsdeelcode",
        "Stadsdeelnaam",
        "Brondocumentverwijzing",
        "Brondocumentdatum",
        "Geometrie",
        "Mutatie-gebruiker",
        "Indicatie-vervallen",
        "TijdvakGeldigheid/begindatumTijdvakGeldigheid",
        "TijdvakGeldigheid/einddatumTijdvakGeldigheid",
        "SDLGME/GME/sleutelVerzendend",
        "SDLGME/GME/Gemeentecode",
        "SDLGME/TijdvakRelatie/begindatumRelatie",
        "SDLGME/TijdvakRelatie/einddatumRelatie"
    ]

    lines = []
    for s in cur_data["contents"]:
        # Take all current and not-deleted stadsdelen
        if s["datum_einde_geldigheid"] is None and \
           s["_date_deleted"] is None:
            line = [
                s["stadsdeelidentificatie"],                # sleutelVerzendend
                s["code"],                                  # Stadsdeelcode
                s["naam"],                                  # Stadsdeelnaam
                s["documentnummer_mutatie"],                # Brondocumentverwijzing
                _to_date(s["documentatiedatum_mutatie"]),   # Brondocumentdatum
                "",                                         # Geometrie
                "?",                                        # Mutatie-gebruiker
                "N" if s["_date_deleted"] is None else "J", # Indicatie-vervallen
                _to_date(s["datum_begin_geldigheid"]),      # TijdvakGeldigheid/begindatumTijdvakGeldigheid
                _to_date(s["datum_einde_geldigheid"]),      # TijdvakGeldigheid/einddatumTijdvakGeldigheid
                s["ligt_in"],                               # SDLGME/GME/sleutelVerzendend
                "",                                         # SDLGME/GME/Gemeentecode
                "",                                         # SDLGME/TijdvakRelatie/begindatumRelatie
            "",                                             # SDLGME/TijdvakRelatie/einddatumRelatie
            ]
            lines.append(line)

    print(f"Exported stadsdelen: {len(lines)}")
    return labels, lines


def _to_date(date_str):
    if date_str is None:
        return ""
    else:
        return datetime.strptime(date_str, "%d-%m-%Y").strftime("%Y%m%d")
