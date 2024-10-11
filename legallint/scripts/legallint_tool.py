#!/usr/bin/env python
from __future__ import absolute_import
import sys
import argparse

import legallint
from legallint.plugin import PluginManager
from legallint.license.update import License
from legallint.lint import LegalLint

def main():
    parser = argparse.ArgumentParser(description=legallint.__description__)
    parser.add_argument('--verbose', action='store_true', help="Enable verbose mode")
    parser.add_argument('-v', '--version', action='version', version=f'LegalLint {legallint.__version__}')

    parser.add_argument(
        '-l', '--lang',
        choices=['python', 'node'], # ['python', 'java', 'node'],
        nargs='+',  # one or more options
        help='Select one or more languages from: python' # python, java, node
    )
    parser.add_argument('-u', '--update', action='store_true', help="Enable update mode")
    parser.add_argument('--license', action='store_true', help="Enable license mode")
    # TODO: add CICD option to raise when to fail
    # TODO: allow flag based settings
    args = parser.parse_args()

    if getattr(args, 'license', False):
        License.get()
        return

    plugins = None
    manager = PluginManager() # plugindirs=["path_to_plugins_directory"]
    if not getattr(args, "lang", []):
        plugins = manager.load_plugins()

    for elang in getattr(args, "lang", []) or []:
        # print(f"loading plugins for: {elang}")
        plugins = manager.load_plugins(elang)

    if plugins:
        for lang in plugins:
            deps = manager.run_plugin(lang)
            print("-" * 15)
            print(f"   {plugins[lang].get_name().upper()}")
            print("-" * 15)
            settings = plugins[lang].load_settings()
            LegalLint(deps, settings)
    else:
        print("No plugins found.")


if __name__ == "__main__":
    main()
