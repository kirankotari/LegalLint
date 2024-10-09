"""
LegalLint python locates 3rd party libraries used and returns name and metadata
"""

import os
import re
from importlib.metadata import distributions

from legallint.plugin import Plugin
from legallint.utils import get_pwd, get_lines, get_matching_keys, read_toml, flatten_set


class PythonPlugin(Plugin):
    def get_name(self):
        return "python"

    def run(self):
        Toml.get_dependencies()
        deps = Toml.to_set()

        # if not deps:
        #     Reqs.get_dependencies()
        #     deps = Reqs.to_set()

        # print(f"python deps found {deps}")

        Expand.map_dependencies_by_package()
        deps = Expand.get_dependencies(deps)
        deps = deps - Expand.not_installed
        # print(f"python deps expanded {deps}")
        return

class Requirements: #  create a class requirements.txt , dev-req.txt , req-dev.txt root direc scan find txt files / req / read that file store the data[] in a var list 
    basedir = os.getcwd()  # Current working directory
    files = ['requirements.txt', 'dev-requirements.txt']  # List of potential requirements files ((dep, req,))
    dependencies = {}

    @classmethod
    def get_requirements_file(cls):
        """
        Locate the requirements file (requirements.txt or dev-requirements.txt) in the base directory.
        Returns the file path if found, otherwise returns None.
        """
        for filename in cls.files:
            fpath = os.path.join(cls.basedir, filename)
            if os.path.isfile(fpath):
                return fpath
        return None
    # we should get list files 

    @classmethod
    def get_dependencies(cls, fpath=None):
        """
        Read the requirements file and extract dependencies.
        Optionally take a specific file path.
        """
        if fpath is None:
            fpath = cls.get_requirements_file()
        
        if fpath is None:
            print("No requirements file found in the base directory.")
            return cls.dependencies

        try:
            with open(fpath, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line and not line.startswith('#'):  # Ignore empty lines and comments
                        # Handle version specifications (e.g., package==version or package>=version)
                        package = line.split(' ')[0].split('==')[0].split('>=')[0]
                        cls.dependencies[package] = line  # Store full line for further use
        except Exception as e:
            print(f"Error reading requirements file: {e}")

        return cls.dependencies
    # we need only keys and it supposed to be a set not dict

    @classmethod
    def to_set(cls, deps=None):
        """
        Convert the collected dependencies into a set for uniqueness.
        """
        # {‘reqs’: [‘pytest’, ‘pandas’], ‘dev-requirements’: [‘mkdocs’]}
        return set(cls.dependencies.keys()) if deps is None else set(deps)

class Expand:
    dep_map = {}
    visited, not_installed = set(), set()

    dep_pattern = re.compile(r"([a-zA-Z0-9\-_]+)")

    @classmethod
    def get_dependencies(cls, pkgs_set):
        """
        Recursively get all dependencies (including dependencies of dependencies).
        """
        dependencies = set()

        for pkg_name in pkgs_set:
            if pkg_name in cls.visited:
                continue
            cls.visited.add(pkg_name)

            if pkg_name not in cls.dep_map:
                cls.not_installed.add(pkg_name)
                continue

            direct_deps = cls.dep_map.get(pkg_name, set())
            dependencies |= direct_deps

            # Recursively find dependencies for each direct dependency
            for dep in direct_deps:
                dependencies |= cls.get_dependencies({dep})

        dependencies |= pkgs_set
        return dependencies

    @classmethod
    def map_dependencies_by_package(cls):
        """
        Maps each package to its direct dependencies.
        """

        for dist in distributions():
            dist_name = dist.metadata.get('Name')
            if dist.requires:
                cls.dep_map[dist_name] = {cls.dep_pattern.match(dep).group(1) for dep in dist.requires}
            else:
                cls.dep_map[dist_name] = set()  # No dependencies



class Toml:
    basedir = get_pwd()
    file = 'pyproject.toml'
    dependencies = {}

    @classmethod
    def get_dependencies(cls, fpath=None):
        if not fpath:
            fpath = f"{cls.basedir}/{cls.file}"
        config = read_toml(fpath)

        # Poetry dependencies
        if 'tool' in config and 'poetry' in config['tool']:
            poetry = config['tool']['poetry']
            for matched_key in get_matching_keys('dependencies', list(poetry.keys())):
                # print(poetry[matched_key])
                if 'python' in poetry[matched_key]:
                    del poetry[matched_key]['python']
                cls.dependencies[matched_key] = list(poetry[matched_key].keys())
            if 'group' in poetry:
                for group, group_deps in poetry['group'].items():
                    if 'dependencies' in group_deps:
                        # print(group_deps['dependencies'])
                        cls.dependencies[group] = list(group_deps['dependencies'].keys())

        # Setuptools dependencies (if present)
        if 'project' in config and 'dependencies' in config['project']:
            cls.dependencies['setuptools'] = [
                each.split('>=')[0] if '>=' in each else each.split('==')[0] if '==' in each else each
                for each in config['project']['dependencies']
            ]
        return cls.dependencies
    
    @classmethod
    def to_set(cls, deps=None):
        return flatten_set(cls.dependencies) if not deps and cls.dependencies else set()


if __name__ == "__main__":
#     Toml.get_dependencies()
#     deps = Toml.to_set()
#     print(deps)
#     deps = Expand.get_dependencies(deps)
#     print(deps)
#    # Requirement testing
    fpath=  Requirements.get_requirements_file()
    if fpath:
        print(fpath)# it prints 
        deps= Requirements.get_dependencies(fpath=fpath)
        print(deps)


