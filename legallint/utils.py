import os
import sys

def get_lines(fpath):
    try:
        with open(fpath, 'r') as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        print(f"Error: The file '{fpath}' was not found.")
    except IOError:
        print(f"Error: An error occurred while reading the file '{fpath}'.")
    return []

def get_basedir():
    return os.path.split(os.path.abspath(sys.modules['legallint'].__file__))[0]

def check_subclass(subclass, cls):
    return False if subclass is cls else issubclass(subclass, cls)