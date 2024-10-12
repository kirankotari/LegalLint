import os
import re
import sys
import json
import toml
import yaml
import itertools


def get_lines(fpath):
    if not os.path.isfile(fpath):
        print(f"Error: The file '{fpath}' was not found.")
        return []
    try:
        with open(fpath, 'r') as file:
            return [line.strip() for line in file.readlines()]
    except IOError:
        print(f"Error: An error occurred while reading the file '{fpath}'.")
    return []

def get_basedir():
    return os.path.split(os.path.abspath(sys.modules['legallint'].__file__))[0]

def check_subclass(subclass, cls):
    return False if subclass is cls else issubclass(subclass, cls)

def get_pwd():
    return os.getcwd()

def flatten_set(data): # dict<key:list-of-values>
    return set(itertools.chain(*data.values()))

def get_matching_keys(substring, keys):
    return [key for key in keys if re.search(substring, key)]

def read_json(fpath):
    if not os.path.isfile(fpath):
        return {}
    with open(fpath, 'r') as f:
        return json.load(f)

def write_json(fpath, data):
    with open(fpath, 'w') as f:
        json.dump(data, f, indent=2, sort_keys=True)

def read_toml(fpath):
    if not os.path.isfile(fpath):
        return {}
    with open(fpath, 'r') as f:
        return toml.load(f)
    
def read_yaml(fpath):
    if not os.path.isfile(fpath):
        return {}
    with open(fpath, 'r') as f:
        return yaml.safe_load(f)

def exit(code=0):
    sys.exit(code)
