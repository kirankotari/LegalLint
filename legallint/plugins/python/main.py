"""
LegalLint python locates 3rd party libraries used and returns name and metadata
"""
import re
from importlib.metadata import distributions

from legallint.plugin import Plugin
from legallint.license.update import License
from legallint.utils import get_pwd, get_lines, get_matching_keys, read_toml, flatten_set, exit


class PythonPlugin(Plugin):
    def get_name(self):
        return "python"

    def run(self):
        deps = self._extracted_from(Toml) or self._extracted_from(Requirements)
        if not deps:
            print('no dependencies found in this directory')
            exit()

        # print(f"python deps found {dep}")
        Expand.map_dependencies_by_package()
        deps = Expand.get_dependencies(deps)
        # print(deps)
        # print(Expand.not_installed)
        # print(Expand.dep_map)
        deps = deps - Expand.not_installed
        # print(f"python deps expanded {deps}")
        pylic = PythonLicense()
        return {dep: pylic.get_package_license(dep) for dep in deps}


    def _extracted_from(self, cls):
        cls.get_dependencies()
        return cls.to_set()

    def load_settings(self):
        config = Toml.read()
        if 'licenses' not in config:
            return None
        config = config['licenses']
        allowed_licenses = set(config.get('allowed') or [])
        trigger_error_licenses = set(config.get('trigger_error') or [])
        skip_libraries = set(config.get('skip_libraries') or [])
        return (allowed_licenses, trigger_error_licenses, skip_libraries)


class PythonLicense(License):
    unknown = {'Unknown'}
    def __init__(self):
        super().__init__()
        self.licenses = super().get(is_print=False)
        self.license_set = {key.split('-')[0] for key in self.licenses if len(key.split('-')[0]) > 2}
        # print(self.license_set)

    def set_to_string(self, value_set):
        return next(iter(value_set)) if len(value_set) == 1 else value_set

    def get_package_license(self, pkg_name):
        # TODO: use static data to optimize
        try:
            dist = next(d for d in distributions() if d.metadata['Name'].lower() == pkg_name.lower())

            if license := self._get_license_from_metadata(dist, 'License'):
                # print(f"license from meta License: {license}")
                if len(license) < 3:
                    return license

            if license := self._get_license_from_metadata(dist, 'License-Expression'):
                # print(f"license from meta License-Expression: {license}")
                if len(license) < 3:
                    return license

            if license := self._get_license_from_classifiers(dist):
                # print(f"license from meta Classifiers: {license}")
                if len(license) < 3:
                    return license

            if license := self._get_license_from_files(dist):
                # print(f"license from meta file: {license}")
                if len(license) < 3:
                    return license

            # TODO: need to fetch priority licenses and return the same
            # Need to use re to find them

        except StopIteration:
            print(f"Package '{pkg_name}' not found.")
            return self.unknown

        return self.unknown

    # Helper function to retrieve license from metadata fields
    def _get_license_from_metadata(self, dist, field_name):
        pkg_licenses = set()
        license_content = dist.metadata.get(field_name, '').strip()
        pkg_licenses |= self._validate_license(license_content)
        return pkg_licenses

    # Helper function to check classifiers for licenses
    def _get_license_from_classifiers(self, dist):
        classifiers = dist.metadata.get_all('Classifier', [])
        pkg_licenses = set()
        for line in classifiers:
            if 'license' not in line.lower():
                continue
            pkg_licenses |= self._validate_license(line)
        return pkg_licenses


    # Helper function to check LICENSE files in the distribution
    def _get_license_from_files(self, dist):
        pkg_licenses = set()
        for each in dist.files:
            if 'LICENSE' in each.name.upper():
                license_path = each.locate().as_posix()
                license_content = dist.read_text(license_path)
                pkg_licenses |= self._validate_license(license_content)
        return pkg_licenses
    
    def _validate_license(self, license_content):
        if license := {
            lic for lic in self.licenses if lic in license_content} or {
            lic for lic in self.license_set if lic in license_content}:
            return license
        return set()
    
    # def _get_proprietary_license(self):
    #     """
    #     import re

    #     class LicenseChecker:
            
    #         # Existing method to get license from files
    #         def _get_license_from_files(self, dist):
    #             pkg_licenses = set()
    #             for each in dist.files:
    #                 if 'LICENSE' in each.name.upper():
    #                     license_path = each.locate().as_posix()
    #                     license_content = dist.read_text(license_path)
    #                     pkg_licenses |= self._validate_license(license_content)
                
    #             # If no licenses were found, use regex to detect proprietary license names
    #             if not pkg_licenses:
    #                 proprietary_license = self._find_proprietary_license(license_content)
    #                 if proprietary_license:
    #                     pkg_licenses.add(proprietary_license)
                
    #             return pkg_licenses

    #         # Validate license by checking known licenses and set licenses
    #         def _validate_license(self, license_content):
    #             if license := {
    #                 lic for lic in self.licenses if lic in license_content} or {
    #                 lic for lic in self.license_set if lic in license_content}:
    #                 return license
    #             return set()
            
    #         # New method to find proprietary license using regex
    #         def _find_proprietary_license(self, license_content):
    #             # Define regex patterns for common proprietary license names
    #             proprietary_patterns = [
    #                 r'Proprietary\s+License',  # Example: 'Proprietary License'
    #                 r'Company\s+Name\s+Proprietary\s+License',  # Customize for known companies
    #                 # Add more patterns as needed
    #             ]
                
    #             # Search through the content using the defined patterns
    #             for pattern in proprietary_patterns:
    #                 match = re.search(pattern, license_content, re.IGNORECASE)
    #                 if match:
    #                     return match.group(0)  # Return the first match found
                
    #             return None
    #     """
    #     return set()


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

            if pkg_name.lower() not in cls.dep_map:
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
            dist_name = dist.metadata.get('Name').lower()
            if dist.requires:
                cls.dep_map[dist_name] = {cls.dep_pattern.match(dep).group(1) for dep in dist.requires}
            else:
                cls.dep_map[dist_name] = set()  # No dependencies


class Toml:
    basedir = get_pwd()
    file = 'pyproject.toml'
    config = None
    dependencies = {}

    @classmethod
    def read(cls, fpath=None):
        if not fpath:
            fpath = f"{cls.basedir}/{cls.file}"
        cls.config = read_toml(fpath)
        return cls.config

    @classmethod
    def get_dependencies(cls, fpath=None):
        if not cls.config:
            cls.read(fpath)

        # Poetry dependencies
        if 'tool' in cls.config and 'poetry' in cls.config['tool']:
            poetry = cls.config['tool']['poetry']
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
        if 'project' in cls.config and 'dependencies' in cls.config['project']:
            cls.dependencies['setuptools'] = [
                each.split('>=')[0] if '>=' in each else each.split('==')[0] if '==' in each else each
                for each in cls.config['project']['dependencies']
            ]
        return cls.dependencies

    @classmethod
    def to_set(cls, deps:dict=None):
        return flatten_set(cls.dependencies) if not deps and cls.dependencies else deps

import os

class Requirements:
    basedir = get_pwd()
    dependencies = {}

    @classmethod
    def clean_line(cls, line):
        # Check if the line starts with a comment (ignoring leading whitespace)
        if re.match(r'^\s*#', line):
            return None
        if line := line.split('#')[0].strip():
            # Remove any conditions (e.g., version specifiers like >=, <=, ==)
            return line.split('>=')[0].split('<=')[0].split('==')[0].strip()
        return None

    @classmethod
    def get_dependencies(cls):
        # List all files in the current working directory
        for filename in os.listdir(cls.basedir):
            # Check if the file contains 'req' or 'dep' and has a .txt extension
            if (('req' in filename or 'dep' in filename) and filename.endswith('.txt')):
                filepath = f"{cls.basedir}/{filename}"
                # Read the contents of the file and store in the dictionary
                deps = set()
                for line in get_lines(filepath):
                    if cleaned := cls.clean_line(line):
                        deps.add(cleaned)
                cls.dependencies[filename] = deps
        return cls.dependencies

    @classmethod
    def to_set(cls, deps:dict=None):
        return flatten_set(cls.dependencies) if not deps and cls.dependencies else deps


if __name__ == "__main__":
    Toml.get_dependencies()
    deps = Toml.to_set()
    print(deps)
    deps = Expand.get_dependencies(deps)
    print(deps)

