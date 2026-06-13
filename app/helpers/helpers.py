import json


def save_json(json_data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4, ensure_ascii=False)


def extract_sources(sources):
    text = "Sources: "
    for source in sources:
        text += f'File: {source["filename"]} Page: {source["page_number"]} '
    return text