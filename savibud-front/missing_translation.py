import os
import json


translations_path = "public/i18n"
reference = "en"


def json_compare(ref:dict, lang_json:dict, lang:str, prefix:str = ""):
    result = lang_json.copy()
    for key, value in ref.items():
        if type(ref[key]) == dict:
            result[key] = json_compare(ref[key], lang_json.get(key,{}), lang, prefix=f"{prefix}{key}.")

        elif key not in lang_json.keys():
            print(f"Missing key {prefix}{key}, can you translate the following in {lang}:")
            print(f"{value}")
            result[key] = input()
    return result

files = os.listdir(translations_path)

with open(f'{translations_path}/{reference}.json') as f:
    ref_dict = json.load(f)

for file in files:
    if file == f"{reference}.json":
        continue
    with open(f'{translations_path}/{file}') as f:
        file_dict = json.load(f)
    lang = file.split('/')[-1].split(".")[0]
    result = json_compare(ref_dict, file_dict, lang)
    if result != lang:
        with open(f'{translations_path}/{file}', 'w') as f:
            json.dump(result, f, indent=4)
    else:
        print(f"{lang} up to date!")
