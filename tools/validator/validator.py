from pathlib import Path
from typing import Dict

import yamale
import os
import validators.settings as settings
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap
from yamale.validators import DefaultValidators


def _get_lc_dict_helper(data: CommentedMap, dict_key_line: Dict[str, int], parentkey: str = "") -> Dict[str, int]:
    """
    Recursive helper function to fetch the line infos of each keys in the config yaml file.

    Built to be called inside of `_get_lc_dict`.
    """
    sep = "."  # Don't modify, it is to match the "keys" return in the errors of the yamale lib.
    keys_indexes = None

    try:
        if len(data) > 0:
            keys_indexes = range(len(data))
    except TypeError:
        pass
    try:
        keys = data.keys()
        keys_indexes = keys
    except AttributeError:
        pass

    if keys_indexes is None:
        return dict_key_line  # return condition from recursion

    for key in keys_indexes:
        if parentkey != "":
            keyref = parentkey + sep + str(key)
        else:
            keyref = str(key)
        try:
            lnum = data.lc.data[key][0] + 1
            if keyref in dict_key_line:
                print(
                    f"WARNING : key '{keyref}' is NOT UNIQUE, at lines {dict_key_line[keyref]:>4} and {lnum:>4}."
                    f" (overwriting)."
                )
            dict_key_line[keyref] = lnum
            # print(f"line {lnum:<3} : {keyref}")
            _get_lc_dict_helper(data[key], dict_key_line, keyref)  # recursion
        except AttributeError:
            pass

    return dict_key_line


def _get_lc_dict(path: Path) -> Dict[str, int]:
    """
    Helper function to trace back the line number in the yaml file for each keys.

    Built to be called inside of `validate`.

    Parameters
    ----------
    path : Path
        Path to the config yaml file (not the schema).

    Returns
    -------
    Dict[str, int]
        Maps the keys to their line number, the line counter (lc).
        This dictionary is only 1 level and the keys corresponds to the ones report by the yamale lib.
    """
    dict_key_line: Dict[str, int] = {}
    with YAML(typ="rt") as yaml:
        for data in yaml.load_all(path):
            dict_key_line = _get_lc_dict_helper(data, dict_key_line)
    return dict_key_line


def validate(path_schema: Path, path_data: Path):
    """
    Validates the config yaml file according to the schema yaml file.

    Will be silent if good and will exit the program if there is an error,
    and will output an detailed error message to fix the config file.

    Parameters
    ----------
    path_schema : Path
        Path to the schema yaml file.
    path_data : Path
        Path to the config yaml file.
    """
    validators = DefaultValidators.copy()  # This is a dictionary
    validators[settings.Settings.tag]=settings.Settings
    # Create a schema object
    schema = yamale.make_schema(path=path_schema, parser="ruamel",validators=validators)

    # Create a Data object
    config = yamale.make_data(path=path_data, parser="ruamel")
    # Validate data against the schema. Throws a ValueError if data is invalid.
    try:
        yamale.validate(schema, config)
        print("Blueprint Yaml Validation success!👍")
    except yamale.YamaleError as e:
        errmsg = "Blueprint Yaml Validation failed!\n"
        lc = _get_lc_dict(path_data)
        for result in e.results:
            title1 = "Schema"
            title2 = "Config"
            sep = f"{'-'*40}\n"
            errmsg += f"{title1:<10} : {result.schema}\n{title2:<10} : {result.data}\n{sep}"
            for error in result.errors:
                keyerr = error.split(":", 1)
                keypath = keyerr[0]
                err = keyerr[1]
                l_num = lc.get(keypath, "?")
                errmsg += f"* line {l_num:>4}:  {keypath:<40} : {err}\n"
            errmsg += f"{sep}"

        print(errmsg)
        exit(1)

class Validator():
    def __init__(self,filename):
        filepath = os.path.dirname(__file__)
        path_schema = filepath.rsplit("/",2)[0]+'/schema/schema.yaml'
        path_data = filename

        validate(path_schema=path_schema, path_data=path_data)




