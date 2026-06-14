import requests
import csv
import pprint
import json

SEARCH_URL = "https://collectionapi.metmuseum.org/public/collection/v1/search"
OBJECT_URL = "https://collectionapi.metmuseum.org/public/collection/v1/objects/{}"
params = {"q": "Japanese woodblock print", "hasImages": "true"}


def get_potential_objects(SEARCH_URL:str, params:dict) -> list:
    search_response = requests.get(SEARCH_URL, params=params, timeout=20)
    search_response.raise_for_status()
    object_ids = search_response.json().get("objectIDs", [])
    return object_ids


def get_item(object_url: str, object_id:str):
    item = None
    try:
        response = requests.get(object_url.format(object_id), timeout=20)
        response.raise_for_status()
        item = response.json()

    except requests.exceptions.HTTPError as err:
        print(f"Skipping object {object_id}: HTTP error: {err}")

    except requests.exceptions.RequestException as err:
        print(f"Skipping object {object_id}: request failed: {err}")

    except ValueError as err:
        print(f"Skipping object {object_id}: invalid JSON: {err}")

    return item


def add_list_from_dictionary(record, requested_object: dict, list_field_name: str, embedded_dict_field_name:str) -> list:
    try:
        my_list = [fields[embedded_dict_field_name] for fields in requested_object.get(list_field_name)]
    except TypeError:
        my_list = []
    record[list_field_name] = my_list
    return record


def write_dictionary_to_csv(filename:str, records:list) -> None:
    with open(f"{filename}.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)

def write_dictionary_to_json(filename:str, records:list) -> None:
    with open(f"{filename}.json", "w", encoding="utf-8") as f:
        json.dump(records, f)


def main():
    max_requests = 100
    max_items = 50

    GET_SAMPLE = True
    sample = {}
    records = []

    output_file_name = "met_japanese_woodblock_prints"

    fields_to_fetch = (
    "objectID",
    "accessionNumber",
    "accessionYear",
    "title",
    "artistDisplayName",
    # "artistPrefix",
    "artistDisplayBio",
    "artistSuffix",
    "artistAlphaSort",
    "artistNationality",
    "artistBeginDate",
    "artistEndDate",
    "artistGender",
    "culture",
    # "tags",
    "objectDate",
    "medium",
    "dimensions",
    "department",
    "classification",
    "primaryImageSmall",
    "objectURL",
    )

    object_ids = get_potential_objects(SEARCH_URL, params)
    for object_id in object_ids[:max_requests]:
        requested_object = get_item(OBJECT_URL, object_id)

        if (
        requested_object
        and requested_object.get("isPublicDomain")
        # and item.get("primaryImageSmall")
        and requested_object.get("culture") == "Japan"
        and "woodblock" in requested_object.get("medium", "").lower()
        ):

            if GET_SAMPLE:
                sample = requested_object
                GET_SAMPLE = False

            record = {field : requested_object.get(field) for field in fields_to_fetch}
            record = add_list_from_dictionary(record, requested_object, "tags", "term")

            records.append(record)
            print(f">>item# {len(records)}: id = {object_id}")

            if len(records) >= max_items:
                break

    if sample:
        write_dictionary_to_json("sample_record", sample)
    write_dictionary_to_json(output_file_name, records)
    write_dictionary_to_csv(output_file_name, records)

    print(f"Saved {len(records)} public-domain image records.")



if __name__ == "__main__":
    main()
